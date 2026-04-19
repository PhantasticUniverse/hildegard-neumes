# ADR-0009: SMuFL alignment for tradition-agnostic glyphs

- Status: Accepted
- Date: 2026-04-19
- Deciders: project maintainers
- Consulted: Rhena team (audit exchange 2026-04-19), Bravura font + `bravura_metadata.json`, SMuFL spec, ADR-0008 (paleographic fidelity arbitration)
- Tags: smufl, conventions, paleography, interop, scope

## Context

A conformance audit against the SMuFL reference fonts (Bravura, Leland, Petaluma, Gootville) and the SMuFL spec revealed three classes of drift in our font:

1. **OS/2 metrics**: we had ascender=800, descender=-200 (sum 1 em). Bravura, Leland, and Gootville all use 2012/-2012 (sum ≈ 4 em); Petaluma uses 1000/-1000. SMuFL consumers computing line height from these values were at risk of clipping tall glyphs or mis-spacing content.

2. **Tradition-agnostic glyph dimensions and y-positioning**: divisio_maior was 2× Bravura's height, divisio_maxima 2× as well, divisio_finalis half as wide, virgula 1/8 as wide. Our divisio_minima and virgula were positioned at y ∈ [0, +250] / [+200, +500] rather than SMuFL's [+250, +500] above-staff convention. These had no paleographic grounding — they were inherited from Rhena's abandoned `rhineland.rs`, which was placeholder code the Rhena team explicitly wrote off.

3. **Calligraphic glyph divergence**: punctum, virga, quilisma, clefs, etc. use Rhineland-distinct widths that differ from Bravura's square-notation equivalents. This divergence is **intentional and paleographic** (ADR-0008).

The question: keep the abandoned-module dimensions for zero Rhena-side churn, or align with SMuFL (Bravura) where there's no paleographic cost?

## Decision

The font aligns with SMuFL/Bravura conventions for all tradition-agnostic aspects and diverges only where Rhineland paleography demands it. Additionally, the font is positioned as a **standalone Rhineland OTF** — Rhena/Viriditas is the current primary consumer but not a privileged one; any SMuFL-aware consumer (Verovio, MuseScore, LilyPond, web `@font-face`) should work with our OTF.

### Align with SMuFL

**OS/2 metrics** (in `scripts/scaffold-ufo.py :: fontinfo_dict()`):
- `ascender`, `openTypeOS2TypoAscender`, `openTypeHheaAscender`, `openTypeOS2WinAscent` → **2000** du (was 800)
- `descender`, `openTypeOS2TypoDescender`, `openTypeHheaDescender` → **-2000** du (was -200)
- `openTypeOS2WinDescent` → **2000** du (unsigned; was 200)

Bravura uses 2012 exactly; we round to 2000 for tool simplicity. Still ≥ 2 em total vertical box (the SMuFL convention). Calligraphic glyphs have plenty of headroom for Phase C growth.

**Tradition-agnostic geometric glyphs** in `GEOMETRIC_FINAL_SHAPES` adopt Bravura's dimensions and **path-intrinsic y-positioning** (the outline itself carries the SMuFL y-offsets so a consumer embedding the path gets correct placement with no additional transform):

| Glyph | x-extent (du) | y-extent (du) | Staff spaces |
|---|---|---|---|
| `rh_divisio_minima`  | [0, 16]  | [+250, +500] | [+1.0, +2.0] — above staff |
| `rh_divisio_maior`   | [0, 16]  | [-250, +250] | [-1.0, +1.0] — centred |
| `rh_divisio_maxima`  | [0, 16]  | [-375, +375] | [-1.5, +1.5] |
| `rh_divisio_finalis` | [0, 120], bars [0,16] and [104,120] | [-375, +375] | [-1.5, +1.5] |
| `rh_virgula`         | [0, 91]  | [+255, +500] | [+1.02, +2.0] — above top line |

**Width contract** (`src/widths.json`, `docs/rhena-coordination/rhineland.contract.json`): `rh_divisio_finalis` 56 → 120; `rh_virgula` 12 → 91.

### Retain Rhineland divergence (per ADR-0008)

The **twelve calligraphic atoms** (`rh_punctum`, `rh_virga`, `rh_punctum_inclinatum`, `rh_quilisma`, `rh_oriscus`, `rh_strophicus`, `rh_pressus`, `rh_liquescent_asc`, `rh_liquescent_desc`, `rh_deminutum`, `rh_c_clef`, `rh_f_clef`) keep their Rhineland-distinct widths, proportions, and pen register. This is the paleographic identity of the font and the reason it exists as a separate OTF from Bravura.

**Compositional primitives** (`rh_pes_line`, `rh_flexa_line`) have no SMuFL equivalent — they are internal primitives a consumer's resolver rotates/scales at render time. They keep their own LSB-0 conventions.

### Out of scope

- **Generalizing `scripts/generate-rhena-glyphs.py` to extract from arbitrary SMuFL fonts (e.g. Bravura for Rhena's chant.rs)**. Declined 2026-04-19 for scope discipline: this project provides a Rhineland font, not SMuFL-extraction tooling. The script is MIT/Apache-dual (ADR-0006) and can be forked and adapted freely by downstream consumers.
- **Full origin-convention unification to LSB-0** across all 19 glyphs. Deferred to v2 per width-review § 3.1.
- **Populated SMuFL metadata sidecar** (`hildegard_metadata.json` engravingDefaults, glyphBBoxes, anchors). Deferred until Phase C completes; placeholder bboxes aren't worth advertising.

## Alternatives considered

1. **Preserve the abandoned `rhineland.rs` conventions** for minimal Rhena-side churn. Rejected: the abandoned module was written off by the Rhena team; its placeholder decisions have no paleographic or SMuFL grounding. Inheriting them is inheriting design errors. Rhena's in-tree rhineland.rs has `#[allow(dead_code)]` and is not live during the ADR-0009 placeholder period, so there's no snapshot churn to preserve.

2. **Match Bravura pixel-exactly (ascender=2012)**. Rejected for metrics — rounding to 2000 keeps the number tool-simple and is still ≥ 2 em per SMuFL convention. Accepted for glyph dimensions (we match Bravura's 16×500 divisio_maior, 16×750 divisio_maxima, 120×750 divisio_finalis, 91×245 virgula exactly).

3. **Full SMuFL alignment including LSB-0 origin unification for all 19 glyphs**. Rejected for v1 — affects calligraphic glyph registration and is already deferred per width-review § 3.1. This ADR's geometric-glyph subset captures most of the interop value without touching the calligraphic registration the drawing briefs depend on.

4. **Generalize codegen tool to support arbitrary SMuFL OTF extraction**. Declined: expands our role from "Rhineland font project" to "SMuFL extraction tooling provider." Tight scope is better for a focused project. Counter-proposal from the Rhena team to provide Bravura extraction for their `chant.rs` declined on the same grounds.

## Consequences

### Positive

- Well-formed SMuFL citizen: Verovio, MuseScore, and any SMuFL-aware consumer render our divisio/virgula glyphs at the correct SMuFL placements.
- Standalone font: consumers don't need to know about Rhena to use our OTF.
- Internally consistent with Rhena's own `chant.rs` dimensions (which already follow Bravura).
- Path-intrinsic y-positioning means the glyph data is self-describing; no per-consumer transform logic needed.
- Scope discipline: the project stays a font provider, not a general tooling provider.

### Negative

- OTF byte identity changes — the stripped-timestamp sha256 in the generated `rhineland_glyphs.rs` `@generated` header shifts. Not breaking, but visible in diffs.
- Any future Rhena-side adoption of the refreshed `rhineland.rs` must account for path-intrinsic y (divisio_minima / virgula carry their own placement; Rhena's resolver should embed paths as-is without additional y offsets).

### Neutral

- Rhena's `rhineland.rs` is in its ADR-0009 placeholder period (no live dispatch for diplomatic mode), so no immediate render impact of the width/height/y changes.
- Pipeline reproducibility unchanged; determinism strategy (ADR-0004) still applies.
- Calligraphic glyph drawing (Phase C) is unaffected; the briefs for the 12 Rhineland-distinct atoms remain authoritative.

## References

- Rhena team SMuFL audit exchange, 2026-04-19 (see `docs/planning/` for round-3 review + response chain)
- `reference-repos/musescore/fonts/bravura/Bravura.otf` and `bravura_metadata.json` (SMuFL reference)
- `reference-repos/smufl-gh-pages/metadata/glyphnames.json`, `ranges.json`, `classes.json`
- ADR-0008: Paleographic fidelity arbitration policy — companion for divergence decisions
- `docs/planning/width-review-2026-04-14.md` § 3.1 (origin convention v2 deferral)
- `docs/paleographic_drawing_briefs.md` §§ 13–19 (geometric glyph specs, SMuFL-aligned)
