"""Проверки CLI и сохранности входных файлов."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.uvm.cli import main


class CliTests(unittest.TestCase):
    def test_input_cannot_be_overwritten(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / "source.json"
            text = '[{"op":"load","b":1}]'
            source.write_text(text, encoding="utf-8")
            with redirect_stderr(StringIO()):
                status = main(["assemble", "--source", str(source),
                               "--output", str(source)])
            self.assertEqual(status, 1)
            self.assertEqual(source.read_text(encoding="utf-8"), text)

    def test_execution_failure_preserves_dump(self):
        with TemporaryDirectory() as folder:
            binary = Path(folder) / "program.bin"
            binary.write_bytes(b"\x00")
            dump = Path(folder) / "memory.xml"
            dump.write_bytes(b"old dump")
            with redirect_stderr(StringIO()):
                status = main(["run", "--binary", str(binary),
                               "--dump", str(dump), "--start", "0",
                               "--end", "0"])
            self.assertEqual(status, 1)
            self.assertEqual(dump.read_bytes(), b"old dump")

    def test_missing_required_option(self):
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            main(["run"])

    def test_assembly_test_mode_prints_reference_bytes(self):
        examples = Path(__file__).resolve().parents[1] / "examples"
        with TemporaryDirectory() as folder:
            target = Path(folder) / "spec.bin"
            out = StringIO()
            with redirect_stdout(out):
                status = main(["assemble", "--source",
                               str(examples / "spec.json"), "--output",
                               str(target), "--test"])
            self.assertEqual(status, 0)
            self.assertEqual(len(target.read_bytes()), 14)
            self.assertIn("0x81, 0x17, 0x01, 0x00, 0x00", out.getvalue())
