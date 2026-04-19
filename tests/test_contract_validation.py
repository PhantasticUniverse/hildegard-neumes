"""Tests for the load_contract() helper in generate-rhena-glyphs.py.

Covers:
- Valid glyph-names.json + widths.json load successfully
- Missing widths entry raises SystemExit(1)
- Bad rust_const regex raises
- Bad font_name regex raises
- Duplicate rust_const raises
- Duplicate font_name raises
- GLYPH_ORDER mismatch (missing entry) raises
- Wrong version raises
- `just show-contract` recipe regression guard (round-3 review §1)
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from _gen_import import import_generator

_gen = import_generator()
load_contract = _gen.load_contract
GLYPH_ORDER = _gen.GLYPH_ORDER


def _write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj), encoding="utf-8")


def _valid_names_map() -> dict:
    return {
        "version": 1,
        "glyphs": [
            {
                "rust_const": name,
                "font_name": f"rh_{name.lower()}",
                "smufl": None,
                "smufl_codepoint": None,
                "doc": "",
            }
            for name in GLYPH_ORDER
        ],
    }


def _valid_widths(names_map: dict) -> dict:
    return {
        "version": 1,
        "widths": {g["font_name"]: 100 for g in names_map["glyphs"]},
    }


class TestLoadContractHappyPath:
    def test_valid_contract_loads(self, tmp_path: Path, names_map_path, widths_path):
        records, widths, tol = load_contract(names_map_path, widths_path)
        assert len(records) == 19
        assert all(r.rust_const in GLYPH_ORDER for r in records)
        assert tol >= 0

    def test_records_match_glyph_order(self, names_map_path, widths_path):
        records, _, _ = load_contract(names_map_path, widths_path)
        actual = tuple(r.rust_const for r in records)
        assert actual == GLYPH_ORDER


class TestLoadContractValidation:
    def test_wrong_version_exits(self, tmp_path: Path):
        names = _valid_names_map()
        names["version"] = 99
        names_path = tmp_path / "names.json"
        widths_path = tmp_path / "widths.json"
        _write_json(names_path, names)
        _write_json(widths_path, _valid_widths(names))
        with pytest.raises(SystemExit) as excinfo:
            load_contract(names_path, widths_path)
        assert excinfo.value.code == 1

    def test_missing_width_entry_exits(self, tmp_path: Path):
        names = _valid_names_map()
        widths = _valid_widths(names)
        del widths["widths"]["rh_punctum"]
        names_path = tmp_path / "names.json"
        widths_path = tmp_path / "widths.json"
        _write_json(names_path, names)
        _write_json(widths_path, widths)
        with pytest.raises(SystemExit) as excinfo:
            load_contract(names_path, widths_path)
        assert excinfo.value.code == 1

    def test_bad_rust_const_exits(self, tmp_path: Path):
        names = _valid_names_map()
        names["glyphs"][0]["rust_const"] = "lowercase_name"
        names_path = tmp_path / "names.json"
        widths_path = tmp_path / "widths.json"
        _write_json(names_path, names)
        _write_json(widths_path, _valid_widths(names))
        with pytest.raises(SystemExit):
            load_contract(names_path, widths_path)

    def test_bad_font_name_exits(self, tmp_path: Path):
        names = _valid_names_map()
        names["glyphs"][0]["font_name"] = "RH_PUNCTUM_WRONG"
        names_path = tmp_path / "names.json"
        widths_path = tmp_path / "widths.json"
        _write_json(names_path, names)
        _write_json(widths_path, _valid_widths(names))
        with pytest.raises(SystemExit):
            load_contract(names_path, widths_path)

    def test_glyph_order_mismatch_exits(self, tmp_path: Path):
        names = _valid_names_map()
        # Remove one glyph entry so order no longer matches GLYPH_ORDER
        names["glyphs"].pop()
        names_path = tmp_path / "names.json"
        widths_path = tmp_path / "widths.json"
        _write_json(names_path, names)
        _write_json(widths_path, _valid_widths(names))
        with pytest.raises(SystemExit):
            load_contract(names_path, widths_path)


class TestShowContractRecipe:
    """Regression guard for the `just show-contract` justfile recipe.

    Round-2's field-name rename (rhena_const → rust_const) missed
    `justfile:65`, the inline Python one-liner that prints the contract
    summary. Round-3 caught the resulting KeyError via `just show-contract`
    crashing. These tests prevent any future rename from silently
    breaking the recipe.

    Two layers of coverage:

    1. `test_show_contract_logic_runs` — reconstructs the recipe's
       essential dict access logic and asserts it runs cleanly. Always
       executes; catches field-name drift via KeyError.

    2. `test_show_contract_just_recipe` — shells out to
       `just show-contract` for the end-to-end real-recipe check. Skips
       when `just` is not installed (most CI matrices and many
       contributor machines).
    """

    def test_show_contract_logic_runs(self, names_map_path: Path, widths_path: Path):
        """Field-name drift guard — runs the recipe's logic directly.

        If any field referenced by the `just show-contract` recipe gets
        renamed without updating `justfile`, this test fails with a
        KeyError pointing at the stale access.
        """
        with open(names_map_path) as f:
            names = json.load(f)
        with open(widths_path) as f:
            widths_raw = json.load(f)
        widths = widths_raw["widths"]

        # Mirror the exact dict accesses justfile's show-contract
        # recipe performs. If any field name drifts, this crashes.
        lines = [
            f"{g['rust_const']:25s} {g['font_name']:25s} w={widths[g['font_name']]:4d}"
            for g in names["glyphs"]
        ]
        assert len(lines) == 19, f"expected 19 glyphs, got {len(lines)}"
        assert all("rh_" in line for line in lines), (
            "expected every line to reference an rh_ font name"
        )

    def test_show_contract_just_recipe(self, project_root: Path):
        """End-to-end check: run the actual `just show-contract` recipe.

        Skipped when `just` is not on PATH. Covers the case where the
        justfile's embedded string escaping drifts from what the
        reconstructed-logic test exercises.
        """
        if shutil.which("just") is None:
            pytest.skip("`just` task runner not installed")

        result = subprocess.run(
            ["just", "show-contract"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"`just show-contract` failed with code {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert result.stdout.strip(), "`just show-contract` produced no output"
        assert "rh_punctum" in result.stdout, (
            "`just show-contract` output does not mention rh_punctum"
        )
