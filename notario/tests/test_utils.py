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
