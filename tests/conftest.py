"""Pytest fixtures for the hildegard-neumes codegen test suite.

Key design decision: the minimal test font is synthesized programmatically
from fontTools.fontBuilder at session start, NOT committed as a binary blob.
This keeps the repo git-clean (no binaries) and makes the fixture fully
reproducible from source.

See docs/adr/ADR-0002-codegen-toolchain.md for rationale.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make the scripts/ directory importable so tests can hit the codegen script
# directly (without going through subprocess) where convenient.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
MINIMAL_TTF = FIXTURE_DIR / "minimal.ttf"
MINIMAL_OTF = FIXTURE_DIR / "minimal.otf"


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Absolute path to the project root."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def scripts_dir(project_root: Path) -> Path:
    return project_root / "scripts"


@pytest.fixture(scope="session")
def src_dir(project_root: Path) -> Path:
    return project_root / "src"


@pytest.fixture(scope="session")
def names_map_path(src_dir: Path) -> Path:
    return src_dir / "glyph-names.json"


@pytest.fixture(scope="session")
def widths_path(src_dir: Path) -> Path:
    return src_dir / "widths.json"


@pytest.fixture(scope="session")
def minimal_ttf(project_root: Path) -> Path:
    """Synthesize a minimal test TTF at session start.

    The TTF contains all 19 named Rhineland glyphs with trivial
    placeholder outlines drawn with quadratic Béziers (``Q`` commands).
    Outlines are intentionally minimal — the goal is to exercise the
    codegen script's contract validation, path extraction, width
    assertion, and normalization pipeline against the TrueType
    codepath, NOT to validate the visual quality of the outlines.
    """
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    from fixtures.make_minimal_ttf import build_minimal_ttf

    build_minimal_ttf(MINIMAL_TTF, project_root / "src" / "widths.json")
    assert MINIMAL_TTF.is_file(), f"failed to produce {MINIMAL_TTF}"
    return MINIMAL_TTF


@pytest.fixture(scope="session")
def minimal_otf(project_root: Path) -> Path:
    """Synthesize a minimal test OTF (CFF) at session start.

    Parallel to ``minimal_ttf``, but produces an OpenType/CFF font with
    cubic Bézier outlines (``C`` commands). Exists so the codegen
    pipeline's cubic-curve path through ``SVGPathPen`` → ``normalize_path``
    gets real test coverage — per ADR-0007 the production font is
    OTF/CFF, and a TTF-only fixture would miss format-specific
    regressions.

    See docs/planning/claude-review-2-2026-04-14.md § 1 for the
    rationale.
    """
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    from fixtures.make_minimal_otf import build_minimal_otf

    build_minimal_otf(MINIMAL_OTF, project_root / "src" / "widths.json")
    assert MINIMAL_OTF.is_file(), f"failed to produce {MINIMAL_OTF}"
    return MINIMAL_OTF


# Format-parametrization helper: tests that need to run against both
# the TTF and OTF fixtures use @pytest.mark.parametrize with this list,
# then resolve the fixture via request.getfixturevalue(fixture_name).
FIXTURE_FORMATS = ["minimal_ttf", "minimal_otf"]
