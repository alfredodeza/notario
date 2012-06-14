
Notario
=======
``notario`` is a validation engine for Python dictionaries, it offers very succinct
and flexible schemas and a very powerful way to express invalid data in
exceptions.

In its most simple example, this is how you would validate a single key, value
pair with ``notario``:

.. doctest::

    >>> from notario import validate
    >>> data = {'key': 'value'}
    >>> schema = ('key', 'value')
    >>> validate(data, schema)

And this is how it would look when it fails:

.. doctest::


    >>> from notario import validate
    >>> from notario.exceptions import Invalid
    >>> data = {'foo': 1}
    >>> schema = ('foo', 'bar')
    >>> try:
    ...     validate(data, schema)
    ... except Invalid, e:
    ...     print e
    ...
    -> foo -> 1  did not match bar


Getting started
---------------
You should know that writing ``notario`` has a few expectations that you
should meet in order to be able to allow the engine to work as expected:

* Data to be validated is automatically **sorted alphabetically by key**
* Schemas **must** be written matching the alphabetical order of the data to be
  validated.
* Schemas must always be ``tuples`` as key value pairs
* Data can contain any kind of data structure **except for tuples**.

Writing schemas can get overly verbose. Consider other validators where you
need to define if a value is required or optional or that it should be of
a certain length, minimum item count, or maximum values. This is crazy.

``notario`` allows you to have callables that should be written to accept
a single required argument and assert *whatever* you need to make sure the
value complies with the expectation. The following example is how one of the
validators from ``notario`` itself is written to make sure a value is a
string::

    def string(value):
        """
        Validates a given input is of type string.
        """
        assert isinstance(value, basestring), "not of type string"

If the ``value`` passed in is not a string, it will raise an
``AsssertionError`` and ``notario`` will catch this and report back where and
how it failed.

This is how you would use it:

.. doctest::

    >>> from notario.validators import types
    >>> from notario.exceptions import Invalid
    >>> data = {'foo': 1}
    >>> schema = (types.string, types.integer)
    >>> from notario import validate
    >>> validate(data, schema)

And when it fails, it would actually tell you where it did and against what, in
the below example we change the value of the schema to be of ``types.string``
and not integer, forcing an ``Invalid`` exception:

.. doctest::


    >>> schema = (types.string, types.string)
    >>> try:
    ...     validate(data, schema)
    ... except Invalid, e:
    ...     print e
    ...
    -> foo  did not pass validation against callable: string
