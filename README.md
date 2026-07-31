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

Release versions use `YY.MM.dd` with an optional revision suffix, and Git tags use `vYY.MM.dd[.N]` (for example, `v26.01.27.1`).
