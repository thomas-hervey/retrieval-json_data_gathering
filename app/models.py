import os
import json
from hashlib import md5
from app import db
import requests
from jsonschema import validate
import json_schema_generator

from urlparse import urlparse


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    searches = db.relationship('Search', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

    @staticmethod
    def make_unique_nickname(nickname):
        new_nickname = ""
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % \
            (md5(self.email.encode('utf-8')).hexdigest(), size)

    def __repr__(self):
        return '<User %r>' % self.nickname


class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    data_info = db.relationship('Data', backref='source', uselist=False)

    url = db.Column(db.String(300), index=True, unique=False)
    is_api = db.Column(db.Boolean, default=False)
    netloc = db.Column(db.String(100), index=True)
    path = db.Column(db.String(400), index=True)

    def __init__(self, form):
        self.url = form.source_url.data
        self.is_api = form.is_api.data
        self.netloc, self.path = self.parse_url(self.url)

    def __repr__(self):
        return '<Search %r>' % self.url

    @staticmethod
    def parse_url(url):
        p = urlparse(url)
        return p.netloc, p.path


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
    search = db.relationship('Search', backref="information")

    def __init__(self, source, *args, **kwargs):
        super(Data, self).__init__(*args, **kwargs)
        self.search = source
        self._r = None
        self._data_type = None
        self._schema = None
        self._data = None

    @property
    def r(self):
        if self._r is None and self.search is not None:
            try:
                _r = requests.get(self.search.url)
                if _r.status_code == requests.codes.ok:
                    self._r = _r
            except AttributeError as e:
                print "Could not locate source: {1}", e
        return self._r

    @property
    def data_type(self):
        if self._data_type is None:
            try:
                self._data_type = self._set_type()
            except AttributeError as e:
                print "TODO"
        return self._data_type

    @property
    def schema(self):
        if self._schema is None:
            try:
                self._schema = self._set_schema()
            except AttributeError as e:
                print "TODO: some sort of attribute error: {1}", e
        return self._schema
    
    @property
    def data(self):
        if self.data_type == "JSON" and self.schema is not None:
            self._data = self.r.json()
            return self._data
        else:
            # TODO: implement other data gathering methods
            return "not json data type: data not retrieved"

    def _set_type(self):
        # TODO: make conditional more robust (more than string match)
        content_type = self.r.headers.get('content-type')
        if "geojson" in content_type:
            return "geoJSON"
        elif "json" in content_type:
            return "JSON"
        elif "WHATEVER_HTML_WOULD_BE" in content_type:
            return content_type
        else:
            return "not_json" + content_type

    def _set_schema(self):
        if self.data_type == "JSON":
            return json_schema_generator.SchemaGenerator.from_json(self.r.text).to_dict()  # create json schema dictionary
        else:
            # TODO: implement other schema gathering methods
            return "not json data type: schema not set"

    # def traverse(self):
    #     """
    #     Traverse decoded data to: save desired information, search for geometry links
    #     """
    #
    #     # 1. look at self.type (and determine methods)
    #     # 2. look at schema (and determine nodes)
    #     # 3. determine traversial technique via nodes (index attributes)
    #     # 4. during traversing:
    #     # 4.1. look for geom field (TODO: add user assistance)
    #     # 4.2. look for desired fields to keep
    #     # 5. extract geometry & fields to keep
    #
    #     # then... implement geom. querying features
    #     # ...     implement geom matching features
    #     # ...     implement data structuring
    #     # ...     implement output saving
    #
    #     print self.data_type
    #
    #     if self.data_type == "JSON":
    #         print "JSON:"
    #         self.json_handler()
    #
    #     elif self.data_type == "geoJSON":
    #         print "GEOJSON: "
    #     else:
    #         print "unsure... self.r.type is... : "
    #
    # # # TODO: reorder function calls (ie. don't have json_handler, just pass json to some function like traverse)
    # # def json_handler( self ):
    # #     print self.same_num_elements()
    # #
    # #     # self.r.has_location = self.has_coordinates()  # checks if json has coordinate attribute(s)
    # #     # self.r.has_placename = self.has_placename()  # checks if json has place name attribute(s)
    #
    # def same_num_elements( self ):
    #     num_attributes = []
    #     for element in self.r.json():
    #         attribute_count = 0
    #         for attribute in element:
    #             attribute_count += 1
    #         num_attributes.append(attribute_count)
    #
    #         # if number of attributes is unique (meaning it isn't in num_attributes'... search it!!!)
    #
    #     num_attributes = set(num_attributes)
    #
    #     return all(x == num_attributes[0] for x in num_attributes)
    #
    # def has_coordinates( self ):
    #     return True
    #
    # def has_placename( self ):
    #     return True

        # PySAL, python
        # Shapely, python
        # OGR, python
        # QGIS, pyqgis, python
        # SagaGIS, python
        # Grass, python
        # spatialite, pyspatialite, python
        # PostreSQL / PostGIS, Psycopg, python
        # R
        # Project, rpy2, python
        # Whitebox
        # GAT, python
        # GeoScript, jython

    # rec = json_schema_generator.Recorder.from_url(self.r.url)
    # save_json_schema_path = os.path.join(os.path.dirname(__file__), '../tmp', 'new.json_schema')
    # rec.save_json_schema(save_json_schema_path)