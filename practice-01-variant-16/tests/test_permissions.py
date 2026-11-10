"""Проверка команд, изменяющих метаданные VFS."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.emulator.config import EXAMPLES
from src.emulator.shell import Shell, ShellError
from src.emulator.vfs import Vfs


class PermissionTests(unittest.TestCase):
    def setUp(self):
        self.shell = Shell(Vfs.load(EXAMPLES / "deep.xml"))
        self.shell.execute("cd /home/student/docs")

    def test_chmod_numeric_and_symbolic(self):
        self.shell.execute("chmod 600 readme.txt")
        self.assertIn("-rw------- ", self.shell.execute("ls -l readme.txt"))
        self.shell.execute("chmod u+x,g+r,o= readme.txt")
        self.assertIn("-rwxr----- ", self.shell.execute("ls -l readme.txt"))
        self.shell.execute("chmod a-w readme.txt")
        self.assertIn("-r-xr----- ", self.shell.execute("ls -l readme.txt"))
        self.shell.execute("chmod +x readme.txt bytes.bin")
        self.assertIn("-r-xr-x--x ", self.shell.execute("ls -l readme.txt"))
        self.assertIn("-rwxr-xr-x ", self.shell.execute("ls -l bytes.bin"))
        self.shell.execute("chmod 1750 /tmp")
        self.assertIn(
            "drwxr-x--T student students 0 tmp", self.shell.execute("ls -l /"),
        )

    def test_chown_owner_group_and_both(self):
        self.shell.execute("chown alice readme.txt")
        self.assertIn("alice students", self.shell.execute("ls -l readme.txt"))
        self.shell.execute("chown :staff readme.txt")
        self.assertIn("alice staff", self.shell.execute("ls -l readme.txt"))
        self.shell.execute("chown bob:team /tmp readme.txt")
        self.assertIn("bob team", self.shell.execute("ls -l readme.txt"))
        self.assertIn("bob team 0 tmp", self.shell.execute("ls -l /"))

    def test_failed_changes_leave_all_paths_unchanged(self):
        before = self.shell.execute("ls -l")
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
                    self.shell.execute(line)
                self.assertEqual(self.shell.execute("ls -l"), before)

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
