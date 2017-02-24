from data import data
import geograpy
import nltk
from re import match

from collections import Mapping, Set, Sequence

# dual python 2/3 compatability, inspired by the "six" library
string_types = (str, unicode) if str is bytes else (str, bytes)
iteritems = lambda mapping: getattr(mapping, 'iteritems', mapping.items)()


def objwalk(obj, path=(), memo=None):
    """
    source:
     http://tech.blog.aknin.name/2011/12/11/walking-python-objects-recursively/
    """
    if memo is None:
        memo = set()
    iterator = None
    if isinstance(obj, Mapping):
        iterator = iteritems
    elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
        iterator = enumerate
    if iterator:
        if id(obj) not in memo:
            memo.add(id(obj))
            for path_component, value in iterator(obj):
                for result in objwalk(value, path + (path_component,), memo):
                    yield result
            memo.remove(id(obj))
    else:
        yield path, obj


stop_words = ['location', 'address', 'place', 'space', 'coordinate', 'area', 'spot', 'position']
stop_words_2 = ['_l']


def is_coord(value):
    """
    Check if value is a coordinate, or coordinate pair
    :param value:
    :return:
    """
    
    # TODO: check if value is a coordinate vs. coordinate pair
    
    coordinate = bool(match("\s*"  # Zero or more whitespace characters
                            "\(?"  # An optional opening parenthesis
                            "\s*"  # Zero or more whitespace characters
                            "-?"  # An optional hyphen (for negative numbers)
                            "\d+"  # One or ore whitespace characters
                            "-?"  # An optional hyphen (for negative numbers)
                            "\d+"  # One or more digits
                            "(?:\.\d+)?"  # An optional period followed by one or more digits (for fractions)
                            "\s*"  # Zero or more whitespace characters
                            "\)?"  # An optional closing parenthesmore digits
                            "(?:\.\d+)?"  # An optional period followed by one or more digits (for fractions)
                            "\s*"  # Zero or more whitespace characters
                            ",?"  # An optional comma
                            "\s*"  # Zero or mis
                            "\s*"  # Zero or more whitespace characters
                            "$",
                            str(value)))
    print str(value), coordinate
    return coordinate



# url = 'http://www.bbc.com/news/world-europe-26919928'
# places = geograpy.get_place_context(url=url)
#
# print places.countries

# for path, value in objwalk(data):
#
#
#     # e = geograpy.extraction.Extractor(text=value)
#     # e.find_entities()
#     # print e.places
#
#     if any(stop in path for stop in stop_words) or any(stop in value for stop in stop_words):
#         print path, value
#         # e = geograpy.extraction.Extractor(text=value)
#         # e.find_entities()
#         # print e.places
#
# #         places = geograpy.get_place_context(text = value)
# #         if pla
# #         print places
# #         #print path, value
# #
#
# e = geograpy.extraction.Extractor(text = 'The United States of america is a place in the world')
# e.find_entities()
#
# # You can now access all of the places found by the Extractor
# print e.places

#
# places = geograpy.get_place_context(text = 'The ')
# places.
# print len(places)

# def walk_dict(d, depth=0):
#     for key, value in d.items():  # sorted(d.items(),key=lambda x: x[0]):
#         if isinstance(value, dict):
#             print ("    ") * depth + ("%s" % key)
#             walk_dict(value, depth + 1)
#         elif isinstance(value, list):
#             depth = depth + 1
#             for item in value:
#                 print ("    ") * depth + "%s" % (item)
#         else:
#             print ("    ") * depth + "%s %s" % (key, value)
#
#
# # for dictionary in data:
# #     walk_dict(dictionary)
# #     print "------------------------------------------"

