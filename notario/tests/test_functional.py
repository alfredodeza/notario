from pytest import raises
from notario import validate
from notario.exceptions import Invalid
from notario.validators import iterables, recursive, types


class TestValidate(object):

    def test_most_simple_validation(self):
        data = {'a': 'a'}
        schema = (('a', 'b'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == '-> a -> a  did not match b'
        
    def test_multi_pair_non_nested_last(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'a'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == '-> d -> d  did not match a'

    def test_multi_pair_non_nested_first(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'b'), ('b', 'b'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == '-> a -> a  did not match b'

    def test_multi_pair_non_nested_second(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'a'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == '-> b -> b  did not match a'

    def test_multi_pair_non_nested_third(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('c', 'a'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == '-> c -> c  did not match a'

    def test_multi_pair_non_nested_last_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('c', 'c'), ('a', 'a'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == '-> d key did not match a'

    def test_multi_pair_non_nested_first_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('f', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == '-> a key did not match f'

    def test_multi_pair_non_nested_second_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('f', 'b'), ('c', 'c'), ('d', 'd'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == '-> b key did not match f'

    def test_multi_pair_non_nested_third_key(self):
        data = {'a': 'a', 'b':'b', 'c':'c', 'd':'d'}
        schema = (('a', 'a'), ('b', 'b'), ('f', 'c'), ('d', 'a'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == '-> c key did not match f'


class TestWithIterableValidators(object):

    def test_all_items_pass(self):
        data = {'a': [1,2,3,4,5]}
        schema = ('a', iterables.AllItems(types.integer))
        assert validate(data, schema) is None

    def test_any_items(self):
        data = {'a': [1,2, 'a string' ,4,5]}
        schema = ('a', iterables.AnyItem(types.string))
        assert validate(data, schema) is None

    def test_all_items_fail(self):
        data = {'a': [1,2, '3',4,5]}
        schema = ('a', iterables.AllItems(types.integer))
        with raises(Invalid) as exc:
            validate(data, schema)
        assert exc.value.args[0] == '-> a -> list[2] item did not pass validation against callable: integer'

    def test_any_items_fail(self):
        data = {'a': [1, 2, 3,4,5]}
        schema = ('a', iterables.AnyItem(types.string))
        with raises(Invalid) as exc:
            validate(data, schema)
        assert exc.value.args[0] == '-> a -> list[]  did not contain any valid items against callable: string'

    def test_any_items_fail_non_callable(self):
        data = {'a': [1, 2, 3,4,5]}
        schema = ('a', iterables.AnyItem('foo'))
        with raises(Invalid) as exc:
            validate(data, schema)
        assert exc.value.args[0] == '-> a -> list[]  did not contain any valid items matching foo'

