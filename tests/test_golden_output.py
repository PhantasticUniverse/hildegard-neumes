"""Golden-output test — exercises the full codegen pipeline end-to-end.

Runs generate-rhena-glyphs.py against the synthesized minimal fixtures
and asserts the output contains the expected Rust structure. The test is
deliberately structural rather than byte-exact — a byte-exact golden would
be fragile against intentional improvements to header comments and Rust
formatting, whereas structural assertions catch real regressions.

Parametrized over both TTF (quadratic) and OTF/CFF (cubic) fixtures.
For the byte-exact double-run check, see test_determinism.py.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


FIXTURE_FORMATS = ["minimal_ttf", "minimal_otf"]


@pytest.mark.parametrize("fixture_name", FIXTURE_FORMATS)
def test_golden_output_shape(
    fixture_name: str,
    names_map_path: Path,
    widths_path: Path,
    scripts_dir: Path,
    tmp_path: Path,
    request: pytest.FixtureRequest,
):
    fixture_path: Path = request.getfixturevalue(fixture_name)
    out = tmp_path / f"rhineland_glyphs_{fixture_name}.rs"
    script = scripts_dir / "generate-rhena-glyphs.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--in",
            str(fixture_path),
            "--names-map",
            str(names_map_path),
            "--widths-table",
            str(widths_path),
            "--out",
            str(out),
            "--timestamp",
            "2026-01-01T00:00:00Z",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    content = out.read_text(encoding="utf-8")

    # Every expected Rhena constant is present as a pub const declaration.
    expected_consts = [
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
    ]
    for const in expected_consts:
        assert f"pub const {const}: Glyph = Glyph {{" in content, (
            f"missing const declaration for {const}"
        )

    # Every expected font name appears as a &'static str literal
    expected_names = [
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
    ]
    for name in expected_names:
        assert f'"{name}"' in content, f"missing font name literal {name!r}"

    # ALL_GLYPHS slice is present and complete
    assert "pub const ALL_GLYPHS: &[&Glyph] = &[" in content
    for const in expected_consts:
        assert f"&{const}," in content

    # Only permitted SVG path commands appear in the emitted path strings.
    # Grep for any disallowed character inside path field values.
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("path: "):
            continue
        path_literal = stripped[len("path: ") :].rstrip(",").strip('"')
        cmds = {c for c in path_literal if c.isalpha()}
        assert cmds.issubset({"M", "L", "C", "Q", "Z"}), (
            f"line contains disallowed path command: {line!r}"
        )
