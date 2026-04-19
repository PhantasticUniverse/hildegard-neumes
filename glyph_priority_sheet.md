# Glyph Priority Sheet (19 atoms)

Status: v1, 2026-04-14.
Scope: drawing-order tiers for the 19 Rhena-consumed atoms. Replaces the archived 40-glyph priority sheet at `docs/archive/glyph_priority_sheet_v0.5.md`.
Source: paleographic drawing briefs at `docs/paleographic_drawing_briefs.md`.

---

## Tier 1 — MVP (6 glyphs)

These are the glyphs needed to render the first line of **O Ecclesia** from Dendermonde Cod. 9 fol. 168v, which is ADR-0004's visual validation target in the Rhena project. Nail these first; everything else can follow.

| # | Glyph | Width | Why first |
| --- | --- | --- | --- |
| 1 | `rh_punctum` | 240 | Highest frequency atom. Its calligraphic register sets the visual language for all other atoms. Nail this first and the rest follow. |
| 2 | `rh_virga` | 90 | The defining Rhineland gesture. Drives visual identity of the whole font. Its head proportions determine the scale of everything else. Width corrected 65→90 by the 2026-04-14 review (foot overflow). |
| 3 | `rh_c_clef` | 110 | Every line of chant begins with a clef. Without it you cannot render a staff. Reference image: `docs/research/images/c_clef.png` (Dendermonde). |
| 4 | `rh_punctum_inclinatum` | 120 | Required for the climacus that appears in O Ecclesia line 1. Cheap to draw once `rh_punctum` is settled — it's a smaller, sharper sibling. |
| 5 | `rh_quilisma` | 170 | Line 1 has at least one quilisma. Its calligraphic undulation is distinctive and is a test of the designer's handling of wavy components, which informs `rh_oriscus` and `rh_pressus` next. |
| 6 | `rh_pressus` | 300 | Line 1 has a pressus. Exercises the vertical+wave vocabulary that gates `rh_oriscus` and the liquescents. |

**Tier 1 completion criterion**: the Rhena CLI command

```bash
cargo run -p hildegard-cli -- render fixtures/corpus/o-ecclesia-line1.rhena --mode diplomatic --output /tmp/o-ecclesia.svg
```

produces an SVG that visibly improves on the abandoned attempt when compared against `hildegard/docs/research/images/o_ecclesia_rhineland_line_01.png`.

---

## Tier 2 — O Ecclesia full coverage (6 glyphs)

Enough to render the full O Ecclesia antiphon (both lines) and typical Hildegard source material without visible gaps. These extend the calligraphic vocabulary built in Tier 1.

| # | Glyph | Width | Notes |
| --- | --- | --- | --- |
| 7 | `rh_oriscus` | 200 | Small punctum body + wavy tail (Gardiner pp. 93–94). Extrapolates from pressus wave work. Directional split (asc/desc) deferred to v2. |
| 8 | `rh_strophicus` | 160 | Apostropha/bistropha/tristropha all collapse to this atom in Rhena's resolver. Slight upturned flick distinguishes from plain punctum. |
| 9 | `rh_liquescent_asc` | 160 | Ascending liquescent (epiphonus). Small head + curved upward tail. Lighter stroke per Gardiner p. 92. Width corrected 140→160 by the 2026-04-14 review (tail overflow). |
| 10 | `rh_liquescent_desc` | 160 | Descending liquescent (cephalicus). Mirror of ascending. Used in *O viridissima virga* f. 474v. Width corrected 140→160 by the 2026-04-14 review. |
| 11 | `rh_pes_line` | 12 | Thin ascending connector. Near-geometric hairline. |
| 12 | `rh_flexa_line` | 172 | Thin descending diagonal connector. Hairline. |

**Tier 2 completion criterion**: render *O viridissima virga* (Riesencodex f. 474r–v, Dendermonde for comparison) end-to-end without falling back to Tier 1 placeholders.

---

## Tier 3 — Structural + auxiliary (7 glyphs)

Non-calligraphic primitives (divisio bars, virgula) and less-common atoms (F-clef, deminutum). These complete the v1 set.

| # | Glyph | Width | Notes |
| --- | --- | --- | --- |
| 13 | `rh_divisio_minima` | 16 | Thin short vertical bar (one staff space). Geometric. |
| 14 | `rh_divisio_maior` | 16 | Thin bar spanning full 4-line staff. Geometric. |
| 15 | `rh_divisio_maxima` | 16 | Thin bar extending above + below staff. Geometric. |
| 16 | `rh_divisio_finalis` | 56 | Double vertical bar. Geometric. |
| 17 | `rh_virgula` | 12 | Small tick breath mark above the staff. |
| 18 | `rh_deminutum` | 100 | Tiny angular mark for diminutive liquescence. Smallest atom. |
| 19 | `rh_f_clef` | 160 | F-clef for low-range antiphons. No direct reference image — extrapolate from C clef + standard F-clef convention. |

**Tier 3 completion criterion**: v1.0 font release. Passes a full-Symphonia rendering test against at least five antiphons spanning both Dendermonde and Riesencodex sources.

---

## Pre-drawing blockers (per ADR-0005)

**Do NOT start drawing until these are resolved**:

1. **Coordinated width review with Rhena** (ADR-0005). Several widths flagged as potentially provisional: `rh_divisio_minima/maior/maxima` (all 16, purely-vertical assumption to verify), `rh_pes_line` (12) vs `rh_flexa_line` (172) consistency, `rh_punctum/virga/pressus` calligraphic mass room. Land one PR against Rhena with any adjustments + golden-snapshot update.
2. **UFO3 source scaffold** (ADR-0001). Create `src/hildegard-neumes.ufo/` with 19 empty glyph slots matching the names and widths in `src/glyph-names.json` + `src/widths.json`.
3. **Contract ownership migration** (ADR-0003, optional but recommended). Rhena adopts `docs/rhena-coordination/rhineland.contract.json` as the single source of truth; font project then reads from a pinned copy.
4. **Codegen test suite** (ADR-0002). `tests/` directory with pytest + minimal.otf fixture. Prevents silent regressions in the codegen path.

---

## Drawing guidance

Common to all atoms: see `docs/paleographic_drawing_briefs.md` § "Stroke register (common to all atoms)". Key points:

- **Broad-nib pen at ~28° above horizontal**, rectangular nib width ~60–75 em-units.
- **Thin calligraphic strokes**, NOT thick square noteheads (not Hufnagelschrift, not Solesmes square).
- **Rounder than Hufnagel, heavier than St Gall**. Heighted on 4-line staff.
- **Liquescents are lighter**: ~70% nib pressure, rounded terminals (Gardiner p. 92).
- **Each atom origin** sits at its pitch anchor (centre of body for punctum; centre of head for virga; top of vertical for pressus), NOT at the bottom of the glyph.

Per-glyph specifics — reference `docs/paleographic_drawing_briefs.md` §§ 1–19.

---

## What explicitly NOT to draw (v1)

Per ADR-0005, review § 13, and glyph inventory v0.5b addenda:

- No accidentals (v2 — constitution §13.1 Gregorio parity target, coordinate with Rhena)
- No directional oriscus split (deferred to v2; Rhena resolver expects a single `rh_oriscus` atom)
- No bistropha/tristropha as dedicated atoms (Rhena stamps multiple `rh_strophicus` copies)
- No dedicated compound glyphs for Hildegard-idiosyncratic forms (RN-021 `flexa_resupina_pressus_subbipunctis` and RN-022 `flexa_resupina_pressus_liquescens` are **assembled** by Rhena's resolver from the 19 atoms, not rendered as compound glyphs)
- No tractulus, torculus rotundus/quadratus split, climacus resupinus, pes subpunctis as dedicated glyphs (Humdrum-only attestations, not in Rhena's NeumeClass enum anyway; deferred to v2 pending direct manuscript verification)
- No GSUB/GPOS rules (not used by Rhena; v2 consideration for Verovio secondary consumer)
