"""
Chainable validators are *encapsulating* validators. They
usually will not validate per se, but can contain other validators
inside them and pass the value to them.
"""
from notario.exceptions import Invalid
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
    Validates against all the validators passed in.
    """

    def __call__(self, value):
        for validator in self.args:
            validator(value)


class AnyIn(BasicChainValidator):
    """
    If any contained validator passes it skips any others
    """

    def __call__(self, value):
        for validator in self.args:
            try:
                return validator(value)
            except Invalid:
                pass

