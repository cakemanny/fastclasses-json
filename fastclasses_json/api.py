from typing import Union

from .core import _process_class


class JSONMixin:

    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, o: dict, *, infer_missing=True): ...

    def to_json(self, *, separators=None, indent=None) -> str: ...

    def from_json(cls, json_data: Union[str, bytes],
                  *, infer_missing=True): ...


def dataclass_json(cls=None):
    if cls is not None:
        return _process_class(cls)
    return _process_class
