# ADR-0009: Generated Rhineland glyphs from external OpenType font

- Status: Proposed (staged in `hildegard-neumes/docs/adr/` — to be copied into Rhena when the integration lands)
- Date: 2026-04-14
- Deciders: project maintainers
- Consulted: ADR-0002 (WASM compilation target), ADR-0004 (Rhineland glyph rendering), ADR-0008 (WASM bindings layer), constitution §§8.1, 10.1, 12 Rule 7, 13.1, hildegard-neumes font project maintainer
- Informed: contributors, downstream renderer integrators (Verovio, LilyPond, Illustrator workflow users)
- Tags: render-ir, glyphs, codegen, font, build-pipeline, diplomatic

## Context

ADR-0004 established a dual glyph system for Rhena: Rhineland calligraphic glyphs for diplomatic mode and SMuFL/Bravura glyphs for normalized mode. ADR-0004 deliberately did **not** prescribe *how* the Rhineland glyphs are authored, stored, or delivered into Rhena's Render IR — only that they MUST exist and MUST visually match the 12th-century German tradition represented in Dendermonde (ca. 1174) and the Riesencodex (ca. 1180–85).

The initial implementation of that mandate was a hand-authored Rust source file at `crates/rhena-core/src/render_ir/glyphs/rhineland.rs`, containing 19 `pub const Glyph` definitions whose `path` fields are hand-typed SVG path strings — geometric approximations of calligraphic forms derived from photographs in `docs/research/images/` (e.g. `punctum.png`, `virda.png`). Representative example:

```rust
pub const VIRGA: Glyph = Glyph {
    name: "rh_virga",
    path: "M-20 20 L-12 -8 L-8 500 L8 500 L12 -5 L55 25 L40 35 Z",
    width: 65,
};
```

This approach has been abandoned as experimental. It has five compounding problems:

1. **Aesthetic ceiling**. Hand-typed path strings in Rust source are geometric placeholders. They cannot express the nuance of a calligraphic stroke — weight variation, entry/exit curvature, ductus — that distinguishes a Rhineland punctum from a square-notation punctum. The shapes are visually coarse.
2. **Designer workflow**. A paleographer or type designer cannot iterate on these glyphs. The authoring surface is a Rust literal string, not a Bézier editor. FontForge, Glyphs, and FontLab are the native tools for this work; forcing the designer into `.rs` files effectively excludes the designer from the loop.
3. **Maintenance cost**. Every visual tweak — curve adjustment, advance-width change, stroke refinement — is a Rust code change that triggers recompilation and golden-snapshot churn, even though nothing about Rhena's semantics has changed.
4. **Reusability**. The path data is locked inside Rhena. A Verovio user, a LilyPond user, an Illustrator user, or a web page wanting `@font-face` access to the Rhineland repertoire cannot consume these glyphs at all. They would have to be re-authored.
5. **Doctrine**. Constitution §12 Rule 7 states: *"Do not make the project depend on one renderer forever."* Path data embedded in Rhena's source tree is, by construction, Rhena-only. The hand-typed approach violates this rule.

In parallel, a sibling project `hildegard-neumes` was initially planned around a Verovio/MEI consumer path. On discovering that Rhena already owns its Render IR pipeline and requires Rhineland glyphs for its diplomatic mode, the font project pivoted: its primary consumer is now Rhena, and its primary artifact is `hildegard-neumes.otf`. The integration plan is documented at `hildegard-neumes/rhena_integration_plan.md`.

This ADR records the decision to replace the hand-authored file with a file mechanically generated from that external font.

## Decision

Rhena MUST source its Rhineland glyph path data from the external `hildegard-neumes` OpenType font project, via build-time code generation. Specifically:

1. Rhineland glyphs MUST be authored in the external `hildegard-neumes` project, whose canonical source is a UFO3 directory at `src/hildegard-neumes.ufo/` (per ADR-0001 in the font project). The font project publishes `hildegard-neumes.otf` (and `.woff2`) as its primary artifacts.

2. A Python codegen script, `hildegard-neumes/scripts/generate-rhena-glyphs.py`, MUST consume `hildegard-neumes.otf` and emit a Rust source file matching Rhena's existing glyph schema:

   ```rust
   pub struct Glyph {
       pub name: &'static str,
       pub path: &'static str,
       pub width: u16,
   }
   ```

3. The emitted file MUST be committed into Rhena's source tree at `crates/rhena-core/src/render_ir/glyphs/rhineland.rs` — the same path the hand-authored file occupies today. The file MUST preserve, verbatim, the 19 existing glyph constant names:

   `PUNCTUM`, `VIRGA`, `PUNCTUM_INCLINATUM`, `QUILISMA`, `ORISCUS`, `STROPHICUS`, `PRESSUS`, `LIQUESCENT_ASC`, `LIQUESCENT_DESC`, `DEMINUTUM`, `C_CLEF`, `F_CLEF`, `DIVISIO_MINIMA`, `DIVISIO_MAIOR`, `DIVISIO_MAXIMA`, `DIVISIO_FINALIS`, `VIRGULA`, `PES_LINE`, `FLEXA_LINE`.

4. Each glyph's `width: u16` value MUST be frozen at its v1 value for this initial swap. A width change is treated as a renderer-visible change and MUST be accompanied by a coordinated golden-snapshot update pass in Rhena in the same commit.

5. The emitted file MUST begin with a prominent `@generated` header containing, at minimum: the source OTF SHA-256, the font version string, and the generation timestamp (UTC, ISO-8601). The header MUST explicitly forbid hand-editing of the file. Downstream `// @generated` linters and code-review tooling SHOULD be configured to recognize it.

6. The generation process MUST be deterministic: regenerating from the same input OTF MUST produce a byte-identical Rust file (modulo the timestamp, which MAY be frozen via `--timestamp` or `SOURCE_DATE_EPOCH` for reproducible builds). Path serialization order and number formatting MUST be stable across runs.

7. The resolver at `crates/rhena-core/src/render_ir/glyphs/mod.rs`, the SVG backend, public API, `Glyph` struct definition, and all downstream Rhena consumers MUST NOT change as a result of this swap. Rhena MUST NOT gain any new runtime dependency, MUST NOT perform runtime font loading, and MUST preserve WASM compatibility as mandated by ADR-0002 and ADR-0008.

8. The font project's release cadence and Rhena's release cadence remain independent. Rhena pins the generated file by committing it; updates occur when Rhena chooses to re-run the codegen against a newer OTF.

## Alternatives considered

### Option A (chosen): External OTF + Python codegen into Rhena source tree

- Pros:
  - Glyph design lives in a font editor — the native tool for the job. Designer iteration loop is FontForge-native, not Rust-native.
  - The same OTF that feeds Rhena is shippable to Verovio, Illustrator, Word, LilyPond, and web `@font-face` consumers. Honours constitution §12 Rule 7.
  - No new Rhena runtime dependency. No runtime font loading. WASM bundle size unchanged.
  - Determinism preserved: the committed `.rs` file is a static artifact, identical on every machine (modulo opt-in timestamp reproducibility).
  - Path data is a *build artifact*, not hand-typed code. Code review reads the diff of a generated file, which is visually explicit.
  - Aesthetic ceiling is the ceiling of the font designer's tool, not the ceiling of a programmer's patience with SVG path strings.
- Cons:
  - Introduces an out-of-tree dependency: the `hildegard-neumes` font project.
  - First-time onboarding for Rhena contributors who want to touch glyphs requires FontForge (or equivalent) and Python.
  - Requires a coordinated release process: "bump OTF version → regenerate `rhineland.rs` → update golden snapshots → commit as one unit."

### Option B: Continue hand-typing paths in `rhineland.rs`

- Pros:
  - Zero new toolchain. No Python dependency. No external project.
  - Fully self-contained within the Rhena repository.
- Cons:
  - All five failure modes enumerated in the Context section. Aesthetic ceiling, designer workflow, maintenance cost, non-reusability, and violation of constitution §12 Rule 7.
  - Locks Rhineland glyphs to Rhena forever, contradicting the project's renderer-independence doctrine.

### Option C: Runtime OTF loading via `include_bytes!` + `ttf-parser`

- Pros:
  - The OTF is truly the single source of truth — no intermediate generated `.rs` file.
  - No codegen step to run or review.
- Cons:
  - Breaks determinism guarantees. Constitution §10.1 requires deterministic output for a given input; runtime path extraction from an OTF through a third-party parser introduces a new source of non-determinism (parser version, floating-point rounding, cubic-to-quadratic conversion behaviour).
  - Adds approximately 100 KB to the WASM bundle, in direct tension with ADR-0002 and ADR-0008.
  - Requires `ttf-parser` (or `fonttools-rs`, or `read-fonts`) as a new runtime dependency in `rhena-core`. Expands the trusted dependency surface and the `cargo audit` footprint.
  - Slower path computation — Bézier extraction on every glyph lookup versus a static string constant.
  - No meaningful advantage over Option A: the OTF is *still* the source of truth in Option A; the only difference is that Option A resolves path data at build time rather than runtime.

### Option D: Build-time Rust build-script codegen (`build.rs` in `rhena-core`)

- Pros:
  - Integrated into `cargo build`. No separate Python toolchain visible at Rhena's edge.
  - Regeneration is automatic on every build.
- Cons:
  - The build script needs `ttf-parser` (or similar) as a build-dependency. The dependency problem is displaced, not eliminated.
  - Couples Rhena's build graph to the font project's release cadence. Any build now requires a resolvable path to the OTF, breaking offline and sandboxed builds.
  - Generated output is not visible in the source tree, so code review cannot see path-data changes — only `.otf` blob changes. This is strictly worse for reviewability than Option A, where the generated `.rs` file appears in diffs.
  - Cross-compilation and WASM builds become sensitive to the build-host's Python/font-parser environment.

## Consequences

### Positive

- Designer workflow is font-editor-native. Paleographers and type designers can contribute without touching Rust.
- The `hildegard-neumes.otf` artifact is externally consumable by any OpenType-aware tool (Verovio, Illustrator, Word, LilyPond, `@font-face`). Rhineland glyphs are no longer locked to Rhena.
- Constitution §12 Rule 7 is satisfied: Rhena is one of several possible renderers for the same glyph repertoire, not the sole owner of the path data.
- Aesthetic quality ceiling is raised from "hand-typed SVG strings" to "whatever a trained type designer can produce in FontForge."
- `@generated` header makes tampering visible in code review and enables automated linters to flag hand-edits.
- Determinism is preserved end-to-end: the committed `.rs` file is a static artifact.

### Negative / trade-offs

- Rhena now depends on an out-of-tree project for a class of visual changes. Glyph-level design work requires the sibling `hildegard-neumes` repository to be checked out.
- Contributors making glyph changes MUST set up FontForge and Python locally, increasing the onboarding surface for that specific workflow.
- The font project and Rhena MUST follow a coordinated release discipline: OTF version bump, regeneration, snapshot update, committed as one unit.
- Two repositories now carry related concerns; a version-mismatch failure mode becomes possible if the generated header and the OTF on disk disagree.

### Neutral

- No runtime behaviour change in Rhena. Same SVG path rendering mechanism.
- No change to the resolver (`render_ir/glyphs/mod.rs`), the SVG backend, the `Glyph` struct, public API, or any downstream consumer.
- No change to WASM bundle size, parser, IR, MEI export, grammar, or authoring experience.
- No change to Gregorio parity matrix coverage (constitution §13.1).

## Compatibility and migration impact

- Breaking change: No. The `Glyph { name, path, width }` struct is preserved. All 19 glyph constant names are preserved. Widths are frozen at v1 values. Rhena's public API is unchanged.
- Affected layers: glyph authoring pipeline and `render_ir/glyphs/rhineland.rs` only. The resolver, SVG backend, semantic IR, and Render IR are untouched.
- Migration plan:
  1. The `hildegard-neumes` project tags `v0.1.0-dev`, freezing an OTF suitable for Rhena consumption.
  2. `scripts/generate-rhena-glyphs.py` is run against that OTF, producing a new `rhineland.rs`.
  3. The generated file replaces the existing hand-authored `rhineland.rs` in a single commit.
  4. The same commit MUST include any diplomatic golden-snapshot updates produced by `cargo test`.
  5. The commit message MUST reference the source OTF SHA-256 and the `hildegard-neumes` tag.
  6. No staged rollout is required. The swap is atomic because the struct contract is unchanged.

## Validation plan

- Required tests:
  - **Diplomatic visual comparison**: render `fixtures/corpus/o-ecclesia-line1.rhena --mode diplomatic` and compare the SVG output against the paleographic reference image `docs/research/images/o_ecclesia_rhineland_line_01.png`. This validation matches the criterion established in ADR-0004.
  - **Normalized mode unchanged**: SMuFL/Bravura output for the same fixture MUST be byte-identical to pre-swap output. Any change indicates a regression outside the scope of this ADR.
  - **Resolver unchanged**: all unit tests in `render_ir/glyphs/mod.rs` MUST pass without modification.
- Golden / regression impact:
  - Diplomatic snapshots in `cargo test` are expected to churn on the first swap. Each churned snapshot MUST be visually reviewed by a maintainer against the Dendermonde reference before acceptance.
  - Normalized snapshots MUST NOT change.
- Performance impact: None. Same SVG path rendering mechanism. Same glyph lookup cost (static `pub const` table).
- Determinism check: `scripts/generate-rhena-glyphs.py` MUST be invoked twice consecutively against the same input OTF with a frozen `--timestamp`. The two resulting `rhineland.rs` files MUST diff empty.
- WASM check: `wasm-pack build` for the Rhena WASM target MUST succeed, and the resulting bundle size MUST NOT increase measurably (< 1 KB drift is acceptable and reflects incidental path-string length changes).

## References

- ADR-0002: WASM compilation target — the binary-size and determinism constraints this ADR MUST respect.
- ADR-0004: Rhineland neume glyphs for diplomatic rendering — the parent ADR establishing the dual glyph strategy. This ADR describes *how* its Rhineland half is delivered.
- ADR-0008: WASM bindings layer — complementary constraint on WASM-visible surfaces.
- Constitution §8.1 — diplomatic renderer MUST prioritize encoded witness fidelity over normalization convenience.
- Constitution §10.1 — deterministic output requirement.
- Constitution §12 Rule 7 — do not depend on one renderer forever.
- Constitution §13.1 — Gregorio parity matrix.
- `hildegard-neumes` project: `../hildegard-neumes` (sibling repository).
- `hildegard-neumes/rhena_integration_plan.md` — the font project's integration plan for Rhena.
- `hildegard-neumes/scripts/generate-rhena-glyphs.py` — the codegen script.
- `hildegard-neumes/src/glyph-names.json` and `src/widths.json` — the machine-readable contract.
- `hildegard-neumes/src/hildegard-neumes.ufo/` — UFO3 source (to be authored; per ADR-0001 in the font project).
- Dendermonde Codex, fol. 168v (O Ecclesia first line) — paleographic reference for the validation plan.
