from notario.engine import RecursiveValidator


class BasicRecursiveValidator(object):
    """
    Base class for recursive validators, can be sub-classed
    for other type of recursive validators but should not be
    used directly.
    """

    __validator_leaf__ = True

    def __init__(self, schema):
        self.schema = schema


class AnyObject(BasicRecursiveValidator):
    """
    Grab the first object in a nested dictionary and apply the schema needed
    """

    def __call__(self, data, tree):
        index = len(data) - 1
        validator = RecursiveValidator(data, self.schema, tree, index=index)
        validator.validate()


class AllObjects(BasicRecursiveValidator):
    """
    For all the objects contained in a dictionary apply the schema passed in.
    """

    def __call__(self, data, tree):
        validator = RecursiveValidator(data, self.schema, tree)
        validator.validate()
