from dataclasses import dataclass, is_dataclass
import sys
import types
import typing


def dataclass_json(cls=None):

    def _wrap():
        return _process_class(cls)

    if cls is not None:
        return _wrap()
    return _wrap


def _f():
    return


def _process_class(cls):
    # ensure this be a dataclass
    cls = dataclass(cls)

    from_dict_src = _from_dict_source(cls)
    from_dict_module = compile(
        from_dict_src, '<fastclass_generated_code>', 'exec'
    )
    from_dict_code = [
        const for const in from_dict_module.co_consts
        if isinstance(const, types.CodeType)
    ][0]

    argdefs = tuple(_referenced_types(cls).values())

    from_dict_func = types.FunctionType(
        from_dict_code,
        # use the defining modules globals
        sys.modules[cls.__module__].__dict__,
        'from_dict',
        argdefs=argdefs,
    )

    cls.from_dict = classmethod(from_dict_func)

    return cls


def _referenced_types(cls):
    # add typenames as args for referenced dataclasses
    dc_types = {}
    for _, field_type in typing.get_type_hints(cls).items():

        origin = typing.get_origin(field_type)
        type_arg = None

        if typing.get_origin(field_type) == typing.Union:
            field_type = typing.get_args(field_type)[0]
            origin = typing.get_origin(field_type)

        if origin == list:
            type_arg = typing.get_args(field_type)[0]
            if is_dataclass(type_arg):
                dc_types[type_arg.__name__] = type_arg

        if is_dataclass(field_type):
            dc_types[field_type.__name__] = field_type
    return dc_types


def _from_dict_source(cls):

    dc_typenames = ','.join(_referenced_types(cls).keys())

    lines = [
        f'def from_dict(cls, o, {dc_typenames}):',
        f'    args = []',
    ]
    for name, field_type in typing.get_type_hints(cls).items():

        origin = typing.get_origin(field_type)
        type_arg = None

        if typing.get_origin(field_type) == typing.Union:
            field_type = typing.get_args(field_type)[0]
            origin = typing.get_origin(field_type)

        if origin == list:
            type_arg = typing.get_args(field_type)[0]
            if not is_dataclass(type_arg):
                type_arg = None

        access = f'o.get({name!r})'

        if type_arg is not None or is_dataclass(field_type):
            lines.append(f'    value = {access}')
            lines.append(f'    if value is not None:')
            if type_arg is not None:
                type_name = type_arg.__name__
                lines.append(
                    '        '
                    f'value = [{type_name}.from_dict(x) for x in value]'
                )
            elif is_dataclass(field_type):
                type_name = field_type.__name__
                lines.append(f'        value = {type_name}.from_dict(value)')
            lines.append(f'    args.append(value)')
        else:
            lines.append(f'    args.append({access})')
    lines.append('    return cls(*args)')
    lines.append('')
    return '\n'.join(lines)
