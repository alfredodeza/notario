from notario.exceptions import Invalid
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
    Go over all the items in an dict object and make sure that at least
    one of the items validates correctly against the schema provided.
    If no items pass it raises ``Invalid``.


    .. testsetup:: anyobject

        from notario import validate
        from notario.validators.recursive import AnyObject

    Example usage for single values::

        data = {'foo': {{'a':10}, {'b':20}, {'c':40}}}
        schema = ('foo', AnyObject(('a', 10)))
        validate(data, schema)

    Example usage for other data structures::

        data = {'foo': [{'b': 10}, {'a': 1}]}
        schema = ('foo', AnyObject(('a', 1))
        validate(data, schema)

    When a single item in the array fails to pass against the validator's schema it
    stops further iteration and it will raise an error like:


    .. doctest:: anyobject

        >>> data = {'foo': {'a':{'a':10}, 'b':{'a':20}, 'c':{'a':20}}}
        >>> schema = ('foo', AnyObject(('a', ('a', 90))))
        >>> validate(data, schema)
        Traceback (most recent call last):
        ...
        Invalid: foo -> a  did not contain any valid objects against callable: AnyObject

    In this particular validator, it remembers on what key of the dict object
    the failure was created and it goes even further giving the key and value
    of the object it went against.
    """

    def __call__(self, data, tree):
        index = len(data) - 1
        validator = RecursiveValidator(data, self.schema, [], index=index)
        for item_index in range(len(data)):
            try:
                return validator.leaf(item_index)
            except Invalid:
                if tree:
                    tree.pop
                pass

        msg = "did not contain any valid objects against callable: %s" % self.__class__.__name__
        raise Invalid(self.schema, tree, pair='value', msg=msg)



class AllObjects(BasicRecursiveValidator):
    """
    For all the objects contained in a dictionary apply the schema passed in
    to the validator.
    If a single item object fails, it raises ``Invalid``.


    .. testsetup:: allobjects

        from notario import validate
        from notario.validators.recursive import AllObjects

    Example usage for single values::

        data = {'foo': {{'a':10}, {'a':20}, {'a':20}}}
        schema = ('foo', AllObjects(('a', 20)))
        validate(data, schema)

    Example usage for other data structures::

        data = {'foo': [{'a': 1}, {'a': 1}]}
        schema = ('foo', AllObjects(('a', 1))
        validate(data, schema)

    When a single item in the array fails to pass against the validator's schema it
    stops further iteration and it will raise an error like:


    .. doctest:: allobjects

        >>> data = {'foo': {'a':{'a':10}, 'b':{'a':20}, 'c':{'a':20}}}
        >>> schema = ('foo', AllObjects(('a', ('a', 90))))
        >>> validate(data, schema)
        Traceback (most recent call last):
        ...
        Invalid: -> foo -> a -> a -> 10  did not match 90

    In this particular validator, it remembers on what key of the dict object
    the failure was created and it goes even further giving the key and value
    of the object it went against.


    """

    def __call__(self, data, tree):
        validator = RecursiveValidator(data, self.schema, tree)
        validator.validate()
