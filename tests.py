#!flask/bin/python
import os
import unittest

import unittest
from datetime import datetime, timedelta

from config import basedir
from app import app, db
from app.models import User, Search
from utils import objwalk


class TestUserGeneration(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, 'test.db')
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_avatar(self):
        # create a user
        u = User(nickname='john', email='john@example.com')
        avatar = u.avatar(128)
        expected = 'http://www.gravatar.com/avatar/' + \
            'd4c74594d841139328695756648b6bd6'
        assert avatar[0:len(expected)] == expected

    def test_make_unique_nickname(self):
        # create a user and write it to the database
        u = User(nickname='john', email='john@example.com')
        db.session.add(u)
        db.session.commit()
        nickname = User.make_unique_nickname('john')
        assert nickname != 'john'
        # make another user with the new nickname
        u = User(nickname=nickname, email='susan@example.com')
        db.session.add(u)
        db.session.commit()
        nickname2 = User.make_unique_nickname('john')
        assert nickname2 != 'john'
        assert nickname2 != nickname



class TestObjwalk(unittest.TestCase):
    """

    source:
     http://tech.blog.aknin.name/2011/12/11/walking-python-objects-recursively/
    """

    def assertObjwalk(self, object_to_walk, *expected_results):
        return self.assertEqual(tuple(sorted(expected_results)), tuple(sorted(objwalk(object_to_walk))))
    def test_empty_containers(self):
        self.assertObjwalk({})
        self.assertObjwalk([])
    def test_single_objects(self):
        for obj in (None, 42, True, "spam"):
            self.assertObjwalk(obj, ((), obj))
    def test_plain_containers(self):
        self.assertObjwalk([1, True, "spam"], ((0,), 1), ((1,), True), ((2,), "spam"))
        self.assertObjwalk({None: 'eggs', 'bacon': 'ham', 'spam': 1},
                           ((None,), 'eggs'), (('spam',), 1), (('bacon',), 'ham'))
        # sets are unordered, so we dont test the path, only that no object is missing
        self.assertEqual(set(obj for path, obj in objwalk(set((1,2,3)))), set((1,2,3)))
    def test_nested_containers(self):
        self.assertObjwalk([1, [2, [3, 4]]],
                           ((0,), 1), ((1,0), 2), ((1, 1, 0), 3), ((1, 1, 1), 4))
        self.assertObjwalk({1: {2: {3: 'spam'}}},
                           ((1,2,3), 'spam'))
    def test_repeating_containers(self):
        repeated = (1,2)
        self.assertObjwalk([repeated, repeated],
                           ((0, 0), 1), ((0, 1), 2), ((1, 0), 1), ((1, 1), 2))
    def test_recursive_containers(self):
        recursive = [1, 2]
        recursive.append(recursive)
        recursive.append(3)
        self.assertObjwalk(recursive, ((0,), 1), ((1,), 2), ((3,), 3))


if __name__ == '__main__':
    unittest.main()
