"""
Thread-safe storage for Notario.
"""
from threading import local

_state = local()


def proxy(key):
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


def create_storage():
    new_storage = proxy('storage')
    _state.storage = type('storage', (object,), {})
    new_storage.store = {}
    return new_storage.store

storage = create_storage()
