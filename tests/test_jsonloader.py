import unittest
import typing
import json


from jsonloader import JSONWrapper, JSONclass
from jsonloader import JSONWrapperAnnotations
from jsonloader import JSONWrapperStrict
from jsonloader import JSONWrapperType


class TestJSONclass(unittest.TestCase):
    def test_JSONclass(self):
        @JSONclass
        class Dummy:
            foo: str

        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': 4}
        wrapper = Dummy(json_obj)
        self.assertEqual(len(wrapper), len(json_obj))

        for k, v in json_obj.items():
            self.assertTrue(hasattr(wrapper, k))
            self.assertEqual(getattr(wrapper, k), v)


class TestJSONWrapper(unittest.TestCase):
    def test_json_to_obj_flat(self):
        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': 4}
        wrapper = JSONWrapper(json_obj)
        self.assertEqual(len(wrapper), len(json_obj))

        for k, v in json_obj.items():
            self.assertTrue(hasattr(wrapper, k))
            self.assertEqual(getattr(wrapper, k), v)

    def test_json_to_obj_recursive(self):
        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        wrapper = JSONWrapper(json_obj)
        self.assertEqual(len(wrapper), len(json_obj))

        for k, v in json_obj.items():
            self.assertTrue(hasattr(wrapper, k))
            self.assertEqual(
                    getattr(wrapper, k), v,
                    f'Error (k, v) ({k}, {v})')

    def test_json_to_obj_str(self):
        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        wrapper = JSONWrapper(json_obj)
        self.assertEqual(str(wrapper), str(json_obj))

    def test_annotation_base(self):
        class Child(JSONWrapper):
            a: str
            b: int

        json_obj = {'a': 'aaa', 'b': 1}
        wrapped = Child(json_obj)
        self.assertEqual(wrapped.a, 'aaa')
        self.assertEqual(wrapped.b, 1)

    def test_annotation_fail(self):
        class Child(JSONWrapperAnnotations):
            a: str
            b: int
            c: str

        json_obj = {'a': 'aaa', 'b': 1}
        with self.assertRaises(KeyError):
            Child(json_obj)

    def test_annotation_recursive(self):
        class Child(JSONWrapperAnnotations):
            a: str
            b: int

            class Bar(JSONWrapperAnnotations):
                bar_key: str
            c: Bar

        json_obj = {'a': 'aaa', 'b': 1, 'c': {'bar_key': 'foo'}}
        wrapped = Child(json_obj)
        self.assertEqual(wrapped.a, 'aaa')
        self.assertEqual(wrapped.b, 1)
        self.assertEqual(wrapped.c.bar_key, 'foo')

    def test_annotation_recursive_fail(self):
        class Child(JSONWrapperAnnotations):
            a: str
            b: int

            class Bar(JSONWrapperAnnotations):
                bar_key: str
            c: Bar

        json_obj = {'a': 'aaa', 'b': 1, 'c': {'bar_key_error': 'foo'}}
        with self.assertRaises(KeyError):
            # This should not be accepted as there is an error in bar_key
            Child(json_obj)

    def test_annotation_strict(self):
        class Child(JSONWrapperStrict):
            a: str
            b: int

        json_obj = {'a': 'aaa', 'b': 1, 'c': 4}
        with self.assertRaises(KeyError):
            Child(json_obj)

    def test_list_child(self):
        class Child(JSONWrapper):
            pass

        json_obj = {'a': 'aaa', 'b': 1, 'c': [1, 2, 3]}
        child = Child(json_obj)
        self.assertTrue(hasattr(child, 'c'))
        self.assertEqual(child.c, [1, 2, 3])

    def test_list_child_type(self):
        class Child(JSONWrapperType):
            c: typing.List[int]

        json_obj = {'a': 'aaa', 'b': 1, 'c': [1, 2, 3]}
        child = Child(json_obj)
        self.assertTrue(hasattr(child, 'c'))
        self.assertEqual(child.c, [1, 2, 3])

    def test_list_child_type_broken(self):
        class Child(JSONWrapperType):
            c: typing.List[str]

        json_obj = {'a': 'aaa', 'b': 1, 'c': [1, 2, 3]}
        with self.assertRaises(TypeError):
            Child(json_obj)

    def test_list_child_type_dont_use_list(self):
        class Child(JSONWrapperType):
            c: [int]

        json_obj = {'a': 'aaa', 'b': 1, 'c': [1, 2, 3]}
        with self.assertRaises(TypeError):
            Child(json_obj)

    def test_operator_equal_dict(self):
        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        wrapper = JSONWrapper(json_obj)
        self.assertEqual(wrapper, json_obj)

    def test_operator_equal_wrapper(self):
        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        wrapper = JSONWrapper(json_obj)
        wrapper2 = JSONWrapper(json_obj)
        self.assertEqual(wrapper, wrapper2)

    def test_operator_nequal_other(self):
        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        wrapper = JSONWrapper(json_obj)
        self.assertNotEqual(wrapper, None)
        self.assertNotEqual(wrapper, 1)

    def test_operator_nequal(self):
        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        wrapper = JSONWrapper(json_obj)
        json_obj['fooooo'] = 'baaaaar'
        self.assertTrue(wrapper != json_obj)

    def test_operator_len(self):
        json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        wrapper = JSONWrapper(json_obj)
        for k, v in json_obj.items():
            self.assertEqual(getattr(wrapper, k), json_obj[k])

        self.assertEqual(len(wrapper), len(json_obj))

    def test_default_value(self):
        json_obj = {'foo': 'bar', 'key3': {'key4': 4}}

        class Child(JSONWrapperType):
            foo: str
            key2: int = 1

        child = Child(json_obj)
        self.assertEqual(child.key2, 1)


if __name__ == '__main__':
    unittest.main()
