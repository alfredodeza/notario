from notario import exceptions


def foo(): return True

class Object(object): pass


class TestInvalid(object):

    def test_include_the_key(self):
        error = exceptions.Invalid('key', ['foo', 'bar', 'key'])
        assert 'key' in error._format_path()

    def test_include_the_path_in_str(self):
        error = exceptions.Invalid('key', ['path'])
        assert 'path' in error.__str__()

    def test_include_the_key_in_str(self):
        error = exceptions.Invalid('key', ['path'])
        assert 'key' in error.__str__()

    def test_multiple_keys_in_format_path(self):
        error = exceptions.Invalid('schema', ['key', 'subkey', 'bar'])
        assert '-> key -> subkey -> bar' in error._format_path()

    def test_full_message(self):
        error = exceptions.Invalid('3', ['foo', 'bar', 'baz'])
        result = error.__str__()
        assert "-> foo -> bar -> baz key did not match '3'" == result

    def test_full_message_for_callable(self):
        error = exceptions.Invalid(foo, ['foo', 'bar', 'baz'])
        result = error.__str__()
        assert "-> foo -> bar -> baz key did not pass validation against callable: foo" == result

    def test_full_message_for_value(self):
        error = exceptions.Invalid('3', ['foo', 'bar', 'baz'], pair='value')
        result = error.__str__()
        assert "-> foo -> bar -> baz did not match '3'" == result

    def test_full_message_for_callable_with_value(self):
        error = exceptions.Invalid(foo, ['foo', 'bar', 'baz'], pair='value')
        result = error.__str__()
        assert "-> foo -> bar -> baz did not pass validation against callable: foo" == result



class TestSchemaError(object):

    def test_reason_has_no_args(self):
        class Foo(object):
            def __repr__(self):
                return "some reason"
        reason = Foo()
        reason.args = []
        error = exceptions.SchemaError(foo, ['foo'], reason=reason, pair='value')
        assert "some reason" == repr(error.reason)
