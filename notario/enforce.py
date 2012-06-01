from notario.utils import is_callable


def enforce(data, schema):
    try:
        if is_callable(schema):
            assert schema(data)
        else:
            assert data == schema
    except AssertionError:
        print "%s is not equal to %s" % (data, schema)

def validate(data, schema):
    data = sorted(data.items())
    data = dict((number, value) for number, value in enumerate(data))
    schema = dict((number, value) for number, value in enumerate(schema))

    for i in range(len(data)):
        key, value = data.get(i)
        skey, svalue = schema.get(i, (None, None))
        if (skey, svalue) == (None, None):
            continue
        enforce(key, skey)
        enforce(value, svalue)



data = {'a': True, 'b': False, 'r': [1,2,3,4]}
schema = ((is_string, True), ('b', is_boolean), (is_string, is_list))

validate(data, schema)
