Fastclasses JSON
================

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
# SimpleExample(str_field='howdy!')

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

from datetime import date

@dataclass_json
@dataclass
class Enitnelav:
    romantic: date

Enitnelav.from_dict({'romantic': '2021-06-17'})  # Enitnelav(romantic=datetime.date(2021, 6, 17))

```

we are not a drop-in replacement for Dataclasses JSON. There are plenty of
cases to use this in spite.
