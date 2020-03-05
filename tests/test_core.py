from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from fastclasses_json import core


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

    assert builder('XXX') == '[A.from_dict(__0) for __0 in XXX]'


def test_expr_builder__optional_enum():

    class A(Enum):
        X = 'ex'
        Y = 'why'

    t = Optional[A]

    builder = core.expr_builder(t)

    assert builder('XXX') == 'A(__0) if (__0:=(XXX)) is not None else None'


def test_references_types__enum():

    class A(Enum):
        X = 'ex'
        Y = 'why'

    @dataclass
    class XX:
        a: A

    assert core.referenced_types(XX) == {'A': A}
