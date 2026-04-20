#!/usr/bin/env python3
"""validate-font.py — post-build sanity checks for hildegard-neumes.{otf,woff,woff2}.

Runs after scripts/build-font.sh to catch authoring drift before it
propagates into a Rhena adoption. Post-ADR-0012 scope: the font IS the
Rhena-facing artifact (no more OTF-to-Rust path codegen), so these
checks are metadata-level only.

Checks (per built artifact):

1. File parses via fontTools.TTFont.
2. unitsPerEm == 1000 (SMuFL scale).
3. Every contract glyph (font_name) is present in the glyph set.
4. Every glyph's advance width matches the contract within tolerance.
5. Every glyph's cmap codepoint matches the contract.

Exits 0 on success, 1 on any failure. Intended for CI and `just validate-font`.

Usage:
    python scripts/validate-font.py \\
        --in build/hildegard-neumes.otf \\
        --contract docs/rhena-coordination/rhineland.contract.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        f"error: fontTools is required. Install with `pip install fonttools`. ({exc})\n"
    )
    sys.exit(2)


def validate(otf_path: Path, contract_path: Path) -> list[str]:
    """Return a list of error strings (empty on success)."""
    errors: list[str] = []

    if not otf_path.is_file():
        return [f"font not found: {otf_path}"]
    if not contract_path.is_file():
        return [f"contract not found: {contract_path}"]

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    tolerance = contract.get("width_tolerance", 1)

    try:
        font = TTFont(str(otf_path))
    except Exception as exc:
        return [f"cannot open {otf_path}: {exc}"]

    if font["head"].unitsPerEm != 1000:
        errors.append(
            f"unitsPerEm = {font['head'].unitsPerEm}, expected 1000"
        )

    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"].metrics
    cmap = font.getBestCmap()
    name_to_cp = {name: cp for cp, name in cmap.items()}

    for g in contract["glyphs"]:
        name = g["font_name"]
        expected_width = g["width"]
        expected_cp = int(g["smufl_codepoint"].removeprefix("U+"), 16)

        if name not in glyph_set:
            errors.append(f"missing glyph: {name}")
            continue

        actual_width = int(hmtx[name][0])
        if abs(actual_width - expected_width) > tolerance:
            errors.append(
                f"{name}: advance {actual_width} != contract {expected_width} "
                f"(tol={tolerance})"
            )

        actual_cp = name_to_cp.get(name)
        if actual_cp != expected_cp:
            got = f"U+{actual_cp:04X}" if actual_cp else "missing"
            errors.append(
                f"{name}: cmap {got} != contract U+{expected_cp:04X}"
            )

    return errors


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--in", dest="in_path", required=True, type=Path,
        help="Path to the .otf / .woff / .woff2 to validate",
    )
    parser.add_argument(
        "--contract", type=Path,
        default=project_root / "docs" / "rhena-coordination" / "rhineland.contract.json",
    )
    args = parser.parse_args()

    errors = validate(args.in_path, args.contract)
    if errors:
        print(f"validate-font: {len(errors)} error(s) in {args.in_path}", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print(f"validate-font: {args.in_path} OK — all 25 glyphs match contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
