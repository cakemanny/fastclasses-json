import sys
import types
import typing

from .core import expr_builder, referenced_types


def dataclass_json(cls=None):
    if cls is not None:
        return _process_class(cls)
    return _process_class


def _process_class(cls):

    # delay the building of our from_dict method until it is first called
    def _temp_from_dict(cls, *args, **kwarg):
        _replace_from_dict(cls)
        return cls.from_dict(*args, **kwarg)

    cls.from_dict = classmethod(_temp_from_dict)

    return cls


def _replace_from_dict(cls):

    from_dict_src = _from_dict_source(cls)
    from_dict_module = compile(
        from_dict_src, '<fastclass_generated_code>', 'exec'
    )
    from_dict_code = [
        const for const in from_dict_module.co_consts
        if isinstance(const, types.CodeType)
    ][0]

    argdefs = tuple(referenced_types(cls).values())

    from_dict_func = types.FunctionType(
        from_dict_code,
        # use the defining modules globals
        sys.modules[cls.__module__].__dict__,
        'from_dict',
        argdefs=argdefs,
    )

    cls.from_dict = classmethod(from_dict_func)


def _from_dict_source(cls):

    dc_typenames = ','.join(referenced_types(cls).keys())

    lines = [
        f'def from_dict(cls, o, {dc_typenames}):',
        f'    args = []',
    ]
    for name, field_type in typing.get_type_hints(cls).items():

        # pop off the top layer of optional, since we are using o.get
        if typing.get_origin(field_type) == typing.Union:
            field_type = typing.get_args(field_type)[0]

        access = f'o.get({name!r})'

        transform = expr_builder(field_type)

        if (transform('x') != 'x'):
            lines.append(f'    value = {access}')
            lines.append(f'    if value is not None:')
            lines.append(f'        value = ' + transform('value'))
            lines.append(f'    args.append(value)')
        else:
            lines.append(f'    args.append({access})')
    lines.append('    return cls(*args)')
    lines.append('')
    return '\n'.join(lines)
