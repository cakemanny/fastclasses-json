from dataclasses import is_dataclass, fields as dataclass_fields, MISSING
from enum import Enum
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


_FROM = 1
_TO = 2


def _process_class(cls):
    import json

    _process_class_internal(cls)

    def from_dict(cls, *args, **kwargs):
        inst = cls._fastclasses_json_from_dict(*args, **kwargs)
        cls.from_dict = cls._fastclasses_json_from_dict
        return inst

    def to_dict(self, *args, **kwargs):
        d = self._fastclasses_json_to_dict(*args, **kwargs)
        cls.to_dict = cls._fastclasses_json_to_dict
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


def _process_class_internal(cls):

    # Delay the building of our from_dict method until it is first called.
    # This allows the compilation to reference classes defined later in
    # the module.
    def _temp_from_dict(cls, *args, **kwarg):
        _replace_from_dict(cls, '_fastclasses_json_from_dict')
        return cls._fastclasses_json_from_dict(*args, **kwarg)

    cls._fastclasses_json_from_dict = classmethod(_temp_from_dict)

    def _temp_to_dict(self, *args, **kwargs):
        _replace_to_dict(cls, '_fastclasses_json_to_dict')
        return self._fastclasses_json_to_dict(*args, **kwargs)

    cls._fastclasses_json_to_dict = _temp_to_dict

    return cls


def _replace_from_dict(cls, from_dict='from_dict'):

    from_dict_src = _from_dict_source(cls)
    from_dict_module = compile(
        from_dict_src, '<fastclass_generated_code>', 'exec'
    )
    from_dict_code = [
        const for const in from_dict_module.co_consts
        if isinstance(const, types.CodeType)
    ][0]

    the_globals = {
        # use the defining modules globals
        **sys.modules[cls.__module__].__dict__,
        # along with any decoders
        **decoders(cls),
        # along with types we use for the conversion
        **referenced_types(cls),
    }

    from_dict_func = types.FunctionType(
        from_dict_code,
        the_globals,
        from_dict,
    )
    from_dict_func.__kwdefaults__ = {'infer_missing': True}

    setattr(cls, from_dict, classmethod(from_dict_func))


def _replace_to_dict(cls, to_dict='to_dict'):

    to_dict_src = _to_dict_source(cls)
    to_dict_module = compile(
        to_dict_src, '<fastclass_generated_code>', 'exec'
    )
    to_dict_code = [
        const for const in to_dict_module.co_consts
        if isinstance(const, types.CodeType)
    ][0]

    the_globals = {
        # use the defining modules globals
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


def _from_dict_source(cls):

    lines = [
        'def from_dict(cls, o, *, infer_missing):',
        '    args = {}',
    ]

    if HAS_DATEUTIL:
        lines.insert(1, '    import dateutil.parser')

    fields_by_name = {f.name: f for f in dataclass_fields(cls)}

    for name, field_type in typing.get_type_hints(cls).items():

        # pop off the top layer of optional, since we are using o.get
        if typing.get_origin(field_type) == typing.Union:
            field_type = typing.get_args(field_type)[0]

        field = fields_by_name[name]

        input_name = name
        if has_meta(field, 'field_name'):
            input_name = field.metadata['fastclasses_json']['field_name']
            if not isinstance(input_name, str):
                raise TypeError(
                    "fastclasses_json, field_name must be str: "
                    f"{cls.__name__}.{name}"
                )

        has_default = (
            field.default is not MISSING
            or field.default_factory is not MISSING
        )
        use_defaults = True  # TODO: get this from a config option
        use_default = has_default and use_defaults

        access = f'o.get({input_name!r})'

        transform = expr_builder_from(field_type)
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


def _to_dict_source(cls):

    lines = [
        'def to_dict(self):',
        '    result = {}',
    ]

    # TODO: option for including Nones or not
    INCLUDE_NONES = False

    fields_by_name = {f.name: f for f in dataclass_fields(cls)}

    for name, field_type in typing.get_type_hints(cls).items():

        access = f'self.{name}'

        transform = expr_builder_to(field_type)

        # custom encoder and decoder routines
        field = fields_by_name[name]
        if has_meta(field, 'encoder'):
            transform = encoder_expr(name)

        # custom mapping of dataclass fieldnames to json field names
        output_name = name
        if has_meta(field, 'field_name'):
            output_name = field.metadata['fastclasses_json']['field_name']
            if not isinstance(output_name, str):
                raise TypeError(
                    "fastclasses_json, field_name must be str: "
                    f"{cls.__name__}.{name}"
                )

        if transform('x') != 'x':
            # since we have an is not none check, elide the first level
            # of optional
            if typing.get_origin(field_type) == typing.Union:
                transform = expr_builder_to(typing.get_args(field_type)[0])
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


def expr_builder_from(t: type, depth=0):
    return expr_builder(t, depth, direction=_FROM)


def expr_builder_to(t: type, depth=0):
    return expr_builder(t, depth, direction=_TO)


def expr_builder(t: type, depth=0, direction=_FROM):
    def identity(expr):
        return expr

    origin = typing.get_origin(t)

    if origin == typing.Union:
        type_arg = typing.get_args(t)[0]
        inner = expr_builder(type_arg, depth + 1, direction)

        def f(expr):
            t0 = f'__{depth}'
            return f'{inner(t0)} if ({t0}:=({expr})) is not None else None'

        return f
    elif origin == list and typing.get_args(t):
        type_arg = typing.get_args(t)[0]
        inner = expr_builder(type_arg, depth + 1, direction)

        def f(expr):
            t0 = f'__{depth}'
            return f'[{inner(t0)} for {t0} in {expr}]'
        return f
    elif origin == dict and typing.get_args(t):
        key_type, value_type = typing.get_args(t)

        if not issubclass_safe(key_type, str):
            warnings.warn(f'to_json will not work for non-str key dict: {t}')
            return identity

        inner = expr_builder(value_type, depth + 1, direction)

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
        # Give indirectly referenced dataclasses a to_dict method without
        # trashing their public API
        if not hasattr(t, '_fastclasses_json_from_dict'):
            _process_class_internal(t)

        # TODO: consider calling to_dict, from_dict if they are there
        # i.e. create a way for serialization to be overridden

        if direction == _FROM:
            def f(expr):
                return f'{t.__name__}._fastclasses_json_from_dict({expr})'
            return f
        else:
            def f(expr):
                # or should be have a function that takes the class and its
                # type?
                return f'({expr})._fastclasses_json_to_dict()'
            return f
    elif issubclass_safe(t, Enum):
        if direction == _FROM:
            def f(expr):
                return f'{t.__name__}({expr})'
            return f
        else:
            def f(expr):
                return f'({expr}).value'
            return f

    from datetime import date, datetime
    if issubclass_safe(t, datetime):
        if direction == _FROM:
            def f(expr):
                t0 = f'__{depth}'
                if HAS_DATEUTIL:
                    # doesn't work for subclasses... but
                    return f'dateutil.parser.isoparse({expr})'
                else:
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

    from decimal import Decimal
    if issubclass_safe(t, Decimal):
        if direction == _FROM:
            return lambda expr: f'{t.__name__}(str({expr}))'
        else:
            return lambda expr: f'str({expr})'

    from uuid import UUID
    if issubclass_safe(t, UUID):
        if direction == _FROM:
            return lambda expr: f'{t.__name__}({expr})'
        else:
            return lambda expr: f'str({expr})'

    return identity


def referenced_types(cls):
    from datetime import date, datetime
    from decimal import Decimal
    from uuid import UUID

    def extract_type(t):
        origin = typing.get_origin(t)
        if (origin == typing.Union or origin == list) and typing.get_args(t):
            type_arg = typing.get_args(t)[0]
            return extract_type(type_arg)
        elif origin == dict and typing.get_args(t):
            value_type_arg = typing.get_args(t)[1]
            return extract_type(value_type_arg)
        elif is_dataclass(t) or issubclass_safe(
            t, (Enum, date, datetime, Decimal, UUID)
        ):
            return t
        return None

    types = {}
    for _, field_type in typing.get_type_hints(cls).items():
        t = extract_type(field_type)
        if t is not None:
            types[t.__name__] = t
    return types
