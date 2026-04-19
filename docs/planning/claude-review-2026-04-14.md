# Planning notes for hildegard-neumes v1

Author: Claude (Opus 4.6), advisory review
Date: 2026-04-14
Audience: next planning phase, before drawing or codegen begins
Scope: `rhena_integration_plan.md` is the doctrine. This note flags gaps and
decisions that will pay back now and hurt later if deferred.

Priority tags: **[BLOCKER]** = must resolve before v1 drawing starts,
**[LOAD-BEARING]** = cheap now, expensive after commits accrue,
**[NICE]** = worth considering.

---

## 1. Source format — reconsider .sfd vs UFO3  [BLOCKER]

The integration plan assumes FontForge-native `.sfd`. Before committing, weigh
UFO3:

| Axis | .sfd | UFO3 |
| --- | --- | --- |
| File shape | single binary-ish file | directory, one `.glif` per glyph |
| Git diffs | opaque | per-glyph XML diffs (PR-reviewable) |
| Tool lock-in | FontForge-only | FontForge, Glyphs, FontLab, robofab, defcon |
| Contributor cost | install FontForge | install any UFO-aware tool |
| Merge conflicts | whole-file | per-glyph, usually trivial |

With 19 glyphs and git-first workflow, UFO3 is the stronger default. FontForge
round-trips UFO3 cleanly (File → Import, File → Generate → UFO). Recommendation:
**commit `src/hildegard-neumes.ufo/`, not `src/hildegard-neumes.sfd`.** Write it
into ADR-0001 so the decision is auditable.

Trade-off: the `build-font.sh` invocation in plan §4 needs to open the UFO
instead of the SFD, which is a one-line change in the FontForge script.

---

## 2. Determinism is load-bearing — nothing in the plan defends it  [BLOCKER]

Rhena's golden-regression doctrine (constitution §10.1) assumes byte-stable
renders. The plan's pipeline is `FontForge → OTF → Python → Rust`. Every
stage can introduce nondeterminism:

- **FontForge OTF export** writes a timestamp into the `head` table and
  orders glyphs by cmap insertion, not by a stable key
- **fontTools** iterates glyphs in font order, which depends on the above
- **svgpathtools** emits floats with `repr()` precision, which changes across
  Python minor versions
- **Dict ordering** in intermediate Python structures was guaranteed only from
  3.7 on
- **FontForge SVG export** alternates between absolute and relative commands,
  and between `M0 0`, `M 0 0`, and `M 0,0` depending on glyph complexity

Mitigation, all in `scripts/generate-rhena-glyphs.py`:

1. Iterate glyphs in the order of `src/glyph-names.json`, never in font order
2. Emit integer coordinates only (round half-to-even at extraction time)
3. Canonicalize path commands: absolute uppercase `M`, `L`, `C`, `Q`, `Z`,
   single space separators, no leading zeros on integers
4. Strip the `head.created` / `head.modified` timestamps before hashing the
   OTF for the `@generated` header
5. Force `SOURCE_DATE_EPOCH=0` when invoking FontForge

CI gate: build twice in a clean environment, `diff` the two
`rhineland_glyphs.rs` files, require byte-identity. This is one GitHub Actions
job, maybe 40 lines. Skipping it now means discovering determinism bugs via
Rhena golden-test churn, which is the worst possible feedback channel.

Write this into ADR-0004 (determinism strategy) before the first `.rs` is
generated.

---

## 3. Contract ownership and drift detection  [LOAD-BEARING]

Right now the Rhena ↔ font contract lives in three places:

- **Rhena's `glyphs/mod.rs`** — the authoritative list of names the resolver
  references
- **Rhena's `rhineland.rs`** — the current widths (v1 source-of-truth for the
  width freeze in plan §3.3)
- **`hildegard-neumes/src/glyph-names.json` + `widths.json`** — the font
  project's machine-readable copy

There is no automated check that these stay in sync. If someone adds
`rh_custos_up` to Rhena's resolver before the font ships it, both projects
will build green and the breakage will surface at `resolve_rhineland`'s
fallback path — silent at compile time.

Three plausible fixes, in order of how much I'd recommend each:

1. **Rhena owns a single `rhineland.contract.json`** checked into
   `crates/rhena-core/src/render_ir/glyphs/` and loaded via `include_str!` in
   a unit test that asserts the `rhineland.rs` constants match it. The font
   project pulls this file (git submodule, or periodic sync via a justfile
   target) and uses it as the generation input instead of the local
   `glyph-names.json`. Single source of truth, single place to edit.
2. **Font project vendors a pinned Rhena SHA** and a CI job that clones Rhena
   at that SHA, greps the resolver for glyph-name strings, and fails if any
   `rh_*` constant is mentioned in Rhena that isn't in `glyph-names.json`.
   Weaker than option 1 — drift still takes a human to bump the SHA — but
   works without any Rhena-side change.
3. **Status quo with a manual checklist**. Rejected: integration work at the
   boundary of two projects always loses a checklist war.

Option 1 is the right long-term shape. It also resolves the "which repo owns
the atomic set" ambiguity that §9 of the integration plan half-answers.
Recommend filing it as a Rhena ADR (ADR-0009?) coordinated with the font's
ADR-0003.

---

## 4. License pick blocks distribution — pick it now  [BLOCKER]

README §License says "TBD, recommended OFL-1.1." Costs nothing to commit a
license text this week; costs actual pain once the first outside contributor
or OTF binary escapes the repo.

Recommendation: commit **SIL Open Font License 1.1 with a Reserved Font Name
of "Hildegard Neumes"** now. OFL is compatible with Rhena's MIT/Apache-2.0
dual license (upstream fonts in the chant world — Gregorio, Bravura — are all
OFL, so contributors will recognize it). The RFN clause means derivative
forks must rename, which is almost always what you want for a named
paleographic font.

Deliverables:

- `OFL.txt` — official SIL text
- `FONTLOG.txt` — SIL-standard changelog stub, covers "what is this,
  who authored what version, how do I report bugs"
- `README.md` license section updated to cite both
- Rhena's `NOTICE` / `README` updated to call out the OFL-1.1 dependency
  (the generated `rhineland.rs` is a derivative work of the font — the
  Python codegen step does not relicense it)

The relicensing question around generated code is subtle: OFL §1 permits
derivative works with the font embedded, §5 lists reserved-font-name
constraints. A code-generated Rust file containing extracted paths is almost
certainly permitted under §1 without renaming (no "Font Software" is being
distributed, only derived vector data), but this should go into ADR-0006 with
an explicit carve-out in the OFL FAQ citation. If there is any doubt, ask
SIL — they answer license questions for free.

---

## 5. Width freeze will fight the calligraphy — budget one coordinated pass  [BLOCKER]

Plan §3.3 freezes widths at v1 to preserve Rhena's golden snapshots. Good
instinct, but some of these widths are aggressive:

- `rh_virga` = 65 (6.5% em) — thin stem, fine
- `rh_punctum` = 240 — reasonable for a calligraphic parallelogram
- `rh_pressus` = 300 — reasonable for a composite body
- `rh_divisio_minima` / `rh_divisio_maior` / `rh_divisio_maxima` = **16 each**
  — this is suspicious. 1.6% of em is about one pen-width. If the divisio
  glyphs share the same advance, how does the renderer distinguish them
  horizontally? Either the glyphs are purely vertical (fine — they're
  barlines) or the widths are placeholders that never got revisited
- `rh_virgula` = 12, `rh_pes_line` = 12 — similarly placeholder-looking
- `rh_flexa_line` = 172 — wildly different from pes_line 12, which is
  internally inconsistent if both are supposed to be "connector strokes"

Recommendation: **one coordinated width review pass with Rhena before drawing
starts**, not after. Concretely:

1. Render each existing Rhena glyph at 100% em and overlay its declared
   advance width as a bbox annotation (trivial PNG batch)
2. Visually verify each glyph fits its allotted advance with room for
   calligraphic mass
3. Flag any width that can't plausibly hold its target shape
4. Propose new widths in a single PR against Rhena, one golden-snapshot
   update, before the font's shapes exist
5. Freeze only after that pass

Drawing into frozen-but-wrong widths is the kind of bug that surfaces three
weeks into the drawing phase and invalidates half the work. Resolve before
FontForge opens.

(Corollary question: are the current Rhena widths derived from anything
musicological, or are they guesses from the abandoned attempt? If the
latter — and the hand-typed paths read like guesses — then the freeze is
just "preserve the bad values for snapshot stability," and loosening it now
is pure win.)

---

## 6. Y-axis convention must be documented and tested  [LOAD-BEARING]

Plan §3.3 says "Y-up. Font-native convention. Rhena's SVG backend applies a
flip transform at render time." Check this before drawing starts:

- Read Rhena's `svg_backend.rs` (or equivalent) and find the transform
  that converts font-space Y-up to SVG's Y-down
- Verify the existing `rhineland.rs` hand-typed paths are actually Y-up
  (the examples in the plan — `M-20 20 L-12 -8 L-8 500 L8 500` — look
  Y-up, with 500 as a head-of-stem and negative values at the foot, but
  this needs confirming against the actual rendered output)
- If Rhena's backend is currently flipping Y-down paths (because the
  abandoned attempt was drawn Y-down), the new font's Y-up export will
  render upside-down at first smoke test

Fix: codegen emits a Y-flip comment at the top of each path, and the first
Rhena smoke test is "run it, look at it, are neumes right-side-up." Cheap
check, prevents a half-day debugging session.

Add a roundtrip test to Rhena: `svg_backend::render` a single punctum glyph,
assert the rendered Y coordinates are monotonically increasing downward.
Will catch an axis flip regression instantly.

---

## 7. Codegen script needs a test plan of its own  [LOAD-BEARING]

`generate-rhena-glyphs.py` is going to end up ~200 lines and is the only
thing between the font tool and Rhena's build. It needs its own test suite,
not just a CI smoke check.

Proposed `tests/` layout:

```
tests/
├── fixtures/
│   ├── minimal.otf                 # hand-crafted 2-glyph OTF for fast tests
│   └── expected_minimal.rs         # golden output
├── test_contract_validation.py     # widths.json, glyph-names.json schemas
├── test_determinism.py             # regen twice, byte-diff
├── test_path_normalization.py      # absolute uppercase, integer coords
├── test_width_assertion.py         # mismatch raises a build error
├── test_golden_output.py           # minimal.otf → expected_minimal.rs
└── test_rhena_smoke.py             # optional: clone Rhena, drop, just check
```

Pytest + fontTools, no other deps. The `minimal.otf` fixture means tests
run in milliseconds and don't depend on FontForge being installed.

Add this to ADR-0002 (codegen tooling choice) as part of the decision record,
not as a future "we'll add tests later."

---

## 8. Metadata sidecar: extract more than widths  [NICE]

The Rhena contract is currently `name + path + width`. Long term, Rhena
probably wants more: bbox, anchors (where does `rh_pes_line` attach?),
ascender/descender. Not needed for v1, but:

**Cheap win:** have the codegen script also emit
`generated/rhineland-metadata.json` with per-glyph bbox, advance, leftSideBearing,
rightSideBearing, and any `anchors` the font defines. Rhena doesn't consume
it in v1, but the file exists, is versioned, and is one import away from
being useful when Rhena's resolver wants anchor-based composition.

Anchor points are particularly high-leverage for chant: a `pes` is a punctum
with a connector stroke that hits the upper-right of the punctum and the
lower-left of the virga. Hard-coded offsets in Rhena's resolver today;
anchor-driven in a principled v2.

---

## 9. ADR set to open before implementation  [LOAD-BEARING]

Mirror Rhena's ADR discipline (`docs/adr/README.md` convention). Suggested
initial set:

- **ADR-0001**: Source format — UFO3, not SFD (see §1)
- **ADR-0002**: Codegen toolchain — Python 3.11+, fontTools, svgpathtools,
  pytest; rationale for not using Rust-native fonttools
- **ADR-0003**: Contract ownership — Rhena owns `rhineland.contract.json`,
  font project consumes (see §3)
- **ADR-0004**: Determinism strategy — SOURCE_DATE_EPOCH, stable iteration
  order, integer coords, reproducibility CI gate (see §2)
- **ADR-0005**: Width freeze scope for v1 — exactly what's frozen, what can
  change, how a width bump is coordinated (see §5)
- **ADR-0006**: License — OFL-1.1 with RFN "Hildegard Neumes", plus the
  generated-code carve-out reasoning (see §4)
- **ADR-0007**: OTF vs TTF, cubic vs quadratic outlines — pin OTF/CFF
- **ADR-0008**: Paleographic fidelity policy — what Gardiner / van Poucke /
  Welker claims we honor when they conflict with usability

Short ADRs. Rhena's existing ones average ~60 lines; match that.

---

## 10. CI skeleton  [LOAD-BEARING]

Copy the minimal surface from Rhena's `.github/workflows/`:

- `lint-docs.yml` — markdownlint + lychee, same config Rhena uses
- `validate-contract.yml` — pytest runs schema validation on
  `glyph-names.json` and `widths.json`
- `build-font.yml` — headless FontForge, produce OTF + WOFF2, upload as
  artifact
- `codegen.yml` — run `generate-rhena-glyphs.py` against a checked-in
  fixture OTF, assert byte-identity with a golden `.rs`
- `reproducibility.yml` — double-build, byte-diff (see §2)
- `smoke-rhena.yml` — clone Rhena at a pinned SHA, drop the generated file,
  `just check`. Tolerated to fail on main while experimenting; hard gate
  before tagging a font release

Total: six jobs, all fast except the Rhena smoke check. None require
GPU, none require paid runners.

---

## 11. Coordinate with Rhena's active plan  [LOAD-BEARING]

Rhena is in the middle of the backend-hardening pass
(`/.claude/plans/swirling-singing-eich.md`). The font swap touches Tier 2
§2.1 (notation vocabulary) but isn't explicitly listed. Two questions for
the next planning phase:

1. Is the Rhineland glyph swap a deliverable inside the backend-hardening
   plan, or a separate plan that follows it?
2. What's the sequencing: does the font ship before, during, or after the
   remaining §4.2/§4.5 (proptest + cargo-fuzz) and §5.4 (wasm-pack tooling)
   work? A font swap during active backend hardening produces noisy
   snapshot churn and is hard to bisect if something else regresses.

Recommendation: **land after §5.4 wasm tooling, before §5.5 docs sync sweep**.
That way §5.5 can include the ADR-0009 Rhena-side note about the switch in
one coordinated docs pass.

Also: reserve Rhena's next free ADR number (ADR-0009) now for "Switch
Rhineland diplomatic glyphs to generated consumption of hildegard-neumes
font." Don't want ADR-0009 to race with something else.

---

## 12. A v1-scoped checklist the planning phase can pick up

Condensed, in the order I'd do them:

1. Decide source format (ADR-0001) — UFO3 unless there's a reason against
2. Commit OFL-1.1 + FONTLOG (ADR-0006, closes README §License)
3. Coordinate width-review pass with Rhena, land one golden-snapshot update
   (ADR-0005)
4. Establish Rhena contract-ownership file + unit test in Rhena (ADR-0003,
   coordinate with Rhena ADR-0009)
5. Write `generate-rhena-glyphs.py` against a hand-crafted minimal OTF
   fixture **before** drawing starts, with full test suite (ADR-0002,
   ADR-0004)
6. CI skeleton up — all six jobs green on an empty repo
7. Now draw the 19 glyphs in UFO3
8. Export, run codegen, copy into Rhena, `just check`, review snapshot
   churn, commit
9. Visual comparison against Rhena's `o_ecclesia_rhineland_line_01.png`
10. Tag v0.1.0 on the font, file Rhena ADR-0009 documenting the switch

Steps 1–6 are all "project hygiene before design work," and they are cheap
now and expensive later. Steps 7–10 are the actual v1 content.

---

## 13. What NOT to do in v1

- Do not add accidentals, directional oriscus, dominican divisions, or
  strophic-family differentiation to v1. They're all called out in plan §6
  as v2 work. Keep v1 a pure shape-quality replacement.
- Do not emit GSUB/GPOS rules in v1. They don't serve Rhena (the resolver
  does its own composition) and they complicate secondary-consumer
  expectations. Add them in v2 for Verovio / Illustrator workflows.
- Do not attempt to normalize the `rh_oriscus` directional split in v1.
  Plan §3.2 correctly defers this; Rhena's resolver expects a single
  atom.
- Do not add a build-time dep on anything other than Python + fontTools +
  svgpathtools + FontForge. Every extra dep taxes the contributor onboarding
  loop. `pyproject.toml` should be minimal.
- Do not ship a Rust crate wrapping the font yet. Plan §7 mentions
  `hildegard-neumes-font` as a future thin crate. Defer until there is a
  second Rust consumer besides Rhena, since Rhena doesn't need it.

---

## 14. Open questions for the planning phase to decide

1. **UFO3 vs SFD** — decide via ADR-0001
2. **Who owns the contract file** — Rhena-side or font-side? (§3)
3. **Widths freeze exact scope** — which glyphs absolutely can't move,
   which are open for the coordinated review pass (§5)
4. **Sequencing relative to Rhena backend-hardening** — before/during/after
   §5.4 and §5.5 (§11)
5. **Do we reserve ADR-0009 in Rhena now?** — yes, recommended (§11)
6. **Generated-file OFL derivation question** — commit a one-paragraph
   note in ADR-0006, ask SIL if in doubt (§4)
7. **Paleographic disagreements** — when Gardiner, van Poucke, and direct
   manuscript inspection conflict on a glyph's shape, who arbitrates?
   ADR-0008 should name a policy, even if the policy is "defer to direct
   manuscript inspection on visual questions, defer to Gardiner on
   classification questions"

---

## Notes I'm less sure about

- The `glyph-names.json` schema uses `$schema` pointing at draft/2020-12.
  fontTools doesn't care, but consider whether you want the CI to actually
  validate against the draft (via `check-jsonschema`) or just trust
  ad-hoc Python validation.
- The `smufl_codepoint_mapping.md` should probably be formalized as
  `src/codepoints.json` alongside `glyph-names.json` and `widths.json`, so
  all three contract files are machine-readable and live in one place.
  The markdown doc then becomes explanation rather than source-of-truth.
  Small refactor, tightens the "single source of truth" story per §3.
- The `examples/` directory is empty — before v1 ships, populate it with at
  least one "how to use this font in Illustrator / in an HTML page /
  in LilyPond" recipe, even stubbed, to prove the secondary-consumer story
  is real and not aspirational.

---

## Final framing

The integration plan is strong. Its two weaknesses are both at the
infrastructure layer, not the design layer:

1. **Determinism** is assumed rather than engineered (§2)
2. **Contract ownership** is ambiguous between two repos (§3)

Both are fixable with one ADR each and a handful of CI jobs. Land those
before a single glyph is drawn, and the rest of the plan executes cleanly.

The paleographic research, glyph inventory, Rhena API contract, SMuFL
alignment, and secondary-consumer story are all in good shape. Don't
re-litigate them.

— End of note
