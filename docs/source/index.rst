
Notario
=======
``notario`` is a validation engine for Python dictionaries, it offers very succinct
and flexible schemas and a very powerful way to express invalid data in
exceptions.

Install it with ``pip``::

    pip install notario

In its most simple example, this is how you would validate a single key, value
pair with ``notario``:

.. doctest::

    >>> from notario import validate
    >>> data = {'key': 'value'}
    >>> schema = ('key', 'value')
    >>> validate(data, schema)

And this is how it would look when it fails:

.. doctest::


    >>> data = {'foo': 1}
    >>> schema = ('foo', 'bar')
    >>> validate(data, schema)
    Traceback (most recent call last):
    ...
    Invalid: -> foo -> 1  did not match bar


Getting started
---------------
You should know that writing ``notario`` has a few expectations that you
should meet in order to be able to allow the engine to work as expected:

* Data to be validated is automatically **sorted alphabetically by key**
* Schemas **must** be written matching the alphabetical order of the data to be
  validated.
* Schemas must always be ``tuples`` representing key value pairs
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
    >>> validate(data, schema)
    Traceback (most recent call last):
    ...
    Invalid: -> foo  did not pass validation against callable: string


Validators
----------
``notario`` comes with a few validators, most of them provide a low level
validation model so you can build your own custom validators on top prividing
you with a lot of flexibility. These are all the current validators available:

* :class:`notario.validators.iterables.AllItems` : For items in an array, apply a schema to all of them.
* :class:`notario.validators.iterables.AnyItem` : Try to get a valid item in an array against a schema
* :class:`notario.validators.recursive.AllObjects` : For all dictionaries objects in a value pair.
* :class:`notario.validators.recursive.AnyObject`: Try to get a valid dictionary object in a value pair.


Handling nested data
--------------------
When data has deeply nested structures, it might be a good idea to use the
recursive validators as they can provide a way for validation of all (or any)
of the nested items in a given value.

For example, if you have some data that looks like:


::

    {
         'a': {
           'boo' : {
             'bar': True,
             'baz': False
             },
           'foo': {
             'bar': True,
             'baz': False
             },
           'yoo' : {
             'bar': True,
             'baz': False
           }
        }
    }

You wouldn't want to write a schema to match *every* single item inside the
value for the ``'a'`` key. To take advantage of the recursive validators, you
first identify that all the objects have a similar structure and write a schema
that matches that.

This is how a schema with the recursive validator would look like:

.. testsetup:: allobjects_passing

    from notario.exceptions import Invalid
    from notario import validate
    from notario.validators import types, recursive
    data = {
             'a': {
               'boo' : {
                 'bar': True,
                 'baz': False
                 },
               'foo': {
                 'bar': True,
                 'baz': False
                 },
               'yoo' : {
                 'bar': True,
                 'baz': False
               }
           }
       }


.. doctest:: allobjects_passing

    >>> from notario.validators import recursive, types
    >>> schema = (
    ...           'a', recursive.AllObjects(
    ...                         (types.string, (
    ...                             ('bar', types.boolean),
    ...                             ('baz', types.boolean)))
    ...                         )
    ...         )
    >>> validate(data, schema)


What the above schema says, is that all of the objects of the ``'a'`` value
should have:

#. a single key (of string type)
#. With a single dict object containing 2 keys
#. One of them being ``'bar'``
#. The other one ``'baz'``
#. Both these keys should have boolean values.

Just as important to pass validation, is equally important to see what happens
when it fails. Lets change the type from ``boolean`` to ``string`` for one of
the expected value in ``'baz'`` and see what happens:

.. testsetup:: allobjects_failing

    from notario.exceptions import Invalid
    from notario import validate
    from notario.validators import types, recursive
    data = {
             'a': {
               'boo' : {
                 'bar': True,
                 'baz': False
                 },
               'foo': {
                 'bar': True,
                 'baz': False
                 },
               'yoo' : {
                 'bar': True,
                 'baz': False
               }
           }
       }


.. doctest:: allobjects_failing

    >>> schema = (
    ...           'a', recursive.AllObjects(
    ...                         (types.string, (
    ...                             ('bar', types.string),
    ...                             ('baz', types.boolean)))
    ...                         )
    ...         )
    >>> validate(data, schema)
    Traceback (most recent call last):
    ...
    Invalid: -> a -> boo -> bar  did not pass validation against callable: string

As you can see by the output, when whe changed ``'bar'`` to enforce a string
and received a boolean, the exception message told you exactly where the
failure was.

API
---

Recursive Validators
--------------------

.. automodule:: notario.validators.recursive
  :members:

Iterable Validators
-------------------

.. automodule:: notario.validators.iterables
  :members:

Type Validators
---------------

.. automodule:: notario.validators.types
  :members:

Chainable Validators
--------------------

.. automodule:: notario.validators.chainable
  :members:


Optional Validators
-------------------

.. module:: notario.utils

.. autofunction:: optional


Other Decorators
----------------

.. automodule:: notario.decorators
  :members:

