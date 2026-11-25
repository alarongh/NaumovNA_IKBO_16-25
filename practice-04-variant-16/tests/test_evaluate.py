"""Константы, области видимости, арифметика и функции."""

import unittest

from src.configlang.evaluate import evaluate


class EvaluateTests(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(evaluate("#[9 - 3 - 2 + 1]"), 5)
        self.assertEqual(evaluate("#[1 - (3 + 2)]"), -4)
        self.assertEqual(evaluate("#[1 - 1]"), 0)

    def test_functions(self):
        text = "var a ({1, ({2})}); #[concat(a, ({3}))]"
        self.assertEqual(evaluate(text), [1, [2], 3])
        self.assertEqual(evaluate("#[len(({}))]"), 0)
        self.assertEqual(evaluate("#[len(begin a := 2; end)]"), 1)
        self.assertEqual(evaluate("#[len(concat(({1}),({2}))) + 1]"), 3)

    def test_nested_scope(self):
        text = (
            "var a 1; begin x := begin var a 2; b := #[a]; end; "
            "y := #[a]; end"
        )
        self.assertEqual(evaluate(text), {"x": {"b": 2}, "y": 1})
        self.assertEqual(evaluate("begin A := 1; a := 2; end"),
                         {"A": 1, "a": 2})

    def test_semantic_errors(self):
        for text in ("#[missing]", "var a 1; var a 2; 1",
                     "var a #[a]; 1", "begin a := 1; a := 2; end",
                     "#[len(1)]", "#[concat(1,2)]", "#[({1}) + 1]",
                     "begin a := begin var x 1; end; b := #[x]; end"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                evaluate(text)
