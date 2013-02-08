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
