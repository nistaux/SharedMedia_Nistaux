#!/usr/bin/env python3
"""Build and validate a deterministic, installable addon release archive."""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import re
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ADDON_NAME = "SharedMedia_Nistaux"
ROOT_FILES = ("README.md", "SharedMedia_Nistaux.lua", "SharedMedia_Nistaux.toc")
MEDIA_DIRECTORIES = ("border", "font", "statusbar")
VERSION_TOKEN = b"@project-version@"
TAG_PATTERN = re.compile(
    r"^v(?P<year>\d{2})\.(?P<month>\d{1,2})\.(?P<day>\d{1,2})\."
    r"(?P<suffix>[0-9a-f]+)$"
)
REGISTERED_PATH_PATTERN = re.compile(
    r"\[\[Interface\\Addons\\SharedMedia_Nistaux\\([^\]]+)\]\]"
)
REGULAR_MODES = {"100644", "100755"}
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


class PackageError(RuntimeError):
    """Raised when source or archive validation fails."""


@dataclasses.dataclass(frozen=True)
class ParsedTag:
    version: str
    suffix: str
    commit_suffix: bool


@dataclasses.dataclass(frozen=True)
class TreeEntry:
    mode: str
    object_type: str
    object_id: str
    path: str


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_git(root: Path, arguments: list[str], *, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        input=input_bytes,
    )
    return result.stdout


def parse_tag(tag: str) -> ParsedTag:
    match = TAG_PATTERN.fullmatch(tag)
    if not match:
        raise PackageError(
            "tag must match vYY.M.D.<suffix>; suffix must be either a 1-6 digit "
            "legacy revision or an exact 7-character lowercase hexadecimal commit ID"
        )

    year = 2000 + int(match.group("year"))
    month = int(match.group("month"))
    day = int(match.group("day"))
    try:
        dt.date(year, month, day)
    except ValueError as error:
        raise PackageError(f"tag contains an invalid calendar date: {error}") from error

    suffix = match.group("suffix")
    if len(suffix) == 7:
        commit_suffix = True
    elif 1 <= len(suffix) <= 6 and suffix.isdigit():
        commit_suffix = False
    else:
        raise PackageError(
            "tag suffix must be either a 1-6 digit legacy revision or an exact "
            "7-character lowercase hexadecimal commit ID"
        )

    return ParsedTag(tag[1:], suffix, commit_suffix)


def resolve_revision(root: Path, revision: str) -> str:
    if not revision or "\0" in revision or "\n" in revision or "\r" in revision:
        raise PackageError("revision must be a non-empty single-line Git revision")
    try:
        resolved = run_git(
            root,
            ["rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"],
        ).decode("ascii").strip()
    except subprocess.CalledProcessError as error:
        raise PackageError(f"revision does not resolve to a Git commit: {revision}") from error
    if not re.fullmatch(r"[0-9a-f]{40,64}", resolved):
        raise PackageError(f"Git returned an invalid commit ID for revision {revision}: {resolved}")
    return resolved


def validate_tag_commit(parsed: ParsedTag, commit_id: str) -> None:
    if parsed.commit_suffix and parsed.suffix != commit_id[:7]:
        raise PackageError(
            f"tag commit suffix {parsed.suffix} does not match packaged commit {commit_id[:7]}"
        )


def tree_entries(root: Path, commit_id: str) -> dict[str, TreeEntry]:
    output = run_git(root, ["ls-tree", "-r", "-z", "--full-tree", commit_id])
    entries: dict[str, TreeEntry] = {}
    for raw_record in output.split(b"\0"):
        if not raw_record:
            continue
        try:
            raw_metadata, raw_path = raw_record.split(b"\t", 1)
            raw_mode, raw_type, raw_id = raw_metadata.split(b" ", 2)
            entry = TreeEntry(
                raw_mode.decode("ascii"),
                raw_type.decode("ascii"),
                raw_id.decode("ascii"),
                raw_path.decode("utf-8"),
            )
        except (UnicodeDecodeError, ValueError) as error:
            raise PackageError("could not parse Git tree entry") from error
        if entry.path in entries:
            raise PackageError(f"Git tree contains a duplicate path: {entry.path}")
        entries[entry.path] = entry
    return entries


def is_allowlisted_path(path: str) -> bool:
    if path in ROOT_FILES:
        return True
    parts = PurePosixPath(path).parts
    return bool(parts and parts[0] in MEDIA_DIRECTORIES)


def selected_tree_entries(root: Path, commit_id: str) -> list[TreeEntry]:
    entries = tree_entries(root, commit_id)
    missing = sorted(set(ROOT_FILES) - entries.keys())
    if missing:
        raise PackageError(f"required files are absent from commit: {', '.join(missing)}")

    selected = sorted(
        (entry for entry in entries.values() if is_allowlisted_path(entry.path)),
        key=lambda entry: entry.path,
    )
    for entry in selected:
        if entry.object_type != "blob" or entry.mode not in REGULAR_MODES:
            raise PackageError(
                "release source must be a regular Git blob with mode 100644 or 100755: "
                f"{entry.path} (mode={entry.mode}, type={entry.object_type})"
            )
    return selected


def read_blob(root: Path, object_id: str) -> bytes:
    try:
        return run_git(root, ["cat-file", "blob", object_id])
    except subprocess.CalledProcessError as error:
        raise PackageError(f"could not read Git blob: {object_id}") from error


def archive_name(relative: str) -> str:
    return f"{ADDON_NAME}/{relative}"


def archive_bytes(root: Path, entry: TreeEntry, version: str) -> bytes:
    content = read_blob(root, entry.object_id)
    if entry.path == "SharedMedia_Nistaux.toc":
        token_count = content.count(VERSION_TOKEN)
        if token_count != 1:
            raise PackageError(
                "SharedMedia_Nistaux.toc must contain exactly one version token; "
                f"found {token_count}"
            )
        content = content.replace(VERSION_TOKEN, version.encode("ascii"))
    return content


def write_archive(
    root: Path,
    output: Path,
    selected: list[TreeEntry],
    version: str,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for entry in selected:
            info = zipfile.ZipInfo(archive_name(entry.path), FIXED_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(
                info,
                archive_bytes(root, entry, version),
                compresslevel=9,
            )


def validate_member_name(name: str) -> None:
    path = PurePosixPath(name)
    if (
        path.is_absolute()
        or ".." in path.parts
        or "\\" in name
        or not path.parts
        or path.parts[0] != ADDON_NAME
    ):
        raise PackageError(f"unsafe archive member: {name}")


def registered_media(lua_source: str) -> set[str]:
    return {
        match.replace("\\", "/")
        for match in REGISTERED_PATH_PATTERN.findall(lua_source)
    }


def validate_archive(output: Path, selected: list[TreeEntry], version: str) -> None:
    selected_paths = {entry.path for entry in selected}
    expected = {archive_name(relative) for relative in selected_paths}
    required = {archive_name(relative) for relative in ROOT_FILES}

    with zipfile.ZipFile(output, "r") as archive:
        members = archive.infolist()
        names = [member.filename for member in members]
        if len(names) != len(set(names)):
            raise PackageError("archive contains duplicate members")
        for member in members:
            validate_member_name(member.filename)
            mode = (member.external_attr >> 16) & 0o170000
            if mode == stat.S_IFLNK:
                raise PackageError(f"archive contains a symlink: {member.filename}")
        if set(names) != expected:
            missing = sorted(expected - set(names))
            extra = sorted(set(names) - expected)
            raise PackageError(f"archive allowlist mismatch; missing={missing}, extra={extra}")
        if not required.issubset(names):
            raise PackageError("archive is missing a required root file")

        toc = archive.read(archive_name("SharedMedia_Nistaux.toc"))
        if VERSION_TOKEN in toc:
            raise PackageError("archive TOC contains an unresolved version token")
        version_line = f"## Version: {version}".encode("ascii")
        if version_line not in toc.splitlines():
            raise PackageError("archive TOC version does not match the release tag")

        lua = archive.read(archive_name("SharedMedia_Nistaux.lua")).decode("utf-8")
        registrations = registered_media(lua)
        registration_calls = lua.count("LSM:Register(")
        if len(registrations) != registration_calls:
            raise PackageError(
                "could not resolve every unique LibSharedMedia registration to a literal addon path"
            )
        for relative in sorted(registrations):
            if relative not in selected_paths:
                raise PackageError(
                    f"registered media is absent from the archive allowlist: {relative}"
                )
            if archive_name(relative) not in names:
                raise PackageError(f"registered media is missing from the archive: {relative}")


def build(
    tag: str,
    output_dir: Path,
    *,
    root: Path | None = None,
    revision: str = "HEAD",
) -> Path:
    root = (root or repository_root()).resolve()
    parsed = parse_tag(tag)
    commit_id = resolve_revision(root, revision)
    validate_tag_commit(parsed, commit_id)
    selected = selected_tree_entries(root, commit_id)
    output = output_dir / f"{ADDON_NAME}-{parsed.version}.zip"
    write_archive(root, output, selected, parsed.version)
    validate_archive(output, selected, parsed.version)
    return output


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="release tag, for example v26.7.31.abcdef0")
    parser.add_argument(
        "--revision",
        default="HEAD",
        help="immutable Git commit to package (default: HEAD)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("dist"),
        help="archive output directory (default: dist)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        output = build(args.tag, args.output_dir, revision=args.revision)
    except (PackageError, OSError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
