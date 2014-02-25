def ensure(assertion, message=None):
    """
    Checks an assertion argument for truth-ness. Will return ``True`` or
    explicitly raise ``AssertionError``. This is to deal with environments
    using ``python -O` or ``PYTHONOPTIMIZE=``.

    :param assertion: some value to evaluate for truth-ness
    :param message: optional message used for raising AssertionError
    """
    message = message or assertion

    if not assertion:
        raise AssertionError(message)

    return True
