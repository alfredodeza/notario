from notario.exceptions import Invalid
from notario.engine import IterableValidator
from notario.utils import is_callable


class BasicIterableValidator(object):
    """
    Base class for iterable validators, can be sub-classed
    for other type of iterable validators but should not be
    used directly.
    """

    __validator_leaf__ = True

    def __init__(self, schema):
        self.schema = schema


class AnyItem(BasicIterableValidator):
    """
    Grab the first item and apply the schema needed
    """

    def __call__(self, data, tree):
        index = len(data) - 1
        validator = IterableValidator(data, self.schema, tree, index=index)
        for item_index in range(len(data)):
            try:
                return validator.leaf(item_index)
            except Invalid:
                if tree:
                    tree.pop()
                pass

        tree.append('list[]')
        if is_callable(self.schema):
            msg = "did not contain any valid items against callable: %s" % self.schema.__name__
        else:
            msg = "did not contain any valid items matching %s" % self.schema
        raise Invalid(self.schema, tree, pair='value', msg=msg)


class AllItems(BasicIterableValidator):
    """
    For all the items in an array apply the schema
    passed in
    """

    def __call__(self, data, tree):
        validator = IterableValidator(data, self.schema, tree)
        validator.validate()
