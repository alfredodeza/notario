"""
Iterable validators for array objects only. They provide a way of
applying a schema to any given items in an array.
"""
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
    Go over all the items in an array and make sure that at least
    one of the items validates correctly against the schema provided.
    If no items pass it raises ``Invalid``.

    .. note:: It only works on arrays, otherwise it will raise a ``SchemaError``

    .. testsetup::

        from notario import validate
        from notario.validators.iterables import AnyItem

    Example usage for single values::

        data = {'foo' : [10, 30, 50]}
        schema = ('foo', AnyItem(50))
        validate(data, schema)

    Example usage for other data structures::

        data = {'foo': [{'a': 1}, {'b': 2}]}
        schema = ('foo', AnyItem(('b', 2))
        validate(data, schema)

    When a single item in the array matches correctly against the validator's schema it
    stops further iteration and the validation passes. Otherwise it will raise an error
    like:


    .. doctest::

        >>> data = {'foo': [{'a': 1}, {'b': 2}]}
        >>> schema = ('foo', AnyItem(('c', 4)))
        >>> validate(data, schema)
        Traceback (most recent call last):
        ...
        Invalid: -> foo -> list[]  did not contain any valid items matching ('c', 4)

    """

    def __call__(self, data, tree):
        index = len(data) - 1
        validator = IterableValidator(data, self.schema, [], index=index)
        for item_index in range(len(data)):
            try:
                return validator.leaf(item_index)
            except Invalid:
                pass

        tree.append('list[]')
        if is_callable(self.schema):
            msg = "did not contain any valid items against callable: %s" % self.schema.__name__
        else:
            msg = "did not contain any valid items matching %s" % repr(self.schema)
        raise Invalid(self.schema, tree, pair='value', msg=msg)


class AllItems(BasicIterableValidator):
    """
    For all the items in an array apply the schema passed in to the validator.
    If a single item fails, it raises ``Invalid``.

    .. note:: It only works on arrays, otherwise it will raise a ``SchemaError``

    .. testsetup:: allitems

        from notario import validate
        from notario.validators.iterables import AllItems

    Example usage for single values::

        data = {'foo' : [10, 10, 10]}
        schema = ('foo', AllItems(10))
        validate(data, schema)

    Example usage for other data structures::

        data = {'foo': [{'a': 1}, {'a': 1}]}
        schema = ('foo', AllItems(('a', 1))
        validate(data, schema)

    When a single item in the array fails to pass against the validator's schema it
    stops further iteration and it will raise an error like:


    .. doctest:: allitems

        >>> data = {'foo': [{'a': 1}, {'a': 2}]}
        >>> schema = ('foo', AllItems(('a', 1)))
        >>> validate(data, schema)
        Traceback (most recent call last):
        ...
        Invalid: -> foo -> list[1] -> a -> 2  did not match 1

    In this particular validator, it remembers on what index of the array the failure
    was created and it goes even further giving the key and value of the object it
    went against.

    """

    def __call__(self, data, tree):
        validator = IterableValidator(data, self.schema, tree)
        validator.validate()
