#!/usr/bin/env bash
# Rebuild every UnboundFS brand-concept asset. See README.md in this folder.
set -euo pipefail
cd "$(dirname "$0")"
: "${UNBOUND_FONT_DIR:?set UNBOUND_FONT_DIR to a folder of TTF files (see README.md)}"
python3 build.py assets
node render.mjs .build/jobs-assets.json
python3 build.py pages
node render.mjs .build/jobs-pages.json
