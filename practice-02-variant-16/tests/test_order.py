"""Порядок зависимостей на ациклическом и циклическом графах."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import unittest

from src.depgraph.cli import main


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class OrderTests(unittest.TestCase):
    def run_order(self, package, filename):
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = main([
                "--package", package, "--test", "--order",
                "--repository", str(EXAMPLES / filename),
            ])
        return status, out.getvalue().strip(), err.getvalue().strip()

    def test_diamond_and_isolated(self):
        self.assertEqual(self.run_order("A", "diamond.json"),
                         (0, "D -> B -> C -> A", ""))
        self.assertEqual(self.run_order("X", "isolated.json"), (0, "X", ""))

    def test_cycle_has_no_load_order(self):
        status, out, err = self.run_order("A", "cycle.json")
        self.assertEqual(status, 1)
        self.assertEqual(out, "")
        self.assertIn("B -> C -> B", err)
