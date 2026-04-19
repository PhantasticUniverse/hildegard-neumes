# ADR-0003: Contract ownership — Rhena owns rhineland.contract.json

- Status: Proposed (font-project side; Rhena-side adoption pending)
- Date: 2026-04-14
- Deciders: project maintainers
- Consulted: claude-review-2026-04-14 § 3, rhena_integration_plan.md § 3
- Tags: contract, cross-project, drift-detection

## Context

The Rhena ↔ font contract — the 19 glyph names, advance widths, SMuFL cross-references, and docstrings — currently lives in three places:

1. Rhena's `glyphs/mod.rs` resolver (references glyph names as string literals).
2. Rhena's `rhineland.rs` (declares widths and names as `pub const`s).
3. This font project's `src/glyph-names.json` and `src/widths.json`.

There is no automated check that these stay in sync. Drift is silent: adding a new name on one side without the other produces a resolver fallback, not a compile error.

## Decision

Rhena SHOULD become the authoritative owner of a single machine-readable contract file at `crates/rhena-core/src/render_ir/glyphs/rhineland.contract.json`. The font project's `scripts/generate-rhena-glyphs.py` SHOULD read from a pinned copy of that file, not from locally-owned duplicates.

The contract file merges the content currently split between `glyph-names.json` and `widths.json`, plus adds validation that Rhena's resolver tests can import via `include_str!`.

Migration path:

1. The font project drafts `docs/rhena-coordination/rhineland.contract.json` with the full v1 contract.
2. Rhena adopts it (new file, new unit test asserting `rhineland.rs` constants match, new ADR on Rhena's side).
3. The font project deletes `src/glyph-names.json` and `src/widths.json` and reads from a pinned copy of Rhena's contract file (git submodule or periodic sync justfile target).

This decision is marked **Proposed** until Rhena adopts the contract file.

## Alternatives considered

1. **Font project owns the contract, Rhena reads it**. Rejected: inverts the ownership. Rhena is the consumer that defines what it needs; the font supplies what Rhena asks for. Having the font define the contract is backwards.
2. **Both projects own independent copies with a CI sync check**. Rejected: two sources of truth, drift always possible during the window between commits.
3. **Status quo: three places, manual coordination**. Rejected: integration work at the boundary of two projects always loses a checklist war (review §3).

## Consequences

### Positive
- Single source of truth for the 19-atom contract.
- Rhena's contract unit test catches drift at compile time.
- Adding a glyph is a Rhena-side PR that propagates to the font project on next sync.

### Negative
- Temporary bi-directional dependency during the migration: the font project needs the contract file to exist in Rhena before it can delete its local copies.
- Requires a Rhena-side ADR + new unit test.

### Neutral
- The v1 OTF swap does not strictly require this — `glyph-names.json` + `widths.json` work for v1. The contract file is a v1→v2 transition.

## References

- `docs/rhena-coordination/rhineland.contract.json` — draft contract file (proposal)
- `claude-review-2026-04-14.md` § 3
- `rhena_integration_plan.md` § 3
