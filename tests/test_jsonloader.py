import unittest
import logging
import os


import jsonloader
from jsonloader import JSONWrapper, JSONclass
from jsonloader import JSONWrapperAnnotations
from jsonloader import JSONWrapperTypeStrict
from jsonloader import JSONWrapperStrict
from jsonloader import JSONWrapperType


LOGGER = logging.getLogger()

class TestJSONclass(unittest.TestCase):
    def test_JSONclass(self):
        @JSONclass
        class Dummy:
            foo : str

        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': 4}
        wrapper = Dummy(json_obj)
        self.assertEquals(len(wrapper), len(json_obj))

        for k, v in json_obj.items():
            self.assertTrue(hasattr(wrapper, k))
            self.assertEquals(getattr(wrapper, k), v)


class TestJSONWrapper(unittest.TestCase):
    def test_json_to_obj_flat(self):
        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': 4}
        wrapper = JSONWrapper(json_obj)
        self.assertEquals(len(wrapper), len(json_obj))

        for k, v in json_obj.items():
            self.assertTrue(hasattr(wrapper, k))
            self.assertEquals(getattr(wrapper, k), v)

    def test_json_to_obj_recursive(self):
        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        wrapper = JSONWrapper(json_obj)
        self.assertEquals(len(wrapper), len(json_obj))

        for k, v in json_obj.items():
            self.assertTrue(hasattr(wrapper, k))
            self.assertEquals(getattr(wrapper, k), v, f'Error (k, v) ({k}, {v})')


    def test_json_to_obj_str(self):
        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        wrapper = JSONWrapper(json_obj)
        self.assertEquals(str(wrapper), str(json_obj))

    def test_annotation_base(self):
        class Child(JSONWrapper):
            a : str
            b : int

        json_obj = {'a': 'aaa', 'b': 1}
        wrapped = Child(json_obj)
        self.assertEquals(wrapped.a, 'aaa')
        self.assertEquals(wrapped.b, 1)

    def test_annotation_fail(self):
        class Child(JSONWrapperAnnotations):
            a : str
            b : int
            c : str

        json_obj = {'a': 'aaa', 'b': 1}
        with self.assertRaises(KeyError):
            wrapped = Child(json_obj)

    def test_annotation_recursive(self):
        class Child(JSONWrapperAnnotations):
            a : str
            b : int
            class Bar(JSONWrapperAnnotations):
                bar_key : str
            c : Bar

        json_obj = {'a': 'aaa', 'b': 1, 'c': {'bar_key': 'foo'}}
        wrapped = Child(json_obj)
        self.assertEquals(wrapped.a, 'aaa')
        self.assertEquals(wrapped.b, 1)
        self.assertEquals(wrapped.c.bar_key, 'foo')

    def test_annotation_recursive_fail(self):
        class Child(JSONWrapperAnnotations):
            a : str
            b : int
            class Bar(JSONWrapperAnnotations):
                bar_key : str
            c : Bar

        json_obj = {'a': 'aaa', 'b': 1, 'c': {'bar_key_error': 'foo'}}
        with self.assertRaises(KeyError):
            # This should not be accepted as there is an error in bar_key
            child = Child(json_obj)
