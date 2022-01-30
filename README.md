# JSONloader

This module is for you if you're tired of writing boilerplate that:
- builds a straightforward Python object from loaded JSON.  
- checks that your input-loaded-JSON has all necessary attributes for your pipeline.
- checks that your input JSON has the right types.


## Example
Main intended usage is through the `JSONclass decorator`, example below:
```python
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

>>> # We want to check we have only annotated parameters and they
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
```

## Install

### User installation
```
python3 -m virtualenv venv
. venv/bin/activate
pip3 install jsonloader
```

### Developer installation
```
python3 -m virtualenv venv
. venv/bin/activate
pip3 install -e '.[dev]'
```

## Run Tests

```
# From git directory
nose2 -t .
```

### Tests coverage
For example, leverage `coverage` module: `nose2 -t . -C --coverage-report html` 



