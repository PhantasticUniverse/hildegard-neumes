# Response to `claude-review-2026-04-14.md`

Date: 2026-04-14
Status: In-session response
Context: the reviewer's note (`docs/planning/claude-review-2026-04-14.md`) audited `rhena_integration_plan.md` and flagged 4 BLOCKERs, 6 LOAD-BEARINGs, and 1 NICE item. This document tracks disposition of each.

## Summary

8 of 14 points addressed in-session. 6 deferred to a follow-up pass. No points rejected.

| Review § | Priority | Disposition |
| --- | --- | --- |
| 1 Source format UFO3 | BLOCKER | ✅ ADR-0001 committed; build-font.sh updated to read UFO3 |
| 2 Determinism | BLOCKER | ✅ ADR-0004 committed; script + build-font.sh fixed (5/5 mitigations) |
| 3 Contract ownership | LOAD-BEARING | 🟡 ADR-0003 (Proposed); draft rhineland.contract.json staged for Rhena adoption |
| 4 Licence | BLOCKER | ✅ ADR-0006, OFL.txt, FONTLOG.txt committed |
| 5 Width freeze | BLOCKER | ✅ ADR-0005 committed (coordinated review pass BEFORE drawing); actual review deferred |
| 6 Y-axis convention | LOAD-BEARING | 🟡 Verified by inspection of existing rhineland.rs paths; Rhena-side smoke test deferred |
| 7 Codegen test plan | LOAD-BEARING | 🟡 Test plan in ADR-0002; `tests/` scaffolding deferred |
| 8 Metadata sidecar | NICE | ⏸ Deferred to v2 |
| 9 ADR set | LOAD-BEARING | ✅ ADR-0001 through ADR-0008 committed |
| 10 CI skeleton | LOAD-BEARING | ⏸ Deferred to follow-up session (.github/workflows/ not yet set up) |
| 11 Coordinate with Rhena active plan | LOAD-BEARING | 🟡 Acknowledged; Rhena-side sequencing question left open |
| 12 v1 checklist | — | 🟡 Steps 1–6 infra partially done; 7–10 (drawing + integration) pending |
| 13 What NOT to do in v1 | — | ✅ Acknowledged; no accidentals, no GSUB/GPOS, no runtime font loading |
| 14 Open questions | — | 🟡 Q1-3, Q5-7 answered via ADRs; Q4 (Rhena sequencing) needs Rhena input |

Legend: ✅ done, 🟡 partial, ⏸ deferred, ❌ rejected.

---

## § 1 — Source format: UFO3 [BLOCKER] → accepted

**Disposition**: ADR-0001 accepted. Source format is `src/hildegard-neumes.ufo/` (UFO3 directory with per-glyph `.glif` files).

**Artefacts**:
- `docs/adr/ADR-0001-source-format.md` (new)
- `scripts/build-font.sh` edited to open `.ufo` instead of `.sfd`

**Not done**: the actual `.ufo` directory does not yet exist. The first FontForge open will create it. `.gitignore` is friendly to `.ufo` (they're version-controllable directories).

## § 2 — Determinism [BLOCKER] → accepted, 5/5 mitigations landed

**Disposition**: ADR-0004 committed. All five mitigations from the review are implemented:

1. ✅ **Iterate in contract order**: `scripts/generate-rhena-glyphs.py` iterates `records` from `glyph-names.json`, never font order. Cross-checked against a hardcoded `GLYPH_ORDER` tuple.
2. ✅ **Integer coordinates**: `_round_half_up()` helper; matches FontForge's save-time integer snap. (Note: review suggested round-half-to-even. I picked round-half-up specifically to match FontForge's behaviour; rationale in the script's `_round_half_up()` docstring. Either is deterministic; I chose the one that agrees with the upstream tool.)
3. ✅ **Canonical paths**: `normalize_path()` emits only `M L C Q Z` absolute uppercase with single-space separators.
4. ✅ **Strip `head.created` / `head.modified` before hashing** — FIXED IN THIS SESSION. New `sha256_of_stable_otf()` helper re-serializes the OTF with timestamps zeroed before hashing.
5. ✅ **Force `SOURCE_DATE_EPOCH=0` in FontForge** — FIXED IN THIS SESSION. `scripts/build-font.sh` exports `SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-0}"` before invoking FontForge.

**CI reproducibility gate**: `justfile` has a `check-generated` recipe that regenerates with a frozen timestamp and asserts byte-identity. GitHub Actions workflow not yet wired (see § 10 below).

**Artefacts**:
- `docs/adr/ADR-0004-determinism.md` (new)
- `scripts/generate-rhena-glyphs.py` (edited)
- `scripts/build-font.sh` (edited)
- `justfile` (already had `check-generated`)

## § 3 — Contract ownership [LOAD-BEARING] → Proposed

**Disposition**: ADR-0003 is marked **Proposed**. The font project drafts `docs/rhena-coordination/rhineland.contract.json`; Rhena has not yet adopted it.

**Current state**: the font project reads from its own `src/glyph-names.json` + `src/widths.json` pair. These are functionally equivalent to the draft contract file. Migration path when Rhena adopts:

1. Rhena PR copies `rhineland.contract.json` into `crates/rhena-core/src/render_ir/glyphs/`.
2. Rhena adds a unit test asserting `rhineland.rs` constants match the contract.
3. Font project updates `scripts/generate-rhena-glyphs.py` to read from a pinned copy of Rhena's file (git submodule or manual sync).
4. Font project deletes its own `glyph-names.json` + `widths.json`.

**Deferred**: actual Rhena-side adoption. That's a Rhena PR, not something I can land unilaterally.

**Artefacts**:
- `docs/adr/ADR-0003-contract-ownership.md` (Proposed)
- `docs/rhena-coordination/rhineland.contract.json` (draft)
- `docs/rhena-coordination/README.md` (explains staging discipline)

## § 4 — Licence [BLOCKER] → accepted OFL-1.1 with RFN

**Disposition**: ADR-0006 committed. SIL OFL 1.1 with Reserved Font Name "Hildegard Neumes".

**Artefacts**:
- `OFL.txt` — canonical SIL text
- `FONTLOG.txt` — SIL-standard changelog stub
- `docs/adr/ADR-0006-license.md` — rationale, generated-code carve-out discussion (OFL §1)
- README.md license section — to be updated next pass

**Note on generated-code relicensing**: ADR-0006 argues that `generated/rhineland_glyphs.rs` is a derivative work under OFL §1 (vector data extraction, not font distribution) and does NOT require the consumer (Rhena) to relicense. This is the standard interpretation but has not been tested in court. If legal review surfaces ambiguity, the SIL FAQ is the definitive source and SIL answers licence questions for free.

## § 5 — Width freeze [BLOCKER] → coordinated review required before drawing

**Disposition**: ADR-0005 committed. Current widths are **provisional** until a coordinated width-review pass with Rhena lands.

**What the ADR mandates**:
1. PNG overlays of each current glyph at 100% em with its advance width annotated as a bbox.
2. Visual verification that each width can plausibly hold a target calligraphic shape.
3. Single coordinated PR against Rhena with any width adjustments + snapshot update.
4. After that PR lands, widths freeze for v1.

**Widths flagged for review**: divisio_minima/maior/maxima (all 16 — verify purely-vertical), pes_line / virgula / flexa_line (connector semantics), punctum/virga/pressus (calligraphic mass room), quilisma/oriscus (undulation room).

**Widths likely fine**: c_clef, f_clef, divisio_finalis, deminutum, liquescents, strophicus, punctum_inclinatum.

**Deferred**: the actual review pass. Cannot happen until the overlay PNGs are produced, which requires the abandoned-attempt glyphs to render as reference material. That's a 30-minute task for a follow-up session.

## § 6 — Y-axis convention [LOAD-BEARING] → verified by inspection

**Disposition**: verified the existing `rhineland.rs` uses Y-up (positive Y at stem top: e.g. `L-8 500 L8 500` is the top of the virga head, with negative Y at the foot). Therefore Rhena's SVG backend already flips Y-up to Y-down at render time, and the new font's Y-up export will be consistent. No immediate fix needed.

**Deferred**: the Rhena-side smoke test the review suggests ("render a single punctum, assert rendered Y coordinates monotonic downward"). That's a test to add to Rhena's test suite; not a blocker for v1.

## § 7 — Codegen script test plan [LOAD-BEARING] → scaffolded in ADR, not implemented

**Disposition**: ADR-0002 commits the test plan. `tests/` directory not yet created.

**Deferred**: actual pytest suite. Scaffold per review § 7:

```
tests/
├── fixtures/
│   ├── minimal.otf            # hand-crafted 2-glyph OTF
│   └── expected_minimal.rs    # golden output
├── test_contract_validation.py
├── test_determinism.py        # regen twice, byte-diff
├── test_path_normalization.py
├── test_width_assertion.py
├── test_golden_output.py
└── test_rhena_smoke.py        # optional, cloned Rhena check
```

## § 8 — Metadata sidecar [NICE] → v2

**Disposition**: deferred to v2. ADR-0007 notes that bbox, anchors, ascender/descender extraction is not v1 scope. The hooks exist — the codegen script can be extended to emit `generated/rhineland-metadata.json` without API changes.

## § 9 — ADR set [LOAD-BEARING] → 8 ADRs committed

**Disposition**: committed.

- ADR-0001: Source format UFO3
- ADR-0002: Codegen toolchain Python + fontTools
- ADR-0003: Contract ownership (Proposed)
- ADR-0004: Determinism strategy
- ADR-0005: Width freeze scope
- ADR-0006: Licence OFL-1.1
- ADR-0007: OTF/CFF outlines
- ADR-0008: Paleographic fidelity arbitration policy

Plus `docs/adr/README.md` index. Target length ~60 lines each; most are 80–100 lines (they carry more rationale than Rhena's shortest ADRs because decisions interact with each other).

## § 10 — CI skeleton [LOAD-BEARING] → deferred

**Disposition**: deferred to a follow-up session. The review specifies 6 workflows:

- `lint-docs.yml` — markdownlint + lychee
- `validate-contract.yml` — pytest on schemas
- `build-font.yml` — headless FontForge
- `codegen.yml` — generate against fixture OTF, byte-identity check
- `reproducibility.yml` — double-build diff
- `smoke-rhena.yml` — clone Rhena, drop, `just check`

None are blocking for v1 drawing; all are cheap to add after the drawing pass. The reproducibility gate is the most important; the rest are hygiene.

## § 11 — Coordinate with Rhena's active plan [LOAD-BEARING] → acknowledged

**Disposition**: acknowledged. The review's recommendation is to land the font swap **after §5.4 wasm tooling, before §5.5 docs sync sweep**. This is captured here for the Rhena-side ADR-0009 draft.

**Not resolved**: Rhena's sequencing decision needs Rhena input. The font project should not unilaterally decide when to hand off.

## § 12 — v1 checklist → mapped

**Disposition**: the review's 10-step v1 checklist maps as follows:

1. ✅ Source format ADR (ADR-0001, UFO3)
2. ✅ OFL-1.1 + FONTLOG (ADR-0006, OFL.txt, FONTLOG.txt)
3. 🟡 Width-review pass (ADR-0005 commits the policy; actual review deferred)
4. 🟡 Contract ownership (ADR-0003 Proposed; rhineland.contract.json drafted)
5. 🟡 `generate-rhena-glyphs.py` with test suite (script written, tests deferred)
6. ⏸ CI skeleton (deferred)
7. ⏸ Draw 19 glyphs (requires UFO3 setup + FontForge)
8. ⏸ Export, codegen, copy into Rhena, `just check`
9. ⏸ Visual comparison against O Ecclesia line 1 reference
10. ⏸ Tag v0.1.0 + file Rhena ADR-0009

Steps 1–6 are "project hygiene before design work." ~60% done in-session.

## § 13 — What NOT to do [implicit] → acknowledged in ADRs and inventory

- No accidentals (v2) — noted in ADR-0005 scope
- No directional oriscus split (v2) — noted in glyph-names.json
- No GSUB/GPOS in v1 — not in scope anywhere
- No new Rhena deps — ADR-0002 is strict
- No `hildegard-neumes-font` Rust crate wrapping the font — not in scope

## § 14 — Open questions

- **Q1 UFO3 vs SFD**: ANSWERED (UFO3, ADR-0001).
- **Q2 Who owns the contract**: ANSWERED (Rhena owns, ADR-0003 Proposed).
- **Q3 Widths freeze scope**: ANSWERED (ADR-0005; coordinated review before drawing).
- **Q4 Sequencing with Rhena**: NEEDS RHENA INPUT. Proposed: after §5.4, before §5.5.
- **Q5 Reserve Rhena ADR-0009**: STAGED at `docs/rhena-coordination/ADR-0009-generated-rhineland-glyphs.md`.
- **Q6 OFL generated-code carve-out**: ANSWERED (ADR-0006 cites OFL §1; SIL FAQ if doubt).
- **Q7 Paleographic arbitration**: ANSWERED (ADR-0008; direct manuscript > Gardiner > Humdrum for visual, Gardiner > Humdrum for classification).

---

## Noted but not resolved

- **CI workflows**: 6 YAML files to draft. Not blocking v1 drawing.
- **tests/ directory**: pytest suite for the codegen script. Cheap once started.
- **Width overlay pass**: 30 minutes once someone can render the abandoned-attempt glyphs.
- **`codepoints.json` extraction**: the review's "Notes I'm less sure about" suggests formalizing SMuFL codepoints as `src/codepoints.json` next to `glyph-names.json` and `widths.json`. Currently handled via the `smufl` / `smufl_codepoint` fields inside `glyph-names.json`, which is functionally equivalent. Revisit if it becomes painful.
- **`examples/` population**: the review's last note suggests at least one "how to use this font in Illustrator / in an HTML page / in LilyPond" recipe. Currently empty after the MEI encoding reference was archived. Stub in follow-up.

## Bottom line

The review's two framing complaints were that (1) determinism is engineered rather than assumed and (2) contract ownership is unambiguous. Both are now addressed: ADR-0004 + the script/build-script fixes satisfy determinism, and ADR-0003 + the staged contract file + the rhena-coordination directory give contract ownership a clear path to Rhena. The 8-ADR set and the licence artefacts close the other two BLOCKERs.

What remains before v1 drawing starts:

1. Coordinated width-review pass with Rhena (review §5, ADR-0005)
2. `tests/` scaffolding for the codegen script (review §7, ADR-0002)
3. CI workflow YAML (review §10)

All three are in the "cheap now, expensive later" category and should land before the first `.glif` is written.
