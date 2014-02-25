from pytest import raises

from notario.normal import Data
from notario import utils
from notario.decorators import delay


class TestIsCallable(object):

    def setup(self):
        def fake_callable(): pass
        self.fake_callable = fake_callable

    def test_is_callable(self):
        result = utils.is_callable(self.fake_callable)
        assert result is True

    def test_is_not_callable(self):
        result = utils.is_callable(1)
        assert result is False


class TestOptionalDecorator(object):

    def fake_validator(self, value):
        return True

    def test_has_no_value(self):
        result = utils.optional(self.fake_validator)('')
        assert result is None

    def test_value(self):
        result = utils.optional(self.fake_validator)('some value!')
        assert result is True

    def test_decorator_is_marked_as_optional(self):
        result = utils.optional('')
        assert result.is_optional is True

    def test_value_has_string(self):
        result = utils.optional('value')
        assert result() == 'value'


class TestSift(object):

    def test_no_required_items(self):
        data = Data({'a': 1, 'b': 2}, {}).normalized()
        result = utils.sift(data)
        assert result == {}

    def test_get_one_item_back(self):

        data = Data({'a': 1, 'b': 2}, {}).normalized()
        result = utils.sift(data, ['b'])
        assert result == {0: ('b', 2)}


class TestReSort(object):

    def test_keys_will_reset_to_zero(self):
        data = {16: ('a', 1), 4: ('b', 1), 3: ('a',1)}
        result = utils.re_sort(data)
        assert result == {0: ('a', 1), 1: ('b', 1), 2: ('a', 1)}


class TestIsEmpty(object):

    def test_not_any_valid_structure_is_false(self):
        result = utils.is_empty(False)
        assert result is False

    def test_valid_structures_are_false_when_empty(self):
        for structure in [[], {}, '']:
            assert utils.is_empty(structure) is True


class TestIsNestedTuple(object):

    def test_is_nested_tuple(self):
        value = (1, (1, 2))
        assert utils.is_nested_tuple(value) is True

    def test_is_single_tuple(self):
        value = (1,)
        assert utils.is_nested_tuple(value) is False

    def test_second_value_is_not_typle(self):
        value = ('a', 'b')
        assert utils.is_nested_tuple(value) is False


class TestDataItem(object):

    def setup(self):
        self.ndict = utils.ndict()

    def test_return_key_from_ndict(self):
        self.ndict[0] = ('a', 'b')
        assert utils.data_item(self.ndict) == "'a'"

    def test_return_key_from_non_ndict(self):
        data = {'b': 'b'}
        assert utils.data_item(data) == "'b'"

    def test_return_first_item_in_list(self):
        data = ['a', 'b', 'c']
        assert utils.data_item(data) == "'a'"

    def test_fallback_to_repr_of_obj(self):
        assert utils.data_item(self.ndict) == "{}"


class TestExpandSchema(object):

    def test_not_delayed(self):
        schema = ('a', 'b')
        assert utils.expand_schema(schema) == schema

    def test_is_delayed(self):
        @delay
        def my_schema():
            return 'a', 'b'
        assert utils.expand_schema(my_schema) == ('a', 'b')


class TestIsSchema(object):

    def test_if_is_tuple(self):
        assert utils.is_schema(('a', 'b')) is True

    def test_is_delayed(self):
        schema = delay(lambda x: True)
        assert utils.is_schema(schema) is True

    def test_is_not_tuple(self):
        assert utils.is_schema([]) is False


class TestEnsure(object):

    def test_ensure(self):
        assert utils.ensure(1 == 1)

    def test_ensure_raises_assertionerror(self):
        with raises(AssertionError):
            utils.ensure(0 == 1)
