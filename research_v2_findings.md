# Research v2 — Findings

Second pass, 2026-04-14. Supplements `research_synthesis.md` after three parallel agent runs focused on: (1) retrying DiMusEd and hunting digital manuscripts; (2) deep-reading Gardiner 2022; (3) planning Verovio integration.

This document captures **new** findings and corrections. The first-pass document (`research_synthesis.md`) remains canonical for the architectural rationale; this document overrides it where conflicts exist.

---

## 1. Digital manuscript surrogates are accessible

Both primary sources are fully digitized and openly available.

### 1.1 Wiesbaden Riesencodex Hs. 2 — HLB RheinMain, CC-BY 4.0

- **Landing page**: `https://hlbrm.digitale-sammlungen.hebis.de/handschriften-hlbrm/content/titleinfo/449618`
- **Full PDF** (264 MB, 481 leaves, CC-BY 4.0): `https://hlbrm.digitale-sammlungen.hebis.de/download/pdf/449618.pdf`
- **URN**: `urn:nbn:de:hebis:43-972`. Published 2006 by HLB RheinMain. Viewer is Visual Library Server (no IIIF), exposing JPEG tiers at 504 / 1000 / 2000 px via `/handschriften-hlbrm/image/view/{id}?w={width}`.
- **Folio → pageview ID mapping** (useful for direct linking):
  - f. 470r — pageview `450574` (Gardiner 2022 Fig. 6, basic-neume reference plate)
  - f. 474r — pageview `450582`
  - f. 474v — pageview `450583` (*O viridissima virga*, Example 9 — cephalicus + pressus liquescens)
  - Pattern: f. n increments the pageview ID by 1 per side. Use arithmetic to jump to other folios.

### 1.2 Dendermonde Cod. 9 — IMSLP, public domain

- **IMSLP main page**: `https://imslp.org/wiki/Dendermonde_Codex_(Hildegard)`
- **Direct PDF** (1.12 GB, 371 pages, public domain, scanned by Teneo Belgian institutional repository 2024-03-27): `https://imslp.org/wiki/File:PMLP1425654-B-DEa_MS_9.pdf`
- **Alternate (Teneo / LIBIS)**: `https://repository.teneo.libis.be/delivery/DeliveryManagerServlet?dps_pid=IE15126695`
- **Cantus Database source 588309** links to the same Teneo hosting.

### 1.3 DiMusEd Tübingen — still unreachable

DiMusEd Tübingen returned HTTP 503 across all paths (main domain, Hildegard notation page, downloads). This appears to be a site-wide outage, not a transient issue. Google's snippet preserves a short description: *"German neumes on lines… a new notation form in Germany, found especially in the context of reform orders like the Cistercians and the Hirsau Reform."* Full content not recoverable in this pass.

**However**, a related finding: the **MEI Neumes Module was originally developed as part of the DiMusEd Hildegard project at Tübingen**, led by Gregor Schräder under Prof. Stefan Morent. This is documented verbatim in `music-encoding-develop/source/docs/06-neumes.xml` in the `neumesBackground` section. Put plainly: **MEI's neume schema was built for exactly this repertoire.** Encoding Hildegard's music in MEI is walking the schema's home ground, not bending it to fit.

### 1.4 hildegard-society.org — link hub, no plates

The society site is a link-and-commentary hub, not an image repository. Individual antiphon pages (e.g., `o-viridissima-virga-song.html`) link out to Hebis pageviews rather than reproducing plates. No scribal-hand galleries, no facsimile images. The full ~60-antiphon index is organized at `https://www.hildegard-society.org/p/music.html`; each commentary page is by Beverly Lomer (transcription/music notes) and Nathaniel M. Campbell (textual commentary).

The **International Society of Hildegard von Bingen Studies** and `hildegard-society.org` are the same organization — no separate scholarly-society domain exists.

---

## 2. Gardiner 2022 deep-read — corrections to v0.5

A full text extraction of Katie Gardiner, *A Conductor's Guide to the Music of Hildegard von Bingen* (DMA diss., Indiana University, 2022, 167 pp.) produced several corrections to what we thought v0.5 could claim.

### 2.1 Page-reference errors

Our first pass placed several passages on wrong pages (best-guess extrapolation from the agent's summary prose). The corrections are in `glyph_inventory_v0.5.md` § 0.1. In summary:

| Passage | Our claim | Actual location |
| --- | --- | --- |
| "Slight uplift in the tail of the pes flexus" + Fig. 1 | p. 29 | **p. 15** (Chapter 1) |
| "Elaborate compound flexus respinus/pressus/subbipunctis" | pp. 32–33 | **p. 16** (Chapter 1) |
| *O viridissima virga* cephalicus / pressus liquescens | "ch. 4" (vague) | **p. 60** (Example 9, Ch. 4) |
| Figure 6 "basic neumes from Riesencodex f. 470r" | Chapter 2 | **p. 91** (opens Chapter 4) |
| Chapter 2 extent | pp. 20–50 | **pp. 20–40** |
| van Poucke "between Sankt Gallen and Hufnagelschrift" quote | p. 25 | **pp. 25–26** |

### 2.2 Gardiner's spelling: "respinus/respina" not "resupinus/resupina"

Gardiner consistently writes the Latin form of the idiosyncratic compound names as *respinus/respina* — without the `u`. Classical Latin is *resupinus/resupina* (from *resupino*, "to bend back"). *Respinus* isn't attested as Latin. This is either Gardiner's transcription error or a corruption inherited from van Poucke's Alamire introduction (her cited source). **Production naming uses the corrected form** (`flexa_resupina_…`) and flags Gardiner's variant in the source column.

### 2.3 Source-strength downgrades

Several v0.5 entries claim Gardiner attestation that the dissertation does not actually support:

- **NOT in Gardiner at all** (Humdrum-only): `tractulus`, `torculus_rotundus` / `torculus_quadratus` split, `climacus_resupinus`, `epiphonus`, and the oriscus variants (salicus, pes quassus).
- **Weakly in Gardiner** (mentioned generically but not as a specific named neume): `pes_subpunctis` (only "climacus and subpunctis constructions" at p. 82, generic), `pes_liquescens` / `pes_flexus_liquescens` / `pressus_liquescens` (components named separately, compound names not enumerated).
- **In Gardiner but only as a square-notation reference**: `torculus_resupinus` (Fig. 5 p. 77 — square notation for comparison, not a Hildegard-specific plate).
- **Properly in Gardiner**: punctum, virga, pes, clivis / flexa, climacus, scandicus, torculus, porrectus / flexa resupina, quilisma, quilisma prepuncto, pressus, pressus liquescens, cephalicus (single mention p. 60), apostropha / bistropha / tristropha (p. 91), oriscus (pp. 93–94), and the two idiosyncratic compounds (p. 16).

**Implication**: v0.5's inventory is broader than what can be defended strictly from Gardiner. That's fine — the Humdrum Hildegard representation is an independent second source, and Humdrum's author clearly did fuller paleographic analysis than Gardiner. But the **paleographic source column** in v0.5 should accurately label each entry by strength, and some decisions (e.g., the torculus rotundus/quadratus split) should be **held until direct manuscript inspection** before committing to two dedicated glyphs. v0.5a has been edited to reflect this.

### 2.4 Gardiner's Figure 6 neume labels (p. 91)

Fig. 6 reproduces eight basic neumes from Riesencodex f. 470r, labeled by Gardiner in the text above each clipping:

> **virga | punctum | pes | clivis | climacus | scandicus | torculus | porrectus**

Notable: Gardiner uses **clivis** (not flexa) and **porrectus** (not flexa resupina) in the figure, though her surrounding prose treats them as synonyms. This is a useful sanity check for the Tier 1 MVP glyph set — those eight forms are what the standard reference plate itself shows.

### 2.5 Gardiner does not discuss pen, nib, stroke angle, or scribal hands

I searched the entire dissertation for "pen", "nib", "quill", "stroke angle", "scribe", "scribal hand", "multiple hands", "five hands", "Hand A/B", "ductus", and every related term. **Gardiner does not discuss any of it.** The word "hand" appears only in the sense of "hand-written neumes," not paleographic hand analysis. The five scribal hands of the Riesencodex documented in Cantus DB source 588308 are not treated in Gardiner.

The only concrete visual descriptions in Gardiner are the four we already have:
1. "Slight uplift in the tail of the pes flexus" (p. 15)
2. Liquescent: *"rounded off, lighter stroke"* (p. 92)
3. Pressus: *"a vertical line attached to a short undulating line"* (p. 94)
4. Quilisma: *"two small jagged-looking waves with a gracefully curved line ascending the distance of a third or sometimes a fourth"* + *"connected to a smooth upward ascending stroke"* (pp. 94–95)

**For pen angle, nib width, stroke weight, and scribal-hand distinctions: Gardiner is not a source.** Use van Poucke 1991 (Alamire Dendermonde facsimile introduction), Welker/Klaper 1998 (Reichert Verlag Riesencodex facsimile), Hiley *Western Plainchant* pp. 340–400, or direct manuscript inspection.

### 2.6 Cephalicus / pressus liquescens passage — actual text (p. 60)

> "The pressus liquescens involves a doubled pitch plus the liquescence, while the cephalicus involves a single pitch plus the liquesence [sic]. One example where these neumes occur in succession is on the word 'frumentum:' [Example 9, Hildegard *O viridissima virga*, Riesencodex f. 474v, cephalicus and pressus liquescens] While from this perspective one is able to see the difference between the first two neumes of the word 'frumentum,' it is imaginable that they were challenging to distinguish in the Gmelch black-and-white plates that Page was working from."

This is the **strongest single piece of paleographic grounding** we have for the cephalicus. It identifies a specific word in a specific folio where the form contrasts with pressus liquescens. First target for sketch-pass work.

### 2.7 Fig. 4 in Gardiner is the same chart as our reference image

Gardiner's Figure 4 (p. 37) is "Hildegard of Bingen Symphonia neume transcription chart — from Beverly Lomer at the International Society of Hildegard von Bingen Studies website (hildegard-society.org/p/music.html)." This is the same chart as `Hildegard_of_Bingen_Symphonia_Neume_Transcription_Chart.jpg` in this project directory. Source confirmed: Lomer/ISHvBS, reproduced in Gardiner.

---

## 3. Verovio neume support — concrete integration architecture

Detailed integration plan in `verovio_integration_plan.md`. Key findings that affect architecture:

### 3.1 Verovio neume support is upstream and first-class

`rism-digital/verovio` has dedicated source files for neume rendering in `src/neume.cpp`, `src/nc.cpp`, `src/view_neume.cpp`, `src/calcligatureorneumeposfunctor.cpp`, plus `include/vrv/neume.h` with a `NeumeGroup` enum of 15 values. MEI neume mode is activated by `notationtype="neume"` on `<staffDef>`; there is no `--neume` flag.

### 3.2 Verovio's current dispatch is square-note-atom-based, not whole-neume

**Critical finding.** Verovio's `CalcLigatureOrNeumePosFunctor::VisitNeume` walks each `<nc>` and assigns atomic SMuFL codepoints *per component* — punctum, virga, punctum inclinatum, etc. It does **not** have a "whole-neume compound glyph" dispatch path. A pes is rendered as a lower punctum + upper punctum, not as a single pes glyph. The `NeumeGroup` enum is used for *spacing calculations*, not for glyph selection.

**Implication for Hildegard**: the Rhineland tradition draws pes, clivis, torculus, porrectus as single pen-gesture shapes, not atom chains. Verovio cannot render these out of the box. We must add a compound-glyph dispatch branch. Concretely:

- Patch `include/vrv/neume.h` to extend `NeumeGroup` with Hildegard family values.
- Patch `src/neume.cpp` `GetNeumeGroup()` to read `<neume @type>` as an MEI-level hint that overrides contour lookup (needed because e.g. torculus rotundus vs quadratus have identical contours).
- Patch `src/calcligatureorneumeposfunctor.cpp` `VisitNeume` to, when `notationtype="neume.rhineland"`, overwrite `m_drawingGlyphs` with a single compound codepoint (from our PUA block U+F420+) and zero the rest.
- Add a `NOTATIONTYPE_neume_rhineland` value to `vrvdef.h`'s `NotationType` enum.

### 3.3 MEI `<neume>` has no controlled `@name`; use `@type`

MEI's `<neume>` element does not carry a canonical family-name attribute. Instead it uses the generic `att.typed` facet via `@type`, which is a free-form string available on every element. Our "Hildegard profile" is simply a documented vocabulary of `@type` values (`torculus_rotundus`, `flexa_resupina_pressus_subbipunctis`, etc.) — **no MEI schema extension is required**. Other repertoires (Aquitanian, Old Hispanic, St Gall) already use this pattern in the Neumes Module samples at `music-encoding-develop/source/examples/neumes/`.

### 3.4 Font distribution — fork, don't zip

Verovio's `--font-add-custom` CLI option accepts a zip that can swap glyph paths for existing codepoints, but **cannot register new codepoints in the build-time-generated `smufl.h` header**. Since Hildegard-specific compound glyphs live in PUA codepoints Verovio has never heard of, a zip alone is insufficient. The font must be committed to `fonts/Hildegard/` in a Verovio fork, its codepoints listed in `fonts/supported.xml`, and `fonts/generate.py` + `fonts/generate_all.sh` re-run to regenerate `smufl.h`.

**Recommended path**: fork as `verovio-hildegard` (precedent: DDMAL/verovio for Neon2). Maintain a minimal patchset against `rism-digital/verovio` `develop`. When stable, open an upstream PR to land the `neume.rhineland` notation mode.

### 3.5 Two-colour staff — use JS post-processor, not C++

Verovio emits staff lines as anonymous `<line>` children of a `<g class="staff">` group. There's no per-line class and MEI has no `<staffLine>` element. A C++ patch to emit `<line class="staff-line-c">` / `<line class="staff-line-f">` would be intrusive. Cheaper: wrap the Verovio SVG output in a ~30-line JS post-processor that assigns classes based on staff-line index (derived from the clef position) and applies CSS (`.staff-line-c { stroke: #F5D200 }`, `.staff-line-f { stroke: #C8232B }`).

### 3.6 MVP path — 6 steps, one weekend

1. Fork + baseline build (`git clone https://github.com/rism-digital/verovio && cmake && make`; verify `./verovio -f svg neumes-sample169.mei` renders).
2. Draw 5 glyphs (`hildegardPunctum`, `hildegardPesRotundus`, `hildegardClivis`, `hildegardTorculusRotundus`, `hildegardPorrectus`) at codepoints `U+F400–U+F404`.
3. Wire the font — copy `fonts/Bravura/` → `fonts/Hildegard/`, replace contents, edit `fonts/supported.xml`, re-run `generate.py`, rebuild.
4. Patch dispatch — extend `NeumeGroup`, add `@type` parsing, add Rhineland branch in `VisitNeume`.
5. Validate — render a two-syllable MEI with `<neume type="torculus_rotundus">` and `<neume type="pes_rotundus">`.
6. Two-colour staff — JS post-processor + CSS, no C++ change.

Full file-level changes in `verovio_integration_plan.md` § 3.

---

## 4. Source-code file paths to consult directly

The Verovio agent did not clone the repo; its line-number references are approximate. Before patching, clone `https://github.com/rism-digital/verovio` locally and `grep` for:

- `NeumeGroup` → `include/vrv/neume.h`
- `s_neumes` → `src/neume.cpp`
- `VisitNeume` → `src/calcligatureorneumeposfunctor.cpp`
- `m_drawingGlyphs` → `src/nc.cpp`
- `DrawNcGlyphs` → `src/view_neume.cpp`
- `NotationType` enum → `include/vrv/vrvdef.h`
- Font build pipeline → `fonts/generate.py`, `fonts/generate_all.sh`, `fonts/supported.xml`
- Reference font directory → `fonts/Bravura/` (model for `fonts/Hildegard/`)

Local reference material already in place at `../reference-repos/`:
- `music-encoding-develop/source/docs/06-neumes.xml` — MEI Neumes Module chapter, including the Tübingen/Hildegard origin note.
- `music-encoding-develop/source/examples/neumes/neumes-sample169.txt` — validated full MEI skeleton; basis for our test corpus.
- `music-encoding-develop/customizations/mei-neumes.xml` — ODD customization reference if any schema-level tweaks become necessary.
- `smufl-gh-pages/metadata/glyphnames.json`, `ranges.json`, `classes.json` — canonical SMuFL metadata. All `chantXxx` codepoints verified.

---

## 5. What changed in v0.5a

`glyph_inventory_v0.5.md` was edited in place to:

- Add a new **§ 0.1 — v0.5a corrections** block with the page-ref fixes, spelling note, and source-attestation downgrade table.
- Fix RN-006's paleographic source to `Gardiner p. 15, Fig. 1`.
- Fix RN-012's to `Gardiner p. 60 — O viridissima virga Ex. 9, Riesencodex f. 474v`.
- Fix RN-021 and RN-022's to `Gardiner p. 16` with explicit flagging of Gardiner's *respinus/respina* spelling.

The body table does not yet have per-row confidence corrections for every Humdrum-only entry; those should flow into a v0.6 revision after direct manuscript reading, not now.

---

## 6. Bottom line

The architecture decision stands exactly as `research_synthesis.md` §3 states: **dumb components font + Verovio-based smart renderer + MEI semantic encoding**. What changes in v2:

- We now have working URLs for both primary manuscripts. Direct reading is no longer a blocker — it's the next obvious step.
- Gardiner is less supportive of the v0.5 inventory than v0.5 claims. Humdrum is carrying more weight than we credited. The Humdrum-only entries (tractulus, torculus rotundus/quadratus, climacus resupinus, epiphonus) should be held pending direct manuscript verification.
- Verovio integration is not just "swap the font" — it requires a fork with a compound-glyph dispatch branch. Precedent exists (DDMAL/verovio for Neon). The minimum viable path is six steps and realistic as a weekend's work once 5 glyphs exist.
- The MEI Neumes Module was created for the Tübingen Hildegard project. This is the most serendipitous finding of the research: the semantic encoding standard is a purpose-built home for this repertoire.

Next: direct manuscript reading pass against Riesencodex f. 470r, f. 474v, and neighbouring folios, leading to v0.6 of the inventory.
