from pytest import raises
from notario import validate
from notario.exceptions import Invalid, SchemaError
from notario.validators import iterables, recursive, types, chainable, cherry_pick
from notario.decorators import optional


class TestValidate(object):

    def test_most_simple_validation(self):
        data = {'a': 'a'}
        schema = (('a', 'b'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == "-> a -> a  did not match 'b'"

    def test_multi_pair_non_nested_last(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'a'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == "-> d -> d  did not match 'a'"

    def test_multi_pair_non_nested_first(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'b'), ('b', 'b'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == "-> a -> a  did not match 'b'"

    def test_multi_pair_non_nested_second(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'a'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == "-> b -> b  did not match 'a'"

    def test_multi_pair_non_nested_third(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('c', 'a'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == "-> c -> c  did not match 'a'"

    def test_multi_pair_non_nested_last_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('c', 'c'), ('a', 'a'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == "-> d key did not match 'a'"

    def test_multi_pair_non_nested_first_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('f', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == "-> a key did not match 'f'"

    def test_multi_pair_non_nested_second_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('f', 'b'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == "-> b key did not match 'f'"

    def test_multi_pair_non_nested_third_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('f', 'c'), ('d', 'a'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == "-> c key did not match 'f'"


class TestCherryPick(object):

    def test_validate_only_one_item(self):
        data = {'a': {'b': 'b', 'c': 'c', 'd': 'd'}}
        schema = ('a', cherry_pick(('b', 'a')))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == "-> a -> b -> b  did not match 'a'"

    def test_validate_custom_items(self):
        data = {'a': {'b': 'b', 'c': 'c', 'd': 'd'}}
        picky = cherry_pick((('b' ,'b'), ('c', 'd')))
        picky.must_validate = ('b',)
        schema = ('a', picky)

        # should not raise invalid, because 'c' never got validated
        assert validate(data, schema) is None

    def test_complain_about_empty_must_validate(self):
        data = {'a': {'b': 'b', 'c': 'c', 'd': 'd'}}
        picky = cherry_pick((('b' ,'b'), ('c', 'd')))
        picky.must_validate = ()
        schema = ('a', picky)

        # should not raise invalid, because 'c' never got validated
        with raises(SchemaError) as exc:
            validate(data, schema)

        assert exc.value.args[0] == "-> a  must_validate attribute must not be empty"


class TestWithIterableValidators(object):

    def test_all_items_pass(self):
        data = {'a': [1, 2, 3, 4, 5]}
        schema = ('a', iterables.AllItems(types.integer))
        assert validate(data, schema) is None

    def test_any_items_pass(self):
        data = {'a': [1,2, 'a string' ,4,5]}
        schema = ('a', iterables.AnyItem(types.string))
        assert validate(data, schema) is None

    def test_all_items_fail(self):
        data = {'a': [1, 2, '3', 4, 5]}
        schema = ('a', iterables.AllItems(types.integer))
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert 'not of type int' in error
        assert '-> a -> list[2] item did not pass validation against callable: integer' in error

    def test_all_items_fail_length(self):
        data = {'a': [{'a': 2}, {'b': {'a': 'b'}}]}
        schema = ('a', iterables.AllItems((types.string, 2)))
        with raises(SchemaError) as exc:
            validate(data, schema)
        assert exc.value.args[0] == '-> a -> b  has less items in schema than in data'

    def test_all_items_fail_non_callable(self):
        data = {'a': [1, 2, '3', 4, 5]}
        schema = ('a', iterables.AllItems('foo'))
        with raises(Invalid) as exc:
            validate(data, schema)
        assert exc.value.args[0] == "-> a -> list[0] item did not match 'foo'"


    def test_any_items_fail(self):
        data = {'a': [1, 2, 3, 4, 5]}
        schema = ('a', iterables.AnyItem(types.string))
        with raises(Invalid) as exc:
            validate(data, schema)
        assert exc.value.args[0] == '-> a -> list[]  did not contain any valid items against callable: string'

    def test_any_items_fail_non_callable(self):
        data = {'a': [1, 2, 3, 4, 5]}
        schema = ('a', iterables.AnyItem('foo'))
        with raises(Invalid) as exc:
            validate(data, schema)
        assert exc.value.args[0] == "-> a -> list[]  did not contain any valid items matching 'foo'"

    def test_any_item_with_dictionaries(self):
        data = {'a': [{'a': 1}, {'b': 2}]}
        schema = ('a', iterables.AnyItem(('c', 4)))
        with raises(Invalid) as exc:
            validate(data, schema)
        assert exc.value.args[0] == "-> a -> list[]  did not contain any valid items matching ('c', 4)"


class TestWithRecursiveValidators(object):

    def test_all_objects_pass(self):
        data = {'a': {'a': 1, 'b': 2, 'c': 3}}
        schema = ('a', recursive.AllObjects((types.string, types.integer)))
        assert validate(data, schema) is None

    def test_any_objects_pass(self):
        data = {'a': {'a': 1, 'b':'a string', 'c': 3}}
        schema = ('a', recursive.AnyObject((types.string, types.string)))
        assert validate(data, schema) is None

    def test_all_objects_fail(self):
        data = {'a': {'a': 1, 'b': 'a string', 'c': 3}}
        schema = ('a', recursive.AllObjects((types.string, types.integer)))
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert '-> a -> b  did not pass validation against callable: integer' in error
        assert 'not of type int' in error

    def test_all_objects_fail_non_callable(self):
        data = {'a': {'a': 1, 'b': 1, 'c': 1}}
        schema = ('a', recursive.AllObjects((types.string, 2)))
        with raises(Invalid) as exc:
            validate(data, schema)
        assert exc.value.args[0] == '-> a -> a -> 1  did not match 2'

    def test_all_objects_fail_length(self):
        data = {'a': {'a': 2, 'b': {'a': 'b'}}}
        schema = ('a', recursive.AllObjects((types.string, 2)))
        with raises(SchemaError) as exc:
            validate(data, schema)
        assert exc.value.args[0] == '-> a -> b  has less items in schema than in data'

    def test_any_object_fail(self):
        data = {'a': {'a': 1, 'b': 4, 'c': 3}}
        schema = ('a', recursive.AnyObject((types.string, types.string)))
        with raises(Invalid) as exc:
            validate(data, schema)
        assert exc.value.args[0] == '-> a  did not contain any valid objects against callable: AnyObject'

    def test_any_objects_fail_non_callable(self):
        data = {'a': {'a': 1, 'b': 4, 'c': 3}}
        schema = ('a', recursive.AnyObject(('a', 'a')))
        with raises(Invalid) as exc:
            validate(data, schema)
        assert exc.value.args[0] == '-> a  did not contain any valid objects against callable: AnyObject'

    def test_no_pollution_from_previous_traversing_all_objects(self):
        data = {
                'a' : { 'a': 1, 'b': 2 },
                'b' : { 'c' :1, 'd': 2 },
                'c' : { 'e': 1, 'f': 2 }
            }
        schema = (
                ('a', (('a', 1), ('b', 2))),
                ('b', (('c', 1), ('d', 2))),
                ('c', recursive.AllObjects((types.string, types.string)))
            )
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert '-> c -> e  did not pass validation against callable: string' in error
        assert 'not of type str' in error

    def test_no_pollution_from_previous_traversing_all_items(self):
        data = {
                'a' : { 'a': 1, 'b': 2 },
                'b' : { 'c' :1, 'd': 2 },
                'c' : ['e', 1, 'f', 2 ]
            }
        schema = (
                ('a', (('a', 1), ('b', 2))),
                ('b', (('c', 1), ('d', 2))),
                ('c', iterables.AllItems(types.string))
            )
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert 'not of type string' in error
        assert '-> c -> list[1] item did not pass validation against callable: string' in error


class TestChainableAllIn(object):

    def test_all_items_pass(self):
        starts = lambda value: True
        data = {'a': 'some string'}
        schema = ('a', chainable.AllIn(types.string, starts))
        assert validate(data, schema) is None

    def test_one_item_fails(self):
        data = {'a': 'some string'}
        schema = ('a', chainable.AllIn(types.string, types.boolean))
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert '-> a  did not pass validation against callable: AllIn -> boolean' in error


class TestChainableAnyIn(object):

    def test_all_items_fail(self):
        def fail(value): raise AssertionError
        data = {'a': 'some string'}
        schema = ('a', chainable.AnyIn(types.boolean, fail))
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert '-> a  did not pass validation against callable: AnyIn' in error

    def test_one_item_passes(self):
        def fail(value): raise AssertionError
        data = {'a': 'some string'}
        schema = ('a', chainable.AnyIn(types.string, fail))
        assert validate(data, schema) is None


class TestOptional(object):

    def test_optional_value(self):
        data = {'optional': '', 'required': 2}
        schema = (('optional', optional(1)), ('required', 2))
        validate(data, schema)

    def test_optional_key(self):
        data = {'required': 2, 'zoo': 1}
        schema = ((optional('optional'), 1), ('required', 2), ('zoo', 1))
        validate(data, schema)
