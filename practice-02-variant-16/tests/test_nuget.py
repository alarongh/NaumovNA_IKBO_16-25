"""Проверки формата NuGet на небольших HTTP-ответах."""

import json
import unittest
from unittest.mock import patch

from src.depgraph.model import Dependency, DependencyError, Package
from src.depgraph.nuget import NugetRepository
from src.depgraph.nuspec import read_dependencies
from src.depgraph.versions import Requirement, version_key


INDEX = "https://example.net/v3/index.json"
BASE = "https://files.example.net/flat"


class NugetTests(unittest.TestCase):
    def test_service_index_and_direct_dependencies(self):
        replies = {
            INDEX: json.dumps({"resources": [
                {"@type": "Other", "@id": INDEX},
                {"@type": "PackageBaseAddress/3.0.0", "@id": BASE + "/"},
            ]}).encode(),
            f"{BASE}/pkg/index.json": b'{"versions":["9.0", "10.0", "11-beta"]}',
            f"{BASE}/pkg/10.0/pkg.nuspec": (
                b'<package xmlns="urn:test"><metadata><dependencies>'
                b'<group targetFramework=".NETStandard2.0">'
                b'<dependency id="Older" version="1.0"/></group>'
                b'<group targetFramework="net10.0">'
                b'<dependency id="Direct" version="[1.0,2.0)"/></group>'
                b'<group targetFramework="net11.0"/></dependencies>'
                b'</metadata></package>'
            ),
        }
        with patch("src.depgraph.nuget.read_url", side_effect=replies.get):
            repo = NugetRepository(INDEX)
            root = repo.root("Pkg")
            self.assertEqual(str(root), "pkg 10.0")
            self.assertEqual(repo.manifest(root), (
                Dependency("direct", "[1.0,2.0)"),
            ))

    def test_empty_compatible_group_takes_precedence(self):
        content = b"""
            <package><metadata><dependencies>
              <group targetFramework=".NETStandard2.0">
                <dependency id="Old" />
              </group>
              <group targetFramework="net8.0" />
            </dependencies></metadata></package>
        """
        self.assertEqual(read_dependencies(content), ())

    def test_bad_manifest_and_unsupported_framework(self):
        unsupported = b"""
            <package><metadata><dependencies>
              <group targetFramework=".NETFramework4.8" />
            </dependencies></metadata></package>
        """
        for content in (b"<bad", b"<package />", unsupported):
            with self.subTest(content=content):
                with self.assertRaises(DependencyError):
                    read_dependencies(content)

    def test_inclusive_exclusive_and_exact_bounds(self):
        interval = Requirement.parse("[1.2, 2)")
        self.assertTrue(interval.accepts(version_key("1.2")))
        self.assertFalse(interval.accepts(version_key("2.0.0")))
        self.assertTrue(Requirement.parse("[1]").accepts(version_key("1.0.0")))
        self.assertFalse(Requirement.parse("(1,)").accepts(version_key("1")))
        self.assertTrue(Requirement.parse("(, 2]").accepts(version_key("2")))

    def test_version_sorting_and_prerelease(self):
        values = ["2", "1.0-beta.10", "1", "1.0-beta.2"]
        expected = ["1.0-beta.2", "1.0-beta.10", "1", "2"]
        self.assertEqual(sorted(values, key=version_key), expected)
        self.assertTrue(Requirement.parse("[1.0-beta.2,2)").allows_prerelease)
        with self.assertRaises(DependencyError):
            Requirement.parse("(1.0)")

    def test_resolve_uses_lowest_satisfying_version(self):
        with patch("src.depgraph.nuget.find_base", return_value=BASE):
            repo = NugetRepository(INDEX)
        repo.version_lists["pkg"] = ("1.0-beta", "1.0", "1.4", "2.0")
        self.assertEqual(repo.resolve(Dependency("pkg", "(1.0,2)")),
                         Package("pkg", "1.4"))
        self.assertEqual(repo.resolve(Dependency("pkg", "[1.0-beta]")),
                         Package("pkg", "1.0-beta"))
        with self.assertRaises(DependencyError):
            repo.resolve(Dependency("pkg", "[3,4)"))
