"""Исполнение команд, общая память и проверка копирования."""

from pathlib import Path
import unittest

from src.uvm.codec import encode
from src.uvm.dump import memory_dump
from src.uvm.format import parse_program
from src.uvm.machine import MEMORY_SIZE, Machine


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class MachineTests(unittest.TestCase):
    def test_copy_array(self):
        machine = Machine(encode(parse_program(EXAMPLES / "copy.json")))
        self.assertEqual(machine.run(), 12)
        for index, expected in enumerate((7, 11, 19)):
            self.assertEqual(machine.word(1024 + index * 4), expected)
            self.assertEqual(machine.word(2048 + index * 4), expected)

    def test_commands_and_data_share_memory(self):
        program = [("load", 0), ("store", 0)]
        machine = Machine(encode(program))
        machine.run()
        self.assertEqual(machine.word(0), 0)

    def test_bad_addresses_and_dump_ranges(self):
        machine = Machine(b"")
        for start, end in ((-1, 0), (0, MEMORY_SIZE), (4, 0), (0, 3)):
            with self.subTest(start=start), self.assertRaises(ValueError):
                memory_dump(machine, start, end)

    def test_empty_program_and_bad_binary(self):
        self.assertEqual(Machine(b"").run(), 0)
        for binary in (b"\x00", b"\x01"):
            with self.subTest(binary=binary), self.assertRaises(ValueError):
                Machine(binary).run()
