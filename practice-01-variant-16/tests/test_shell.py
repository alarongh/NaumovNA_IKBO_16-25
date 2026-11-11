"""Проверка разбора, команд и перемещения по VFS."""

import unittest

from src.emulator.config import EXAMPLES
from src.emulator.shell import Shell, ShellError, parse_command
from src.emulator.vfs import Vfs


def make_shell():
    """Открыть независимый сеанс на учебном образе."""
    return Shell(Vfs.load(EXAMPLES / "deep.xml"))


class ShellTests(unittest.TestCase):
    def test_split_command(self):
        result = parse_command("  ls   -l  /home ")
        self.assertEqual(result, ("ls", ["-l", "/home"]))

    def test_empty_and_unknown_commands(self):
        shell = make_shell()
        self.assertEqual(shell.execute("   "), "")
        with self.assertRaisesRegex(ShellError, "команда не найдена"):
            shell.execute("unknown")

    def test_ls_options(self):
        shell = make_shell()
        self.assertEqual(shell.execute("ls"), "home\ntmp\nwelcome.txt")
        shell.execute("cd /home/student/docs")
        self.assertEqual(shell.execute("ls"), "bytes.bin\nreadme.txt")
        self.assertEqual(
            shell.execute("ls -a"), ".\n..\n.note\nbytes.bin\nreadme.txt",
        )
        self.assertIn("-rw-r--r-- student students 2 .note",
                      shell.execute("ls -al"))
        self.assertEqual(shell.execute("ls -- .note"), ".note")

    def test_cd_keeps_state_and_cannot_escape_root(self):
        shell = make_shell()
        shell.execute("cd /home/student")
        shell.execute("cd ./docs/../docs")
        self.assertEqual(shell.execute("pwd"), "/home/student/docs")
        with self.assertRaisesRegex(ShellError, "не каталог"):
            shell.execute("cd bytes.bin")
        with self.assertRaisesRegex(ShellError, "не каталог"):
            shell.execute("cd bytes.bin/..")
        self.assertEqual(shell.execute("pwd"), "/home/student/docs")
        shell.execute("cd ../../../../..")
        self.assertEqual(shell.execute("pwd"), "/")
        shell.execute("cd /tmp")
        shell.execute("cd")
        self.assertEqual(shell.execute("pwd"), "/")

    def test_du_and_uname(self):
        shell = make_shell()
        self.assertEqual(shell.execute("du -s /"), "20\t/")
        self.assertEqual(shell.execute("du /home"), (
            "10\t/home/student/docs\n17\t/home/student\n17\t/home"
        ))
        size = shell.execute("du -- /welcome.txt")
        self.assertEqual(size, "3\t/welcome.txt")
        self.assertEqual(shell.execute("uname"), "Linux")
        self.assertEqual(
            shell.execute("uname -a"), "Linux vfs 1.0 emulator",
        )

    def test_bad_options_and_paths(self):
        shell = make_shell()
        for line in ("ls /absent", "ls -x", "ls / /tmp", "pwd arg",
                     "uname -x", "du -a", "du /missing/../tmp"):
            with self.subTest(line=line), self.assertRaises(ShellError):
                shell.execute(line)

    def test_exit_with_and_without_arguments(self):
        shell = make_shell()
        with self.assertRaises(ShellError):
            shell.execute("exit extra")
        self.assertFalse(shell.closed)
        shell.execute("exit")
        self.assertTrue(shell.closed)
