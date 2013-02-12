from notario import normal


class TestSchema(object):

    def test_return_data_structure_with_cero_index(self):
        result = normal.Schema({}, ['a']).normalized()
        assert result == {0: ['a']}

    def test_recurse_if_second_item_is_typle(self):
        data = ('a', ('a', 'b'))
        result = normal.Schema({}, data).normalized()
        assert result == {0: ('a', {0: ('a', 'b')})}

    def test_respect_more_than_two_values_in_tuple(self):
        data = ('a', (('a', 'b'), ('c', 'c'), ('d', 'd')))
        result = normal.Schema({}, data).normalized()
        assert result == {0: ('a', {0: ('a', 'b'), 1: ('c', 'c'), 2: ('d', 'd')})}

    def test_basic_key_value_pairs(self):
        data = (('a', 'b'), ('b', 'b'), ('c', 'c'))
        result = normal.Schema({}, data).normalized()
        assert result == {0: ('a', 'b'), 1: ('b', 'b'), 2: ('c', 'c')}
