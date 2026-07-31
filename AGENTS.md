# Repository instructions

## Start here

1. Read `README.md` for the user-facing overview.
2. Read `docs/project-notes.md` for architecture, workflows, known issues, and validation.
3. Inspect `SharedMedia_Nistaux.toc` and `SharedMedia_Nistaux.lua`; together they are the complete executable surface.

## Stable project facts

- This is a personal World of Warcraft LibSharedMedia provider, not a configuration addon.
- `SharedMedia` is required and must load first.
- The installed folder must remain named `SharedMedia_Nistaux` because media paths contain that name.
- Unregistered files are not exposed through LibSharedMedia by this addon, although another addon can reference a packaged media file directly by path.
- Registration paths must exactly match packaged filenames, extensions, and case.
- The Git repository currently contains no Details API integration or dependency. Details-named `.blp` files are passive artwork.
- Do not attribute an in-game error to this addon without checking the complete Lua stack trace and the installed addon directory for stale local files.

## Change checklist

- Make the smallest change that satisfies the request.
- Preserve existing LibSharedMedia display names unless a rename is explicitly requested; consumers may store those names in profiles.
- Verify every changed registration against the filesystem.
- Keep core media registration independent of optional consumer addons.
- Run `git diff --check` and inspect `git diff` and `git status` before reporting completion.
- Clearly distinguish static repository validation from in-game testing that still needs to be performed.
- Track actionable follow-up work in GitHub Issues rather than adding undocumented TODOs.
