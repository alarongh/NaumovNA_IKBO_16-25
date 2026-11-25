"""Покрытие конструкций и вложенности грамматики."""

import unittest

from src.configlang.parser import parse


class ParserTests(unittest.TestCase):
    def test_all_structures(self):
        cases = [
            "1", "({})", "begin end",
            "({1, ({2}), begin inner := ({3}); end})",
            "var base 3; begin size := #[base + 1]; end",
            "begin var local 2; size := #[len(concat(({}),({1})))]; end",
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertEqual(parse(text).data, "start")

    def test_invalid_syntax(self):
        for text in ("", "0", "01", "-1", "begin a := 1 end",
                     "begin a1 := 2; end", "({1,})", "({1 2})",
                     "1 2", "// comment\n1", "var a 1 2", "beginx"):
            with self.subTest(text=text), self.assertRaisesRegex(
                ValueError, "строка",
            ):
                parse(text)
