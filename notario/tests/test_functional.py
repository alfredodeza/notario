from pytest import raises
from notario import validate
from notario.exceptions import Invalid, SchemaError
from notario.validators import (iterables, recursive, types,
                                chainable, cherry_pick, Hybrid)
from notario.decorators import optional


class TestValidate(object):

    def test_simple_validation_against_empty_data(self):
        data = {}
        schema = (('a', 'b'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert 'top level has no data to validate against schema' in error

    def test_most_simple_validation(self):
        data = {'a': 'a'}
        schema = (('a', 'b'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> a -> a did not match 'b'" in error

    def test_required_key_is_missing(self):
        data = {'a': 'a', 'c': 'c'}
        schema = (('a', 'a'), ('b', 'b'), ('c', 'c'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "key did not match schema" in error
        assert  "required key in data is missing: b" in error
    def test_key_is_empty_string(self):
        data = {'a': ''}
        schema = (('a', 'b'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> a -> '' did not match 'b'" in error

    def test_multi_pair_non_nested_last(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'a'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> d -> d did not match 'a'" in error

    def test_multi_pair_non_nested_first(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'b'), ('b', 'b'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> a -> a did not match 'b'" in error

    def test_multi_pair_non_nested_second(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'a'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> b -> b did not match 'a'" in error

    def test_multi_pair_non_nested_third(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('c', 'a'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> c -> c did not match 'a'" in error

    def test_multi_pair_non_nested_last_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('c', 'c'), ('a', 'a'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> d key did not match 'a'" in error

    def test_multi_pair_non_nested_first_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('f', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> a key did not match 'f'" in error

    def test_multi_pair_non_nested_second_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('f', 'b'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> b key did not match 'f'" in error

    def test_multi_pair_non_nested_third_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('f', 'c'), ('d', 'a'))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> c key did not match 'f'" in error

    def test_key_fails_before_value(self):
        data = {'a': {'a': {'b': 'b'}}}
        schema = ('a', ('b', ('b', 'b')))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> a -> a key did not match 'b'" in error


class TestCherryPick(object):

    def test_validate_only_one_item(self):
        data = {'a': {'b': 'b', 'c': 'c', 'd': 'd'}}
        schema = ('a', cherry_pick(('b', 'a')))

        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> a -> b -> b did not match 'a'" in error

    def test_validate_custom_items(self):
        data = {'a': {'b': 'b', 'c': 'c', 'd': 'd'}}
        picky = cherry_pick((('b' ,'b')))
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

        error = exc.value.args[0]
        assert  "-> a  must_validate attribute must not be empty" in error


class TestHybrid(object):

    def test_hybrid_delegates_when_dict_or_list(self):
        # send off to Recursive when isinstance(value, (dict, list))
        data = {'a':  ['a']}
        hybrid = Hybrid(types.string, iterables.AllItems('b'))
        schema = ('a', hybrid)
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert "list[0] item did not match 'b'" in error

    def test_hybrid_delegates_when_dict_or_empty_list(self):
        # send off to Recursive when isinstance(value, (dict, list))
        data = {'a':  []}
        hybrid = Hybrid(types.string, iterables.AllItems('b'))
        schema = ('a', hybrid)
        assert validate(data, schema) is None


class TestWithIterableValidators(object):

    def test_all_items_pass(self):
        data = {'a': [1, 2, 3, 4, 5]}
        schema = ('a', iterables.AllItems(types.integer))
        assert validate(data, schema) is None

    def test_nested_can_raise_nested_invalid(self):
        data = {'a': {'a': 'b'}}
        data = {'a': [{'a': [1,2]}, {'a': {}}]}
        nested_schema = ('a', iterables.AllItems(types.integer))
        schema = ('a', iterables.AllItems(nested_schema))
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert 'did not pass validation against callable: integer'
        assert exc.value.reason == 'expected a list but got dict'

    def test_nested_raises_nested_invalid(self):
        data = {'a': [{'a': ['a']}, {'b': 'c'}]}
        nested_schema = iterables.MultiIterable(('a', ['b']), ('b', 'c'))
        schema = ('a', iterables.AllItems(nested_schema))
        with raises(Invalid) as exc:
            validate(data, schema)
        assert exc.value.reason == 'expected a list but got dict'

    def test_any_items_pass(self):
        data = {'a': [1, 2, 'a string', 4, 5]}
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
        error = exc.value.args[0]
        assert  '-> a -> b  has less items in schema than in data' in error

    def test_all_items_fail_non_callable(self):
        data = {'a': [1, 2, '3', 4, 5]}
        schema = ('a', iterables.AllItems('foo'))
        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> a -> list[0] item did not match 'foo'" in error

    def test_any_items_fail(self):
        data = {'a': [1, 2, 3, 4, 5]}
        schema = ('a', iterables.AnyItem(types.string))
        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  '-> a -> list[] did not contain any valid items against callable: string' in error

    def test_any_items_fail_non_callable(self):
        data = {'a': [1, 2, 3, 4, 5]}
        schema = ('a', iterables.AnyItem('foo'))
        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> a -> list[] did not contain any valid items matching 'foo'" in error

    def test_any_item_with_dictionaries(self):
        data = {'a': [{'a': 1}, {'b': 2}]}
        schema = ('a', iterables.AnyItem(('c', 4)))
        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  "-> a -> list[] did not contain any valid items matching ('c', 4)" in error


class TestWithRecursiveValidators(object):

    def test_all_objects_pass(self):
        data = {'a': {'a': 1, 'b': 2, 'c': 3}}
        schema = ('a', recursive.AllObjects((types.string, types.integer)))
        assert validate(data, schema) is None

    def test_nested_raises_nested_invalid(self):
        data = {'a': {'a': ['a'], 'b': {}}}
        nested_schema = iterables.AllItems(types.string)
        schema = ('a', recursive.AllObjects((types.string, nested_schema)))
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert 'did not pass validation against callable: AllItems' in error

    def test_all_objects_pass_with_hybrid(self):
        data = {'a': {'a': 1, 'b': 2, 'c': 3}}
        dawg = Hybrid(lambda x: True, (types.string, types.integer))
        yo_dawg = recursive.AllObjects(dawg)
        schema = ('a', yo_dawg)
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
        assert '-> a -> b -> a string did not pass validation against callable: integer' in error
        assert 'not of type int' in error

    def test_all_objects_fail_non_callable(self):
        data = {'a': {'a': 1, 'b': 1, 'c': 1}}
        schema = ('a', recursive.AllObjects((types.string, 2)))
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert  '-> a -> a -> 1 did not match 2' in error

    def test_all_objects_fail_length(self):
        data = {'a': {'a': 2, 'b': {'a': 'b'}}}
        schema = ('a', recursive.AllObjects((types.string, 2)))
        with raises(SchemaError) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  '-> a -> b  has less items in schema than in data' in error

    def test_any_object_fail(self):
        data = {'a': {'a': 1, 'b': 4, 'c': 3}}
        schema = ('a', recursive.AnyObject((types.string, types.string)))
        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  '-> a did not contain any valid objects against callable: AnyObject' in error

    def test_any_objects_fail_non_callable(self):
        data = {'a': {'a': 1, 'b': 4, 'c': 3}}
        schema = ('a', recursive.AnyObject(('a', 'a')))
        with raises(Invalid) as exc:
            validate(data, schema)

        error = exc.value.args[0]
        assert  '-> a did not contain any valid objects against callable: AnyObject' in error

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
        assert '-> c -> e -> 1 did not pass validation against callable: string' in error
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
        assert '-> a -> some string did not pass validation against callable: AllIn -> boolean' in error


class TestChainableAnyIn(object):

    def test_all_items_fail(self):
        def fail(value): raise AssertionError
        data = {'a': 'some string'}
        schema = ('a', chainable.AnyIn(types.boolean, fail))
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert '-> a -> some string did not pass validation against callable: AnyIn' in error

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
