# JSONloader
[![Downloads](https://pepy.tech/badge/jsonloader)](https://pepy.tech/project/jsonloader)
[![CI](https://github.com/OhMajesticLama/jsonloader/actions/workflows/lint-and-tests.yml/badge.svg)](https://github.com/OhMajesticLama/jsonloader/actions/workflows/lint-and-tests.yml)

This module is for you if you're tired of writing boilerplate that:
- builds a straightforward Python object from loaded JSON or similar dict-based
  data loading (e.g. CSV).
- checks that your input-loaded-JSON has all necessary attributes for your pipeline.
- checks that your input JSON has the right types.


## Examples
Main intended usage is through the `JSONclass` decorator, example below:

By default we don't check for anything, we just build the object
as we received it.
```python
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
```

We want to ensure we have annotated parameters
```python
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
```

We want to ensure we have *only* annotated parameters
```python
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
```

We want to ensure we have only annotated parameters and they
are of annotated type.
```python
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
```

Default values are supported too.
```python
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
```

A JSONclass can be converted back to a dict, even for recursive
structures
```python
>>> from jsonloader import JSONclass
>>> data = {'a': 'aa', 'b':2, 'c': {'foo': 'bar'}}
>>> @JSONclass(annotations_type=True, annotations=True)
... class Example:
...     a: str
...     b: int
...
>>> example = Example(data)
>>> assert dict(example) == data
```

## Install

### User installation
```
# Recommendation: install jsonloader in your project virtualenv
# Should you not want to use virtualenv or equivalent, it's recommended to use
# '--user' pip option to avoid a system-level install.
pip3 install jsonloader
```

### Developer installation

Github repository currently points to latest development version. Please
jump to latest released version tag if you intend to work on PyPI version.
For example `git checkout tags/v0.4.3`.

```
# These commands assume virtualenv is installed
python3 -m virtualenv venv
. venv/bin/activate

# Actually install the deps
pip3 install -e '.[dev]'

# To setup the project's git hooks:
git config --local core.hooksPath hook
```

## Run Tests

```
# From this repository top directory
pytest --doctest-modules
```

### Tests coverage
For example, leverage `coverage` module:
```
coverage run -m pytest --doctest-modules
coverage html
```
