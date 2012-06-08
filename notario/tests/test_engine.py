from pytest import raises
from notario import engine
from notario.exceptions import Invalid, SchemaError
from notario.validators import recursive, iterables, types


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

    def test_respect_more_than_two_values_in_tuple(self):
        data = ('a', (('a', 'b'), ('c', 'c'), ('d', 'd')))
        result = engine.normalize_schema(data)
        assert result == {0: ('a', {0: ('a', 'b'), 1: ('c', 'c'), 2: ('d', 'd')})}


class TestValidator(object):

    def test_validate_top_level_keys(self):
        data = {'a': 1, 'b': 2}
        schema = (('a', 1), ('c', 2))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> b key did not match c'

    def test_validate_length_equality(self):
        data = {'a': 1, 'b': 2}
        schema = (('a', 1, 2), ('c', 2))
        with raises(SchemaError) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == ' length did not match schema'

    def test_validate_top_level_values(self):
        data = {'a': 1, 'b': 2}
        schema = (('a', 1), ('b', 1))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> b -> 2 value did not match 1'

    def test_validate_value_nested_dictionaries(self):
        data = {'a': 1, 'b': {'a': 2, 'b' : 1}}
        schema = (('a', 1), ('b', (('a', 2), ('b', 2))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> b -> b -> 1 value did not match 2'

    def test_validate_key_nested_dictionaries(self):
        data = {'a': 1, 'b': {'a': 2, 'b' : 1}}
        schema = (('a', 1), ('b', (('b', 2), ('b', 1))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> b -> a key did not match b'

    def test_validate_value_nested_arrays(self):
        data = {'a': 1, 'b': {'a': 2, 'b' : [1, 2, 3]}}
        schema = (('a', 1), ('b', (('a', 2), ('b', [1, 1, 3]))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> b -> b -> [1, 2, 3] value did not match [1, 1, 3]'

    def test_validate_key_nested_arrays(self):
        data = {'a': 1, 'b': {'a': 2, 'b' : [1, 2, 3]}}
        schema = (('a', 1), ('b', (('a', 2), ('b', [1, 1, 3]))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> b -> b -> [1, 2, 3] value did not match [1, 1, 3]'

    def test_validate_multiple_items_as_values(self):
        data = {'a': 1, 'b': {'a': 2, 'b' : 1, 'd':1, 'c':2}}
        schema = (('a', 1), ('b', (('a', 2), ('b', 1), ('c', 2), ('d', 2))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> b -> d -> 1 value did not match 2'



class TestValidatorLeaves(object):
    """
    The Validator object would behave differently with
    validator classes that have  the __validator_leaf__
    """

    def test_traverser_returns_the_iterable_leaf_if_seen(self):
        data = {'a': {'b': [1, 1, 1, 1]}}
        schema = ('a', ('b', iterables.AllItems(2)))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> a -> b -> list[0] key did not match 2'

    def test_traverser_returns_the_recursive_leaf_if_seen(self):
        data = {'a': {'b': [1, 1, 1, 1]}}
        schema = ('a', recursive.AllObjects(('b', [1, 1, 1, 2])))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> a -> b -> [1, 1, 1, 1] value did not match [1, 1, 1, 2]'


class TestRecursiveValidator(object):

    def test_bad_index_number(self):
        data = {'a': {'a':'a', 'b':'b'}}
        schema = ('a', 'a')
        recursive_validator = recursive.RecursiveValidator(data, schema, ['a'], index=100)
        with raises(SchemaError) as exc:
            recursive_validator.validate()

        assert exc.value[0] == '-> a  not enough items in data to select from'

    def test_deal_with_recursion(self):
        data = {'a': {'a':'a', 'b':{'a': 'b', 'c':'c', 'd':1}}}
        schema = ('a', (('a', 'a'), ('b', recursive.AllObjects((types.String, types.String)))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        assert exc.value[0] == '-> a -> b -> d value did not pass validation against callable: String'


class TestIterableValidator(object):

    def test_bad_index_number(self):
        pass

