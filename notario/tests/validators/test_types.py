from pytest import raises
from notario.validators import types
from notario.tests import util

#
# Most of these are just excercising the code really
# as they are just making sure isinstance returns
# what we expect, effectively testing python
#


class TestTypes(object):

    def test_string_pass(self):
        assert types.string('a string') is None

    def test_boolean_pass(self):
        assert types.boolean(False) is None

    def test_dictionary_pass(self):
        assert types.dictionary({}) is None

    def test_array_pass(self):
        assert types.array([]) is None

    def test_integer_pass(self):
        assert types.integer(1) is None

    def test_string_fail(self):
        with raises(AssertionError) as exc:
            types.string(1)
        assert exc.value.args[0] == 'not of type string'

    def test_boolean_fail(self):
        with raises(AssertionError) as exc:
            types.boolean('a string')
        assert exc.value.args[0] == 'not of type boolean'

    def test_dictionary_fail(self):
        with raises(AssertionError) as exc:
            types.dictionary([])
        assert exc.value.args[0] == 'not of type dictionary'

    def test_array_fail(self):
        with raises(AssertionError) as exc:
            types.array({})
        assert exc.value.args[0] == 'not of type array'

    def test_integer_fail(self):
        with raises(AssertionError) as exc:
            types.integer('a string')
        assert exc.value.args[0] == 'not of type int'


class TestTypesAsDecorators(object):

    def test_string_pass(self):
        @types.string
        def validate(value):
            assert value == "a string"

        assert validate('a string') is None

    def test_boolean_pass(self):
        @types.boolean
        def validate(value):
            assert value is False

        assert validate(False) is None

    def test_dictionary_pass(self):
        @types.dictionary
        def validate(value):
            assert value == {}

        assert validate({}) is None

    def test_array_pass(self):
        @types.array
        def validate(value):
            assert value == []

        assert validate([]) is None

    def test_integer_pass(self):
        @types.integer
        def validate(value):
            assert value == 1

        assert validate(1) is None

    def test_string_fail(self):
        @types.string
        def validate(value):
            assert value == 'a string' # pragma: no cover

        with raises(AssertionError) as exc:
            validate(1)
        assert exc.value.args[0] == 'not of type string'

    def test_boolean_fail(self):
        @types.boolean
        def validate(value):
            assert value is False # pragma: no cover

        with raises(AssertionError) as exc:
            validate('a string')
        assert exc.value.args[0] == 'not of type boolean'

    def test_dictionary_fail(self):
        @types.dictionary
        def validate(value):
            assert value == {} # pragma: no cover

        with raises(AssertionError) as exc:
            validate([])
        assert exc.value.args[0] == 'not of type dictionary'

    def test_array_fail(self):
        @types.array
        def validate(value):
            assert value is False # pragma: no cover

        with raises(AssertionError) as exc:
            validate({})
        assert exc.value.args[0] == 'not of type array'

    def test_integer_fail(self):
        @types.integer
        def validate(value):
            assert value == 1 # pragma: no cover

        with raises(AssertionError) as exc:
            validate('a string')
        assert exc.value.args[0] == 'not of type int'


class TestTypesDelegating(object):

    def test_string_decorated(self):
        @types.string
        def validate(value):
            assert len(value) == 1, 'too long'

        with raises(AssertionError) as exc:
            validate('123')
        result = util.assert_message(exc)
        assert result == 'too long'

    def test_boolean_decorated(self):
        @types.boolean
        def validate(value):
            assert value is False, 'not false'

        with raises(AssertionError) as exc:
            validate(True)
        result = util.assert_message(exc)
        assert result == 'not false'

    def test_dictionary_decorated(self):
        @types.dictionary
        def validate(value):
            assert len(value) == 1, 'too long'

        with raises(AssertionError) as exc:
            validate({'a': 1, 'b': 2})
        result = util.assert_message(exc)
        assert result == 'too long'

    def test_array_decorated(self):
        @types.array
        def validate(value):
            assert len(value) == 1, 'too long'

        with raises(AssertionError) as exc:
            validate([1, 2])
        result = util.assert_message(exc)
        assert result == 'too long'

    def test_integer_fail(self):
        @types.integer
        def validate(value):
            assert value == 1, 'too big'

        with raises(AssertionError) as exc:
            validate(3)

        result = util.assert_message(exc)
        assert result == 'too big'
