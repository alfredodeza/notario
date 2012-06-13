from notario.utils import is_callable


class Invalid(Exception):
    """
    This Exception class is used only by the :class:`Validator`
    class to provide a clear message when a validation mismatch occurs
    while traversing the configuration tree.
    """

    def __init__(self, schema_item, path, reason=None, pair='key'):
        self.schema_item = schema_item
        self.path = path
        self._reason = reason
        self._pair = pair
        Exception.__init__(self, self.__str__())

    def __str__(self):
        return self._get_message()

    def _format_path(self, use_pair=True):
        message = ""
        for key in self.path:
            accessed_key = '-> %s ' % key
            message += accessed_key
        if use_pair and self._pair != 'value':
            return message + self._pair
        return message or "top level"

    def _format_message(self):
        if is_callable(self.schema_item):
            msg = "did not pass validation against callable: %s" % (self.schema_item.__name__)
        else:
            msg = "did not match %s" % (self.schema_item)
        return msg

    def _get_message(self):
        return "%s %s" % (self._format_path(), self._format_message())

    @property
    def reason(self):
        try:
            return self._reason.args[0]
        except IndexError:
            return self._reason


class SchemaError(Invalid):

    def _get_message(self):
        msg = "%s %s" % (self._format_path(use_pair=False), self._reason)
        return msg
