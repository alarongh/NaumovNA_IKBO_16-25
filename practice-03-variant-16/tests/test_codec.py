"""Байтовые тесты из спецификации и проверки декодера."""

import unittest

from src.uvm.codec import decode_at, encode


class CodecTests(unittest.TestCase):
    def test_four_reference_sequences(self):
        cases = [
            (("load", 559), bytes.fromhex("81 17 01 00 00")),
            (("read", 565), bytes.fromhex("EE 1A 01")),
            (("store", 435), bytes.fromhex("8C D9 00")),
            (("popcnt", 942), bytes.fromhex("36 D7 01")),
        ]
        for command, expected in cases:
            with self.subTest(command=command):
                self.assertEqual(encode([command]), expected)
                decoded, offset = decode_at(expected, 0, len(expected))
                self.assertEqual(decoded, command)
                self.assertEqual(offset, len(expected))

    def test_bad_opcode_truncation_and_padding(self):
        for data in (b"\x00", b"\x01", b"\x01\x00\x00\x00\x80"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                decode_at(data, 0, len(data))
