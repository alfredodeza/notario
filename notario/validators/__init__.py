

class cherry_pick(tuple):
    """
    This is not really a validator, but will allow one to make
    sure just certain keys (as defined in ``must_validate`` are
    validated. The engine will discard all others that are not
    defined here.

    It should be used in the same manner as when constructing
    a schema, but instead of a regular tuple, this should be used.

    .. note::
        If ``must_validate`` is not defined with any items, it will
        generate them with the items on the tuple passed in if possible, unless
        the tuple created is not a key value pair.

    """
    must_validate = ()

    def __init__(self, _tuple):
        try:
            self.must_validate = tuple([key for key, value in _tuple])
        except ValueError:  # single k/v pair
            if len(_tuple) == 2:
                self.must_validate = (_tuple[0],)
        return super(cherry_pick, self).__init__()


class Hybrid(object):
    """
    Validators in Notario are usually meant to validate very specific, granular
    *values* or *items*, but there is no easy way of trying to validate
    a single value or to enforce a schema if for some reason the validator
    doesn't know if it will get a single value or an object.

    For example, if the constraint was something like: "value can be either an
    integer or an array with integers", it would not be possible to juggle that
    with other validators.

    The Hybrid validator helps with that as it is able to accept both
    a validator and a schema. If it receives something that looks like a single
    value (like a boolean, integer or string) it will use the validator,
    otherwise, it will trigger Notario's engine along with the schema provided
    at initialization.

    This is how the previous scenario would be represented::

    .. doctest:: Hybrid

        >>> from notario.validators import Hybrid
        >>> from notario import validate, ensure
        >>> def validator(value):
            ... ensure(isinstance(value, bool))
            ...
        >>> schema = ('a', Hybrid(validator, ('a', 1)))
        >>> data = {'a', False}
        >>> validate(data, schema)
        >>> # if data changes, the validator accomodates for it
        >>> data = {'a': {'a': 1}}
        >>> vaidate(data, schema)

    .. warning::
        Only if the argument passed in to this validator is of type ``list`` or
        ``dict`` will the schema be enforced, otherwise it will fall back to
        using the validator.

    """

    __validator_leaf__ = True

    def __init__(self, validator, schema):
        self.validator = validator
        self.schema = schema

    def __call__(self, value, *args):
        if isinstance(value, (dict, list)):
            from notario.validators.recursive import RecursiveValidator
            validator = RecursiveValidator(value, self.schema, *args)
            validator.validate()
        else:
            try:
                tree = args[0]
            except IndexError:
                tree = []
            from notario.engine import enforce
            enforce(value, self.validator, tree, pair='value')
