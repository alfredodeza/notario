

def is_callable(data):
    if hasattr(data, '__call__'):
        return True
    return False


def optional(validator):
    """
    This decorator allows to have validators work only when there is
    a value that contains some data, otherwise it will just not pass
    the information to the actual validator and will not fail as a
    result.

    As any normal decorator, it can be used corectly with the decorator
    syntax or in the actual schema.

    This is how it would look in a schema::

        ('key', optional(my_validator))

    Where ``my_validator`` can be any validator that accepts a single
    argument.

    In case a class based validator is being used (like the ``recursive`` or ``iterables``
    then it would look like::

        ('key', optional(class_validator(('key', 'value'))))

    Of course, the schema should vary depending on your needs, it is just the
    way of constructing the validator call that should be important.
    """

    def decorated(value):
        if value:
            return validator(value)
        return

    return decorated
