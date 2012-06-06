from notario.exceptions import Invalid, SchemaError
from notario.utils import is_callable


class Validator(object):

    def __init__(self, data, schema, **kw):
        self.data = normalize(data)
        self.schema = normalize_schema(schema)

    def validate(self):
        self.traverser(self.data, self.schema, [])

    def traverser(self, data, schema, tree):
        """
        Traverses the dictionary, recursing onto itself if
        it sees apropriate key/value pairs that indicate that
        there is a need for more validation in a branch below us.
        """
        if len(data) != len(schema):
            raise SchemaError(data, tree, reason='length did not match schema')

        for index in range(len(data)):
            key, value = data[index]
            skey, svalue = schema[index]

            tree.append(key)
            if isinstance(value, dict):
                return self.traverser(value, svalue, tree)
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
        enforce(value, svalue, tree, 'value')



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
    if len(data_structure) == 2 and isinstance(data_structure[1], tuple):
        if not isinstance(data_structure[0], tuple):
            new_struct = {0: (data_structure[0], normalize_schema(data_structure[1]))}
        else:
            new_struct = dict((number, value) for number, value in enumerate(data_structure))
        for i in range(len(new_struct)):
            value = new_struct.get(i)
            if len(value) == 2 and isinstance(value[1], tuple): # a nested tuple
                new_struct[i] = (value[0], normalize_schema(value[1]))
        return new_struct
    elif len(data_structure) > 2:
        return dict((number, value) for number, value in enumerate(data_structure))
    else:
        return {0: data_structure}


def enforce(data_item, schema_item, tree, pair):
    if is_callable(schema_item):
        try:
            schema_item(data_item)
        except AssertionError as e:
            raise Invalid(schema_item, tree, reason=e, pair=pair)
    else:
        try:
            assert data_item == schema_item
        except AssertionError:
            if pair == 'value':
                tree.append(data_item)
            raise Invalid(schema_item, tree, pair=pair)


def validate(data, schema, **kw):
    """
    Main entry point for the validation engine.

    :param data: The incoming data, as a dictionary object.
    :param schema: The schema from which data will be validated against
    """
    validator = Validator(data, schema, **kw)
    validator.validate()
