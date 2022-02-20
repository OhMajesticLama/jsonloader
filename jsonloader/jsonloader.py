"""
This module is for you if you're tired of writing boilerplate that:
- build a straightforward Python object from loaded JSON.
- checks that your input-loaded-JSON has all necessary attributes for your
  pipeline.
- checks that your input JSON has the right types.
"""
import functools
from typing import Union, Any

import typeguard

TYPING_JSON_LOADED = Union[dict, list, int, str, float, bool]


def JSONclass(
        cls=None,
        *,
        annotations: bool = False,
        annotations_strict: bool = False,
        annotations_type: bool = False):
    """
    By default we don't check for anything, we just build the object
    as we received it.
    >>> from jsonloader import JSONclass
    >>> data = {'a': 'aa', 'b': 'bb', 'c': 1}
    >>> @JSONclass
    ... class Example:
    ...     pass
    ...
    >>> example = Example(data)
    >>> example.a
    'aa'
    >>> example.b
    'bb'

    We want to ensure we have annotated parameters
    >>> from jsonloader import JSONclass
    >>> data = {'a': 'aa', 'b': 'bb', 'c': 1}
    >>> @JSONclass(annotations=True)
    ... class Example:
    ...     a: str
    ...     d: int
    ...
    >>> try:
    ...     example = Example(data)
    ... except KeyError:
    ...     print("error - missing 'd'")
    ...
    error - missing 'd'
    >>> data['d'] = 1  # Let's fix the missing data
    >>> example = Example(data)  # No more error in loading.

    We want to ensure we have *only* annotated parameters
    >>> from jsonloader import JSONclass
    >>> data = {'a': 'aa', 'b': 'bb', 'c': 1}
    >>> @JSONclass(annotations=True, annotations_strict=True)
    ... class Example:
    ...     a: str
    ...     b: int
    ...
    >>> try:
    ...     example = Example(data)
    ... except KeyError:
    ...     print("error - extra 'c'")
    ...
    error - extra 'c'
    >>> del data['c']  # Let's remove unwanted data
    >>> example = Example(data)  # No more error in loading.

    We want to ensure we have only annotated parameters and they
    are of annotated type.
    >>> from jsonloader import JSONclass
    >>> data = {'a': 'aa', 'b': 'bb'}
    >>> @JSONclass(annotations_strict=True, annotations_type=True)
    ... class Example:
    ...     a: str
    ...     b: int
    ...
    >>> try:
    ...     example = Example(data)
    ... except TypeError:
    ...     print("error - b is not int")
    ...
    error - b is not int

    Default values are supported too.
    >>> from jsonloader import JSONclass
    >>> data = {'a': 'aa'}
    >>> @JSONclass(annotations_strict=True, annotations_type=True)
    ... class Example:
    ...     a: str
    ...     b: int = 1
    ...
    >>> example = Example(data)
    >>> example.b
    1

    A JSONclass can be converted back to a dict, even for recursive
    structures
    >>> from jsonloader import JSONclass
    >>> data = {'a': 'aa', 'b':2, 'c': {'foo': 'bar'}}
    >>> @JSONclass(annotations_type=True, annotations=True)
    ... class Example:
    ...     a: str
    ...     b: int
    ...
    >>> example = Example(data)
    >>> assert dict(example) == data
    """
    def decorator(cls):
        custom_jsonwrapper = wrapper_factory(
            annotations=annotations,
            annotations_strict=annotations_strict,
            annotations_type=annotations_type)

        # Set cls in second to allow overwride of custom_json_wrapper
        class CustomJSONWrapper(custom_jsonwrapper, cls):
            pass
        CustomJSONWrapper.__name__ = cls.__name__
        return CustomJSONWrapper

    if cls is None:
        # We need to return a class decorator
        return decorator
    else:
        return decorator(cls)


class JSONWrapper:
    def __new__(cls,
                json_loaded_object: TYPING_JSON_LOADED = None,
                *,
                annotations: bool = False,
                annotations_strict: bool = False,
                annotations_type: bool = False) -> Any:
        """
        >>> # JSON object should be loaded JSON (e.g. with json standard).
        >>> json_obj = {'foo': 'bar', 'key3': {'key4': 4}}
        >>> wrapper = JSONWrapper(json_obj)
        >>> vars(wrapper)
        {'foo': 'bar', 'key3': '<JSONWrapper: {'key4': 4}>'}
        >>> wrapper.foo
        'bar'
        >>> wrapper
        '<JSONWrapper: {'foo': 'bar', 'key3': '<JSONWrapper: {'key4': 4}>'}>'
        """
        annotations = (annotations
                       or annotations_type
                       or annotations_strict)
        default_attributes = {}

        if not hasattr(cls, '__annotations__'):
            # There is nothing to check, don't provoke failure.
            annotations = False

        if (annotations
                and hasattr(json_loaded_object, dict.keys.__name__)
                and hasattr(json_loaded_object, dict.items.__name__)):
            # dict-like object + check_keys request
            keys_a = set(cls.__annotations__.keys())
            keys_j = set(json_loaded_object.keys())

            for k, t in cls.__annotations__.items():
                if hasattr(cls, k):
                    # A default value has been set by user
                    # a. Check consistent default type with annotation
                    if annotations_type:
                        typeguard.check_type(
                                '{}: default of {}'.format(k, getattr(cls, k)),
                                getattr(cls, k), t)

                    # b. Discard key from keys availability in loaded object.
                    keys_a.discard(k)
                    keys_j.discard(k)

                    # c. Store for setting to new instance when we instantiate
                    # Note: This will have the same side effects for mutable
                    # default values as for function parameters and class-level
                    # defaults.
                    default_attributes[k] = getattr(cls, k)

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

        if (annotations_type
                and hasattr(cls, '__annotations__')
                and hasattr(json_loaded_object, dict.items.__name__)):
            for k, v in json_loaded_object.items():
                if k in cls.__annotations__:
                    # Let coverage to annotations and annotations_strict checks
                    # Here we just check that received data is of expected type
                    t = cls.__annotations__[k]
                    if isinstance(t, list):
                        raise TypeError(
                                "Use typing.List instead of [] or list for "
                                "annotated types. Nested types in [] will not "
                                "be checked.")
                    typeguard.check_type('{}: {}'.format(k, v), v, t)

        if hasattr(json_loaded_object, dict.items.__name__):
            # we're in a dict, let's set attributes
            new_obj = super(JSONWrapper, cls).__new__(cls)
            for k, v in default_attributes.items():
                if k not in json_loaded_object:
                    # Attribute not passed as parameter and we have a default.
                    # Set it.
                    setattr(new_obj, k, v)
            for k, v in json_loaded_object.items():
                if annotations and k in cls.__annotations__:
                    # Recursive Wrapper case, we want to set the
                    # same parameters as requested by user.
                    if hasattr(cls, '__annotations__'):
                        type_a = cls.__annotations__[k]
                        try:
                            if issubclass(type_a, JSONWrapper):
                                setattr(new_obj, k, type_a(v))
                                # Successfully set, skip to next attribute.
                                continue
                        except TypeError:
                            # type_a is not a JSONWrapper Child,
                            # use generic case below.
                            pass

                # Generic case
                setattr(new_obj, k,
                        # In default case, we want to use the same parameter
                        # for child as parent.
                        JSONWrapper(
                            v,
                            annotations=annotations,
                            annotations_type=annotations_type,
                            annotations_strict=annotations_strict))
            return new_obj
        elif (hasattr(json_loaded_object, list.__iter__.__name__)
                and hasattr(json_loaded_object, list.clear.__name__)):
            # We have a list-like object and not a string
            return [JSONWrapper(
                v,
                annotations=annotations,
                annotations_type=annotations_type,
                annotations_strict=annotations_strict)
                    for v in json_loaded_object]
        else:
            return json_loaded_object

    def __eq__(self, other):
        if isinstance(other, dict):
            return self.__dict__ == other
        elif hasattr(other, '__dict__'):
            return self.__dict__ == other.__dict__
        try:
            return self.__dict__ == other
        except Exception as exc:
            raise TypeError(f"{self.__class__.__name__} can't compare to "
                            "{type(other)}") from exc

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, str(self.__dict__))

    def __repr__(self):
        return "'{}'".format(self.__str__())

    def __iter__(self):
        for k, v in self.__dict__.items():
            if isinstance(v, JSONWrapper):
                yield k, dict(v)
            else:
                yield k, v

    def __getitem__(self, item: str) -> Any:
        if not hasattr(self, item):
            raise KeyError(item)
        return getattr(self, item)


@functools.lru_cache(maxsize=None)
def wrapper_factory(
        *,
        annotations: bool = False,
        annotations_strict: bool = False,
        annotations_type: bool = False) -> JSONWrapper:
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
            ...     foo: int
            ...
            >>> Foo({{'foo': 1}})
            '<Foo: {{'foo': 1}}>'

        equivalent to:
            >>> class Foo(JSONWrapper):
            ...     foo: int
            ...
            >>> Foo({{'foo': 1}},
            ...     annotations={annotations},
            ...     annotations_type={annotations_type},
            ...     annotations_strict={annotations_strict})
            ...
            '<Foo: {{'foo': 1}}>'

    """.format(
            name_suffix=name_suffix,
            annotations=annotations,
            annotations_type=annotations_type,
            annotations_strict=annotations_strict)

    newclass.__new__ = functools.partial(
            newclass.__new__,
            annotations=annotations,
            annotations_strict=annotations_strict,
            annotations_type=annotations_type)
    newclass.__doc__ = doc
    return newclass


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
