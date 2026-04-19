#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-rhena-glyphs.py — emit rhineland_glyphs.rs for Rhena/Viriditas

Reads the Hildegard Neumes OTF, extracts per-glyph SVG path strings and
advance widths, validates them against a frozen widths contract, and emits
a Rust source file matching Rhena's existing `Glyph { name, path, width }`
struct.

Usage:
    python scripts/generate-rhena-glyphs.py \\
        --in build/hildegard-neumes.otf \\
        --names-map src/glyph-names.json \\
        --widths-table src/widths.json \\
        --out generated/rhineland_glyphs.rs

Exit codes:
    0  success
    1  validation failure (missing glyph, width mismatch, malformed path)
    2  I/O or CLI error

See ADR-0009 in Rhena (staged in hildegard-neumes/docs/adr/) and
rhena_integration_plan.md § 3 in the font repo for the contract this
script implements.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        "error: fontTools is required. Install with `pip install fonttools`.\n"
        f"       ({exc})\n"
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Constants and contracts
# ---------------------------------------------------------------------------

# Authoritative glyph emission order. Must match Rhena's existing rhineland.rs
# ALL_GLYPHS slice order. This list is the single source of truth for
# ordering; glyph-names.json is validated to match it exactly.
GLYPH_ORDER: tuple[str, ...] = (
    "PUNCTUM",
    "VIRGA",
    "PUNCTUM_INCLINATUM",
    "QUILISMA",
    "ORISCUS",
    "STROPHICUS",
    "PRESSUS",
    "LIQUESCENT_ASC",
    "LIQUESCENT_DESC",
    "DEMINUTUM",
    "C_CLEF",
    "F_CLEF",
    "DIVISIO_MINIMA",
    "DIVISIO_MAIOR",
    "DIVISIO_MAXIMA",
    "DIVISIO_FINALIS",
    "VIRGULA",
    "PES_LINE",
    "FLEXA_LINE",
)

RUST_CONST_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
FONT_NAME_RE = re.compile(r"^rh_[a-z0-9_]+$")

# SVG path tokens we accept after normalization. Anything else is a hard
# error — Rhena's SVG backend only implements these five commands.
ALLOWED_COMMANDS = frozenset("MLCQZ")

DEFAULT_VERSION = "0.1.0-dev"
DEFAULT_WIDTH_TOLERANCE = 1  # font units


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GlyphRecord:
    rust_const: str
    font_name: str
    smufl: str | None
    smufl_codepoint: str | None
    doc: str


@dataclass(frozen=True)
class ExtractedGlyph:
    rust_const: str
    font_name: str
    svg_path: str  # normalized: absolute uppercase integer commands
    width: int
    doc: str


# ---------------------------------------------------------------------------
# Contract loading
# ---------------------------------------------------------------------------


def load_contract(
    names_map_path: Path, widths_path: Path
) -> tuple[list[GlyphRecord], dict[str, int], int]:
    """Load and validate glyph-names.json and widths.json.

    Returns (glyph_records_in_order, widths_by_font_name, tolerance).

    Raises SystemExit(1) on any contract violation.
    """
    try:
        names_raw = json.loads(names_map_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _die(f"cannot read names map {names_map_path}: {exc}", code=2)

    try:
        widths_raw = json.loads(widths_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _die(f"cannot read widths table {widths_path}: {exc}", code=2)

    if names_raw.get("version") != 1:
        _die(f"{names_map_path}: expected version 1")
    if widths_raw.get("version") != 1:
        _die(f"{widths_path}: expected version 1")

    raw_glyphs = names_raw.get("glyphs")
    if not isinstance(raw_glyphs, list):
        _die(f"{names_map_path}: `glyphs` must be a list")

    records: list[GlyphRecord] = []
    seen_const: set[str] = set()
    seen_font: set[str] = set()
    for i, entry in enumerate(raw_glyphs):
        if not isinstance(entry, dict):
            _die(f"{names_map_path}[{i}]: entry is not an object")
        rc = entry.get("rust_const", "")
        fn = entry.get("font_name", "")
        if not RUST_CONST_RE.match(rc):
            _die(f"{names_map_path}[{i}]: bad rust_const {rc!r}")
        if not FONT_NAME_RE.match(fn):
            _die(f"{names_map_path}[{i}]: bad font_name {fn!r}")
        if rc in seen_const:
            _die(f"{names_map_path}: duplicate rust_const {rc}")
        if fn in seen_font:
            _die(f"{names_map_path}: duplicate font_name {fn}")
        seen_const.add(rc)
        seen_font.add(fn)
        records.append(
            GlyphRecord(
                rust_const=rc,
                font_name=fn,
                smufl=entry.get("smufl"),
                smufl_codepoint=entry.get("smufl_codepoint"),
                doc=entry.get("doc", ""),
            )
        )

    # Ordering check: glyph-names.json must match GLYPH_ORDER exactly.
    actual_order = tuple(r.rust_const for r in records)
    if actual_order != GLYPH_ORDER:
        missing = set(GLYPH_ORDER) - set(actual_order)
        extra = set(actual_order) - set(GLYPH_ORDER)
        _die(
            f"{names_map_path}: glyph order does not match GLYPH_ORDER.\n"
            f"  missing: {sorted(missing)}\n"
            f"  extra:   {sorted(extra)}\n"
            f"  If adding a glyph, update GLYPH_ORDER in this script too."
        )

    widths = widths_raw.get("widths")
    if not isinstance(widths, dict):
        _die(f"{widths_path}: `widths` must be an object")

    for r in records:
        if r.font_name not in widths:
            _die(f"{widths_path}: missing width for {r.font_name}")
        if not isinstance(widths[r.font_name], int):
            _die(f"{widths_path}: width for {r.font_name} must be an integer")

    expected_font_names = {r.font_name for r in records}
    for extra_name in sorted(set(widths) - expected_font_names):
        sys.stderr.write(
            f"warning: {widths_path}: extra width entry {extra_name!r} not in "
            f"glyph-names.json (will be ignored)\n"
        )

    tolerance = widths_raw.get("tolerance", DEFAULT_WIDTH_TOLERANCE)
    if not isinstance(tolerance, int) or tolerance < 0:
        _die(f"{widths_path}: tolerance must be a non-negative integer")

    return records, {k: int(v) for k, v in widths.items()}, tolerance


# ---------------------------------------------------------------------------
# Font extraction
# ---------------------------------------------------------------------------


def extract_glyph(font: TTFont, glyph_name: str) -> tuple[str, int]:
    """Extract (svg_path_string, advance_width) for one glyph.

    - advance_width is read from the `hmtx` table directly (font units).
    - svg_path_string is produced by SVGPathPen walking the glyph outline,
      then normalized to absolute uppercase integer commands.
    - Y is NOT flipped (Rhena's SVG backend handles the flip).
    - Bearings are NOT applied (we author with LSB = 0).
    """
    glyph_set = font.getGlyphSet()
    if glyph_name not in glyph_set:
        raise KeyError(f"glyph {glyph_name!r} not in font glyph set")

    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    raw_path = pen.getCommands()

    # fontTools' SVGPathPen already emits absolute uppercase commands, but
    # we run it through normalize_path() anyway to (a) round floats to ints,
    # (b) tighten whitespace, (c) defend against future fontTools changes.
    path = normalize_path(raw_path)

    hmtx = font["hmtx"].metrics
    if glyph_name not in hmtx:
        raise KeyError(f"glyph {glyph_name!r} has no hmtx entry")
    advance_width, _lsb = hmtx[glyph_name]
    return path, int(advance_width)


# ---------------------------------------------------------------------------
# Path normalization
# ---------------------------------------------------------------------------

# Tokenizer for SVG path data. Handles signed decimals, scientific notation,
# and collapsed-sign constructs like "10-5" (= "10 -5"). fontTools does not
# produce those, but we tokenize defensively so this helper is reusable.
_PATH_TOKEN_RE = re.compile(
    r"""
    ([MmLlHhVvCcSsQqTtAaZz])                # command letter
    | (-?\d*\.\d+(?:[eE][+-]?\d+)?)         # float:   .5, 1.2, 1e-3
    | (-?\d+(?:[eE][+-]?\d+)?)              # int:     1, -3
    """,
    re.VERBOSE,
)

# Argument arities for each command (count of numbers per coordinate set).
_ARITY = {
    "M": 2, "L": 2, "H": 1, "V": 1,
    "C": 6, "S": 4, "Q": 4, "T": 2,
    "A": 7, "Z": 0,
}


def _round_half_up(x: float) -> int:
    """Round-half-up to nearest int, matching FontForge's save-time snap.

    Python's built-in round() uses banker's rounding (round-half-to-even),
    which oscillates between runs and can produce spurious diffs in
    generated output. FontForge snaps to the integer grid on save via
    round-half-up, so we mimic that here.
    """
    return int(math.floor(x + 0.5)) if x >= 0 else -int(math.floor(-x + 0.5))


def normalize_path(path_str: str) -> str:
    """Normalize an SVG path to absolute uppercase integer commands.

    Accepts any valid SVG path data. Produces a string using only
    {M, L, C, Q, Z}. Raises ValueError on any input that cannot be
    expressed in that vocabulary (arcs, for example).

    Algorithm:
      1. Tokenize the input into (command, numbers...) groups.
      2. Walk the groups, tracking current point and subpath start.
      3. Convert each relative command to its absolute form by adding
         the current point. Convert H/V to L. Expand T/S to Q/C using
         the standard reflection rule. Reject A (arcs).
      4. Round all numbers to integer via _round_half_up().
      5. Emit a compact canonical string: "M x y L x y C a b c d e f Z".
         Single space separators, no trailing whitespace.
    """
    tokens = _tokenize_path(path_str)
    if not tokens:
        return ""

    out: list[str] = []
    cx = cy = 0.0  # current point
    sx = sy = 0.0  # subpath start point
    last_ctrl: tuple[float, float] | None = None

    i = 0
    n = len(tokens)
    # First token must be M or m.
    if tokens[0][0] != "cmd" or tokens[0][1] not in ("M", "m"):
        raise ValueError(f"path must start with M/m, got {tokens[0][1]!r}")

    while i < n:
        kind, val = tokens[i]
        if kind != "cmd":
            raise ValueError(f"expected command at position {i}, got {val!r}")
        cmd = val
        i += 1
        arity = _ARITY.get(cmd.upper())
        if arity is None:
            raise ValueError(f"unknown command {cmd!r}")

        if cmd.upper() == "Z":
            if out and out[-1] != "Z":
                out.append("Z")
            cx, cy = sx, sy
            last_ctrl = None
            continue

        # Consume one or more coordinate groups for this command.
        first_group = True
        while i < n and tokens[i][0] == "num":
            if i + arity > n:
                raise ValueError(f"truncated {cmd} group at token {i}")
            nums = [float(tokens[i + k][1]) for k in range(arity)]
            i += arity

            # Per SVG spec: after the first M, subsequent implicit pairs
            # are L (or l if m). After explicit L/C/Q etc., subsequent
            # groups repeat the same command.
            eff = cmd
            if cmd in ("M", "m") and not first_group:
                eff = "L" if cmd == "M" else "l"

            _emit_group(out, eff, nums, cx, cy, last_ctrl)

            # Update current point and last control point.
            cx, cy, last_ctrl = _advance_state(eff, nums, cx, cy, last_ctrl)

            if cmd in ("M", "m") and first_group:
                sx, sy = cx, cy

            first_group = False

    return " ".join(out)


def _tokenize_path(s: str) -> list[tuple[str, str]]:
    """Tokenize an SVG path string. Returns list of ("cmd"|"num", text)."""
    out: list[tuple[str, str]] = []
    for m in _PATH_TOKEN_RE.finditer(s):
        if m.group(1):
            out.append(("cmd", m.group(1)))
        elif m.group(2):
            out.append(("num", m.group(2)))
        elif m.group(3):
            out.append(("num", m.group(3)))
    return out


def _emit_group(
    out: list[str],
    cmd: str,
    nums: list[float],
    cx: float,
    cy: float,
    last_ctrl: tuple[float, float] | None,
) -> None:
    """Convert one coordinate group to canonical form and append to out."""
    rel = cmd.islower()
    up = cmd.upper()

    def abs_pt(dx: float, dy: float) -> tuple[float, float]:
        return (cx + dx, cy + dy) if rel else (dx, dy)

    if up == "M" or up == "L":
        x, y = abs_pt(nums[0], nums[1])
        out.append(f"{up} {_round_half_up(x)} {_round_half_up(y)}")

    elif up == "H":
        x = cx + nums[0] if rel else nums[0]
        out.append(f"L {_round_half_up(x)} {_round_half_up(cy)}")

    elif up == "V":
        y = cy + nums[0] if rel else nums[0]
        out.append(f"L {_round_half_up(cx)} {_round_half_up(y)}")

    elif up == "C":
        x1, y1 = abs_pt(nums[0], nums[1])
        x2, y2 = abs_pt(nums[2], nums[3])
        x, y = abs_pt(nums[4], nums[5])
        out.append(
            f"C {_round_half_up(x1)} {_round_half_up(y1)} "
            f"{_round_half_up(x2)} {_round_half_up(y2)} "
            f"{_round_half_up(x)} {_round_half_up(y)}"
        )

    elif up == "S":
        # Reflect previous cubic control through current point.
        if last_ctrl is None:
            rx1, ry1 = cx, cy
        else:
            rx1, ry1 = 2 * cx - last_ctrl[0], 2 * cy - last_ctrl[1]
        x2, y2 = abs_pt(nums[0], nums[1])
        x, y = abs_pt(nums[2], nums[3])
        out.append(
            f"C {_round_half_up(rx1)} {_round_half_up(ry1)} "
            f"{_round_half_up(x2)} {_round_half_up(y2)} "
            f"{_round_half_up(x)} {_round_half_up(y)}"
        )

    elif up == "Q":
        x1, y1 = abs_pt(nums[0], nums[1])
        x, y = abs_pt(nums[2], nums[3])
        out.append(
            f"Q {_round_half_up(x1)} {_round_half_up(y1)} "
            f"{_round_half_up(x)} {_round_half_up(y)}"
        )

    elif up == "T":
        if last_ctrl is None:
            rx1, ry1 = cx, cy
        else:
            rx1, ry1 = 2 * cx - last_ctrl[0], 2 * cy - last_ctrl[1]
        x, y = abs_pt(nums[0], nums[1])
        out.append(
            f"Q {_round_half_up(rx1)} {_round_half_up(ry1)} "
            f"{_round_half_up(x)} {_round_half_up(y)}"
        )

    elif up == "A":
        raise ValueError(
            "elliptical arc commands (A/a) are not supported by Rhena's SVG "
            "backend; redraw the offending glyph with cubics in FontForge"
        )

    else:
        raise ValueError(f"unreachable: command {cmd!r}")


def _advance_state(
    cmd: str,
    nums: list[float],
    cx: float,
    cy: float,
    last_ctrl: tuple[float, float] | None,
) -> tuple[float, float, tuple[float, float] | None]:
    """Return new (cx, cy, last_ctrl) after applying one coordinate group."""
    rel = cmd.islower()
    up = cmd.upper()

    def abs_pt(dx: float, dy: float) -> tuple[float, float]:
        return (cx + dx, cy + dy) if rel else (dx, dy)

    if up in ("M", "L"):
        x, y = abs_pt(nums[0], nums[1])
        return x, y, None
    if up == "H":
        return (cx + nums[0] if rel else nums[0]), cy, None
    if up == "V":
        return cx, (cy + nums[0] if rel else nums[0]), None
    if up == "C":
        x2, y2 = abs_pt(nums[2], nums[3])
        x, y = abs_pt(nums[4], nums[5])
        return x, y, (x2, y2)
    if up == "S":
        x2, y2 = abs_pt(nums[0], nums[1])
        x, y = abs_pt(nums[2], nums[3])
        return x, y, (x2, y2)
    if up == "Q":
        x1, y1 = abs_pt(nums[0], nums[1])
        x, y = abs_pt(nums[2], nums[3])
        return x, y, (x1, y1)
    if up == "T":
        if last_ctrl is None:
            rx1, ry1 = cx, cy
        else:
            rx1, ry1 = 2 * cx - last_ctrl[0], 2 * cy - last_ctrl[1]
        x, y = abs_pt(nums[0], nums[1])
        return x, y, (rx1, ry1)
    raise ValueError(f"unreachable in _advance_state: {cmd!r}")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_glyph(
    name: str, actual_width: int, expected_width: int, tolerance: int
) -> None:
    """Assert the font's advance width matches the contract.

    Raises SystemExit(1) with a clear message on mismatch.
    """
    if abs(actual_width - expected_width) > tolerance:
        _die(
            f"width mismatch for {name}: "
            f"font has {actual_width}, contract expects {expected_width} "
            f"(tolerance {tolerance}). Fix the glyph's sidebearings in "
            f"FontForge, or update src/widths.json if this change is "
            f"intentional (coordinate with Rhena before updating)."
        )


def validate_path_commands(font_name: str, path: str) -> None:
    """Ensure only {M L C Q Z} commands appear in a normalized path."""
    cmds = {c for c in path if c.isalpha()}
    bad = cmds - ALLOWED_COMMANDS
    if bad:
        _die(
            f"glyph {font_name!r} produced disallowed commands {sorted(bad)} "
            f"after normalization. This is a bug in normalize_path() or an "
            f"unsupported glyph feature in the OTF."
        )


def validate_glyph_presence(
    font: TTFont, expected: Iterable[str]
) -> None:
    """Fail loud on missing glyphs, warn on unexpected extras."""
    glyph_set = set(font.getGlyphOrder())
    expected = list(expected)

    missing = [n for n in expected if n not in glyph_set]
    if missing:
        _die(
            f"OTF is missing {len(missing)} expected glyph(s): {missing}. "
            f"Rebuild the font from the SFD and retry."
        )

    # Warn on unexpected glyphs, but don't fail — future-proofing.
    known_font_internals = {".notdef", ".null", "nonmarkingreturn", "space"}
    unexpected = [
        n for n in glyph_set
        if n not in expected
        and n not in known_font_internals
        and not n.startswith(".")
    ]
    if unexpected:
        sys.stderr.write(
            f"warning: OTF contains {len(unexpected)} glyph(s) not in "
            f"glyph-names.json: {sorted(unexpected)}. These will be ignored. "
            f"If they should be exposed to Rhena, add them to the contract.\n"
        )


# ---------------------------------------------------------------------------
# Rust rendering
# ---------------------------------------------------------------------------


def render_rust_file(
    glyphs: list[ExtractedGlyph],
    version: str,
    sha256_hex: str,
    timestamp_iso: str,
) -> str:
    """Produce the final `rhineland_glyphs.rs` source string.

    Deterministic given (glyphs, version, sha256_hex, timestamp_iso).
    Callers control timestamp_iso to make the output reproducible when
    SOURCE_DATE_EPOCH or --timestamp is provided.
    """
    lines: list[str] = []
    ap = lines.append

    ap(f"//! @generated by hildegard-neumes/scripts/generate-rhena-glyphs.py at {timestamp_iso}")
    ap(f"//! Source OTF: hildegard-neumes.otf (sha256: {sha256_hex})")
    ap(f"//! Font version: {version}")
    ap("//! Do not edit by hand — regenerate via `python scripts/generate-rhena-glyphs.py`.")
    ap("//!")
    ap("//! Custom Rhineland neume glyph paths for diplomatic rendering.")
    ap("//! Traced from Dendermonde Cod. 9 and Wiesbaden Riesencodex Hs. 2.")
    ap("//! Coordinate system: 1000-unit em, Y-up, flipped by SVG transform at render scale.")
    ap("//!")
    ap("//! ADR-0004: Rhineland neume glyphs for diplomatic rendering.")
    ap("//! ADR-0009: Generated Rhineland glyphs from external OpenType font.")
    ap("")
    ap("#![allow(clippy::unreadable_literal)]")
    ap("")
    ap("use super::Glyph;")
    ap("")

    for g in glyphs:
        if g.doc:
            ap(f"/// {g.doc}")
        ap(f"pub const {g.rust_const}: Glyph = Glyph {{")
        ap(f"    name: {_rust_str(g.font_name)},")
        ap(f"    path: {_rust_str(g.svg_path)},")
        ap(f"    width: {g.width},")
        ap("};")
        ap("")

    ap("/// All Rhineland glyphs in the order defined by glyph-names.json.")
    ap("/// Rhena's resolver indexes into this slice; do not reorder without")
    ap("/// coordinating with Rhena's `glyphs/mod.rs`.")
    ap("pub const ALL_GLYPHS: &[&Glyph] = &[")
    for g in glyphs:
        ap(f"    &{g.rust_const},")
    ap("];")
    ap("")  # trailing newline

    return "\n".join(lines)


def _rust_str(s: str) -> str:
    """Render a Python string as a Rust &'static str literal.

    Our inputs (font_name and svg_path) are ASCII, so we only need to
    escape the minimal set: backslash and double-quote. No unicode escapes
    are ever produced by normalize_path() or by the FONT_NAME_RE regex.
    """
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ---------------------------------------------------------------------------
# Misc helpers
# ---------------------------------------------------------------------------


def sha256_of_stable_otf(path: Path) -> str:
    """Hash the OTF with head.created/modified zeroed for determinism.

    FontForge updates `head.created` and `head.modified` on every save,
    so a naive file hash would change on every regeneration even when
    no glyph data changed. We zero the timestamp fields and re-serialize
    the OTF through fontTools, then hash that. The resulting hash
    reflects only the glyph outlines, metrics, and stable tables.

    Per ADR-0004 (determinism strategy) in docs/adr/.
    """
    font = TTFont(str(path))
    head = font["head"]
    head.created = 0
    head.modified = 0
    buf = io.BytesIO()
    font.save(buf)
    return hashlib.sha256(buf.getvalue()).hexdigest()


def read_version(project_root: Path) -> str:
    vf = project_root / "VERSION"
    if vf.is_file():
        txt = vf.read_text(encoding="utf-8").strip()
        if txt:
            return txt
    return DEFAULT_VERSION


def resolve_timestamp(cli_override: str | None) -> str:
    """Pick the ISO-8601 UTC timestamp for the header.

    Priority: --timestamp flag > SOURCE_DATE_EPOCH > wall clock now.
    The first two enable reproducible builds.
    """
    if cli_override:
        return cli_override
    sde = os.environ.get("SOURCE_DATE_EPOCH")
    if sde:
        try:
            dt = datetime.fromtimestamp(int(sde), tz=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            pass
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _die(msg: str, code: int = 1):
    sys.stderr.write(f"error: {msg}\n")
    sys.exit(code)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate rhineland_glyphs.rs from hildegard-neumes.otf",
    )
    parser.add_argument(
        "--in", dest="in_path", required=True, type=Path,
        help="Path to input OTF (e.g. build/hildegard-neumes.otf)",
    )
    parser.add_argument(
        "--names-map", required=True, type=Path,
        help="Path to src/glyph-names.json",
    )
    parser.add_argument(
        "--widths-table", required=True, type=Path,
        help="Path to src/widths.json",
    )
    parser.add_argument(
        "--out", required=True, type=Path,
        help="Path to output Rust file (e.g. generated/rhineland_glyphs.rs)",
    )
    parser.add_argument(
        "--project-root", type=Path, default=Path(__file__).resolve().parent.parent,
        help="Project root (used to locate VERSION file)",
    )
    parser.add_argument(
        "--tolerance", type=int, default=None,
        help="Override width tolerance (font units). Default: from widths.json.",
    )
    parser.add_argument(
        "--timestamp", type=str, default=None,
        help="Override header timestamp (ISO-8601 UTC). Also honors SOURCE_DATE_EPOCH.",
    )
    args = parser.parse_args(argv)

    if not args.in_path.is_file():
        _die(f"input OTF not found: {args.in_path}", code=2)
    if not args.names_map.is_file():
        _die(f"names map not found: {args.names_map}", code=2)
    if not args.widths_table.is_file():
        _die(f"widths table not found: {args.widths_table}", code=2)

    records, widths, contract_tolerance = load_contract(
        args.names_map, args.widths_table
    )
    tolerance = args.tolerance if args.tolerance is not None else contract_tolerance

    try:
        font = TTFont(str(args.in_path))
    except Exception as exc:  # fontTools raises many shapes
        _die(f"cannot open OTF {args.in_path}: {exc}", code=2)

    # Sanity: em size
    upem = font["head"].unitsPerEm
    if upem != 1000:
        sys.stderr.write(
            f"warning: OTF unitsPerEm={upem}, expected 1000. Widths and "
            f"coordinates will be emitted verbatim; verify Rhena is happy.\n"
        )

    validate_glyph_presence(font, (r.font_name for r in records))

    extracted: list[ExtractedGlyph] = []
    for r in records:
        try:
            path, actual_width = extract_glyph(font, r.font_name)
        except (KeyError, ValueError) as exc:
            _die(f"extracting {r.font_name}: {exc}")

        validate_path_commands(r.font_name, path)
        validate_glyph(r.font_name, actual_width, widths[r.font_name], tolerance)

        extracted.append(
            ExtractedGlyph(
                rust_const=r.rust_const,
                font_name=r.font_name,
                svg_path=path,
                width=int(widths[r.font_name]),  # emit contract value, not actual
                doc=r.doc,
            )
        )

    version = read_version(args.project_root)
    sha256_hex = sha256_of_stable_otf(args.in_path)
    timestamp_iso = resolve_timestamp(args.timestamp)

    rust_src = render_rust_file(extracted, version, sha256_hex, timestamp_iso)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rust_src, encoding="utf-8")

    print(f"Generated {len(extracted)} glyphs to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
