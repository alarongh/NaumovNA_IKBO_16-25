"""Точка входа графического эмулятора."""

import tkinter as tk

from emulator.gui import Terminal
from emulator.shell import Shell


def main():
    """Открыть окно и запустить цикл событий."""
    root = tk.Tk()
    Terminal(root, Shell(), "Учебная VFS")
    root.mainloop()


if __name__ == "__main__":
    main()
