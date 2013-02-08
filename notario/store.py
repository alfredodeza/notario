"""
Thread-safe storage for Notario.
"""
from threading import local

_state = local()


def _proxy(key):
    class ObjectProxy(object):
        def __getattr__(self, attr):
            obj = getattr(_state, key)
            return getattr(obj, attr)

        def __setattr__(self, attr, value):
            obj = getattr(_state, key)
            return setattr(obj, attr, value)

        def __delattr__(self, attr):
            obj = getattr(_state, key)
            return delattr(obj, attr)
    return ObjectProxy()


def create_store():
    """
    A helper for setting the _proxy and slapping the store
    object for us.

    :return: A thread-local storage as a dictionary
    """
    new_storage = _proxy('store')
    _state.store = type('store', (object,), {})
    new_storage.store = dict()
    return new_storage.store

store = create_store()


#
# Helpers
#

class new_store(object):

    def __init__(self):
        self.store = create_store()

    def __enter__(self):
        return self.store

    def __exit__( self, exc_type, exc_val, exc_tb):
        # clear the store regardless of exceptions
        del _state.store
        if exc_type:
            return False
        return True