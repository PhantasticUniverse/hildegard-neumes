"""Determinism test — per ADR-0004, post-ADR-0012 codegen.

Runs the generator twice against the same contract with a frozen
SOURCE_DATE_EPOCH and asserts the two outputs are byte-identical.
If they differ, some non-determinism has leaked in (dict iteration
order, float formatting, unpinned timestamp, etc.).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PINNED_EPOCH = "1777593600"  # 2026-05-01T00:00:00Z, arbitrary pinned value


def _run_generator(
    script: Path, contract: Path, out: Path, epoch: str = PINNED_EPOCH
) -> None:
    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = epoch
    subprocess.run(
        [sys.executable, str(script), "--contract", str(contract), "--out", str(out)],
        check=True,
        env=env,
    )


def test_double_run_byte_identical(
    contract_path: Path, scripts_dir: Path, tmp_path: Path
):
    script = scripts_dir / "generate-rhena-glyphs.py"
    out_a = tmp_path / "a.rs"
    out_b = tmp_path / "b.rs"

    _run_generator(script, contract_path, out_a)
    _run_generator(script, contract_path, out_b)

    assert out_a.read_bytes() == out_b.read_bytes(), (
        "generator output is non-deterministic under pinned SOURCE_DATE_EPOCH"
    )


def test_epoch_change_changes_header_timestamp(
    contract_path: Path, scripts_dir: Path, tmp_path: Path
):
    """Sanity check that the pin is actually being honored."""
    script = scripts_dir / "generate-rhena-glyphs.py"
    out_a = tmp_path / "a.rs"
    out_b = tmp_path / "b.rs"

    _run_generator(script, contract_path, out_a, epoch="0")
    _run_generator(script, contract_path, out_b, epoch="2000000000")

    header_a = out_a.read_text(encoding="utf-8").splitlines()[0]
    header_b = out_b.read_text(encoding="utf-8").splitlines()[0]
    assert header_a != header_b, (
        "header timestamp did not change with SOURCE_DATE_EPOCH — pin ignored"
    )
    # Bodies after the header block should still match
    body_a = "\n".join(out_a.read_text(encoding="utf-8").splitlines()[4:])
    body_b = "\n".join(out_b.read_text(encoding="utf-8").splitlines()[4:])
    assert body_a == body_b, "content diverged between epoch runs — non-timestamp drift"
