import sys
from notario.exceptions import Invalid, SchemaError
from notario.utils import is_callable


class Validator(object):

    def __init__(self, data, schema):
        self.data = normalize(data)
        self.schema = normalize_schema(schema)

    def validate(self):
        self.length_equality(self.data, self.schema, 0, [])
        self.traverser(self.data, self.schema, [])

    def traverser(self, data, schema, tree):
        """
        Traverses the dictionary, recursing onto itself if
        it sees apropriate key/value pairs that indicate that
        there is a need for more validation in a branch below us.
        """
        if hasattr(schema, '__validator_leaf__'):
            try:
                return schema(data)
            except Invalid:
                e = sys.exc_info()[1]
                tree.extend(e.path)
                raise Invalid(e.schema_item, tree, pair=e._pair)

        for index in range(len(data)):
            self.length_equality(data, schema, index, tree)
            key, value = data[index]
            skey, svalue = schema[index]
            tree.append(key)
            if isinstance(value, dict):
                self.traverser(value, svalue, tree)
                tree.pop()
            else:
                self.leaf(data[index], schema[index], tree)
                tree.pop()

    def leaf(self, data, schema, tree):
        """
        The deepest validation we can make in any given circumstance. Does not
        recurse, it will just receive both values and the tree, passing them on
        to the :fun:`enforce` function.
        """
        key, value = data
        skey, svalue = schema
        enforce(key, skey, tree, 'key')
        if hasattr(svalue, '__validator_leaf__'):
            return svalue(value, tree)
        enforce(value, svalue, tree, 'value')


    def length_equality(self, data, schema, index, tree):
        try:
            data = data[index]
            schema = schema[index]
        except KeyError:
            raise SchemaError(data, tree, reason="less items in schema than in data")
        if hasattr(schema, '__validator_leaf__'):
            return
        if len(data) != len(schema):
            raise SchemaError(data, tree, reason='length did not match schema')


class BaseItemValidator(object):

    def __init__(self, data, schema, tree=None, index=None):
        self.data = data
        self.schema = schema
        self.tree = tree or []
        self.index = index or 0

    def validate(self):
        self.traverser(self.data, self.schema, self.tree)


class IterableValidator(BaseItemValidator):
    """
    The iterable validator allows the definition of a single schema that can be
    run against any number of items in a given data structure
    """

    def traverser(self, data, schema, tree):
        """
        Here there is really no need for traversing any more
        we are running under the assumption that we are an actual
        leaf and there is no more to recurse into.
        """
        if len(data) < self.index:
            raise SchemaError(data, tree, reason="not enough items in data to select from")
        self.leaves(data, self.schema, tree)

    def leaves(self, data, schema, tree):
        for item_index in range(self.index, len(data)):
            if (data[item_index], dict) and isinstance(schema, tuple):
                try:
                    _validator = Validator(data[item_index], schema)
                    return _validator.validate()
                except Invalid:
                    e = sys.exc_info()[1]
                    tree.append('list[%s]' % item_index)
                    tree.extend(e.path)
                    raise Invalid(e.schema_item, tree, pair='value')
            else:
                try:
                    assert data[item_index] == schema
                except AssertionError:
                    tree.append('list[%s]' % item_index)
                    raise Invalid(schema, tree, pair='item')


class RecursiveValidator(BaseItemValidator):
    """
    The recursive validator allows the definition of a single schema that can be
    run against any number of items in a given data structure
    """

    def traverser(self, data, schema, tree):
        schema = normalize_schema(self.schema)
        if len(data) < self.index:
            raise SchemaError(data, tree, reason="not enough items in data to select from")
        for index in range(self.index, len(data)):
            _validate = Validator({}, {})
            _validate.data = {0: data[index]}
            _validate.schema = schema
            _validate.validate()


def normalize(data_structure, sort=True):
    """
    Receives a dictionary and returns an ordered
    dictionary, with integers as keys for tuples.
    """
    if sort:
        for k, v in data_structure.items():
            if isinstance(v, dict):
                data_structure[k] = normalize(v)
        data_structure = sorted(data_structure.items())
    return dict((number, value) for number, value in enumerate(data_structure))


def normalize_schema(data_structure):
    if len(data_structure) == 2 and isinstance(data_structure[1], tuple) or len(data_structure) > 2:
        if not isinstance(data_structure[0], tuple):
            new_struct = {0: (data_structure[0], normalize_schema(data_structure[1]))}
        else:
            new_struct = dict((number, value) for number, value in enumerate(data_structure))
        for i in range(len(new_struct)):
            value = new_struct.get(i)
            if len(value) == 2 and isinstance(value[1], tuple): # a nested tuple
                new_struct[i] = (value[0], normalize_schema(value[1]))
        return new_struct
    else:
        return {0: data_structure}


def enforce(data_item, schema_item, tree, pair):
    if is_callable(schema_item):
        try:
            schema_item(data_item)
        except AssertionError:
            e = sys.exc_info()[1]
            raise Invalid(schema_item, tree, reason=e, pair=pair)
    else:
        try:
            assert data_item == schema_item
        except AssertionError:
            if pair == 'value':
                tree.append(data_item)
            raise Invalid(schema_item, tree, pair=pair)


def validate(data, schema):
    """
    Main entry point for the validation engine.

    :param data: The incoming data, as a dictionary object.
    :param schema: The schema from which data will be validated against
    """
    validator = Validator(data, schema)
    validator.validate()
