# Design archive

Previous design work, kept permanently for reference and possible future use.
**Nothing in this folder is part of the official UnboundFS identity, and nothing here may be bundled
with application builds, DMG installers or release packages.** The approved, production identity
lives in [`design/brand/`](../brand/).

| Archive | Contents |
|---|---|
| [`phase-0-branding/`](phase-0-branding/) | All eight Phase 0 logo and app icon concepts (SVG sources, PNG exports, boards, comparison sheet, interactive gallery), the generator and validation scripts, palettes, font notices, and [rejected / experimental variants](phase-0-branding/rejected/). Concept 05 Shear was selected by the owner. |

## Permanent backup

The original, unmodified Phase 0 collection is also preserved on the branch
[`archive/phase-0-branding`](https://github.com/ish4ra/UnboundFS/tree/archive/phase-0-branding),
so it survives independently of any feature branch or pull request.

## Rules for this folder

- Add, never delete. Superseded work moves here instead of being removed.
- Archived assets are excluded from source archives via `.gitattributes` (`export-ignore`) and must
  never be referenced by an Xcode target, packaging script or release workflow.
- Each archive keeps its own README explaining what it is and why it was superseded.
