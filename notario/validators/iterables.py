"""
Iterable validators for array objects only. They provide a way of
applying a schema to any given items in an array.
"""
from notario.exceptions import Invalid, SchemaError
from notario.engine import IterableValidator
from notario.utils import is_callable, safe_repr, expand_schema, is_schema


class BasicIterableValidator(object):
    """
    Base class for iterable validators, can be sub-classed
    for other type of iterable validators but should not be
    used directly.
    """

    __validator_leaf__ = True

    def __init__(self, schema):
        self.schema = schema

    def safe_type(self, data, tree):
        """
        Make sure that the incoming data complies with the class type we
        are expecting it to be. In this case, classes that inherit from this
        base class expect data to be of type ``list``.
        """
        if not isinstance(data, list):
            name = self.__class__.__name__
            msg = "did not pass validation against callable: %s" % name
            reason = 'expected a list but got %s' % safe_repr(data)
            raise Invalid(self.schema, tree, reason=reason, pair='value', msg=msg)


class AnyItem(BasicIterableValidator):
    """
    Go over all the items in an array and make sure that at least
    one of the items validates correctly against the schema provided.
    If no items pass it raises ``Invalid``.

    .. note::
        It only works on arrays, otherwise it will raise a ``SchemaError``

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

    When a single item in the array matches correctly against the validator's
    schema it stops further iteration and the validation passes. Otherwise it
    will raise an error like:


    .. doctest::

        >>> data = {'foo': [{'a': 1}, {'b': 2}]}
        >>> schema = ('foo', AnyItem(('c', 4)))
        >>> validate(data, schema)
        Traceback (most recent call last):
        ...
        Invalid: -> foo -> list[]  did not contain any valid items matching ('c', 4)

    """

    def __call__(self, data, tree):
        schema = expand_schema(self.schema)
        self.safe_type(data, tree)
        index = len(data) - 1
        validator = IterableValidator(data, schema, [], index=index, name='AnyItem')
        for item_index in range(len(data)):
            try:
                return validator.leaf(item_index)
            except Invalid:
                pass

        tree.append('list[]')
        if is_callable(schema):
            msg = "did not contain any valid items against callable: %s" % schema.__name__
        else:
            msg = "did not contain any valid items matching %s" % repr(schema)
        raise Invalid(schema, tree, pair='value', msg=msg)


class AllItems(BasicIterableValidator):
    """
    For all the items in an array apply the schema passed in to the validator.
    If a single item fails, it raises ``Invalid``.

    .. note::
        It only works on arrays, otherwise it will raise a ``SchemaError``

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

    When a single item in the array fails to pass against the validator's
    schema it stops further iteration and it will raise an error like:


    .. doctest:: allitems

        >>> data = {'foo': [{'a': 1}, {'a': 2}]}
        >>> schema = ('foo', AllItems(('a', 1)))
        >>> validate(data, schema)
        Traceback (most recent call last):
        ...
        Invalid: -> foo -> list[1] -> a -> 2  did not match 1

    In this particular validator, it remembers on what index of the array the
    failure was created and it goes even further giving the key and value of
    the object it went against.

    """

    def __call__(self, data, tree):
        schema = expand_schema(self.schema)
        self.safe_type(data, tree)
        validator = IterableValidator(data, schema, tree, name='AllItems')
        validator.validate()


class MultiIterable(object):

    """
    .. testsetup:: *

        from notario import validate
        from notario.validators.iterables import MultiIterable

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

    .. doctest:: multiiterable

        >>> data = {'main': {'foo': 'bar'}}
        >>> schema = ('main', MultiIterable(('foo', 1), ('foo', 'bar')))
        >>> validate(data, schema)

    Because we can't be sure what the data may hold we are forced to define
    different rules and apply them so that they can pass. If we repeat the
    expectation but an invalid value comes along, the validator will naturally
    fail:

    .. doctest:: mutlirecursive_fail

        >>> data = {'main': [{'foo': False}]}
        >>> schema = ('main', MultiIterable(('foo', 1), ('foo', 'bar')))
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
        validator = IterableValidator(data, first_schema, tree, index=index, name='MultiIterable')

        for item_index in range(len(data)):
            try:
                validator.leaf(item_index)
            except (SchemaError, Invalid):
                self.itemized_validation(validator, item_index)

    def itemized_validation(self, validator, item_index):
        error = None

        for schema in self.schemas:
            try:
                validator.schema = expand_schema(schema)
                validator.tree = []
                return validator.leaf(item_index)
            except (SchemaError, Invalid) as e:
                error = e

        if error is not None:
            raise error
