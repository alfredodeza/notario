from notario import validators


class TestCherryPick(object):

    def test_single_pair_tuple(self):
        result = validators.cherry_pick(('a', 'b'))
        assert result.must_validate == ('a',)

    def test_single_items_tuples(self):
        result = validators.cherry_pick(('a', 'b', 'c', 'd'))
        assert result.must_validate == ()

    def test_empty_tuple(self):
        result = validators.cherry_pick(())
        assert result.must_validate == ()
