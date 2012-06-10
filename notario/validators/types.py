"""
Basic type validators
"""
from notario._compat import basestring

def string(value):
    """
    Validates a given input is of type string.
    """
    assert isinstance(value, basestring), "not of type string"


def boolean(value):
    """
    Validates a given input is of type boolean.
    """
    assert isinstance(value, bool), "not of type boolean"


def dictionary(value):
    """
    Validates a given input is of type dictionary.
    """
    assert isinstance(value, dict), "not of type dictionary"


def array(value):
    """
    Validates a given input is of type list.
    """
    assert isinstance(value, list), "not of type array"

def integer(value):
    """
    Validates a given input is of type int..
    """
    assert isinstance(value, int), "not of type int"
