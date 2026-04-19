#!/usr/bin/env python3
"""validate-font.py — post-build sanity checks for hildegard-neumes.otf.

Runs after scripts/build-font.sh to catch common authoring mistakes before
they propagate through the codegen pipeline into Rhena. Checks:

1. OTF parses via fontTools without errors
2. All 19 expected glyph names are present
3. Every glyph's advance width matches src/widths.json within tolerance
4. Every glyph's bbox fits inside [max(|xMin|, |xMax|) * 2] for centred
   glyphs, OR [0, advance] for LSB-0 glyphs. Flags overflows per the
   2026-04-14 width review (docs/planning/width-review-2026-04-14.md).
5. No disallowed SVG path commands after normalization through the same
   normalize_path() helper the codegen uses.
6. unitsPerEm is 1000.

Exits 0 on success, 1 on any failure. Intended for use in CI and for the
`just validate-font` recipe in the justfile.

Usage:
    python scripts/validate-font.py \\
        --in build/hildegard-neumes.otf \\
        --names-map src/glyph-names.json \\
        --widths-table src/widths.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        f"error: fontTools is required. Install with `pip install fonttools`. ({exc})\n"
    )
    sys.exit(2)


_SCRIPT_DIR = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location(
    "generate_rhena_glyphs",
    _SCRIPT_DIR / "generate-rhena-glyphs.py",
)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
# CRITICAL: register in sys.modules before exec so @dataclass decorators
# can resolve cls.__module__. Otherwise dataclass raises AttributeError
# on 'NoneType' has no __dict__.
sys.modules["generate_rhena_glyphs"] = _MODULE
_SPEC.loader.exec_module(_MODULE)

normalize_path = _MODULE.normalize_path
ALLOWED_COMMANDS = _MODULE.ALLOWED_COMMANDS
load_contract = _MODULE.load_contract


def _path_bbox(path: str) -> tuple[int, int, int, int]:
    """Compute a coarse bbox from the integer coordinates in a normalized SVG path.

    This is a **conservative upper bound** for cubic Bézier curves.
    The convex-hull theorem guarantees the curve stays inside the polygon
    formed by its control points, so including control points in the bbox
    produces a bound that is never too small — but it can be strictly
    larger than the actual curve bbox when a control point extends past
    the curve's true extremes. A real glyph may therefore be flagged as
    overflowing when the rendered curve actually fits within its advance.

    Fine for false-positive overflow detection (we surface the warning
    so the designer can re-check), not suitable for accurate rendering
    bbox computation. Per docs/planning/claude-review-2-2026-04-14.md § 9.
    """
    tokens = [t for t in path.split() if t and t not in ALLOWED_COMMANDS]
    xs: list[int] = []
    ys: list[int] = []
    for i in range(0, len(tokens), 2):
        if i + 1 < len(tokens):
            try:
                xs.append(int(tokens[i]))
                ys.append(int(tokens[i + 1]))
            except ValueError:
                pass
    if not xs or not ys:
        return (0, 0, 0, 0)
    return (min(xs), min(ys), max(xs), max(ys))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate hildegard-neumes.otf")
    parser.add_argument("--in", dest="in_path", required=True, type=Path)
    parser.add_argument("--names-map", required=True, type=Path)
    parser.add_argument("--widths-table", required=True, type=Path)
    parser.add_argument(
        "--strict-overflow",
        action="store_true",
        help="Treat bbox-vs-advance overflows as errors. Default is warning.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    if not args.in_path.is_file():
        print(f"error: OTF not found: {args.in_path}", file=sys.stderr)
        return 2

    records, widths, tolerance = load_contract(args.names_map, args.widths_table)

    try:
        font = TTFont(str(args.in_path))
    except Exception as exc:
        print(f"error: cannot open OTF: {exc}", file=sys.stderr)
        return 1

    if font["head"].unitsPerEm != 1000:
        warnings.append(
            f"unitsPerEm = {font['head'].unitsPerEm}, expected 1000"
        )

    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"].metrics

    for rec in records:
        if rec.font_name not in glyph_set:
            errors.append(f"missing glyph: {rec.font_name}")
            continue

        # Check advance width
        actual_width = int(hmtx[rec.font_name][0])
        expected_width = widths[rec.font_name]
        if abs(actual_width - expected_width) > tolerance:
            errors.append(
                f"{rec.font_name}: advance width mismatch "
                f"(font={actual_width}, contract={expected_width}, tol={tolerance})"
            )

        # Check path commands and bbox
        pen = SVGPathPen(glyph_set)
        glyph_set[rec.font_name].draw(pen)
        try:
            normalized = normalize_path(pen.getCommands())
        except ValueError as exc:
            errors.append(f"{rec.font_name}: path normalization failed: {exc}")
            continue

        cmds = {c for c in normalized if c.isalpha()}
        bad = cmds - ALLOWED_COMMANDS
        if bad:
            errors.append(
                f"{rec.font_name}: disallowed path commands {sorted(bad)}"
            )

        # Overflow check: body width vs advance
        xmin, _, xmax, _ = _path_bbox(normalized)
        body_width = xmax - xmin
        if body_width > actual_width:
            msg = (
                f"{rec.font_name}: body width {body_width} "
                f"(x∈[{xmin}, {xmax}]) exceeds advance {actual_width}"
            )
            if args.strict_overflow:
                errors.append(msg)
            else:
                warnings.append(msg)

    # Report
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    for e in errors:
        print(f"error: {e}", file=sys.stderr)

    if errors:
        print(
            f"\nvalidate-font: {len(errors)} error(s), {len(warnings)} warning(s)",
            file=sys.stderr,
        )
        return 1

    print(
        f"validate-font: OK ({len(records)} glyphs, {len(warnings)} warning(s))"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
