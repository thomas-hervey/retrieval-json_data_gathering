from utils import objwalk, stop_words, data, is_coord


def _traverse_tuple(_tuple):
    for path, value in objwalk(_tuple):
        print "TUPLE: ", _tuple, "PATH: ", path, "VALUE ", value
        
        is_coord(value)
        
    print "***************"
    # TODO: tuple > list > tuple
    #print _tuple

    # if type(_tuple[0][0]) is tuple:  # tuple's list contains a tuple
    #     for tuple_element in _tuple[0][0]:
    #         print tuple_element
    # else:  # if tuple's list doesn't contain a tuple
    #     return _tuple[0][0]

    # _type = ""
    # return _type


def _get_location_types( _location_tuples ):
    """
    :param _location_tuples: list of potential locations as key(s), value tuples
    :return:
    """
    
    for _tuple in _location_tuples:  # iterate through tuples
        _traverse_tuple(_tuple)
        # TODO: determine ranking scheme to pick "best" location
        # print "TUPLE ", _tuple
        #_type = _determine_type(_tuple)  # determine location type of 'key(s)'


def _get_locations( path, value ):
    
    loc_attrs = []  # location attributes
    
    for element in path:  # iterate through path elements
        if isinstance(element, basestring):  # check if element is a string
            for stop in stop_words:  # iterate through location stop words  # TODO: either remove stop words, or have different mechinism
                if element in stop or stop in element:  # check if element ~ stop word
                    
                    if path.index(element) == len(path) - 1:
                        loc_attrs.append(element)  # append element, the last element in tuple
                    else:
                        loc_attrs.append(path[path.index(element):])  # append element, and all nested elements
                break  # record first found location (with nested elements) only as 'key'
    
    if len(loc_attrs) != 0:  # if location attributes were found
        return loc_attrs, value  # create location attribute tuple with location 'key(s)' and value


def _get_attributes( _data ):
    """
    Extract location attribute(s) from response data

    :param _data: data class instance
    :return:
    """
    
    features_to_check_counter = 5  # TODO: features_to_check_counter = len(_data) / 10
    location_determined = False
    location_tuples = []

    for path, value in objwalk(_data):  # iterate through data element tree
    
        # isolate best location attributes from sample
        if location_determined is False and path[0] >= features_to_check_counter:
            _get_location_types(location_tuples)  # determine location characteristics (e.g. coords, toponyms)
            location_determined = True
        # get attributes for this element
        elif location_determined is False:
            location_tuples.append(_get_locations(path, value))
        # best location attributes have been determined
        else:
            print "determined"
            # TODO: implement -> if path is in list of columns desired, add to attribute list
            # TODO: (make sure features_to_check columns were grabbed too)


        
                
    return True


def locational_referencing(data):
    attributes = _get_attributes(data)

my_data = data
locational_referencing(my_data)



# for path, value in objWalk(_data):
    # check if loc. attrs. have ben determined
        # if so:
        # if not: check if it's time to determine them -->
        # if not either: gather more details
