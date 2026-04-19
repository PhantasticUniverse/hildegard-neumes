# ADR-0005: Width freeze scope for v1

- Status: Accepted
- Date: 2026-04-14
- Deciders: project maintainers
- Consulted: claude-review-2026-04-14 § 5, rhena_integration_plan.md § 3.3
- Tags: contract, widths, coordination

## Context

`rhena_integration_plan.md` § 3.3 freezes advance widths at the values currently in Rhena's abandoned `rhineland.rs`. The rationale is golden-snapshot stability: changing a width would cascade through every diplomatic-mode test that uses the glyph.

Inspection of the current widths raises questions. Several values look like placeholders from the abandoned attempt rather than musically derived choices:

- `rh_divisio_minima`, `rh_divisio_maior`, `rh_divisio_maxima` are all `width: 16` — three different phrase-break depths with identical advance. This is defensible if they are purely vertical glyphs (visible distinction is height, not width), but it is not obvious.
- `rh_virgula: 12`, `rh_pes_line: 12`, `rh_divisio_minima: 16` cluster at the low end with no obvious scaling logic.
- `rh_flexa_line: 172` and `rh_pes_line: 12` are both described as "connector strokes" but have radically different advance widths. This is defensible (flexa_line is a horizontal diagonal; pes_line is a vertical hairline), but it is not self-evident.

Drawing calligraphic shapes into advance widths that were never meant to hold calligraphic mass will produce visible clipping or awkward sidebearings and waste designer effort.

## Decision

V1's width freeze is **provisional**, not permanent. The following policy MUST be followed before the first FontForge glyph is authored:

1. **Coordinated width-review pass with Rhena**. A maintainer produces PNG overlays of each current glyph at 100% em with its declared advance width annotated as a bbox. Visual inspection confirms each width plausibly holds a target calligraphic shape.
2. **Single PR against Rhena** with any width adjustments, landed with the golden-snapshot update pass in a single commit.
3. **After that PR lands**, widths are considered frozen for v1. Further width changes require a new ADR and another coordinated snapshot update.

The font project's `src/widths.json` is marked as the authoritative v1 width source during drawing. After the review pass, the numbers match the post-review Rhena values.

Widths explicitly flagged for review (not preserved blindly):
- `rh_divisio_minima`, `rh_divisio_maior`, `rh_divisio_maxima` — verify purely-vertical interpretation
- `rh_pes_line`, `rh_virgula`, `rh_flexa_line` — verify connector semantics
- `rh_punctum` (240), `rh_virga` (65), `rh_pressus` (300) — verify sufficient room for calligraphic mass at the target 1000-unit em
- `rh_quilisma` (170), `rh_oriscus` (200) — verify room for undulation components

Widths NOT flagged (likely already correct): `rh_c_clef`, `rh_f_clef`, `rh_divisio_finalis`, `rh_deminutum`, `rh_liquescent_asc`, `rh_liquescent_desc`, `rh_strophicus`, `rh_punctum_inclinatum`.

## Alternatives considered

1. **Freeze current values unconditionally**. Rejected: drawing into wrong widths is a bug that surfaces three weeks into the drawing phase and invalidates half the work.
2. **Open widths entirely, update snapshots as glyphs are drawn**. Rejected: one-PR-per-width cascades into dozens of snapshot updates in Rhena, each of which must be reviewed individually. Batching into one coordinated pass is strictly cheaper.
3. **Let the designer move widths during drawing without coordination**. Rejected: designer has no visibility into Rhena's snapshot surface area and cannot reason about downstream impact.

## Consequences

### Positive
- Drawing starts with widths that actually fit their target shapes.
- Rhena's snapshot surface gets one coordinated churn, not many.

### Negative
- Adds a pre-drawing coordination step that blocks v1 glyph authoring.
- Requires a Rhena maintainer to review width-adjustment PRs.

### Neutral
- Does not affect the final font's external-consumer contract (OTF users care about widths, not which pass set them).

## Post-decision note (2026-04-14 width review)

The width review ran after this ADR landed (see `docs/planning/width-review-2026-04-14.md` and round-2 review §5 at `docs/planning/claude-review-2-2026-04-14.md`). It found three overflow bugs in the abandoned-attempt widths inherited into the initial contract:

- `rh_virga`: advance 65 < body width 75 (foot extends to +55)
- `rh_liquescent_asc`: advance 140 < body width 145 (tail endpoint at +75)
- `rh_liquescent_desc`: advance 140 < body width 145 (mirror of asc)

Per the post-decision option A documented in round-2 review §5, **the font project's contract leads Rhena**. The three widths have been corrected in-place:

- `src/widths.json` (font project): `rh_virga=90`, `rh_liquescent_asc=160`, `rh_liquescent_desc=160`
- `docs/rhena-coordination/rhineland.contract.json` (staged for Rhena): same corrected values + `width_review` provenance field pointing at the analysis document

**Transient state**: Rhena's `crates/rhena-core/src/render_ir/glyphs/rhineland.rs` currently still contains the pre-review (buggy) widths. The coordinated adoption PR on the Rhena side will (a) update `rhineland.rs` with the new widths, (b) accept the resulting diplomatic-mode golden snapshot diffs, and (c) optionally land the contract-ownership migration (ADR-0003 Phase 3) together. The font project's `justfile` `copy-to-rhena` recipe is gated on that PR landing first — see `rhena_integration_plan.md` § 5 step 7.

After the coordinated PR merges, this ADR transitions from **Accepted (provisional policy)** to **Accepted (post-review values frozen for v1)** — the widths are locked until a new ADR authorizes another coordinated update.

## References

- `src/widths.json` — post-review v1 width contract
- `docs/rhena-coordination/rhineland.contract.json` — staged Rhena contract with corrected widths
- `docs/planning/width-review-2026-04-14.md` — the analysis that found the bugs
- `docs/planning/claude-review-2-2026-04-14.md` § 5 — round-2 review adopting option A
- `rhena_integration_plan.md` § 3.3
- `claude-review-2026-04-14.md` § 5
