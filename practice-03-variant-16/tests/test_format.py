"""Проверки входного языка и полей спецификации."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.uvm.format import SPECS, parse_instruction, parse_program


class FormatTests(unittest.TestCase):
    def test_spec_fields(self):
        path = Path(__file__).resolve().parents[1] / "examples/spec.json"
        fields = [(SPECS[name][0], b) for name, b in parse_program(path)]
        self.assertEqual(fields, [(1, 559), (110, 565), (12, 435),
                                  (54, 942)])

    def test_invalid_instructions(self):
        cases = [None, {}, {"op": "bad", "b": 1},
                 {"op": "load", "b": True}, {"op": "read", "b": -1},
                 {"op": "read", "b": 131072},
                 {"op": "load", "b": 134217728}]
        for item in cases:
            with self.subTest(item=item), self.assertRaises(ValueError):
                parse_instruction(item, 1)

    def test_bad_json_structure(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "input.json"
            for text in ("{}", "[", '[{"op":"load","op":"read","b":0}]'):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    parse_program(path)
