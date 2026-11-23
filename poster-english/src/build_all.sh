#!/usr/bin/env bash
# Rebuilds every deliverable. Needs: python3 + segno, node + playwright (chromium).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build output
python3 src/build_poster.py build/poster_trim.html 0
python3 src/build_poster.py build/poster_bleed.html 3
node src/render.js build/poster_trim.html  output/Roadside-Mosques-Poster_EN_85x200cm_print.pdf 850 2000
node src/render.js build/poster_bleed.html output/Roadside-Mosques-Poster_EN_85x200cm_with-3mm-bleed_print.pdf 856 2006
node src/render.js build/poster_trim.html  output/Roadside-Mosques-Poster_EN_preview.png 850 2000 0.5
