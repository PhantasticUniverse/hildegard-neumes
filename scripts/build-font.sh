#!/usr/bin/env bash
# build-font.sh — export hildegard-neumes.otf (+.woff2) from the UFO3 source
# at src/hildegard-neumes.ufo/ (per ADR-0001 in docs/adr/).
#
# Requires FontForge installed and on PATH. On macOS:
#     brew install fontforge
#
# Usage:
#     bash scripts/build-font.sh
#
# Outputs go to build/. The output files are .gitignored.

set -euo pipefail

# Determinism: pin FontForge's internal timestamps to the Unix epoch.
# Per ADR-0004 in docs/adr/. FontForge respects SOURCE_DATE_EPOCH for its
# head.created / head.modified writes when available, which is the
# reproducible-builds standard environment variable.
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-0}"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UFO_SOURCE="$PROJECT_ROOT/src/hildegard-neumes.ufo"
BUILD_DIR="$PROJECT_ROOT/build"

if ! command -v fontforge >/dev/null 2>&1; then
    echo "error: fontforge not found on PATH. Install with: brew install fontforge" >&2
    exit 2
fi

if [ ! -d "$UFO_SOURCE" ]; then
    echo "error: UFO3 source not found at $UFO_SOURCE" >&2
    echo "       Open FontForge (or any UFO-aware tool), create a UFO3 at" >&2
    echo "       that path, and populate the 19 glyph slots per" >&2
    echo "       src/glyph-names.json and src/widths.json." >&2
    echo "       Per ADR-0001 (source format)." >&2
    exit 2
fi

mkdir -p "$BUILD_DIR"

# Drive FontForge via its Python API rather than the -lang=ff FF-script
# frontend. On macOS Homebrew FontForge 20251009, the FF-script engine
# segfaults on Open() against a well-formed UFO3 while the Python API
# loads and generates cleanly. The two paths are equivalent for headless
# export; Python is the stable one.
fontforge -script - "$UFO_SOURCE" "$BUILD_DIR" <<'PYEOF' 2>&1 \
    | grep -v '^Copyright' \
    | grep -v '^Based on sources' \
    | grep -v "^Core python package 'pkg_resources'" \
    || true
import sys
import fontforge
ufo_path, build_dir = sys.argv[1], sys.argv[2]
font = fontforge.open(ufo_path)
font.generate(f"{build_dir}/hildegard-neumes.otf")
font.generate(f"{build_dir}/hildegard-neumes.woff2")
font.close()
PYEOF

echo "Built:"
ls -la "$BUILD_DIR"/hildegard-neumes.{otf,woff2} 2>/dev/null || true
