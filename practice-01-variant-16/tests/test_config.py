"""Проверка CLI и формата стартового файла."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.emulator.config import create_parser, read_startup


class ConfigTests(unittest.TestCase):
    def test_default_and_explicit_paths(self):
        parser = create_parser()
        defaults = parser.parse_args([])
        self.assertTrue(defaults.vfs.is_file())
        self.assertIsNone(defaults.startup)
        options = parser.parse_args([
            "--vfs", "my vfs.xml", "--startup", "startup.txt",
        ])
        self.assertEqual(options.vfs, Path("my vfs.xml"))
        self.assertEqual(options.startup, Path("startup.txt"))

    def test_startup_comments_and_bom(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "startup.txt"
            path.write_text(
                " # комментарий\n\nls /  # конец строки\ncd /a#b\nexit\n",
                encoding="utf-8-sig",
            )
            self.assertEqual(read_startup(path), ["ls /", "cd /a#b", "exit"])
