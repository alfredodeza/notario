

def string(value):
    """
    Validates a given input is of type string.
    """
    assert isinstance(value, basestring)


def boolean(value):
    """
    Validates a given input is of type boolean.
    """
    assert isinstance(value, bool)


def dictionary(value):
    """
    Validates a given input is of type dictionary.
    """
    assert isinstance(value, dict)


def array(value):
    """
    Validates a given input is of type list.
    """
    assert isinstance(value, list)

def integer(value):
    """
    Validates a given input is of type int..
    """
    assert isinstance(value, int), "not of type int"
