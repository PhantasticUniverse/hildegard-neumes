# Rhena coordination

This directory holds materials that are **conceptually Rhena-side** but staged in this project for review before being copied / adopted upstream. None of these files are authoritative on their own; they become authoritative only when Rhena's maintainers adopt them.

## Contents

### `ADR-0009-generated-rhineland-glyphs.md`

A draft Rhena-side Architecture Decision Record documenting the decision to consume a generated Rhineland glyph module produced from this font project's OTF, replacing the abandoned experimental inline-Rust attempt. This file was initially staged in `docs/adr/` but has been moved here to avoid confusion with this project's own ADR-0001 through ADR-0008.

When the integration lands, this file should be copied to `hildegard/docs/adr/ADR-0009-generated-rhineland-glyphs.md` and adopted by Rhena's ADR process. The filename `ADR-0009` reflects Rhena's ADR numbering (the next free slot after Rhena's existing ADR-0008-wasm-bindings-layer).

### `rhineland.contract.json`

A draft of the single-source-of-truth contract file that this font project's codegen script would consume if Rhena adopts ADR-0003 (contract ownership). This file is a proposal — the font project currently reads from its own `src/glyph-names.json` + `src/widths.json` pair, and migrates to this contract only when Rhena owns it.

**2026-04-14 update (width review)**: the contract file now carries the post-review widths (`rh_virga=90`, `rh_liquescent_asc=160`, `rh_liquescent_desc=160`) per the analysis at `docs/planning/width-review-2026-04-14.md`. An earlier staging file `widths_proposed.json` was deleted in the same pass because its content has merged into this contract. Rhena's `crates/rhena-core/src/render_ir/glyphs/rhineland.rs` still has the pre-review values; the coordinated adoption PR on the Rhena side brings the widths and the diplomatic-mode golden-snapshot updates together in one commit. See the `width_review` provenance field at the top of `rhineland.contract.json` for the authoritative pointer.

Proposed target location in Rhena: `hildegard/crates/rhena-core/src/render_ir/glyphs/rhineland.contract.json`.

## Workflow

When a file in this directory is ready for adoption in Rhena:

1. Open a PR in Rhena that copies the file to its target location.
2. In the same PR, add any Rhena-side glue (unit tests, `include_str!` references, documentation updates).
3. Update this project's `docs/adr/ADR-0003-contract-ownership.md` status from Proposed to Accepted once the contract file lands.
4. Update this project's `scripts/generate-rhena-glyphs.py` to read from the pinned contract file.

## Why stage here instead of writing directly into Rhena?

The font project has the reviewer context (paleographic research, width review, Gardiner deep-read) but does not have commit rights or review authority in Rhena. Staging here lets the work accumulate for a coherent Rhena-side review pass, rather than dripping in cross-project PRs without context.
