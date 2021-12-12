from typing import Union

from .core import _process_class

_ERR_MISSING_DECORATOR = """\
JSONMixin is only to support type checking. Combine with using the \
@dataclass_json decorator"""


class JSONMixin:
    """
    A mixin to assist with type checking.

    The recommended method is to use `fastclasses_json.mypy_plugin`. If you
    are using a different type checker or incompatible version of mypy then
    this is a good fallback.

    Example:

        @dataclass_json
        @dataclass
        class MyDataclass(JSONMixin):
            ...
    """

    def to_dict(self) -> dict:
        raise NotImplementedError(_ERR_MISSING_DECORATOR)

    @classmethod
    def from_dict(cls, o: dict, *, infer_missing=True):
        raise NotImplementedError(_ERR_MISSING_DECORATOR)

    def to_json(self, *, separators=None, indent=None) -> str:
        raise NotImplementedError(_ERR_MISSING_DECORATOR)

    @classmethod
    def from_json(cls, json_data: Union[str, bytes], *, infer_missing=True):
        raise NotImplementedError(_ERR_MISSING_DECORATOR)


def dataclass_json(cls=None):
    """
    Returns the same class that was passed in with to_dict, from_dict, to_json
    and from_json methods added.

    Can only be applied to classes decorated with @dataclass

    Example:

        @dataclass_json
        @dataclass
        class MyDataclass:
            my_field: str

        MyDataclass.from_json('{"my_field": "my value"}')
    """
    if cls is not None:
        return _process_class(cls)
    return _process_class
