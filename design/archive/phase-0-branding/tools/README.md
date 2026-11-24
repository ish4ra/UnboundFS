# Brand-concept build tools

These scripts generate every file in `design/branding/` from the parametric definitions in
`concepts.py`. They are design tooling only, not application code.

| File | Role |
|---|---|
| `concepts.py` | Geometry (100 × 100 unit canvas), palettes, typography and symbolism for all eight concepts |
| `svgkit.py` | macOS-style icon container, harfbuzz-shaped wordmarks converted to outlines, SVG documents |
| `build.py` | `assets` writes the SVG sources and PNG jobs; `pages` writes boards, sheets, gallery and README |
| `render.mjs` | Rasterises SVG and HTML with headless Chromium (Playwright) |
| `validate.py` | Checks SVG validity, PNG sizes and transparency, and README links |
| `build.sh` | Runs the full pipeline |

## Requirements

- Python 3.10+ with `fonttools`, `uharfbuzz` and `brotli`
- Node 18+ with `playwright` and a Chromium build
- TTF copies of the wordmark typefaces (all SIL OFL 1.1) in one folder, named as in `svgkit.FONTS`:
  Manrope, Space Grotesk, Outfit, Fraunces, JetBrains Mono and Sora (for example from the
  `@fontsource/*` npm packages, converted from WOFF with fontTools), plus Inter / Inter Display.

```bash
UNBOUND_FONT_DIR=/path/to/ttf ./build.sh && python3 validate.py
```

Fonts are not committed: the published SVGs contain outlines, so nobody needs them to view the assets.
