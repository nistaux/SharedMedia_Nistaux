# SharedMedia_Nistaux

A personal LibSharedMedia media pack for World of Warcraft. It makes a curated set of fonts, status-bar textures, and a border available to addons that consume LibSharedMedia.

## Requirements and installation

- Install and enable the [**SharedMedia** addon](https://www.curseforge.com/wow/addons/sharedmedia).
- Install this repository as `World of Warcraft/_retail_/Interface/AddOns/SharedMedia_Nistaux` (adjust the game flavor directory as needed).
- Keep the folder name exactly `SharedMedia_Nistaux`; registered media paths depend on it.

This addon does not require or directly integrate with consumer addons. It only registers media such as fonts and textures through LibSharedMedia for compatible addons to use.

## Repository guide

- [`docs/project-notes.md`](docs/project-notes.md) — architecture, safe change workflow, integration guidance, troubleshooting, validation, and known issues
- [`AGENTS.md`](AGENTS.md) — concise repository-local instructions for Pi and other coding agents
- [`SharedMedia_Nistaux.toc`](SharedMedia_Nistaux.toc) — addon metadata and load order
- [`SharedMedia_Nistaux.lua`](SharedMedia_Nistaux.lua) — the complete runtime implementation
- [GitHub Issues](https://github.com/nistaux/SharedMedia_Nistaux/issues) — tracked defects and maintenance work

## Development

Media files that are not registered in `SharedMedia_Nistaux.lua` are not exposed by this addon through LibSharedMedia, although another addon could reference a packaged file directly by path. When adding or changing a registration, verify that its path exactly matches the packaged filename, extension, and case. See the [project notes](docs/project-notes.md#adding-or-changing-media) for the full workflow.

## Releases

A pushed release tag builds an installable custom ZIP with one `SharedMedia_Nistaux/` root folder. The archive includes only `SharedMedia_Nistaux.lua`, `SharedMedia_Nistaux.toc`, `README.md`, and the complete `border/`, `font/`, and `statusbar/` directories. Repository-only files and unused top-level media directories are excluded.

Future release tags use `vYY.M.D.<7-character-commit>`, for example `v26.7.31.abcdef0`. The packaged TOC receives the tag version without the leading `v`; the source TOC keeps its build token. Historical numeric revision tags remain valid.

Download the custom `SharedMedia_Nistaux-<version>.zip` release asset for installation. GitHub's automatic “Source code” archives are unavoidable repository snapshots; they are not filtered and are not the install package.
