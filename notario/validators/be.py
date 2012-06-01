

def string(value):
    """
    Validates a given input is of type string.
    """
    return isinstance(value, basestring)


def boolean(value):
    """
    Validates a given input is of type boolean.
    """
    return isinstance(value, bool)


def dictionary(value):
    """
    Validates a given input is of type dictionary.
    """
    return isinstance(value, dict)


def array(value):
    """
    Validates a given input is of type list.
    """
    return isinstance(value, list)
