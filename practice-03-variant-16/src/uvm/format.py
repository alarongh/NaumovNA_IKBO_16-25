"""Описание команд и разбор языка JSON."""

import json
from pathlib import Path


OP_BITS = 7
CONST_BITS = 27
ADDRESS_BITS = 17
SPECS = {
    "load": (1, CONST_BITS, 5),
    "read": (110, ADDRESS_BITS, 3),
    "store": (12, ADDRESS_BITS, 3),
    "popcnt": (54, ADDRESS_BITS, 3),
}


def unique_fields(pairs):
    """Отклонить повторяющиеся ключи JSON."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"повторяющийся ключ: {key}")
        result[key] = value
    return result


def parse_program(path):
    """Преобразовать JSON-массив в список пар имени команды и B."""
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=unique_fields)
    if not isinstance(data, list):
        raise ValueError("программа должна быть массивом JSON")
    return [parse_instruction(item, index)
            for index, item in enumerate(data, start=1)]


def parse_instruction(item, index):
    """Проверить команду и допустимый диапазон операнда."""
    if not isinstance(item, dict) or set(item) != {"op", "b"}:
        raise ValueError(f"команда {index}: нужны ровно поля op и b")
    name, operand = item["op"], item["b"]
    if not isinstance(name, str) or name not in SPECS:
        raise ValueError(f"команда {index}: неизвестная операция")
    bits = SPECS[name][1]
    if type(operand) is not int or not 0 <= operand < (1 << bits):
        raise ValueError(f"команда {index}: B вне диапазона {bits} бит")
    return name, operand
