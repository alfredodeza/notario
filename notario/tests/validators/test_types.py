from pytest import raises
from notario.validators import types

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
