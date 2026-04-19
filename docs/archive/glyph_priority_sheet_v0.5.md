# Glyph Priority Sheet

Status: v1, 2026-04-14.
Scope: ordered drawing roadmap for the Hildegard Rhineland neume font. Tiers define the order in which glyphs should be drawn, so the font becomes useful at each checkpoint rather than only at v1-complete.
Prereq: direct manuscript reading pass against Riesencodex f. 470r and Dendermonde plates. Do **not** draw Tier 1 from memory or from square-notation references.

---

## Tier 0 — Verovio baseline (reuse Bravura, no drawing needed)

These are fine to leave as Bravura defaults in the MVP. Revisit when Tier 3 finishes.

| Codepoint | Name | Notes |
| --- | --- | --- |
| U+E8F0 | `chantStaff` | 4-line Rhineland staff; colour applied by JS post-processor |
| U+E8F3–U+E8F6 | `chantDivisioMinima / Maior / Maxima / Finalis` | Phrase/section dividers |
| U+E8F7 | `chantVirgula` | Short breath mark |
| U+E906 | `chantCclef` | Movable C-clef |
| U+E902 | `chantFclef` | F-clef (if needed for low-range antiphons) |

---

## Tier 1 — MVP prototype (10 glyphs, ~1 weekend of drawing)

**Goal**: render a short MEI antiphon end-to-end in the Verovio fork. Proves the whole pipeline. Matches Gardiner Fig. 6 (p. 91) — the eight basic neumes from Riesencodex f. 470r — minus climacus/scandicus (assembly-first; see Tier 1 assembly notes).

| # | Codepoint | Glyph name | Inventory ref | Source to trace |
| --- | --- | --- | --- | --- |
| 1 | U+E990 | `chantPunctum` (Rhineland register) | RN-003 | Riesencodex f. 470r, plate 3 per Gardiner Fig. 6 |
| 2 | U+E996 | `chantPunctumVirga` (Rhineland register) | RN-001 | f. 470r, plate 1 |
| 3 | U+F400 | `hildegard.dot_punctum` | Component (new v0.5) | f. 470r — the dots in climacus/scandicus |
| 4 | U+E99B | `chantQuilisma` (Rhineland — jagged wave with ascending tail) | RN-019 | f. 470r or directly from a quilisma occurrence in *O viridissima virga* f. 474r |
| 5 | U+F420 | `hildegard.pes` | RN-005 | f. 470r, plate 3 |
| 6 | U+F422 | `hildegard.flexa` | RN-007 (Gardiner "clivis") | f. 470r, plate 4 |
| 7 | U+F440 | `hildegard.torculus_rotundus` | RN-029 | f. 470r, plate 7. **Note**: verify whether D/R distinguishes rotundus vs quadratus before committing. If not, drop "rotundus" suffix. |
| 8 | U+F443 | `hildegard.porrectus` | RN-032 | f. 470r, plate 8 (Gardiner "porrectus") |
| 9 | U+F460 | `hildegard.cephalicus` | RN-012 | f. 474v, word "frumentum" — Gardiner p. 60, Ex. 9 |
| 10 | U+F402 | `hildegard.rounded_liquescent_terminal` | Component (new v0.5) | f. 474v liquescent occurrences |

**Assembly-first in Tier 1** (no new glyphs, composed from Tier 1 atoms at render time):
- climacus: virga + descending chain of dot-puncta
- scandicus: punctum + ascending chain of dot-puncta

**Tier 1 completion criterion**: render the MEI fragment in `examples/mei_encoding_reference.md` §1 end-to-end on the Verovio fork, visible in a browser, with the yellow-C / red-F staff. This is the minimal proof-of-life.

---

## Tier 2 — Core families (~15 glyphs)

**Goal**: enough to render a typical Hildegard antiphon without visible gaps. Covers all Gardiner-attested fixed families, plus the most common modified-family members.

| # | Codepoint | Glyph name | Inventory ref | Notes |
| --- | --- | --- | --- | --- |
| 11 | U+E99F | `chantStrophicus` / `apostropha` | RN-009 | Atomic. |
| 12 | U+F424 | `hildegard.bistropha` | RN-010 | Repetition pair. |
| 13 | U+F425 | `hildegard.tristropha` | RN-011 | Repetition triple. |
| 14 | U+E99C | `chantOriscusAscending` | RN-028a | Gardiner pp. 93–94 — "small note with a wavy component." |
| 15 | U+E99D | `chantOriscusDescending` | RN-028b | |
| 16 | U+F421 | `hildegard.pes_flexus` | RN-006 | Note slight uplift in tail distinguishing from flexa (Gardiner p. 15). |
| 17 | U+F423 | `hildegard.flexa_resupina` | RN-008 | Gardiner "porrectus" is this shape; verify synonymy in manuscripts. |
| 18 | U+F403 | `hildegard.pressus_core` | Component | Vertical line + short undulating line (Gardiner p. 94). |
| 19 | U+F480 | `hildegard.pressus` | RN-016 | Built on pressus-core component. |
| 20 | U+F481 | `hildegard.pressus_liquescens` | RN-017 | pressus-core + rounded-liquescent-terminal. Gardiner p. 60 contrasts this with cephalicus. |
| 21 | U+F404 | `hildegard.quilisma_jagged_core` | Component | Never free-standing; attaches to ascending tail. |
| 22 | U+F405 | `hildegard.ascending_tail_connector` | Component | Quilisma tail; possibly reused in other rising connectors. |
| 23 | U+F461 | `hildegard.epiphonus` | RN-013 | Ascending liquescent. **Humdrum-only attestation** — verify against manuscripts before committing. |
| 24 | U+F462 | `hildegard.pes_liquescens` | RN-014 | |
| 25 | U+F406 | `hildegard.subpunctis_tail` | Component | Descending dot-puncta chain; variable length at render time. |

**Tier 2 completion criterion**: render *O viridissima virga* (Riesencodex f. 474r–v, Dendermonde for comparison) end-to-end in MEI without falling back to Tier 1 placeholders.

---

## Tier 3 — Full v1 inventory + Hildegard-idiosyncratic compounds (~15 glyphs)

**Goal**: complete v1. The Hildegard-specific showpieces (RN-021, RN-022) land here because they are the project's signature glyphs and should be drawn only after the component library (pressus-core, subpunctis-tail, rounded-liquescent-terminal) is stable enough to build them on.

| # | Codepoint | Glyph name | Inventory ref | Notes |
| --- | --- | --- | --- | --- |
| 26 | U+F482 | `hildegard.pressus_subpunctis` | RN-018 | pressus-core + subpunctis-tail. |
| 27 | U+F464 | `hildegard.pes_subpunctis` | RN-035 | pes + subpunctis-tail. **Humdrum-only attestation** — verify. |
| 28 | U+F463 | `hildegard.pes_flexus_liquescens` | RN-015 | |
| 29 | U+F444 | `hildegard.porrectus_flexus` | RN-033 | **Not explicitly in Gardiner** — inferred. Verify. |
| 30 | U+F442 | `hildegard.torculus_resupinus` | RN-031 | Gardiner Fig. 5 p. 77 — but from a square-notation comparison. Verify Rhineland form. |
| 31 | U+F441 | `hildegard.torculus_quadratus` | RN-030 | **Humdrum-only** distinction from rotundus. **Must verify** against manuscripts. Drop entirely if D/R doesn't distinguish. |
| 32 | U+F4A0 | `hildegard.flexa_resupina_pressus_subbipunctis` | **RN-021** | **Hildegard-idiosyncratic compound.** Gardiner p. 16. Built from flexa_resupina core + pressus-core + subpunctis-tail. Project showpiece. |
| 33 | U+F4A1 | `hildegard.flexa_resupina_pressus_liquescens` | **RN-022** | **Hildegard-idiosyncratic compound.** Gardiner p. 16. Built from flexa_resupina core + pressus-core + rounded-liquescent-terminal. Project showpiece. |
| 34 | U+E9D8 | `chantEpisema` | — | Only if attested in D/R — verify first. |
| 35 | U+E9D9 | `chantAugmentum` | — | Only if attested. |
| 36 | U+F407 | `hildegard.torculus_round_head` | Component | Only if drawing both torculus variants. |
| 37 | U+F408 | `hildegard.torculus_square_head` | Component | Only if drawing both torculus variants. |
| 38 | U+EA04–U+EA09 | custos stem-up / stem-down positions | — | 6 glyphs if custos appears in Rhineland sources. |

**Tier 3 completion criterion**: v1.0 font release. Passes a full *Symphonia* antiphon rendering test against at least 5 different antiphons spanning D and R sources.

---

## Tier 4 — Deferred / conditional (post-v1)

Held until either direct manuscript verification justifies drawing or until user demand for the specific form arises.

| Glyph | Inventory ref | Hold reason |
| --- | --- | --- |
| `hildegard.tractulus` | RN-027 | **Humdrum-only.** Gardiner does not distinguish it from punctum. Draw only if D/R plates show a visually distinct short-horizontal-dash form. |
| `hildegard.climacus_resupinus` | RN-034 | **Humdrum-only.** Probably composable from climacus + ascending connector at render time; dedicated glyph may be unnecessary. |
| Precomposed convenience sub-font | — | For Word/Illustrator users who won't run Verovio. Ship reactively after knowing which 30–50 shapes editorial designers actually ask for. |
| Stylistic set `ss01` / `ss02` for alternate traditions | — | E.g., a "Dendermonde hand" vs "Riesencodex Hand A" stylistic switch. Only if the direct manuscript pass shows meaningful visual distinction and users need it. |
| Two-colour SVG-in-OT staff glyphs | — | Rejected in v1 for compat reasons; revisit if the JS post-processor approach hits a wall. |
| Alternate St-Gall / Hufnagel comparison glyphs | — | For editorial contexts showing Rhineland next to comparable traditions. Pure nice-to-have. |

---

## Drawing guidance (all tiers)

1. **Always trace from the manuscripts, not from Solesmes references.** IMSLP Dendermonde, HLB RheinMain Riesencodex. Viewer URLs in `README.md`.
2. **Draw at em = 2048** (Verovio's standard; matches Bravura).
3. **Keep all glyphs baseline-anchored and staff-position-agnostic.** Verovio positions glyphs on the staff; the font contributes shapes, not staff placement.
4. **Reuse components** where possible. A pes_liquescens is pes-core + rounded-liquescent-terminal, drawn as one glyph but sourced from two components in the `.sfd`. Gregorio's `squarize.py` pattern applies here: maintain the small component set in the source, generate composites at build time.
5. **Stroke register** is "between St Gall and Hufnagelschrift" (van Poucke via Gardiner pp. 25–26). Rounder than Hufnagel's horseshoe-nail virga; heavier than St Gall's pointed-pen forms. Ink-forward. Liquescents are lighter and rounded (Gardiner p. 92).
6. **Verify every Humdrum-only entry against direct manuscript inspection before drawing.** Do not commit to glyph shapes for tractulus / torculus rotundus+quadratus split / climacus resupinus / pes subpunctis / epiphonus until you have seen them in D or R.
7. **Each new glyph gets a row in `hildegard_metadata.json`** with its codepoint, SMuFL or Hildegard name, and a paleographic source citation. Don't defer metadata.
