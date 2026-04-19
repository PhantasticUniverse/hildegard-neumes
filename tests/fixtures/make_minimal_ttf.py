"""Programmatically synthesize a minimal test TTF for the codegen test suite.

The fixture contains 19 named Rhineland glyphs with trivial placeholder
outlines (small rectangles at the declared advance widths). Outlines are
intentionally minimal — the goal is to exercise the codegen pipeline, not
to validate visual shape quality.

Usage (imported by tests/conftest.py at session start):

    from fixtures.make_minimal_ttf import build_minimal_ttf
    build_minimal_ttf(output_path, widths_json_path)

Standalone usage (for debugging):

    python tests/fixtures/make_minimal_ttf.py \\
        --widths src/widths.json \\
        --out tests/fixtures/minimal.ttf
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

# Canonical ordering — matches src/glyph-names.json and Rhena's existing
# ALL_GLYPHS slice. Any change here MUST be synchronized with
# scripts/generate-rhena-glyphs.py GLYPH_ORDER.
GLYPH_FONT_NAMES = (
    "rh_punctum",
    "rh_virga",
    "rh_punctum_inclinatum",
    "rh_quilisma",
    "rh_oriscus",
    "rh_strophicus",
    "rh_pressus",
    "rh_liquescent_asc",
    "rh_liquescent_desc",
    "rh_deminutum",
    "rh_c_clef",
    "rh_f_clef",
    "rh_divisio_minima",
    "rh_divisio_maior",
    "rh_divisio_maxima",
    "rh_divisio_finalis",
    "rh_virgula",
    "rh_pes_line",
    "rh_flexa_line",
)

EM_SIZE = 1000


def _placeholder_glyph(advance_width: int):
    """A tiny LSB-0 rectangle with a quadratic curve on the right edge.

    Shape: 10 units wide × 100 units tall. The right edge is drawn as a
    quadratic Bézier (``qCurveTo``) rather than a straight line so the
    extracted path string contains at least one ``Q`` command —
    exercising the TrueType glyf codepath in ``SVGPathPen``. The OTF
    sibling fixture (`make_minimal_otf.py`) does the same with a cubic
    (``C``). Parametrized tests assert the outputs differ.

    The outline is intentionally minimal — the goal is to feed the
    codegen pipeline, not to validate visual shape quality.
    """
    pen = TTGlyphPen(None)
    pen.moveTo((0, 0))
    pen.lineTo((10, 0))
    # Quadratic curve up the right edge: one off-curve control point + endpoint.
    pen.qCurveTo((10, 50), (10, 100))
    pen.lineTo((0, 100))
    pen.closePath()
    return pen.glyph()


def build_minimal_ttf(output_path: Path, widths_json_path: Path) -> None:
    """Synthesize a minimal TTF containing the 19 Rhineland glyphs.

    Advance widths are read from src/widths.json; outlines are placeholder
    rectangles. The font is not intended to render meaningfully — only to
    serialize/deserialize cleanly and expose the expected glyph names to
    fontTools consumers.
    """
    widths_raw = json.loads(Path(widths_json_path).read_text(encoding="utf-8"))
    widths = widths_raw.get("widths", {})

    fb = FontBuilder(EM_SIZE, isTTF=True)

    glyph_order = [".notdef", *GLYPH_FONT_NAMES]
    fb.setupGlyphOrder(glyph_order)

    # Minimal cmap — map .notdef to space so the font has a valid character
    # map. The Rhineland glyphs don't need cmap entries for the codegen
    # pipeline to work (fontTools exposes them by glyph name via the
    # glyph set, not via unicode codepoints).
    fb.setupCharacterMap({0x0020: ".notdef"})

    glyphs = {".notdef": _placeholder_glyph(500)}
    metrics = {".notdef": (500, 0)}

    for name in GLYPH_FONT_NAMES:
        advance = int(widths.get(name, 100))
        glyphs[name] = _placeholder_glyph(advance)
        metrics[name] = (advance, 0)  # LSB = 0

    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
    fb.setupNameTable(
        {
            "familyName": "Hildegard Neumes Minimal Test",
            "styleName": "Regular",
            "uniqueFontIdentifier": "hildegard-neumes-minimal-test-0.1.0",
            "fullName": "Hildegard Neumes Minimal Test Regular",
            "psName": "HildegardNeumesMinimalTest-Regular",
        }
    )
    fb.setupPost()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fb.save(str(output_path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build minimal test TTF")
    parser.add_argument("--widths", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    build_minimal_ttf(args.out, args.widths)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
