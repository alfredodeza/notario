from pytest import raises
from notario.validators import iterables, types
from notario.exceptions import Invalid, SchemaError


class TestAnyItem(object):

    def test_any_item_fail(self):
        data = [1, 2, 6, 4, 5]
        schema = 7
        with raises(Invalid) as exc:
            any_item = iterables.AnyItem(schema)
            any_item(data, [])
        msg = '-> list[] did not contain any valid items matching 7'
        assert exc.value.args[0] == msg

    def test_tuple_schemas_cannot_run_on_single_values(self):
        data = [1, 2, 6, 4, 5]
        schema = ('a', 'b')
        with raises(SchemaError) as exc:
            any_item = iterables.AnyItem(schema)
            any_item(data, [])
        msg = "-> top level iterable contains single items, schema does not"
        assert exc.value.args[0] == msg

    def test_single_schemas_can_run_on_tuple_items(self):
        data = [{'a':'a'}, {'b':'b'}]
        schema = 'a'
        with raises(Invalid) as exc:
            any_item = iterables.AnyItem(schema)
            any_item(data, [])
        msg = "-> list[] did not contain any valid items matching 'a'"
        assert exc.value.args[0] == msg

    def test_any_item_pass(self):
        data = [1, 2, 6, 4, 5]
        schema = 6
        any_item = iterables.AnyItem(schema)
        assert  any_item(data, []) is None

    def test_any_item_pass_last_item(self):
        data = [1, 2, 3, 4, 6]
        schema = 6
        any_item = iterables.AnyItem(schema)
        assert  any_item(data, []) is None

    def test_any_item_fail_on_non_lists(self):
        data = 4
        schema = 1
        all_items = iterables.AnyItem(schema)
        with raises(Invalid) as exc:
            all_items(data, [])
        error = exc.value.args[0]
        assert  'top level did not pass validation against callable: AnyItem' in error

    def test_expecting_list_error(self):
        data = 4
        schema = 1
        all_items = iterables.AnyItem(schema)
        with raises(Invalid) as exc:
            all_items(data, [])
        assert 'expected a list but got int' == exc.value.reason



class TestAllItems(object):

    def test_all_items_pass(self):
        data = [1, 1, 1, 1]
        schema = 1
        all_items = iterables.AllItems(schema)
        assert all_items(data, []) is None

    def test_all_items_fail_on_non_lists(self):
        data = 4
        schema = 1
        all_items = iterables.AllItems(schema)
        with raises(Invalid) as exc:
            all_items(data, [])
        error = exc.value.args[0]
        assert  'top level did not pass validation against callable: AllItems' in error

    def test_expecting_list_error(self):
        data = 4
        schema = 1
        all_items = iterables.AllItems(schema)
        with raises(Invalid) as exc:
            all_items(data, [])
        assert 'expected a list but got int' == exc.value.reason

    def test_all_items_fail(self):
        data = [1, 1, 3, 1]
        schema = 1
        all_items = iterables.AllItems(schema)
        with raises(Invalid) as exc:
            all_items(data, [])
        error = exc.value.args[0]
        assert  '-> list[2] item did not match 1' in error

    def test_all_items_fail_last_item(self):
        data = [1, 1, 1, 3]
        schema = 1
        all_items = iterables.AllItems(schema)
        with raises(Invalid) as exc:
            all_items(data, [])

        error = exc.value.args[0]
        assert  '-> list[3] item did not match 1' in error

    def test_all_items_fail_uses_first_invalid(self):
        data = [3, 5, 2, 3]
        schema = 1
        all_items = iterables.AllItems(schema)
        with raises(Invalid) as exc:
            all_items(data, [])

        error = exc.value.args[0]
        assert  '-> list[0] item did not match 1' in error

    def test_fails_when_missing_items(self):
        data = [{"host": "example.com"}]
        schema = (("host", types.string),("interface", types.string))
        all_items = iterables.AllItems(schema)
        with raises(Invalid) as exc:
            all_items(data, [])
        error = exc.value.args[0]
        assert  "-> list[0] -> item[1] did not match 'interface'" in  error
        assert "(required item in schema is missing: interface)" in error
