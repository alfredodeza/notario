"""
Basic type validators
"""
from functools import wraps
from notario._compat import basestring
from notario.exceptions import Invalid
from notario.utils import is_callable, forced_leaf_validator, ensure


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

        @wraps(_validator)
        def decorated(value):
            ensure(isinstance(value, basestring), "not of type string")
            return _validator(value)
        return decorated
    ensure(isinstance(_object, basestring), "not of type string")


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

        @wraps(_validator)
        def decorated(value):
            ensure(isinstance(value, bool), "not of type boolean")
            return _validator(value)
        return decorated
    ensure(isinstance(_object, bool), "not of type boolean")


@forced_leaf_validator
def dictionary(_object, *args):
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
    error_msg = 'not of type dictionary'
    if is_callable(_object):
        _validator = _object

        @wraps(_validator)
        def decorated(value):
            ensure(isinstance(value, dict), error_msg)
            return _validator(value)
        return decorated
    try:
        ensure(isinstance(_object, dict), error_msg)
    except AssertionError:
        if args:
            msg = 'did not pass validation against callable: dictionary'
            raise Invalid('', msg=msg, reason=error_msg, *args)
        raise


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

        @wraps(_validator)
        def decorated(value):
            ensure(isinstance(value, list), "not of type array")
            return _validator(value)
        return decorated
    ensure(isinstance(_object, list), "not of type array")


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

        @wraps(_validator)
        def decorated(value):
            ensure(isinstance(value, int), "not of type int")
            return _validator(value)
        return decorated
    ensure(isinstance(_object, int), "not of type int")
