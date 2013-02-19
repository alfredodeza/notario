import re


class Linker(list):
    """
    This list-like object will receive key/value pairs as regexes with
    accompanying failure error messages and upon a call, it will apply them
    sequentially so that a user can understand at what point in the regex the
    failure happened with a given value.

    .. note::
        Direct use of this class is discouraged as the functionality is exposed
        through the :def:`chain` helper function.
    """

    def __init__(self, regexes, prepend_negation=None):
        if prepend_negation is None:
            self.prepend_negation = False
        else:
            self.prepend_negation = prepend_negation
        self._sanity(regexes)
        self.prepend_negation = prepend_negation
        self.regexes = regexes
        self._build()

    def _sanity(self, items):
        try:
            for item in items:
                pattern, reason = item
        except ValueError:
            raise TypeError('arguments must be key value pairs')

    def _build(self):
        self.append(re.compile(self.regexes[0][0]))
        for number in range(1, len(self.regexes)):
            new_regex = self._get_regex(number)
            self.append(re.compile(new_regex))

    def _get_regex(self, number):
        items = []
        for item, _ in self.regexes[:number + 1]:
            items.append(item)
        return ''.join(items)

    def _get_reason(self, item_number):
        reason = self.regexes[item_number][1]
        if self.prepend_negation:
            return "does not %s" % self.regexes[item_number][1]
        return reason

    def __call__(self, value):
        for count, regex in enumerate(self):
            if not regex.match(value):
                raise AssertionError(self._get_reason(count))


def chain(*regexes, **kwargs):
    """
    A helper function to interact with the regular expression engine
    that compiles and applies partial matches to a string.

    It expects key value tuples as arguments (any number of them) where the
    first pair is the regex to compile and the latter is the message to display
    when the regular expression does not match.

    The engine constructs partial regular expressions from the input and
    applies them sequentially to find the exact point of failure and allowing
    the ability to return a meaningful message.

    Because adding negation statements like "does not..." can become
    repetitive, the function defaults to ``True`` to include the option to
    prepend the negative.

    For example, this is what would happen with a failing regex::

        >>> rx = chain((r'^\d+', 'start with a digit'))
        >>> rx('foo')
        Traceback (most recent call last):
        ...
        AssertionError: does not start with a digit

    If there is no need for prepending the negation, the keyword argument will
    need to set it as ``False``::

        >>> rx = chain((r'^\d+', 'it should start with a digit'),
        ...            prepend_negation=False)
        >>> rx('foo')
        Traceback (most recent call last):
        ...
        AssertionError: it should start with a digit
    """

    prepend_negation = kwargs.get('prepend_negation', True)
    return Linker(regexes, prepend_negation=prepend_negation)
