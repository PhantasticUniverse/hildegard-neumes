# Rhineland / Hildegard Neume Glyph Inventory — v0.5

Supersedes: `glyph_inventory.md` (v0.4).
Primary consumer: the Rhena/Viriditas Rust project (`../hildegard`). See `rhena_integration_plan.md` for how this inventory feeds the font's drawn glyph set.
Companion docs: `README.md`, `rhena_integration_plan.md`, `research_synthesis.md`, `research_v2_findings.md`, `smufl_codepoint_mapping.md`, `verovio_integration_plan.md` (secondary), `glyph_priority_sheet.md`.

---

## 0.2 — v0.5b Rhena alignment (2026-04-14)

A second correction pass, folding in the discovery that the font's **primary consumer** is the Rhena/Viriditas Rust notation platform (`/Users/xaviermac/Documents/2_Areas/Coding-Projects/hildegard`), which has an existing (abandoned) Rhineland glyph module at `crates/rhena-core/src/render_ir/glyphs/rhineland.rs` and a component-level atomic resolver at `glyphs/mod.rs`.

### What this changes

**The inventory below describes 35 paleographic neume families.** That research is still valid — it documents what neume forms exist in Hildegard's music and how they're attested. **But the font's drawn shapes are not 35 family-level glyphs.** Rhena's render architecture draws ~19 atomic shapes and assembles multi-component neumes at render time by positioning atoms via a resolver. So the font's drawn inventory is a **subset** of the paleographic inventory below.

### Rhena's 19-atom set (the production glyph names)

| Rhena glyph name | Used by (NeumeClass via resolver) | v0.5 inventory reference |
| --- | --- | --- |
| `rh_punctum` | Punctum; inner / lower components of Pes, Flexa, Torculus, Porrectus, Pressus; scandicus non-last | RN-003 |
| `rh_virga` | Virga; Punctum as standalone; first component of Flexa, Climacus, Torculus (inner), Porrectus, Pressus; last component of Pes, Scandicus, Epiphonus | RN-001 |
| `rh_punctum_inclinatum` | Climacus non-first components; descending-from-prev inside Pressus family | RN-002 dot-punctum; Component (new v0.5) |
| `rh_quilisma` | Quilisma ornamental role | RN-019 |
| `rh_oriscus` | Oriscus ornamental role (asc + desc, not yet split in Rhineland) | RN-028 |
| `rh_strophicus` | Apostropha / Bistropha / Tristropha (all three currently collapse to this atom) | RN-009, RN-010, RN-011 |
| `rh_pressus` | First component of Pressus / PressusSubpunctis / PressusLiquescens | RN-016 pressus core (Gardiner p. 94) |
| `rh_liquescent_asc` | Ascending liquescent terminal (Epiphonus, pes liquescens, etc.) | RN-013 epiphonus core |
| `rh_liquescent_desc` | Descending liquescent terminal (Cephalicus, etc.) | RN-012 cephalicus core |
| `rh_deminutum` | Diminutive liquescent | Component (new v0.5) — rounded terminal |
| `rh_c_clef` | Movable C-clef on 4-line staff | Staff-system glyph |
| `rh_f_clef` | F-clef for low-range antiphons | Staff-system glyph |
| `rh_divisio_minima` | DivisionKind::Minima | Staff-system glyph |
| `rh_divisio_maior` | DivisionKind::Minor | Staff-system glyph |
| `rh_divisio_maxima` | DivisionKind::Maior | Staff-system glyph |
| `rh_divisio_finalis` | DivisionKind::Finalis | Staff-system glyph |
| `rh_virgula` | DivisionKind::Virgula; fallback for Minimis + DominicanD (TODO in Rhena) | Staff-system glyph |
| `rh_pes_line` | Ascending connector between lower/upper components of pes and similar rising neumes | Component (connector) |
| `rh_flexa_line` | Descending diagonal connector for flexa/clivis | Component (connector) |

**19 glyphs total.** Em = 1000, Y-up, Bravura-compatible. Advance widths per `rhena_integration_plan.md` § 3.3.

### What assembles from atoms (no dedicated glyph)

Every multi-component neume family below is rendered by Rhena as a sequence of atoms placed at computed (x, y) positions. No dedicated compound glyph.

- **Pes** → `rh_punctum` + `rh_pes_line` + `rh_virga`
- **Flexa** → `rh_virga` + `rh_flexa_line` + `rh_punctum`
- **Pes flexus** → `rh_punctum` + `rh_virga` + `rh_punctum` (sequence)
- **Flexa resupina / Porrectus** → `rh_virga` + `rh_punctum` + `rh_punctum`
- **Climacus** → `rh_virga` + `rh_punctum_inclinatum × n`
- **Scandicus** → `rh_punctum × n` + `rh_virga`
- **Torculus** (all variants) → `rh_punctum` + `rh_virga` + `rh_punctum`
- **Torculus resupinus** → sequence
- **Porrectus flexus** → sequence
- **Climacus resupinus** → sequence
- **Pes subpunctis** → `rh_punctum` + `rh_virga` + `rh_punctum_inclinatum × n`
- **Pressus** → `rh_pressus` + `rh_punctum`
- **Pressus subpunctis** → `rh_pressus` + `rh_punctum_inclinatum × n`
- **Pressus liquescens** → `rh_pressus` + `rh_punctum` + `rh_liquescent_desc`
- **Cephalicus** → `rh_virga` + `rh_liquescent_desc`
- **Epiphonus** → `rh_punctum` + `rh_liquescent_asc`
- **Pes liquescens / pes flexus liquescens** → atom sequence + liquescent terminal
- **Quilisma prepuncto** → `rh_punctum` + `rh_quilisma` + `rh_virga`

### Undoing v0.5's RN-021/022 reclassification

v0.5 § 4.2 reclassified RN-021 (`flexa_resupina_pressus_subbipunctis`) and RN-022 (`flexa_resupina_pressus_liquescens`) from "composite sequence (assembly only)" to "Hildegard-idiosyncratic compound — dedicated glyph." That reclassification was based on Gardiner p. 16 naming them as characteristic Hildegard forms, and it would have required dedicated OTF codepoints at U+F4A0 / U+F4A1 in the private PUA block.

**That decision does not apply to the Rhena consumer.** Rhena's architecture assembles these from atoms:

- **RN-021** `flexa_resupina_pressus_subbipunctis` → `rh_virga + rh_punctum + rh_punctum + rh_pressus + rh_punctum_inclinatum + rh_punctum_inclinatum`
- **RN-022** `flexa_resupina_pressus_liquescens` → `rh_virga + rh_punctum + rh_punctum + rh_pressus + rh_punctum + rh_liquescent_desc`

Whether these *should* have dedicated Rhena atoms is a separate question. Gardiner's paleographic claim is that these are visually unified single pen gestures, not stitched sequences. If the assembled output doesn't capture that unity, a v2 coordination with Rhena can add a dedicated atom, a new `NeumeClass` variant, and a resolver case. **That is deferred to a future ADR in the Rhena project**, not part of this font's v1.

### SMuFL codepoint allocation — stays valid for secondary consumers

`smufl_codepoint_mapping.md` remains the authoritative codepoint plan for the OTF's **external consumer** interface (Verovio, Illustrator, Word, LilyPond, web). Rhena itself doesn't use codepoints — its resolver references glyphs by string name (`rh_punctum`, `rh_virga`, etc.). But the OTF still needs SMuFL-aligned codepoints where overlap exists, so that SMuFL-aware tools can use the font without custom mapping tables. The mapping is:

- SMuFL `chantPunctum` U+E990 → glyph name `rh_punctum`
- SMuFL `chantPunctumVirga` U+E996 → `rh_virga`
- SMuFL `chantPunctumInclinatum` U+E991 → `rh_punctum_inclinatum`
- SMuFL `chantQuilisma` U+E99B → `rh_quilisma`
- SMuFL `chantOriscusAscending` U+E99C → `rh_oriscus` (directional split deferred)
- SMuFL `chantStrophicus` U+E99F → `rh_strophicus`
- Private PUA U+F403 → `rh_pressus` (no SMuFL equivalent)
- SMuFL `chantAuctumAsc` U+E994 → `rh_liquescent_asc`
- SMuFL `chantAuctumDesc` U+E995 → `rh_liquescent_desc`
- SMuFL `chantPunctumDeminutum` U+E9A1 → `rh_deminutum`
- SMuFL `chantCclef` U+E906 → `rh_c_clef`
- SMuFL `chantFclef` U+E902 → `rh_f_clef`
- SMuFL `chantDivisioMinima` U+E8F3 → `rh_divisio_minima`
- SMuFL `chantDivisioMaior` U+E8F4 → `rh_divisio_maior`
- SMuFL `chantDivisioMaxima` U+E8F5 → `rh_divisio_maxima`
- SMuFL `chantDivisioFinalis` U+E8F6 → `rh_divisio_finalis`
- SMuFL `chantVirgula` U+E8F7 → `rh_virgula`
- Private PUA (connector) → `rh_pes_line`
- Private PUA (connector) → `rh_flexa_line`

### v2 inventory expansion (coordinated with Rhena)

These are not in the v1 set and need coordination with the Rhena project (ADRs required):

- **Accidentals** (`rh_flat`, `rh_natural`, `rh_sharp` + editorial variants) — Rhena's constitution §13.1 calls for Gregorio parity on 9 accidental variants, but neither `rhineland.rs` nor `square.rs` currently has them. Requires font glyphs + resolver extension + Render IR field.
- **Directional oriscus** (`rh_oriscus_asc` / `rh_oriscus_desc`) — `square.rs` already splits these; `rhineland.rs` does not.
- **Dedicated strophic atoms** — Apostropha / Bistropha / Tristropha currently all map to `rh_strophicus`. A dedicated split is possible if Rhineland manuscripts distinguish them visually.
- **Custos** if attested.
- **Dominican + Minimis division variants** — TODO comments in `glyphs/mod.rs` lines 99–110 fall back to virgula.
- **RN-021 / RN-022 dedicated compound atoms** — per the paleographic argument above.

See `rhena_integration_plan.md` § 6 for the v2 roadmap.

---

## 0.1 — v0.5a corrections (2026-04-14)

---

## 0.1 — v0.5a corrections (2026-04-14)

A deep-read of Gardiner 2022 revealed that several paleographic page references and source attributions in this document are wrong or overstated. Fixes below; the body table has been edited in place for the most important ones. A full v0.6 revision should happen after direct manuscript reading, but these corrections should not wait.

**Page-reference corrections (Gardiner 2022 DMA diss.)**
- **Figure 1** (flexa vs pes flexus "slight uplift in the tail") is on **p. 15** (Chapter 1), not p. 29. Applied below to RN-006.
- **"Idiosyncratic neumes" passage** naming `flexus respinus/pressus/subbipunctis` and `flexus respina/pressus liquescens` is on **p. 16** (Chapter 1), not pp. 32–33. Applied below to RN-021, RN-022.
- **O viridissima virga cephalicus / pressus liquescens** discussion is on **p. 60** (Chapter 4), Example 9, Riesencodex f. 474v. Applied below to RN-012.
- **van Poucke quote** ("between Sankt Gallen neumes and the so-called gothic neumes (Hufnagelschrift)") is on **pp. 25–26**, not just p. 25.
- **Figure 6** (basic neumes from Riesencodex f. 470r) is on **p. 91**, opening Chapter 4 — not in Chapter 2. Its neume labels are: `virga | punctum | pes | clivis | climacus | scandicus | torculus | porrectus`. Note Gardiner uses **clivis** (not flexa) and **porrectus** (not flexa resupina) in the figure labels, though her prose treats them as synonyms.

**Spelling note (Gardiner's idiosyncratic compound names)**
Gardiner writes *"flexus respinus/respina"* throughout — without the 'u'. The classical Latin form is *resupinus/resupina* (from *resupino*, "to bend back"). *Respinus* is not attested as a Latin word; treat Gardiner's spelling as an error or a corrupted transmission from van Poucke's Alamire introduction. The inventory keeps the corrected spelling `flexa_resupina_…` as the production form but documents Gardiner's variant in the source column.

**Source-attestation downgrades.** The v0.5 body table implies many entries are supported by Gardiner. A careful read shows that several are **Humdrum-attested only** and do not appear in Gardiner's text. Source strength per entry:

| Entry | Original v0.5 claim | Corrected attestation |
| --- | --- | --- |
| RN-010 bistropha, RN-011 tristropha, RN-009 apostropha | Gardiner + Humdrum | ✓ Gardiner p. 91 ("The repercussive neumes include the apostropha, bistropha, and tristropha"); Humdrum |
| RN-013 epiphonus | Gardiner ch. 2 | ✗ **NOT in Gardiner**. Inherited from general chant paleography. Humdrum lists liquescent variants generically. Downgrade confidence to Medium. |
| RN-027 tractulus | Gardiner ch. 2 | ✗ **NOT in Gardiner** — Humdrum-only. Downgrade to Medium. Consider whether it is visually distinct from punctum in Dendermonde / Riesencodex plates before committing. |
| RN-028 oriscus | Gardiner ch. 2 | ✓ Gardiner pp. 93–94 ("a small note, similar to a punctum or apostropha, that has a wavy component"). |
| RN-029 torculus_rotundus, RN-030 torculus_quadratus | Humdrum split | ✗ **NOT in Gardiner** (zero occurrences of "rotundus" or "quadratus" in Gardiner). This split is Humdrum-only. Downgrade to Low-Medium. **Must verify** against direct manuscript inspection before committing to two dedicated glyphs. |
| RN-031 torculus_resupinus | Gardiner ch. 2 | ✓ Gardiner p. 77, Fig. 5 — but the figure is about square notation, not Hildegard's Rhineland form specifically. Medium confidence. |
| RN-032 porrectus | Gardiner Fig. 6 | ✓ Gardiner Fig. 6 p. 91 ("porrectus or flexa resupina" — treated as synonyms). |
| RN-033 porrectus_flexus | Gardiner ch. 2 | ✗ **NOT explicitly in Gardiner**. Standard chant paleography term; inferred. Medium confidence. |
| RN-034 climacus_resupinus | Gardiner ch. 2 | ✗ **NOT in Gardiner**. Humdrum-only. Downgrade to Medium. |
| RN-035 pes_subpunctis | Gardiner ch. 2 | ⚠ Gardiner p. 82 only says "climacus and subpunctis constructions" generically — not `pes subpunctis` specifically. Medium confidence. |
| RN-014 pes_liquescens, RN-015 pes_flexus_liquescens, RN-017 pressus_liquescens | Gardiner ch. 2 | ⚠ "Liquescens" + "pes" appear separately but the specific compound names are not explicitly enumerated by Gardiner. Medium confidence. |
| RN-012 cephalicus | Gardiner ch. 4 | ✓ Gardiner p. 60 — single mention, *O viridissima virga* Riesencodex f. 474v, contrasted with pressus liquescens. |
| RN-020 quilisma_prepuncto | Gardiner ch. 2 | ✓ Gardiner p. 60 — "the quilisma prepuncto, that may be open to some interpretation." |

**What this means for v0.6.** A direct manuscript read of Dendermonde Cod. 9 (via IMSLP facsimile, public domain: `https://imslp.org/wiki/Dendermonde_Codex_(Hildegard)`) and Riesencodex Hs. 2 (via HLB RheinMain, CC-BY: `https://hlbrm.digitale-sammlungen.hebis.de/handschriften-hlbrm/content/titleinfo/449618`, folio 470r at pageview 450574) should settle the Humdrum-only entries. Likely outcomes: keep what Rhineland manuscripts actually show; demote or merge items the manuscripts don't distinguish (e.g., torculus rotundus vs quadratus if Hildegard's hand only draws one form).

---

## 0. What changed from v0.4

Fold-ins from paleographic research (Gardiner 2022, van Poucke, Welker/Klaper 1998, Pfau 1998, Meconi 2013, Humdrum Hildegard representation, Cantus DB 588308/588309):

1. **New families added** (all attested in Dendermonde and/or Riesenkodex, missing from v0.4):
   RN-027 `tractulus`, RN-028 `oriscus` (ascendens + descendens),
   RN-029 `torculus_rotundus`, RN-030 `torculus_quadratus`,
   RN-031 `torculus_resupinus`, RN-032 `porrectus`, RN-033 `porrectus_flexus`,
   RN-034 `climacus_resupinus`, RN-035 `pes_subpunctis`.
2. **Reclassification of RN-021 and RN-022.** Gardiner explicitly names *"the elaborate compound flexus resupinus/pressus/subbipunctis"* and *"flexus resupina/pressus liquescens"* as **idiosyncratic Hildegard compounds**. In v0.4 these were classified as composite sequences / assembly-only. In v0.5 they are **dedicated glyphs / Hildegard-idiosyncratic compounds** — they are the signature ornamental forms and deserve bespoke drawing.
3. **New atomic/component items.**
   - `dot-punctum` (distinct from square punctum — for climacus and scandicus chains; Rhineland climacus is *virga + detached dot-puncta*, not lozenge chains).
   - `tractulus` (short horizontal dash, a distinct single-tone sign).
   - `oriscus` (ascending and descending head components).
   - `rounded-liquescent-terminal` (Hildegard-specific — Gardiner p. 92: *"rounded off, lighter stroke"*).
   - `quilisma` reclassified: in v0.4 it was an atomic sign + family. In v0.5 it is a **fused form**: Gardiner describes it as "two jagged waves *connected to* a smooth upward ascending stroke." The jagged-wave core is a component, the ascending tail is a separate connector.
   - `pressus-core` reclassified per Gardiner p. 94: *"a vertical line attached to a short undulating line"* — this is a literal design brief, not a generic repeat-core.
4. **New column on the inventory table**: `Paleographic source` — citation(s) attesting the form in manuscript or scholarship.
5. **New section § 15**: Paleographic register — stroke contract, staff layout (yellow C / red F), source manuscripts, scribal variation.
6. **New section § 16**: Architecture decision pointer — the v1 font is *dumb components + Verovio-based smart renderer + MEI semantic encoding*. Rationale lives in `research_synthesis.md`.

Rule additions: Rule 6 (paleographic grounding) and Rule 7 (notational register).

---

## 1. Hildegard-focused working rules

### Rule 1 — separate family from instance

A label like `pes` names a **family**, not one exact vertical shape.

Track two different things:
- **Family cardinality** — what the neume type does in principle.
- **Chart exemplar cardinality** — how many notes the supplied chart example happens to show.

### Rule 2 — think in staff steps / ambitus, not semitones

For font planning, what matters is vertical span and attachment behaviour. Describe each neume by contour, repetition, span variability, length variability.

### Rule 3 — not every chart row should become one final glyph

Some chart rows are atomic signs; some are families; some are modified families; some are composite sequences shown as examples. Distinguish before production.

### Rule 4 — Hildegard needs both semantic and graphic labelling

Some forms are best treated as semantic family names for the inventory, graphic components for the font, and specific chart exemplars for testing — simultaneously.

### Rule 5 — add a Gregorio/gabc-style constructor layer

Borrow the abstraction: family first, construction logic second, final drawing third. Do **not** copy square-notation visual assumptions.

### Rule 6 — anchor every entry to paleographic evidence (new in v0.5)

Every inventory entry should name at least one source — manuscript folio, Gardiner page, Humdrum encoding, van Poucke commentary, or explicit "Unattested: chart-only." If we cannot point to the form in Dendermonde or Riesenkodex or a named scholarly inventory, it is a candidate for removal or renaming. This keeps the font honest about what is Hildegard and what is inherited assumption.

### Rule 7 — the notational register is "between St Gall and Hufnagelschrift" (new in v0.5)

The font is *not* square-Solesmes and *not* gothic horseshoe-nail. van Poucke's characterization (quoted in Gardiner 2022 p. 25): *"early German, in notational chronology between Sankt Gallen neumes and the so-called gothic neumes (Hufnagelschrift)."* Stroke register should be rounder than Hufnagel, more substantial than St Gall, heighted on a 4-line staff. Square-notation glyphs should not be reused, and square-notation design decisions (lozenge climacus chains, three-lobed free-standing quilisma) should be explicitly rejected where Rhineland practice differs.

---

## 2. What the type labels mean

### Atomic sign
Smallest reusable graphic sign in the system. "Atomic" = smallest practical building block for the font, not "theologically basic."
Examples: punctum, virga, apostropha, tractulus, oriscus (new in v0.5).

### Component
A reusable graphic part that may appear inside larger neumes. May overlap with atomic signs.
Examples: quilisma jagged-wave core, rounded liquescent terminal, pressus vertical-plus-undulation, ascending tail connector.

### Neume family
A named chant category whose instances can be recognized across occurrences.
Examples: pes, flexa, climacus, scandicus, pressus, torculus, porrectus.

### Modified family
A family that adds a systematic feature.
Examples: liquescent forms, prepuncto forms, subpunctis forms.

### Repetition family
A family whose identity depends on pitch repetition.
Examples: apostropha family (bistropha, tristropha), pressus core behaviour.

### Composite sequence
A sequence made from already-known families. Usually should **not** become one final encoded glyph, unless (v0.5 addition) paleography names the compound as a distinctive Hildegard form — see RN-021 / RN-022.

### Hildegard-idiosyncratic compound (new in v0.5)
A multi-family shape that Gardiner, Meconi, or comparable paleographic sources specifically name as characteristic of Hildegard's hand. Treated as a dedicated glyph even though it looks compositionally like a sequence of families.

### Chart exemplar
A specific example in the transcription chart, useful for testing, not automatically a final font unit.

---

## 3. Core columns for the build sheet

| Field | Meaning |
| --- | --- |
| ID | Stable internal ID |
| Chart label | Exact wording from the chart (if present) |
| Canonical family label | Clean working name |
| Semantic type | Atomic / component / family / modified / repetition / composite / Hildegard-idiosyncratic |
| Contour | single, ascending, descending, repeated, up-down, down-up, ascending chain, descending chain, mixed |
| Family cardinality | Fixed / Variable / Subtype-dependent |
| Chart exemplar cardinality | Number of notes shown in the chart example |
| Pitch-relation pattern | Symbolic relation model such as `+`, `-`, `=`, `+-`, `-+`, `= -` |
| Repeated pitch core? | Yes / No / Partial |
| Variable ambitus? | Yes / No |
| Modifier | None / Liquescent / Prepuncto / Subpunctis / Composite |
| Constructor / recipe | Plain-language construction rule |
| Atomic parts used | Reusable pieces involved |
| Contextual allograph needs? | Yes / No / Maybe |
| Font strategy | Atomic component / dedicated glyph / assembly / both |
| **Paleographic source** (new) | Citation(s) attesting the form |
| Confidence | High / Medium / Low |
| Review notes | Manual-check field |

---

## 4. Hildegard-focused inventory table

Note: v0.4 rows RN-001 through RN-020 are carried forward with content unchanged except where explicitly noted. RN-021 and RN-022 are reclassified. RN-023 through RN-026 remain composite sequences. RN-027 through RN-035 are new in v0.5. For full column detail on unchanged rows, see v0.4; this table foregrounds the fields that matter for v0.5 decisions.

### 4.1 Core families (unchanged from v0.4 except font strategy phrasing)

| ID | Family | Semantic type | Contour | Family card. | Modifier | Font strategy | Paleographic source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RN-001 | virga | Atomic sign | single | Fixed | None | Dedicated glyph | Gardiner ch. 2 (basic neume inventory); Humdrum `v` |
| RN-002 | climacus | Neume family | descending chain | Variable | None | Assembly (virga + dot-puncta chain) | Gardiner ch. 2; ISHBS Music page; Humdrum `cl` |
| RN-003 | punctum | Atomic sign | single | Fixed | None | Dedicated glyph | Gardiner ch. 2; Humdrum `p` |
| RN-004 | scandicus | Neume family | ascending chain | Variable | None | Assembly (ascending virga+puncta) | Gardiner ch. 2; Humdrum `sc` |
| RN-005 | pes | Neume family | ascending | Fixed | None | Dedicated glyph, 3–4 span variants | Gardiner ch. 2 (podatus); Humdrum `pes`/`pd` |
| RN-006 | pes_flexus | Neume family | up-down | Fixed | None | Dedicated glyph; slight uplift in tail distinguishes from flexa (Gardiner Fig. 1 p. 15) | Gardiner p. 15, Fig. 1 |
| RN-007 | flexa | Neume family | descending | Fixed | None | Dedicated glyph, 3–4 span variants | Gardiner ch. 2 (clivis); Humdrum `cl`/`clv` |
| RN-008 | flexa_resupina | Neume family | down-up | Fixed | None | Dedicated glyph | Gardiner ch. 2; Humdrum `cl.r` |
| RN-009 | apostropha | Atomic sign / repetition seed | single | Fixed | None | Dedicated glyph | Gardiner ch. 2; Humdrum `ap` |
| RN-010 | bistropha | Repetition family | repeated | Fixed | None | Dedicated glyph | Gardiner ch. 2; Humdrum `ds`/`bs` |
| RN-011 | tristropha | Repetition family | repeated | Fixed | None | Dedicated glyph | Gardiner ch. 2; Humdrum `ts` |
| RN-012 | cephalicus | Modified family | descending | Fixed | Liquescent | Dedicated glyph; uses rounded-liquescent-terminal | Gardiner p. 60 — *O viridissima virga* Ex. 9, Riesencodex f. 474v ("the cephalicus involves a single pitch plus the liquesence") |
| RN-013 | epiphonus | Modified family | ascending | Fixed | Liquescent | Dedicated glyph; uses rounded-liquescent-terminal | Gardiner ch. 2 |
| RN-014 | pes_liquescens | Modified family | up-down | Fixed | Liquescent | Dedicated glyph | Gardiner ch. 2; Humdrum `pes.al`/`pes.dl` |
| RN-015 | pes_flexus_liquescens | Modified family | up-down-down | Fixed | Liquescent | Dedicated glyph | Gardiner ch. 2 |
| RN-016 | pressus | Neume family / repetition family | repeated | Subtype-dependent | None | Dedicated glyph — *"vertical line attached to a short undulating line"* (Gardiner p. 94) | Gardiner p. 94; Humdrum `pr.mi`/`pr.ma` |
| RN-017 | pressus_liquescens | Modified family | repeated then liquescent descent | Fixed | Liquescent | Dedicated glyph | Gardiner ch. 4 (flagged among idiosyncratic forms) |
| RN-018 | pressus_subpunctis | Modified family | repeated then descending tail | Fixed | Subpunctis | Dedicated glyph | Gardiner ch. 2 |
| RN-019 | quilisma | Special sign + neume family | rising / special-form | Subtype-dependent | None | Dedicated glyph — *"jagged waves connected to a smooth upward ascending stroke"* (Gardiner p. 94–95). Jagged-wave core + ascending tail as internal components. | Gardiner pp. 94–95 |
| RN-020 | quilisma_prepuncto | Modified family | prefixed rising special-form | Fixed | Prepuncto | Assembly (prefix punctum + quilisma) | Gardiner ch. 2 |

### 4.2 Reclassified in v0.5

| ID | Family | Old classification (v0.4) | **New classification (v0.5)** | Font strategy | Paleographic source |
| --- | --- | --- | --- | --- | --- |
| RN-021 | `flexa_resupina_pressus_subbipunctis` | Composite sequence (assembly only) | **Hildegard-idiosyncratic compound** | **Dedicated glyph** | Gardiner p. 16: *"elaborate compound flexus respinus/pressus/subbipunctis"* (sic — Gardiner writes "respinus" throughout; corrected to *resupinus* in production). |
| RN-022 | `flexa_resupina_pressus_liquescens` | Composite sequence (assembly only) | **Hildegard-idiosyncratic compound** | **Dedicated glyph** | Gardiner p. 16: *"flexus respina/pressus liquescens"* (sic — see note on RN-021 spelling). Gardiner flags both as *"idiosyncratic neumes… that can be challenging to decipher."* |

### 4.3 Composite sequences remaining as assembly-only

| ID | Family | Notes |
| --- | --- | --- |
| RN-023 | `composite_pes_cephalicus` | Generic sequence, not Hildegard-idiosyncratic. |
| RN-024 | `composite_flexa_pes` | Generic sequence. |
| RN-025 | `composite_quilisma_pressus` | Generic sequence. |
| RN-026 | `composite_quilisma_pressus_liquescens` | Generic sequence. |

### 4.4 New entries in v0.5

| ID | Family | Semantic type | Contour | Family card. | Modifier | Font strategy | Paleographic source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RN-027 | `tractulus` | Atomic sign | single | Fixed | None | Dedicated glyph (distinct from punctum — short horizontal dash form) | Gardiner ch. 2; Humdrum `tr` |
| RN-028 | `oriscus` (ascendens + descendens variants) | Atomic sign / component | single (directional) | Fixed (per variant) | None | Dedicated glyphs (2 variants: ascending, descending) | Gardiner ch. 2; SMuFL `chantOriscusAscending` / `chantOriscusDescending` / `chantOriscusLiquescens` |
| RN-029 | `torculus_rotundus` | Neume family | up-down | Fixed | None | Dedicated glyph, round/curved head variant | Gardiner ch. 2; Humdrum `to.ro` — explicitly split from quadratus |
| RN-030 | `torculus_quadratus` | Neume family | up-down | Fixed | None | Dedicated glyph, angular/square head variant | Gardiner ch. 2; Humdrum `to.qu` |
| RN-031 | `torculus_resupinus` | Neume family | up-down-up | Fixed | None | Dedicated glyph | Gardiner ch. 2; Humdrum `to.r` |
| RN-032 | `porrectus` | Neume family | down-up (with connecting diagonal) | Fixed | None | Dedicated glyph | Gardiner ch. 2; Humdrum `po` |
| RN-033 | `porrectus_flexus` | Neume family | down-up-down | Fixed | None | Dedicated glyph | Gardiner ch. 2; Humdrum `po.f` |
| RN-034 | `climacus_resupinus` | Neume family | descending-then-rising chain | Variable | None | Assembly | Gardiner ch. 2; Humdrum `cl.r` |
| RN-035 | `pes_subpunctis` | Modified family | up then descending tail | Variable in tail length | Subpunctis | Dedicated glyph + tail assembly | Gardiner ch. 2 |

---

## 5. Families vs chart exemplars — updated

### Families close to fixed graphical units
virga, punctum, tractulus, apostropha, bistropha, tristropha, pes, flexa, cephalicus, epiphonus, oriscus, torculus rotundus, torculus quadratus, torculus resupinus, porrectus, porrectus flexus, pes subpunctis.

### Families whose chart example should not be mistaken for the whole family
climacus, scandicus, climacus resupinus, quilisma, pressus.

### Dedicated-glyph Hildegard-idiosyncratic compounds (new category)
RN-021 (`flexa_resupina_pressus_subbipunctis`), RN-022 (`flexa_resupina_pressus_liquescens`).

### Assembly-only composites
RN-023, RN-024, RN-025, RN-026.

---

## 6. Atomic / component layer — updated for v0.5

| Component | Role | Status in v0.5 | Used by |
| --- | --- | --- | --- |
| `punctum` | Square note sign | Atomic | punctum, scandicus/climacus heads where square form applies |
| `dot-punctum` **(new)** | Rhineland detached dot — climacus/scandicus chains use these, NOT lozenges | Atomic | climacus, scandicus, climacus resupinus, subpunctis tails |
| `virga` | Stemmed note sign | Atomic | virga, climacus head, scandicus contexts |
| `tractulus` **(new)** | Short horizontal dash form | Atomic | tractulus as single-tone sign |
| `apostropha` | Repetition sign | Atomic | apostropha, bistropha, tristropha |
| `oriscus-ascendens` **(new)** | Ascending special-form head | Atomic / component | oriscus family, pes_quassus-style combinations if attested |
| `oriscus-descendens` **(new)** | Descending special-form head | Atomic / component | oriscus family, flexus-oriscus-style combinations if attested |
| `quilisma-jagged-core` | Jagged wave, never free-standing in Hildegard | Component | quilisma, quilisma prepuncto, quilisma+torculus |
| `ascending-tail-connector` **(new)** | Smooth upward stroke used as quilisma tail and in other rising connectors | Component | quilisma (mandatory tail), potentially torculus resupinus |
| `rounded-liquescent-terminal` **(revised)** | Hildegard-specific rounded lighter-stroke liquescent ending (Gardiner p. 92) | Component | cephalicus, epiphonus, pes_liquescens, pes_flexus_liquescens, pressus_liquescens, RN-022 |
| `pressus-core` **(revised)** | Vertical line + short undulating line (Gardiner p. 94) | Component | pressus, pressus_liquescens, pressus_subpunctis, RN-021, RN-022 |
| `subpunctis-tail` | Descending chain of dot-puncta | Component | pressus subpunctis, pes subpunctis, RN-021, composite subpunctis sequences |
| `torculus-round-head` **(new)** | Round pen-drawn up-down head | Component | torculus rotundus |
| `torculus-square-head` **(new)** | Angular up-down head | Component | torculus quadratus |

All dot-punctum, oriscus, tractulus, torculus-head, rounded-liquescent, pressus-core, and quilisma-jagged-core shapes should be **drawn from Dendermonde / Riesenkodex plates**, not from Solesmes reference.

---

## 7. Connector / construction layer

| Logic ID | Logic name | Role | Needed by |
| --- | --- | --- | --- |
| L-001 | ascending connector | joins lower note to higher continuation | pes, scandicus, epiphonus, quilisma-family rising forms, torculus resupinus (second leg) |
| L-002 | descending connector | joins upper note to lower continuation | flexa, climacus, cephalicus, subpunctis tails, torculus (descent), porrectus flexus (descent) |
| L-003 | rebound connector | handles down-up motion | flexa resupina, porrectus, mixed composites |
| L-004 | repeat-pitch join | handles same-note repercussion linkage | bistropha, tristropha, pressus family |
| L-005 | liquescent termination behaviour | governs transition into rounded-liquescent terminal | cephalicus, epiphonus, pes liquescens, pressus liquescens, RN-022 |
| L-006 | composite sequencing spacing | governs spacing and joining between consecutive families | RN-023 through RN-026 |
| L-007 **(new)** | porrectus diagonal stroke | draws the descending-then-rising diagonal body of the porrectus | porrectus, porrectus flexus |
| L-008 **(new)** | quilisma tail-attach behaviour | quilisma-jagged-core always terminates into ascending-tail-connector | quilisma, quilisma prepuncto, quilisma+pressus, quilisma+torculus |

---

## 8. Standalone vs assembly decision sheet — v0.5

### A. Definitely standalone in the shipped font

virga, punctum, dot-punctum, tractulus, apostropha, oriscus (asc + desc), bistropha, tristropha, pes, flexa, pes_flexus, flexa_resupina, cephalicus, epiphonus, pressus, pressus_subpunctis, torculus_rotundus, torculus_quadratus, torculus_resupinus, porrectus, porrectus_flexus, **RN-021 (flexa_resupina_pressus_subbipunctis), RN-022 (flexa_resupina_pressus_liquescens)** — the Hildegard-idiosyncratic compounds now sit here.

### B. Standalone recommended, with underlying construction model

pes_liquescens, pes_flexus_liquescens, pressus_liquescens, quilisma (with explicit jagged-core + ascending-tail internal components), pes_subpunctis.

### C. Assembly-first, optional convenience presets

scandicus, climacus, climacus_resupinus, quilisma_prepuncto.

### D. Assembly only

RN-023 (`composite_pes_cephalicus`), RN-024 (`composite_flexa_pes`), RN-025 (`composite_quilisma_pressus`), RN-026 (`composite_quilisma_pressus_liquescens`).

---

## 9. Finalized internal naming scheme — v0.5

| Family / item | Internal production name |
| --- | --- |
| virga | `virga` |
| punctum | `punctum` |
| dot-punctum | `dot_punctum` |
| tractulus | `tractulus` |
| apostropha | `apostropha` |
| oriscus ascendens | `oriscus_ascendens` |
| oriscus descendens | `oriscus_descendens` |
| bistropha | `bistropha` |
| tristropha | `tristropha` |
| pes | `pes` |
| pes flexus | `pes_flexus` |
| flexa | `flexa` |
| flexa resupina | `flexa_resupina` |
| cephalicus | `cephalicus` |
| epiphonus | `epiphonus` |
| pes liquescens | `pes_liquescens` |
| pes flexus liquescens | `pes_flexus_liquescens` |
| pes subpunctis | `pes_subpunctis` |
| climacus | `climacus` |
| climacus resupinus | `climacus_resupinus` |
| scandicus | `scandicus` |
| torculus rotundus | `torculus_rotundus` |
| torculus quadratus | `torculus_quadratus` |
| torculus resupinus | `torculus_resupinus` |
| porrectus | `porrectus` |
| porrectus flexus | `porrectus_flexus` |
| pressus | `pressus` |
| pressus liquescens | `pressus_liquescens` |
| pressus subpunctis | `pressus_subpunctis` |
| quilisma | `quilisma` |
| quilisma prepuncto | `quilisma_prepuncto` |
| **RN-021** | `hildegard_flexa_resupina_pressus_subbipunctis` |
| **RN-022** | `hildegard_flexa_resupina_pressus_liquescens` |
| composite pes + cephalicus | `composite_pes_cephalicus` |
| composite flexa + pes | `composite_flexa_pes` |
| composite quilisma + pressus | `composite_quilisma_pressus` |
| composite quilisma + pressus liquescens | `composite_quilisma_pressus_liquescens` |

The `hildegard_` prefix marks Hildegard-idiosyncratic compound forms as first-class dedicated glyphs — it is explicit that these are *not* composites but named Rhineland shapes.

---

## 10. Paleographic register & source grounding (new in v0.5)

### 10.1 Source manuscripts

- **Dendermonde, St.-Pieters-en-Paulusabdij, Cod. 9** ("Villarenser codex"), c. 1174/75. Cantus source [588309](https://cantusdatabase.org/source/588309). 57 Symphonia items. One column per page. Considered more authoritative by the ISHBS editors.
- **Wiesbaden, Hochschul- und Landesbibliothek RheinMain, Hs. 2** (Riesenkodex), c. 1180–85. Cantus source [588308](https://cantusdatabase.org/source/588308). 46 × 30 cm. Two columns per page, 17 staves per column. Music on ff. 466–481v. **Five scribal hands discernible in the codex overall** — variation is inherent; a modern font can responsibly pick a representative register.

### 10.2 Notational register

Per van Poucke (intro. to the Dendermonde facsimile, quoted in Gardiner 2022 p. 25): *"early German, in notational chronology between Sankt Gallen neumes and the so-called gothic neumes (Hufnagelschrift)."*

The font should therefore be:

- **Rounder than Hufnagel** (no horseshoe-nail virga; that is the next century).
- **More substantial than St Gall** (not the airy pointed-pen forms; these are heavier, ink-forward).
- **Fully heighted** on a 4-line staff (not adiastematic).
- **Ink register**: substantial monochrome; lighter "rounded off" strokes reserved for the liquescent family (Gardiner p. 92).

### 10.3 Staff

- **4 lines.**
- **Yellow line = C, red line = F.** This is a renderer responsibility, not a font responsibility — the font ships monochrome, and the renderer colours lines before placing glyphs.
- **Movable C-clef.**
- Text sits beneath the staff.

### 10.4 Specific stroke contracts

- **Climacus / scandicus**: virga + *detached dot-puncta*, not connected lozenge chains. Source: ISHBS editorial methodology + Gardiner ch. 2. Design consequence: dot-punctum is an atomic primitive; square `punctum` is *not* its climacus form.
- **Quilisma**: jagged-wave core *always attached* to a smooth ascending tail. Source: Gardiner pp. 94–95. Design consequence: no free-standing quilisma; the glyph is a fused quilisma-jagged-core + ascending-tail-connector.
- **Pressus**: vertical line attached to a short undulating line. Source: Gardiner p. 94.
- **Liquescents**: rounded off, lighter stroke. Source: Gardiner p. 92. Design consequence: all members of the liquescent family share a `rounded-liquescent-terminal` component with uniform lighter weight.
- **Pes flexus vs flexa**: distinguished by a slight uplift in the tail of the pes flexus. Source: Gardiner Fig. 1 p. 29. Design consequence: these are different glyphs, not derived.
- **Torculus rotundus vs quadratus**: both round and angular forms coexist. Source: Humdrum Hildegard representation (encoded separately); Gardiner ch. 2. Design consequence: two dedicated glyphs with different heads.

### 10.5 Explicitly rejected conventions

- **Square-notation lozenge chains** for climacus/scandicus — Solesmes convention, not Rhineland.
- **Free-standing three-lobed quilisma** — Liber Usualis convention, not Rhineland.
- **Horseshoe-nail virga** — Hufnagelschrift, one century too late.
- **Solesmes reference for stroke weight or pen angle** — reference Dendermonde / Riesenkodex plates directly.

### 10.6 Key citations

- Katie Gardiner, *A Conductor's Guide to the Music of Hildegard von Bingen*, DMA diss., Indiana University, 2022. [PDF](https://scholarworks.iu.edu/iuswrrest/api/core/bitstreams/1a626db3-354f-4a79-94c2-227cd959eec0/content).
- Peter van Poucke, intro. to *Symphonia: Dendermonde* facsimile (quoted in Gardiner).
- Lorenz Welker & Michael Klaper, *Hildegard von Bingen: Lieder: Faksimile Riesencodex (Hs. 2)*, Elementa Musicae, 1998.
- Marianne Richert Pfau, *Symphonia armonie celestium revelationum*, 8 vols., Hildegard Publishing Co., 1998.
- Honey Meconi, "The Unknown Hildegard: Editing, Performance, and Reception," in Monson & Marvin eds., 2013 — flags "incomplete pressus" as another idiosyncratic form.
- David Hiley, s.v. "Hufnagel," *Grove Music Online*, 2001.
- [International Society of Hildegard von Bingen Studies — Music page](https://www.hildegard-society.org/p/music.html).
- [Humdrum Hildegard representation](https://www.humdrum.org/Humdrum/representations/hildegard.rep.html) — analytic encoding with torculus rotundus/quadratus, pressus minor/maior, liquescent modifiers.
- [DiMusEd Tübingen Hildegard notation](https://www.dimused.uni-tuebingen.de/hildegard_notation.php) — was 503 during research; retry.

---

## 11. Architecture decision pointer (new in v0.5)

The v1 font architecture, derived in `research_synthesis.md`:

1. **Dumb components font** (~40–80 baseline-anchored glyphs) in OpenType. Aligned with SMuFL where SMuFL already has a codepoint; private PUA block for Hildegard-specific forms. See `smufl_codepoint_mapping.md`.
2. **Smart renderer as a Verovio extension**, consuming MEI neume-module input, drawing the two-colour 4-line staff, placing glyphs by computed (x, y) coordinates, and assembling variable-length families (climacus, scandicus, porrectus, torculus) from components at render time.
3. **No GSUB chant shaping** — OpenType shaping has one axis, chant has two (sequence + absolute pitch). Industry prior art (Gregorio, Caeciliae, Verovio) is unanimous that this approach fails.
4. **Minimal `kern` + handful of `rlig` ligatures** for Word/Illustrator paste compatibility as a bonus, not as the primary mechanism.
5. **MEI as semantic encoding target** — portable, notation-agnostic, compatible with digital musicology.

Rationale in full: see `research_synthesis.md`.

---

## 12. What to build next

1. **Direct manuscript reading pass.** Dendermonde Cod. 9 and Riesenkodex Hs. 2 digitizations; Gardiner Fig. 6 ("basic neumes from Riesencodex f. 470r"); retry DiMusEd Tübingen page.
2. **SMuFL codepoint mapping** — see `smufl_codepoint_mapping.md` (v0.1 sketch).
3. **Hand / Illustrator trace pass** — ~40 atomic + fixed-family shapes, traced from manuscript plates. Nail the stroke register before any `.sfd` work.
4. **Verovio prototype** — swap one existing SMuFL chant font with 5–10 sketched atoms as proof of concept.
5. **First `.sfd` source.** FontForge, modelled structurally on `greciliae-base.sfd` but with Hildegard glyph shapes and v0.5 glyph names.
6. **Build script.** Minimal Python FontForge generator emitting `.ttf` from `.sfd`. Start simple; resist building a `squarize.py` clone until proved necessary.
7. **v0.6 inventory** — fold in findings from the direct manuscript pass (stroke-weight measurements, further attested forms, variation notes between D and R).
