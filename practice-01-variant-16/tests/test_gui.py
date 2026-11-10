"""Проверка ввода и вывода в настоящем окне Tk."""

import tkinter as tk
import unittest

from src.emulator.gui import Terminal
from src.emulator.shell import Shell


class TerminalTests(unittest.TestCase):
    def test_interactive_session(self):
        root = tk.Tk()
        self.addCleanup(self.close_window, root)
        terminal = Terminal(root, Shell(), "Учебная VFS")
        root.update()
        terminal.entry.focus_force()
        root.update()
        self.assertIn("Учебная VFS", root.title())
        for line in ("ls -l /home", "cd /home", "unknown", "exit extra", ""):
            terminal.entry.insert(0, line)
            terminal.entry.event_generate("<Return>")
            root.update()
        output = terminal.output.get("1.0", "end-1c")
        self.assertIn("$ ls -l /home\nls: ['-l', '/home']\n", output)
        self.assertIn("$ cd /home\ncd: ['/home']\n", output)
        self.assertIn("Ошибка: unknown: команда не найдена", output)
        self.assertIn("Ошибка: exit: команда не принимает аргументы", output)
        terminal.entry.insert(0, "exit")
        terminal.entry.event_generate("<Return>")
        self.assertTrue(terminal.shell.closed)
        with self.assertRaises(tk.TclError):
            root.winfo_exists()

    @staticmethod
    def close_window(root):
        """Закрыть окно при прерванном тесте."""
        try:
            root.destroy()
        except tk.TclError:
            pass
