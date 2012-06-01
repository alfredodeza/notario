from notario import utils

def fake_callable():
    pass

class TestIsCallable(object):

    def test_is_callable(self):
        result = utils.is_callable(fake_callable)
        assert result is True

    def test_is_not_callable(self):
        result = utils.is_callable(1)
        assert result is False
