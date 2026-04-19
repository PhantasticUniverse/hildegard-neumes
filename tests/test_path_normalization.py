"""Tests for normalize_path() in generate-rhena-glyphs.py.

Covers the path-canonicalization contract: absolute uppercase {M, L, C, Q, Z}
commands, single space separators, integer coordinates, no leading zeros,
round-half-up rounding, and explicit rejection of arc commands.
"""

from __future__ import annotations

import pytest

from _gen_import import import_generator

_gen = import_generator()
normalize_path = _gen.normalize_path
_round_half_up = _gen._round_half_up


class TestRoundHalfUp:
    def test_rounds_half_up_positive(self):
        assert _round_half_up(0.5) == 1
        assert _round_half_up(1.5) == 2
        assert _round_half_up(2.5) == 3

    def test_rounds_half_up_negative(self):
        assert _round_half_up(-0.5) == -1
        assert _round_half_up(-1.5) == -2
        assert _round_half_up(-2.5) == -3

    def test_integer_passthrough(self):
        assert _round_half_up(5.0) == 5
        assert _round_half_up(-7.0) == -7

    def test_small_positive_rounding(self):
        assert _round_half_up(0.4) == 0
        assert _round_half_up(0.6) == 1


class TestNormalizePath:
    def test_simple_absolute_rectangle(self):
        path = "M0 0 L10 0 L10 10 L0 10 Z"
        assert normalize_path(path) == "M 0 0 L 10 0 L 10 10 L 0 10 Z"

    def test_relative_commands_become_absolute(self):
        # m (relative moveto) followed by l (relative lineto)
        path = "m0 0 l10 0 l0 10 l-10 0 z"
        result = normalize_path(path)
        # Note: first m is treated as absolute because cursor starts at 0,0
        assert "M 0 0" in result
        assert "L 10 0" in result
        assert "L 10 10" in result
        assert "L 0 10" in result
        assert result.endswith("Z")

    def test_float_coords_rounded_to_integers(self):
        path = "M0.7 0.3 L10.5 0.5 L10.5 10.5 Z"
        result = normalize_path(path)
        # 0.7 rounds to 1, 0.3 rounds to 0, 10.5 rounds to 11 (round-half-up), 0.5 rounds to 1
        assert "M 1 0" in result
        assert "L 11 1" in result
        assert "L 11 11" in result

    def test_cubic_bezier_preserved(self):
        path = "M0 0 C10 0 10 10 0 10 Z"
        result = normalize_path(path)
        assert "C 10 0 10 10 0 10" in result

    def test_quadratic_bezier_preserved(self):
        path = "M0 0 Q5 10 10 0 Z"
        result = normalize_path(path)
        assert "Q 5 10 10 0" in result

    def test_horizontal_command_becomes_L(self):
        path = "M0 0 H10 Z"
        result = normalize_path(path)
        assert "L 10 0" in result
        assert "H" not in result

    def test_vertical_command_becomes_L(self):
        path = "M0 0 V10 Z"
        result = normalize_path(path)
        assert "L 0 10" in result
        assert "V" not in result

    def test_arc_command_rejected(self):
        path = "M0 0 A5 5 0 0 1 10 10 Z"
        with pytest.raises(ValueError, match="arc"):
            normalize_path(path)

    def test_empty_path(self):
        assert normalize_path("") == ""

    def test_path_must_start_with_m(self):
        path = "L10 10 Z"
        with pytest.raises(ValueError, match="must start with M"):
            normalize_path(path)

    def test_implicit_lineto_after_moveto(self):
        # "M 0 0 10 10" is "moveto (0,0), implicit lineto (10,10)"
        path = "M0 0 10 10 Z"
        result = normalize_path(path)
        assert "M 0 0" in result
        assert "L 10 10" in result
