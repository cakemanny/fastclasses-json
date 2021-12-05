from typing import Union

from .core import _process_class


class JSONMixin:

    def to_dict(self) -> dict:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, o: dict, *, infer_missing=True):
        raise NotImplementedError

    def to_json(self, *, separators=None, indent=None) -> str:
        raise NotImplementedError

    @classmethod
    def from_json(cls, json_data: Union[str, bytes], *, infer_missing=True):
        # TODO: make the message more useful?
        raise NotImplementedError


def dataclass_json(cls=None):
    """
    TODO: add some documentation here
    """
    if cls is not None:
        return _process_class(cls)
    return _process_class
