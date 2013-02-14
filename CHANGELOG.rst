0.1.0
-----
If you could summarize a *wealth* of new features, it would be this release!

* Introduce the ``Hybrid`` validator: create one with a validator and a schema
* Create a ``cherry_pick`` validator: Validate present keys, ignore the rest
* Improved exception messages, several fixes to include ``exception.reason``
* Created a ``MultiSchema`` validator: define several schemas, try each one on
  failure, raise if none passes.
* Added a global store, so that validators can *remember* if some value has
  been seen.
* ``optiional`` can now be used on keys (not only values)
* All validators in ``notario.types`` can be used as decorators as well.
* Added new decorators: ``not_empty``, ``instance_of``
