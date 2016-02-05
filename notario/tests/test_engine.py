from pytest import raises
from notario import engine
from notario.exceptions import Invalid, SchemaError
from notario.validators import recursive, iterables, types
from notario.decorators import optional
from notario.tests import util


class TestEnforce(object):

    def test_callable_failure_raises_invalid(self):
        def bad_callable(v): assert False
        with raises(Invalid) as exc:
            engine.enforce('1', bad_callable, ['1'], 'key')
        error = exc.value.args[0]
        assert '-> 1 key did not pass validation against callable: bad_callable' in error

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
        error = exc.value.args[0]
        assert '-> 1 key did not match 2' in error

    def test_callable_with_messages_are_passed_on(self):
        def callable_message(v): assert False, "this is completely False"
        with raises(Invalid) as exc:
            engine.enforce(1, callable_message, ['1'], 'key')
        result = util.assert_message(exc.value.reason)
        assert result  == "this is completely False"


class TestValidator(object):

    def test_validate_top_level_keys(self):
        data = {'a': 1, 'b': 2}
        schema = (('a', 1), ('c', 2))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert  "-> b key did not match 'c'" in error

    def test_validate_length_equality(self):
        data = {'a': 1, 'b': 2}
        schema = (('a', 1, 2), ('c', 2))
        with raises(SchemaError) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert  '-> top level length did not match schema' in error

    def test_validate_length_equality_less_items(self):
        data = {'a': 1, 'b': 2, 'c':'c'}
        schema = (('a', 1), ('b', 2))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert "top level has unexpected item in data: ('c', 'c')" in error

    def test_validate_length_equality_returns(self):
        data = {0:('a', 1)}
        class _Schema(object):
            __validator_leaf__ = True
        schema = {0:_Schema()}
        validator = engine.Validator({}, {})
        result = validator.length_equality(data, schema, 0, [])
        assert result is None

    def test_validate_top_level_values(self):
        data = {'a': 1, 'b': 2}
        schema = (('a', 1), ('b', 1))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert  '-> b -> 2 did not match 1' in error

    def test_validate_value_nested_dictionaries(self):
        data = {'a': 1, 'b': {'a': 2, 'b' : 1}}
        schema = (('a', 1), ('b', (('a', 2), ('b', 2))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert  '-> b -> b -> 1 did not match 2' in error

    def test_validate_key_doubly_nested_dictionaries(self):
        data = {'a': 1, 'b': {'a': 2, 'b' : {'a':'a'}}}
        schema = (('a', 1), ('b', (('a', 2), ('b', ('a', 'b')))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert  "-> b -> b -> a -> a did not match 'b'" in error

    def test_validate_key_nested_dictionaries(self):
        data = {'a': 1, 'b': {'a': 2, 'b' : 1}}
        schema = (('a', 1), ('b', (('b', 2), ('b', 1))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert  "-> b -> a key did not match 'b'" in error

    def test_validate_value_nested_arrays(self):
        data = {'a': 1, 'b': {'a': 2, 'b' : [1, 2, 3]}}
        schema = (('a', 1), ('b', (('a', 2), ('b', [1, 1, 3]))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert  '-> b -> b -> [1, 2, 3] did not match [1, 1, 3]' in error

    def test_validate_key_nested_arrays(self):
        data = {'a': 1, 'b': {'a': 2, 'b' : [1, 2, 3]}}
        schema = (('a', 1), ('b', (('a', 2), ('b', [1, 1, 3]))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert  '-> b -> b -> [1, 2, 3] did not match [1, 1, 3]' in error

    def test_validate_multiple_items_as_values(self):
        data = {'a': 1, 'b': {'a': 2, 'b' : 1, 'd':1, 'c':2}}
        schema = (('a', 1), ('b', (('a', 2), ('b', 1), ('c', 2), ('d', 2))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert  '-> b -> d -> 1 did not match 2' in error in error


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

        error = exc.value.args[0]
        assert  '-> a -> b -> list[0] item did not match 2' in error

    def test_traverser_returns_the_recursive_leaf_if_seen(self):
        data = {'a': {'b': [1, 1, 1, 1]}}
        schema = ('a', recursive.AllObjects(('b', [1, 1, 1, 2])))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert  '-> a -> b -> [1, 1, 1, 1] did not match [1, 1, 1, 2]' in error


class TestRecursiveValidator(object):

    def test_bad_index_number(self):
        data = {'a': {'a':'a', 'b':'b'}}
        schema = ('a', 'a')
        recursive_validator = recursive.RecursiveValidator(data, schema, index=100)
        with raises(SchemaError) as exc:
            recursive_validator.validate()

        error = exc.value.args[0]
        assert  '-> top level has not enough items to select from' in error

    def test_deal_with_recursion(self):
        data = {'a': {'a': 'a', 'b': {'a': 'b', 'c': 'c', 'd': 1}}}
        schema = ('a', (('a', 'a'), ('b', recursive.AllObjects((types.string, types.string)))))
        with raises(Invalid) as exc:
            validator = engine.Validator(data, schema)
            validator.validate()

        error = exc.value.args[0]
        assert '1 did not pass validation against callable: string' in error
        assert 'not of type string' in error


class TestIterableValidator(object):

    def test_not_enough_items_in_data(self):
        data = {0: ('a', 'b')}
        schema = {0: ('a', 'b')}
        iter_validator = engine.IterableValidator(data, schema, index=100)
        with raises(SchemaError) as exc:
            iter_validator.validate()
        error = exc.value.args[0]
        assert '-> top level has not enough items to select from' in error

    def test_validate_nested_array_first(self):
        data = [{'a':'a'}, {'b': 'b'}]
        schema = (types.string, 'b') # note how this is not normalized
        iter_validator = engine.IterableValidator(data, schema, index=0)
        with raises(Invalid) as exc:
            iter_validator.validate()

        error = exc.value.args[0]
        assert  "-> list[0] -> a -> a did not match 'b'" in error

    def test_validate_nested_array(self):
        data = [{'a':'b'}, {'b': 'c'}]
        schema = (types.string, 'b') # note how this is not normalized
        iter_validator = engine.IterableValidator(data, schema, index=0)
        with raises(Invalid) as exc:
            iter_validator.validate()

        error = exc.value.args[0]
        assert  "-> list[1] -> b -> c did not match 'b'" in error

    def test_report_schema_errors(self):
        data = [1,2,3,4]
        schema = (types.string, ('b', 'a'))
        iter_validator = engine.IterableValidator(data, schema, index=0)
        with raises(SchemaError) as exc:
            iter_validator.validate()
        error = exc.value.args[0]
        assert "iterable contains single items, schema does not" in error

    def test_invalid_on_non_list(self):
        data = {'foo': [{'a':'b'}, {'b': 'c'}]}
        schema = (types.string, 'b') # note how this is not normalized
        iter_validator = engine.IterableValidator(data, schema, index=0)
        with raises(Invalid) as exc:
            iter_validator.validate()
        error = exc.value.args[0]
        assert "top level did not pass validation against callable: IterableValidator" in error


class TestOptionalKeys(object):

    def test_optional_key_passes(self):
        data = {'a': 1, 'c': 3}
        schema = (('a', 1), (optional('b'), 2), ('c', 3))
        validator = engine.Validator(data, schema)
        assert validator.validate() is None

    def test_optional_key_raises(self):
        data = {'a': 1, 'b': 3, 'c': 3}
        schema = (('a', 1), (optional('b'), 2), ('c', 3))
        validator = engine.Validator(data, schema)
        with raises(Invalid) as exc:
            validator.validate()
        exc_msg = str(exc.value)
        assert '3 did not match 2' in exc_msg
        assert 'b -> 3' in exc_msg


class TestValidate(object):

    def test_refuses_non_dicts(self):
        with raises(TypeError):
            engine.validate(['a list'], ('a', 'b'))
