from notario.exceptions import Invalid
from notario.utils import safe_repr, expand_schema, is_schema
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

    When a single item in the array fails to pass against the validator's
    schema it stops further iteration and it will raise an error like:


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
        schema = expand_schema(self.schema)
        index = len(data) - 1
        validator = RecursiveValidator(data, schema, [], index=index)
        for item_index in range(len(data)):
            try:
                return validator.leaf(item_index)
            except Invalid:
                if tree:
                    tree.pop
                pass

        msg = "did not contain any valid objects against callable: %s" % self.__class__.__name__
        raise Invalid(schema, tree, pair='value', msg=msg)


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

    When a single item in the array fails to pass against the validator's
    schema it stops further iteration and it will raise an error like:


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
        schema = expand_schema(self.schema)
        validator = RecursiveValidator(data, schema, tree)
        validator.validate()


class MultiRecursive(object):

    """
    .. testsetup:: *

        from notario import validate
        from notario.validators.recursive import MultiRecursive

    This validator is useful when there is a need for validating any number of
    schemas for a given data set.

    If the requirement is, for example, to validate either ``string: string``
    or ``string: int`` this will not be possible with any of the other
    validators in Notario because they all assume a rule that must dominate
    everything. Otherwise, it is required to specify the expectation.

    In the case that the object to validate complies with the above
    requirement, this validator can accept **any number** of schemas as
    arguments, so if one schema fails, the next one will be tried until all the
    schemas are applied for a given item. The ``MultiRecursive`` validator will
    look like this in order to pass the incoming data:

    .. doctest:: multirecursive

        >>> data = {'main': {'foo': 'bar'}}
        >>> schema = ('main', MultiRecursive(('foo', 1), ('foo', 'bar')))
        >>> validate(data, schema)

    Because we can't be sure what the data may hold we are forced to define
    different rules and apply them so that they can pass. If we repeat the
    expectation but an invalid value comes along, the validator will naturally
    fail:

    .. doctest:: mutlirecursive_fail

        >>> data = {'main': {'foo': False}}
        >>> schema = ('main', MultiRecursive(('foo', 1), ('foo', 'bar')))
        >>> validate(data, schema)
        Traceback (most recent call last):
        ...
        Invalid: -> foo -> False did not match 'bar'

    """
    __validator_leaf__ = True

    def __init__(self, *schemas):
        for schema in schemas:
            if not is_schema(schema):
                raise TypeError("got a non schema argument: %s" % safe_repr(schema))
        self.schemas = schemas

    def __call__(self, data, tree):
        """
        Go through each item in data against the first schema in the arguments.
        If that fails try each subsequent schema until it passes. Even if
        schemas are failing to apply to that given item, consume all the
        available ones until at least one passes.

        If nothing passes, the last error is raised.

        :param data: Incoming data from the validator engine in normalized dict
        form.
        :param tree: The traversing tree up to this point, always passed in.
        :raises Invalid: If none of the schemas can validate the data.
        """
        first_schema = expand_schema(self.schemas[0])
        index = len(data) - 1
        validator = RecursiveValidator(data, first_schema, [], index=index)
        for item_index in range(len(data)):
            try:
                validator.leaf(item_index)
            except Invalid:
                self.itemized_validation(validator, item_index)

    def itemized_validation(self, validator, item_index):
        error = None

        for schema in self.schemas:
            try:
                validator.schema = expand_schema(schema)
                validator.tree = []
                return validator.leaf(item_index)
            except Invalid as e:
                error = e

        if error is not None:
            raise error
