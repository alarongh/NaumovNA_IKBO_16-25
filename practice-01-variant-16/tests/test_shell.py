"""Проверка разбора и диспетчеризации команд."""

import unittest

from src.emulator.shell import Shell, ShellError, parse_command


class ShellTests(unittest.TestCase):
    def test_split_command(self):
        self.assertEqual(parse_command("  ls   -l  /home "), ("ls", ["-l", "/home"]))

    def test_empty_and_unknown_commands(self):
        shell = Shell()
        self.assertEqual(shell.execute("   "), "")
        with self.assertRaisesRegex(ShellError, "команда не найдена"):
            shell.execute("unknown")

    def test_stub_commands(self):
        shell = Shell()
        self.assertEqual(shell.execute("ls -l"), "ls: ['-l']")
        self.assertEqual(shell.execute("cd"), "cd: []")

    def test_exit_with_and_without_arguments(self):
        shell = Shell()
        with self.assertRaises(ShellError):
            shell.execute("exit extra")
        self.assertFalse(shell.closed)
        shell.execute("exit")
        self.assertTrue(shell.closed)
