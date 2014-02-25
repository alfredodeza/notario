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
    if name == 'ndict':
        name = 'dict'
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

        >>> data = {16: ('1', 'b'), 3: ('1', 'a')}
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


def is_empty(value):
    try:
        return len(value) == 0
    except TypeError:
        return False


def is_not_empty(value):
    return not is_empty(value)


def is_nested_tuple(value):
    if len(value) == 2 and isinstance(value[1], tuple): # nested tuple
        return True
    return False


def data_item(data):
    """
    When trying to return a meaningful error about an unexpected data item
    we cannot just `repr(data)` as that could show a gigantic data struture.

    This utility should try to get the key of the first item or the single item
    in the data structure.
    """
    if isinstance(data, ndict):
        # OK, we have something that looks like {0: ('a', 'b')}
        # or something that is a regular dictionary
        # so try to return 'a' regardless of the length
        for item in data:
            return repr(data[item][0])
    elif isinstance(data, dict):
        for item in data:
            return repr(data[item])
    elif isinstance(data, list):
        return repr(data[0])
    return repr(data)


def forced_leaf_validator(func):
    """
    Some decorators may need to use this if doing anything related
    with a dictionary value. Since callables are usually validating
    single values (e.g. a string or a boolean) and not a dictionary
    per-se because Notario will already normalize the data.
    """
    func.__validator_leaf__ = True
    return func


def expand_schema(schema):
    if hasattr(schema, '__delayed__'):
        return schema()
    return schema


def is_schema(_object):
    """
    A helper to determine if we are indeed dealing with what it seems to be
    a schema.
    """
    if hasattr(_object, '__delayed__') or isinstance(_object, tuple):
        return True
    return False


def ensure(assertion, message=None):
    """
    Checks an assertion argument for truth-ness. Will return ``True`` or
    explicitly raise ``AssertionError``. This is to deal with environments
    using ``python -O` or ``PYTHONOPTIMIZE=``.

    :param assertion: some value to evaluate for truth-ness
    :param message: optional message used for raising AssertionError
    """
    message = message or assertion

    if not assertion:
        raise AssertionError(message)

    return True
