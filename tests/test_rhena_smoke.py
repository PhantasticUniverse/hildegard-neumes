"""Optional smoke test: copy Rhena, drop generated file into the copy, cargo check.

**Safety model (per review §2):** this test operates exclusively on a
throwaway `shutil.copytree` of the Rhena checkout, created under
`tmp_path` and cleaned up automatically by pytest. The original Rhena
repository at `RHENA_PATH` is **never mutated**. Earlier versions of
this test used a `try/finally` backup/restore pattern, which was unsafe
— a SIGKILL, OOM, power loss, CI runner timeout, or subprocess crash
in `cargo check`'s child processes would leave the original Rhena
`rhineland.rs` overwritten with placeholder-TTF output. Copy-first is
the only way to guarantee the sibling repo is untouched.

**Configuration.** The Rhena path is resolved in this order:
1. `RHENA_PATH` environment variable (explicit override)
2. `../hildegard` relative to this file's project root (default sibling
   checkout)

If neither is present or `Cargo.toml` is missing, the test is skipped
with a helpful message.

**Scope.** The test only runs `cargo check -p rhena-core`, not
`cargo test`. The generated file uses a placeholder fixture, so
`cargo test` would produce spurious snapshot churn. Real snapshot
verification happens after the true OTF lands and a human reviews
diffs against the Dendermonde manuscript reference (ADR-0004
validation plan). This test is a compile-level gate, not a
snapshot-level gate — sufficient to catch struct/field/naming
regressions that would break Rhena's build.

See also:
- docs/planning/claude-review-2-2026-04-14.md § 2 (the review finding)
- docs/adr/ADR-0004-determinism.md (validation plan)
- docs/rhena-coordination/ADR-0009-generated-rhineland-glyphs.md (integration)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def _resolve_rhena_path() -> Path:
    """Return the configured Rhena path.

    RHENA_PATH env var wins; default is ``../hildegard`` relative to
    the hildegard-neumes project root.
    """
    env = os.environ.get("RHENA_PATH")
    if env:
        return Path(env).expanduser().resolve()
    project_root = Path(__file__).resolve().parent.parent
    return (project_root.parent / "hildegard").resolve()


RHENA_PATH = _resolve_rhena_path()


requires_rhena = pytest.mark.skipif(
    not (RHENA_PATH / "Cargo.toml").is_file(),
    reason=(
        f"Rhena sibling project not found at {RHENA_PATH} "
        "(override with RHENA_PATH env var)"
    ),
)

requires_cargo = pytest.mark.skipif(
    shutil.which("cargo") is None,
    reason="cargo not installed",
)


@pytest.fixture
def rhena_copy(tmp_path: Path) -> Path:
    """Return a throwaway copy of the Rhena tree at ``tmp_path/rhena``.

    Uses ``shutil.copytree`` with ``ignore=shutil.ignore_patterns(...)``
    to skip ``target/``, ``.git/``, and compiled Rust artefacts. This
    keeps the copy fast (~a few seconds on a clean checkout) and avoids
    hauling a large ``.git`` history into tmp. The original
    ``RHENA_PATH`` is never touched — the test operates exclusively on
    the copy, which pytest cleans up on session teardown.

    Skips (rather than errors) if Rhena isn't available, so the same
    test module is safe to run on a machine without the sibling
    checkout.
    """
    if not (RHENA_PATH / "Cargo.toml").is_file():
        pytest.skip(f"Rhena not found at {RHENA_PATH}")
    dst = tmp_path / "rhena"
    shutil.copytree(
        RHENA_PATH,
        dst,
        symlinks=True,
        ignore=shutil.ignore_patterns(
            "target",
            ".git",
            "*.rlib",
            "*.rmeta",
            "*.d",
            ".DS_Store",
        ),
    )
    return dst


@pytest.mark.slow
@requires_rhena
@requires_cargo
def test_rhena_accepts_generated_file(
    minimal_ttf: Path,
    names_map_path: Path,
    widths_path: Path,
    scripts_dir: Path,
    tmp_path: Path,
    rhena_copy: Path,
):
    """End-to-end: codegen → drop into a COPY of Rhena → cargo check.

    Even with a minimal placeholder TTF, ``cargo check`` should succeed
    because the generated file is syntactically valid Rust and preserves
    the ``Glyph`` struct contract. A compile failure here means we
    broke the ABI with Rhena's ``render_ir::glyphs`` module (renamed
    field, changed struct shape, wrong const names) — those are the
    regressions this test exists to catch.
    """
    out = tmp_path / "rhineland_glyphs.rs"
    script = scripts_dir / "generate-rhena-glyphs.py"

    gen = subprocess.run(
        [
            sys.executable,
            str(script),
            "--in",
            str(minimal_ttf),
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
    assert gen.returncode == 0, gen.stderr

    target = (
        rhena_copy
        / "crates"
        / "rhena-core"
        / "src"
        / "render_ir"
        / "glyphs"
        / "rhineland.rs"
    )
    assert target.is_file(), f"Rhena target not found in copy: {target}"
    shutil.copy(out, target)

    check = subprocess.run(
        ["cargo", "check", "-p", "rhena-core"],
        cwd=rhena_copy,
        capture_output=True,
        text=True,
    )
    assert check.returncode == 0, (
        "cargo check failed after dropping the generated file into a Rhena copy.\n"
        f"stdout: {check.stdout}\nstderr: {check.stderr}"
    )
    # No restore needed — rhena_copy is in tmp_path and pytest cleans it up.
