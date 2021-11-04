Fastclasses JSON
================

[![CI](https://github.com/cakemanny/fastclasses-json/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/cakemanny/fastclasses-json/actions/workflows/pythonpackage.yml?query=branch%3Amaster)
[![PyPI](https://img.shields.io/pypi/v/fastclasses-json)](https://pypi.org/project/fastclasses-json/)

Inspired by [Dataclasses JSON](https://github.com/lidatong/dataclasses-json/).
This library attempts provide some basic functionality for encoding and
decoding [dataclasses](https://docs.python.org/3/library/dataclasses.html)
with close to hand-written performance characteristics for large datasets.

```python

from dataclasses import dataclass
from fastclasses_json import dataclass_json

@dataclass_json
@dataclass
class SimpleExample:
    str_field: str

SimpleExample.from_dict({'str_field': 'howdy!'})
SimpleExample.from_json('{"str_field": "howdy!"}')
# SimpleExample(str_field='howdy!')
SimpleExample('hi!').to_dict()
# {'str_field': 'hi!'}
SimpleExample('hi!').to_json()
# '{"str_field":"hi!"}'

```

Installation
------------
```bash
$ pip install fastclasses-json
```

Supported Types
---------------
* `typing.List[T]` where `T` is also decorated with `@dataclass_json`
* `typing.Optional[T]`
* `typing.Optional[typing.List[T]]`
* `typing.List[typing.Optional[T]]`
* `typing.List[typing.List[typing.List[T]]]` etc
* `typing.Dict[str, T]`
* `enum.Enum` subclasses
* `datetime.date` and `datetime.datetime` as ISO8601 format strings
  - NB: if `python-dateutil` is installed, it will be used instead of the
    standard library for parsing
* `decimal.Decimal` as strings
* `uuid.UUID` as strings
* Mutually recursive dataclasses.

any other types will just be left as is

```python
from __future__ import annotations
from typing import Optional, List

@dataclass_json
@dataclass
class Russian:
    doll: Optional[Doll]

@dataclass_json
@dataclass
class Doll:
    russian: Optional[Russian]

Russian.from_dict({'doll': {'russian': {'doll': None}}})
# Russian(doll=Doll(russian=Russian(doll=None)))
Russian(Doll(Russian(None))).to_dict()
# {'doll': {'russian': {}}}

from enum import Enum

class Mood(Enum):
    HAPPY = 'json'
    SAD = 'xml'

@dataclass_json
@dataclass
class ILikeEnums:
    maybe_moods: Optional[List[Mood]]


ILikeEnums.from_dict({})  # ILikeEnums(maybe_moods=None)
ILikeEnums.from_dict({'maybe_moods': ['json']})  # ILikeEnums(maybe_moods=[Mood.HAPPY])
ILikeEnums(maybe_moods=[Mood.HAPPY]).to_dict()  # {'maybe_moods': ['json']}

from datetime import date

@dataclass_json
@dataclass
class Enitnelav:
    romantic: date

Enitnelav.from_dict({'romantic': '2021-06-17'})  # Enitnelav(romantic=datetime.date(2021, 6, 17))
Enitnelav(romantic=date(2021, 6, 17)).to_dict()  # {'romantic': '2021-06-17'}

from decimal import Decimal
from uuid import UUID

@dataclass_json
@dataclass
class TaxReturn:
    number: UUID
    to_pay: Decimal  # 😱

TaxReturn.from_dict({'number': 'e10be89e-938f-4b49-b4cf-9765f2f15298', 'to_pay': '0.01'})
# TaxReturn(number=UUID('e10be89e-938f-4b49-b4cf-9765f2f15298'), to_pay=Decimal('0.01'))
TaxReturn(UUID('e10be89e-938f-4b49-b4cf-9765f2f15298'), Decimal('0.01')).to_dict()
# {'number': 'e10be89e-938f-4b49-b4cf-9765f2f15298', 'to_pay': '0.01'}

```

we are not a drop-in replacement for Dataclasses JSON. There are plenty of
cases to use this in spite.

Configuration
-------------

Per-field configuration is done by including a `"fastclasses_json"` dict
in the field metadata dict.

* `encoder`: a function to convert a given field value when converting from
  a `dataclass` to a `dict` or to JSON. Can be any callable.
* `decoder`: a function to convert a given field value when converting from
  JSON or a dict into the python `dataclass`. Can be any callable.
* `field_name`: the name the field should be called in the JSON output.

### example

```python
@dataclass_json
@dataclass
class Coach:
    from_: str = field(metadata={
        "fastclasses_json": {
            "field_name": "from",
            "encoder": lambda v: v[:5].upper(),
        }
    })
    to_: str = field(metadata={
        "fastclasses_json": {
            "field_name": "to",
            "encoder": lambda v: v[:5].upper(),
        }
    })


Coach("London Victoria", "Amsterdam Sloterdijk").to_dict()
# {'from': 'LONDO', 'to': 'AMSTE'}
```


Type checking (i.e. using mypy)
-------------------------------

If using type annotations in your code, you may notice type errors when type
checking classes that use the `@dataclass_json` decorator.

```
% mypy tests/for_type_checking.py
tests/for_type_checking.py:27: error: "A" has no attribute "to_json"
tests/for_type_checking.py:28: error: "Type[A]" has no attribute "from_dict"
```

There are two techniques for overcoming this, one which is simpler but likely
to break or be unstable between versions of python and mypy; and one which
is a bit more work on your part.

### Mypy plugin

Changes in python and mypy are likely to lead to a game of cat and mouse, but
for the moment, we have a plugin that you can configure in your `setup.cfg`

```
% cat setup.cfg
[mypy]
plugins = fastclasses_json.mypy_plugin
```

### Mixin with stub methods

There is a mixin containing stub methods for converting to and from dicts and
JSON. This can be useful if the mypy plugin breaks or if you are using a
different type checker.

```python
from dataclasses import dataclass
from fastclasses_json import dataclass_json, JSONMixin

@dataclass_json
@dataclass
class SimpleTypedExample(JSONMixin):
    what_a_lot_of_hassle_these_types_eh: str

print(SimpleTypedExample.from_dict({'what_a_lot_of_hassle_these_types_eh': 'yes'}))
```
```
% mypy that_listing_above.py
Success: no issues found in 1 source file
```

Notice that you have to use both the `@dataclass_json` decorator and the
`JSONMixin` mixin. How very annoying!


Migration & Caveats
-------------------

### `None`
Fields with the value `None` are not included in the produced JSON. This helps
keep the JSON nice and compact

```python
from dataclasses import dataclass
from fastclasses_json import dataclass_json
from typing import Optional

@dataclass_json
@dataclass
class Farm:
    sheep: Optional[int]
    cows: Optional[int]

Farm(sheep=None, cows=1).to_json()
# '{"cows":1}'
```


### `infer_missing`
Fastclasses JSON does not get annoyed if fields are missing when deserializing.
Missing fields are initialized as `None`. This differs from the defaults in
[Dataclasses JSON][dataclasses-json].

```python
from dataclasses import dataclass
from fastclasses_json import dataclass_json

@dataclass_json
@dataclass
class Cupboard:
    num_hats: int
    num_coats: int

Cupboard.from_dict({'num_hats': 2})
# Cupboard(num_hats=2, num_coats=None)
```

In [Dataclasses JSON][dataclasses-json], there is the `infer_missing`
parameter that gives this behaviour.
To make migration easier, `from_dict` and `from_json` takes the dummy parameter
`infer_missing`, so that the following code works the same and does
not cause errors:

```python
Cupboard.from_dict({'num_hats': 2}, infer_missing=True)
# Cupboard(num_hats=2, num_coats=None)
```

[dataclasses-json]: https://github.com/lidatong/dataclasses-json/

<!-- TODO: write about nested Any? -->
