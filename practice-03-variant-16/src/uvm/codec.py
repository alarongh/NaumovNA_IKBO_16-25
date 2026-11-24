"""Побайтовое кодирование и декодирование команд."""

from .format import OP_BITS, SPECS


OP_MASK = (1 << OP_BITS) - 1
BY_OPCODE = {spec[0]: (name, *spec[1:]) for name, spec in SPECS.items()}


def encode(program):
    """Собрать little-endian команды с нулевыми старшими битами."""
    result = bytearray()
    for name, operand in program:
        opcode, _, size = SPECS[name]
        value = opcode | (operand << OP_BITS)
        result.extend(value.to_bytes(size, "little"))
    return bytes(result)


def decode_at(memory, offset, end):
    """Прочитать команду из общей памяти в границах программы."""
    opcode = memory[offset] & OP_MASK
    if opcode not in BY_OPCODE:
        raise ValueError(f"адрес {offset}: неизвестный код {opcode}")
    name, bits, size = BY_OPCODE[opcode]
    following = offset + size
    if following > end:
        raise ValueError(f"адрес {offset}: неполная команда")
    value = int.from_bytes(memory[offset:following], "little")
    if value >> (OP_BITS + bits):
        raise ValueError(f"адрес {offset}: ненулевые резервные биты")
    return (name, value >> OP_BITS), following
