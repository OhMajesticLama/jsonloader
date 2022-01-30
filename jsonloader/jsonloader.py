"""
This module is for you if you're tired of writing boilerplate that:
- build a straightforward Python object from loaded JSON.  
- checks that your input-loaded-JSON has all necessary attributes for your pipeline.
- checks that your input JSON has the right types.
"""
import itertools
import functools
from typing import Union, List, Any

import typeguard

TYPING_JSON_LOADED = Union[dict, list, int, str, float, bool]


def JSONclass(cls=None,
        *,
        annotations : bool = False,
        annotations_strict : bool = False,
        annotations_type : bool = False):
    """
    >>> # By default we don't check for anything, we just build the object
    >>> # as we received it.
    >>> data = {'a': 'aa', 'b': 'bb', 'c': 1}
    >>> @JSONClass
    ... class Example:
    ...     pass
    ...
    >>> wrapper = Example(data)
    >>> wrapper.a
    'aa'
    >>> wrapper.b
    'bb'

    >>> # We want to ensure we have annotated parameters
    >>> data = {'a': 'aa', 'b': 'bb', 'c': 1}
    >>> @JSONClass(annotations=True)
    ... class Example:
    ...     a : str
    ...     d : int
    ...
    >>> try:
    ...     wrapper = Example(data)
    ... except KeyError:
    ...     print("error - missing 'd'")
    ...
    error - missing 'd'
    
    >>> # We want to ensure we have *only* annotated parameters
    >>> data = {'a': 'aa', 'b': 'bb', 'c': 1}
    >>> @JSONClass(annotations=True, annotations_strict=True)
    ... class Example:
    ...     a : str
    ...     b : int
    ...
    >>> try:
    ...     wrapper = Example(data)
    ... except KeyError:
    ...     print("error - extra 'c'")
    ...
    error - extra 'c'

    >>> # We want to ensure we have only annotated parameters and they
    >>> # are of annotated type.
    >>> data = {'a': 'aa', 'b': 'bb'}
    >>> @JSONClass(annotations=True, annotations_strict=True, annotations_type=True)
    ... class Example:
    ...     a : str
    ...     b : int
    ...
    >>> try:
    ...     wrapper = Example(data)
    ... except TypeError:
    ...     print("error - b is int")
    ...
    error - b is int
    """
    def decorator(cls):
        custom_jsonwrapper = wrapper_factory(
            annotations=annotations,
            annotations_strict=annotations_strict,
            annotations_type=annotations_type)
        class CustomJSONWrapper(custom_jsonwrapper, cls): pass
        return CustomJSONWrapper

    if cls is None:
        # We need to return a class decorator
        return decorator
    else:
        return decorator(cls)


@functools.lru_cache(maxsize=None)
def wrapper_factory(*,
        annotations : bool = False,
        annotations_strict : bool = False,
        annotations_type : bool = False):
    """
    Internal class to generate special cases of JSONWrapper if needed.
    """
    if (not annotations
        and not annotations_strict 
        and not annotations_type):
            return JSONWrapper

    name_suffix = ''
    if annotations_type:
        name_suffix += 'Type'
    if annotations_strict:
        name_suffix += 'Strict'
    if not len(name_suffix) and annotations:
        name_suffix += 'Annotations'
    newclass = type(f'JSONWrapper{name_suffix}', (JSONWrapper,), {})

    doc = """
        This is a helper that makes:
            >>> class Foo(JSONWrapper{name_suffix}):
            ...     foo : int
            ...
            >>> Foo({{'foo': 1}})

        equivalent to:
            >>> class Foo(JSONWrapper):
            ...     foo : int
            ...
            >>> Foo({{'foo': 1}},
            ...     annotations={annotations}
            ...     annotations_type={annotations_type},
            ...     annotations_strict={annotations_strict})

    """.format(
            name_suffix=name_suffix,
            annotations=annotations,
            annotations_type=annotations_type, 
            annotations_strict=annotations_strict)

    newclass.__new__ = functools.partial(newclass.__new__,
            annotations=annotations,
            annotations_strict=annotations_strict,
            annotations_type=annotations_type)
    return newclass


class JSONWrapper:
    def __new__(cls,
            json_loaded_object : TYPING_JSON_LOADED = None,
            *,
            annotations : bool = False,
            annotations_strict : bool = False,
            annotations_type : bool = False):
        """
        >>> # JSON object must be loaded JSON (e.g. with json standard module).
        ... # Or spelled differently: a Python dictionary of dictionaries, list,
        ... # str, int, floats, bool, None. If the structure is recursive, the
        ... # tree leaves must be int, float, bool, None or str instances. 
        >>> json_obj = {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        >>> wrapper = JSONWrapper(json_obj)
        >>> vars(wrapper)
        {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        >>> wrapper.foo
        'bar'
        >>> wrapper
        {'foo': 'bar', 'key2': 12.3, 'key3': {'key4': 4}}
        >>> # JSONWrapper will refuse to wrap non-JSON types
        >>> json_obj['func'] = map
        >>> try:
        ...     JSONWrapper(json_obj)
        ... except TypeError as exc:
        ...     print('I got an error')
        'I got an error'

        """
        annotations = (annotations
                or annotations_type
                or annotations_strict)
        if not hasattr(cls, '__annotations__'):
            # There is nothing to check, don't provoke failure.
            annotations = False

        if (annotations
                and hasattr(json_loaded_object, dict.keys.__name__)
                and hasattr(json_loaded_object, dict.items.__name__)):
            # dict-like object + check_keys request
            keys_a = set(cls.__annotations__.keys())
            keys_j = set(json_loaded_object.keys())

            if not keys_a.issubset(keys_j):
                raise KeyError("({}) annotated keys not found in ({})".format(
                    keys_a.difference(keys_j), json_loaded_object
                    ))

                if annotations_strict and not keys_j.issubset(keys_a):
                    # We want strict overlap between annotations and JSON object.
                    raise KeyError(
                        "({}) JSON keys not found in annotations ({})".format(
                        keys_j.difference(keys_a),  keys_a
                        ))

                if annotations_type:
                    for k, t in cls.__annotations__.items():
                        try:
                            typeguard.check_type(k, json_loaded_object[k], t)
                            #check_annotated_type(json_loaded_object[k], t)
                        except TypeError:
                            raise TypeError(
                                    "({}:{}) is not a value "
                                    "of annotated type {}".format(k,
                                        json_loaded_object[k], t))
                        continue 
                        #if t is Any:
                        #    continue
                        #if not isinstance(json_loaded_object[k], t):
                        #    raise TypeError(
                        #            "({}:{}) is not a value "
                        #            "of annotated type {}".format(k,
                        #                json_loaded_object[k], t))
                        #elif isinstance(t, list):
                        #    # User annotated with name : [str] or similar
                        #    if len(t):
                        #        raise NotImplementedError
                        #elif issubclass(t, list):
                        #    if True: raise NotImplementedError
                        #elif issubclass(t, List):
            

        if hasattr(json_loaded_object, dict.items.__name__):
            # we're in a dict, let's set attributes
            new_obj = super(JSONWrapper, cls).__new__(cls)
            for k, v in json_loaded_object.items():
                if annotations and k in cls.__annotations__:
                    # Recursive case
                    if hasattr(cls, '__annotations__'):
                        type_a = cls.__annotations__[k]
                        if issubclass(type_a, JSONWrapper):
                            setattr(new_obj, k, type_a(v))
                            #setattr(new_obj, k, JSONWrapperStrict(v,))
                            continue
                # Generic case
                setattr(new_obj, k,
                        JSONWrapper(v,
                            annotations=annotations,
                            annotations_type=annotations_type,
                            annotations_strict=annotations_strict))
            return new_obj
        elif (hasattr(json_loaded_object, list.__iter__.__name__)
                and hasattr(json_loaded_object, list.clear.__name__)):
            # We have a list-like object and not a string
            return [JSONWrapper(v,
                annotations=annotations,
                annotations_type=annotations_type,
                annotations_strict=annotations_strict)
                    for v in json_loaded_object]
        else:
            return json_loaded_object

    def __eq__(self, other):
        if hasattr(other, '__dict__'):
            return self.__dict__ == other.__dict__
        elif isinstance(other, dict):
            return self.__dict__ == other
        try:
            # Maybe it's dict like, manual implementation of dict comparison.
            if len(self.__dict__) != len(other):
                return False
            else:
                for k, v in other.items():
                    if k not in self.__dict__:
                        return False
                    if v != self.__dict__.get(k):
                        return False
                return True
        except AttributeError:
            pass
        raise TypeError(f"JSONDictWrapper can't compare to {type(other)}")

    def __neq__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return len(self.__dict__)
    
    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)


JSONWrapperAnnotations = wrapper_factory(annotations=True)

JSONWrapperTypeStrict = wrapper_factory(
        annotations_type=True,
        annotations_strict=True)

JSONWrapperType = wrapper_factory(annotations_type=True)

JSONWrapperStrict = wrapper_factory(annotations_strict=True)

__all__ = [
    JSONclass.__name__,
    JSONWrapper.__name__,
    JSONWrapperAnnotations.__name__,
    JSONWrapperType.__name__,
    JSONWrapperTypeStrict.__name__,
    JSONWrapperStrict.__name__
        ]

