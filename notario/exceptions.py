from notario.utils import is_callable


class Invalid(Exception):
    """
    This Exception class is used only by the :class:`Validator`
    class to provide a clear message when a validation mismatch occurs
    while traversing the configuration tree.
    """

    def __init__(self, schema_item, path, reason=None):
        self.schema_item = schema_item
        self.path = path
        self.reason = reason
        Exception.__init__(self, self.__str__())

    def __str__(self):
        return self._get_message()

    def _format_path(self):
        message = ""
        for key in self.path.split():
            accessed_key = '-> %s ' % key
            message += accessed_key
        return message

    def _get_message(self):
        if is_callable(self.schema_item):
            msg = "%s did not pass validation against callable: %s" % (
                    self._format_path(), self.schema_item.__name__)
        else:
            msg = "%s did not match %s" % (
                    self._format_path(), self.schema_item)
        return msg
