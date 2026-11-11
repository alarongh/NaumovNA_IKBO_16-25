"""Проверка команд, изменяющих метаданные VFS."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.emulator.config import EXAMPLES
from src.emulator.shell import Shell, ShellError
from src.emulator.vfs import Vfs


def make_shell_in_docs():
    """Создать сеанс в каталоге с файлами для проверки прав."""
    shell = Shell(Vfs.load(EXAMPLES / "deep.xml"))
    shell.execute("cd /home/student/docs")
    return shell


class PermissionTests(unittest.TestCase):
    def test_chmod_numeric_and_symbolic(self):
        shell = make_shell_in_docs()
        shell.execute("chmod 600 readme.txt")
        self.assertIn("-rw------- ", shell.execute("ls -l readme.txt"))
        shell.execute("chmod u+x,g+r,o= readme.txt")
        self.assertIn("-rwxr----- ", shell.execute("ls -l readme.txt"))
        shell.execute("chmod a-w readme.txt")
        self.assertIn("-r-xr----- ", shell.execute("ls -l readme.txt"))
        shell.execute("chmod +x readme.txt bytes.bin")
        self.assertIn("-r-xr-x--x ", shell.execute("ls -l readme.txt"))
        self.assertIn("-rwxr-xr-x ", shell.execute("ls -l bytes.bin"))
        shell.execute("chmod 1750 /tmp")
        self.assertIn(
            "drwxr-x--T student students 0 tmp", shell.execute("ls -l /"),
        )

    def test_chown_owner_group_and_both(self):
        shell = make_shell_in_docs()
        shell.execute("chown alice readme.txt")
        self.assertIn("alice students", shell.execute("ls -l readme.txt"))
        shell.execute("chown :staff readme.txt")
        self.assertIn("alice staff", shell.execute("ls -l readme.txt"))
        shell.execute("chown bob:team /tmp readme.txt")
        self.assertIn("bob team", shell.execute("ls -l readme.txt"))
        self.assertIn("bob team 0 tmp", shell.execute("ls -l /"))

    def test_failed_changes_leave_all_paths_unchanged(self):
        shell = make_shell_in_docs()
        before = shell.execute("ls -l")
        cases = (
            "chmod 777 readme.txt absent", "chmod 999 readme.txt",
            "chmod u+ readme.txt", "chmod 644", "chmod",
            "chown bob:team readme.txt absent", "chown : readme.txt",
            "chown invalid:name:again readme.txt", "chown bob: readme.txt",
            "chown bob", "chown",
        )
        for line in cases:
            with self.subTest(line=line):
                with self.assertRaises(ShellError):
                    shell.execute(line)
                self.assertEqual(shell.execute("ls -l"), before)

    def test_edits_do_not_rewrite_image(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "image.xml"
            original = (EXAMPLES / "files.xml").read_bytes()
            path.write_bytes(original)
            shell = Shell(Vfs.load(path))
            shell.execute("chmod 700 hello.txt")
            shell.execute("chown alice:staff hello.txt")
            self.assertIn("alice staff", shell.execute("ls -l hello.txt"))
            self.assertEqual(path.read_bytes(), original)
            restored = Shell(Vfs.load(path))
            expected = "-rw-r--r-- student students 12 hello.txt"
            self.assertEqual(restored.execute("ls -l hello.txt"), expected)
