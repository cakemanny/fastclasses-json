
def issubclass_safe(cls, class_or_tuple):
    try:
        return issubclass(cls, class_or_tuple)
    except Exception:
        return False
