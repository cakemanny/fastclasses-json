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
