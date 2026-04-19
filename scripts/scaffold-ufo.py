#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scaffold-ufo.py — create src/hildegard-neumes.ufo/ from the 19-atom contract.

Reads src/glyph-names.json and src/widths.json and emits a valid UFO3
directory. Each contract glyph is authored as either:

- a **final geometric shape** (the seven tradition-agnostic atoms —
  divisio family, virgula, pes_line, flexa_line). Tradition-agnostic
  shapes adopt Bravura SMuFL conventions per ADR-0009; compositional
  primitives (pes_line, flexa_line) keep their own conventions since
  they have no SMuFL equivalent; or
- a **placeholder rectangle** (the twelve calligraphic atoms) sized
  to fit inside the advance width, which a designer later replaces
  in FontForge per docs/paleographic_drawing_briefs.md §§ 1–12.

Having both live in one deterministic script means re-running
``just rescaffold-ufo`` regenerates the seven geometric glyphs to
their canonical shapes and resets the twelve calligraphic
placeholders — exactly what you want after a contract change. The
script is the single source of truth for every non-calligraphic
shape in the font.

The output UFO3 opens cleanly in FontForge (or any UFO3-aware tool),
builds to a valid OTF via scripts/build-font.sh, and exercises the
full scripts/generate-rhena-glyphs.py codegen pipeline end-to-end.

Design units (du) are the 1000-UPM font units. SMuFL uses staff
spaces as its native measurement (1 ss = 0.25 em = 250 du in our
scale); we use du for paths and quote staff spaces when referencing
SMuFL conventions.

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
# SMuFL convention is a ≥ 2 em vertical box so tall music glyphs don't
# clip. Bravura/Leland/Gootville use 2012/-2012 exactly; Petaluma uses
# 1000/-1000. We round Bravura's value for cleanliness — 2 em even,
# still SMuFL-conformant. See docs/adr/ADR-0009-smufl-alignment.md.
ASCENT = 2000
DESCENT = -2000  # signed, font-native Y-up convention

# ---------------------------------------------------------------------------
# Phase A: placeholder bboxes for the twelve calligraphic atoms
# ---------------------------------------------------------------------------
#
# Keyed by font_name. Tuple: (xmin, ymin, xmax, ymax). A designer
# replaces these with real calligraphic shapes in FontForge per
# docs/paleographic_drawing_briefs.md §§ 1–12. Bboxes are conservative
# — they fit inside the post-review advance widths and hint at the
# intended vertical extent from the brief (tall virga stem, tall-left
# pressus asymmetry, directional liquescent tails).
PLACEHOLDER_BBOX: dict[str, tuple[int, int, int, int]] = {
    "rh_punctum":            (-100,  -40,  100,   40),
    "rh_virga":              ( -30, -540,   30,   40),
    "rh_punctum_inclinatum": ( -50,  -35,   50,   35),
    "rh_quilisma":           ( -75,  -25,   75,   25),
    "rh_oriscus":            ( -85,  -35,   85,   35),
    "rh_strophicus":         ( -70,  -35,   70,   35),
    "rh_pressus":            (-130, -200,  130,   80),
    "rh_liquescent_asc":     ( -65,  -30,   65,  240),
    "rh_liquescent_desc":    ( -65, -240,   65,   30),
    "rh_deminutum":          ( -40,  -30,   40,   30),
    "rh_c_clef":             (   5,    0,  105,  250),
    "rh_f_clef":             (   5,    0,  155,  250),
}


# ---------------------------------------------------------------------------
# Final shapes for the seven geometric atoms (SMuFL-aligned)
# ---------------------------------------------------------------------------
#
# Each entry is a list of contours; each contour is a list of
# (x, y) points. Counter-clockwise winding in y-up coordinates
# marks a filled interior (standard TrueType/CFF fill rule).
#
# **Tradition-agnostic glyphs** (divisio family, virgula) adopt
# Bravura's SMuFL conventions per ADR-0009:
# - staff space height = 250 du
# - y=0 is the staff midline
# - divisio_minima and virgula sit **above** the staff (y ∈ [+250, +500])
# - divisio_maior/maxima/finalis are **centered** on the midline
# - dimensions match Bravura's bravura_metadata.json bboxes
# - y-positioning is **path-intrinsic** — the outline itself carries
#   the SMuFL y-offsets so a consumer embedding the path gets correct
#   placement with no additional transform
#
# Source: Bravura (SMuFL reference font) at
# `reference-repos/musescore/fonts/bravura/bravura_metadata.json`.
# We write off the abandoned `rhineland.rs` conventions (2x heights,
# y=0 baselines, 12-du virgula) — those were unvalidated placeholder
# decisions in code Rhena threw away.
#
# **Compositional primitives** (`rh_pes_line`, `rh_flexa_line`) have
# no SMuFL equivalent; they keep their own conventions for Rhena's
# resolver (rotated/scaled at render time).
GEOMETRIC_FINAL_SHAPES: dict[str, list[list[tuple[int, int]]]] = {
    "rh_divisio_minima": [
        # 1 staff space, positioned above top line (SMuFL: [1.0, 2.0] ss)
        [(0, 250), (16, 250), (16, 500), (0, 500)],
    ],
    "rh_divisio_maior": [
        # 2 staff spaces, centered on midline (SMuFL: [-1.0, 1.0] ss)
        [(0, -250), (16, -250), (16, 250), (0, 250)],
    ],
    "rh_divisio_maxima": [
        # 3 staff spaces, centered (SMuFL: [-1.5, 1.5] ss)
        [(0, -375), (16, -375), (16, 375), (0, 375)],
    ],
    "rh_divisio_finalis": [
        # Two 16-du bars separated by an 88-du gap (total 120 du wide),
        # same height as divisio_maxima (3 staff spaces, centered).
        # Matches Bravura chantDivisioFinalis bbox SW=[0,-1.5] NE=[0.48,1.5].
        [(0, -375), (16, -375), (16, 375), (0, 375)],         # left bar
        [(104, -375), (120, -375), (120, 375), (104, 375)],   # right bar
    ],
    "rh_virgula": [
        # Breath mark above the top line. Bravura chantVirgula width 91 du,
        # y ∈ [+255, +500] (just above the staff). Final shape in Bravura
        # is a curvy hook; for v1 we use a rectangle at the same bbox —
        # good-enough placeholder for SMuFL-compatible positioning.
        [(0, 255), (91, 255), (91, 500), (0, 500)],
    ],
    "rh_pes_line": [
        # Thin ascending connector, one staff space tall, LSB-0. No SMuFL
        # equivalent — compositional primitive; Rhena's resolver rotates
        # and scales it at render time to span the interval of any pes.
        [(0, 0), (12, 0), (12, 250), (0, 250)],
    ],
    "rh_flexa_line": [
        # Descending diagonal parallelogram, 172 du wide, 260 du tall,
        # 12 du thick. No SMuFL equivalent — compositional primitive.
        # Top edge at y=0, x ∈ [0, 12]; bottom edge at y=-260,
        # x ∈ [160, 172]. CCW from bottom-left corner.
        [(160, -260), (172, -260), (12, 0), (0, 0)],
    ],
}


def _assert_contract_coverage(contract_glyph_names: list[str]) -> None:
    """Every contract glyph must appear in exactly one shape table."""
    placeholder = set(PLACEHOLDER_BBOX)
    geometric = set(GEOMETRIC_FINAL_SHAPES)
    both = placeholder & geometric
    if both:
        raise RuntimeError(
            f"glyph(s) defined in both PLACEHOLDER_BBOX and "
            f"GEOMETRIC_FINAL_SHAPES: {sorted(both)}. Each glyph belongs "
            f"in exactly one table."
        )
    contract = set(contract_glyph_names)
    uncovered = contract - (placeholder | geometric)
    if uncovered:
        raise RuntimeError(
            f"contract glyph(s) missing from both shape tables: "
            f"{sorted(uncovered)}. Add to PLACEHOLDER_BBOX (calligraphic) "
            f"or GEOMETRIC_FINAL_SHAPES (geometric)."
        )
    extra = (placeholder | geometric) - contract
    if extra:
        raise RuntimeError(
            f"shape table(s) reference glyph(s) not in the contract: "
            f"{sorted(extra)}. Remove them or add to src/glyph-names.json."
        )


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
            "Seven tradition-agnostic atoms (divisio family, virgula, "
            "pes_line, flexa_line) ship as final shapes per ADR-0009. "
            "Twelve calligraphic atoms start as placeholder rectangles "
            "and are authored in FontForge per "
            "docs/paleographic_drawing_briefs.md."
        ),
        # --- staff-space guidelines (horizontal lines at ±0.5, ±1, ±1.5,
        # ±2, ±2.5, ±3 staff spaces from the pitch-anchor baseline y=0).
        # 1 ss = 250 du in our 1000-UPM SMuFL-conformant scale (per
        # ADR-0009). Shown in all glyph editors as a staff-relative
        # scaffold so calligraphic atoms are drawn to the correct
        # height on first pass. Whole staff-spaces are bolder; half
        # positions (space between lines) are fainter.
        # Horizontal guidelines specify only `y` per UFO3 spec; `angle` is
        # only valid when both x and y are given (for oblique guides).
        "guidelines": [
            {"y":  750, "name": "+3 ss",   "color": "0.6,0.6,0.9,0.5"},
            {"y":  625, "name": "+2.5 ss", "color": "0.8,0.8,0.95,0.35"},
            {"y":  500, "name": "+2 ss",   "color": "0.6,0.6,0.9,0.6"},
            {"y":  375, "name": "+1.5 ss", "color": "0.8,0.8,0.95,0.4"},
            {"y":  250, "name": "+1 ss",   "color": "0.5,0.5,0.9,0.7"},
            {"y":  125, "name": "+0.5 ss", "color": "0.8,0.8,0.95,0.45"},
            {"y": -125, "name": "-0.5 ss", "color": "0.8,0.8,0.95,0.45"},
            {"y": -250, "name": "-1 ss",   "color": "0.5,0.5,0.9,0.7"},
            {"y": -375, "name": "-1.5 ss", "color": "0.8,0.8,0.95,0.4"},
            {"y": -500, "name": "-2 ss",   "color": "0.6,0.6,0.9,0.6"},
            {"y": -625, "name": "-2.5 ss", "color": "0.8,0.8,0.95,0.35"},
            {"y": -750, "name": "-3 ss",   "color": "0.6,0.6,0.9,0.5"},
        ],
    }


# ---------------------------------------------------------------------------
# GLIF rendering
# ---------------------------------------------------------------------------


def render_glif(
    glyph_name: str,
    advance_width: int,
    unicode_codepoint: str | None,
    contours: list[list[tuple[int, int]]],
) -> str:
    """Render a .glif v2 XML string from one or more closed contours.

    ``contours`` is a list of contour definitions; each contour is a
    list of integer (x, y) points. Every point is written with
    ``type="line"`` — no curves at the scaffold stage. Winding
    direction is the caller's responsibility (counter-clockwise fills,
    clockwise cuts; TrueType/CFF convention).

    ``unicode_codepoint`` is a "U+NNNN" string or None. None means the
    glyph has no cmap entry and is accessed by glyph name only —
    applies to ``rh_pes_line``, ``rh_flexa_line``, and ``.notdef``.
    """
    unicode_line = ""
    if unicode_codepoint:
        hex_digits = unicode_codepoint.upper().removeprefix("U+")
        unicode_line = f'  <unicode hex="{hex_digits}"/>\n'

    contour_xml_parts: list[str] = []
    for contour in contours:
        points_xml = "\n".join(
            f'      <point x="{x}" y="{y}" type="line"/>' for x, y in contour
        )
        contour_xml_parts.append(f"    <contour>\n{points_xml}\n    </contour>")
    contours_xml = "\n".join(contour_xml_parts)

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<glyph name="{glyph_name}" format="2">\n'
        f'  <advance width="{advance_width}"/>\n'
        f'{unicode_line}'
        '  <outline>\n'
        f'{contours_xml}\n'
        '  </outline>\n'
        '</glyph>\n'
    )


def contours_for(glyph_name: str) -> list[list[tuple[int, int]]]:
    """Return the contour list for a contract glyph.

    Final geometric shapes from GEOMETRIC_FINAL_SHAPES take precedence;
    otherwise falls back to a single CCW rectangle derived from
    PLACEHOLDER_BBOX. Raises KeyError if the glyph isn't covered by
    either table — :func:`_assert_contract_coverage` catches this
    earlier with a clearer message, but the fallback is defensive.
    """
    if glyph_name in GEOMETRIC_FINAL_SHAPES:
        return GEOMETRIC_FINAL_SHAPES[glyph_name]
    xmin, ymin, xmax, ymax = PLACEHOLDER_BBOX[glyph_name]
    # Counter-clockwise in y-up: BL -> BR -> TR -> TL.
    return [[(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]]


def render_notdef_glif() -> str:
    """The conventional .notdef: a rectangular frame with empty interior.

    Outer contour counter-clockwise (filled); inner contour clockwise
    (subtracts, producing the hollow frame). Width 500, height spans the
    full ascender box.
    """
    return render_glif(
        glyph_name=".notdef",
        advance_width=500,
        unicode_codepoint=None,
        contours=[
            # Outer frame, counter-clockwise (fills)
            [(50, 0), (450, 0), (450, 700), (50, 700)],
            # Inner cutout, clockwise (subtracts — opposite winding)
            [(100, 50), (100, 650), (400, 650), (400, 50)],
        ],
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

    contract_names = [g["font_name"] for g in names_raw["glyphs"]]
    _assert_contract_coverage(contract_names)

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

    # The 19 contract glyphs. Seven are authored as final geometric
    # shapes from GEOMETRIC_FINAL_SHAPES; the other twelve as
    # placeholder rectangles from PLACEHOLDER_BBOX. Coverage guard in
    # _assert_contract_coverage ensures exactly one match per glyph.
    for entry in names_raw["glyphs"]:
        name = entry["font_name"]
        if name not in widths:
            raise KeyError(f"widths.json missing entry for {name!r}")

        filename = glif_filename(name)
        (glyphs_dir / filename).write_text(
            render_glif(
                glyph_name=name,
                advance_width=widths[name],
                unicode_codepoint=entry.get("smufl_codepoint"),
                contours=contours_for(name),
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
