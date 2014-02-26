"""
Chainable validators are *encapsulating* validators. They
usually will not validate per se, but can contain other validators
inside them and pass the value to them.
"""
from notario.utils import is_callable


class BasicChainValidator(object):
    """
    The base chainable validator, should not be used directly
    but can be sub-classed to extend into custom chainable
    validators.
    """

    def __init__(self, *args):
        for i in args:
            if not is_callable(i):
                raise TypeError("got a non-callable argument: %s" % repr(i))
        self.args = args


class AllIn(BasicChainValidator):
    """
    Validates against all the validators passed in. This chainable validator
    will pass in the actual to every single validator that is contained as an
    argument.

    Example usage::

        from notario.validators import types

        data = {'foo' : "some string"}
        schema = ('foo', AllIn(types.string))
        validate(data, schema)

    When more than one validator needs to be chained this validator can take it
    in as another argument. Lets say that you have a validator that specifies
    a minimum length a maxium length and that it starts with the letter 's'::::

        data = {'foo' : "some string"}
        schema = ('foo', AllIn(min_length, max_length, StartsWith('s'))
        validate(data, schema)


    :raises: TypeError if the validator is *not* a callable
    """

    def __call__(self, value):
        for validator in self.args:
            try:
                validator(value)
            except AssertionError as exc:
                self.__name__ = 'AllIn -> %s' % validator.__name__
                raise AssertionError(exc)


class AnyIn(BasicChainValidator):
    """
    If any contained validator passes it skips any others, even if those others
    might fail at some point.  If no validators pass at the end it fails
    pointing out that the ``AnyIn`` validator was not able to pass against any
    contained validator.

    :raises: TypeError if the validator is *not* a callable
    """
    __name__ = 'AnyIn'

    def __call__(self, value):
        for validator in self.args:
            try:
                return validator(value)
            except AssertionError:
                pass

        raise AssertionError("did not passed validation against any validator")
