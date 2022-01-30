# JSONloader

This module is for you if you're tired of writing boilerplate that:
- build a straightforward Python object from loaded JSON.  
- checks that your input-loaded-JSON has all necessary attributes for your pipeline.
- checks that your input JSON has the right types.

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



