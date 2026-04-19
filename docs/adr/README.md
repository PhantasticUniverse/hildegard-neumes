# Architecture Decision Records

Short-form decision records for the Hildegard Neumes font project, following the format used by the sibling Rhena project (`../hildegard/docs/adr/`). Each record captures a single architectural decision, its alternatives, and its consequences. Target length: ~60 lines, crisp, no hedging.

## Conventions

- One decision per file.
- Filename: `ADR-NNNN-short-slug.md` (zero-padded to four digits).
- Status values: Proposed, Accepted, Superseded, Deprecated, Rejected.
- Normative language follows BCP 14 (MUST / SHOULD / MAY, capitalized only where normative).
- New ADRs are numbered sequentially; do not reuse numbers.

## Index

| Number | Title | Status |
| --- | --- | --- |
| ADR-0001 | Source format: UFO3, not SFD | Accepted |
| ADR-0002 | Codegen toolchain: Python 3.11+ with fontTools | Accepted |
| ADR-0003 | Contract ownership: Rhena owns rhineland.contract.json | Proposed |
| ADR-0004 | Determinism strategy for codegen | Accepted |
| ADR-0005 | Width freeze scope for v1 | Accepted |
| ADR-0006 | Licence: SIL OFL 1.1 with Reserved Font Name | Accepted |
| ADR-0007 | OpenType/CFF outlines, not TrueType | Accepted |
| ADR-0008 | Paleographic fidelity arbitration policy | Accepted |
| ADR-0009 | SMuFL alignment for tradition-agnostic glyphs | Accepted |

## Coordination with Rhena

Decisions that affect the Rhena project's code are staged in `../rhena-coordination/` rather than committed as ADRs in this repo. The Rhena-side switch to consuming this font's generated output is tracked there as `ADR-0009-generated-rhineland-glyphs.md`, awaiting Rhena's ADR committee to adopt it under Rhena's own numbering — note that this is **Rhena's** ADR-0009 (to be adopted into Rhena's sequence), distinct from **our** font-project ADR-0009 (SMuFL alignment) listed above.
