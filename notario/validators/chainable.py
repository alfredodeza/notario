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


    :raises: TypeError if the validator is *not* a callable
    """

    def __call__(self, value):
        for validator in self.args:
            try:
                validator(value)
            except AssertionError, exc:
                self.__name__ = 'AllIn -> %s' % validator.__name__
                raise AssertionError(exc)



class AnyIn(BasicChainValidator):
    """
    If any contained validator passes it skips any others

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
