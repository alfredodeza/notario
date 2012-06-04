from pytest import raises
from notario import engine
from notario.exceptions import Invalid


class TestEnforce(object):

    def test_callable_failure_raises_invalid(self):
        def bad_callable(v): assert False
        with raises(Invalid) as exc:
            engine.enforce('1', bad_callable, ' 1')
        assert exc.value[0] == '-> 1  did not pass validation against callable: bad_callable'

    def test_callable_passes_with_flying_colors(self):
        def cool_callable(v): pass
        result = engine.enforce('1', cool_callable, ' 1')
        assert result is None

    def test_equal_params_pass_with_flying_colors(self):
        result = engine.enforce('1', '1', ' ')
        assert result is None

    def test_unequal_params_raise_invalid(self):
        with raises(Invalid) as exc:
            engine.enforce(1, 2, ' 1')
        assert exc.value[0] == '-> 1  did not match 2'

    def test_callable_with_messages_are_passed_on(self):
        def callable_message(v): assert False, "this is completely False"
        with raises(Invalid) as exc:
            engine.enforce(1, callable_message, ' 1')
        assert exc.value.reason == "this is completely False"
