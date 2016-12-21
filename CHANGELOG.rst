0.0.12
------
21-Dec-2016

* Detect missing data keys

0.0.11
------
24-Feb-2016

* Improves the error message when an schema item is required but the data is
  missing it. Before it assumed it was a list item.

0.0.10
------
23-Feb-2016

* Fixes an issue when extra items in a schema are required but missing from
  data but would not raise Invalid.

0.0.9
-----
15-Feb-2016

* Improve tests to work with latest py.test release that broke assertion errors
* Include the license file when cutting a release

0.0.8
-----
* fail when dictionaries are empty and a schema is provided

0.0.7
-----
* Fix odd spacing in error messages

0.0.6
-----
Note this entry does not refelct fully the features in 0.0.6
* Python 3 compatibility
* Replace use of asserts with wrapped ensure() to deal with python -O
* creates a utility to validate called ``ensure``

0.0.5
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
