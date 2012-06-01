

def is_callable(data):
    if hasattr(data, '__call__'):
        return True
    return False
