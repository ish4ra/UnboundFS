# Brand build tools

Design tooling only, not application code. Everything in `design/brand/` is generated from here.

| File | Role |
|---|---|
| `shear.py` | Canonical symbol geometry, palette and colour contexts (copied unchanged from Phase 0) |
| `svgkit.py` | Icon container, harfbuzz-shaped outlined lettering (shared with the Phase 0 tools) |
| `build_brand.py` | `assets` → SVGs and render jobs; `package` → `.icns`, `.iconset`, asset catalogs; `pages` → boards, GitHub and promo images |
| `render.mjs` | Headless Chromium rasteriser (Playwright) |
| `validate_brand.py` | Identity test against the approved concept, SVG/PNG/ICNS/asset-catalog checks, documentation links |
| `build.sh` | Runs the whole pipeline, then validation |

Requirements: Python 3.10+ with `fonttools`, `uharfbuzz`, `Pillow`; Node 18+ with `playwright`;
Inter (OFL) installed at `/usr/share/fonts/opentype/inter/`.

```bash
./build.sh
```

`AppIcon.icns` is written directly (PNG-payload `icp4/icp5/ic07–ic14` entries, the same layout
`iconutil` produces), so the build does not need macOS. On a Mac it can be cross-checked with
`iconutil -c iconset AppIcon.icns`.
