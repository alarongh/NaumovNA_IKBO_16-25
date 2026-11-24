"""XML-дамп слов общей памяти."""

from xml.etree import ElementTree as ET

from .machine import WORD_BYTES


def memory_dump(machine, start, end):
    """Вывести слова с шагом 4, включая обе границы диапазона."""
    machine.check_address(start)
    machine.check_address(end)
    if start > end or (end - start) % WORD_BYTES:
        raise ValueError("диапазон должен задавать целое число слов")
    root = ET.Element("memory", start=str(start), end=str(end),
                      word_bytes=str(WORD_BYTES))
    for address in range(start, end + 1, WORD_BYTES):
        cell = ET.SubElement(root, "cell", address=str(address))
        cell.text = str(machine.word(address))
    ET.indent(root)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)
