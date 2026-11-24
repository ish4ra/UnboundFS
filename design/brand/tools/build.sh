#!/usr/bin/env bash
# Rebuild every production UnboundFS brand asset. See README.md in this folder.
set -euo pipefail
cd "$(dirname "$0")"
: "${UNBOUND_FONT_DIR:=}"   # only Inter is needed; it is read from /usr/share/fonts/opentype/inter
python3 build_brand.py assets
node render.mjs .build/jobs-assets.json
python3 build_brand.py package
python3 build_brand.py pages
node render.mjs .build/jobs-pages.json
python3 validate_brand.py
