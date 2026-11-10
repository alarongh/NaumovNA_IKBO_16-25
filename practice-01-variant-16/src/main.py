"""Точка входа графического эмулятора."""

import tkinter as tk

from emulator.config import create_parser, read_startup
from emulator.gui import Terminal
from emulator.shell import Shell
from emulator.vfs import Vfs, VfsError


def main(argv=None):
    """Прочитать настройки, открыть окно и запустить цикл событий."""
    parser = create_parser()
    options = parser.parse_args(argv)
    vfs_path = options.vfs.resolve()
    startup_path = options.startup.resolve() if options.startup else None
    try:
        lines = read_startup(startup_path) if startup_path else []
    except (OSError, UnicodeError) as error:
        parser.error(f"стартовый скрипт: {error}")
    try:
        vfs = Vfs.load(vfs_path)
    except VfsError as error:
        parser.error(f"VFS: {error}")
    settings = f"VFS = {vfs_path}\nСтартовый скрипт = {startup_path or 'нет'}"
    root = tk.Tk()
    terminal = Terminal(root, Shell(), vfs.name)
    terminal.write(settings)
    terminal.write(vfs.summary())
    root.after_idle(terminal.run_startup, lines)
    root.mainloop()


if __name__ == "__main__":
    main()
