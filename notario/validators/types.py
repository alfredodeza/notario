

def String(value):
    """
    Validates a given input is of type string.
    """
    assert isinstance(value, basestring), "not of type string"


def Boolean(value):
    """
    Validates a given input is of type boolean.
    """
    assert isinstance(value, bool), "not of type boolean"


def Dictionary(value):
    """
    Validates a given input is of type dictionary.
    """
    assert isinstance(value, dict), "not of type dictionary"


def Array(value):
    """
    Validates a given input is of type list.
    """
    assert isinstance(value, list), "not of type array"

def Integer(value):
    """
    Validates a given input is of type int..
    """
    assert isinstance(value, int), "not of type int"
