"""Pytest fixtures for the hildegard-neumes codegen test suite.

Post-ADR-0012 (Rhena's @font-face + codepoint shift), the codegen no
longer extracts paths from the OTF — it emits Rust metadata from the
authoritative contract at docs/rhena-coordination/rhineland.contract.json.
The synthesized-minimal-TTF/OTF fixtures that lived here previously are
gone; tests now exercise the generator end-to-end against the real
contract and check structural + determinism invariants of the output.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))


@pytest.fixture(scope="session")
def project_root() -> Path:
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
def contract_path(project_root: Path) -> Path:
    return project_root / "docs" / "rhena-coordination" / "rhineland.contract.json"
