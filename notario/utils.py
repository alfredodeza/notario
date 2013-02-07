import warnings


def is_callable(data):
    if hasattr(data, '__call__'):
        return True
    return False


# Backwards compatibility
def optional(validator):
    from notario import decorators
    msg = "import optional from notario.decorators, not from utils"
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
    return decorators.optional(validator)
