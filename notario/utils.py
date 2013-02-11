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


class ndict(dict):
    """
    Used by Notario so that it can slap attributes to the object
    when it is created, something that regular dictionaries will not
    allow to do.
    """
    pass


def re_sort(data):
    """
    A data with keys that are not enumerated sequentially will be
    re sorted and sequentially ordered.

    For example::

        data = {16: ('1', 'b'), 3: ('1', 'a')}

    Will become::

        >>> re_sort(data)
        >>> {0: ('1', 'a'), 1: ('1', 'b')}
        
    """
    keys = sorted(data.keys())
    new_data = {}
    for number, key in enumerate(keys):
        new_data[number] = data[key]
    return new_data


def sift(data, required_items=None):
    """
    Receive a ``data`` object that will be in the form
    of a normalized structure (e.g. ``{0: {'a': 0}}``) and
    filter out keys that match the ``required_items``.
    """
    required_items = required_items or []
    new_data = {}
    for k, v in data.items():
        if v[0] in required_items:
            new_data[k] = v
    return re_sort(new_data)
