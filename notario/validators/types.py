"""
Basic type validators
"""
from notario._compat import basestring
from notario.utils import is_callable


def string(_object):
    """
    Validates a given input is of type string.

    Example usage::

        data = {'a' : 21}
        schema = (string, 21)

    You can also use this as a decorator, as a way to check for the
    input before it even hits a validator you may be writing.

    .. note::
        If the argument is a callable, the decorating behavior will be
        triggered, otherwise it will act as a normal function.
    """
    if is_callable(_object):
        _validator = _object

        def decorated(value):
            assert isinstance(value, basestring), "not of type string"
            return _validator(value)
        return decorated
    assert isinstance(_object, basestring), "not of type string"


def boolean(_object):
    """
    Validates a given input is of type boolean.

    Example usage::

        data = {'a' : True}
        schema = ('a', boolean)

    You can also use this as a decorator, as a way to check for the
    input before it even hits a validator you may be writing.

    .. note::
        If the argument is a callable, the decorating behavior will be
        triggered, otherwise it will act as a normal function.

    """
    if is_callable(_object):
        _validator = _object

        def decorated(value):
            assert isinstance(value, bool), "not of type boolean"
            return _validator(value)
        return decorated
    assert isinstance(_object, bool), "not of type boolean"


def dictionary(_object):
    """
    Validates a given input is of type dictionary.

    Example usage::

        data = {'a' : {'b': 1}}
        schema = ('a', dictionary)

    You can also use this as a decorator, as a way to check for the
    input before it even hits a validator you may be writing.

    .. note::
        If the argument is a callable, the decorating behavior will be
        triggered, otherwise it will act as a normal function.

    """
    if is_callable(_object):
        _validator = _object

        def decorated(value):
            assert isinstance(value, dict), "not of type dictionary"
            return _validator(value)
        return decorated
    assert isinstance(_object, dict), "not of type dictionary"


def array(_object):
    """
    Validates a given input is of type list.

    Example usage::

        data = {'a' : [1,2]}
        schema = ('a', array)

    You can also use this as a decorator, as a way to check for the
    input before it even hits a validator you may be writing.

    .. note::
        If the argument is a callable, the decorating behavior will be
        triggered, otherwise it will act as a normal function.

    """
    if is_callable(_object):
        _validator = _object

        def decorated(value):
            assert isinstance(value, list), "not of type array"
            return _validator(value)
        return decorated
    assert isinstance(_object, list), "not of type array"


def integer(_object):
    """
    Validates a given input is of type int..

    Example usage::

        data = {'a' : 21}
        schema = ('a', integer)

    You can also use this as a decorator, as a way to check for the
    input before it even hits a validator you may be writing.

    .. note::
        If the argument is a callable, the decorating behavior will be
        triggered, otherwise it will act as a normal function.
    """
    if is_callable(_object):
        _validator = _object

        def decorated(value):
            assert isinstance(value, int), "not of type int"
            return _validator(value)
        return decorated
    assert isinstance(_object, int), "not of type int"
