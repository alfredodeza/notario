from pytest import raises
from notario import validate
from notario.exceptions import Invalid

class TestValidate(object):

    def test_most_simple_validation(self):
        data = {'a': 'a'}
        schema = (('a', 'b'))

        with raises(Invalid) as exc:
            validate(data, schema)

        assert exc.value.args[0] == '-> a -> a  did not match b'
        
