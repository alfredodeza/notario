from notario import utils


class TestIsCallable(object):

    def setup(self):
        def fake_callable(): pass
        self.fake_callable = fake_callable

    def test_is_callable(self):
        result = utils.is_callable(self.fake_callable)
        assert result is True

    def test_is_not_callable(self):
        result = utils.is_callable(1)
        assert result is False


class TestOptionalDecorator(object):

    def fake_validator(self, value):
        return True

    def test_has_no_value(self):
        result = utils.optional(self.fake_validator)('')
        assert result is None

    def test_value(self):
        result = utils.optional(self.fake_validator)('some value!')
        assert result is True

    def test_decorator_is_marked_as_optional(self):
        result = utils.optional('')
        assert result.is_optional is True

    def test_value_has_string(self):
        result = utils.optional('value')
        assert result() == 'value'
