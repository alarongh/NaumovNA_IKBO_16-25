"""Три вектора длины шесть и сохранение результата в исходные адреса."""

from pathlib import Path
import unittest
from xml.etree import ElementTree as ET

from src.uvm.codec import encode
from src.uvm.dump import memory_dump
from src.uvm.format import parse_program
from src.uvm.machine import Machine


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class VectorTests(unittest.TestCase):
    def test_three_xml_results(self):
        results = [
            [0, 1, 2, 3, 4, 5],
            [3, 4, 8, 1, 10, 16],
            [27, 1, 6, 6, 7, 6],
        ]
        for number, expected in enumerate(results, start=1):
            with self.subTest(number=number):
                source = EXAMPLES / f"vector-{number}.json"
                machine = Machine(encode(parse_program(source)))
                self.assertEqual(machine.run(), 24)
                root = ET.fromstring(memory_dump(machine, 1024, 1044))
                self.assertEqual([int(c.text) for c in root], expected)
                self.assertEqual([int(c.get("address")) for c in root],
                                 [1024, 1028, 1032, 1036, 1040, 1044])
