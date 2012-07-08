"""
Chainable validators are *encapsulating* validators. They
usually will not validate per se, but can contain other validators
inside them and pass the value to them.
"""


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
