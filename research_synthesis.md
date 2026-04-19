# Hildegard Neume Font — Research Synthesis & Architecture Recommendation

Status: v1 synthesis, 2026-04-14
Scope: consolidates parallel research into Gregorio internals, SMuFL + prior chant fonts, Hildegard paleography, and OpenType technology options, and turns it into a v1 architecture proposal for the Hildegard/Rhineland neume font.

---

## 1. What we set out to answer

Before committing to a font production approach, four questions needed grounded answers:

1. **Gregorio as prior art.** How does Gregorio's shipped font (Greciliae) actually build and render neumes? Is it an intelligent OpenType font or an external compiler?
2. **Existing chant font precedents.** What does SMuFL standardize for chant? What do Caeciliae, Greciliae, and LilyPond's Gregorian support actually do architecturally?
3. **Rhineland/Hildegard paleography.** What does the notation in Dendermonde Cod. 9 and Wiesbaden Riesenkodex Hs. 2 actually look like, and how does it differ from the square-Solesmes tradition?
4. **Font technology options.** For a font that handles variable-length neumes, staff placement, and composite sequences, what does OpenType support in practice — ligatures, mark attachment, colour layers, or an external engine?

Four agents ran in parallel (two Explore on the reference-repos, two general-purpose on web research and tech-option analysis). This document is the synthesis.

---

## 2. Findings

### 2.1 Gregorio is not a "smart" OpenType font

The single most useful clarification: Gregorio's font (Greciliae / Gregorio / Grana Padano) is a **precomposed glyph matrix**, not a shaping-engine-driven font.

- Source files: FontForge `.sfd` — `greciliae-base.sfd` (237 atomic components), plus `gregorio-base.sfd`, `granapadano-base.sfd`.
- Build tool: `fonts/squarize.py`, a FontForge Python script that pastes components into ~2,000+ composites at build time.
- Naming convention: `{Shape}{Ambitus1}{Ambitus2}{Liquescence}` — e.g., `ScandicusOneTwoDeminutus`.
- Variable-length families (scandicus, ancus, porrectus) are solved by **enumerating every (shape, ambitus pair) combination** as a separate glyph, capped at MAX_AMBITUS=5.
- gabc → glyph mapping: the compiler (`src/gregoriotex/gregoriotex-write.c`, lines 356–1237) computes a glyph name from parsed pitches and shape, then looks it up. No runtime composition. No fallback for missing names.
- Alternate notations (Laon, St Gall modern reconstructions) = **entirely separate font files** with identical glyph names, swapped via a TeX macro. No feature-based switching. No mixed notation in one document.
- Vertical staff placement is done by **GregorioTeX**, not the font. Font supplies short line-segment glyphs that the compiler positions by writing TeX boxes. Staff-line colour and horizontal placement live entirely outside the font.

**Lesson:** Gregorio's reputation as "the chant font" is misleading. It is really a chant *compiler* with a dumb font attached. The font is a delivery format, not an engine.

### 2.2 Caeciliae takes the same approach but for Word/InDesign users

Caeciliae (by Br. Matthew Spencer OSJ, the upstream of Greciliae) is designed to work without a compiler. It achieves joining through **kerning and tight sidebearings** on PUA-encoded components. Users type a sequence of atomic glyphs (including short "staff-line-segment" glyphs between neumes); the font's kern table pulls them into correct horizontal overlap. Vertical placement is entirely the user's responsibility — they pick the right pre-drawn glyph at the right position on the staff.

**Lesson:** even the professional-grade chant fonts deliberately do *not* try to make OpenType "understand" chant. They ship component libraries and put intelligence elsewhere (in a compiler, or in the user's hand).

### 2.3 SMuFL's chant coverage is thin and atom-level by design

SMuFL (Standard Music Font Layout) defines ~50 chant glyph names across three PUA ranges:

- **U+E990–U+E9AF** — plainchant single-note forms (punctum, punctum inclinatum + variants, virga, quilisma, oriscus, strophicus)
- **U+E9B0–U+E9CF** — plainchant multi-note forms (podatus, deminutum variants, entry lines, ligatures, connecting lines, strophicus liquescens for intervals 2nd–6th only)
- **U+E9D0–U+E9DF** — plainchant articulations (ictus, circulus, semicirculus, accentus, episema, augmentum)
- **U+EA00–U+EA1F** — medieval miscellany (custos variants)

Key architectural facts:

- SMuFL encodes atoms and a small set of precomposed ligatures. It does **not** standardize variable-length neumes.
- Multi-note forms are enumerated only for intervals of a 2nd through a 6th. Beyond that, SMuFL offers no mechanism — "use a precomposed glyph if available, fall back to application logic."
- All chant glyphs are PUA. There is no Unicode standard for neumes.
- Articulations are separate glyphs that applications must composite onto neumes (not modifiers baked in).

### 2.4 MEI (Music Encoding Initiative) is notation-agnostic

MEI's `<neume>` + `<nc>` (neume-component) model is the closest thing to a portable semantic encoding for chant:

```xml
<syllable>
  <syl>text</syl>
  <neume type="pes">
    <nc pname="c" oct="4"/>
    <nc pname="d" oct="4" tilt="ne" intm="u" liquescent="true"/>
  </neume>
</syllable>
```

`<nc>` supports attributes: `pname`, `oct`, `tilt` (pen-stroke direction: n/ne/e/se/s/sw/w/nw), `intm` (interval motion), `con` (connection: gapped/looped/extended), `rellen` (relative pen length), plus ornament flags `oriscus`, `quilisma`, `liquescent`, `auctum`, `deminutum`, `cavum`, `strophicus`.

This model **encodes intent, not glyph choice**, and it can represent St. Gall, Old Hispanic, Aquitanian, square, or Rhineland notation with the same schema. For a Hildegard project that wants portability and alignment with digital musicology tooling, MEI is the right semantic target.

### 2.5 LilyPond's Gregorian support is programmatic, not font-based

LilyPond does not ship a precomposed neume font. `gregorian-ligature-engraver.cc` analyzes note sequences at compile time using per-note prefix flags (VIRGA, INCLINATUM, ORISCUS, QUILISMA, DEMINUTUM, CAVUM, AUCTUM, ASCENDENS, DESCENDENS) and draws neumes by selecting Feta-font primitives and positioning them. Notable for the Hildegard project only as a warning: LilyPond's shape library is Solesmes-centric and will not accommodate Rhineland forms out of the box.

### 2.6 Hildegard's notation: "between St Gall and Hufnagelschrift"

The most important paleographic findings (sources: Gardiner 2022 DMA dissertation, van Poucke's intro to the Dendermonde facsimile, Cantus Database entries for sources 588308 and 588309, Welker/Klaper 1998 Riesenkodex facsimile, Pfau 1998 Symphonia edition, Humdrum Hildegard representation):

**Register.** Peter van Poucke characterizes it as *"early German, in notational chronology between Sankt Gallen neumes and the so-called gothic neumes (Hufnagelschrift)"* (quoted in Gardiner 2022, p. 25). It is *not* square-Solesmes, *not* fully adiastematic St Gall, *not* mature Hufnagel. Pfau labels it "German Hufnagel Notation" but this is mildly anachronistic — the horseshoe-nail virga of Hufnagelschrift is the next century.

**Staff.** Both manuscripts use a **four-line staff with a yellow line for C and a red line for F**, plus a movable C-clef. Text sits beneath the staff. Fully diastematic (heighted), not adiastematic.

**Sources.**
- Dendermonde, St.-Pieters-en-Paulusabdij, Cod. 9 (c. 1174/75). 57 Symphonia items. "More authoritative" per ISHBS editors.
- Wiesbaden, Hochschul- und Landesbibliothek RheinMain, Hs. 2 — the Riesenkodex (c. 1180–85), 46 × 30 cm, two columns, 17 staves per column, music on ff. 466–481v. Five distinct scribal hands discernible in the codex overall.

**Distinctive neume forms (Gardiner, Humdrum inventory, Meconi):**

- **Climacus / scandicus**: **virga + detached puncta**, not lozenge chains. The editors "deliberately have not connected" the constituent notes. **Do not reuse square-notation diamond glyphs.**
- **Quilisma**: *"two small jagged-looking waves with a gracefully curved line ascending the distance of a third or sometimes a fourth… connected to a smooth upward ascending stroke"* (Gardiner pp. 94–95). The jagged wave is **attached to a smooth ascending tail**, not free-standing.
- **Pressus**: *"a vertical line attached to a short undulating line"* (Gardiner p. 94). Direct design brief.
- **Liquescents**: *"rounded off, lighter stroke"* (Gardiner p. 92). Stylistic contract for the whole liquescent family — lighter weight + rounded terminals.
- **Torculus rotundus vs quadratus**: both round and angular forms of the same neume coexist in Hildegard's sources; Humdrum encodes them separately. Meaningful for glyph design — give both variants.
- **Flexa vs pes flexus**: distinguished *"by a slight uplift in the tail of the pes flexus"* (Gardiner Fig. 1, p. 29). Subtle but real.
- **Hildegard-idiosyncratic compounds**: Gardiner explicitly names *"the elaborate compound flexus resupinus/pressus/subbipunctis"* and *"flexus resupina/pressus liquescens"* as *"idiosyncratic neumes… that can be challenging to decipher"* (pp. 32–33). Meconi also flags an *"incomplete pressus"*.

**Neume families attested in Hildegard (Gardiner + Humdrum, consolidated):**

Single-tone: punctum, tractulus, virga, oriscus.
Two-note: pes (podatus), clivis/flexa (+ liquescent variants).
Three-note: torculus (rotundus and quadratus), porrectus, torculus resupinus, porrectus flexus.
Multi-note: climacus, climacus resupinus, scandicus, pes subpunctis, quilisma, quilisma-torculus.
Stropha family: apostropha, bistropha, tristropha.
Pressus family: pressus minor, pressus maior, pressus liquescens.
Liquescent modifiers: augmentative and diminutive, applied across the above.
Cephalicus (descending liquescent clivis) explicitly discussed in *O viridissima virga* (Riesenkodex f. 474v).

**Gap in v0.4.** Oriscus, tractulus, torculus (both rotundus and quadratus), torculus_resupinus, porrectus, porrectus_flexus, climacus_resupinus, and pes_subpunctis are all present in the manuscript sources and attested in scholarly inventories but absent from the v0.4 inventory. These must be added in v0.5.

### 2.7 There is no existing Rhineland neume font

Existing Hildegard work:

- **Barth / Ritscher / Schmidt-Görg** (1969/2012 *Lieder*) — only complete edition in Solesmes square notation. Not faithful to Rhineland shapes.
- **Pfau** (1998, 8 vols.) — modern five-line staff. Notation-key labels source as "German Hufnagel Notation."
- **Corrigan** (2016) — stemless noteheads on 5-line staff, comparative D vs R.
- **International Society of Hildegard von Bingen Studies** — modern 5-line staff transcriptions with slurs and slashed-eighth liquescents. Not a font.
- **Luca Ricossa** — unpublished diplomatic PageStream transcriptions using standardized digital neumes, side-by-side D and R. Not a published font.
- **Cantus Database** — Volpiano encoding (pitch only, no shape).
- **Humdrum Hildegard representation** — analytic encoding (torculus rotundus/quadratus distinction, pressus minor/maior, liquescent modifiers) — "designed to facilitate analytic applications rather than music printing."
- **DiMusEd Tübingen** — has a Hildegard notation page but it was returning HTTP 503 during research. Retry; may be the most focused current academic resource.

**No public font renders Hildegard's Rhineland neumes diplomatically.** This project would fill a real and unoccupied gap.

### 2.8 Font technology options evaluated

Opinionated assessment by agent (full version in the agent's report):

| Option | Verdict | Why |
| --- | --- | --- |
| **Precomposed per (family, length, span, start)** | Reject as primary | ~3,400+ glyphs for fixed families alone before touching climacus/scandicus; maintenance disaster; Illustrator glyph panel unusable. |
| **GSUB ligatures on PUA sequences** | Reject as primary | OT shaping can't express "absolute staff position." GSUB substitutes glyph sequences; it has no access to vertical pitch. Also: `liga` is off by default in Illustrator and many word processors. |
| **GPOS mark attachment for staff placement** | Helper only | Vertical offsets in GPOS are relative to baseline/previous anchor. Chant's vertical axis is *absolute on the staff*, not relative. Viable inside a single ligature group, not as primary placement. |
| **COLR / SVG-in-OT** | Skip | Chant is monochrome. Zero benefit, compat cost. |
| **External shaping engine (Gregorio-style)** | Proven | This is what Gregorio, Caeciliae, and LilyPond all do under the hood. Scales to any neume length. Downside: requires a toolchain. |
| **Dumb components font + smart renderer** | **Recommended** | This is the architecture behind every serious chant font. The variant worth picking is *which smart renderer*. |

**Practical shaping-engine notes:**

- HarfBuzz handles long `liga`/`calt`/`rlig` chains fine. Two quirks: historical mark-to-ligature bugs (harfbuzz #2044); HarfBuzz does not line-break mid-ligature. Neither kills GSUB as a tool, but they kill it as *primary* architecture.
- Staff rendering in the wild: (a) font draws short line segments typed between neumes (Caeciliae); (b) engraver draws staff, font supplies note shapes (Verovio, LilyPond, MuseScore + SMuFL); (c) magic codepoints per staff line (combinatorial dead end). For a browser-first project, option (b) is clearly correct.

---

## 3. Architecture recommendation for v1

**Dumb components font + Verovio-based smart renderer. MEI as the encoding target. SMuFL-aligned where overlap exists, with a private PUA block for Hildegard-specific forms.**

### 3.1 Font deliverable

An OpenType font containing **~40–80 baseline-anchored component glyphs**, specifically:

1. **SMuFL-aligned atoms** (where SMuFL already has a codepoint): `chantPunctum`, `chantPunctumInclinatum` + auctum/deminutum variants, `chantPunctumVirga`, `chantQuilisma`, `chantOriscusAscending`/`Descending`/`Liquescens`, `chantStrophicus` + `Auctus`, `chantEpisema`, `chantAugmentum`, `chantIctus`, `chantAccentus`, `chantCirculus`, `chantSemicirculus`, `chantCustosStem*`.

2. **Hildegard-specific forms in a private PUA block** (recommend U+F400–U+F4FF as a placeholder subrange, final allocation to be verified against SMuFL's `glyphnames.json` to avoid collision): Rhineland dot-punctum, tractulus, rounded liquescent terminal, quilisma-with-tail, pressus-vertical-line-with-undulation, torculus rotundus and quadratus heads, porrectus body, subbipunctis tail, and the Hildegard-idiosyncratic compound glyphs (RN-021, RN-022 in v0.4).

3. **Fixed-family atoms** — pes, flexa, pes_flexus, flexa_resupina, bistropha, tristropha, cephalicus, epiphonus — drawn at 3–4 span variants each, *not* positioned on a staff. Purely baseline-anchored shapes.

4. **Minimal `kern` table** so users who paste components into Illustrator or Word get reasonable horizontal joining.

5. **A small handful of `rlig` ligatures** (required ligatures, always on) for the most common composite sequences (`flexa + pes`, `quilisma + pressus`, `pes + cephalicus`) as a convenience — but **not** relied on for correctness.

6. **Do not** attempt GPOS mark attachment for staff position in v1.

7. **Do not** bake staff line colour (yellow C, red F) into the font — that is a renderer responsibility. The font ships monochrome.

### 3.2 Renderer deliverable

Build the smart renderer as a **Verovio extension / SMuFL font swap**, not greenfield.

- Verovio ([verovio.org](https://www.verovio.org/index.xhtml)) already renders MEI neume notation with SMuFL fonts, has a JS/WASM build, and handles staff drawing and line breaking. Neon2 ([music-encoding.org/conference/abstracts/abstracts_mec2019/Neon2.pdf](https://music-encoding.org/conference/abstracts/abstracts_mec2019/Neon2.pdf)) is the web-first editor built on top of it.
- Work scope: supply Rhineland component glyphs, teach Verovio a few Hildegard shape rules, add the two-colour staff (yellow C / red F). Weeks, not months, versus months-to-years for a bespoke engraver.
- Variable families (climacus, scandicus, quilisma_prepuncto, porrectus, torculus variants) get assembled at render time from components using the connector logic in inventory §11.B.
- MEI-based input gives you notation-agnostic encoding + compatibility with existing digital-musicology tooling essentially for free.

### 3.3 What to defer to v2

- Full composite sequences (RN-023, RN-024, RN-025, RN-026) — assembled by the renderer, no new font glyphs needed.
- A precomposed convenience sub-font for Illustrator/Word users. Tempting but only worth doing once you know which 30–50 shapes editorial designers actually request. Ship reactively.
- LilyPond export. Verovio → MEI first; LilyPond via MEI export later.
- St Gall / Hufnagel stylistic sets (`ss01`, `ss02`) for notation switching. Possible future if a user needs to show Rhineland next to a comparative form.

### 3.4 What to explicitly not build

- A GSUB-driven "smart font" that tries to own chant shaping end-to-end. Industry prior art is unanimous that this fails.
- A staff-position-per-line codepoint scheme. Combinatorial dead end.
- A bespoke TeX pipeline. Gregorio already exists; if you want print output, borrow theirs via a MEI → gabc bridge.

---

## 4. Concrete next steps, in order

1. **Go direct to the manuscript sources.** Pull Dendermonde Cod. 9 and Riesenkodex Hs. 2 digitizations; find Gardiner 2022 Figure 6 ("basic neumes from Riesenkodex f. 470r"). Retry the DiMusEd Tübingen Hildegard notation page. The goal: read the hand yourself before any font work.
2. **Publish v0.5 inventory** (see `glyph_inventory_v0.5.md`) — folds in oriscus, tractulus, torculus rotundus/quadratus, torculus resupinus, porrectus, porrectus flexus, climacus resupinus, pes subpunctis, and reclassifies RN-021/022 as dedicated glyphs. Adds a paleographic source column.
3. **Publish SMuFL codepoint mapping** (see `smufl_codepoint_mapping.md`) — one row per inventory item, SMuFL vs private PUA.
4. **Hand sketch / Illustrator trace pass.** ~40 atomic + fixed-family shapes, traced from Dendermonde and Riesenkodex plates. Get the stroke register right (rounder than Hufnagel, heavier than St Gall) before any `.sfd` work. No OpenType yet.
5. **Verovio prototype.** Swap one existing SMuFL chant font in Verovio with 5–10 of the sketched atoms as a proof of concept before going deep on the full component library.
6. **First `.sfd` source**, based on the sketch pass. FontForge, modeled on Gregorio's `greciliae-base.sfd` as a structural reference — but with Hildegard glyph shapes and Hildegard glyph names.
7. **Build script.** A minimal Python generator that emits the `.ttf` from the `.sfd`. Start simple; resist the temptation to build a `squarize.py` clone until variable-family assembly proves necessary.

---

## 5. Key citations (for the v0.5 inventory source column and future documentation)

**Primary sources:**
- Dendermonde, St.-Pieters-en-Paulusabdij, Cod. 9 — [Cantus 588309](https://cantusdatabase.org/source/588309)
- Wiesbaden, HLB RheinMain, Hs. 2 (Riesenkodex) — [Cantus 588308](https://cantusdatabase.org/source/588308)

**Scholarship:**
- Katie Gardiner, *A Conductor's Guide to the Music of Hildegard von Bingen*, DMA diss., Indiana University, 2022 — [scholarworks.iu.edu PDF](https://scholarworks.iu.edu/iuswrrest/api/core/bitstreams/1a626db3-354f-4a79-94c2-227cd959eec0/content). Most useful single source; chs. 2 and 4.
- Peter van Poucke, intro. to *Symphonia: Dendermonde* facsimile (quoted in Gardiner) — the "between Sankt Gallen and Hufnagelschrift" characterization.
- Lorenz Welker & Michael Klaper, *Hildegard von Bingen: Lieder: Faksimile Riesencodex (Hs. 2)*, Elementa Musicae, 1998.
- Marianne Richert Pfau, *Symphonia armonie celestium revelationum*, 8 vols., Hildegard Publishing Co., 1998.
- Honey Meconi, "The Unknown Hildegard: Editing, Performance, and Reception," in Monson & Marvin eds., *Music in Print and Beyond*, Boydell & Brewer, 2013.
- David Hiley, s.v. "Hufnagel," *Grove Music Online*, 2001.
- [International Society of Hildegard von Bingen Studies — Music page](https://www.hildegard-society.org/p/music.html) — editorial methodology, source choices.
- [Humdrum Hildegard representation](https://www.humdrum.org/Humdrum/representations/hildegard.rep.html) — analytic encoding inventory with torculus rotundus/quadratus split.
- [DiMusEd Tübingen Hildegard notation](https://www.dimused.uni-tuebingen.de/hildegard_notation.php) — was 503; retry.

**Font / tech prior art:**
- [Gregorio project](https://github.com/gregorio-project/gregorio) — especially `fonts/squarize.py`, `fonts/stemsschemas.py`, `fonts/fonts_README.md`, `src/gregoriotex/gregoriotex-write.c`.
- [Caeciliae by Br. Matthew Spencer OSJ](https://marello.org/caeciliae/) — upstream of Greciliae.
- [SMuFL spec](https://w3c.github.io/smufl/latest/) — chant ranges at U+E990–U+E9DF and U+EA00–U+EA1F.
- [Verovio](https://www.verovio.org/) — web-first MEI engraver.
- [Neon (DDMAL)](https://github.com/DDMAL/Neon) — Verovio-based neume editor.
- [MEI schema, neumes module](https://music-encoding.org/schema/dev/mei-all.html).
- [HarfBuzz shaping features](https://harfbuzz.github.io/shaping-opentype-features.html).

---

## 6. Bottom line

Hildegard's neumes sit in a register that is not served by any existing font, and the architecture choice is clearer than expected: **ship a dumb component font that aligns with SMuFL where it can and extends into private PUA where it must, and do the shaping work inside Verovio via MEI input.** That keeps the font honest, gives you a web-first renderer essentially for free, and leaves a clean path to print output through MEI-to-gabc later.

The v0.4 inventory's semantic layer is broadly sound; the main corrections are paleographic (missing families attested in Dendermonde/Riesenkodex, wrong assembly status for the idiosyncratic compounds, and no grounding in the actual Rhineland stroke register). Those corrections are captured in v0.5.
