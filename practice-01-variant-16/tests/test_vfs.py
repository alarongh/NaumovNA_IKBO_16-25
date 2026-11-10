"""Проверка загрузки XML и хранения данных в памяти."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.emulator.config import EXAMPLES
from src.emulator.vfs import Vfs, VfsError


class VfsTests(unittest.TestCase):
    def test_three_images(self):
        cases = [
            ("minimal.xml", "каталогов 1, файлов 0"),
            ("files.xml", "каталогов 1, файлов 3"),
            ("deep.xml", "каталогов 5, файлов 5"),
        ]
        for filename, expected in cases:
            with self.subTest(filename=filename):
                self.assertIn(expected, Vfs.load(EXAMPLES / filename).summary())

    def test_binary_and_text_files(self):
        root = Vfs.load(EXAMPLES / "files.xml").root
        self.assertEqual(root.children["hello.txt"].data, "Привет".encode())
        self.assertEqual(root.children["bytes.bin"].data, b"\x00\x01\xff")
        self.assertEqual(root.children["empty.txt"].data, b"")
        self.assertFalse(root.children["empty.txt"].is_directory)

    def test_invalid_images(self):
        cases = [
            "<missing",
            '<different name="VFS" />',
            '<vfs name="VFS"><dir name="." /></vfs>',
            '<vfs name="VFS"><file /></vfs>',
            '<vfs name="VFS"><dir name="x" /><file name="x" /></vfs>',
            '<vfs name="VFS"><file name="x" encoding="base64">?</file></vfs>',
        ]
        with TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.xml"
            for xml in cases:
                with self.subTest(xml=xml):
                    path.write_text(xml, encoding="utf-8")
                    with self.assertRaises(VfsError):
                        Vfs.load(path)
