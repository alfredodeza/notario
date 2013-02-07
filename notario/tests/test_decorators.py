from py.test import raises
from notario import decorators


class TestInstanceOf(object):

    def test_not_of_any_valid_types(self):
        @decorators.instance_of()
        def validator(value):
            assert True
        
        with raises(AssertionError) as exc:
            validator(0)
        exc_msg = exc.value[0]

        assert 'not of any valid types' in exc_msg
        assert 'list' in exc_msg
        assert 'dict' in exc_msg
        assert 'str' in exc_msg
        
    def test_custom_valid_types(self):
        @decorators.instance_of((str,))
        def validator(value):
            assert True
        
        with raises(AssertionError) as exc:
            validator({})
        exc_msg = exc.value[0]

        assert 'not of any valid types' in exc_msg
        assert 'str' in exc_msg
        
    def test_custom_class(self):
        class Foo(object):
            pass

        @decorators.instance_of((Foo,))
        def validator(value):
            assert True
        
        with raises(AssertionError) as exc:
            validator({})
        exc_msg = exc.value[0]

        assert 'not of any valid types' in exc_msg
        assert 'Foo' in exc_msg
        

class TestNotEmpty(object):

    def test_not_empty_dict(self):
        @decorators.not_empty
        def validator(value):
            assert len(value)

        with raises(AssertionError) as exc:
            validator({})
        exc_msg = exc.value[0]

        assert 'is empty' in exc_msg
        
    def test_not_empty_str(self):
        @decorators.not_empty
        def validator(value):
            assert len(value)

        with raises(AssertionError) as exc:
            validator("")
        exc_msg = exc.value[0]

        assert 'is empty' in exc_msg

    def test_not_empty_list(self):
        @decorators.not_empty
        def validator(value):
            assert len(value)

        with raises(AssertionError) as exc:
            validator([])
        exc_msg = exc.value[0]

        assert 'is empty' in exc_msg
