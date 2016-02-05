from notario._compat import basestring


def assert_message(exception):
    """
    Newever py.test versions modify the AssertionError exceptions so that they
    can add more information to it when using the ``==`` operator for
    comparison.
    This helper splits on the newlines and returns the first part, providing
    a backwards compatible solution that only extracts the portion of the
    assertion that notario would normally use.

    A statement like ``assert 3 == 1, 'too big'`` would look like this in newer py.test versions::

        AssertionError(u'too big\nassert 3 == 1',)

    But before they would look like::


        AssertionError(u'too big',)
    """
    if isinstance(exception, basestring):
        arguments = exception
    else:
        arguments = exception.value.args[0]
    return arguments.split('\n')[0]
