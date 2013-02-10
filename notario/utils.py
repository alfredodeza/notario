import warnings


def is_callable(data):
    if hasattr(data, '__call__'):
        return True
    return False


def safe_repr(obj):
    """
    Try to get ``__name__`` first, ``__class__.__name__`` second
    and finally, if we can't get anything acceptable, fallback
    to user a ``repr()`` call.
    """
    name = getattr(obj, '__name__', getattr(obj.__class__, '__name__'))
    return name or repr(obj)


# Backwards compatibility
def optional(validator):
    from notario import decorators
    msg = "import optional from notario.decorators, not from utils"
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
    return decorators.optional(validator)
