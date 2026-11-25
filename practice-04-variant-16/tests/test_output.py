"""Проверка результата стандартным TOML-парсером и через CLI."""

import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import tomllib
import unittest

from src.configlang.evaluate import evaluate
from src.configlang.toml_output import render_document


ROOT = Path(__file__).resolve().parents[1]


class OutputTests(unittest.TestCase):
    def test_nested_values_roundtrip(self):
        cases = [
            "begin end", "({})", "1", "#[1-2]",
            "begin a := ({}); b := begin end; end",
            "({1,begin inner := ({2,begin end}); end,({3})})",
        ]
        for text in cases:
            value = evaluate(text)
            expected = value if isinstance(value, dict) else {"value": value}
            self.assertEqual(tomllib.loads(render_document(value)), expected)

    def test_int64_limits(self):
        self.assertEqual(tomllib.loads(render_document(2**63-1)),
                         {"value": 2**63-1})
        for value in (2**63, -(2**63)-1):
            with self.assertRaises(ValueError):
                render_document(value)

    def test_two_domains_and_cli(self):
        with TemporaryDirectory() as folder:
            target = Path(folder) / "config.toml"
            for name in ("server", "study"):
                data = (ROOT / f"examples/{name}.conf").read_bytes()
                result = subprocess.run(
                    [sys.executable, "-B", str(ROOT / "src/main.py"),
                     "--output", str(target)], input=data,
                    capture_output=True,
                    env={**os.environ, "PYTHONUTF8": "1"},
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                expected = evaluate(data.decode("utf-8"))
                self.assertEqual(tomllib.loads(target.read_text("utf-8")),
                                 expected)

    def test_cli_failure_preserves_output(self):
        with TemporaryDirectory() as folder:
            target = Path(folder) / "config.toml"
            target.write_bytes(b"previous")
            result = subprocess.run(
                [sys.executable, "-B", str(ROOT / "src/main.py"),
                 "--output", str(target)], input=b"begin broken end",
                capture_output=True,
                    env={**os.environ, "PYTHONUTF8": "1"},
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("строка", result.stderr.decode("utf-8"))
            self.assertEqual(target.read_bytes(), b"previous")
