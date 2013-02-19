import re


class Linker(list):

    def __init__(self, regexes, prepend_negation=None):
        if prepend_negation is None:
            self.prepend_negation = False
        else:
            self.prepend_negation = prepend_negation
        self._sanity(regexes)
        self.prepend_negation = prepend_negation
        self.regexes = regexes
        self.build()

    def _sanity(self, items):
        try:
            for item in items:
                pattern, reason = item
        except ValueError:
            raise TypeError('arguments must be key value pairs')

    def build(self):
        self.append(re.compile(self.regexes[0][0]))
        for number in range(1, len(self.regexes)):
            new_regex = self._get_regex(number)
            self.append(re.compile(new_regex))

    def _get_regex(self, number):
        items = []
        for item, _ in self.regexes[:number + 1]:
            items.append(item)
        return ''.join(items)

    def get_reason(self, item_number):
        reason = self.regexes[item_number][1]
        if self.prepend_negation:
            return "does not %s" % self.regexes[item_number][1]
        return reason

    def __call__(self, value):
        for count, regex in enumerate(self):
            if not regex.match(value):
                raise AssertionError(self.get_reason(count))


def chain(*regexes, **kwargs):
    prepend_negation = kwargs.get('prepend_negation', True)
    return Linker(regexes, prepend_negation=prepend_negation)
