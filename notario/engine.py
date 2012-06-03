from notario.exceptions import Invalid
from notario.utils import is_callable


class Validator(object):
    
    def __init__(self, data, schema, **kw):
        self.data = normalize(data)
        self.schema = normalize(schema, sort=False)
        self.key_tree = ""
        self.value_tree = ""

    def validate(self):
        for i in range(len(self.data)):
            key, value = self.data.get(i)
            self.key_tree + " %s" % key
            skey, svalue = self.schema.get(i, (None, None))
            self.value_tree + " %s" % value
            if (skey, svalue) == (None, None):
                continue
            enforce(key, skey, self.key_tree)
            enforce(value, svalue, self.value_tree)


def normalize(data_structure, sort=True):
    """
    Receives a dictionary and returns an ordered 
    dictionary, with integers as keys for tuples.
    """
    if sort:
        data_structure = sorted(data_structure.items())
    return dict((number, value) for number, value in enumerate(data_structure))


def enforce(data_item, schema_item, tree):
    if is_callable(schema_item):
        try:
            schema(data_item)
        except:
            raise Invalid(schema_item, tree)
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
