"""CLI ассемблера."""

import argparse
import sys

from uvm.format import SPECS, parse_program


def main():
    """Проверить программу и показать промежуточные поля."""
    parser = argparse.ArgumentParser(description="Ассемблер УВМ")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    try:
        program = parse_program(args.source)
        if args.test:
            for name, operand in program:
                print(f"A={SPECS[name][0]}, B={operand}")
    except (OSError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
