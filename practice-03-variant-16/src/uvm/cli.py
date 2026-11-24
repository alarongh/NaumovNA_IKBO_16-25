"""Параметры ассемблера и интерпретатора."""

import argparse
from pathlib import Path
import sys

from .codec import encode
from .dump import memory_dump
from .files import write_result
from .format import parse_program
from .machine import Machine


def create_parser():
    """Описать две команды и их параметры."""
    parser = argparse.ArgumentParser(description="УВМ, вариант 16")
    commands = parser.add_subparsers(dest="command", required=True)
    assemble = commands.add_parser("assemble", help="JSON в машинный код")
    assemble.add_argument("--source", required=True, type=Path)
    assemble.add_argument("--output", required=True, type=Path)
    assemble.add_argument("--test", action="store_true")
    run = commands.add_parser("run", help="исполнение и XML-дамп")
    run.add_argument("--binary", required=True, type=Path)
    run.add_argument("--dump", required=True, type=Path)
    run.add_argument("--start", required=True, type=int)
    run.add_argument("--end", required=True, type=int)
    return parser


def assemble(args):
    """Записать команды и вывести байты в тестовом режиме."""
    program = parse_program(args.source)
    write_result(args.source, args.output, encode(program))
    print(f"Команд: {len(program)}")
    if args.test:
        for command in program:
            print(", ".join(f"0x{b:02X}" for b in encode([command])))


def execute(args):
    """Выполнить бинарную программу и сохранить выбранные слова."""
    machine = Machine(args.binary.read_bytes())
    memory_dump(machine, args.start, args.end)
    count = machine.run()
    data = memory_dump(machine, args.start, args.end)
    write_result(args.binary, args.dump, data)
    print(f"Выполнено команд: {count}")
    print(f"Дамп: {args.dump}")


def main(argv=None):
    """Запустить выбранный режим и вернуть код завершения."""
    args = create_parser().parse_args(argv)
    try:
        if args.command == "assemble":
            assemble(args)
        else:
            execute(args)
    except (OSError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0
