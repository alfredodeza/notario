from notario.exceptions import Invalid
from notario.utils import is_callable


class Validator(object):
    
    def __init__(self, data, schema, **kw):
        self.data = normalize(data)
        self.schema = normalize_schema(schema)
        self.key_tree = ""
        self.value_tree = ""

    def validate(self):
        for i in range(len(self.data)):
            key, value = self.data.get(i)
            key_tree = "%s %s" % (self.key_tree, key)
            skey, svalue = self.schema.get(i, (None, None))
            value_tree = "%s %s" % (self.value_tree, value)
            if (skey, svalue) == (None, None):
                continue
            enforce(key, skey, key_tree)
            enforce(value, svalue, value_tree)


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
    normalized = {}
    for number, value in enumerate(data_structure):
        if isinstance(value[1], tuple): # a nested tuple
            normalized[number] = normalize_schema(value[1])
        else:
            normalized[number] = value
    return normalized
    #for i in range(len(mapped)):
        #k, v = mapped.get(i)
    #for k, v in mapped.items():
        #if isinstance(v, tuple):
            #mapped[i][k] = dict((number, value) for number, value in enumerate(v))

    #return mapped



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
