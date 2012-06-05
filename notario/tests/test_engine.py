from pytest import raises
from notario import engine
from notario.exceptions import Invalid


class TestEnforce(object):

    def test_callable_failure_raises_invalid(self):
        def bad_callable(v): assert False
        with raises(Invalid) as exc:
            engine.enforce('1', bad_callable, ['1'], 'key')
        assert exc.value[0] == '-> 1 key did not pass validation against callable: bad_callable'

    def test_callable_passes_with_flying_colors(self):
        def cool_callable(v): pass
        result = engine.enforce('1', cool_callable, ['1'], 'key')
        assert result is None

    def test_equal_params_pass_with_flying_colors(self):
        result = engine.enforce('1', '1', ['1'], 'key')
        assert result is None

    def test_unequal_params_raise_invalid(self):
        with raises(Invalid) as exc:
            engine.enforce(1, 2, ['1'], 'key')
        assert exc.value[0] == '-> 1 key did not match 2'

    def test_callable_with_messages_are_passed_on(self):
        def callable_message(v): assert False, "this is completely False"
        with raises(Invalid) as exc:
            engine.enforce(1, callable_message, ['1'], 'key')
        assert exc.value.reason == "this is completely False"


class TestNormalizeSchema(object):

    def test_return_data_structure_with_cero_index(self):
        result = engine.normalize_schema(['a'])
        assert result == {0: ['a']}

    def test_recurse_if_second_item_is_typle(self):
        data = ('a', ('a', 'b'))
        result = engine.normalize_schema(data)
        assert result == {0: ('a', {0: ('a', 'b')})}


class TestValidator(object):

    def test_validate_top_level_keys(self):
        data = {'a': 1, 'b': 2}
        schema = (('a', 1), ('c', 2))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> b key did not match c'

    def test_validate_top_level_values(self):
        data = {'a': 1, 'b': 2}
        schema = (('a', 1), ('b', 1))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> b -> 2 value did not match 1'
