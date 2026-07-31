# SharedMedia_Nistaux project guide

_Last reviewed: 2026-07-31_

## Start here

`SharedMedia_Nistaux` is a small personal World of Warcraft media pack. It registers selected fonts, status-bar textures, and a border with `LibSharedMedia-3.0`, allowing any compatible addon to discover them.

For a new task:

1. Read `SharedMedia_Nistaux.toc` to confirm metadata, dependencies, and load order.
2. Read `SharedMedia_Nistaux.lua`; it is the entire runtime implementation.
3. Determine whether the requested asset is registered or merely packaged.
4. Check [GitHub Issues](https://github.com/nistaux/SharedMedia_Nistaux/issues) for known work.
5. Preserve the installed folder name and existing LibSharedMedia display names unless the task explicitly requires changing them.

## Repository map

| Path | Purpose |
| --- | --- |
| `SharedMedia_Nistaux.toc` | WoW addon metadata, dependency declaration, and file load order |
| `SharedMedia_Nistaux.lua` | Obtains LibSharedMedia and registers the curated runtime media set |
| `font/` | Packaged font files |
| `statusbar/` | Packaged status-bar textures |
| `border/` | Packaged border textures |
| `background/` | Image inventory; currently not registered or loaded by this addon |
| `sound/` | Reserved media directory; currently empty |
| `README.md` | Human-facing project entry point |
| `AGENTS.md` | Concise repository-local instructions for coding agents |
| `docs/project-notes.md` | This technical guide and durable troubleshooting context |
| [`docs/media-provenance.md`](media-provenance.md) | Bundled-media provenance, license evidence, and owner disposition |
| `tools/package_release.py` | Reproducible release builder and archive validator |
| `tests/` | Standard-library packaging tests |
| `.github/workflows/release.yml` | Tag-triggered test, package, and GitHub release workflow |

## Runtime architecture

The runtime addon has no UI, events, SavedVariables, configuration, localization, or plugin modules. Repository release tooling is separate from its linear load path:

1. WoW reads `SharedMedia_Nistaux.toc`.
2. The TOC requires `SharedMedia`, ensuring that dependency loads first.
3. WoW executes `SharedMedia_Nistaux.lua`.
4. Lua obtains `LibSharedMedia-3.0` through `LibStub`.
5. Lua synchronously registers 1 border, 14 fonts, and 15 status-bar textures.
6. Consumer addons query LibSharedMedia for those registered names.

Most packaged files are inventory only and are not exposed through LibSharedMedia by this addon. Another addon can still reference a packaged media file directly by path. The installed addon folder must remain named `SharedMedia_Nistaux` because every registered asset path contains that folder name.

Current dependency metadata is:

```toc
## Dependencies: SharedMedia
```

## Adding or changing media

1. Put the media file in the directory matching its LibSharedMedia type.
2. Add or update the corresponding `LSM:Register(mediaType, displayName, path)` call in `SharedMedia_Nistaux.lua`.
3. Match the repository filename, extension, path, and case exactly.
4. Use `Interface\AddOns\SharedMedia_Nistaux\...` as the in-game path prefix.
5. Preserve an existing display name unless intentionally migrating consumer profiles; addons may persist that name in SavedVariables.
6. Run the static validation below.
7. Test the entry in game through an addon that consumes LibSharedMedia. Static checks cannot prove that WoW can decode or render the media.

Keep generic media registration independent of consumer addons such as Details, ElvUI, or ToxiUI.

## Details investigation

There is no executable Details integration in the current repository or in any commit currently reachable from its Git history:

- no Details global or API access;
- no Details plugin registration;
- no Details dependency in the TOC;
- no Details load-state checks or event handlers.

The only Details-named files are passive installer artwork:

- `background/Installer/DetailsOne.blp`
- `background/Installer/DetailsTwo.blp`

Neither file is referenced by this addon's TOC or Lua. Media files cannot execute Details code and should not cause a Lua error when Details is absent. Removing them would reduce the assets distributed by this addon but would not change its current registrations.

If an installed local copy produces a Details-related error, capture the complete Lua stack trace and compare `Interface/AddOns/SharedMedia_Nistaux` with this repository. A stale local Lua or XML file may not exist in Git.

### If direct Details integration is added later

Details consumes LibSharedMedia, so direct integration is normally unnecessary. If a future feature genuinely calls Details APIs:

1. Declare `## OptionalDeps: Details`, not a required dependency.
2. Keep ordinary LibSharedMedia registration outside the Details-specific path.
3. Confirm Details has fully loaded and capability-check each API method before calling it.
4. Make initialization idempotent.
5. If Details may load later, retry only on `ADDON_LOADED` for the exact addon folder name `Details`.
6. Do not force-load Details merely to offer optional styling.

`OptionalDeps` provides load ordering when the other addon is available without making it mandatory. Current clients expose load state through `C_AddOns.IsAddOnLoaded`; `ADDON_LOADED` signals that an addon's Lua files have finished loading.

## Known work

GitHub Issues is the source of truth for actionable work:

- [#1 Fix invalid status-bar texture registrations](https://github.com/nistaux/SharedMedia_Nistaux/issues/1) — the three path extensions are corrected in the current code; in-game rendering validation remains pending.
- [#2 Complete distribution metadata and bundled-media provenance](https://github.com/nistaux/SharedMedia_Nistaux/issues/2) — add release metadata and resolve the licensing/redistribution findings recorded in [`docs/media-provenance.md`](media-provenance.md).

Do not infer that an issue is resolved from this document; check its current GitHub state.

## Validation

### Before every change

- Confirm which WoW client flavor and installed addon copy are involved.
- Inspect the complete stack trace for reported Lua errors.
- Check existing registrations before adding a duplicate display name.

### Static repository checks

```bash
# Formatting and intended changes
git diff --check
git diff
git status --short

# Executable addon files
find . -type f \( -iname '*.lua' -o -iname '*.toc' -o -iname '*.xml' \) \
  -not -path './.git/*' -print

# Details references in executable or metadata files
rg -n -i 'details' --glob '*.lua' --glob '*.toc' --glob '*.xml' .
```

Audit all registered paths against the filesystem:

```bash
python - <<'PY'
import re
import subprocess
from pathlib import Path

source = Path("SharedMedia_Nistaux.lua").read_text()
tracked = set(subprocess.run(
    ["git", "ls-files"], check=True, capture_output=True, text=True
).stdout.splitlines())
for wow_path in re.findall(r"\[\[(Interface[^]]+)\]\]", source):
    relative = wow_path.split("SharedMedia_Nistaux" + chr(92), 1)[1]
    relative = relative.replace(chr(92), "/")
    status = "OK" if relative in tracked and Path(relative).is_file() else "MISSING"
    print(f"{status:7} {relative}")
PY
```

### In-game validation

- Enable `SharedMedia` and `SharedMedia_Nistaux` for the intended client flavor.
- Confirm addon initialization produces no Lua errors.
- Fetch/select changed media through at least one LibSharedMedia consumer.
- Confirm fonts load and textures render rather than appearing blank or green.
- If the failure only occurs in the installed copy, compare that directory with Git for stale files.

## Releases

Future release tags use `vYY.M.D.<7-character-commit>`. Historical tags with numeric revision suffixes remain valid, but new tags use the short commit ID so the source is unambiguous. The source TOC contains `## Version: @project-version@`; the release builder replaces that token in memory with the tag version without the leading `v` and does not modify the working file.

The custom archive contains one installable `SharedMedia_Nistaux/` root and this exact allowlist:

- `SharedMedia_Nistaux.lua`
- `SharedMedia_Nistaux.toc`
- `README.md`
- all tracked regular files under `border/`, `font/`, and `statusbar/`

It excludes `background/`, `sound/`, `docs/`, `.git/`, `.github/`, `AGENTS.md`, `tools/`, `tests/`, and every other path. GitHub's automatic source archives cannot be filtered; users should install the custom ZIP asset instead.

### Release procedure

Finish all intended changes before choosing the version. Commit them, then run:

```bash
SHORT_SHA=$(git rev-parse --short=7 HEAD)
TAG="v26.7.31.$SHORT_SHA"
git tag "$TAG"

python -m unittest discover -s tests -v
python tools/package_release.py --tag "$TAG" --revision HEAD
unzip -l "dist/SharedMedia_Nistaux-${TAG#v}.zip"
sha256sum "dist/SharedMedia_Nistaux-${TAG#v}.zip"

git push origin "$TAG"
```

Use the actual release date in the tag. The exact seven-character suffix must match the first seven characters of the resolved `--revision` commit; 1-6 digit suffixes are accepted only for historical numeric revisions. The builder reads the immutable Git commit tree, so staged, unstaged, and untracked files cannot affect the archive. If local validation fails after creating the local tag, fix the problem and recreate the tag on the corrected commit before pushing it. A pushed matching tag starts `.github/workflows/release.yml`, which repeats the tests, packages `HEAD` from the tagged checkout, creates the GitHub release, and uploads only the custom ZIP asset.

## Primary references

- Blizzard-generated addon API documentation (`C_AddOns.IsAddOnLoaded`, `ADDON_LOADED`): <https://github.com/Gethe/wow-ui-source/blob/live/Interface/AddOns/Blizzard_APIDocumentationGenerated/AddOnsDocumentation.lua>
- Warcraft Wiki TOC format and dependency directives: <https://warcraft.wiki.gg/wiki/The_TOC_Format>
- Warcraft Wiki `ADDON_LOADED`: <https://warcraft.wiki.gg/wiki/ADDON_LOADED>
- Details upstream repository and TOC: <https://github.com/Tercioo/Details-Damage-Meter> and <https://github.com/Tercioo/Details-Damage-Meter/blob/master/Details.toc>
- Details UI API: <https://github.com/Tercioo/Details-Damage-Meter/blob/master/API%20UI.txt>
