"""Tests for validate_glyph() width assertion in generate-rhena-glyphs.py."""

from __future__ import annotations

import pytest

from _gen_import import import_generator

_gen = import_generator()
validate_glyph = _gen.validate_glyph
validate_path_commands = _gen.validate_path_commands


class TestValidateGlyph:
    def test_exact_match_passes(self):
        validate_glyph("rh_punctum", 240, 240, tolerance=1)

    def test_within_tolerance_passes(self):
        validate_glyph("rh_punctum", 239, 240, tolerance=1)
        validate_glyph("rh_punctum", 241, 240, tolerance=1)

    def test_exactly_at_tolerance_passes(self):
        validate_glyph("rh_punctum", 241, 240, tolerance=1)

    def test_over_tolerance_fails(self):
        with pytest.raises(SystemExit) as excinfo:
            validate_glyph("rh_punctum", 242, 240, tolerance=1)
        assert excinfo.value.code == 1

    def test_zero_tolerance_requires_exact(self):
        validate_glyph("rh_punctum", 240, 240, tolerance=0)
        with pytest.raises(SystemExit):
            validate_glyph("rh_punctum", 241, 240, tolerance=0)

    def test_error_message_mentions_glyph_name(self, capsys):
        with pytest.raises(SystemExit):
            validate_glyph("rh_virga", 100, 65, tolerance=1)
        captured = capsys.readouterr()
        assert "rh_virga" in captured.err
        assert "100" in captured.err
        assert "65" in captured.err


class TestValidatePathCommands:
    def test_valid_path_passes(self):
        validate_path_commands("rh_punctum", "M 0 0 L 10 0 L 10 10 L 0 10 Z")

    def test_with_cubic_passes(self):
        validate_path_commands("rh_oriscus", "M 0 0 C 5 10 15 10 20 0 Z")

    def test_with_quadratic_passes(self):
        validate_path_commands("rh_flexa", "M 0 0 Q 10 10 20 0 Z")

    def test_lowercase_command_fails(self):
        # normalize_path should never produce these, but defense in depth
        with pytest.raises(SystemExit):
            validate_path_commands("rh_punctum", "M 0 0 l 10 0 L 10 10 Z")

    def test_disallowed_command_fails(self):
        with pytest.raises(SystemExit):
            validate_path_commands("rh_punctum", "M 0 0 H 10 Z")
