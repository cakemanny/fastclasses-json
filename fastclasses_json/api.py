import sys
import types
import typing

from .core import expr_builder_from, expr_builder_to, referenced_types


def dataclass_json(cls=None):
    if cls is not None:
        return _process_class(cls)
    return _process_class


def _process_class(cls):

    # Delay the building of our from_dict method until it is first called.
    # This allows the compilation to reference classes defined later in
    # the module.
    def _temp_from_dict(cls, *args, **kwarg):
        _replace_from_dict(cls)
        return cls.from_dict(*args, **kwarg)

    cls.from_dict = classmethod(_temp_from_dict)

    def _temp_to_dict(self, *args, **kwargs):
        _replace_to_dict(cls)
        return self.to_dict(*args, **kwargs)

    cls.to_dict = _temp_to_dict

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

    the_globals = {
        # use the defining modules globals
        **sys.modules[cls.__module__].__dict__,
        # along with types we use for the conversion
        **referenced_types(cls)
    }

    from_dict_func = types.FunctionType(
        from_dict_code,
        the_globals,
        'from_dict',
    )

    cls.from_dict = classmethod(from_dict_func)


def _replace_to_dict(cls):

    to_dict_src = _to_dict_source(cls)
    to_dict_module = compile(
        to_dict_src, '<fastclass_generated_code>', 'exec'
    )
    to_dict_code = [
        const for const in to_dict_module.co_consts
        if isinstance(const, types.CodeType)
    ][0]

    to_dict_func = types.FunctionType(
        to_dict_code,
        sys.modules[cls.__module__].__dict__,
        'to_dict',
    )

    cls.to_dict = to_dict_func


def _from_dict_source(cls):

    lines = [
        'def from_dict(cls, o):',
        '    args = []',
    ]
    for name, field_type in typing.get_type_hints(cls).items():

        # pop off the top layer of optional, since we are using o.get
        if typing.get_origin(field_type) == typing.Union:
            field_type = typing.get_args(field_type)[0]

        access = f'o.get({name!r})'

        transform = expr_builder_from(field_type)

        if transform('x') != 'x':
            lines.append(f'    value = {access}')
            lines.append(f'    if value is not None:')  # noqa: F541
            lines.append(f'        value = ' + transform('value'))  # noqa: E501,F541
            lines.append(f'    args.append(value)')  # noqa: F541
        else:
            lines.append(f'    args.append({access})')
    lines.append('    return cls(*args)')
    lines.append('')
    return '\n'.join(lines)


def _to_dict_source(cls):

    lines = [
        'def to_dict(self):',
        '    result = {}',
    ]

    # TODO: option for including Nones or not
    INCLUDE_NONES = False

    for name, field_type in typing.get_type_hints(cls).items():

        access = f'self.{name}'

        transform = expr_builder_to(field_type)

        if transform('x') != 'x':
            # since we have an is not none check, elide the first level
            # of optional
            if typing.get_origin(field_type) == typing.Union:
                transform = expr_builder_to(typing.get_args(field_type)[0])
            lines.append(f'    value = {access}')
            lines.append(f'    if value is not None:')
            lines.append(f'        value = ' + transform('value'))
            if INCLUDE_NONES:
                lines.append(f'    result[{name!r}] = value')
            else:
                lines.append(f'        result[{name!r}] = value')
        else:
            lines.append(f'    result[{name!r}] = {access}')

    lines.append('    return result')
    lines.append('')
    return '\n'.join(lines)
