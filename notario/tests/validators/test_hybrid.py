from pytest import raises
from notario.validators import Hybrid
from notario.exceptions import Invalid
from notario import validate


class TestHybrid(object):

    def setup(self):
        def validator(x): assert x
        self.validator = validator

    def test_use_validator_passes(self):
        schema = ()
        hybrid = Hybrid(self.validator, schema)
        assert hybrid(1) is None

    def test_use_validator_fails(self):
        schema = ()
        hybrid = Hybrid(self.validator, schema)
        with raises(AssertionError):
            hybrid(0)

    def test_use_schema_passes(self):
        schema = ('a', 1)
        hybrid = Hybrid(self.validator, schema)
        hybrid({0: ('a', 1)})

    def test_use_schema_fails(self):
        schema = ('a', 2)
        hybrid = Hybrid(self.validator, schema)
        with raises(Invalid) as exc:
            hybrid({0: ('a', 1)})
        error = exc.value.args[0]
        assert 'a -> 1  did not match 2' in error


class TestFunctional(object):

    def setup(self):
        def validator(x): assert x
        self.validator = validator

    def test_passes_single_value(self):
        sschema = (1, 2)
        schema = ('a', Hybrid(self.validator, sschema))
        data = {'a': 2}
        assert validate(data, schema) is None

    def test_passes_object(self):
        sschema = (1, 2)
        schema = ('a', Hybrid(self.validator, sschema))
        data = {'a': {1: 2}}
        assert validate(data, schema) is None

    def test_fail_object(self):
        sschema = (1, 1)
        schema = ('a', Hybrid(self.validator, sschema))
        data = {'a': {1: 2}}
        with raises(Invalid) as exc:
            validate(data, schema)
        error = exc.value.args[0]
        assert '1 -> 2  did not match 1' in error
        assert error.startswith('-> a -> 1')
