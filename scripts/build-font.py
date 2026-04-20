#!/usr/bin/env python3
"""build-font.py — pure-Python OTF/WOFF/WOFF2 build from the UFO3 source.

Alternative to scripts/build-font.sh (FontForge-based), designed for CI
environments where installing a recent FontForge is impractical — Ubuntu's
apt ships FontForge 20230101 which segfaults on our UFO3 layout.

Stack: ``fontTools`` + ``ufo2ft`` + ``ufoLib2``. All pure Python. ufo2ft
compiles UFO3 → OTF (CFF) by way of fontTools' glyph-set pipeline;
fontTools then flavors to WOFF / WOFF2. Rhena's ADR-0012 @font-face
delivery expects both WOFF flavours served alongside (WOFF2 preferred,
WOFF fallback).

Determinism: honours SOURCE_DATE_EPOCH for head.created / head.modified.

Usage:
    python scripts/build-font.py

Outputs:
    build/hildegard-neumes.otf
    build/hildegard-neumes.woff
    build/hildegard-neumes.woff2

Notes on byte-identity vs build-font.sh:
    fontTools and FontForge use different CFF serializers, so the OTF
    bytes will differ between this script and scripts/build-font.sh.
    Both are valid, SMuFL-conformant fonts that pass validate-font.py;
    the shell/FontForge build is the local-dev canonical, the Python
    build is the CI-reliable equivalent. Any consumer needing
    byte-exact equivalence should pick one build path and stick with it.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
    from ufo2ft import compileOTF
    from ufoLib2 import Font
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        "error: build-font.py requires fontTools, ufo2ft, and ufoLib2. "
        f"Install with: pip install fonttools ufo2ft ufoLib2 brotli\n({exc})\n"
    )
    sys.exit(2)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
UFO_PATH = PROJECT_ROOT / "src" / "hildegard-neumes.ufo"
BUILD_DIR = PROJECT_ROOT / "build"

# Mac-HFS-epoch offset (seconds between 1904-01-01 and 1970-01-01). OTF
# head.created / head.modified are stored as seconds since 1904.
MAC_EPOCH_OFFSET = 2082844800


def _deterministic_mac_time() -> int:
    """SOURCE_DATE_EPOCH → Mac-HFS timestamp (1904-based)."""
    unix_epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0"))
    return unix_epoch + MAC_EPOCH_OFFSET


def build(ufo_path: Path, build_dir: Path) -> None:
    if not ufo_path.is_dir():
        sys.stderr.write(
            f"error: UFO3 source not found at {ufo_path}\n"
            "       This script is the CI / pure-Python build path — see "
            "scripts/build-font.sh for the FontForge-based local build.\n"
        )
        sys.exit(2)

    build_dir.mkdir(parents=True, exist_ok=True)
    ufo = Font.open(ufo_path)
    otf = compileOTF(ufo, removeOverlaps=True, optimizeCFF=0)

    mac_time = _deterministic_mac_time()
    otf["head"].created = mac_time
    otf["head"].modified = mac_time

    otf_path = build_dir / "hildegard-neumes.otf"
    otf.save(otf_path)
    print(f"built {otf_path}")

    # WOFF — reopen from OTF to start with a clean TTFont each flavor
    woff = TTFont(str(otf_path))
    woff.flavor = "woff"
    woff_path = build_dir / "hildegard-neumes.woff"
    woff.save(woff_path)
    print(f"built {woff_path}")

    # WOFF2
    woff2 = TTFont(str(otf_path))
    woff2.flavor = "woff2"
    woff2_path = build_dir / "hildegard-neumes.woff2"
    woff2.save(woff2_path)
    print(f"built {woff2_path}")


if __name__ == "__main__":
    build(UFO_PATH, BUILD_DIR)
