"""Programmatically synthesize a minimal test OTF (CFF) for the codegen test suite.

**Why this exists** (per docs/planning/claude-review-2-2026-04-14.md § 1):
ADR-0007 pins the production font as OpenType/CFF with cubic Bézier
outlines. `tests/fixtures/make_minimal_ttf.py` produces a TrueType font
with quadratic outlines, which does NOT exercise the codepath that
`SVGPathPen` takes for CFF glyphs. A bug in how `normalize_path` handles
real CFF cubics — rounding drift on control-point coordinates, subtle
`C`-after-`S` edge cases — would pass every existing test and fail on
first contact with the real OTF.

This fixture complements `make_minimal_ttf.py`. Together they give
defense-in-depth coverage across both outline formats:
- The TTF fixture produces ``Q`` commands via ``TTGlyphPen``.
- The OTF fixture produces ``C`` commands via ``T2CharStringPen``.

Parametrized tests in ``tests/test_determinism.py`` and
``tests/test_golden_output.py`` run the codegen pipeline against both
fixtures independently, catching format-specific regressions.

Usage (imported by ``tests/conftest.py`` at session start):

    from fixtures.make_minimal_otf import build_minimal_otf
    build_minimal_otf(output_path, widths_json_path)

Standalone (for debugging):

    python tests/fixtures/make_minimal_otf.py \\
        --widths src/widths.json \\
        --out tests/fixtures/minimal.otf
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen

# Canonical ordering — must match src/glyph-names.json and
# scripts/generate-rhena-glyphs.py GLYPH_ORDER. Kept in sync manually;
# the codegen test suite's contract-validation tests enforce that any
# drift surfaces as a test failure, not a silent mismatch.
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


def _placeholder_charstring(advance_width: int):
    """Draw a small rectangle with a cubic curve segment.

    Shape: a rectangle 10 units wide × 100 units tall, with the right
    edge drawn as a cubic Bézier (two interior control points) rather
    than a straight line. This guarantees at least one ``C`` command
    appears in the extracted path string — the whole point of the CFF
    fixture relative to the TTF fixture is to exercise the cubic code
    path in ``SVGPathPen`` → ``normalize_path``.

    The outline is intentionally minimal — the goal is to feed the
    codegen pipeline, not to validate visual shape quality.
    """
    pen = T2CharStringPen(advance_width, None)
    pen.moveTo((0, 0))
    pen.lineTo((10, 0))
    # Cubic curve up the right edge — two control points + endpoint.
    pen.curveTo((10, 33), (10, 67), (10, 100))
    pen.lineTo((0, 100))
    pen.closePath()
    return pen.getCharString()


def build_minimal_otf(output_path: Path, widths_json_path: Path) -> None:
    """Synthesize a minimal OTF containing the 19 Rhineland glyphs.

    Advance widths are read from ``src/widths.json``; outlines are
    placeholder rectangles with at least one cubic curve per glyph.
    """
    widths_raw = json.loads(Path(widths_json_path).read_text(encoding="utf-8"))
    widths = widths_raw.get("widths", {})

    fb = FontBuilder(EM_SIZE, isTTF=False)  # CFF, not glyf

    glyph_order = [".notdef", *GLYPH_FONT_NAMES]
    fb.setupGlyphOrder(glyph_order)

    # Minimal cmap — map a space to .notdef so the font has a valid
    # character map. The Rhineland glyphs don't need cmap entries; the
    # codegen pipeline reads them by name from the glyph set, not by
    # Unicode codepoint.
    fb.setupCharacterMap({0x0020: ".notdef"})

    # Build charstrings for every glyph (including .notdef).
    char_strings: dict[str, object] = {}
    for name in glyph_order:
        advance = int(widths.get(name, 500))
        char_strings[name] = _placeholder_charstring(advance)

    # Per fontTools' FontBuilder API: setupCFF(psName, fontInfo,
    # charStrings, privateDict). privateDict can be empty for a minimal
    # font; fontTools fills in sensible defaults.
    fb.setupCFF(
        psName="HildegardNeumesMinimalTestCFF-Regular",
        fontInfo={
            "FullName": "Hildegard Neumes Minimal Test CFF",
            "FamilyName": "Hildegard Neumes Minimal Test CFF",
            "Weight": "Regular",
            "version": "0.1",
        },
        charStringsDict=char_strings,
        privateDict={},
    )

    # Compute LSB per glyph from the charstring bounds. T2CharString
    # tracks its own bounds via calcBounds(glyphSet); glyphSet=None is
    # fine here because we have no composite charstrings.
    metrics: dict[str, tuple[int, int]] = {}
    for name in glyph_order:
        advance = int(widths.get(name, 500))
        cs = char_strings[name]
        bounds = cs.calcBounds(None)
        lsb = int(bounds[0]) if bounds is not None else 0
        metrics[name] = (advance, lsb)

    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupOS2(
        sTypoAscender=800,
        sTypoDescender=-200,
        usWinAscent=800,
        usWinDescent=200,
    )
    fb.setupNameTable(
        {
            "familyName": "Hildegard Neumes Minimal Test CFF",
            "styleName": "Regular",
            "uniqueFontIdentifier": "hildegard-neumes-minimal-test-cff-0.1.0",
            "fullName": "Hildegard Neumes Minimal Test CFF Regular",
            "psName": "HildegardNeumesMinimalTestCFF-Regular",
        }
    )
    fb.setupPost()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fb.save(str(output_path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build minimal test OTF (CFF)")
    parser.add_argument("--widths", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    build_minimal_otf(args.out, args.widths)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
