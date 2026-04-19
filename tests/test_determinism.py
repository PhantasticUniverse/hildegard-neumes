"""Determinism test — per ADR-0004.

Runs the codegen script twice against the same minimal test fixture with a
frozen timestamp, and asserts the two output files are byte-identical.

Parametrized over both the TTF (quadratic Bézier) and OTF/CFF (cubic
Bézier) fixtures, so determinism is verified independently for both
outline formats. Per review §1 (docs/planning/claude-review-2-2026-04-14.md),
the OTF fixture is the one that matches production (ADR-0007), while the
TTF fixture provides defense-in-depth coverage.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


FIXTURE_FORMATS = ["minimal_ttf", "minimal_otf"]


@pytest.mark.parametrize("fixture_name", FIXTURE_FORMATS)
def test_double_run_byte_identical(
    fixture_name: str,
    names_map_path: Path,
    widths_path: Path,
    scripts_dir: Path,
    tmp_path: Path,
    request: pytest.FixtureRequest,
):
    """Run the generator twice with SOURCE_DATE_EPOCH=0 and --timestamp frozen.

    The two output files MUST be byte-identical. Runs independently
    against each fixture (TTF, OTF); different formats naturally produce
    different output, but each format's own two runs must agree. If they
    differ, some non-determinism has leaked into the pipeline (e.g. dict
    iteration order, float formatting, timestamp embedding).
    """
    fixture_path: Path = request.getfixturevalue(fixture_name)
    out1 = tmp_path / f"run1_{fixture_name}.rs"
    out2 = tmp_path / f"run2_{fixture_name}.rs"
    script = scripts_dir / "generate-rhena-glyphs.py"
    frozen_ts = "2026-01-01T00:00:00Z"

    def run_once(out_path: Path) -> None:
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
                str(out_path),
                "--timestamp",
                frozen_ts,
            ],
            env={"SOURCE_DATE_EPOCH": "0", "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"generator failed with code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    run_once(out1)
    run_once(out2)

    bytes1 = out1.read_bytes()
    bytes2 = out2.read_bytes()
    assert bytes1 == bytes2, (
        f"determinism failure on {fixture_name}: two runs of "
        "generate-rhena-glyphs.py produced different output. Per ADR-0004 "
        "this MUST NOT happen. Inspect the diff manually:\n"
        f"  run1: {out1}\n"
        f"  run2: {out2}"
    )


@pytest.mark.parametrize("fixture_name", FIXTURE_FORMATS)
def test_header_contains_provenance(
    fixture_name: str,
    names_map_path: Path,
    widths_path: Path,
    scripts_dir: Path,
    tmp_path: Path,
    request: pytest.FixtureRequest,
):
    """The generated file header MUST contain sha256, version, and timestamp.

    Runs against both fixtures independently.
    """
    fixture_path: Path = request.getfixturevalue(fixture_name)
    out = tmp_path / f"out_{fixture_name}.rs"
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
    assert "@generated" in content
    assert "sha256:" in content
    assert "2026-01-01T00:00:00Z" in content
    assert "ADR-0004" in content
    assert "ADR-0009" in content


def test_ttf_and_otf_differ(
    minimal_ttf: Path,
    minimal_otf: Path,
    names_map_path: Path,
    widths_path: Path,
    scripts_dir: Path,
    tmp_path: Path,
):
    """Sanity: the TTF and OTF fixtures SHOULD produce different output.

    If they produce identical output, the fixtures are not actually
    exercising different codepaths and the parametrization is pointless.
    This test ensures the two formats emit distinguishable SVG path
    commands (Q for quadratic, C for cubic).
    """
    script = scripts_dir / "generate-rhena-glyphs.py"
    frozen_ts = "2026-01-01T00:00:00Z"

    def run(fixture: Path, out: Path) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--in",
                str(fixture),
                "--names-map",
                str(names_map_path),
                "--widths-table",
                str(widths_path),
                "--out",
                str(out),
                "--timestamp",
                frozen_ts,
            ],
            env={"SOURCE_DATE_EPOCH": "0", "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr

    ttf_out = tmp_path / "from_ttf.rs"
    otf_out = tmp_path / "from_otf.rs"
    run(minimal_ttf, ttf_out)
    run(minimal_otf, otf_out)

    ttf_text = ttf_out.read_text(encoding="utf-8")
    otf_text = otf_out.read_text(encoding="utf-8")

    # Different input formats MUST produce different path data.
    assert ttf_text != otf_text, (
        "TTF and OTF fixtures produced identical output — the fixtures "
        "are not exercising different codepaths."
    )

    # OTF path MUST contain at least one cubic (C) command.
    assert " C " in otf_text, (
        "OTF output has no cubic C commands — CFF codepath is not "
        "being exercised."
    )
    # TTF path MUST contain at least one quadratic (Q) command.
    assert " Q " in ttf_text, (
        "TTF output has no quadratic Q commands — glyf codepath is not "
        "being exercised."
    )
