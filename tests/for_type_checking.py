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

# erm... change this to True when playing with the mypy module
if typing.TYPE_CHECKING and False:
    # Should/can we have some asserts in here...? 🤷
    reveal_type(a.to_dict)  # noqa: F821
    reveal_type(A.from_dict)  # noqa: F821
    reveal_type(A.from_json)  # noqa: F821
    reveal_type(A.from_dict({'x': 'hi'}))  # noqa: F821
    reveal_type(A.from_json('{"x":"hi"}'))  # noqa: F821
    reveal_type(A.to_json)  # noqa: F821
print(a.to_json())
print(A.from_dict({'x': 'hi'}))
print(A.from_json('{"x":"hi"}'))
print(A.from_json(b'{"x":"hi"}'))
