"""Параметры запуска и чтение стартового скрипта."""

import argparse
from pathlib import Path
import re


EXAMPLES = Path(__file__).resolve().parents[2] / "examples"


def create_parser():
    """Описать пути к VFS и стартовому скрипту."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки с GUI.")
    parser.add_argument(
        "--vfs", type=Path, default=EXAMPLES / "deep.xml",
        help="путь к XML-файлу виртуальной файловой системы",
    )
    parser.add_argument(
        "--startup", type=Path, help="путь к стартовому скрипту в UTF-8",
    )
    return parser


def read_startup(path):
    """Прочитать команды, пропуская пустые строки и комментарии с #."""
    commands = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        command = re.split(r"(?<!\S)#", line, maxsplit=1)[0].strip()
        if command:
            commands.append(command)
    return commands
