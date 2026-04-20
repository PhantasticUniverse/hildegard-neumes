# SMuFL Codepoint Mapping — Hildegard Neume Font v0.1

Status: v0.1 sketch, 2026-04-14.
Scope: codepoint allocation plan for the Hildegard/Rhineland neume font. Maps each inventory item from `glyph_inventory_v0.5.md` to either an existing SMuFL codepoint (reused) or a private PUA codepoint (Hildegard-specific).
Companion docs: `research_synthesis.md`, `glyph_inventory_v0.5.md`.

Verified against SMuFL `glyphnames.json` and `ranges.json` at `../reference-repos/smufl-gh-pages/metadata/`.

---

## 1. Allocation strategy

**Principle 1 — use SMuFL where semantics align, even if the Rhineland stroke differs.**
If a glyph is semantically a punctum, virga, quilisma, oriscus, strophicus, episema, or similar atomic sign already named in SMuFL, occupy the standard SMuFL codepoint. The *drawing* is Rhineland (stroke register per § 10.2 of the inventory), but the *position* is standard. This buys free interop with MuseScore, Finale, Dorico, Verovio, and any SMuFL-aware tool: they see a punctum where SMuFL says one is. Document the Rhineland register divergence in the font metadata, not in the codepoint choice.

**Principle 2 — use private PUA for Hildegard-specific forms SMuFL does not model.**
Distinct shapes that have no SMuFL name (dot-punctum distinct from square punctum, rounded-liquescent-terminal as a named component, pressus-core as "vertical line + undulation", Hildegard-idiosyncratic compounds) go into a dedicated private PUA block. Chosen block: **U+F400–U+F4FF**. This is clear of the highest SMuFL allocation (U+EF08 as of the current metadata) with ~1,270 codepoints of headroom between them.

**Principle 3 — do not overload SMuFL codepoints for family-level neumes.**
SMuFL has `chantPodatusLower` / `chantPodatusUpper` and `chantDeminutumUpper` / `chantDeminutumLower`, but these model a two-part podatus in a very specific way (lower + upper component typed as a pair). Our `pes` is a family with per-span variants. Occupying `chantPodatusLower`/`Upper` with our pes glyphs would mis-signal semantics to SMuFL-aware tools. Instead, use SMuFL's punctum/virga atoms for the components *within* our pes glyph, and put our dedicated pes family glyphs in private PUA.

**Principle 4 — staff + clefs + division marks do use SMuFL codepoints.**
These are unambiguous. Our Rhineland 4-line staff, movable C-clef, and divisio marks occupy SMuFL's standard positions. The renderer draws the yellow-C/red-F colouring separately; the font glyph is monochrome.

**Principle 5 — the private PUA block is reserved and documented.**
U+F400–U+F4FF is this font's Hildegard private extension range. Final allocations are stable from v1 onward; pre-v1 slot changes are allowed with a documented diff.

---

## 2. SMuFL glyphs reused (standard codepoints)

These occupy SMuFL's existing chant range. Drawing register is Rhineland; semantics match SMuFL.

### 2.1 Staff, clefs, divisio (U+E8F0–U+E906)

| Inventory role | SMuFL name | Codepoint | Notes |
| --- | --- | --- | --- |
| 4-line chant staff (rendered as font char when compiling-from-font) | `chantStaff` | U+E8F0 | Monochrome in font; yellow C / red F is a *renderer* responsibility. |
| Staff wide variant | `chantStaffWide` | U+E8F1 | Optional. |
| Staff narrow variant | `chantStaffNarrow` | U+E8F2 | Optional. |
| Divisio minima | `chantDivisioMinima` | U+E8F3 | |
| Divisio maior | `chantDivisioMaior` | U+E8F4 | |
| Divisio maxima | `chantDivisioMaxima` | U+E8F5 | |
| Divisio finalis | `chantDivisioFinalis` | U+E8F6 | |
| Virgula | `chantVirgula` | U+E8F7 | |
| Caesura | `chantCaesura` | U+E8F8 | |
| F-clef (plainchant) | `chantFclef` | U+E902 | |
| C-clef (plainchant) | `chantCclef` | U+E906 | Movable in Hildegard sources. |

### 2.2 Single-note forms (U+E990–U+E9AF)

| Inventory ID | Inventory name | SMuFL name | Codepoint | Register note |
| --- | --- | --- | --- | --- |
| RN-003 | `punctum` | `chantPunctum` | U+E990 | Square/block punctum drawn in Rhineland register. |
| — | `punctum_inclinatum` (future) | `chantPunctumInclinatum` | U+E991 | Slanted punctum — not in v0.5 inventory but reserved for a future row if attested in D/R. |
| — | `punctum_inclinatum_auctum` (future) | `chantPunctumInclinatumAuctum` | U+E992 | Reserved. |
| — | `punctum_inclinatum_deminutum` (future) | `chantPunctumInclinatumDeminutum` | U+E993 | Reserved. |
| — | `punctum_auctum_asc` (future) | `chantAuctumAsc` | U+E994 | Reserved. |
| — | `punctum_auctum_desc` (future) | `chantAuctumDesc` | U+E995 | Reserved. |
| RN-001 | `virga` | `chantPunctumVirga` | U+E996 | Stemmed virga — Rhineland-register body. |
| — | `virga_reversed` | `chantPunctumVirgaReversed` | U+E997 | Reserved (attested in some Germanic notations; verify in D/R). |
| — | (not used) | `chantPunctumCavum` | U+E998 | Hollow variant — not planned in v1. |
| — | (not used) | `chantPunctumLinea` | U+E999 | Not planned. |
| — | (not used) | `chantPunctumLineaCavum` | U+E99A | Not planned. |
| RN-019 (core only) | `quilisma` | `chantQuilisma` | U+E99B | **Divergence**: SMuFL's quilisma is the free-standing three-lobed square form. Hildegard's is jagged-wave + attached ascending tail (Gardiner pp. 94–95). We occupy this codepoint with the Rhineland form; document in metadata that register differs. Users who want a square-quilisma should not use this font. |
| RN-028a | `oriscus_ascendens` | `chantOriscusAscending` | U+E99C | Direct match. |
| RN-028b | `oriscus_descendens` | `chantOriscusDescending` | U+E99D | Direct match. |
| — | `oriscus_liquescens` | `chantOriscusLiquescens` | U+E99E | Reserved. |
| RN-009 | `apostropha` | `chantStrophicus` | U+E99F | Note SMuFL calls this "strophicus," not "apostropha" — the terms are interchangeable in most paleographic traditions. |
| — | `strophicus_auctus` | `chantStrophicusAuctus` | U+E9A0 | Reserved. |
| — | `punctum_deminutum` | `chantPunctumDeminutum` | U+E9A1 | Reserved. |

### 2.3 Multi-note forms (U+E9B0–U+E9CF)

SMuFL's multi-note range is *deliberately used sparingly* for this font. SMuFL names precomposed forms for intervals 2nd–6th; they don't cover the whole Hildegard family. For most families we use private PUA. Only the ones below map cleanly.

| Inventory ID | Inventory name | SMuFL name | Codepoint | Notes |
| --- | --- | --- | --- | --- |
| — | (component) entry line asc 2nd | `chantEntryLineAsc2nd` | U+E9B4 | Reserved — potentially useful as an ascending-tail-connector substrate. |
| — | entry line asc 3rd | `chantEntryLineAsc3rd` | U+E9B5 | Reserved. |
| — | entry line asc 4th | `chantEntryLineAsc4th` | U+E9B6 | Reserved. |
| — | entry line asc 5th | `chantEntryLineAsc5th` | U+E9B7 | Reserved. |
| — | entry line asc 6th | `chantEntryLineAsc6th` | U+E9B8 | Reserved. |
| — | ligatura desc 2nd | `chantLigaturaDesc2nd` | U+E9B9 | Reserved. |
| — | ligatura desc 3rd | `chantLigaturaDesc3rd` | U+E9BA | Reserved. |
| — | ligatura desc 4th | `chantLigaturaDesc4th` | U+E9BB | Reserved. |
| — | ligatura desc 5th | `chantLigaturaDesc5th` | U+E9BC | Reserved. |
| — | connecting line asc 2nd | `chantConnectingLineAsc2nd` | U+E9BD | Reserved. |
| — | connecting line asc 3rd–6th | … | U+E9BE–U+E9C1 | Reserved. |
| — | strophicus liquescens 2nd–5th | … | U+E9C2–U+E9C5 | Reserved. |

We do **not** map `pes` to `chantPodatusLower`/`chantPodatusUpper`. SMuFL's podatus is a two-glyph typing model (lower then upper) that conflicts with our family-level pes glyph. Use private PUA instead.

### 2.4 Articulations (U+E9D0–U+E9DF)

| Inventory role | SMuFL name | Codepoint | Notes |
| --- | --- | --- | --- |
| Ictus above | `chantIctusAbove` | U+E9D0 | Reserved for future ornament layer. |
| Ictus below | `chantIctusBelow` | U+E9D1 | |
| Circulus above | `chantCirculusAbove` | U+E9D2 | |
| Circulus below | `chantCirculusBelow` | U+E9D3 | |
| Semicirculus above | `chantSemicirculusAbove` | U+E9D4 | |
| Semicirculus below | `chantSemicirculusBelow` | U+E9D5 | |
| Accentus above | `chantAccentusAbove` | U+E9D6 | |
| Accentus below | `chantAccentusBelow` | U+E9D7 | |
| Episema | `chantEpisema` | U+E9D8 | Likely needed in v1 if episema marks are attested in D/R — verify. |
| Augmentum | `chantAugmentum` | U+E9D9 | Mora sign. |

### 2.5 Miscellany — custos (U+EA04–U+EA09)

| Inventory role | SMuFL name | Codepoint |
| --- | --- | --- |
| Custos stem up, lowest | `chantCustosStemUpPosLowest` | U+EA04 |
| Custos stem up, low | `chantCustosStemUpPosLow` | U+EA05 |
| Custos stem up, middle | `chantCustosStemUpPosMiddle` | U+EA06 |
| Custos stem down, middle | `chantCustosStemDownPosMiddle` | U+EA07 |
| Custos stem down, high | `chantCustosStemDownPosHigh` | U+EA08 |
| Custos stem down, highest | `chantCustosStemDownPosHighest` | U+EA09 |

---

## 3. Private PUA block — U+F400–U+F4FF (Hildegard extension)

This block is reserved for this font and documented in its metadata. Sub-ranges group related glyphs for ease of maintenance.

### 3.1 Hildegard-specific atomic components — U+F400–U+F41F

| Code | Glyph name | Inventory ref | Purpose |
| --- | --- | --- | --- |
| U+F400 | `hildegard.dot_punctum` | Component (new in v0.5) | Rhineland detached dot for climacus/scandicus chains. **Not** the square punctum at U+E990 — these are visually distinct. |
| U+F401 | `hildegard.tractulus` | RN-027 | Short horizontal dash single-tone sign. |
| U+F402 | `hildegard.rounded_liquescent_terminal` | Component (new in v0.5) | Rounded, lighter-stroke liquescent ending (Gardiner p. 92). Shared across cephalicus, epiphonus, pes_liquescens, pressus_liquescens, RN-022. |
| U+F403 | `hildegard.pressus_core` | Component (new in v0.5) | Vertical line + short undulating line (Gardiner p. 94). Shared across pressus, pressus_liquescens, pressus_subpunctis, RN-021, RN-022. |
| U+F404 | `hildegard.quilisma_jagged_core` | Component (new in v0.5) | Jagged-wave core, never free-standing — always occurs attached to an ascending tail. |
| U+F405 | `hildegard.ascending_tail_connector` | Component (new in v0.5) | Smooth upward stroke used as quilisma tail. |
| U+F406 | `hildegard.subpunctis_tail` | Component | Descending chain of dot-puncta; variable length handled at render time. |
| U+F407 | `hildegard.torculus_round_head` | Component | Round pen-drawn up-down head (for torculus rotundus). |
| U+F408 | `hildegard.torculus_square_head` | Component | Angular up-down head (for torculus quadratus). |
| U+F409–U+F41F | reserved | — | — |

### 3.2 Fixed-family dedicated glyphs — U+F420–U+F43F

These are family-level glyphs, drawn as whole shapes. Span variants are encoded as stylistic-set alternates or as separate adjacent codepoints (decision deferred — see § 4).

| Code | Glyph name | Inventory ref |
| --- | --- | --- |
| U+F420 | `hildegard.pes` | RN-005 |
| U+F421 | `hildegard.pes_flexus` | RN-006 |
| U+F422 | `hildegard.flexa` | RN-007 |
| U+F423 | `hildegard.flexa_resupina` | RN-008 |
| U+F424 | `hildegard.bistropha` | RN-010 |
| U+F425 | `hildegard.tristropha` | RN-011 |
| U+F426–U+F43F | reserved | — |

### 3.3 Torculus and porrectus family — U+F440–U+F45F

| Code | Glyph name | Inventory ref |
| --- | --- | --- |
| U+F440 | `hildegard.torculus_rotundus` | RN-029 |
| U+F441 | `hildegard.torculus_quadratus` | RN-030 |
| U+F442 | `hildegard.torculus_resupinus` | RN-031 |
| U+F443 | `hildegard.porrectus` | RN-032 |
| U+F444 | `hildegard.porrectus_flexus` | RN-033 |
| U+F445–U+F45F | reserved | — |

### 3.4 Liquescent family — U+F460–U+F47F

| Code | Glyph name | Inventory ref |
| --- | --- | --- |
| U+F460 | `hildegard.cephalicus` | RN-012 |
| U+F461 | `hildegard.epiphonus` | RN-013 |
| U+F462 | `hildegard.pes_liquescens` | RN-014 |
| U+F463 | `hildegard.pes_flexus_liquescens` | RN-015 |
| U+F464 | `hildegard.pes_subpunctis` | RN-035 |
| U+F465–U+F47F | reserved | — |

### 3.5 Pressus family — U+F480–U+F49F

| Code | Glyph name | Inventory ref |
| --- | --- | --- |
| U+F480 | `hildegard.pressus` | RN-016 |
| U+F481 | `hildegard.pressus_liquescens` | RN-017 |
| U+F482 | `hildegard.pressus_subpunctis` | RN-018 |
| U+F483–U+F49F | reserved | — |

### 3.6 Hildegard-idiosyncratic compounds — U+F4A0–U+F4BF

These are first-class dedicated glyphs, not assemblies. Named compounds flagged by Gardiner pp. 32–33 as characteristic of Hildegard's hand.

| Code | Glyph name | Inventory ref |
| --- | --- | --- |
| U+F4A0 | `hildegard.flexa_resupina_pressus_subbipunctis` | RN-021 |
| U+F4A1 | `hildegard.flexa_resupina_pressus_liquescens` | RN-022 |
| U+F4A2 | `hildegard.incomplete_pressus` (reserved) | Meconi 2013 — flag; verify |
| U+F4A3–U+F4BF | reserved | — |

### 3.7 Reserved for v2 — U+F4C0–U+F4FF

Reserved for future: precomposed convenience sub-font (if shipped), climacus/scandicus presets, stylistic-set alternates, cross-manuscript variants (Dendermonde vs Riesenkodex hand), composite sequences if any are promoted from assembly to dedicated.

---

## 4. Open questions for allocation

1. **Span variants for fixed families.** `pes` can span a 2nd, 3rd, 4th, 5th. Options:
   - (a) One codepoint, multiple stylistic-set alternates (`ss01`–`ss04`) selecting span.
   - (b) Separate adjacent codepoints (`pes_2nd` at U+F420, `pes_3rd` at U+F421, etc.).
   - (c) Single codepoint, renderer composes from atoms at draw time.
   - **Tentative preference**: (c) for variable families, (a) for fixed families. Deferred to first `.sfd` pass.

2. **Quilisma codepoint.** Do we occupy `chantQuilisma` (U+E99B) with the Rhineland jagged-core-with-tail form, or move it to private PUA and leave U+E99B unused? Current decision: **occupy U+E99B** for interop; draw it Rhineland. Flag in font metadata that the register differs. Revisit if it causes confusion in SMuFL-aware tools.

3. **`apostropha` vs `chantStrophicus`.** Paleographic traditions use both terms for the same shape. We occupy `chantStrophicus` (U+E99F) and use the internal name `apostropha`. Alternatively, we could reserve a private PUA code and leave U+E99F for a more canonical square-form strophicus. Current decision: **occupy U+E99F**.

4. **`punctum_inclinatum` family.** SMuFL allocates three codepoints for inclinatum (U+E991–U+E993). Punctum inclinatum is the slanted form used in descending climacus chains in square notation. Hildegard's climacus uses *dot-puncta*, not inclinatums. We should probably **not** occupy these codepoints — leave them unused, and let SMuFL-aware tools notice the gap. The dot-punctum lives at U+F400.

5. **Multi-note SMuFL range.** Do we reuse any of U+E9B0–U+E9CF? Current position: **no**, use private PUA for all family-level glyphs. Reserve the SMuFL multi-note range for a future v2 convenience sub-font if we want SMuFL-tool compatibility for precomposed common intervals.

6. **Episema usage.** Is episema attested in Dendermonde or Riesenkodex? If yes, we ship the glyph at U+E9D8. If it's not attested, we leave the slot unused in v1.

7. **Staff-line colour.** The monochrome staff at U+E8F0 is used if the renderer treats staff lines as font characters. Colour (yellow C, red F) is applied in SVG by the renderer. Alternatively, we could ship two colourable SVG-in-OT layers — but § 2 of `research_synthesis.md` argues against COLR/SVG-in-OT for compat reasons. Current decision: **monochrome font, renderer colours**.

---

## 5. Font metadata (OpenType `name` / `meta`)

The font's OpenType metadata should declare:

- **Font family**: `Hildegard Neume` (or final name TBD)
- **Version**: matches inventory version (`v0.5` in inventory → font version `0.5.0`)
- **Vendor ID**: TBD (4-char OpenType vendor tag)
- **License**: TBD (recommend OFL 1.1 for Gregorio-family compatibility)
- **`meta` table** with:
  - `dlng` (designed languages): `Latn`
  - Custom tag `smufl` pointing to a SMuFL metadata JSON documenting:
    - Which SMuFL codepoints are occupied (listed in § 2 above).
    - The private PUA block U+F400–U+F4FF with glyph names and descriptions.
    - Divergences from SMuFL register (notably the quilisma at U+E99B).
    - Paleographic source citations per glyph (Gardiner pages, Humdrum names, manuscript folios where known).

Model the SMuFL metadata JSON on Bravura's `bravura_metadata.json` (in Bravura's repo) and Gregorio's `greciliae.json` structure. Fields to include: `fontName`, `fontVersion`, `engravingDefaults`, `glyphAdvanceWidths`, `glyphsWithAnchors`, and a custom `hildegardExtension` block documenting the PUA allocations and paleographic sources.

---

## 6. Interop expectations

With this mapping:

- **MuseScore / Finale / Dorico / Verovio** will display the font's staff, clefs, divisio marks, punctum, virga, quilisma, oriscus, strophicus, articulations, and custos at their standard positions. They will *not* automatically display the family-level glyphs (pes, flexa, torculus, porrectus) or the Hildegard compounds — those are in PUA.
- **Verovio with MEI neume input** will need a custom font mapping table pointing Hildegard neume types to the private PUA codepoints. This is the primary intended use path.
- **Illustrator / Word** can paste any codepoint directly; our `kern` table handles horizontal joining for atoms. Family-level glyphs paste as single characters.
- **Gregorio / gabc** — not a target in v1. v2 could add a MEI→gabc bridge so the font works with GregorioTeX.

---

## 7. Next steps for this document

1. Verify all SMuFL codepoints against the latest `glyphnames.json` when SMuFL releases a new version.
2. Once the first `.sfd` pass is done, lock span-variant allocation (question § 4.1) and freeze the U+F420–U+F4AF assignments.
3. Add a `glyph notes` column to § 3 with the SFD source file and glyph-name-within-SFD once FontForge sources exist.
4. Draft `hildegard_metadata.json` following the Bravura pattern as the font's SMuFL metadata sidecar.
