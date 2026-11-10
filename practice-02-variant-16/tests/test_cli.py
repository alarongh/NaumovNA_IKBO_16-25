"""Проверка опций и ошибок CLI."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.depgraph.cli import main
from src.depgraph.config import NUGET_INDEX, parse_args


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class ConfigurationTests(unittest.TestCase):
    def test_defaults(self):
        args = parse_args(["--package", "Newtonsoft.Json"])
        self.assertEqual(args.repository, NUGET_INDEX)
        self.assertEqual(args.output, Path("graph.svg"))
        self.assertFalse(args.test)
        self.assertFalse(args.ascii)

    def test_config_is_printed_as_key_value(self):
        output = StringIO()
        source = str(EXAMPLES / "diamond.json")
        with redirect_stdout(output):
            result = main([
                "--package", "A", "--test", "--repository", source,
                "--output", "diagram.svg", "--ascii",
            ])
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue().splitlines(), [
            "package=A", f"repository={source}", "test=True",
            "output=diagram.svg", "ascii=True",
        ])

    def test_each_option_reports_an_error(self):
        cases = [
            (["--package", "/bad"], "--package"),
            (["--repository", "ftp://example.net/feed"], "--repository"),
            (["--repository", "https://example.net:99999/"], "--repository"),
            (["--test=maybe"], "--test"),
            (["--test"], "--repository"),
            (["--output", "graph.png"], "--output"),
            (["--ascii=maybe"], "--ascii"),
        ]
        for flags, expected in cases:
            with self.subTest(flags=flags):
                argv = ["--package", "A", *flags]
                errors = StringIO()
                with redirect_stderr(errors), self.assertRaises(SystemExit):
                    parse_args(argv)
                self.assertIn(expected, errors.getvalue().splitlines()[-1])

    def test_rejects_output_that_overwrites_repository(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "input.dot"
            source.write_text('{"A": []}', encoding="utf-8")
            argv = [
                "--test", "--package", "A", "--repository", str(source),
                "--output", str(source.with_suffix(".svg")),
            ]
            with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
                parse_args(argv)
