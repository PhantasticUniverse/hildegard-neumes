#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scaffold-ufo.py — create src/hildegard-neumes.ufo/ from the 19-atom contract.

Reads src/glyph-names.json and src/widths.json and emits a valid UFO3
directory with all 19 Rhineland atom glyph slots populated with
placeholder rectangle outlines at their declared advance widths.

The output UFO3 opens cleanly in FontForge (or any UFO3-aware tool),
builds to a valid OTF via scripts/build-font.sh, and exercises the full
scripts/generate-rhena-glyphs.py codegen pipeline end-to-end. The
placeholder shapes preserve the width contract and are distinct enough
at a glance to identify glyphs in FontForge's glyph grid. The final
calligraphic shapes are the designer's job (Phase C). Phase B upgrades
the seven geometric glyphs (divisio bars, virgula, connector lines) to
their final shapes in pure Python.

This is Phase A per the 2026-04-19 plan. Placeholder bboxes fit
conservatively inside the post-review advance widths (src/widths.json
— `rh_virga` 90, `rh_liquescent_asc`/`_desc` 160) so validate-font.py's
bbox-vs-advance check passes, and hint at the final registration where
the paleographic brief specifies it (tall virga stem, tall-left
pressus, directional liquescent tails).

Usage:
    python scripts/scaffold-ufo.py              # fails if UFO exists
    python scripts/scaffold-ufo.py --force      # overwrite existing UFO
    python scripts/scaffold-ufo.py --out PATH   # write to alternate path
"""

from __future__ import annotations

import argparse
import json
import plistlib
import shutil
import sys
from pathlib import Path

EM = 1000
ASCENT = 800
DESCENT = -200  # signed, font-native Y-up convention

# Placeholder bbox per glyph, keyed by font_name. Tuple: (xmin, ymin,
# xmax, ymax). Chosen per docs/planning/width-review-2026-04-14.md § 1,
# conservatively inside the post-review advance widths. Centred-origin
# glyphs straddle x=0; LSB-0 glyphs sit at x >= 2 (leaves a 2-unit LSB
# margin so the advance check has slack). Heights hint at the intended
# vertical extent from the paleographic briefs without committing to
# final shapes.
PLACEHOLDER_BBOX: dict[str, tuple[int, int, int, int]] = {
    # Centred-origin glyphs (convention inherited from abandoned attempt;
    # v1 preserves the mix; v2 may unify to LSB-0).
    "rh_punctum":            (-100,  -40,  100,   40),
    "rh_virga":              ( -35,  -40,   35,  500),
    "rh_punctum_inclinatum": ( -50,  -35,   50,   35),
    "rh_quilisma":           ( -75,  -25,   75,   25),
    "rh_oriscus":            ( -85,  -35,   85,   35),
    "rh_strophicus":         ( -70,  -35,   70,   35),
    "rh_pressus":            (-130, -200,  130,   80),
    "rh_liquescent_asc":     ( -65,  -30,   65,  240),
    "rh_liquescent_desc":    ( -65, -240,   65,   30),
    "rh_deminutum":          ( -40,  -30,   40,   30),
    # LSB-0 glyphs (rh_pes_line redrawn LSB-0 per width-review § 5.6).
    "rh_c_clef":             (   5,    0,  105,  250),
    "rh_f_clef":             (   5,    0,  155,  250),
    "rh_divisio_minima":     (   2,    0,   14,  125),
    "rh_divisio_maior":      (   2,    0,   14,  500),
    "rh_divisio_maxima":     (   2, -125,   14,  625),
    "rh_divisio_finalis":    (   2,    0,   54,  500),
    "rh_virgula":            (   2,  400,   10,  500),
    "rh_pes_line":           (   2,    0,   10,  125),
    "rh_flexa_line":         (   2,    0,  170,  125),
}


# ---------------------------------------------------------------------------
# Filename sanitization (minimal UFO3 rules for our specific glyph set)
# ---------------------------------------------------------------------------

# UFO3 maps glyph names to filenames per rules at
# https://unifiedfontobject.org/versions/ufo3/conventions/. We hand-roll
# a minimal subset because our names are predictable lowercase ASCII
# with no collisions — the full ruleset (case folding, reserved Windows
# names, length truncation, collision disambiguation) is overkill for
# 20 glyphs. If future glyphs break the assumption the guard below
# fires with a clear error rather than corrupting the UFO.


def glif_filename(glyph_name: str) -> str:
    """Return the .glif filename for a glyph, per a minimal UFO3 rule set.

    Handles only what the 19-atom contract + ``.notdef`` requires:
    - leading-dot replacement (`.notdef` → `_notdef.glif`)
    - everything else passes through unchanged (ASCII lowercase + underscore)

    Raises ValueError on any name that would need fuller sanitization, so
    a future contract expansion cannot silently produce a broken UFO.
    """
    if glyph_name == ".notdef":
        return "_notdef.glif"
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_")
    if not glyph_name or not set(glyph_name).issubset(allowed):
        raise ValueError(
            f"glyph name {glyph_name!r} requires non-minimal UFO3 filename "
            f"sanitization (uppercase, punctuation, or non-ASCII). Extend "
            f"glif_filename() or pull in fontTools.ufoLib.filenames."
        )
    return f"{glyph_name}.glif"


# ---------------------------------------------------------------------------
# Plist helpers
# ---------------------------------------------------------------------------


def write_plist(path: Path, obj) -> None:
    """Write a plist file in XML format (UFO3 mandates XML, not binary)."""
    path.write_bytes(plistlib.dumps(obj, fmt=plistlib.FMT_XML, sort_keys=True))


def fontinfo_dict(version: str) -> dict:
    """Build the fontinfo.plist content.

    Keys per the UFO3 fontinfo spec. SMuFL/Bravura conventions for the
    OS/2 and hhea metrics (em=1000, ascender=800, descender=-200,
    linegap=0). Panose class 5 = symbol/pictorial.
    """
    return {
        # --- identification
        "familyName": "Hildegard Neumes",
        "styleName": "Regular",
        "styleMapFamilyName": "Hildegard Neumes",
        "styleMapStyleName": "regular",
        # --- version / provenance
        "versionMajor": 0,
        "versionMinor": 1,
        "copyright": (
            "Copyright 2026 Hildegard Neumes Project. "
            "Licensed under the SIL Open Font License 1.1."
        ),
        "trademark": (
            'Hildegard Neumes is a Reserved Font Name under the SIL OFL 1.1.'
        ),
        # --- metrics (SMuFL / Bravura convention)
        "unitsPerEm": EM,
        "ascender": ASCENT,
        "descender": DESCENT,
        "capHeight": 700,  # not meaningful for a symbol font; included for validators
        "xHeight": 500,
        "italicAngle": 0.0,
        # --- OpenType name table
        "openTypeNameDesigner": "Hildegard Neumes Project",
        "openTypeNameManufacturer": "Hildegard Neumes Project",
        "openTypeNameLicense": (
            "This Font Software is licensed under the SIL Open Font "
            "License, Version 1.1. See OFL.txt in the source distribution."
        ),
        "openTypeNameLicenseURL": "https://openfontlicense.org/",
        # --- OS/2
        "openTypeOS2WidthClass": 5,   # normal
        "openTypeOS2WeightClass": 400,  # regular
        "openTypeOS2TypoAscender": ASCENT,
        "openTypeOS2TypoDescender": DESCENT,
        "openTypeOS2TypoLineGap": 0,
        "openTypeOS2WinAscent": ASCENT,
        "openTypeOS2WinDescent": abs(DESCENT),  # winDescent is unsigned
        "openTypeOS2Panose": [5, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 5 = pictorial/symbol
        "openTypeOS2Selection": [7],  # UseTypoMetrics bit
        # --- hhea
        "openTypeHheaAscender": ASCENT,
        "openTypeHheaDescender": DESCENT,
        "openTypeHheaLineGap": 0,
        # --- PostScript
        "postscriptFontName": "HildegardNeumes-Regular",
        "postscriptFullName": "Hildegard Neumes Regular",
        "postscriptUnderlineThickness": 50,
        "postscriptUnderlinePosition": -100,
        # --- note field for humans
        "note": (
            f"Scaffolded from the 19-atom contract at v{version}. "
            "Placeholder rectangles — Phase A. Final calligraphic shapes "
            "authored per docs/paleographic_drawing_briefs.md."
        ),
    }


# ---------------------------------------------------------------------------
# GLIF rendering
# ---------------------------------------------------------------------------


def render_glif(
    glyph_name: str,
    advance_width: int,
    unicode_codepoint: str | None,
    bbox: tuple[int, int, int, int],
) -> str:
    """Render a .glif v2 XML string for one placeholder glyph.

    Outline is a single counter-clockwise closed rectangle sized to the
    bbox tuple (xmin, ymin, xmax, ymax). All four corners are line points
    (no curves). Winding matches the filled-interior convention for
    TrueType/CFF.

    `unicode_codepoint` is a "U+NNNN" string or None; None means the glyph
    has no cmap entry (accessed by glyph name only — applies to
    `rh_pes_line`, `rh_flexa_line`, and `.notdef`).
    """
    xmin, ymin, xmax, ymax = bbox
    unicode_line = ""
    if unicode_codepoint:
        hex_digits = unicode_codepoint.upper().removeprefix("U+")
        unicode_line = f'  <unicode hex="{hex_digits}"/>\n'

    # Counter-clockwise in y-up coords: BL -> BR -> TR -> TL
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<glyph name="{glyph_name}" format="2">\n'
        f'  <advance width="{advance_width}"/>\n'
        f'{unicode_line}'
        '  <outline>\n'
        '    <contour>\n'
        f'      <point x="{xmin}" y="{ymin}" type="line"/>\n'
        f'      <point x="{xmax}" y="{ymin}" type="line"/>\n'
        f'      <point x="{xmax}" y="{ymax}" type="line"/>\n'
        f'      <point x="{xmin}" y="{ymax}" type="line"/>\n'
        '    </contour>\n'
        '  </outline>\n'
        '</glyph>\n'
    )


def render_notdef_glif() -> str:
    """The conventional .notdef: a rectangular frame with empty interior.

    Outer contour counter-clockwise (filled); inner contour clockwise
    (subtracts, producing the hollow frame). Width 500, height spans the
    full ascender box.
    """
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<glyph name=".notdef" format="2">\n'
        '  <advance width="500"/>\n'
        '  <outline>\n'
        # Outer frame, counter-clockwise
        '    <contour>\n'
        '      <point x="50"  y="0"   type="line"/>\n'
        '      <point x="450" y="0"   type="line"/>\n'
        '      <point x="450" y="700" type="line"/>\n'
        '      <point x="50"  y="700" type="line"/>\n'
        '    </contour>\n'
        # Inner cutout, clockwise (opposite winding = subtracted)
        '    <contour>\n'
        '      <point x="100" y="50"  type="line"/>\n'
        '      <point x="100" y="650" type="line"/>\n'
        '      <point x="400" y="650" type="line"/>\n'
        '      <point x="400" y="50"  type="line"/>\n'
        '    </contour>\n'
        '  </outline>\n'
        '</glyph>\n'
    )


# ---------------------------------------------------------------------------
# Main scaffolding
# ---------------------------------------------------------------------------


def scaffold(
    out_path: Path,
    names_map_path: Path,
    widths_path: Path,
    version: str,
) -> int:
    """Produce the full UFO3 at ``out_path``. Returns the glyph count."""
    names_raw = json.loads(names_map_path.read_text(encoding="utf-8"))
    widths_raw = json.loads(widths_path.read_text(encoding="utf-8"))
    widths = widths_raw["widths"]

    out_path.mkdir(parents=True)

    # ---- top-level UFO3 plists
    write_plist(out_path / "metainfo.plist", {
        "creator": "com.github.hildegard-neumes.scaffold-ufo",
        "formatVersion": 3,
    })
    write_plist(out_path / "fontinfo.plist", fontinfo_dict(version))
    write_plist(out_path / "layercontents.plist", [
        ["public.default", "glyphs"],
    ])

    # public.glyphOrder fixes OpenType glyph ordering (.notdef first, then
    # contract order). Without this, FontForge may re-sort by cmap entries
    # and the generated rhineland_glyphs.rs would show a different order
    # than ALL_GLYPHS, breaking the codegen contract.
    glyph_order = [".notdef"] + [g["font_name"] for g in names_raw["glyphs"]]
    write_plist(out_path / "lib.plist", {
        "public.glyphOrder": glyph_order,
    })

    # ---- default layer
    glyphs_dir = out_path / "glyphs"
    glyphs_dir.mkdir()

    contents: dict[str, str] = {}

    # .notdef first so it's at glyph index 0 in the OTF
    notdef_filename = glif_filename(".notdef")
    (glyphs_dir / notdef_filename).write_text(render_notdef_glif(), encoding="utf-8")
    contents[".notdef"] = notdef_filename

    # The 19 contract glyphs
    for entry in names_raw["glyphs"]:
        name = entry["font_name"]
        if name not in widths:
            raise KeyError(f"widths.json missing entry for {name!r}")
        if name not in PLACEHOLDER_BBOX:
            raise KeyError(f"PLACEHOLDER_BBOX missing entry for {name!r}")

        filename = glif_filename(name)
        (glyphs_dir / filename).write_text(
            render_glif(
                glyph_name=name,
                advance_width=widths[name],
                unicode_codepoint=entry.get("smufl_codepoint"),
                bbox=PLACEHOLDER_BBOX[name],
            ),
            encoding="utf-8",
        )
        contents[name] = filename

    write_plist(glyphs_dir / "contents.plist", contents)

    return len(contents)


def main(argv: list[str] | None = None) -> int:
    project_root = Path(__file__).resolve().parent.parent

    parser = argparse.ArgumentParser(
        description="Scaffold src/hildegard-neumes.ufo/ from the 19-atom contract.",
    )
    parser.add_argument(
        "--out", type=Path,
        default=project_root / "src" / "hildegard-neumes.ufo",
        help="UFO3 output directory (default: src/hildegard-neumes.ufo/).",
    )
    parser.add_argument(
        "--names-map", type=Path,
        default=project_root / "src" / "glyph-names.json",
    )
    parser.add_argument(
        "--widths-table", type=Path,
        default=project_root / "src" / "widths.json",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Remove any existing UFO at --out before scaffolding.",
    )
    args = parser.parse_args(argv)

    if args.out.exists():
        if not args.force:
            sys.stderr.write(
                f"error: {args.out} already exists. Pass --force to overwrite.\n"
            )
            return 2
        shutil.rmtree(args.out)

    for p in (args.names_map, args.widths_table):
        if not p.is_file():
            sys.stderr.write(f"error: required input not found: {p}\n")
            return 2

    version_file = project_root / "VERSION"
    version = version_file.read_text(encoding="utf-8").strip() if version_file.is_file() else "0.0.0-dev"

    count = scaffold(
        out_path=args.out,
        names_map_path=args.names_map,
        widths_path=args.widths_table,
        version=version,
    )

    print(f"Scaffolded {count} glyphs to {args.out}")
    print("Next:")
    print(f"  1. open {args.out} in FontForge (or any UFO3-aware editor)")
    print(f"  2. redraw glyphs per docs/paleographic_drawing_briefs.md")
    print(f"  3. `just build-font` to export build/hildegard-neumes.otf")
    print(f"  4. `just generate-rhena` to regenerate the Rhena consumer file")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
