from .core import _process_class


def dataclass_json(cls=None):
    if cls is not None:
        return _process_class(cls)
    return _process_class
