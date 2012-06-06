

class Any(object):
    """
    Grab the first item and apply the schema needed
    """

    def __init__(self, schema):
        self.schema = schema

    def __call__(self, data):
        # call validator here against data
        pass


class All(object):
    """
    For all the items in an array apply the schema
    passed in
    """

    def __init__(self, schema):
        self.schema = schema

    def __call__(self, data):
        # call validator here against data
        pass

