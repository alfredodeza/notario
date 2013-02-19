from py.test import raises
from notario import regex


class TestLinker(object):

    def test_do_not_accept_non_pairs(self):
        with raises(TypeError):
            regex.Linker([('a',)], True)

    def test_build_itself_with_same_amount_of_regexes(self):
        rx = regex.Linker([('a', 'some reason'), ('b', 'other reason')], True)
        assert len(rx) == 2

    def test_assertion_error_for_failure(self):
        rx = regex.Linker([(r"\d+", "not a digit")])
        with raises(AssertionError):
            rx('f')

    def test_assertion_error_has_message(self):
        rx = regex.Linker([(r"\w+$", "does not begin with a word")])
        with raises(AssertionError) as exc:
            rx('_*')
        error = exc.value.args[0]
        assert error == 'does not begin with a word'


class TestLinkerSequentially(object):

    def setup(self):
        self.rxs = [(r"^\w+", "begin with a word"),
                    (r"-", "follow a dash"),
                    (r"_$", "end with an underscore")]

    def test_fail_on_first_regex(self):
        rx = regex.Linker(self.rxs)
        with raises(AssertionError) as exc:
            rx(' ')
        error = exc.value.args[0]
        assert error == 'begin with a word'

    def test_fail_on_second_regex(self):
        rx = regex.Linker(self.rxs)
        with raises(AssertionError) as exc:
            rx('f ')
        error = exc.value.args[0]
        assert error == 'follow a dash'

    def test_fail_on_last_regex(self):
        rx = regex.Linker(self.rxs)
        with raises(AssertionError) as exc:
            rx('d- ')
        error = exc.value.args[0]
        assert error == 'end with an underscore'

    def test_fail_on_first_regex_with_prepending(self):
        rx = regex.Linker(self.rxs, True)
        with raises(AssertionError) as exc:
            rx(' ')
        error = exc.value.args[0]
        assert error == 'does not begin with a word'


class TestChain(object):

    def test_prepend_with_multi_regex(self):
        rx = regex.chain((r'^\w+', 'start with a word'),
                         (r'\s+$', 'end with whitespace'))
        with raises(AssertionError) as exc:
            rx('w')
        error = exc.value.args[0]
        assert error == 'does not end with whitespace'

    def test_dont_prepend_with_multi_regex(self):
        rx = regex.chain((r'^\w+', 'start with a word'),
                         (r'\s+$', 'end with whitespace'),
                         prepend_negation=False)
        with raises(AssertionError) as exc:
            rx('w')
        error = exc.value.args[0]
        assert error == 'end with whitespace'

