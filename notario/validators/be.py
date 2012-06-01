

def string(value):
    """
    Validates a given input is of type string.
    """
    return isinstance(value, basestring)


def boolean(value):
    return False



issequence = lambda x: isinstance(x, (list, tuple))
istext     = lambda x: isinstance(x, basestring)
isdict     = lambda x: isinstance(x, dict)
isset      = lambda x: isinstance(x, set)
