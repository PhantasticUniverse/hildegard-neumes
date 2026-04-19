# Rhena Integration Plan — PRIMARY consumer

Status: v1, 2026-04-14.
Scope: how the Hildegard Neume font integrates with the Rhena/Viriditas Rust project at `/Users/xaviermac/Documents/2_Areas/Coding-Projects/hildegard`. This is the **primary** integration path for the font.
Supersedes: `verovio_integration_plan.md` (demoted to secondary-consumer reference).
Companion: `README.md`, `glyph_inventory_v0.5.md` § 0.2.

---

## 0. Frame

The Hildegard Neume font exists because of the Rhena (Viriditas) project at `../hildegard`. Rhena is a compiler-first, Hildegard-first notation platform:

> **Rhena DSL → Parser → Semantic IR → Render IR → Renderers (diplomatic, normalized) + Adapters (MEI, TEI, IIIF, GABC, search)**

Rhena already has a working end-to-end pipeline (Phase 3 complete, 133 tests passing, MEI export landed, diagnostic system, Gregorio parity in progress per constitution §13.1). **What it does not have** is a proper font. It has an experimental inline-Rust attempt at Rhineland neume glyphs that was explicitly abandoned. Replacing that attempt — cleanly, architecturally, long-term — is what this font project is for.

## 1. What exists in Rhena today (the abandoned attempt)

Two Rust modules in `hildegard/crates/rhena-core/src/render_ir/glyphs/`:

- `rhineland.rs` — 232 lines, **19 glyphs**, Rhineland tradition. Hand-coded SVG path strings in `pub const` declarations. Example:
  ```rust
  pub const VIRGA: Glyph = Glyph {
      name: "rh_virga",
      path: "M-20 20 L-12 -8 L-8 500 L8 500 L12 -5 L55 25 L40 35 Z",
      width: 65,
  };
  ```
- `square.rs` — 113 lines, **17 glyphs**, SMuFL square tradition. Paths extracted by hand from Bravura.svg.

Both modules expose the same `Glyph { name: &'static str, path: &'static str, width: u16 }` shape. The resolver in `glyphs/mod.rs` (functions `resolve_rhineland` and `resolve_square`) picks an atom per neume *component* based on position (`is_first`, `is_last`, `is_descending_from_prev`), `NeumeClass`, ornamental role, and liquescent status. Multi-component neumes (pes, flexa, torculus, porrectus, climacus) are **assembled at render time from atoms**, not rendered as whole-neume compound glyphs. A `Pes` is `PUNCTUM + VIRGA`; a `Climacus` is `VIRGA + PUNCTUM_INCLINATUM × n`; a `Pressus` is `PRESSUS + ...`. The SVG backend embeds all glyph path data in a `<defs>` block and uses `<use xlink:href="#glyph_name" x="..." y="..."/>` references for placement.

**Why the inline approach was abandoned.** The existing Rhineland paths are crude geometric placeholders — `PUNCTUM` is a parallelogram with cubic smoothing, `VIRGA` is a thin stem with a triangular foot extension (`L55 25 L40 35` — a blunt hand-traced corner), `QUILISMA` is a 3-tooth straight-line zigzag, `ORISCUS` is an elliptical S-curve, `PRESSUS` is just a wider punctum. They are functional for layout proof-of-concept but do not look like Rhineland calligraphy. Beyond aesthetics, the approach has structural problems:

1. **Glyph design is baked into source code.** Every visual tweak is a code change. Font editors (FontForge, Glyphs, Fontlab) cannot open a `.rs` file.
2. **No iteration loop for a designer.** The authoring-export-test cycle runs through `cargo build`, not a design tool.
3. **No external consumability.** The shapes exist only inside Rhena. Illustrator, Word, LilyPond, Verovio, a future C++ or web consumer — none can reuse these glyphs. This violates the constitution's hostile-design Rule 7: *"Do not make the project depend on one renderer forever."*
4. **No font metrics beyond width.** No ascent, descent, bbox, kern table, anchors, hinting. The `width: u16` field is the entire metric surface.
5. **Bravura is duplicated, not referenced.** `square.rs` is a hand-copied snapshot of Bravura paths. Bravura updates do not propagate; bugs in extraction cannot be traced back to upstream.
6. **Aesthetic quality scales with hand-typing patience.** Calligraphic neumes are exactly the kind of shape where a font editor — with bezier point manipulation, shape rotation, stroke-to-fill conversion, visual preview — is dramatically better than typed path strings.

The user's directive is unambiguous: *"The attempted font was experimental and abandoned for a reason. Be sure to do what is best long term."* Long term means: **a real font file authored in real font tooling**, not hand-typed paths.

## 2. Decision: real OpenType font + compile-time codegen

**The font project's primary artifact is `hildegard-neumes.otf`** — a real OpenType font, authored in FontForge (or Glyphs / FontLab / UFO3), exported via the font tool's native build pipeline.

**The Rhena project consumes it via a codegen step.** A small script (Python, to avoid adding a Rust build dependency to Rhena) reads the `.otf`, extracts per-glyph SVG path data and advance widths, and emits a `rhineland_glyphs.rs` file matching Rhena's existing `Glyph { name, path, width }` API. The generated file is committed to Rhena's source tree as `crates/rhena-core/src/render_ir/glyphs/rhineland.rs`, marked with a `// @generated` sentinel header.

**Why compile-time codegen rather than runtime font loading:**

- **Determinism.** Rhena's golden-regression doctrine (constitution §10.1) requires byte-stable renders. Compile-time path strings are stable; runtime font parsing introduces a moving part.
- **WASM size.** Rhena compiles to WASM (ADR-0002). Every runtime dep counts. `ttf-parser` or `fonttools-rs` would add 50–200 KB to the wasm bundle for no benefit over pre-generated paths.
- **Zero new Rhena dependencies.** The Rhena build stays pure Rust 1.85+. The font project is out-of-tree.
- **Preserved contract.** The `Glyph` struct, resolver logic, SVG backend, and all 133 existing Rhena tests stay unchanged. Integration is a file replacement, not a refactor.
- **Iteration loop.** The font designer iterates in a font editor, exports the `.otf`, runs one Python command, copies the generated file into Rhena, runs `just check`. Feedback loop in minutes, not hours.

**Architecture diagram:**

```
hildegard-neumes/                       hildegard/  (Rhena)
├── src/                                ├── crates/rhena-core/src/render_ir/glyphs/
│   └── hildegard-neumes.sfd            │   ├── mod.rs           (unchanged, resolver)
│                                       │   ├── rhineland.rs     ← GENERATED from .otf
├── build/                              │   └── square.rs        (unchanged, Bravura)
│   ├── hildegard-neumes.otf            │
│   ├── hildegard-neumes.woff2          │
│   └── hildegard-neumes-metadata.json  │
│                                       │
├── scripts/                            │
│   ├── build-font.sh                   │
│   └── generate-rhena-glyphs.py  ─────→│  outputs rhineland.rs
│                                       │
├── generated/                          │
│   └── rhineland_glyphs.rs             │
```

The font project is the single source of truth. Rhena is a downstream consumer. The `generated/rhineland_glyphs.rs` file sits in the font project's tree as a build artifact; copying it into Rhena is the integration step.

## 3. Stable API contract with Rhena

The following are **hard constraints** the font project must preserve. Changing any of them requires a coordinated Rhena-side update and a CHANGELOG note in Rhena.

### 3.1 Glyph struct shape

```rust
#[derive(Debug, Clone)]
pub struct Glyph {
    pub name: &'static str,
    pub path: &'static str,
    pub width: u16,
}
```

The generated `rhineland.rs` must produce `pub const` declarations of this exact shape. No field additions without coordination.

### 3.2 Glyph names (stable IDs)

Rhena's resolver (`glyphs/mod.rs`) references glyphs by the `rh_` string prefix. The current atomic set is:

| Rhena constant | Glyph name string | SMuFL mapping (for OTF codepoint) |
| --- | --- | --- |
| `PUNCTUM` | `rh_punctum` | `chantPunctum` U+E990 |
| `VIRGA` | `rh_virga` | `chantPunctumVirga` U+E996 |
| `PUNCTUM_INCLINATUM` | `rh_punctum_inclinatum` | `chantPunctumInclinatum` U+E991 |
| `QUILISMA` | `rh_quilisma` | `chantQuilisma` U+E99B |
| `ORISCUS` | `rh_oriscus` | `chantOriscusAscending` U+E99C (directional split deferred) |
| `STROPHICUS` | `rh_strophicus` | `chantStrophicus` U+E99F |
| `PRESSUS` | `rh_pressus` | private PUA U+F403 (no SMuFL equivalent for Rhineland pressus core) |
| `LIQUESCENT_ASC` | `rh_liquescent_asc` | `chantAuctumAsc` U+E994 |
| `LIQUESCENT_DESC` | `rh_liquescent_desc` | `chantAuctumDesc` U+E995 |
| `DEMINUTUM` | `rh_deminutum` | `chantPunctumDeminutum` U+E9A1 |
| `C_CLEF` | `rh_c_clef` | `chantCclef` U+E906 |
| `F_CLEF` | `rh_f_clef` | `chantFclef` U+E902 |
| `DIVISIO_MINIMA` | `rh_divisio_minima` | `chantDivisioMinima` U+E8F3 |
| `DIVISIO_MAIOR` | `rh_divisio_maior` | `chantDivisioMaior` U+E8F4 |
| `DIVISIO_MAXIMA` | `rh_divisio_maxima` | `chantDivisioMaxima` U+E8F5 |
| `DIVISIO_FINALIS` | `rh_divisio_finalis` | `chantDivisioFinalis` U+E8F6 |
| `VIRGULA` | `rh_virgula` | `chantVirgula` U+E8F7 |
| `PES_LINE` | `rh_pes_line` | private PUA (connector, no SMuFL) |
| `FLEXA_LINE` | `rh_flexa_line` | private PUA (connector, no SMuFL) |

**19 atomic shapes.** This is the v1 inventory. Connectors (`rh_pes_line`, `rh_flexa_line`) are arguably not "glyphs" in the font sense — they're thin geometric primitives used for ascending/descending stroke joins — but the Rhena resolver treats them uniformly, so they live in the font for consistency. They can be extracted from simple straight-line paths; no font-editor work required beyond defining them.

### 3.3 Design space and coordinate convention

- **Em square: 1000 units.** Matches Bravura (SMuFL convention) and the existing `rhineland.rs` assumptions.
- **Y-up.** Font-native convention. Rhena's SVG backend applies a flip transform at render time.
- **Advance widths in u16 (0–65535).** The `width` field in `Glyph` is `u16`.
- **Widths must match the font-project contract** (`src/widths.json` and `docs/rhena-coordination/rhineland.contract.json`). The 2026-04-14 width review (`docs/planning/width-review-2026-04-14.md`) found three overflow bugs in the inherited values and corrected them; the font project now leads Rhena until the coordinated adoption PR lands. Post-review widths:

| Glyph | Width (u16) | Note |
| --- | --- | --- |
| rh_punctum | 240 | |
| rh_virga | 90 | **post-review; was 65** |
| rh_punctum_inclinatum | 120 | |
| rh_quilisma | 170 | |
| rh_oriscus | 200 | |
| rh_strophicus | 160 | |
| rh_pressus | 300 | |
| rh_liquescent_asc | 160 | **post-review; was 140** |
| rh_liquescent_desc | 160 | **post-review; was 140** |
| rh_deminutum | 100 | |
| rh_c_clef | 110 | |
| rh_f_clef | 160 | |
| rh_divisio_minima | 16 | |
| rh_divisio_maior | 16 | |
| rh_divisio_maxima | 16 | |
| rh_divisio_finalis | 56 | |
| rh_virgula | 12 | |
| rh_pes_line | 12 | |
| rh_flexa_line | 172 | |

Rhena's in-tree `rhineland.rs` still carries the pre-review values (65/140/140) as of this writing; the coordinated adoption PR on the Rhena side brings the width updates and the diplomatic-mode golden-snapshot updates together in one commit. After that PR lands, widths are frozen for v1 pending a v2 ADR.

### 3.4 SVG path data discipline

Rhena's SVG backend concatenates glyph `path` strings directly into the output SVG as `<path d="..."/>` (via `<use>` on path data stored in `<defs>`). The generator must produce path strings that:

- Use only `M`, `L`, `C`, `Q`, `Z` commands (absolute). These are what the existing inline paths use and what Rhena's backend handles. Avoid `A` (arcs) and lowercase (relative) forms for byte-stability.
- Use integer coordinates (or at most one decimal place). Rhena's existing paths are all integer — keeps byte-stable diffs.
- Start each glyph at its own origin (0, 0 is the reference point for advance-width layout).
- Omit transforms, opacity, stroke attributes — everything is a filled path.

The Python codegen script must **normalize** FontForge's exported paths to meet these constraints. FontForge's default SVG export uses lowercase relative commands; the generator converts to absolute uppercase.

### 3.5 Generated file format

```rust
//! @generated by hildegard-neumes/scripts/generate-rhena-glyphs.py
//! Source: hildegard-neumes v{VERSION}, hildegard-neumes.otf, sha256:{HASH}
//! Do not edit by hand — regenerate via `python scripts/generate-rhena-glyphs.py`.
//!
//! Custom Rhineland neume glyph paths for diplomatic rendering.
//! Traced from Dendermonde Cod. 9 and Wiesbaden Riesencodex Hs. 2.
//! Coordinate system: 1000-unit em, Y-up, flipped by SVG transform at render scale.
//!
//! ADR-0004: Rhineland neume glyphs for diplomatic rendering.

use super::Glyph;

pub const PUNCTUM: Glyph = Glyph {
    name: "rh_punctum",
    path: "M... L... Z",
    width: 240,
};
// … 18 more …

pub const ALL_GLYPHS: &[&Glyph] = &[
    &PUNCTUM, &VIRGA, /* … */
];
```

The header's `@generated` marker signals to any reviewer (and to CI linters like `generated-file-check`) that the file is a build output. The sha256 of the source `.otf` gives a tamper-evident link from source to generation.

## 4. Build pipeline

The font project's primary build commands:

```bash
# One-time setup: FontForge + Python 3.11+ + fontTools
brew install fontforge
pip install fonttools

# Build the font from source
fontforge -lang=ff -c 'Open("src/hildegard-neumes.sfd"); Generate("build/hildegard-neumes.otf"); Generate("build/hildegard-neumes.woff2");'

# Generate Rhena consumer file
python scripts/generate-rhena-glyphs.py \
  --in build/hildegard-neumes.otf \
  --names-map src/glyph-names.json \
  --widths-table src/widths.json \
  --out generated/rhineland_glyphs.rs

# Copy into Rhena (manual; or via a justfile target in Rhena)
cp generated/rhineland_glyphs.rs ../hildegard/crates/rhena-core/src/render_ir/glyphs/rhineland.rs
cd ../hildegard && just check
```

`glyph-names.json` is the name-mapping table from § 3.2, machine-readable so the generator can look up Rhena constants per glyph. `widths.json` is the width-preservation table from § 3.3 used to assert that the font's advance widths match the Rhena contract; a mismatch is a build error.

## 5. The v1 MVP: replace the abandoned attempt

**Goal of v1**: swap `rhineland.rs` in Rhena from 19 hand-typed geometric approximations to 19 FontForge-authored calligraphic shapes, with no other changes to Rhena's code path.

Steps:

1. **Set up the font source.** Create `hildegard-neumes/src/hildegard-neumes.sfd` in FontForge. Establish em=1000, define the 19 glyph slots with Rhena-compatible names, leave them empty.
2. **Trace from Dendermonde fol. 168v.** The existing `hildegard/docs/research/images/` directory contains reference captures: `o_ecclesia_rhineland_line_01.png`, `punctum.png`, `virda.png`, `climacus.png`, `flexa.png`, `pes_short.png`, `pes_long.png`, `pressus.png`, `quilisma.png`, `quilisma+pressus.png`, `c_clef.png`. These are the starting traces — plus direct reads of the IMSLP Dendermonde PDF and the HLB RheinMain Riesencodex PDF (URLs in README).
3. **Draw the 19 atomic shapes in FontForge.** Match the paleographic register: thin calligraphic pen strokes, not geometric blocks. Preserve the advance widths from § 3.3 (set sidebearings to match).
4. **Export the OTF.** FontForge-native.
5. **`generate-rhena-glyphs.py` is already written** (`scripts/generate-rhena-glyphs.py`, ~790 lines, `fontTools` + hand-rolled path normalizer — no `svgpathtools` dependency). It loads the OTF, iterates glyphs in contract order, converts each glyph's outline via `SVGPathPen`, normalizes to absolute uppercase integer commands, validates widths against `src/widths.json`, and emits `rhineland_glyphs.rs`.
6. **Copy the generated file into Rhena** at `crates/rhena-core/src/render_ir/glyphs/rhineland.rs`. Replace the existing file verbatim.
7. **Run `just check` in Rhena.** Expect golden-test churn (the output SVG paths have changed). Review the diffs visually; if the new shapes are correct, update the snapshots (`cargo insta accept` or equivalent). Commit.
8. **Render `o-ecclesia-line1.rhena` in diplomatic mode** and compare against `hildegard/docs/research/images/o_ecclesia_rhineland_line_01.png`. This is the project's existing visual-comparison validation per ADR-0004's "Validation plan" section.

**MVP done** when: Rhena renders the O Ecclesia first line in diplomatic mode and the output visually resembles the Dendermonde manuscript, meaningfully better than the current geometric placeholders.

## 6. v2 and beyond (coordinated with Rhena)

Once v1 ships, open ADRs in the Rhena project for these coordinated expansions:

1. **Accidentals.** The Rhena constitution §13.1 Gregorio-parity matrix calls for "witness-varying accidentals" (9 variants per CLAUDE.md Tier 2 §2.1). Neither `rhineland.rs` nor `square.rs` has accidental glyphs today. Propose: add `rh_flat`, `rh_natural`, `rh_sharp`, plus editorial variants (`rh_flat_paren`, `rh_flat_soft`, etc.). Requires (a) new font glyphs, (b) a resolver extension in `glyphs/mod.rs`, (c) a Render IR field for accidentals on the appropriate element.
2. **Directional oriscus.** `square.rs` already has `sq_oriscus_asc` and `sq_oriscus_desc`. `rhineland.rs` has a single `rh_oriscus`. Propose a directional split.
3. **Dominican and Minimis divisions.** TODO comments in `glyphs/mod.rs` lines 99–110 note these fall back to virgula. Propose dedicated glyphs.
4. **Custos.** If Rhineland manuscripts attest custos at line ends, add `rh_custos_up`, `rh_custos_down` variants.
5. **Strophic-family differentiation.** Currently all of `Apostropha | Bistropha | Tristropha` map to the same `rh_strophicus`. Propose separate atoms if the Dendermonde/Riesencodex hand distinguishes them visually.
6. **Width review.** Revisit the v1-frozen widths once the shapes are settled. Coordinate with Rhena for a single golden-snapshot update.

These are all future work. v1 is strictly a quality replacement of the 19 abandoned atoms.

## 7. Secondary consumers (the font is not Rhena-only)

Though Rhena is the primary consumer, the OTF deliverable is explicitly designed to work outside Rhena:

- **Verovio** (see `verovio_integration_plan.md`, now archived as secondary). The OTF can be installed as a custom SMuFL font in a Verovio fork. SMuFL codepoints (per § 3.2 and `smufl_codepoint_mapping.md`) are exactly for this. Verovio's per-component dispatch is architecturally similar to Rhena's, so the same 19 atoms suffice.
- **Illustrator, Word, InDesign.** Users can paste glyphs via PUA codepoints listed in `hildegard_metadata.json`. Kerning and optional `rlig` composites give basic joining.
- **LilyPond, MuseScore, Finale, Dorico.** Any SMuFL-aware engraver can load the OTF. Coverage is Rhineland-only, so square-notation chant rendering is unchanged; the font contributes only to chant-in-Rhineland-style workflows.
- **Web / CSS.** `hildegard-neumes.woff2` ships alongside the OTF for direct `@font-face` declarations.
- **Future Rust consumers beyond Rhena.** A thin crate `hildegard-neumes-font` could wrap the OTF via `include_bytes!` + `ttf-parser` for runtime-loading contexts. Not needed for v1.

This multi-consumer capability is what the user's directive ("do what is best long term") demands. Inline-Rust paths locked the glyphs into one renderer; a real OTF unlocks every future consumer with zero marginal work.

## 8. Relationship to existing font-project documents

| Document | Status after pivot |
| --- | --- |
| `README.md` | **Updated** to Rhena-first framing |
| `glyph_inventory_v0.5.md` | **§ 0.2 added** mapping to Rhena NeumeClass + atomic glyph set; v0.5 RN-021/022 "dedicated glyph" reclassification undone (Rhena assembles them) |
| `smufl_codepoint_mapping.md` | **Still valid** — the codepoint plan is for the OTF, used by secondary consumers. Rhena itself keys off glyph *name strings*, not codepoints. |
| `research_synthesis.md` | **Still valid** — architectural rationale and paleographic grounding hold |
| `research_v2_findings.md` | **Still valid** — manuscript URLs, Gardiner corrections, MEI-Tübingen note all hold |
| `verovio_integration_plan.md` | **Demoted** to secondary-consumer reference. Header added marking it as such. |
| `glyph_priority_sheet.md` | **Still valid** but re-tier around Rhena's 19-atom v1 set instead of 40-family ladder |
| `examples/mei_encoding_reference.md` | **Still valid** as secondary-consumer reference (Verovio MEI authoring) |
| `hildegard_metadata.json` | **Still valid** for external consumers; Rhena itself ignores it |

## 9. What this means for the paleographic inventory

The v0.5 inventory researched **35 neume families** across atomic / fixed / variable / modified / repetition / idiosyncratic-compound / composite tiers. That research is still valid as **paleographic grounding** — it documents what forms exist in Hildegard and how they're attested.

But the **font's drawn shapes** are the ~19 Rhena atoms, not 35 family glyphs. The 35 families map to the 19 atoms via Rhena's resolver logic + NeumeClass vocabulary. Examples:

- `pes` → `rh_punctum` (lower) + `rh_pes_line` (connector) + `rh_virga` (upper)
- `flexa` → `rh_virga` (upper) + `rh_flexa_line` (connector) + `rh_punctum` (lower)
- `climacus` → `rh_virga` + `rh_punctum_inclinatum × n`
- `torculus` → `rh_punctum` + `rh_virga` (middle) + `rh_punctum` (or depending on context)
- `pressus` → `rh_pressus` + `rh_punctum` or `rh_punctum_inclinatum`
- `pressus_subpunctis` → `rh_pressus` + `rh_punctum_inclinatum × n`
- `flexa_resupina_pressus_subbipunctis` (RN-021) → assembled from the same atoms via the resolver

**v0.5's reclassification of RN-021/022 as "dedicated glyphs" was wrong for this consumer.** Rhena's architecture assembles idiosyncratic compounds from atoms. The v0.5b update in `glyph_inventory_v0.5.md` § 0.2 undoes that reclassification.

Whether Rhena *should* have dedicated compound glyphs for RN-021/022 is a separate question — Gardiner's paleographic claim (p. 16) is that these are visually unified Hildegard pen gestures, not stitched-together sequences. If the assembled output doesn't capture that, a v2 proposal to Rhena can add `rh_flexa_resupina_pressus_subbipunctis` as a dedicated atom + a new NeumeClass variant + a resolver case. But that's a future ADR, not v1 scope.

## 10. Success criteria

**v1 of the font project is successful when:**

1. `hildegard-neumes.otf` exists, exports from `hildegard-neumes.sfd`, and passes basic validation (no unreferenced glyphs, em=1000, all 19 names present).
2. `scripts/generate-rhena-glyphs.py` produces a Rust file that byte-compiles in Rhena.
3. Advance widths in the generated file match the v1-frozen `widths.json`.
4. Dropping the generated file into `hildegard/crates/rhena-core/src/render_ir/glyphs/rhineland.rs` passes `cargo check` in Rhena.
5. `just check` passes in Rhena after golden-test snapshot review/update.
6. `cargo run -p hildegard-cli -- render fixtures/corpus/o-ecclesia-line1.rhena --mode diplomatic --output /tmp/o_ecclesia.svg` produces an SVG that visually resembles `docs/research/images/o_ecclesia_rhineland_line_01.png` better than the current abandoned attempt.
7. A brief ADR in Rhena (ADR-0008 or next available) documents the switch from inline paths to generated font consumption, referencing this plan.

That's the MVP. Everything else (v2 accidentals, directional oriscus, Verovio secondary-consumer path, web delivery, additional fonts) builds on this foundation.
