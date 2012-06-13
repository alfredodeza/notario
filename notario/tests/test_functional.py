from pytest import raises
from notario import validate
from notario.exceptions import Invalid


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
