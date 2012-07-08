"""
Chainable validators are *encapsulating* validators. They
usually will not validate per se, but can contain other validators
inside them and pass the value to them.
"""


class BasicChainValidator(object):
    """
    The base chainable validator, should not be used directly
    but can be sub-classed to extend into custom chainable
    validators.
    """
    pass


class AllIn(object):
    """
    Validates against all the validators passed in.
    """
    pass


class AnyIn(object):
    """
    If any contained validator passes it skips any others
    """
    pass
