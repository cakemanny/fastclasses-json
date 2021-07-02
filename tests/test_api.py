from dataclasses import dataclass
from typing import Optional, List, Dict

from fastclasses_json.api import dataclass_json


def test_decorator():

    @dataclass_json
    @dataclass
    class A:
        x: int

    assert A.from_dict
    assert A(1).from_dict

    assert A.to_dict
    assert A(1).to_dict

    @dataclass_json()
    @dataclass
    class B:
        x: int

    assert B.from_dict
    assert B(1).from_dict

    assert B.to_dict
    assert B(1).to_dict


def test_to_dict():

    @dataclass_json
    @dataclass
    class A:
        x: int
        y: str

    assert A(5, 'hi').to_dict() == {'x': 5, 'y': 'hi'}


def test_from_dict():

    @dataclass_json
    @dataclass
    class A:
        x: int
        y: str

    assert A.from_dict({'x': 5, 'y': 'hi'}) == A(5, 'hi')


def test_to_json():

    @dataclass_json
    @dataclass
    class A:
        x: int
        y: str

    assert A(5, 'hi').to_json() == '{"x":5,"y":"hi"}'
    import textwrap
    assert A(5, 'hi').to_json(indent=2) == textwrap.dedent(
        """\
        {
          "x": 5,
          "y": "hi"
        }"""
    )


def test_from_json():

    @dataclass_json
    @dataclass
    class A:
        x: int
        y: str

    assert A.from_json('{"x":5,"y":"hi"}') == A(5, 'hi')


def test_to_dict__optional():

    @dataclass_json
    @dataclass
    class A:
        x: Optional[int]

    assert A(None).to_dict() == {}
    assert A(1).to_dict() == {'x': 1}


def test_from_dict__optional():

    @dataclass_json
    @dataclass
    class A:
        x: Optional[int]

    assert A.from_dict({}) == A(None)


def test_to_dict__nested():

    @dataclass
    class A:
        a: str

    @dataclass_json
    @dataclass
    class B:
        a: A

    assert B(A('xxx')).to_dict() == {
        'a': {
            'a': 'xxx'
        }
    }


def test_from_dict__nested():

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


def test_to_dict__list_nested():

    @dataclass
    class A:
        a: str

    @dataclass_json
    @dataclass
    class B:
        a: List[A]

    assert B([A('xxx'), A('yyy')]).to_dict() == {
        'a': [{
            'a': 'xxx',
        }, {
            'a': 'yyy',
        }]
    }


def test_from_dict__list_nested():

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


def test_to_dict__optional_nested():

    @dataclass
    class A:
        a: str

    @dataclass_json
    @dataclass
    class B:
        a: Optional[A]

    assert B(A('xxx')).to_dict() == {
        'a': {
            'a': 'xxx'
        }
    }
    assert B(None).to_dict() == {}


def test_from_dict__optional_nested():

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


def test_to_dict__optional_list_nested():

    @dataclass
    class A:
        a: str

    @dataclass_json
    @dataclass
    class B:
        a: Optional[List[A]]

    assert B([A('xxx'), A('yyy')]).to_dict() == {
        'a': [{
            'a': 'xxx',
        }, {
            'a': 'yyy',
        }]
    }
    assert B(None).to_dict() == {}


def test_from_dict__optional_list_nested():

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


def test_to_dict__string_type_name():

    assert B(A('yes')).to_dict() == {
        'A': {
            's': 'yes',
        }
    }


@dataclass_json
@dataclass
class D:
    C: Optional['C'] = None


@dataclass
class C:
    s: str


def test_from_dict__string_type_name__reverse_definition_order():

    assert D.from_dict({
        'C': {
            's': 'yes',
        }
    }) == D(C('yes'))


def test_to_dict__string_type_name__reverse_definition_order():

    assert D(C('yes')).to_dict() == {
        'C': {
            's': 'yes',
        }
    }


def test_to_dict__enum():
    from enum import Enum

    class A(Enum):
        X = 'ex'
        Y = 'why'

    @dataclass_json
    @dataclass
    class B:
        a: A

    assert B(A.X).to_dict() == {'a': 'ex'}
    assert B(A.Y).to_dict() == {'a': 'why'}


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


def test_to_dict__optional_enum():
    from enum import Enum

    class A(Enum):
        X = 'ex'
        Y = 'why'

    @dataclass_json
    @dataclass
    class B:
        a: Optional[A]

    assert B(A.X).to_dict() == {'a': 'ex'}
    assert B(A.Y).to_dict() == {'a': 'why'}
    assert B(None).to_dict() == {}


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
    assert B.from_dict({}) == B(None)


def test_to_dict__list_of_enum():
    from enum import Enum

    class A(Enum):
        X = 'ex'
        Y = 'why'

    @dataclass_json
    @dataclass
    class B:
        a: List[A]

    assert B([A.X]).to_dict() == {'a': ['ex']}
    assert B([A.Y]).to_dict() == {'a': ['why']}


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


def test_to_dict__dict_of_enum():
    from enum import Enum

    class A(Enum):
        X = 'ex'
        Y = 'why'

    @dataclass_json
    @dataclass
    class B:
        a: Dict[str, A]

    assert B({'marky': A.X}).to_dict() == {'a': {'marky': 'ex'}}
    assert B({'marky': A.Y}).to_dict() == {'a': {'marky': 'why'}}


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


def test_to_dict__date():
    from datetime import date

    @dataclass_json
    @dataclass
    class A:
        x: date

    assert A(date(2021, 6, 17)).to_dict() == {'x': "2021-06-17"}


def test_from_dict__date():
    from datetime import date

    @dataclass_json
    @dataclass
    class A:
        x: date

    assert A.from_dict({'x': "2021-06-17"}) == A(date(2021, 6, 17))


def test_from_dict__datetime():
    from datetime import datetime, timezone

    @dataclass_json
    @dataclass
    class A:
        x: datetime

    assert A.from_dict({'x': "2021-06-17"}) == A(datetime(2021, 6, 17))

    assert A.from_dict({'x': "2021-06-17T10:00:00"}) \
        == A(datetime(2021, 6, 17, 10, 0, 0,))

    assert A.from_dict({'x': "2021-06-17T10:00:00+00:00"}) \
        == A(datetime(2021, 6, 17, 10, 0, 0, tzinfo=timezone.utc))
    assert A.from_dict({'x': "2021-06-17T10:00:00Z"}) \
        == A(datetime(2021, 6, 17, 10, 0, 0, tzinfo=timezone.utc))
