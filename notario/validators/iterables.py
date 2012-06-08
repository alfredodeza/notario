from notario.engine import Validator, IterableValidator


class BasicIterableValidator(object):
    """
    Base class for iterable validators, can be sub-classed
    for other type of iterable validators but should not be
    used directly.
    """

    __validator_iterable__ = True

    def __init__(self, schema):
        self.schema = schema


class AnyItem(BasicIterableValidator):
    """
    Grab the first item and apply the schema needed
    """

    def __call__(self, data, tree):
        index = len(data) - 1
        validator = IterableValidator(data, self.schema, tree, index=index)
        validator.validate()


class AllItems(BasicIterableValidator):
    """
    For all the items in an array apply the schema
    passed in
    """

    def __call__(self, data, tree):
        validator = IterableValidator(data, self.schema, tree)
        validator.validate()
