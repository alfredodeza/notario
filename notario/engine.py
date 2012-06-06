from notario.exceptions import Invalid
from notario.utils import is_callable


class Validator(object):

    def __init__(self, data, schema, **kw):
        self.data = normalize(data)
        self.schema = normalize_schema(schema)

    def validate(self):
        def validate_tuple(data, schema, k_tree, v_tree):
            key, value = data
            skey, svalue = schema
            enforce(key, skey, k_tree, 'key')
            enforce(value, svalue, k_tree, 'value')

        def traverser(data, schema, k_tree, v_tree, index=0):
            for index in range(index, len(data)):
                key, value = data[index]
                skey, svalue = schema[index]

                k_tree.append(key)
                v_tree.append(value)
                if isinstance(value, dict):
                    return traverser(value, svalue, k_tree, v_tree)
                else:
                    validate_tuple(data[index], schema[index], k_tree, v_tree)
                    k_tree.pop()
                    v_tree.pop()


        if len(self.data) != len(self.schema):
            raise Exception("lengths are no equal")
        traverser(self.data, self.schema, [], [])

    def key_value_validation(self, data_item, schema_item, tree):
        """
        Will make recursion work better as we can call this
        over and over again until all nested data structures
        are processed and validated properly.
        """
        return enforce(data_item, schema_item, tree)


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
