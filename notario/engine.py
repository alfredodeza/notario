import sys
from notario.exceptions import Invalid, SchemaError, Skip
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
            return schema(data, tree)

        for index in range(len(data)):
            self.length_equality(data, schema, index, tree)
            key, value = data[index]
            skey, svalue = schema[index]
            tree.append(key)
            if isinstance(value, dict):
                self.traverser(value, svalue, tree)
            else:
                # In this while loop, because we may have optional validators
                # we can't rely on the fact that we will have a 1:1 mapping of
                # schema/data items, so if for some reason a key in the data
                # fails validation on an key in the schema and this key is
                # marked as ``is_optional`` it will raise a Skip exception,
                # telling us that we need to keep moving to the next item
                # declared in the schema
                try_count = index
                while True:
                    try:
                        self.leaf(data[index], schema[try_count], tree)
                        break
                    except Skip:
                        try_count += 1
            if tree:
                tree.pop()

    def leaf(self, data, schema, tree):
        """
        The deepest validation we can make in any given circumstance. Does not
        recurse, it will just receive both values and the tree, passing them on
        to the :fun:`enforce` function.
        """
        key, value = data
        skey, svalue = schema
        try:
            enforce(key, skey, tree, 'key')
        except :
            if hasattr(skey, 'is_optional'):
                # then this schema is the wrong one, so let's tell our caller
                # he needs to skip
                raise Skip
            raise # otherwise re-raise
        if hasattr(svalue, '__validator_leaf__'):
            return svalue(value, tree)
        enforce(value, svalue, tree, 'value')

    def length_equality(self, data, schema, index, tree):
        try:
            data = data[index]
            schema = schema[index]
        except (KeyError, TypeError):
            reason = "has less items in schema than in data"
            raise SchemaError(data, tree, reason=reason)
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

    def traverser(self, data, schema, tree):
        if len(data) < self.index:
            reason = "has not enough items to select from"
            raise SchemaError(data, tree, reason=reason)
        self.leaves(data, schema, tree)


class IterableValidator(BaseItemValidator):
    """
    The iterable validator allows the definition of a single schema that can be
    run against any number of items in a given data structure
    """

    def data_sanity(self, data):
        if not isinstance(data, list):
            reason = 'IterableValidator needs a list to validate'
            raise SchemaError('', [], reason=reason, pair='value')

    def leaf(self, index):
        self.data_sanity(self.data)
        self.enforce(self.data, self.schema, index, self.tree)

    def leaves(self, data, schema, tree):
        self.data_sanity(data)
        for item_index in range(self.index, len(data)):
            self.enforce(data, schema, item_index, tree)

    def enforce(self, data, schema, item_index, tree):
        if isinstance(data[item_index], dict) and isinstance(schema, tuple):
            try:
                _validator = Validator(data[item_index], schema)
                _validator.validate()
            except Invalid:
                e = sys.exc_info()[1]
                tree.append('list[%s]' % item_index)
                tree.extend(e.path)
                raise Invalid(e.schema_item, tree, pair='value')

            # FIXME this is utterly redundant, and also happens in
            # RecursiveValidator
            except SchemaError:
                e = sys.exc_info()[1]
                tree.extend(e.path)
                raise SchemaError('', tree, reason=e._reason, pair='value')

        elif isinstance(schema, tuple) and not isinstance(data[item_index], (tuple, dict)):
            raise SchemaError(data, tree, reason='iterable contains single items, schema does not')
        else:
            try:
                if is_callable(schema):
                    schema(data[item_index])
                else:
                    assert data[item_index] == schema
            except AssertionError:
                tree.append('list[%s]' % item_index)
                raise Invalid(schema, tree, pair='item')


class RecursiveValidator(BaseItemValidator):
    """
    The recursive validator allows the definition of a single schema that can
    be run against any number of items in a given data structure
    """

    def leaf(self, index):
        self.enforce(self.data, self.schema, index, self.tree)

    def leaves(self, data, schema, tree):
        for item_index in range(self.index, len(data)):
            self.enforce(data, schema, item_index, tree)

    def enforce(self, data, schema, item_index, tree):
        try:
            _validate = Validator({}, self.schema)
            _validate.data = {0: data[item_index]}
            _validate.validate()
        except Invalid:
            e = sys.exc_info()[1]
            tree.extend(e.path)
            raise Invalid(e.schema_item, tree, pair='value')
        except SchemaError:
            e = sys.exc_info()[1]
            tree.extend(e.path)
            raise SchemaError('', tree, reason=e._reason, pair='value')


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
    schema_is_optional = hasattr(schema_item, 'is_optional')
    if is_callable(schema_item) and not schema_is_optional:
        try:
            schema_item(data_item)
        except AssertionError:
            e = sys.exc_info()[1]
            raise Invalid(schema_item, tree, reason=e, pair=pair)
    else:
        try:
            if schema_is_optional:
                assert data_item == schema_item()
            else:
                assert data_item == schema_item
        except AssertionError:
            e = sys.exc_info()[1]
            if pair == 'value':
                tree.append(data_item)
            raise Invalid(schema_item, tree, reason=e, pair=pair)


def validate(data, schema):
    """
    Main entry point for the validation engine.

    :param data: The incoming data, as a dictionary object.
    :param schema: The schema from which data will be validated against
    """
    validator = Validator(data, schema)
    validator.validate()
