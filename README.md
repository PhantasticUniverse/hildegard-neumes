# Hildegard Neumes

An OpenType font for the Rhineland neume notation used in Hildegard von Bingen's music manuscripts — **Dendermonde Cod. 9** (c. 1174/75) and **Wiesbaden Riesencodex Hs. 2** (c. 1180–85). Built to replace the abandoned experimental inline-Rust glyph attempt in the Rhena/Viriditas notation platform with a real, iterable, universally consumable font asset.

## Why this project exists

The **Rhena/Viriditas** project at `/Users/xaviermac/Documents/2_Areas/Coding-Projects/hildegard` is a compiler-first, Hildegard-first notation platform. It parses a custom Rhena DSL into a witness-aware semantic IR, projects to a Render IR, and renders diplomatic (Rhineland) and normalized (square) output. ADR-0004 fixes the dual-glyph strategy: **Rhineland for diplomatic mode, SMuFL/Bravura for normalized mode.**

Rhena already ships Bravura paths for square notation. Its Rhineland path is an experimental attempt that was abandoned: 19 hand-typed SVG path strings in `crates/rhena-core/src/render_ir/glyphs/rhineland.rs`, baked into Rust source, with crude geometric approximations of calligraphic forms. The approach was abandoned for three kinds of reasons — aesthetic (the shapes are placeholders), structural (glyph design baked into code, no font-editor workflow, no external consumability), and doctrinal (violates constitution Rule 7: *"Do not make the project depend on one renderer forever"*).

**This font project replaces that attempt**, with a real OpenType font authored in real font tooling, delivered to Rhena via a compile-time codegen step that preserves the existing `Glyph { name, path, width }` API.

## Architecture in one paragraph

The font is authored in FontForge (or equivalent) and exported as `hildegard-neumes.otf`. A small Python script reads the `.otf`, extracts SVG path data and advance widths, and emits `rhineland_glyphs.rs` matching Rhena's existing `Glyph` struct. That generated file is committed into Rhena at `crates/rhena-core/src/render_ir/glyphs/rhineland.rs` with an `@generated` header. Rhena's resolver (`glyphs/mod.rs`), SVG backend, and 133 existing tests stay unchanged. Iteration loop: open font editor → redraw a glyph → export `.otf` → `python scripts/generate-rhena-glyphs.py` → copy to Rhena → `just check`. The OTF is also a universally consumable artifact: Verovio, Illustrator, Word, LilyPond, web `@font-face`, and any future Rust consumer can use it directly. SMuFL codepoint alignment is preserved so external chant tooling gets interop for free.

## State of the project

- **Architecture decision** (`rhena_integration_plan.md`) — **PRIMARY**. Real OTF + codegen into Rhena. The abandoned inline-Rust attempt is the thing to replace.
- **Inventory (v0.5b)** (`glyph_inventory_v0.5.md`) — 35 paleographic neume families; § 0.2 maps them to Rhena's 19 atomic glyph set. Gardiner page refs corrected per deep-read. Humdrum-only caveats flagged.
- **Glyph priority sheet** (`glyph_priority_sheet.md`) — 3-tier drawing roadmap for Rhena's 19 atoms.
- **Paleographic drawing briefs** (`docs/paleographic_drawing_briefs.md`) — per-atom authoring guidance: pen angle, stroke register, key features, what NOT to draw.
- **SMuFL codepoint mapping** (`smufl_codepoint_mapping.md`) — for the OTF's external-consumer interface. Rhena itself keys off glyph *name strings*, not codepoints.
- **ADRs 0001–0008** (`docs/adr/`) — architecture decision records: UFO3 source, Python+fontTools codegen, contract ownership (Proposed), determinism strategy, width-freeze scope, OFL licence, OTF/CFF outlines, paleographic fidelity policy.
- **Rhena coordination** (`docs/rhena-coordination/`) — materials staged for Rhena adoption: `ADR-0009-generated-rhineland-glyphs.md` (draft Rhena-side ADR) and `rhineland.contract.json` (draft single-source-of-truth contract with post-review widths).
- **Planning + reviews** (`docs/planning/`) — `claude-review-2026-04-14.md` (round 1), `claude-review-2-2026-04-14.md` (round 2), `width-review-2026-04-14.md` (per-glyph bbox vs advance analysis), and disposition docs.
- **Research synthesis, pass 1** (`research_synthesis.md`) — architectural rationale, gregorio/SMuFL/MEI/OpenType analysis.
- **Research findings, pass 2** (`research_v2_findings.md`) — manuscript URLs, Gardiner corrections, MEI-Tübingen origin note, Verovio architecture details.
- **Metadata sidecar stub** (`hildegard_metadata.json`) — SMuFL-compatible metadata for external consumers.
- **Neume chart** — `Hildegard_of_Bingen_Symphonia_Neume_Transcription_Chart.jpg` (Beverly Lomer / ISHvBS, reproduced in Gardiner 2022 as Fig. 4).
- **Archived** (`docs/archive/`) — superseded docs retained for history: `verovio_integration_plan.md` (secondary-consumer reference, not the primary path), `mei_encoding_reference.md`, `glyph_priority_sheet_v0.5.md`, and `glyph_inventory.md` (v0.4, superseded by `glyph_inventory_v0.5.md` at the project root).

## Start here (for contributors drawing glyphs)

If you're opening this project to author the first glyphs, read in order:

1. `glyph_priority_sheet.md` — decides *which* 6 glyphs to draw first (Tier 1 MVP: `rh_punctum`, `rh_virga`, `rh_c_clef`, `rh_punctum_inclinatum`, `rh_quilisma`, `rh_pressus`).
2. `docs/paleographic_drawing_briefs.md` — per-atom drawing guidance distilled from manuscript study.
3. `docs/planning/width-review-2026-04-14.md` — the advance-width analysis; three widths were corrected (`rh_virga` 65→90, `rh_liquescent_asc` / `desc` 140→160) and live in `src/widths.json`.
4. `rhena_integration_plan.md` — the full build pipeline and Rhena integration architecture.
5. Manuscript reference images in the sibling Rhena project at `/Users/xaviermac/Documents/2_Areas/Coding-Projects/hildegard/docs/research/images/` — direct traces from Dendermonde fol. 168v.

Then: open `src/hildegard-neumes.ufo/` in FontForge (or any UFO3-aware editor). The scaffold is already in place — every glyph is a placeholder rectangle at its target advance width with the correct SMuFL codepoint. Double-click a glyph to enter the outline editor and redraw. If you ever need to regenerate the scaffold from scratch (e.g. after a contract change), run `just rescaffold-ufo`.

## Primary manuscript sources

Both fully digitized and openly accessible:

- **Riesencodex (Wiesbaden, HLB RheinMain, Hs. 2)** — CC-BY 4.0, full PDF at `https://hlbrm.digitale-sammlungen.hebis.de/download/pdf/449618.pdf`.
  - f. 470r (Gardiner Fig. 6 basic-neume plate): pageview `450574`
  - f. 474v (*O viridissima virga*, cephalicus / pressus liquescens contrast): pageview `450583`
  - Landing page: `https://hlbrm.digitale-sammlungen.hebis.de/handschriften-hlbrm/content/titleinfo/449618`
- **Dendermonde Cod. 9** — public domain, IMSLP facsimile: `https://imslp.org/wiki/Dendermonde_Codex_(Hildegard)`.
- **Cantus Database**: source `588308` (Riesencodex), `588309` (Dendermonde).

Rhena's existing research captures are at `hildegard/docs/research/images/` — `punctum.png`, `virda.png`, `flexa.png`, `climacus.png`, `quilisma.png`, `pressus.png`, `c_clef.png`, `o_ecclesia_rhineland_line_01.png`, `o_ecclesia_rhineland_line_02.png`, and the modern-transcription overlays. Start there for the initial trace pass.

## Stable API contract with Rhena

The font must emit a `rhineland_glyphs.rs` file preserving this exact shape (all constants, names, widths) so Rhena's resolver in `crates/rhena-core/src/render_ir/glyphs/mod.rs` can consume it without changes:

```
rh_punctum              width 240
rh_virga                width 90    (post-review; was 65)
rh_punctum_inclinatum   width 120
rh_quilisma             width 170
rh_oriscus              width 200
rh_strophicus           width 160
rh_pressus              width 300
rh_liquescent_asc       width 160   (post-review; was 140)
rh_liquescent_desc      width 160   (post-review; was 140)
rh_deminutum            width 100
rh_c_clef               width 110
rh_f_clef               width 160
rh_divisio_minima       width 16
rh_divisio_maior        width 16
rh_divisio_maxima       width 16
rh_divisio_finalis      width 56
rh_virgula              width 12
rh_pes_line             width 12
rh_flexa_line           width 172
```

19 glyphs. Em = 1000, Y-up, Bravura convention. Three widths were corrected by the 2026-04-14 width review; the rest are frozen at v1 pending a v2 ADR. Details in `docs/planning/width-review-2026-04-14.md` and `rhena_integration_plan.md` § 3.

## Document map

```
hildegard-neumes/
├── README.md                                      ← you are here
├── rhena_integration_plan.md                      (PRIMARY — architecture + build pipeline)
├── glyph_inventory_v0.5.md                        (v0.5b — paleographic inventory; § 0.2 Rhena alignment)
├── glyph_priority_sheet.md                        (drawing tiers — 19 Rhena atoms)
├── research_synthesis.md                          (pass 1: gregorio, SMuFL, MEI, OT tech)
├── research_v2_findings.md                        (pass 2: manuscripts, Gardiner deep-read, Verovio)
├── smufl_codepoint_mapping.md                     (OTF codepoint plan for external consumers)
├── hildegard_metadata.json                        (SMuFL metadata sidecar stub)
├── OFL.txt                                        (SIL Open Font License 1.1)
├── FONTLOG.txt                                    (SIL-standard changelog)
├── VERSION                                        (font version string)
├── pyproject.toml                                 (dev deps: fontTools, pytest)
├── justfile                                       (task runner — build, generate, test, check)
├── .gitignore
├── Hildegard_of_Bingen_Symphonia_Neume_Transcription_Chart.jpg  (Lomer/ISHvBS chart)
├── src/
│   ├── glyph-names.json                           (names + SMuFL + rust_const; contract fragment)
│   ├── widths.json                                (advance widths contract fragment)
│   └── hildegard-neumes.ufo/                      (UFO3 source — Phase A placeholder rectangles)
├── scripts/
│   ├── scaffold-ufo.py                            (contract → src/hildegard-neumes.ufo/)
│   ├── build-font.sh                              (headless FontForge → OTF + WOFF2)
│   ├── generate-rhena-glyphs.py                   (OTF → generated rhineland_glyphs.rs)
│   └── validate-font.py                           (post-build bbox-vs-advance sanity checks)
├── tests/                                         (pytest suite per ADR-0002)
│   ├── conftest.py                                (session fixtures: minimal_ttf, minimal_otf)
│   ├── _gen_import.py                             (importlib helper for the hyphenated script)
│   ├── fixtures/
│   │   ├── make_minimal_ttf.py                    (synthesizes quadratic TTF placeholder)
│   │   └── make_minimal_otf.py                    (synthesizes cubic CFF placeholder)
│   ├── test_contract_validation.py
│   ├── test_path_normalization.py
│   ├── test_width_assertion.py
│   ├── test_determinism.py                        (parametrized over ttf/otf)
│   ├── test_golden_output.py                      (parametrized over ttf/otf)
│   ├── test_scaffold.py                           (Phase A UFO3 scaffolding + round-trip)
│   └── test_rhena_smoke.py                        (optional — skipped without RHENA_PATH; copies, never mutates)
├── .github/workflows/                             (6 CI jobs per ADR-0004)
│   ├── lint-docs.yml
│   ├── validate-contract.yml
│   ├── build-font.yml
│   ├── codegen.yml                                (matrix over ttf/otf)
│   ├── reproducibility.yml                        (matrix over ttf/otf; byte-identity gate)
│   └── smoke-rhena.yml                            (workflow_dispatch only; compile-level gate)
├── build/                                         (gitignored — OTF/WOFF2 artifacts, _check/ scratch)
├── generated/                                     (gitignored — rhineland_glyphs.rs output)
└── docs/
    ├── adr/                                       (8 ADRs — infrastructure decisions)
    │   ├── README.md                              (ADR index)
    │   ├── ADR-0001-source-format.md              (UFO3 not SFD)
    │   ├── ADR-0002-codegen-toolchain.md          (Python + fontTools)
    │   ├── ADR-0003-contract-ownership.md         (Rhena owns contract, Proposed)
    │   ├── ADR-0004-determinism.md                (5 determinism mitigations)
    │   ├── ADR-0005-width-freeze-scope.md         (post-review widths in place)
    │   ├── ADR-0006-license.md                    (OFL-1.1 with RFN)
    │   ├── ADR-0007-otf-cff-outlines.md
    │   └── ADR-0008-paleographic-fidelity-policy.md
    ├── paleographic_drawing_briefs.md             (per-glyph drawing briefs for all 19 atoms)
    ├── planning/
    │   ├── claude-review-2026-04-14.md            (round-1 review)
    │   ├── response-to-claude-review-2026-04-14.md
    │   ├── claude-review-2-2026-04-14.md          (round-2 review)
    │   └── width-review-2026-04-14.md             (per-glyph bbox-vs-advance analysis; 3 bugs flagged)
    ├── rhena-coordination/                        (materials staged for Rhena adoption)
    │   ├── README.md
    │   ├── ADR-0009-generated-rhineland-glyphs.md (draft Rhena ADR)
    │   └── rhineland.contract.json                (draft contract file with post-review widths)
    └── archive/                                   (superseded / secondary-consumer docs)
        ├── glyph_inventory.md                     (v0.4, superseded by v0.5b)
        ├── glyph_priority_sheet_v0.5.md
        ├── mei_encoding_reference.md
        └── verovio_integration_plan.md
```

## v1 status snapshot

**Done**:
- Source format fixed to UFO3 (ADR-0001).
- **Phase A UFO3 scaffold landed (2026-04-19)**: `src/hildegard-neumes.ufo/` now contains `.notdef` + the 19 Rhineland atoms with placeholder rectangle outlines at their post-review advance widths, SMuFL codepoints in the cmap, `public.glyphOrder` pinned so the OTF glyph order matches `ALL_GLYPHS`. Produced by `scripts/scaffold-ufo.py` (Python + stdlib `plistlib`, no `defcon` / `fs` deps). Round-trip verified via `fontTools.ufoLib.UFOReader` in `tests/test_scaffold.py`.
- Build pipeline: `scripts/build-font.sh` (headless FontForge, `SOURCE_DATE_EPOCH=0`) and `scripts/generate-rhena-glyphs.py` (~790 lines, fontTools-based, hand-rolled path normalizer so no `svgpathtools` dependency).
- Machine-readable contract: `src/glyph-names.json` + `src/widths.json`. Staged single-source-of-truth for Rhena adoption at `docs/rhena-coordination/rhineland.contract.json`.
- Width review ran (2026-04-14, `docs/planning/width-review-2026-04-14.md`). Three overflow bugs found (`rh_virga` 65→90, `rh_liquescent_asc`/`desc` 140→160) and corrected in `src/widths.json` + the staged contract + the scaffolded UFO3. Rhena's in-tree widths still hold the pre-review values; the coordinated adoption PR catches them up.
- Determinism: 5/5 ADR-0004 mitigations in place (contract-order iteration, round-half-up integer coords, canonical path commands, stripped-timestamp OTF hash, `SOURCE_DATE_EPOCH=0`). `justfile` `check-generated` recipe + `.github/workflows/reproducibility.yml` matrix byte-identity gate.
- Test suite: 56 pytest cases (54 active + 2 recipe regression guards), parametrized over TTF/OTF fixtures for format-specific coverage plus Phase A UFO3 structure + round-trip tests. `tests/fixtures/make_minimal_ttf.py` synthesizes a quadratic TTF; `tests/fixtures/make_minimal_otf.py` synthesizes a cubic CFF OTF — both built programmatically via fontTools `FontBuilder`, not committed as binaries.
- 8 ADRs (`docs/adr/ADR-0001`–`0008`): source format, codegen toolchain, contract ownership, determinism, width freeze, OFL 1.1 licence, OTF/CFF outlines, paleographic fidelity arbitration policy.
- 6 CI workflows (`.github/workflows/`): lint-docs, validate-contract, build-font (headless FontForge), codegen (matrix over fmt), reproducibility (matrix over fmt), smoke-rhena (workflow_dispatch only, compile-level gate).
- Licence: OFL 1.1 with Reserved Font Name "Hildegard Neumes" (`OFL.txt` + `FONTLOG.txt`, ADR-0006).
- Rhena-safe smoke test: `tests/test_rhena_smoke.py` uses `shutil.copytree` into `tmp_path` — operates on a throwaway copy, never mutates the sibling Rhena repo.

**Remaining (gated on drawing start)**:
- Coordinated Rhena-side PR for post-review widths + diplomatic-mode snapshot update (Rhena-maintainer action; `docs/rhena-coordination/rhineland.contract.json` is the diff target).
- **Phase B** (still CLI): upgrade the seven geometric glyphs (`rh_divisio_minima`/`_maior`/`_maxima`/`_finalis`, `rh_virgula`, `rh_pes_line`, `rh_flexa_line`) from placeholder rectangles to their final shapes in pure Python.
- **Phase C** (FontForge GUI): redraw the twelve calligraphic atoms starting with Tier 1 (`rh_punctum`, `rh_virga`, `rh_c_clef`, `rh_punctum_inclinatum`, `rh_quilisma`, `rh_pressus`) per `glyph_priority_sheet.md` and `docs/paleographic_drawing_briefs.md`. Trace from Dendermonde fol. 168v reference captures.
- First end-to-end render of `fixtures/corpus/o-ecclesia-line1.rhena --mode diplomatic` in Rhena, visual comparison against the manuscript reference, snapshot acceptance, and `v0.1.0` font tag.
- File Rhena ADR-0009 (draft staged at `docs/rhena-coordination/ADR-0009-generated-rhineland-glyphs.md`).

**v2 (deferred, coordinated with Rhena via new ADRs)**: accidentals (9 variants per Gregorio parity), directional oriscus split, Dominican division variants, custos, strophic differentiation (bi/tristropha dedicated atoms), full origin-convention unification to LSB-0, metadata sidecar (bbox/anchors/bearings).

## License

The font (OTF, WOFF2, UFO3 source) is licensed under the **SIL Open Font License 1.1** with Reserved Font Name **"Hildegard Neumes"**. See `OFL.txt` and `FONTLOG.txt`. Rationale in `docs/adr/ADR-0006-license.md`.

Compatible with Rhena's MIT + Apache-2.0 dual license. The generated `rhineland_glyphs.rs` file is a derivative work under OFL §1 (vector data extraction) and does not relicense its consumer — see ADR-0006 for the carve-out.

Documentation, scripts, and JSON schemas are dual-licensed under MIT + Apache-2.0, matching Rhena.

Manuscript sources: Riesencodex CC-BY 4.0, Dendermonde public domain.

## Key citations

See `research_synthesis.md` § 5 and `research_v2_findings.md` sources block for the full bibliography. Load-bearing single source for paleography is **Katie Gardiner, *A Conductor's Guide to the Music of Hildegard von Bingen*, DMA diss., Indiana University, 2022**, with the caveat that her paleographic treatment is derivative and should be supplemented by direct manuscript inspection. For pen/nib/stroke-angle detail, consult van Poucke 1991 (Alamire Dendermonde facsimile introduction) or Welker/Klaper 1998 (Reichert Verlag Riesencodex facsimile) — Gardiner does not cover that ground.
