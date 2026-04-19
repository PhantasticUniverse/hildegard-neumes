# ADR-0004: Determinism strategy for codegen

- Status: Accepted
- Date: 2026-04-14
- Deciders: project maintainers
- Consulted: claude-review-2026-04-14 § 2, Rhena constitution § 10.1 (regression doctrine), ADR-0002 (codegen toolchain)
- Tags: determinism, ci, build-pipeline

## Context

Rhena's golden-regression doctrine (constitution §10.1) requires byte-stable renders from a given input. The font project's pipeline — `FontForge → OTF → Python → Rust` — has at least five sources of nondeterminism:

1. FontForge writes wall-clock timestamps into the OTF `head.created` / `head.modified` fields on every save.
2. fontTools iterates glyphs in font order, which depends on cmap insertion order.
3. SVG path serialization has multiple valid forms (absolute vs relative, leading-zero integers, whitespace variants).
4. Python's `round()` uses banker's rounding; non-banker alternatives exist and disagree on `.5` values.
5. Python dict iteration is insertion-ordered only since 3.7; assumption must be explicit.

If not addressed, the pipeline produces different `rhineland_glyphs.rs` output on different machines, different Python versions, or different clock times — which means Rhena's snapshot tests oscillate and the generated-file header sha256 is useless as a provenance signal.

## Decision

`scripts/generate-rhena-glyphs.py` MUST implement all of the following:

1. **Iterate glyphs in contract order, not font order.** The order is defined by the `glyphs` array in `src/glyph-names.json` and is cross-checked against a hardcoded `GLYPH_ORDER` tuple in the script.
2. **Emit integer coordinates only.** Floats are rounded at extraction time via `_round_half_up()` (round half-away-from-zero, matching FontForge's own integer-grid snap). Python's default banker's rounding is NOT used, to avoid its parity-dependent oscillation across Python versions.
3. **Canonicalize path commands**: absolute uppercase `M`, `L`, `C`, `Q`, `Z`; single space separators; no leading zeros on integers; no trailing whitespace.
4. **Strip OTF timestamps before hashing.** The sha256 embedded in the generated-file header is computed over a version of the OTF with `head.created = 0` and `head.modified = 0`, re-serialized through fontTools. See `sha256_of_stable_otf()` in the script.
5. **Force reproducible FontForge export.** `scripts/build-font.sh` sets `SOURCE_DATE_EPOCH=0` before invoking FontForge, pinning any FontForge-internal timestamp writes.

`justfile` MUST provide a `check-generated` recipe that regenerates `rhineland_glyphs.rs` against a frozen timestamp and asserts byte-identity with the committed version. CI MUST wire a `reproducibility.yml` job that builds the font twice in a clean environment and diffs the two generated files.

## Alternatives considered

1. **Trust the toolchain**. Rejected: five independent sources of nondeterminism (listed above) each need explicit handling; none are fixed by trust.
2. **Content-hash instead of file-hash**. Rejected: loses the "this is the sha256 of the input file" semantic; a stripped-timestamp file hash is almost as content-pure and keeps the provenance story simple.
3. **Banker's rounding (Python default)**. Rejected: oscillates on `.5` values across Python versions and does not match FontForge's save-time integer snap, producing phantom diffs.

## Consequences

### Positive
- Byte-identical `rhineland_glyphs.rs` across runs, machines, Python versions, and clocks.
- CI can enforce reproducibility with a `diff -q`.
- The `@generated` header's sha256 is a meaningful provenance signal.

### Negative
- `sha256_of_stable_otf()` is slower than a raw file hash (it re-serializes the OTF through fontTools). Negligible on a 19-glyph font.
- `SOURCE_DATE_EPOCH=0` may confuse FontForge-aware tools that read its timestamp for display. Acceptable.

### Neutral
- No runtime impact on Rhena.

## References

- `scripts/generate-rhena-glyphs.py` — `sha256_of_stable_otf()`, `_round_half_up()`, `normalize_path()`
- `scripts/build-font.sh` — `SOURCE_DATE_EPOCH` pin
- `justfile` — `check-generated` recipe
- `claude-review-2026-04-14.md` § 2
- Reproducible Builds: https://reproducible-builds.org/docs/source-date-epoch/
