"""Проверка ввода и вывода в настоящем окне Tk."""

import tkinter as tk
import unittest
from unittest.mock import patch

from src.emulator.config import EXAMPLES, read_startup
from src.emulator.gui import Terminal
from src.emulator.shell import Shell
from src.emulator.vfs import Vfs


class TerminalTests(unittest.TestCase):
    def test_interactive_session(self):
        root = tk.Tk()
        self.addCleanup(self.close_window, root)
        vfs = Vfs.load(EXAMPLES / "deep.xml")
        terminal = Terminal(root, Shell(vfs), vfs.name)
        root.update()
        terminal.entry.focus_force()
        root.update()
        self.assertIn("Учебная VFS", root.title())
        for line in ("ls -l /home", "cd /home", "unknown", "exit extra", ""):
            terminal.entry.insert(0, line)
            terminal.entry.event_generate("<Return>")
            root.update()
        output = terminal.output.get("1.0", "end-1c")
        self.assertIn(
            "/ $ ls -l /home\ndrwxr-xr-x student students 0 student", output,
        )
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
        vfs = Vfs.load(EXAMPLES / "deep.xml")
        terminal = Terminal(root, Shell(vfs), vfs.name)
        terminal.run_startup(["unknown", "ls /", "cd /"])
        output = terminal.output.get("1.0", "end-1c")
        self.assertIn("$ unknown\nОшибка:", output)
        self.assertIn("/ $ ls /\nhome\ntmp\nwelcome.txt\n/ $ cd /", output)
        terminal.run_startup(["exit", "ls"])
        self.assertTrue(terminal.shell.closed)

    def test_complete_stage_three_startup(self):
        root = tk.Tk()
        self.addCleanup(self.close_window, root)
        vfs = Vfs.load(EXAMPLES / "deep.xml")
        terminal = Terminal(root, Shell(vfs), vfs.name)
        lines = read_startup(EXAMPLES / "stage-3-complete.txt")
        with patch.object(terminal, "write", wraps=terminal.write) as write:
            terminal.run_startup(lines)
        dialog = [call.args[0] for call in write.call_args_list]
        self.assertIn("/ $ ls -l /", dialog)
        self.assertIn("/ $ cd", dialog)
        self.assertIn("Ошибка: unknown: команда не найдена", dialog)
        self.assertIn("Ошибка: exit: команда не принимает аргументы", dialog)
        self.assertEqual(dialog[-1], "/ $ exit")
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
