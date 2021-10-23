import unittest


class TestEscape(unittest.TestCase):
    def test_escape(self):
        from kyofu.util import escape_for_like

        self.assertEqual('', escape_for_like(''))
        self.assertEqual('foo', escape_for_like('foo'))
        self.assertEqual('foo%', escape_for_like(r'foo\%'))
        self.assertEqual('foo_', escape_for_like(r'foo\_'))
        self.assertEqual('foo%%bar', escape_for_like(r'foo\%\%bar'))
        self.assertEqual('foo%_bar', escape_for_like(r'foo\%\%bar'))
        self.assertEqual('foo_%bar', escape_for_like(r'foo\_\_bar'))
        self.assertEqual('foo__bar', escape_for_like(r'foo\_\_bar'))


if __name__ == '__main__':
    unittest.main()
