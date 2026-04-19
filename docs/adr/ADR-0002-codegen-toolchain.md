# ADR-0002: Codegen toolchain — Python 3.11+ with fontTools

- Status: Accepted
- Date: 2026-04-14
- Deciders: project maintainers
- Consulted: claude-review-2026-04-14 § 7, rhena_integration_plan.md § 4
- Tags: codegen, tooling, build-pipeline

## Context

The font project converts `hildegard-neumes.otf` into a Rust source file that Rhena consumes. The converter needs to read OpenType outline data, emit SVG path strings, and validate against a contract. A language and library stack must be chosen.

## Decision

The codegen toolchain is **Python 3.11+ with the `fontTools` library**. The primary script is `scripts/generate-rhena-glyphs.py`. Dependencies:

- `fontTools` — OTF/TTF reader, `SVGPathPen` for outline → SVG conversion.
- `pytest` — test runner for the codegen script's own test suite.
- Python 3.11+ standard library — `argparse`, `dataclasses`, `hashlib`, `io`, `json`, `pathlib`, `re`.

No additional runtime dependencies. `pyproject.toml` is minimal.

The script MUST have its own test suite at `tests/` exercising **both** outline formats:

- `tests/fixtures/make_minimal_otf.py` — CFF (cubic Bézier) fixture, matching production per ADR-0007. Built via `FontBuilder(isTTF=False)` + `T2CharStringPen.curveTo()`; `SVGPathPen` extracts paths containing `C` commands.
- `tests/fixtures/make_minimal_ttf.py` — TrueType (quadratic Bézier) fixture for defense-in-depth coverage of the `glyf` codepath. Built via `FontBuilder(isTTF=True)` + `TTGlyphPen.qCurveTo()`; extracted paths contain `Q` commands.

Both fixtures are regenerated programmatically at pytest session start (via `tests/conftest.py` session fixtures `minimal_ttf` and `minimal_otf`), **not** committed as binary blobs. Tests that depend on format-specific behaviour parametrize over both via `@pytest.mark.parametrize("fixture_name", ["minimal_ttf", "minimal_otf"])` with indirect resolution through `request.getfixturevalue`. A canary test `test_ttf_and_otf_differ` asserts the two codepaths produce distinguishable output (OTF contains `C`, TTF contains `Q`), preventing silent regression into a format-blind test suite.

Test categories: contract validation (incl. recipe regression guard for `just show-contract`), path normalization, width assertion, determinism (double-run byte diff per format), and structural golden output against both fixtures. Neither fixture requires FontForge at test time.

## Alternatives considered

1. **Rust-native `ttf-parser` + `build.rs`**. Rejected: couples Rhena's cargo build to the font project's release cadence, displaces the dependency rather than eliminating it, and makes code review read glyph changes as `.otf` blob diffs (opaque) rather than `.rs` source diffs (explicit).
2. **Node.js + `opentype.js`**. Rejected: adds a second runtime to contributor onboarding. Python is already required for reproducibility tooling in most font projects.
3. **FontForge scripting in `.pe`**. Rejected: FontForge-specific, no test infrastructure, limited error reporting.

## Consequences

### Positive
- Python + fontTools is the de facto standard in type design tooling; documentation and community help are abundant.
- `SVGPathPen` already emits canonical uppercase absolute commands; the normalizer only has to integerize and validate.
- Tests run in milliseconds against `minimal.otf` without needing FontForge installed.

### Negative
- Rhena contributors now need Python + pip + fontTools installed locally if they want to regenerate glyphs. Onboarding surface grows slightly.
- Python version drift (3.11 vs 3.12 vs 3.13) can affect integer-format output; pin the Python version in CI.

### Neutral
- Rhena's cargo build is untouched. `rhena-core` gains no dependencies.

## References

- fontTools documentation: https://fonttools.readthedocs.io/
- `scripts/generate-rhena-glyphs.py` — the script itself
- `rhena_integration_plan.md` § 4
