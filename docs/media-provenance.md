# Bundled media provenance audit

_Last reviewed: 2026-07-31_

This document records evidence; it is not legal advice. A filename, visual similarity, copyright notice, or copy found in another addon does not by itself grant redistribution rights.

## Owner disposition (2026-07-31)

This is a personal media pack shared informally with friends. The owner has explicitly accepted the recorded uncertainty for that use and made these scope decisions:

- do not continue auditing, deleting, or replacing unregistered assets;
- do not remove, replace, or seek permission for restricted or unresolved registered media;
- do not add a repository-wide license at this time;
- package releases from the approved runtime allowlist and leave the remaining repository inventory unchanged.

These are project-maintenance decisions, not conclusions about third-party rights. Do not repeatedly reopen the provenance or remediation work unless the owner asks, the intended use changes, or a rights holder raises a concern.

## Snapshot and status vocabulary

After correcting the three `.tga`/`.blp` registration mismatches tracked in issue #1, the repository contains **140 media files**:

- **30 registered and present:** 14 fonts, 15 status-bar textures, and 1 border.
- **110 tracked but unregistered:** available by direct file path in a source checkout, but not exposed by this addon through LibSharedMedia.

These counts cover tracked files below `background/`, `border/`, `font/`, `sound/`, and `statusbar/`. Registration is determined from `SharedMedia_Nistaux.lua`. The custom release archive excludes the 41 files under `background/`; it includes the remaining 69 unregistered files because the approved `statusbar/` directory is packaged as a complete unit.

| Term | Meaning |
| --- | --- |
| **Exact match** | File content was matched to an upstream repository copy. This establishes provenance only, not permission. |
| **Likely origin** | Names, metadata, directory structure, or visual role point to a source, but an exact source artifact is not yet pinned. |
| **Permission documented** | A primary license grants redistribution if its conditions are satisfied. |
| **Restricted** | Available evidence expressly limits or prohibits this repository's separate redistribution. |
| **Unknown rights** | No sufficiently specific redistribution grant has been verified. Treat as non-redistributable until resolved. |

## Current distribution conclusion

The current repository should not be given a blanket license that purports to cover all bundled media.

ToxiUI's current upstream license prohibits redistribution of its addon content without permission while explicitly excluding third-party resources from that license's scope. Its official FAQ separately says ToxiUI fonts, icons, and textures may not be acquired for use outside ToxiUI. Exact matching can show that a local file occurs in ToxiUI, but it cannot establish whether ToxiUI or a third party owns that file, nor can it supply a missing redistribution grant. Each resource still needs its own exact source and license chain.

The repository owner can choose a license for repository-authored Lua and documentation. That project license must explicitly exclude third-party media unless and until each media file's redistribution rights are verified and its license conditions are included.

## Registered font audit

Embedded metadata was read from the local font binaries. Upstream ToxiUI/ElvUI matches are provenance evidence only. Where the exact original release and license file are not pinned, status remains unknown even when a family is commonly distributed elsewhere.

| Local file | Evidence and likely/exact origin | Redistribution conclusion | Next action |
| --- | --- | --- | --- |
| `font/ActionMan.ttf` | Embedded metadata: Iconian Fonts/ShyFonts, 2000; “Freeware for non-commercial use.” Copies occur in UI media repositories. | **Restricted/unclear.** Non-commercial-use wording is not an unqualified redistribution grant. | Pin the exact author release and license terms or replace/remove. |
| `font/BigNoodleToo.ttf` | Embedded metadata: James Arboghast/Sentinel Type, 2014; authorized for Sentinel Type licensees of Blizzard only and “may not be copied or distributed.” | **Restricted.** The embedded notice expressly prohibits this distribution. | Remove unless the owner can document applicable permission; replace profile usage deliberately. |
| `font/ContinuumMedium.ttf` | Embedded metadata credits Brøderbund Software (1996–1997), “All rights reserved.” No license grant is embedded. | **Unknown rights.** Copyright notice is not redistribution permission. | Locate an authoritative license covering this exact file or remove/replace. |
| `font/DieDieDie.ttf` | Embedded metadata identifies Static Type / Mike Emory (2001), says the font is free for personal use, and directs commercial users to contact the author. No separate redistribution grant is pinned. | **Restricted/unclear.** Personal-use permission is not an unqualified right to redistribute the font binary. | Locate the authoritative original package and redistribution terms, obtain permission, or remove/replace. |
| `font/Expressway.ttf` | Embedded metadata: Typodermic/Ray Larabie, version 2.100; “Do not distribute.” It links to Typodermic. | **Restricted.** The local binary expressly prohibits distribution. | Remove unless a separate license held by the owner expressly permits repository redistribution. |
| `font/Homespun.ttf` | Embedded metadata identifies “Homespun TT BRK” and Enigma Fonts, but contains no redistribution grant. Copies occur in UI media repositories. | **Unknown rights.** Exact original release/license is not pinned. | Pin the author release and applicable license or remove/replace. |
| `font/Invisible.ttf` | Embedded metadata says it was made by Simpy for WoW in 2021. Copies with this name occur in UI media repositories, but this audit has not pinned an authoritative exact source or independent redistribution license for the local binary. | **Unknown rights.** Inclusion in another addon is not a redistribution grant. | Obtain author permission or an independently licensed source, or remove. |
| `font/Montserrat-Black.ttf` | Embedded metadata credits the Montserrat Project Authors and declares SIL OFL 1.1. The official Montserrat repository is OFL-1.1, but the exact local binary-to-upstream release chain is not pinned. | **Likely permission, conditions incomplete.** OFL permits bundling/redistribution, but the exact source/version and required license copy must be established. | Match the binary to an official release (or replace with one), record it, and include the OFL text. |
| `font/Montserrat-Bold.ttf` | Same embedded OFL metadata and unresolved exact upstream chain as `Montserrat-Black.ttf`. | **Likely permission, conditions incomplete.** | Pin/replace from an official release and include the OFL text. |
| `font/Montserrat-Medium.ttf` | Same embedded OFL metadata and unresolved exact upstream chain as `Montserrat-Black.ttf`. | **Likely permission, conditions incomplete.** | Pin/replace from an official release and include the OFL text. |
| `font/PTSansNarrow.ttf` | Embedded metadata credits ParaType and includes the SIL OFL 1.1 text and reserved font names. OFL 1.1 permits its required notice to remain in accessible machine-readable font metadata. | **Permission documented; provenance incomplete.** The embedded license supports redistribution, while the exact official release/source for this binary is not yet pinned. | Pin the exact official release; optionally add a standalone OFL copy and attribution for easier auditing and archive packaging. |
| `font/Steelfish.ttf` | Embedded metadata links to Typodermic's license. Copies occur in UI media repositories, but this audit has not pinned the exact original package/license version for the local binary. | **Unknown rights.** A license URL in metadata is not enough to select the applicable redistribution terms. | Pin the exact Typodermic release and license or remove/replace. |
| `font/ToxiUI.ttf` | Embedded metadata: copyright 2023 ToxiUI, version 1.20. This strongly identifies a ToxiUI origin, but the exact authoritative release artifact is not pinned. | **Restricted.** ToxiUI's official FAQ prohibits separate acquisition/use of its fonts without permission. | Obtain explicit permission or remove/replace. |
| `font/ToxiUIIcons.ttf` | Embedded metadata: copyright 2023 ToxiUI Team, version 1.20. This strongly identifies a ToxiUI origin, but the exact authoritative release artifact is not pinned. | **Restricted.** ToxiUI's official FAQ prohibits separate acquisition/use of its icons without permission. | Obtain explicit permission or remove/replace. |

## Registered non-font audit

| Local group | Count | Evidence | Redistribution conclusion |
| --- | ---: | --- | --- |
| `statusbar/BuiOnePixel.tga`, `statusbar/ToxiUI-*`, and `statusbar/Bezo*` | 13 | Names and exact Git blob comparisons tie these files to ToxiUI's media tree, but do not establish whether ToxiUI or a third party owns each file. | **Unknown rights pending an original source/license.** ToxiUI's restrictions apply to ToxiUI-owned content; third-party resources require their own license chain. |
| `statusbar/d1.tga`, `statusbar/d1-border.tga` | 2 | These occur in UI media collections, including the copied media corpus, but this audit has not pinned an authoritative original source/license. | **Unknown rights.** |
| `border/Border_DropShadow.blp` | 1 | Likely origin is an upstream UI media collection; the authoritative original source/license is not pinned. | **Unknown rights.** |

All 30 runtime registrations now resolve to exact tracked filenames. This is a technical path result, not a license result.

## Unregistered corpus

The remaining **110 files** are not registered by `SharedMedia_Nistaux.lua`. They remain tracked in the Git repository; the custom release archive includes only the 69 located under the allowlisted `statusbar/` directory and excludes the 41 under `background/`.

The directory layout and many exact Git blob matches connect much of `background/` and the unregistered `statusbar/` subdirectories to ToxiUI. That establishes a strong likely/exact immediate source for groups such as installer artwork, armory/class artwork, logos, role/state icons, and theme/UI icons. It does **not** establish original ownership or separate redistribution permission. A complete path-by-path source map has not yet been recorded, so all 110 files remain **unknown rights** unless a file is later shown to be ToxiUI-owned (and restricted under its terms) or covered by a verified third-party license.

Per the owner disposition above, retain this corpus without further path-level audit or remediation unless the owner later changes scope.

## Maintenance status

The audit findings remain available as context, but remediation and further provenance work are intentionally out of scope under the owner disposition above. Release metadata is supplied by the tag-driven package builder. No project-wide license is selected; this avoids implying that one license covers third-party media. In-game validation is still required whenever a registered filename, media file, or display name changes.

## Primary evidence and sources

- Local font binaries and their embedded metadata: [`../font/`](../font/)
- Current ToxiUI repository: <https://github.com/Toxicom/toxiui>
- ToxiUI license (addon redistribution restriction and third-party-resource exclusion): <https://github.com/Toxicom/toxiui/blob/development/LICENSE>
- Official ToxiUI FAQ (fonts/icons/textures reuse): <https://toxiui.com/faq/>
- Official Montserrat repository and OFL license: <https://github.com/JulietaUla/Montserrat> and <https://github.com/JulietaUla/Montserrat/blob/master/OFL.txt>
- Google Fonts Montserrat source/license mirror: <https://github.com/google/fonts/tree/main/ofl/montserrat>
- Google Fonts PT Sans source/license mirror: <https://github.com/google/fonts/tree/main/ofl/ptsans>
- Typodermic official license information (relevant to Expressway and Steelfish): <https://typodermicfonts.com/license/>
- Upstream ElvUI repository media corpus used for provenance comparison: <https://github.com/tukui-org/ElvUI>

## Audit limitations

- No legal conclusion is made beyond quoting or applying explicit primary-source terms.
- “Exact match” does not prove that the matching upstream repository was the original rights holder.
- Links describe current upstream terms and may not prove the terms attached to an older local binary.
- In-game rendering and profile migration have not been tested.
