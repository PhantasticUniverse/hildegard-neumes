# Glyph Priority Sheet (19 atoms)

Status: v1, 2026-04-14.
Scope: drawing-order tiers for the 19 Rhena-consumed atoms. Replaces the archived 40-glyph priority sheet at `docs/archive/glyph_priority_sheet_v0.5.md`.
Source: paleographic drawing briefs at `docs/paleographic_drawing_briefs.md`.

---

## Tier 1 — MVP (6 glyphs)

These are the glyphs needed to render the first line of **O Ecclesia** from Dendermonde Cod. 9 fol. 168v, which is ADR-0004's visual validation target in the Rhena project. Nail these first; everything else can follow.

| # | Glyph | Width | Why first |
| --- | --- | --- | --- |
| 1 | `rh_punctum` | 160 | Highest frequency atom. Its calligraphic register sets the visual language for all other atoms. Width 160 (body 130) set 2026-04-19 via trace-at-scale from punctum.png. |
| 2 | `rh_virga` | 120 | The defining Rhineland gesture. Head + thin descending stem + small foot hook. Width 120 (head 91 wide) set 2026-04-19 via trace-at-scale from virda.png; measured narrower than the punctum when calibrated to staff guidelines (earlier 240 "head matches punctum" assumption was eyeball-based and over-sized). |
| 3 | `rh_c_clef` | 134 | **Placeholder**: outline extracted from Bravura chantCclef (OFL 1.1) 2026-04-19 pending a Rhineland trace from `docs/reference/images/c_clef.png`. Functional stand-in so every staff has a clef during Phase C; replace with Rhineland shape when drawing time permits. |
| 4 | `rh_punctum_inclinatum` | 140 | Width 140 (body 110×65, ~85% of `rh_punctum`) set 2026-04-19 via trace-at-scale from `climacus.png`. Sharper left/right points than the punctum. Rhena stamps this atom N times for climacus cascades. |
| 5 | `rh_quilisma` | 280 | Width 280 (body 247×276) set 2026-04-19 via trace-at-scale from `quilisma.png`. Rising ornamental gesture with rounded humps — larger and more vertical than the earlier "flat ribbon" spec suggested; manuscript trace is authoritative. |
| 6 | `rh_pressus` | 240 | Line 1 has a pressus. Width 240 (body 207×219) set 2026-04-19 via trace-at-scale from `pressus.png`. 28-point single contour. Exercises the vertical+wave vocabulary that gates `rh_oriscus` and the liquescents. |

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
| 8 | `rh_strophicus` | 110 | Apostropha (Hildegard name); stamped 1×/2×/3× by Rhena for apostropha/bistropha/tristropha. Width 110 (body 73×54) set 2026-04-19 via trace-at-scale from the Lomer Symphonia chart row 5. |
| 9 | `rh_liquescent_asc` | 160 | Ascending liquescent (epiphonus). Small head + curved upward tail. Lighter stroke per Gardiner p. 92. Width corrected 140→160 by the 2026-04-14 review (tail overflow). |
| 10 | `rh_liquescent_desc` | 150 | Cephalicus (Hildegard name). Width 150 (body 120×238) set 2026-04-19 via trace-at-scale from manuscript. Round-loop head + descending calligraphic curl with interior void (two contours). |
| 11 | `rh_pes_line` | 12 | Thin ascending connector. Near-geometric hairline. |
| 12 | `rh_flexa_line` | 172 | Thin descending diagonal connector. Hairline. |

**Tier 2 completion criterion**: render *O viridissima virga* (Riesencodex f. 474r–v, Dendermonde for comparison) end-to-end without falling back to Tier 1 placeholders.

---

## Tier 3 — Structural + auxiliary (7 glyphs)

Non-calligraphic primitives (divisio bars, virgula) and less-common atoms (F-clef, deminutum). These complete the v1 set.

| # | Glyph | Width | Notes |
| --- | --- | --- | --- |
| 13 | `rh_divisio_minima` | 16 | Thin bar (1 staff space, above top line). SMuFL-aligned per ADR-0009. |
| 14 | `rh_divisio_maior` | 16 | Thin bar (2 staff spaces, centred on midline). SMuFL-aligned. |
| 15 | `rh_divisio_maxima` | 16 | Thin bar (3 staff spaces, centred). SMuFL-aligned. |
| 16 | `rh_divisio_finalis` | 120 | Two 16-du bars, 88-du gap. Width corrected 56→120 by ADR-0009 SMuFL alignment. |
| 17 | `rh_virgula` | 91 | Breath mark above staff. Width corrected 12→91 by ADR-0009 SMuFL alignment. |
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
