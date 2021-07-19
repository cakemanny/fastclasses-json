from dataclasses import dataclass
from fastclasses_json import dataclass_json
import typing


@dataclass_json
@dataclass
class A:
    x: str


@dataclass_json
@dataclass
class B:
    y: int


a = A("hi")

if typing.TYPE_CHECKING:
    reveal_type(a.to_dict)
    reveal_type(A.from_dict)
    reveal_type(A.from_dict({'x': 'hi'}))
    reveal_type(A.from_json('{"x":"hi"}'))
print(a.to_json())
print(A.from_dict({'x': 'hi'}))
print(A.from_json('{"x":"hi"}'))
