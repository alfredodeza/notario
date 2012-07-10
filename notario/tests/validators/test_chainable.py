from pytest import raises
from notario.validators import chainable


class TestBasicChainValidator(object):


    def test_complains_when_args_are_not_callable(self):
        with raises(TypeError) as exc:
            chainable.BasicChainValidator("not a callable")
        assert exc.value.args[0] == "got a non-callable argument: 'not a callable'"

    def test_assigns_validators_if_all_are_callable(self):
        def foo(): pass
        def bar(): pass
        chain = chainable.BasicChainValidator(foo, bar)
        assert chain.args == (foo, bar)


class TestAllIn(object):

    def test_all_validators_pass(self):
        def foo(value): pass
        def bar(value): pass
        chain = chainable.AllIn(foo, bar)
        assert chain('some value') is None
