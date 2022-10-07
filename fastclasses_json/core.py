from collections import abc
from dataclasses import is_dataclass, fields as dataclass_fields, MISSING
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID
import json
import sys
import types
import typing
import warnings

from .utils import issubclass_safe

try:
    import dateutil.parser
    assert dateutil.parser
    HAS_DATEUTIL = True
except Exception:
    HAS_DATEUTIL = False

PY_37 = sys.version_info[:2] == (3, 7)

# We have to write the condition like this for mypy to recognise it
if sys.version_info >= (3, 8):
    from typing import get_origin as typing_get_origin
    from typing import get_args as typing_get_args
else:
    from typing_extensions import get_origin as typing_get_origin
    from typing_extensions import get_args as typing_get_args


_FROM = 1
_TO = 2


def _process_class(cls, **options):

    if not is_dataclass(cls):
        raise TypeError("must be called with a dataclass type")

    _process_class_internal(cls, options=options)

    def from_dict(cls, *args, **kwargs):
        inst = getattr(cls, _from_dict_func(options))(*args, **kwargs)
        cls.from_dict = getattr(cls, _from_dict_func(options))
        return inst

    def to_dict(self, *args, **kwargs):
        d = getattr(self, _to_dict_func(options))(*args, **kwargs)
        cls.to_dict = getattr(cls, _to_dict_func(options))
        return d

    cls.from_dict = classmethod(from_dict)
    cls.to_dict = to_dict

    def from_json(cls, json_data, infer_missing=True):
        return cls.from_dict(
            json.loads(json_data), infer_missing=infer_missing
        )

    def to_json(self, *, separators=None, indent=None):
        if indent is None and separators is None:
            separators = (',', ':')
        return json.dumps(self.to_dict(), separators=separators, indent=indent)

    cls.from_json = classmethod(from_json)
    cls.to_json = to_json
    return cls


def _from_dict_func(options):
    if options:
        return '_fastclasses_json_from_dict_%x' % _hash_options(options)
    return '_fastclasses_json_from_dict'


def _to_dict_func(options):
    if options:
        return '_fastclasses_json_to_dict_%x' % _hash_options(options)
    return '_fastclasses_json_to_dict'


def _hash_options(options):
    return abs(hash(tuple(options.items())))


def _process_class_internal(cls, options):

    # Delay the building of our from_dict method until it is first called.
    # This allows the compilation to reference classes defined later in
    # the module.
    def _temp_from_dict(cls, *args, **kwarg):
        _replace_from_dict(cls, options, _from_dict_func(options))
        return getattr(cls, _from_dict_func(options))(*args, **kwarg)

    setattr(cls, _from_dict_func(options), classmethod(_temp_from_dict))

    def _temp_to_dict(self, *args, **kwargs):
        _replace_to_dict(cls, options, _to_dict_func(options))
        return getattr(self, _to_dict_func(options))(*args, **kwargs)

    setattr(cls, _to_dict_func(options), _temp_to_dict)

    return cls


def _replace_from_dict(cls, options, from_dict='from_dict'):

    from_dict_src = _from_dict_source(cls, options)
    from_dict_module = compile(
        from_dict_src, '<fastclass_generated_code>', 'exec'
    )
    from_dict_code = [
        const for const in from_dict_module.co_consts
        if isinstance(const, types.CodeType)
    ][0]

    the_globals = {
        # use the defining module's globals
        **sys.modules[cls.__module__].__dict__,
        # along with any decoders
        **decoders(cls),
        # along with types we use for the conversion
        **referenced_types(cls),
    }
    if HAS_DATEUTIL:
        the_globals['dateutil'] = dateutil

    from_dict_func = types.FunctionType(
        from_dict_code,
        the_globals,
        from_dict,
    )
    from_dict_func.__kwdefaults__ = {'infer_missing': True}

    setattr(cls, from_dict, classmethod(from_dict_func))


def _replace_to_dict(cls, options, to_dict='to_dict'):

    to_dict_src = _to_dict_source(cls, options)
    to_dict_module = compile(
        to_dict_src, '<fastclass_generated_code>', 'exec'
    )
    to_dict_code = [
        const for const in to_dict_module.co_consts
        if isinstance(const, types.CodeType)
    ][0]

    the_globals = {
        # use the defining module's globals
        **sys.modules[cls.__module__].__dict__,
        # along with any encoders
        **encoders(cls),
    }

    to_dict_func = types.FunctionType(
        to_dict_code,
        the_globals,
        to_dict,
    )

    setattr(cls, to_dict, to_dict_func)


def _from_dict_source(cls, options=None):

    lines = [
        'def from_dict(cls, o, *, infer_missing):',
        '    args = {}',
    ]

    fields_by_name = {f.name: f for f in dataclass_fields(cls)}

    for name, field_type in typing.get_type_hints(cls).items():

        # pop off the top layer of optional, since we are using o.get
        if typing_get_origin(field_type) == typing.Union:
            field_type = typing_get_args(field_type)[0]

        field = fields_by_name[name]

        input_name = deduce_serialised_name(name, options, field, cls)

        has_default = (
            field.default is not MISSING
            or field.default_factory is not MISSING
        )
        use_defaults = True  # TODO: get this from a config option
        use_default = has_default and use_defaults

        access = f'o.get({input_name!r})'

        transform = expr_builder_from(field_type, options)
        if has_meta(field, 'decoder'):
            transform = decoder_expr(name)

        if transform('x') != 'x':
            lines.append(f'    value = {access}')
            lines.append(f'    if value is not None:')  # noqa: F541
            lines.append(f'        value = ' + transform('value'))  # noqa: E501,F541
            if use_default:
                # has a default, so no need to put in args
                lines.append(f'    if {input_name!r} in o:')
                lines.append(f'        args[{name!r}] = value')
            else:
                lines.append(f'    args[{name!r}] = value')
        else:
            if use_default:
                # has a default, so no need to put in args
                lines.append(f'    if {input_name!r} in o:')
                lines.append(f'        args[{name!r}] = {access}')
            else:
                lines.append(f'    args[{name!r}] = {access}')
    lines.append('    return cls(**args)')
    lines.append('')
    return '\n'.join(lines)


def _to_dict_source(cls, options=None):

    lines = [
        'def to_dict(self):',
        '    result = {}',
    ]

    # TODO: option for including Nones or not
    INCLUDE_NONES = False

    fields_by_name = {f.name: f for f in dataclass_fields(cls)}

    for name, field_type in typing.get_type_hints(cls).items():

        access = f'self.{name}'

        transform = expr_builder_to(field_type, options)

        # custom encoder and decoder routines
        field = fields_by_name[name]
        if has_meta(field, 'encoder'):
            transform = encoder_expr(name)

        # custom mapping of dataclass fieldnames to json field names
        output_name = deduce_serialised_name(name, options, field, cls)

        if transform('x') != 'x':
            # since we have an is not none check, elide the first level
            # of optional
            if (typing_get_origin(field_type) == typing.Union
                    # This is a bit yuk. Premature optimization 🙄
                    and transform('x') == expr_builder_to(field_type, options)('x')):
                transform = expr_builder_to(typing_get_args(field_type)[0], options)
            lines.append(f'    value = {access}')
            lines.append(f'    if value is not None:')  # noqa: F541
            lines.append(f'        value = ' + transform('value'))  # noqa: E501,F541
            if INCLUDE_NONES:
                lines.append(f'    result[{output_name!r}] = value')
            else:
                lines.append(f'        result[{output_name!r}] = value')
        else:
            lines.append(f'    result[{output_name!r}] = {access}')

    lines.append('    return result')
    lines.append('')
    return '\n'.join(lines)


def deduce_serialised_name(name, options, field, cls):
    serialised_name = name
    if options and options.get('field_name_transform'):
        serialised_name = options['field_name_transform'](name)
        if not isinstance(serialised_name, str):
            raise TypeError(
                "fastclasses_json, result of field_name_transform must be str: "
                f"{options['field_name_transform'].__name__}"
            )
    if has_meta(field, 'field_name'):
        serialised_name = field.metadata['fastclasses_json']['field_name']
        if not isinstance(serialised_name, str):
            raise TypeError(
                "fastclasses_json, field_name must be str: "
                f"{cls.__name__}.{name}"
            )
    return serialised_name


def encoders(cls):
    result = {}
    for field in dataclass_fields(cls):
        if has_meta(field, 'encoder'):
            sym = f'{field.name}#encoder'
            result[sym] = field.metadata['fastclasses_json']['encoder']
    return result


def decoders(cls):
    result = {}
    for field in dataclass_fields(cls):
        if has_meta(field, 'decoder'):
            sym = f'{field.name}#decoder'
            result[sym] = field.metadata['fastclasses_json']['decoder']
    return result


def has_meta(field, meta):
    if field.metadata and field.metadata.get('fastclasses_json', {}).get(meta):
        return True
    return False


def encoder_expr(name):
    # this funny x#encoder will have been placed in globals
    return lambda expr: f'globals()["{name}#encoder"]({expr})'


def decoder_expr(name):
    # this funny x#decoder will have been placed in globals
    return lambda expr: f'globals()["{name}#decoder"]({expr})'


def expr_builder_from(t: type, options, depth=0):
    return expr_builder(t, options, depth, direction=_FROM)


def expr_builder_to(t: type, options, depth=0):
    return expr_builder(t, options, depth, direction=_TO)


def expr_builder(t: type, options=None, depth=0, direction=_FROM):
    def identity(expr):
        return expr

    # Container types

    origin = typing_get_origin(t)

    if origin == typing.Union:
        type_arg = typing_get_args(t)[0]
        inner = expr_builder(type_arg, options, depth + 1, direction)

        def f(expr):
            t0 = f'__{depth}'
            if PY_37:
                # Lazy solution for py37'ers
                return f'{inner(expr)} if ({expr}) is not None else None'
            return f'{inner(t0)} if ({t0}:=({expr})) is not None else None'

        return f
    elif origin == tuple and typing_get_args(t):
        type_args = typing_get_args(t)
        # Tuple[A, ...] means an any-length tuple of all As
        if type_args[1:] == (Ellipsis,):
            inner = expr_builder(type_args[0], options, depth + 1, direction)

            def f(expr):
                t0 = f'__{depth}'
                return f'tuple({inner(t0)} for {t0} in {expr})'
            return f
        else:
            inners = [
                expr_builder(type_arg, options, depth + 1, direction)
                for type_arg in type_args
            ]

            def f(expr):
                t0 = f'__{depth}'

                e1 = f'{t0}:=({expr})'
                parts = ['(']
                for i, inner in enumerate(inners):
                    xx = f'{t0}[{i}]'
                    if PY_37:
                        xx = f'({expr})[{i}]'
                    parts.append(f'{inner(xx)},')
                parts.append(')')
                e2 = ''.join(parts)
                if PY_37:
                    return e2
                # e1 is just for evaluating expr no more than once
                # e2 is the actual result
                return f'({e1},{e2})[1]'
            return f
    elif (issubclass_safe(origin, abc.Sequence)
          and issubclass_safe(list, origin)
          and typing_get_args(t)):
        type_arg = typing_get_args(t)[0]
        inner = expr_builder(type_arg, options, depth + 1, direction)

        def f(expr):
            t0 = f'__{depth}'
            return f'[{inner(t0)} for {t0} in {expr}]'
        return f
    elif (issubclass_safe(origin, abc.Mapping)
          and issubclass_safe(dict, origin)
          and typing_get_args(t)):
        key_type, value_type = typing_get_args(t)

        # TODO: Enums, dates and decimals should be trivial to add here
        if key_type not in (str, int, float, bool, UUID):
            warnings.warn(f'to_json will not work for dict with key: {t}')
            return identity

        inner = expr_builder(value_type, options, depth + 1, direction)

        key_func = expr_builder(key_type, options, depth + 1, direction)
        if direction == _FROM:
            if key_type is str:
                pass
            elif key_type in (int, float):
                key_func = lambda k: f'{key_type.__name__}({k})'
            elif key_type is bool:
                # The double evaluation of k is fine since k always
                # an iteration variable in f below
                key_func = lambda k: f'({k} is True or {k} == "true")'

        def f(expr):
            k0 = f'__k{depth}'
            v0 = f'__v{depth}'
            return (
                '{'
                + f'{key_func(k0)}: {inner(v0)} for {k0},{v0} in ({expr}).items()'
                + '}'
            )
        return f

    # Pleb types

    if False:
        # Call to_dict method whenever it exists?
        # Probably not. It could be surprising.
        # We should use a protocol class if possible to be able to
        # check it in referenced_types as well
        import inspect
        if direction == _FROM:
            if hasattr(t, 'from_dict') and inspect.ismethod(t.from_dict):
                return lambda expr: f'{t.__name__}.from_dict({expr})'
        else:
            if hasattr(t, 'to_dict') and inspect.isfunction(t.to_dict):
                return lambda expr: f'({expr}).to_dict()'

    if is_dataclass(t):
        # Give indirectly referenced dataclasses a to_dict method without
        # trashing their public API
        if not hasattr(t, _from_dict_func(options)):
            _process_class_internal(t, options)

        if direction == _FROM:
            def f(expr):
                return f'{t.__name__}.{_from_dict_func(options)}({expr})'
            return f
        else:
            return lambda expr: f'({expr}).{_to_dict_func(options)}()'
    elif issubclass_safe(t, Enum):
        if direction == _FROM:
            return lambda expr: f'{t.__name__}({expr})'
        else:
            return lambda expr: f'({expr}).value'

    if issubclass_safe(t, datetime):
        if direction == _FROM:
            def f(expr):
                t0 = f'__{depth}'
                if HAS_DATEUTIL and issubclass_safe(datetime, t):
                    return f'dateutil.parser.isoparse({expr})'
                else:
                    if PY_37:
                        return (f'{t.__name__}.fromisoformat('
                                f'({expr})[:-1]+"+00:00" if ({expr})[-1]=="Z" '
                                f'else ({expr})'
                                ')')
                    return (f'{t.__name__}.fromisoformat('
                            f'{t0}[:-1]+"+00:00" if ({t0}:={expr})[-1]=="Z" '
                            f'else {t0}'
                            ')')
            return f
        else:
            return lambda expr: f'({expr}).isoformat()'
    if issubclass_safe(t, date):
        if direction == _FROM:
            # TODO: use dateutil.parser.isoparse if available?
            return lambda expr: f'{t.__name__}.fromisoformat({expr})'
        else:
            return lambda expr: f'({expr}).isoformat()'

    if issubclass_safe(t, Decimal):
        if direction == _FROM:
            return lambda expr: f'{t.__name__}(str({expr}))'
        else:
            return lambda expr: f'str({expr})'

    if issubclass_safe(t, UUID):
        if direction == _FROM:
            return lambda expr: f'{t.__name__}({expr})'
        else:
            return lambda expr: f'str({expr})'

    return identity


def referenced_types(cls):

    # If we support tuples or unions properly, this needsto return
    # multiple types
    def extract_types(t):
        origin = typing_get_origin(t)
        if origin == tuple and typing_get_args(t):
            xs = tuple()
            for type_arg in typing_get_args(t):
                xs += extract_types(type_arg)
            return xs
        if (origin == typing.Union
                or issubclass_safe(origin, abc.Sequence)) and typing_get_args(t):
            type_arg = typing_get_args(t)[0]
            return extract_types(type_arg)
        elif issubclass_safe(origin, abc.Mapping) and typing_get_args(t):
            key_type_arg, value_type_arg = typing_get_args(t)
            if key_type_arg is UUID:
                return (UUID,) + extract_types(value_type_arg)
            return extract_types(value_type_arg)
        elif is_dataclass(t) or issubclass_safe(
            t, (Enum, date, datetime, Decimal, UUID)
        ):
            return (t,)
        return tuple()

    types = {}
    for _, field_type in typing.get_type_hints(cls).items():
        for t in extract_types(field_type):
            types[t.__name__] = t
    return types
