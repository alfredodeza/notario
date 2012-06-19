from pytest import raises
from notario.validators import iterables
from notario.exceptions import Invalid, SchemaError


class TestAnyItem(object):

    def test_any_item_fail(self):
        data = [1, 2, 6, 4, 5]
        schema = 7
        with raises(Invalid) as exc:
            any_item = iterables.AnyItem(schema)
            any_item(data, [])
        msg = '-> list[]  did not contain any valid items matching 7'
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
        msg = "-> list[]  did not contain any valid items matching 'a'"
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


class TestAllItems(object):

    def test_all_items_pass(self):
        data = [1, 1, 1, 1]
        schema = 1
        all_items = iterables.AllItems(schema)
        assert all_items(data, []) is None

    def test_all_items_fail(self):
        data = [1, 1, 3, 1]
        schema = 1
        all_items = iterables.AllItems(schema)
        with raises(Invalid) as exc:
            all_items(data, [])
        assert exc.value.args[0] == '-> list[2] item did not match 1'

    def test_all_items_fail_last_item(self):
        data = [1, 1, 1, 3]
        schema = 1
        all_items = iterables.AllItems(schema)
        with raises(Invalid) as exc:
            all_items(data, [])
        assert exc.value.args[0] == '-> list[3] item did not match 1'

    def test_all_items_fail_uses_first_invalid(self):
        data = [3, 5, 2, 3]
        schema = 1
        all_items = iterables.AllItems(schema)
        with raises(Invalid) as exc:
            all_items(data, [])
        assert exc.value.args[0] == '-> list[0] item did not match 1'

