from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict
import textwrap

from fastclasses_json.api import dataclass_json
from fastclasses_json import core


def test_to_dict_source():

    class A:
        x: int

    assert core._to_dict_source(A) == textwrap.dedent(
        """\
        def to_dict(self):
            result = {}
            result['x'] = self.x
            return result
        """
    )


def test_from_dict_source():

    class A:
        x: int

    assert core._from_dict_source(A) == textwrap.dedent(
        """\
        def from_dict(cls, o):
            args = []
            args.append(o.get('x'))
            return cls(*args)
        """
    )


def test_from_dict_source__optional():

    class A:
        x: Optional[int]

    assert core._from_dict_source(A) == textwrap.dedent(
        """\
        def from_dict(cls, o):
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

    assert core._from_dict_source(B) == textwrap.dedent(
        """\
        def from_dict(cls, o):
            args = []
            value = o.get('a')
            if value is not None:
                value = [A._fastclasses_json_from_dict(__0) for __0 in value]
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

    assert core._from_dict_source(B) == textwrap.dedent(
        """\
        def from_dict(cls, o):
            args = []
            value = o.get('a')
            if value is not None:
                value = A(value)
            args.append(value)
            return cls(*args)
        """
    )


def test_expr_builder__list_enum():

    class A(Enum):
        X = 'ex'
        Y = 'why'

    t = List[A]

    builder = core.expr_builder(t)

    assert builder('XXX') == '[A(__0) for __0 in XXX]'


def test_expr_builder__list_list_enum():
    class A(Enum):
        X = 'ex'
        Y = 'why'

    t = List[List[A]]

    builder = core.expr_builder(t)

    assert builder('XXX') == '[[A(__1) for __1 in __0] for __0 in XXX]'


def test_expr_builder__list_dataclass():

    @dataclass
    class A:
        X = 'ex'
        Y = 'why'

    t = List[A]

    builder = core.expr_builder(t)

    assert builder('XXX') == \
        '[A._fastclasses_json_from_dict(__0) for __0 in XXX]'


def test_expr_builder__optional_enum():

    class A(Enum):
        X = 'ex'
        Y = 'why'

    t = Optional[A]

    builder = core.expr_builder(t)

    assert builder('XXX') == 'A(__0) if (__0:=(XXX)) is not None else None'


def test_expr_builder__dict_enum():

    class A(Enum):
        X = 'ex'
        Y = 'why'

    t = Dict[str, A]

    builder = core.expr_builder(t)

    assert builder('XXX') == '{__k0: A(__v0) for __k0,__v0 in (XXX).items()}'


def test_references_types__enum():

    class A(Enum):
        X = 'ex'
        Y = 'why'

    @dataclass
    class XX:
        a: A

    assert core.referenced_types(XX) == {'A': A}
