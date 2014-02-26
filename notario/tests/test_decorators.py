from py.test import raises
from notario import decorators


class TestInstanceOf(object):

    def test_not_of_any_valid_types(self):
        @decorators.instance_of()
        def validator(value):
            assert True  # pragma: no cover

        with raises(AssertionError) as exc:
            validator(0)
        exc_msg = str(exc.value)

        assert 'not of any valid types' in exc_msg
        assert 'list' in exc_msg
        assert 'dict' in exc_msg
        assert 'str' in exc_msg

    def test_custom_valid_types(self):
        @decorators.instance_of((str,))
        def validator(value):
            assert True # pragma: no cover

        with raises(AssertionError) as exc:
            validator({})
        exc_msg = str(exc.value)

        assert 'not of any valid types' in exc_msg
        assert 'str' in exc_msg

    def test_custom_class(self):
        class Foo(object):
            pass

        @decorators.instance_of((Foo,))
        def validator(value):
            assert True # pragma: no cover

        with raises(AssertionError) as exc:
            validator({})
        exc_msg = str(exc.value)

        assert 'not of any valid types' in exc_msg
        assert 'Foo' in exc_msg


class TestNotEmpty(object):

    def test_not_of_any_valid_types(self):
        with raises(AssertionError) as exc:
            decorators.not_empty(False)
        errors = exc.value.args[0]
        assert 'not of any valid types' in errors

    def test_not_empty_dict(self):
        @decorators.not_empty
        def validator(value):
            assert len(value) # pragma: no cover

        with raises(AssertionError) as exc:
            validator({})
        exc_msg = str(exc.value)

        assert 'is empty' in exc_msg

    def test_not_empty_str(self):
        @decorators.not_empty
        def validator(value):
            assert len(value) # pragma: no cover

        with raises(AssertionError) as exc:
            validator("")
        exc_msg = str(exc.value)

        assert 'is empty' in exc_msg

    def test_not_empty_list(self):
        @decorators.not_empty
        def validator(value):
            assert len(value) # pragma: no cover

        with raises(AssertionError) as exc:
            validator([])
        exc_msg = str(exc.value)

        assert 'is empty' in exc_msg

    def test_non_decorator_empty_string(self):
        with raises(AssertionError) as exc:
            decorators.not_empty("")
        exc_msg = str(exc.value)

        assert 'is empty' in exc_msg

    def test_is_empty_delegates_to_validator(self):
        @decorators.not_empty
        def validator(value):
            assert len(value) == 2, 'not two'

        with raises(AssertionError) as exc:
            validator([1])
        exc_msg = str(exc.value)

        assert 'not two' in exc_msg
