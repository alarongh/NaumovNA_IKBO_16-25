"""Общая байтовая память программы и данных."""

from .codec import decode_at
from .format import ADDRESS_BITS


MEMORY_SIZE = 1 << ADDRESS_BITS
WORD_BYTES = 4


class Machine:
    """Последовательная УВМ с аккумулятором и счётчиком команд."""

    def __init__(self, binary):
        if len(binary) > MEMORY_SIZE:
            raise ValueError("программа не помещается в память")
        self.memory = bytearray(MEMORY_SIZE)
        self.memory[:len(binary)] = binary
        self.end = len(binary)
        self.pc = 0
        self.accumulator = 0
        self.operations = {
            "load": self.load, "read": self.read, "store": self.store,
        }

    def check_address(self, address):
        """Проверить, что слово целиком помещается в памяти."""
        if not 0 <= address <= MEMORY_SIZE - WORD_BYTES:
            raise ValueError(f"слово по адресу {address} выходит за память")

    def word(self, address):
        """Прочитать беззнаковое слово little-endian."""
        self.check_address(address)
        data = self.memory[address:address + WORD_BYTES]
        return int.from_bytes(data, "little")

    def put_word(self, address, value):
        """Записать слово в общую память."""
        self.check_address(address)
        self.memory[address:address + WORD_BYTES] = value.to_bytes(
            WORD_BYTES, "little",
        )

    def load(self, operand):
        """Загрузить поле B в аккумулятор."""
        self.accumulator = operand

    def read(self, operand):
        """Загрузить слово из памяти в аккумулятор."""
        self.accumulator = self.word(operand)

    def store(self, operand):
        """Записать аккумулятор в память по адресу B."""
        self.put_word(operand, self.accumulator)

    def run(self):
        """Выполнять команды до конца исходной программы."""
        count = 0
        while self.pc < self.end:
            (name, operand), following = decode_at(
                self.memory, self.pc, self.end,
            )
            if name not in self.operations:
                raise ValueError(f"операция {name} ещё не реализована")
            self.operations[name](operand)
            self.pc = following
            count += 1
        return count
