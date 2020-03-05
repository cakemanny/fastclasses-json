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
* `enum.Enum` subclasses
* Mutually recursive dataclasses.

but not yet:
* `typing.Dict[str, T]`

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

```

we are not a drop-in replacement for Dataclasses JSON. There are plenty of
cases to use this in spite

```python
@dataclass_json
@dataclass
class ImBroken:
    when_will_i_get_fixed: datetime

ImBroken.from_dict({'when_will_i_get_fixed': 'soon 🤞'})
# ImBroken(when_will_i_get_fixed='soon 🤞')

```
