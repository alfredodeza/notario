from pytest import raises
from notario.validators import types
from notario.validators import recursive
from notario.exceptions import Invalid
from notario.normal import Data, Schema


class TestAllObjects(object):

    def test_all_objects_fail(self):
        data = {0:('a', '1'), 1:('b', 2), 2:('c', '3')}
        schema = ((types.string, types.integer))
        with raises(Invalid) as exc:
            any_object = recursive.AllObjects(schema)
            any_object(data, [])
        msg = '-> a -> 1 did not pass validation against callable: integer'
        error = exc.value.args[0]
        assert msg in error
        assert 'not of type int' in error

    def test_all_objects_pass(self):
        data = {0:('a', 1), 1:('b', 2), 2:('c', 3)}
        schema = ((types.string, types.integer))
        any_object = recursive.AllObjects(schema)
        assert any_object(data, []) is None


class TestAnyObject(object):

    def test_any_object_fail_all(self):
        data = {0:('a', '1'), 1:('b', '2'), 2:('c', '3')}
        schema = ((types.string, types.integer))
        with raises(Invalid) as exc:
            any_object = recursive.AnyObject(schema)
            any_object(data, [])
        msg = '-> top level did not contain any valid objects against callable: AnyObject'
        assert exc.value.args[0] == msg

    def test_any_object_pass_first(self):
        data = {0:('a', '1'), 1:('b', 2), 2:('c', 3)}
        schema = ((types.string, types.string))
        any_object = recursive.AnyObject(schema)
        assert any_object(data, []) is None

    def test_any_object_pass_second(self):
        data = {0:('a', 1), 1:('b', '2'), 2:('c', 3)}
        schema = ((types.string, types.string))
        any_object = recursive.AnyObject(schema)
        assert any_object(data, []) is None

    def test_any_object_pass_last(self):
        data = {0:('a', 1), 1:('b', 2), 2:('c', '3')}
        schema = ((types.string, types.string))
        any_object = recursive.AnyObject(schema)
        assert any_object(data, []) is None


class TestMultiSchema(object):

    def test_pass_single_data_item(self):
        data = Data({'a': 2}, {}).normalized()
        schemas = (('a', 2), ('b', 1))

        multi = recursive.MultiRecursive(*schemas)
        assert multi(data, []) is None

    def test_fail_on_non_callable(self):
        with raises(TypeError):
            recursive.MultiRecursive(False)

    def test_pass_two_data_items(self):
        data = Data({'a': 2, 'b': 1}, {}).normalized()
        schemas = (('a', 2), ('b', 1))

        multi = recursive.MultiRecursive(*schemas)
        assert multi(data, []) is None

    def test_pass_on_second_schema(self):
        data = Data({'b': 1}, {}).normalized()
        multi = recursive.MultiRecursive(('a', 2), ('b', 1))
        assert multi(data, []) is None

    def test_fail_on_last_schema(self):
        data = Data({'a': 2, 'b': 1}, {}).normalized()
        schemas = (('a', 2), ('b', 2))

        multi = recursive.MultiRecursive(*schemas)
        with raises(Invalid) as exc:
            multi(data, [])
        assert '1 did not match 2' in exc.value.args[0]

    def test_pass_on_third_schema(self):
        data = Data({'a': 2, 'b': 1}, {}).normalized()
        schemas = (('a', 2), ('b', 2), ('b', 1))

        multi = recursive.MultiRecursive(*schemas)
        assert multi(data, []) is None

    def test_pass_single_on_third_schema(self):
        data = Data({'z': 2}, {}).normalized()
        schemas = (('a', 2), ('b', 2), ('z', 2))

        multi = recursive.MultiRecursive(*schemas)
        assert multi(data, []) is None

    def test_fail_single_on_third_schema(self):
        data = Data({'z': 2}, {}).normalized()
        schemas = (('a', 2), ('b', 2), ('z', 1))

        multi = recursive.MultiRecursive(*schemas)
        with raises(Invalid) as exc:
            multi(data, [])
        assert 'z -> 2 did not match 1' in exc.value.args[0]

