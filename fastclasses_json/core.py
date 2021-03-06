from dataclasses import is_dataclass
from enum import Enum
import typing
import warnings

from .utils import issubclass_safe


def expr_builder(t: type, depth=0):
    def identity(expr):
        return expr

    origin = typing.get_origin(t)

    if origin == typing.Union:
        type_arg = typing.get_args(t)[0]
        inner = expr_builder(type_arg, depth + 1)

        def f(expr):
            t0 = f'__{depth}'
            return f'{inner(t0)} if ({t0}:=({expr})) is not None else None'

        return f
    elif origin == list:
        type_arg = typing.get_args(t)[0]
        inner = expr_builder(type_arg, depth + 1)

        def f(expr):
            t0 = f'__{depth}'
            return f'[{inner(t0)} for {t0} in {expr}]'
        return f
    elif origin == dict:
        key_type, value_type = typing.get_args(t)

        if not issubclass_safe(key_type, str):
            warnings.warn(f'to_json will not work for non-str key dict: {t}')
            return identity

        inner = expr_builder(value_type, depth + 1)

        def f(expr):
            k0 = f'__k{depth}'
            v0 = f'__v{depth}'
            return (
                '{'
                + f'{k0}: {inner(v0)} for {k0},{v0} in ({expr}).items()'
                + '}'
            )
        return f
    elif is_dataclass(t):
        def f(expr):
            return f'{t.__name__}.from_dict({expr})'
        return f
    elif issubclass_safe(t, Enum):
        def f(expr):
            return f'{t.__name__}({expr})'
        return f

    return identity


def referenced_types(cls):

    def extract_type(t):
        origin = typing.get_origin(t)
        if origin == typing.Union or origin == list:
            type_arg = typing.get_args(t)[0]
            return extract_type(type_arg)
        elif origin == dict:
            value_type_arg = typing.get_args(t)[1]
            return extract_type(value_type_arg)
        elif is_dataclass(t) or issubclass_safe(t, Enum):
            return t
        return None

    types = {}
    for _, field_type in typing.get_type_hints(cls).items():
        t = extract_type(field_type)
        if t is not None:
            types[t.__name__] = t
    return types
