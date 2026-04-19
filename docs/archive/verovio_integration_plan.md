# Verovio Integration Plan — Hildegard Neume Font (SECONDARY consumer)

> **⚠️ Status: SECONDARY CONSUMER REFERENCE.** This plan was written before I discovered the primary consumer — the Rhena/Viriditas Rust project at `../hildegard`. The **primary integration path is now `rhena_integration_plan.md`**, which targets Rhena's own Rust-native render pipeline. Verovio is a *secondary* consumer — the OTF this font project ships can be installed in a Verovio fork for users who want chant-engraver rendering, but that is not where the architectural centre of gravity sits.
>
> What remains valid in this document:
> - The Verovio architecture analysis (atom-based dispatch, per-component glyph selection, fonts/Hildegard/ directory layout)
> - The MEI encoding profile for Verovio-consumed chant
> - The fork-and-patch MVP path for a future Verovio build
> - The SMuFL codepoint alignment, which the primary OTF already provides
>
> What is obsolete:
> - The framing that "Verovio is the smart renderer" — Rhena has its own.
> - The `notationtype="neume.rhineland"` MEI hook — not used by Rhena. Verovio fork work would still need it if a secondary Verovio path is ever pursued.
> - The MVP-path ordering — should go *after* the Rhena integration MVP, not before it.
>
> Keep this document for when/if a Verovio secondary-consumer path is pursued. Do not treat it as the authoritative integration plan.

---

Status: v1 (superseded as primary), 2026-04-14.
Scope: concrete file-level roadmap for integrating a Hildegard Rhineland neume font into a forked `rism-digital/verovio`, as a secondary consumer of the `hildegard-neumes.otf` produced by this font project.
Companion: `rhena_integration_plan.md` (primary), `research_synthesis.md`, `research_v2_findings.md` § 3.

---

## 1. What Verovio already does

Verovio (upstream `rism-digital/verovio`, active `develop` branch) has first-class support for MEI neume notation. Relevant source files:

| File | Role |
| --- | --- |
| `include/vrv/neume.h` | `Neume` element; `NeumeGroup` enum (15 values); `s_neumes` contour map declaration |
| `src/neume.cpp` | `Neume::GetNeumeGroup()` classifier; `s_neumes` static map |
| `src/nc.cpp` | `Nc` (neume component) element; `m_drawingGlyphs` vector holds resolved SMuFL codepoints |
| `src/calcligatureorneumeposfunctor.cpp` | `VisitNeume` / `VisitNc` — where `m_drawingGlyphs` is actually populated at layout time |
| `src/view_neume.cpp` | SVG drawing pass; `DrawNcGlyphs` renders whatever `m_drawingGlyphs` contains |
| `src/adjustneumexfunctor.cpp` | Horizontal spacing adjustment for neume groups |
| `src/syllable.cpp`, `src/liquescent.cpp`, `src/oriscus.cpp`, `src/quilisma.cpp`, `src/plica.cpp` | Modeled MEI child elements |
| `include/vrv/vrvdef.h` | `NotationType` enum (including existing `NOTATIONTYPE_neume`) |
| `include/vrv/smufl.h` | Auto-generated codepoint constants (e.g. `SMUFL_E990_chantPunctum`) |
| `fonts/supported.xml` | Registry of active glyph codepoints per font |
| `fonts/generate.py`, `fonts/generate_all.sh` | Font build pipeline (regenerates `smufl.h`) |
| `fonts/Bravura/` | Reference font directory layout (SVG glyphs + generated bbox XML) |

Neume mode is activated by `notationtype="neume"` on `<staffDef>`. There is no `--neume` CLI flag.

**Current dispatch model is atom-based.** `VisitNeume` walks each `<nc>` and assigns atomic SMuFL codepoints *per component*:

- `hasLiquescent` → `SMUFL_E995_chantAuctumDesc` / `SMUFL_E994_chantAuctumAsc`
- `hasOriscus` → `SMUFL_EA2A_medRenOriscusCMN`
- `hasQuilisma` → `SMUFL_E99B_chantQuilisma`
- default `SMUFL_E990_chantPunctum`, reassigned on `@ligated` / pitch difference to `chantLigaturaDesc2nd` etc., or on `@tilt` to `chantPunctumInclinatum`

A pes is rendered as *two independent punctum glyphs*, not a single pes glyph. The `NeumeGroup` enum is used for *spacing*, not for glyph selection.

## 2. What Hildegard needs that Verovio does not have

Three deltas:

### 2.1 Compound-glyph dispatch

Rhineland neumes are single pen-gesture shapes (pes rotundus, torculus, porrectus) drawn as one glyph, not atom chains. We need a new dispatch path in `VisitNeume` that, when `notationtype="neume.rhineland"` is active, writes a single compound codepoint to the first `nc`'s `m_drawingGlyphs` and leaves subsequent `nc`s empty (or invisible).

### 2.2 Expanded classification vocabulary

Verovio's `NeumeGroup` enum has 15 values: `PUNCTUM, CLIVIS, PES, PRESSUS, CLIMACUS, PORRECTUS, SCANDICUS, TORCULUS, SCANDICUS_FLEXUS, PORRECTUS_FLEXUS, TORCULUS_RESUPINUS, CLIMACUS_RESUPINUS, PES_SUBPUNCTIS, PORRECTUS_SUBPUNCTIS, SCANDICUS_SUBPUNCTIS`. Our inventory has 35 families, including torculus rotundus vs quadratus (identical contours, different head shapes), Hildegard-idiosyncratic compounds (RN-021/022), and pressus family variants.

The cleanest way to extend classification without breaking the existing contour-lookup path: read MEI's `<neume @type>` attribute as a hint inside `GetNeumeGroup()`. `@type` is a free-form string available on every MEI element via `att.typed` — no schema extension required.

### 2.3 Two-colour staff

Rhineland manuscripts use a 4-line staff with **yellow C-line** and **red F-line**. Verovio emits staff lines as anonymous `<line>` children of `<g class="staff">`; MEI has no `<staffLine>` element. C++ patching is intrusive; a JS SVG post-processor is cheaper (§ 3.D).

---

## 3. Concrete file-level changes

### A. Register glyphs — **required**

Choose between in-tree and out-of-tree distribution:

**In-tree (recommended)**: create `fonts/Hildegard/` directory in the fork, modeled on `fonts/Bravura/`. Place SVG path files for each glyph named by SMuFL name (e.g., `hildegardPunctum.svg`). Add codepoint registrations to `fonts/supported.xml`:

```xml
<glyph glyph-code="F400" smufl-name="hildegardDotPunctum"/>
<glyph glyph-code="F401" smufl-name="hildegardTractulus"/>
<glyph glyph-code="F420" smufl-name="hildegardPes"/>
<glyph glyph-code="F421" smufl-name="hildegardPesFlexus"/>
<glyph glyph-code="F422" smufl-name="hildegardFlexa"/>
<glyph glyph-code="F423" smufl-name="hildegardFlexaResupina"/>
<glyph glyph-code="F440" smufl-name="hildegardTorculusRotundus"/>
<glyph glyph-code="F441" smufl-name="hildegardTorculusQuadratus"/>
<glyph glyph-code="F443" smufl-name="hildegardPorrectus"/>
<glyph glyph-code="F460" smufl-name="hildegardCephalicus"/>
<glyph glyph-code="F4A0" smufl-name="hildegardFlexaResupinaPressusSubbipunctis"/>
<glyph glyph-code="F4A1" smufl-name="hildegardFlexaResupinaPressusLiquescens"/>
<!-- … etc. -->
```

Then run:

```bash
python fonts/generate.py extract Hildegard
bash fonts/generate_all.sh
```

This regenerates `include/vrv/smufl.h` with new constants like `SMUFL_F400_hildegardDotPunctum`, `SMUFL_F420_hildegardPes`, etc. These constants are then available to the C++ dispatch code.

**Out-of-tree (insufficient for Rhineland)**: `--font-add-custom Hildegard.zip` swaps glyph paths for existing codepoints only. **Cannot register new codepoints** in `smufl.h` at runtime. Rejected for this project because our PUA block (`U+F400+`) contains codepoints Verovio has never heard of.

### B. Extend classification — **required**

**`include/vrv/neume.h`** — append to `NeumeGroup` enum (approximate lines 32–47 per research agent; verify locally):

```cpp
enum NeumeGroup {
    // ... existing 15 values ...
    PUNCTUM, CLIVIS, PES, PRESSUS, CLIMACUS, PORRECTUS, SCANDICUS, TORCULUS,
    SCANDICUS_FLEXUS, PORRECTUS_FLEXUS, TORCULUS_RESUPINUS, CLIMACUS_RESUPINUS,
    PES_SUBPUNCTIS, PORRECTUS_SUBPUNCTIS, SCANDICUS_SUBPUNCTIS,
    // New Hildegard Rhineland values:
    PES_RHINELAND,
    FLEXA_RHINELAND,
    PES_FLEXUS_RHINELAND,
    FLEXA_RESUPINA_RHINELAND,
    TORCULUS_ROTUNDUS_RHINELAND,
    TORCULUS_QUADRATUS_RHINELAND,
    TORCULUS_RESUPINUS_RHINELAND,
    PORRECTUS_RHINELAND,
    PORRECTUS_FLEXUS_RHINELAND,
    CLIMACUS_RESUPINUS_RHINELAND,
    CEPHALICUS_RHINELAND,
    EPIPHONUS_RHINELAND,
    PES_LIQUESCENS_RHINELAND,
    PES_FLEXUS_LIQUESCENS_RHINELAND,
    PES_SUBPUNCTIS_RHINELAND,
    PRESSUS_RHINELAND,
    PRESSUS_LIQUESCENS_RHINELAND,
    PRESSUS_SUBPUNCTIS_RHINELAND,
    QUILISMA_RHINELAND,
    QUILISMA_PREPUNCTO_RHINELAND,
    FLEXA_RESUPINA_PRESSUS_SUBBIPUNCTIS_RHINELAND,
    FLEXA_RESUPINA_PRESSUS_LIQUESCENS_RHINELAND,
};
```

**`src/neume.cpp`** — extend `GetNeumeGroup()` to honour `@type`:

```cpp
NeumeGroup Neume::GetNeumeGroup()
{
    // New: if @type is a Hildegard Rhineland vocabulary string, return the mapped enum.
    const std::string &neumeType = this->GetType();  // from att.typed
    if (!neumeType.empty()) {
        static const std::map<std::string, NeumeGroup> rhinelandTypes = {
            {"pes_rhineland", PES_RHINELAND},
            {"flexa_rhineland", FLEXA_RHINELAND},
            {"pes_flexus_rhineland", PES_FLEXUS_RHINELAND},
            {"flexa_resupina_rhineland", FLEXA_RESUPINA_RHINELAND},
            {"torculus_rotundus", TORCULUS_ROTUNDUS_RHINELAND},
            {"torculus_quadratus", TORCULUS_QUADRATUS_RHINELAND},
            {"torculus_resupinus_rhineland", TORCULUS_RESUPINUS_RHINELAND},
            {"porrectus_rhineland", PORRECTUS_RHINELAND},
            {"porrectus_flexus_rhineland", PORRECTUS_FLEXUS_RHINELAND},
            {"climacus_resupinus_rhineland", CLIMACUS_RESUPINUS_RHINELAND},
            {"cephalicus", CEPHALICUS_RHINELAND},
            {"epiphonus", EPIPHONUS_RHINELAND},
            {"pes_liquescens", PES_LIQUESCENS_RHINELAND},
            {"pes_flexus_liquescens", PES_FLEXUS_LIQUESCENS_RHINELAND},
            {"pes_subpunctis", PES_SUBPUNCTIS_RHINELAND},
            {"pressus_rhineland", PRESSUS_RHINELAND},
            {"pressus_liquescens", PRESSUS_LIQUESCENS_RHINELAND},
            {"pressus_subpunctis", PRESSUS_SUBPUNCTIS_RHINELAND},
            {"quilisma_rhineland", QUILISMA_RHINELAND},
            {"quilisma_prepuncto", QUILISMA_PREPUNCTO_RHINELAND},
            {"flexa_resupina_pressus_subbipunctis", FLEXA_RESUPINA_PRESSUS_SUBBIPUNCTIS_RHINELAND},
            {"flexa_resupina_pressus_liquescens", FLEXA_RESUPINA_PRESSUS_LIQUESCENS_RHINELAND},
        };
        auto it = rhinelandTypes.find(neumeType);
        if (it != rhinelandTypes.end()) return it->second;
    }

    // Existing contour-lookup path unchanged below…
}
```

Design note on `@type` vocabulary: generic families (`torculus_rotundus`, `cephalicus`) don't need a `_rhineland` suffix because they're only meaningful in neume notation anyway. Ambiguous ones (`pes`, `flexa`) that could conflict with square notation do. This keeps MEI documents clean while avoiding collision with existing Verovio behaviour.

### C. Dispatch glyph codepoints — **required (the real work)**

**`src/calcligatureorneumeposfunctor.cpp`** — in `VisitNeume`, add a Rhineland branch near the top:

```cpp
FunctorCode CalcLigatureOrNeumePosFunctor::VisitNeume(Neume *neume)
{
    // New: if the active notation type is Rhineland and the neume group is a Rhineland family,
    // write a single compound codepoint to the first nc and zero the rest.
    if (neume->GetNotationType() == NOTATIONTYPE_neume_rhineland) {
        NeumeGroup group = neume->GetNeumeGroup();
        wchar_t compoundGlyph = 0;
        switch (group) {
            case PES_RHINELAND:                               compoundGlyph = SMUFL_F420_hildegardPes; break;
            case PES_FLEXUS_RHINELAND:                        compoundGlyph = SMUFL_F421_hildegardPesFlexus; break;
            case FLEXA_RHINELAND:                             compoundGlyph = SMUFL_F422_hildegardFlexa; break;
            case FLEXA_RESUPINA_RHINELAND:                    compoundGlyph = SMUFL_F423_hildegardFlexaResupina; break;
            case TORCULUS_ROTUNDUS_RHINELAND:                 compoundGlyph = SMUFL_F440_hildegardTorculusRotundus; break;
            case TORCULUS_QUADRATUS_RHINELAND:                compoundGlyph = SMUFL_F441_hildegardTorculusQuadratus; break;
            case TORCULUS_RESUPINUS_RHINELAND:                compoundGlyph = SMUFL_F442_hildegardTorculusResupinus; break;
            case PORRECTUS_RHINELAND:                         compoundGlyph = SMUFL_F443_hildegardPorrectus; break;
            case PORRECTUS_FLEXUS_RHINELAND:                  compoundGlyph = SMUFL_F444_hildegardPorrectusFlexus; break;
            case CEPHALICUS_RHINELAND:                        compoundGlyph = SMUFL_F460_hildegardCephalicus; break;
            case EPIPHONUS_RHINELAND:                         compoundGlyph = SMUFL_F461_hildegardEpiphonus; break;
            case PES_LIQUESCENS_RHINELAND:                    compoundGlyph = SMUFL_F462_hildegardPesLiquescens; break;
            case PES_FLEXUS_LIQUESCENS_RHINELAND:             compoundGlyph = SMUFL_F463_hildegardPesFlexusLiquescens; break;
            case PES_SUBPUNCTIS_RHINELAND:                    compoundGlyph = SMUFL_F464_hildegardPesSubpunctis; break;
            case PRESSUS_RHINELAND:                           compoundGlyph = SMUFL_F480_hildegardPressus; break;
            case PRESSUS_LIQUESCENS_RHINELAND:                compoundGlyph = SMUFL_F481_hildegardPressusLiquescens; break;
            case PRESSUS_SUBPUNCTIS_RHINELAND:                compoundGlyph = SMUFL_F482_hildegardPressusSubpunctis; break;
            case FLEXA_RESUPINA_PRESSUS_SUBBIPUNCTIS_RHINELAND: compoundGlyph = SMUFL_F4A0_hildegardFlexaResupinaPressusSubbipunctis; break;
            case FLEXA_RESUPINA_PRESSUS_LIQUESCENS_RHINELAND: compoundGlyph = SMUFL_F4A1_hildegardFlexaResupinaPressusLiquescens; break;
            default: break;  // not a Rhineland compound — fall through to atom dispatch
        }
        if (compoundGlyph != 0) {
            // Assign the single compound glyph to the first Nc; empty the rest.
            auto ncList = neume->FindAllDescendantsByType(NC);
            bool isFirst = true;
            for (auto *obj : ncList) {
                Nc *nc = dynamic_cast<Nc *>(obj);
                nc->m_drawingGlyphs.clear();
                if (isFirst) {
                    nc->m_drawingGlyphs.push_back(compoundGlyph);
                    isFirst = false;
                }
            }
            return FUNCTOR_CONTINUE;
        }
    }

    // Fall through to existing square-notation atom dispatch …
}
```

**`include/vrv/vrvdef.h`** — add to `NotationType` enum:

```cpp
enum NotationType {
    NOTATIONTYPE_NONE = 0,
    NOTATIONTYPE_cmn,
    NOTATIONTYPE_mensural,
    // … existing values …
    NOTATIONTYPE_neume,
    NOTATIONTYPE_neume_rhineland,  // NEW
};
```

**`libmei/atts_shared.cpp`** — this is generated code. `AttTyped::StrToNotationtype` needs to accept `"neume.rhineland"` (dot-delimited subtype per MEI convention). Best path: regenerate libmei from the MEI ODD with a customization file that adds `neume.rhineland` to the `data.NOTATIONTYPE` enumeration. Alternative: patch the generated code directly (simpler short-term, lost on next regen).

### D. Two-colour staff — **JS post-processor, not C++**

Do not patch `src/view_page.cpp` `DrawStaffLines` in v1. Instead, wrap the Verovio SVG output in a small JS post-processor:

```javascript
// hildegard-staff-color.js
function colorRhinelandStaff(svgElement) {
  const staffs = svgElement.querySelectorAll('g.staff');
  for (const staff of staffs) {
    const lines = staff.querySelectorAll('line, path.staff-line');
    // 4-line Hildegard staff with movable C-clef. Assume clef already positioned.
    // Determine which line is C (yellow) and which is F (red) by reading <clef> position.
    // For now, hardcode the Riesencodex convention: C=line 3, F=line 1.
    lines[0]?.classList.add('hildegard-staff-line-f');  // bottom
    lines[2]?.classList.add('hildegard-staff-line-c');  // third from bottom
  }
}
```

Paired with CSS:

```css
.hildegard-staff-line-c { stroke: #F5D200; }  /* yellow */
.hildegard-staff-line-f { stroke: #C8232B; }  /* red */
```

Defer any C++ staff-line colouring work to post-v1. If the project grows into a full upstream contribution, that's where a proper MEI `<staffLine @color>` extension would live.

### E. `adjustneumexfunctor.cpp` spacing

Hildegard compound glyphs have different advance widths than atom chains. After landing A–C, rendered output will likely show spacing anomalies between compound neumes and their neighbours. Fix by extending `AdjustNeumeXFunctor::VisitNeume` with Rhineland-aware advance-width lookup from the font's bbox XML. Defer until visible; not blocking for the MVP.

---

## 4. MEI encoding profile

No schema extension required. The "Hildegard profile" is a documented vocabulary of `@type` strings on `<neume>`. Minimum viable MEI document (adapted from `music-encoding-develop/source/examples/neumes/neumes-sample169.txt`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mei xmlns="http://www.music-encoding.org/ns/mei" meiversion="5.0">
  <meiHead>
    <fileDesc>
      <titleStmt><title>Hildegard test</title></titleStmt>
      <pubStmt/>
    </fileDesc>
  </meiHead>
  <music>
    <body>
      <mdiv>
        <score>
          <scoreDef>
            <staffGrp>
              <staffDef n="1" lines="4" notationtype="neume.rhineland">
                <clef shape="C" line="3"/>
              </staffDef>
            </staffGrp>
          </scoreDef>
          <section>
            <staff n="1">
              <layer>
                <syllable>
                  <syl>O</syl>
                  <neume type="torculus_rotundus">
                    <nc pname="e" oct="3"/>
                    <nc pname="f" oct="3"/>
                    <nc pname="e" oct="3"/>
                  </neume>
                </syllable>
              </layer>
            </staff>
          </section>
        </score>
      </mdiv>
    </body>
  </music>
</mei>
```

The key switch is `notationtype="neume.rhineland"` on `<staffDef>`. This activates the new dispatch branch. For backward compatibility with upstream Verovio (which won't recognize `neume.rhineland`), users can fall back to `notationtype="neume"` and accept square-note rendering.

Encoding examples for every v0.5 family: `examples/mei_encoding_reference.md`.

---

## 5. Recommended distribution strategy

**Primary: fork as `verovio-hildegard`.**

- Base: `rism-digital/verovio` `develop` branch.
- Patchset lives on a `hildegard` branch; rebase monthly against upstream.
- Ship as:
  - WASM npm package (mirror upstream's `emscripten/npm-dev`) — `verovio-hildegard-js`.
  - Python wheel via `bindings/python` — `verovio-hildegard-python`.
  - Native CLI build for server-side rendering.
- Font ships inside `fonts/Hildegard/` — no zip packaging needed.

**Secondary: upstream the notation mode.**

After the prototype stabilizes and the patch minimizes, open an upstream PR adding `NOTATIONTYPE_neume_rhineland`, the Rhineland `NeumeGroup` values, and the dispatch branch. Justify with a test corpus of 3–5 MEI documents + expected SVG snapshots. The Verovio team has historically been receptive to historical notations (mensural + square neumes are already upstream). Expect a multi-month review cycle.

**Rejected: post-process Verovio SVG output.**

This works only if we accept square-note atoms from Verovio and repaint them. For Rhineland we cannot rewrite atomic punctum glyphs into compound pes rotundus forms in SVG post-processing — we'd be re-implementing layout in JS. The SVG post-processor approach is used only for the two-colour staff (§ 3.D), not for glyph substitution.

---

## 6. MVP path — 6 steps

1. **Fork + baseline build.**
   ```bash
   git clone https://github.com/rism-digital/verovio
   cd verovio && mkdir build && cd build
   cmake -DBUILD_AS_LIBRARY=OFF ../tools
   make -j
   ./verovio -f svg ../doc/examples/neumes-sample169.mei
   ```
   Confirm a square-note neume sample renders. This proves toolchain readiness.

2. **Draw 5 glyphs** (per `glyph_priority_sheet.md` Tier 1 subset):
   - `hildegardPunctum` (U+E990 — reuse codepoint, draw Rhineland register)
   - `hildegardPesRotundus` (U+F420)
   - `hildegardClivis` (U+F422)
   - `hildegardTorculusRotundus` (U+F440)
   - `hildegardPorrectus` (U+F443)

   SVG paths, em = 2048. Trace from Riesencodex f. 470r (pageview 450574). Reference Gardiner Fig. 6 labels: these are the five families the basic-neume plate exhibits, minus virga, climacus, scandicus (which are assembly-only or deferred in Tier 1).

3. **Wire the font.**
   ```bash
   cp -r fonts/Bravura fonts/Hildegard
   # Replace SVGs in fonts/Hildegard/ with your traced glyphs.
   # Edit fonts/supported.xml to register the new codepoints.
   python fonts/generate.py extract Hildegard
   bash fonts/generate_all.sh
   cd build && make -j
   ```
   Confirm `include/vrv/smufl.h` now contains `SMUFL_F420_hildegardPesRotundus` (etc.) and `./verovio --font Hildegard` loads without error.

4. **Patch dispatch.** Apply the `NeumeGroup` extension (§ 3.B), the `GetNeumeGroup()` `@type` parser (§ 3.B), and the `VisitNeume` Rhineland branch (§ 3.C). Add `NOTATIONTYPE_neume_rhineland` to `vrvdef.h`. Patch `libmei/atts_shared.cpp` directly to accept `"neume.rhineland"` as a notation type string (regenerate from ODD post-MVP).

5. **Validate.** Render a two-syllable MEI file with:
   ```xml
   <neume type="torculus_rotundus"><nc pname="e"/><nc pname="f"/><nc pname="e"/></neume>
   ```
   Inspect the SVG. Confirm the single `SMUFL_F440_hildegardTorculusRotundus` glyph is emitted at the correct staff position, not a chain of punctum glyphs.

6. **Two-colour staff.** Add `hildegard-staff-color.js` + CSS (§ 3.D). Wrap the Verovio SVG output and confirm yellow C-line + red F-line render in a browser.

Deliverable after step 6: a single HTML page that loads the WASM build of `verovio-hildegard`, parses a small MEI file, and renders five Rhineland neume families on a yellow/red 4-line staff. That's the smallest artifact that proves the whole pipeline.

---

## 7. Uncertainties and verify-locally flags

The research that informed this plan was web-based; line-number references above are approximate. Before patching, clone the repo and verify:

- Exact location of `NeumeGroup` in `include/vrv/neume.h`
- Exact location of `s_neumes` in `src/neume.cpp`
- Exact location of `VisitNeume` in `src/calcligatureorneumeposfunctor.cpp`
- Whether `AttTyped::StrToNotationtype` is in `libmei/atts_shared.cpp` or a different generated file
- Current state of `fonts/README.md` and exact `generate.py` invocation — read it once locally; it's the canonical spec for adding fonts to Verovio.
- DDMAL/verovio fork commit history vs upstream `develop` — if DDMAL has useful editor hooks we want (for future Neon-style editing), base our fork on theirs.

---

## 8. Bottom line

The plan is: **fork upstream Verovio, add a Rhineland notation type, add a compound-glyph dispatch branch, ship the font in `fonts/Hildegard/`, post-process the SVG in JS for staff colours.** Six steps to an MVP once five glyphs exist. The MEI schema is already a home for this repertoire — it was built for the Tübingen Hildegard project and doesn't need extension. Upstreaming is a reachable long-term goal, not a short-term blocker.
