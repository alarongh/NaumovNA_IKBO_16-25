"""Проверка ввода и вывода в настоящем окне Tk."""

import tkinter as tk
import unittest

from src.emulator.config import EXAMPLES
from src.emulator.gui import Terminal
from src.emulator.shell import Shell
from src.emulator.vfs import Vfs


class TerminalTests(unittest.TestCase):
    def test_interactive_session(self):
        root = tk.Tk()
        self.addCleanup(self.close_window, root)
        terminal = Terminal(root, Shell(Vfs.load(EXAMPLES / "deep.xml")), "Учебная VFS")
        root.update()
        terminal.entry.focus_force()
        root.update()
        self.assertIn("Учебная VFS", root.title())
        for line in ("ls -l /home", "cd /home", "unknown", "exit extra", ""):
            terminal.entry.insert(0, line)
            terminal.entry.event_generate("<Return>")
            root.update()
        output = terminal.output.get("1.0", "end-1c")
        self.assertIn("/ $ ls -l /home\ndrwxr-xr-x student students 0 student", output)
        self.assertIn("/ $ cd /home\n/home $ unknown", output)
        self.assertEqual(terminal.prompt.cget("text"), "/home $ ")
        self.assertIn("Ошибка: unknown: команда не найдена", output)
        self.assertIn("Ошибка: exit: команда не принимает аргументы", output)
        terminal.entry.insert(0, "exit")
        terminal.entry.event_generate("<Return>")
        self.assertTrue(terminal.shell.closed)
        with self.assertRaises(tk.TclError):
            root.winfo_exists()

    def test_startup_dialog_and_exit(self):
        root = tk.Tk()
        self.addCleanup(self.close_window, root)
        terminal = Terminal(root, Shell(Vfs.load(EXAMPLES / "deep.xml")), "Проверка")
        terminal.run_startup(["unknown", "ls /", "cd /"])
        output = terminal.output.get("1.0", "end-1c")
        self.assertIn("$ unknown\nОшибка:", output)
        self.assertIn("/ $ ls /\nhome\ntmp\nwelcome.txt\n/ $ cd /", output)
        terminal.run_startup(["exit", "ls"])
        self.assertTrue(terminal.shell.closed)

    @staticmethod
    def close_window(root):
        """Закрыть окно при прерванном тесте."""
        try:
            root.destroy()
        except tk.TclError:
            pass
