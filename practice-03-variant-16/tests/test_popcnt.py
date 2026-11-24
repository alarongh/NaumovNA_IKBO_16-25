"""Проверки операции popcnt и адреса результата."""

import unittest

from src.uvm.codec import encode
from src.uvm.machine import Machine


class PopcntTests(unittest.TestCase):
    def test_count_and_destination(self):
        machine = Machine(encode([("load", 2048), ("popcnt", 1024)]))
        machine.put_word(1024, 45)
        machine.run()
        self.assertEqual(machine.word(2048), 4)
        self.assertEqual(machine.word(1024), 45)
        self.assertEqual(machine.accumulator, 2048)

    def test_zero_full_word_and_in_place(self):
        for value, expected in ((0, 0), (0xFFFFFFFF, 32), (0x80000000, 1)):
            machine = Machine(encode([("load", 1024), ("popcnt", 1024)]))
            machine.put_word(1024, value)
            machine.run()
            self.assertEqual(machine.word(1024), expected)

    def test_destination_bounds(self):
        machine = Machine(encode([("load", 131071), ("popcnt", 1024)]))
        with self.assertRaises(ValueError):
            machine.run()
