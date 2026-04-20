"""Tests for scripts/scaffold-ufo.py — Phase A UFO3 scaffolding.

Verifies that running the scaffold script produces a valid UFO3
directory whose advance widths, SMuFL codepoints, and glyph inventory
agree with the 19-atom contract at src/glyph-names.json +
src/widths.json.

Tests run against a temporary output path via --out and --force so the
live src/hildegard-neumes.ufo/ is never touched.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# fontTools.ufoLib transitively imports `fs` (pyfilesystem2). It's an
# optional ecosystem dep, not declared in pyproject.toml. Skip the
# round-trip tests when it's absent rather than forcing the dependency;
# the file-structure tests below don't need it.
#
# The `fs` import emits a DeprecationWarning (pkg_resources usage), and
# pyproject.toml promotes warnings to errors. Suppress that specific
# warning during the probe so absence-of-fs doesn't read as failure of
# the whole collection.
_ufolib_available = False
UFOReader = None  # type: ignore[assignment]
try:
    import warnings as _warnings
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", DeprecationWarning)
        from fontTools.ufoLib import UFOReader  # noqa: F401
    _ufolib_available = True
except Exception:
    pass


@pytest.fixture(scope="module")
def scaffolded_ufo(
    tmp_path_factory: pytest.TempPathFactory,
    scripts_dir: Path,
    names_map_path: Path,
    widths_path: Path,
) -> Path:
    """Run scaffold-ufo.py into a tmp_path and return the UFO path."""
    out_dir = tmp_path_factory.mktemp("scaffold") / "hildegard-neumes.ufo"
    script = scripts_dir / "scaffold-ufo.py"

    result = subprocess.run(
        [
            sys.executable, str(script),
            "--out", str(out_dir),
            "--names-map", str(names_map_path),
            "--widths-table", str(widths_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"scaffold-ufo.py exited {result.returncode}\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert out_dir.is_dir(), f"UFO3 directory not produced at {out_dir}"
    return out_dir


class TestUFOStructure:
    """File-structure assertions that don't require fontTools.ufoLib."""

    def test_required_toplevel_files(self, scaffolded_ufo: Path):
        for name in ("metainfo.plist", "fontinfo.plist",
                     "layercontents.plist", "lib.plist"):
            assert (scaffolded_ufo / name).is_file(), f"missing {name}"

    def test_glyphs_directory_exists(self, scaffolded_ufo: Path):
        glyphs = scaffolded_ufo / "glyphs"
        assert glyphs.is_dir()
        assert (glyphs / "contents.plist").is_file()

    def test_one_glif_per_glyph(
        self, scaffolded_ufo: Path, names_map_path: Path
    ):
        import json
        n_contract = len(json.loads(names_map_path.read_text())["glyphs"])
        expected = n_contract + 1  # +1 for .notdef
        glifs = sorted((scaffolded_ufo / "glyphs").glob("*.glif"))
        assert len(glifs) == expected, (
            f"expected {expected} .glif files ({n_contract} atoms + .notdef), "
            f"got {len(glifs)}"
        )

    def test_notdef_filename_is_sanitized(self, scaffolded_ufo: Path):
        # UFO3 requires leading-dot replacement; `.notdef` → `_notdef.glif`.
        assert (scaffolded_ufo / "glyphs" / "_notdef.glif").is_file()
        assert not (scaffolded_ufo / "glyphs" / ".notdef.glif").exists()

    def test_metainfo_format_version(self, scaffolded_ufo: Path):
        import plistlib
        meta = plistlib.loads((scaffolded_ufo / "metainfo.plist").read_bytes())
        assert meta["formatVersion"] == 3
        assert "creator" in meta

    def test_layercontents_defines_default_layer(self, scaffolded_ufo: Path):
        import plistlib
        layers = plistlib.loads((scaffolded_ufo / "layercontents.plist").read_bytes())
        assert ["public.default", "glyphs"] in layers

    def test_glyph_order_starts_with_notdef(
        self, scaffolded_ufo: Path, names_map_path: Path
    ):
        import json
        import plistlib
        n_contract = len(json.loads(names_map_path.read_text())["glyphs"])
        lib = plistlib.loads((scaffolded_ufo / "lib.plist").read_bytes())
        order = lib.get("public.glyphOrder", [])
        assert order[0] == ".notdef", "public.glyphOrder must start with .notdef"
        assert len(order) == n_contract + 1


@pytest.mark.skipif(
    not _ufolib_available,
    reason="fontTools.ufoLib requires `fs` package (optional dependency)",
)
class TestUFORoundTrip:
    """UFOReader round-trip assertions — stronger but needs `pip install fs`."""

    def test_reader_accepts_ufo(self, scaffolded_ufo: Path):
        reader = UFOReader(scaffolded_ufo)
        # UFOReader 4.x deprecates `.formatVersion` in favour of
        # `.formatVersionTuple` — accept either.
        version_tuple = getattr(reader, "formatVersionTuple", None)
        if version_tuple is not None:
            assert version_tuple[0] == 3
        else:
            assert reader.formatVersion == 3

    def test_fontinfo_metrics(self, scaffolded_ufo: Path):
        reader = UFOReader(scaffolded_ufo)
        info = type("Info", (), {})()
        reader.readInfo(info)
        assert info.unitsPerEm == 1000
        # SMuFL ≥ 2 em vertical box per ADR-0009 (Bravura uses ±2012
        # exactly; we round to ±2000).
        assert info.ascender == 2000
        assert info.descender == -2000
        assert info.familyName == "Hildegard Neumes"
        assert info.styleName == "Regular"

    def test_glyph_widths_match_contract(
        self, scaffolded_ufo: Path, widths_path: Path
    ):
        reader = UFOReader(scaffolded_ufo)
        glyph_set = reader.getGlyphSet()
        expected = json.loads(widths_path.read_text())["widths"]

        for name, expected_width in expected.items():
            assert name in glyph_set, f"glyph {name!r} missing from UFO"
            g = type("G", (), {})()
            glyph_set.readGlyph(name, g)
            assert g.width == expected_width, (
                f"{name}: UFO advance {g.width} != contract {expected_width}"
            )

    def test_glyph_codepoints_match_contract(
        self, scaffolded_ufo: Path, names_map_path: Path
    ):
        reader = UFOReader(scaffolded_ufo)
        glyph_set = reader.getGlyphSet()
        entries = json.loads(names_map_path.read_text())["glyphs"]

        for entry in entries:
            name = entry["font_name"]
            expected_cp = entry["smufl_codepoint"]
            g = type("G", (), {})()
            glyph_set.readGlyph(name, g)
            actual = list(getattr(g, "unicodes", []) or [])

            if expected_cp is None:
                assert actual == [], (
                    f"{name}: expected no unicode, UFO has {actual}"
                )
            else:
                want = int(expected_cp.removeprefix("U+"), 16)
                assert actual == [want], (
                    f"{name}: expected U+{want:04X}, UFO has {actual}"
                )

    def test_placeholder_paths_non_empty(
        self, scaffolded_ufo: Path, widths_path: Path
    ):
        """Every scaffolded glyph must have a non-empty outline.

        The older "body width <= advance" invariant was dropped post-
        2026-04-20: PLACEHOLDER_BBOX in scaffold-ufo.py now mirrors the
        drawn calligraphic bboxes for accurate regeneration, and
        calligraphic glyphs routinely have hooks/flicks extending beyond
        their advance. That's a normal font-design property (negative
        LSB, RSB overflow) not a bug.
        """
        from fontTools.pens.basePen import BasePen

        class BoundsPen(BasePen):
            def __init__(self, glyphSet):
                super().__init__(glyphSet)
                self.xmin = self.ymin = self.xmax = self.ymax = None

            def _moveTo(self, pt):
                self._update(*pt)

            def _lineTo(self, pt):
                self._update(*pt)

            def _curveToOne(self, *pts):
                for pt in pts:
                    self._update(*pt)

            def _qCurveToOne(self, *pts):
                for pt in pts:
                    self._update(*pt)

            def _update(self, x, y):
                if self.xmin is None or x < self.xmin:
                    self.xmin = x
                if self.xmax is None or x > self.xmax:
                    self.xmax = x
                if self.ymin is None or y < self.ymin:
                    self.ymin = y
                if self.ymax is None or y > self.ymax:
                    self.ymax = y

        reader = UFOReader(scaffolded_ufo)
        glyph_set = reader.getGlyphSet()
        expected = json.loads(widths_path.read_text())["widths"]

        for name in expected:
            pen = BoundsPen(glyph_set)
            glyph_set[name].draw(pen)
            assert pen.xmin is not None, f"{name}: empty outline"
            body = pen.xmax - pen.xmin
            assert body > 0, f"{name}: degenerate outline (zero width)"


class TestGuardrails:
    """Scaffolder guardrails against destructive re-runs."""

    def test_refuses_to_overwrite_without_force(
        self, scaffolded_ufo: Path, scripts_dir: Path,
        names_map_path: Path, widths_path: Path,
    ):
        script = scripts_dir / "scaffold-ufo.py"
        result = subprocess.run(
            [
                sys.executable, str(script),
                "--out", str(scaffolded_ufo),  # already exists
                "--names-map", str(names_map_path),
                "--widths-table", str(widths_path),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, (
            "scaffold-ufo.py should refuse to overwrite without --force"
        )
        assert "already exists" in result.stderr.lower()

    def test_force_allows_overwrite(
        self, scaffolded_ufo: Path, scripts_dir: Path,
        names_map_path: Path, widths_path: Path,
    ):
        script = scripts_dir / "scaffold-ufo.py"
        result = subprocess.run(
            [
                sys.executable, str(script),
                "--out", str(scaffolded_ufo),
                "--names-map", str(names_map_path),
                "--widths-table", str(widths_path),
                "--force",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"--force overwrite failed: {result.stderr}"
        )
