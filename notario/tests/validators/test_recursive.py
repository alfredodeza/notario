from pytest import raises
from notario.validators import types
from notario.validators import recursive
from notario.exceptions import Invalid


class TestAllObjects(object):

    def test_all_objects_fail(self):
        data = {0:('a', '1'), 1:('b', 2), 2:('c', '3')}
        schema = ((types.string, types.integer))
        with raises(Invalid) as exc:
            any_object = recursive.AllObjects(schema)
            any_object(data, [])
        msg = '-> a  did not pass validation against callable: integer'
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
