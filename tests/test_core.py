from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict
import textwrap

from fastclasses_json.api import dataclass_json
from fastclasses_json import core


# These tests are only keeping an eye on the innards. It's fine for them
# to break and need to be rewritten or deleted.


def test_to_dict_source():

    @dataclass
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


def test_to_dict_source__optional():

    @dataclass
    class A:
        x: Optional[int]

    # The `value = value` line aint great but oh well
    assert core._to_dict_source(A) == textwrap.dedent(
        """\
        def to_dict(self):
            result = {}
            value = self.x
            if value is not None:
                value = value
                result['x'] = value
            return result
        """
    )


def test_from_dict_source():

    @dataclass
    class A:
        x: int

    assert core._from_dict_source(A) == textwrap.dedent(
        """\
        def from_dict(cls, o, *, infer_missing):
            args = {}
            args['x'] = o.get('x')
            return cls(**args)
        """
    )


def test_from_dict_source__optional():

    @dataclass
    class A:
        x: Optional[int]

    assert core._from_dict_source(A) == textwrap.dedent(
        """\
        def from_dict(cls, o, *, infer_missing):
            args = {}
            args['x'] = o.get('x')
            return cls(**args)
        """
    )


def test_from_dict_source__default():

    @dataclass
    class A:
        x: int = 1

    assert core._from_dict_source(A) == textwrap.dedent(
        """\
        def from_dict(cls, o, *, infer_missing):
            args = {}
            if 'x' in o:
                args['x'] = o.get('x')
            return cls(**args)
        """
    )


def test_from_dict_source__list_nested():

    @dataclass
    class A:
        a: str

    @dataclass
    class B:
        a: List[A]

    assert core._from_dict_source(B) == textwrap.dedent(
        """\
        def from_dict(cls, o, *, infer_missing):
            args = {}
            value = o.get('a')
            if value is not None:
                value = [A._fastclasses_json_from_dict(__0) for __0 in value]
            args['a'] = value
            return cls(**args)
        """
    )


def test_from_dict_source__tuple():
    from typing import Tuple

    @dataclass
    class A:
        a: str

    @dataclass
    class B:
        b: str

    @dataclass_json
    @dataclass
    class C:
        c: Tuple[A, B]

    assert core._from_dict_source(C) == textwrap.dedent(
        """\
        def from_dict(cls, o, *, infer_missing):
            args = {}
            value = o.get('c')
            if value is not None:
                value = (__0:=(value),(A._fastclasses_json_from_dict(__0[0]),B._fastclasses_json_from_dict(__0[1]),))[1]
            args['c'] = value
            return cls(**args)
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
        def from_dict(cls, o, *, infer_missing):
            args = {}
            value = o.get('a')
            if value is not None:
                value = A(value)
            args['a'] = value
            return cls(**args)
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
