"""
Basic type validators
"""
from notario._compat import basestring

def string(value):
    """
    Validates a given input is of type string.

    Example usage::

        data = {'a' : 21}
        schema = (string, 21)
    """
    assert isinstance(value, basestring), "not of type string"


def boolean(value):
    """
    Validates a given input is of type boolean.

    Example usage::

        data = {'a' : True}
        schema = ('a', boolean)
    """
    assert isinstance(value, bool), "not of type boolean"


def dictionary(value):
    """
    Validates a given input is of type dictionary.

    Example usage::

        data = {'a' : {'b': 1}}
        schema = ('a', dictionary)
    """
    assert isinstance(value, dict), "not of type dictionary"


def array(value):
    """
    Validates a given input is of type list.

    Example usage::

        data = {'a' : [1,2]}
        schema = ('a', array)
    """
    assert isinstance(value, list), "not of type array"

def integer(value):
    """
    Validates a given input is of type int..

    Example usage::

        data = {'a' : 21}
        schema = ('a', integer)
    """
    assert isinstance(value, int), "not of type int"
