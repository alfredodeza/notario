from notario.exceptions import Invalid
from notario.utils import is_callable


class Validator(object):

    def __init__(self, data, schema, **kw):
        self.data = normalize(data)
        self.schema = normalize_schema(schema)
        self.key_tree = ""
        self.value_tree = ""

    def validate(self):
        print "Data: %s" % self.data
        print "Schema %s" % self.schema
        for i in range(len(self.data)):
            key, value = self.data.get(i)
            key_tree = "%s %s" % (self.key_tree, key)
            skey, svalue = self.schema.get(i, (None, None))
            value_tree = "%s %s" % (self.value_tree, value)
            if (skey, svalue) == (None, None):
                continue
            enforce(key, skey, key_tree)
            enforce(value, svalue, value_tree)

    def key_value_validation(self, key, value, tree):
        """
        Will make recursion work better as we can call this
        over and over again until all nested data structures
        are processed and validated properly.
        """
        pass


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
        new_struct =  dict((number, value) for number, value in enumerate(data_structure))
        for i in range(len(new_struct)):
            value = new_struct.get(i)
            if len(value) == 2 and isinstance(value[1], tuple): # a nested tuple
                new_struct[i] = (value[0], normalize_schema(value[1]))
        return new_struct
    else:
        return {0: data_structure}


def enforce(data_item, schema_item, tree):
    if is_callable(schema_item):
        try:
            schema_item(data_item)
        except AssertionError as e:
            raise Invalid(schema_item, tree, reason=e)
    else:
        try:
            assert data_item == schema_item
        except AssertionError:
            raise Invalid(schema_item, tree)


def validate(data, schema, **kw):
    """
    Main entry point for the validation engine.

    :param data: The incoming data, as a dictionary object.
    :param schema: The schema from which data will be validated against
    """
    validator = Validator(data, schema, **kw)
    validator.validate()
