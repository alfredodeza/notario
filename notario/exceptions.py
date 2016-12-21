from notario._compat import basestring
from notario.utils import is_callable


class NotarioException(Exception):

    def __init__(self, schema_item, path, reason=None, pair='key', msg=None):
        self.schema_item = schema_item
        self.path = path
        self._reason = reason
        self._pair = pair
        self._msg = msg
        Exception.__init__(self, self.__str__())

    def __str__(self):
        return self._get_message()

    def _format_path(self, use_pair=True):
        message = ""
        for key in self.path:
            if isinstance(key, basestring):
                if key == '':
                    key = "'%s'" % key
            accessed_key = '-> %s ' % key
            message += accessed_key
        if use_pair and self._pair != 'value':
            return message + self._pair
        return message or "-> top level"

    def _formatted_reason(self):
        if self.reason:
            return " (%s)" % self.reason
        return ''

    def _format_message(self):
        reason = self._formatted_reason()
        if self._msg:
            return self._msg
        if self.schema_item is None:
            return "did not match schema %s" % reason
        if is_callable(self.schema_item):
            msg = "did not pass validation against callable: %s"\
                  "%s" % (self.schema_item.__name__, reason)
        else:
            msg = "did not match %s%s" % (repr(self.schema_item), reason)
        return msg

    @property
    def reason(self):
        try:
            return self._reason.args[0]
        except IndexError:
            return self._reason
        except AttributeError:
            return self._reason or ''


class Invalid(NotarioException):
    """
    This Exception class is used only by the :class:`Validator`
    class to provide a clear message when a validation mismatch occurs
    while traversing the configuration tree.
    """

    def _get_message(self):
        path = self._format_path()
        message = self._format_message()
        if path.endswith(' '):
            return "%s%s" % (path, message)
        return "%s %s" % (path, message)


class NestedInvalid(Invalid):
    """
    When a validator is deeply nested, (e.g. a recursive inside an iterable)
    catching exceptions for better reporting is very difficult because of how
    most are caught and re-written to accomodate a tree.  This exception will
    probably be useful only to those types of validators, that need to raise an
    ``Invalid`` exception that should not be re-written in any way.
    """
    pass


class SchemaError(NotarioException):

    def _get_message(self):
        msg = "%s %s" % (self._format_path(use_pair=False), self._reason)
        return msg


class Skip(Exception):
    """
    This Exception class is used for ``optional`` decorators that fail
    to get the right key for a given data.
    """
    pass
