from dataclasses import dataclass
from typing import Optional, List, Dict
import textwrap

from fastclasses_json import api
from fastclasses_json.api import dataclass_json


def test_decorator():

    @dataclass_json
    @dataclass
    class A:
        x: int

    assert A.from_dict
    assert A(1).from_dict

    @dataclass_json()
    @dataclass
    class B:
        x: int

    assert B.from_dict
    assert B(1).from_dict


def test_from_dict_source():

    class A:
        x: int

    assert api._from_dict_source(A) == textwrap.dedent(
        """\
        def from_dict(cls, o, ):
            args = []
            args.append(o.get('x'))
            return cls(*args)
        """
    )


def test_from_dict_source__optional():

    class A:
        x: Optional[int]

    assert api._from_dict_source(A) == textwrap.dedent(
        """\
        def from_dict(cls, o, ):
            args = []
            args.append(o.get('x'))
            return cls(*args)
        """
    )


def test_from_dict_source__list_nested():

    @dataclass_json
    @dataclass
    class A:
        a: str

    @dataclass_json
    @dataclass
    class B:
        a: List[A]

    assert api._from_dict_source(B) == textwrap.dedent(
        """\
        def from_dict(cls, o, A):
            args = []
            value = o.get('a')
            if value is not None:
                value = [A.from_dict(__0) for __0 in value]
            args.append(value)
            return cls(*args)
        """
    )


def test_from_dict_source__enum():
    from enum import Enum

    class A(Enum):
        X = 'ex'
        Y = 'why'

    @dataclass_json
    @dataclass
    class B:
        a: A

    assert api._from_dict_source(B) == textwrap.dedent(
        """\
        def from_dict(cls, o, A):
            args = []
            value = o.get('a')
            if value is not None:
                value = A(value)
            args.append(value)
            return cls(*args)
        """
    )


def test_from_dict():

    @dataclass_json
    @dataclass
    class A:
        x: int
        y: str

    assert A.from_dict({'x': 5, 'y': 'hi'}) == A(5, 'hi')


def test_from_dict__optional():

    @dataclass_json
    @dataclass
    class A:
        x: Optional[int]

    assert A.from_dict({}) == A(None)


def test_from_dict__nested():

    @dataclass_json
    @dataclass
    class A:
        a: str

    @dataclass_json
    @dataclass
    class B:
        a: A

    assert B.from_dict({
        'a': {
            'a': 'xxx'
        }
    }) == B(A('xxx'))


def test_from_dict__list_nested():

    @dataclass_json
    @dataclass
    class A:
        a: str

    @dataclass_json
    @dataclass
    class B:
        a: List[A]

    assert B.from_dict({
        'a': [{
            'a': 'xxx',
        }, {
            'a': 'yyy',
        }]
    }) == B([A('xxx'), A('yyy')])


def test_from_dict__optional_nested():

    @dataclass_json
    @dataclass
    class A:
        a: str

    @dataclass_json
    @dataclass
    class B:
        a: Optional[A]

    assert B.from_dict({
        'a': {
            'a': 'xxx'
        }
    }) == B(A('xxx'))


def test_from_dict__optional_list_nested():

    @dataclass_json
    @dataclass
    class A:
        a: str

    @dataclass_json
    @dataclass
    class B:
        a: Optional[List[A]]

    assert B.from_dict({
        'a': [{
            'a': 'xxx',
        }, {
            'a': 'yyy',
        }]
    }) == B([A('xxx'), A('yyy')])


def test_from_dict__optional_list_nested_with_defaults():

    @dataclass_json
    @dataclass
    class A:
        a: str

    @dataclass_json
    @dataclass
    class B:
        a: Optional[List[A]] = None

    assert B.from_dict({
        'a': [{
            'a': 'xxx',
        }, {
            'a': 'yyy',
        }]
    }) == B([A('xxx'), A('yyy')])


# These have to be defined at the module level since that's where string type
# hints are evaluated, they are for the string_type_name

@dataclass_json
@dataclass
class A:
    s: str


@dataclass_json
@dataclass
class B:
    A: Optional['A'] = None


def test_from_dict__string_type_name():

    assert B.from_dict({
        'A': {
            's': 'yes',
        }
    }) == B(A('yes'))


@dataclass_json
@dataclass
class D:
    C: Optional['C'] = None


@dataclass_json
@dataclass
class C:
    s: str


def test_from_dict__string_type_name__reverse_definition_order():

    assert D.from_dict({
        'C': {
            's': 'yes',
        }
    }) == D(C('yes'))


def test_from_dict__enum():
    from enum import Enum

    class A(Enum):
        X = 'ex'
        Y = 'why'

    @dataclass_json
    @dataclass
    class B:
        a: A

    assert B.from_dict({'a': 'ex'}) == B(A.X)
    assert B.from_dict({'a': 'why'}) == B(A.Y)


def test_from_dict__optional_enum():
    from enum import Enum

    class A(Enum):
        X = 'ex'
        Y = 'why'

    @dataclass_json
    @dataclass
    class B:
        a: Optional[A]

    assert B.from_dict({'a': 'ex'}) == B(A.X)
    assert B.from_dict({'a': 'why'}) == B(A.Y)


def test_from_dict__list_of_enum():
    from enum import Enum

    class A(Enum):
        X = 'ex'
        Y = 'why'

    @dataclass_json
    @dataclass
    class B:
        a: List[A]

    assert B.from_dict({'a': ['ex']}) == B([A.X])
    assert B.from_dict({'a': ['why']}) == B([A.Y])


def test_from_dict__dict_of_enum():
    from enum import Enum

    class A(Enum):
        X = 'ex'
        Y = 'why'

    @dataclass_json
    @dataclass
    class B:
        a: Dict[str, A]

    assert B.from_dict({'a': {'marky': 'ex'}}) == B({'marky': A.X})
    assert B.from_dict({'a': {'marky': 'why'}}) == B({'marky': A.Y})
