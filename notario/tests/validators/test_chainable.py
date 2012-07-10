from pytest import raises
from notario.validators import chainable


class TestBasicChainValidator(object):


    def test_complains_when_args_are_not_callable(self):
        with raises(TypeError) as exc:
            chainable.BasicChainValidator("not a callable")
        assert exc.value.args[0] == "got a non-callable argument: 'not a callable'"
