from __future__ import annotations

import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGER_PATH = ROOT / "tools" / "package_release.py"
SPEC = importlib.util.spec_from_file_location("package_release", PACKAGER_PATH)
assert SPEC and SPEC.loader
package_release = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = package_release
SPEC.loader.exec_module(package_release)

REQUIRED_ROOT_FILES = {
    "SharedMedia_Nistaux/README.md",
    "SharedMedia_Nistaux/SharedMedia_Nistaux.lua",
    "SharedMedia_Nistaux/SharedMedia_Nistaux.toc",
}
ALLOWED_DIRECTORIES = {"border", "font", "statusbar"}


def git(
    root: Path,
    *arguments: str,
    input_bytes: bytes | None = None,
    env: dict[str, str] | None = None,
) -> bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        input=input_bytes,
        env=env,
    )
    return result.stdout


class PackageReleaseTests(unittest.TestCase):
    fixture: tempfile.TemporaryDirectory[str]
    repo: Path
    base_commit: str
    valid_tag: str
    counter = 0

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.fixture.name) / "repository"
        cls.repo.mkdir()

        for relative in package_release.ROOT_FILES:
            shutil.copy2(ROOT / relative, cls.repo / relative)
        for directory in package_release.MEDIA_DIRECTORIES:
            shutil.copytree(ROOT / directory, cls.repo / directory)

        git(cls.repo, "init", "--quiet")
        git(cls.repo, "config", "user.name", "Release Test")
        git(cls.repo, "config", "user.email", "release-test@example.invalid")
        git(cls.repo, "config", "core.autocrlf", "false")
        git(cls.repo, "add", "--all")
        git(cls.repo, "commit", "--quiet", "-m", "fixture")
        cls.base_commit = git(cls.repo, "rev-parse", "HEAD").decode("ascii").strip()
        cls.valid_tag = f"v26.7.31.{cls.base_commit[:7]}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.cleanup()

    @classmethod
    def commit_with_entry(
        cls,
        path: str,
        content: bytes,
        *,
        mode: str = "100644",
        parent: str | None = None,
    ) -> str:
        parent = parent or cls.base_commit
        cls.counter += 1
        index_path = Path(cls.fixture.name) / f"index-{cls.counter}"
        env = os.environ.copy()
        env["GIT_INDEX_FILE"] = str(index_path)
        git(cls.repo, "read-tree", parent, env=env)
        object_id = git(
            cls.repo,
            "hash-object",
            "-w",
            "--stdin",
            input_bytes=content,
        ).decode("ascii").strip()
        git(
            cls.repo,
            "update-index",
            "--add",
            "--cacheinfo",
            f"{mode},{object_id},{path}",
            env=env,
        )
        tree_id = git(cls.repo, "write-tree", env=env).decode("ascii").strip()
        commit_id = git(
            cls.repo,
            "commit-tree",
            tree_id,
            "-p",
            parent,
            "-m",
            "fixture mutation",
        ).decode("ascii").strip()
        index_path.unlink(missing_ok=True)
        return commit_id

    def build(
        self,
        output_dir: Path,
        *,
        tag: str | None = None,
        revision: str | None = None,
    ) -> Path:
        return package_release.build(
            tag or self.valid_tag,
            output_dir,
            root=self.repo,
            revision=revision or self.base_commit,
        )

    def test_archive_layout_version_and_exclusions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive_path = self.build(Path(temporary))
            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()
                tree_paths = git(
                    self.repo,
                    "ls-tree",
                    "-r",
                    "--name-only",
                    self.base_commit,
                ).decode("utf-8").splitlines()
                expected = set(REQUIRED_ROOT_FILES)
                expected.update(
                    f"SharedMedia_Nistaux/{path}"
                    for path in tree_paths
                    if Path(path).parts[0] in ALLOWED_DIRECTORIES
                )
                self.assertEqual(set(names), expected)
                self.assertEqual(len(names), len(set(names)))
                self.assertTrue(REQUIRED_ROOT_FILES.issubset(names))
                for name in names:
                    parts = Path(name).parts
                    self.assertEqual(parts[0], "SharedMedia_Nistaux")
                    if len(parts) > 2:
                        self.assertIn(parts[1], ALLOWED_DIRECTORIES)
                for excluded in ("background/", "sound/", "docs/", ".github/", "tools/", "tests/"):
                    self.assertFalse(any(excluded in name for name in names))
                self.assertNotIn("SharedMedia_Nistaux/AGENTS.md", names)

                version = self.valid_tag.removeprefix("v")
                toc = archive.read("SharedMedia_Nistaux/SharedMedia_Nistaux.toc").decode("utf-8")
                self.assertIn(f"## Version: {version}", toc.splitlines())
                self.assertNotIn("@project-version@", toc)

    def test_invalid_tags_are_rejected(self) -> None:
        invalid_tags = (
            "26.7.31.abcdef0",
            "v26.2.29.abcdef0",
            "v26.13.1.abcdef0",
            "v26.7.31.abc123",
            "v26.7.31.abcdef01",
            "v26.7.31.ABCDEF0",
            "v26.7.31.abc/def",
            "v2026.7.31.abcdef0",
            "v26.7.31.1234567a",
        )
        with tempfile.TemporaryDirectory() as temporary:
            for tag in invalid_tags:
                with self.subTest(tag=tag):
                    with self.assertRaises(package_release.PackageError):
                        self.build(Path(temporary), tag=tag)

    def test_commit_suffix_must_match_resolved_revision(self) -> None:
        mismatch = "0000000" if self.base_commit[:7] != "0000000" else "1111111"
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(package_release.PackageError, "does not match"):
                self.build(Path(temporary), tag=f"v26.7.31.{mismatch}")

    def test_seven_digit_suffix_is_a_verified_commit_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(package_release.PackageError, "does not match"):
                self.build(Path(temporary), tag="v26.7.31.1234567")

    def test_numeric_revision_tag_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive_path = self.build(Path(temporary), tag="v26.1.27.123456")
            self.assertTrue(archive_path.is_file())

    def test_repeat_builds_are_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_bytes = self.build(Path(first)).read_bytes()
            second_bytes = self.build(Path(second)).read_bytes()
            self.assertEqual(hashlib.sha256(first_bytes).digest(), hashlib.sha256(second_bytes).digest())
            self.assertEqual(first_bytes, second_bytes)

    def test_dirty_tracked_worktree_and_index_are_ignored(self) -> None:
        readme = self.repo / "README.md"
        committed = git(self.repo, "show", f"{self.base_commit}:README.md")
        try:
            readme.write_bytes(b"dirty staged content\n")
            git(self.repo, "add", "README.md")
            readme.write_bytes(b"dirty unstaged content\n")
            with tempfile.TemporaryDirectory() as temporary:
                archive_path = self.build(Path(temporary))
                with zipfile.ZipFile(archive_path) as archive:
                    packaged = archive.read("SharedMedia_Nistaux/README.md")
                self.assertEqual(packaged, committed)
                self.assertNotEqual(packaged, readme.read_bytes())
                staged = git(self.repo, "show", ":README.md")
                self.assertNotEqual(packaged, staged)
        finally:
            git(self.repo, "reset", "--hard", self.base_commit)

    def test_selected_git_symlink_mode_is_rejected(self) -> None:
        commit_id = self.commit_with_entry(
            "statusbar/linked.tga",
            b"ToxiUI-clean.tga",
            mode="120000",
        )
        tag = f"v26.7.31.{commit_id[:7]}"
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(package_release.PackageError, "mode=120000"):
                self.build(Path(temporary), tag=tag, revision=commit_id)

    def test_missing_toc_token_is_rejected(self) -> None:
        toc = git(self.repo, "show", f"{self.base_commit}:SharedMedia_Nistaux.toc")
        commit_id = self.commit_with_entry(
            "SharedMedia_Nistaux.toc",
            toc.replace(package_release.VERSION_TOKEN, b"development"),
        )
        tag = f"v26.7.31.{commit_id[:7]}"
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(package_release.PackageError, "found 0"):
                self.build(Path(temporary), tag=tag, revision=commit_id)

    def test_duplicate_toc_token_is_rejected(self) -> None:
        toc = git(self.repo, "show", f"{self.base_commit}:SharedMedia_Nistaux.toc")
        duplicate = toc + b"\n## Duplicate: " + package_release.VERSION_TOKEN + b"\n"
        commit_id = self.commit_with_entry("SharedMedia_Nistaux.toc", duplicate)
        tag = f"v26.7.31.{commit_id[:7]}"
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(package_release.PackageError, "found 2"):
                self.build(Path(temporary), tag=tag, revision=commit_id)

    def test_registration_outside_allowlist_is_rejected(self) -> None:
        lua = git(self.repo, "show", f"{self.base_commit}:SharedMedia_Nistaux.lua")
        lua += (
            b'\nLSM:Register("statusbar", "Missing", '
            b'[[Interface\\Addons\\SharedMedia_Nistaux\\background\\Missing.blp]])\n'
        )
        commit_id = self.commit_with_entry("SharedMedia_Nistaux.lua", lua)
        tag = f"v26.7.31.{commit_id[:7]}"
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(package_release.PackageError, "absent from the archive allowlist"):
                self.build(Path(temporary), tag=tag, revision=commit_id)

    def test_unresolvable_revision_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(package_release.PackageError, "does not resolve"):
                self.build(Path(temporary), revision="not-a-revision")


if __name__ == "__main__":
    unittest.main()
