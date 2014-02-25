from pytest import raises

from notario.assertions import ensure


def test_ensure():
    assert ensure(1 == 1)


def test_ensure_raises_assertionerror():
    with raises(AssertionError):
        ensure(0 == 1)
