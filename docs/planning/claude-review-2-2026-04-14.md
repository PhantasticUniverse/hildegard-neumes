# Second planning review — hildegard-neumes v1

Author: Claude (Opus 4.6), advisory review round 2
Date: 2026-04-14 (later pass)
Audience: next planning phase, before UFO3 drawing starts
Prior review: `docs/planning/claude-review-2026-04-14.md`
Prior response: `docs/planning/response-to-claude-review-2026-04-14.md`

Scope: this is a re-review after a large infrastructure landing. The
baseline is everything that landed between the first review and now:
ADR-0001…0008, OFL/FONTLOG, pyproject/justfile/ruff, the 787-line
`generate-rhena-glyphs.py`, `validate-font.py`, a 36-test pytest suite,
6 GitHub Actions workflows, the 293-line paleographic drawing briefs,
the 221-line width review, and the `docs/rhena-coordination/` staging
directory with a draft contract + ADR-0009.

Priority tags: **[BLOCKER]** = fix before the first `.glif` is authored,
**[LOAD-BEARING]** = cheap now, expensive later, **[NICE]** = polish.

---

## 0. Credit where due

Most of what the first review flagged is now addressed, and a few
things landed stronger than proposed. Worth naming so the next round
doesn't re-tread them:

- **Determinism.** All five ADR-0004 mitigations are real in the script,
  not just in the ADR. `sha256_of_stable_otf()` re-serializes through
  fontTools with timestamps zeroed. `_round_half_up()` explicitly
  rejects banker's rounding and documents why. `SOURCE_DATE_EPOCH=0`
  is wired in `build-font.sh`, honored in the script's
  `resolve_timestamp()`, and asserted by `test_determinism.py` +
  `.github/workflows/reproducibility.yml`. This is exactly the defense
  the first review asked for.
- **Width review.** The approach is stronger than my original proposal.
  I suggested rendering PNG bbox overlays; instead the review did
  text-only bbox analysis directly from the committed path strings,
  found three real overflow bugs (`rh_virga`, `rh_liquescent_asc`,
  `rh_liquescent_desc`), flagged an open-subpath bug in both
  liquescents, and identified the mixed origin-convention issue as
  architectural rather than per-glyph. Faster, cleaner, and
  diff-ready via `widths_proposed.json`.
- **Paleographic drawing briefs.** 293 lines, per-glyph, with pen
  angles, nib widths, stroke sequences, origin registration, and
  explicit "NOT" examples. This is the single most valuable new
  artifact — it converts the manuscript research into authoring
  guidance that a designer can act on without re-reading Gardiner.
- **Staging pattern.** `docs/rhena-coordination/` cleanly separates
  "drafts for upstream Rhena review" from "our own ADRs," which
  unblocks parallel work without muddying either project's
  decision record. Good idea; should keep it.
- **Test suite.** 36 passing tests, covering contract validation
  (including the subtle dataclass-module-resolution workaround in
  `_gen_import.py`), determinism, path normalization, width
  assertion, and structural golden output. For a codegen script
  this is the right surface area.

The rest of this review is what I found new, or partially-done items
from round one that have now become visible in the implementation.

---

## 1. Test fixture is TTF — ADR-0007's OTF/CFF pin is not exercised  [BLOCKER]

The most important finding. `tests/fixtures/make_minimal_ttf.py:85`
builds the test fixture as `FontBuilder(EM_SIZE, isTTF=True)`, producing
a TrueType/`glyf` font with quadratic Bézier outlines. ADR-0007 pins
the real font as `.otf` with **CFF** (cubic) outlines. Every CI run,
every local `just test`, and every PR exercises the codegen pipeline
against a font format the real pipeline will never see.

Concretely what this misses:

- `SVGPathPen` takes a different internal path for glyf vs CFF. With
  glyf it decodes TrueType contours and emits `Q` (quadratic)
  commands. With CFF it decodes Type 2 charstrings and emits `C`
  (cubic) commands. The path each takes through `fontTools.pens`
  differs meaningfully.
- A bug in how `normalize_path` handles real CFF cubics — rounding
  drift on control-point coordinates, subtle boundary cases in
  `_advance_state()` for `C` after `S` — would pass every existing
  test and fail on first contact with the real OTF.
- The `test_cubic_bezier_preserved` unit test operates on a synthetic
  string, not on a pen-emitted CFF path. It's defensive of
  `normalize_path()`'s internals, not of the pipeline.

The fact that this slipped is visible in the response document itself:
the scaffold plan listed `tests/fixtures/minimal.otf` and
`tests/fixtures/expected_minimal.rs`; what landed is `minimal.ttf`.
Drift between the plan and the implementation.

Two possible fixes, in order of how much I'd recommend each:

1. **Replace** the TTF fixture with a CFF-based OTF fixture. Build via
   `FontBuilder(EM_SIZE, isTTF=False)`, feed glyphs via
   `fontBuilder.setupCFF(psName, fontInfo, charStrings, privateDict)`
   with manually-constructed Type 2 charstrings. Slightly more code
   than `setupGlyf`, but not dramatically more — fontTools exposes
   `T2Charstring` and `Program` helpers. One fixture, close to real.
2. **Add** an OTF fixture alongside the TTF, parametrize
   `test_golden_output_shape` and `test_double_run_byte_identical`
   over both. Keeps the TTF path tested (defense in depth: if someone
   ever ships a TTF build, the pipeline still works) and adds CFF
   coverage.

Option 2 is what I'd do — slightly more code, dramatically more
confidence, and both formats have real consumers (Rhena via OTF,
possibly secondary Android/legacy consumers via TTF in a v2 build).

Whichever you pick, update `.github/workflows/codegen.yml` +
`reproducibility.yml` to build the CFF fixture too. Update
`make_minimal_ttf.py` → `make_minimal_fixtures.py` (or similar)
and reflect in `conftest.py`.

---

## 2. `test_rhena_smoke.py` can leave Rhena corrupted  [BLOCKER]

`tests/test_rhena_smoke.py:77-105` takes the following shape:

```python
target = RHENA_PATH / "crates/.../rhineland.rs"
backup = tmp_path / "rhineland.rs.backup"
shutil.copy(target, backup)
try:
    shutil.copy(out, target)    # overwrite Rhena's source file in place
    check = subprocess.run(["cargo", "check", ...], cwd=RHENA_PATH)
    ...
finally:
    shutil.copy(backup, target)
```

Three problems:

1. **Finally doesn't run on SIGKILL, OOM, power loss, CI runner
   timeout, or crashes in `cargo check`'s child processes.** If any
   of those happen, the Rhena checkout at `../hildegard` is left with
   placeholder-TTF output in `rhineland.rs`. Running `just check` in
   Rhena will then fail in a confusing way, and the user will wonder
   why the abandoned attempt disappeared.
2. **Hardcoded absolute path** to the sibling Rhena checkout
   (developer-specific, of the form `/Users/<name>/.../hildegard`)
   — not portable. Works on exactly one machine.
3. **Only runs `cargo check -p rhena-core`**, which is compilation
   without running tests. It does not exercise the snapshot path that
   the whole point of the pipeline is to update. This is a weak smoke
   check masquerading as integration.

Fix: copy the Rhena tree to a tmp path, operate on the copy, never
touch the original:

```python
@pytest.fixture
def rhena_copy(tmp_path: Path) -> Path:
    if not RHENA_PATH.exists():
        pytest.skip("Rhena not found")
    dst = tmp_path / "rhena"
    shutil.copytree(RHENA_PATH, dst, symlinks=True,
                    ignore=shutil.ignore_patterns("target", ".git"))
    return dst

def test_rhena_accepts_generated_file(rhena_copy, ...):
    target = rhena_copy / "crates/.../rhineland.rs"
    shutil.copy(out, target)
    subprocess.run(["cargo", "check", "-p", "rhena-core"], cwd=rhena_copy)
    # tmp_path is cleaned up automatically; the original Rhena is untouched
```

Downside: `shutil.copytree` on a Rhena checkout with a populated
`target/` directory is slow. Mitigate with the `ignore` pattern above
(exclude `target/` and `.git/`) and/or use a hardlink-based copy
(`shutil.copytree(..., copy_function=os.link)` where supported).

Also: drop the hardcoded absolute path. Use an env var
(`RHENA_PATH`) that defaults to `../hildegard` relative to the
project root. CI sets it explicitly; local developers override.

---

## 3. `smoke-rhena.yml` lies about test success  [BLOCKER]

`.github/workflows/smoke-rhena.yml:76-80`:

```yaml
- name: cargo test (Rhena — expect snapshot churn with placeholder TTF)
  working-directory: hildegard
  run: |
    cargo test -p rhena-core 2>&1 || true
    echo "::notice::Snapshot churn is expected when a placeholder TTF..."
```

The `|| true` swallows non-zero exit. The workflow reports green even
when every diplomatic test fails. That's a dishonest CI signal: it
looks like real coverage on the PR status page but is no more
rigorous than `echo ok`.

The underlying reasoning in the comment is valid — snapshot churn IS
expected with a placeholder fixture — but the conclusion is wrong.
The right response to "we can't validate test output with this
fixture" is "don't run the test," not "run it and ignore the result."

Fix: delete the `cargo test` step. Keep `cargo check -p rhena-core`
as the compile-level gate. Once the real OTF lands (post-drawing),
add back a `cargo test` step that actually asserts snapshots are
unchanged (the build has upgraded from "pretending to integrate" to
"really integrating").

Secondary: the cron triggers nightly at 06:00 UTC regardless of
whether anything has changed. Since `build/hildegard-neumes.otf`
doesn't yet exist and the fixture pipeline drives the smoke test,
the cron runs exactly the same workload every day. Gate the cron on
workflow-dispatch only until there's a real OTF to smoke-test
against.

Also note: the workflow clones `hildegard-project/hildegard` — a
GitHub org/repo that doesn't exist (Rhena is local-only for now).
Once enabled via schedule, every cron run will fail at the checkout
step. Either flip to `continue-on-error: true` (already set, good)
or gate the job on a repository_dispatch event until the upstream
exists.

---

## 4. ADR-0009 (staged for Rhena) is stale — still says SFD  [LOAD-BEARING]

`docs/rhena-coordination/ADR-0009-generated-rhineland-glyphs.md:40`:

> "Rhineland glyphs MUST be authored in the external `hildegard-neumes`
> FontForge project, whose canonical source is `hildegard-neumes.sfd`."

But ADR-0001 (font project, **Accepted**) decided UFO3 over SFD
specifically to unlock git-reviewable per-glyph diffs. When Rhena
adopts ADR-0009, it lands with a wrong source-format claim that
contradicts the sibling project's own decision record.

Fix: one-line edit. `hildegard-neumes.sfd` → `src/hildegard-neumes.ufo/`.
Also scan the rest of the ADR for "SFD" / "sfd" and update everywhere.

---

## 5. The draft contract file encodes the bug widths  [LOAD-BEARING]

`docs/rhena-coordination/rhineland.contract.json` has the original
(buggy) widths — `rh_virga` 65, `rh_liquescent_asc` 140,
`rh_liquescent_desc` 140 — from the abandoned attempt. The width
review (`docs/planning/width-review-2026-04-14.md`) analytically
proved all three overflow their advance, and
`docs/rhena-coordination/widths_proposed.json` documents the fix
(90, 160, 160).

Right now there are effectively **three copies** of the width
contract, and one of them is known-wrong:

| Source | Widths | Status |
| --- | --- | --- |
| `src/widths.json` | pre-review (buggy) | font project local |
| `rhineland.contract.json` | pre-review (buggy) | draft for Rhena |
| `widths_proposed.json` | post-review (corrected) | fix proposal |

If Rhena adopts `rhineland.contract.json` before the width PR lands,
they adopt the bugs and then need a follow-up ADR + snapshot churn
to fix them. Backwards order.

Fix: decide the sequence explicitly, and document it in ADR-0005:

- **Option A** (recommended): update `rhineland.contract.json` now
  with the corrected widths from `widths_proposed.json`, add a note
  that the three corrections are not yet reflected in Rhena's
  current `rhineland.rs` but will be in the coordinated adoption
  PR. The contract then leads and Rhena's code follows. Delete
  `widths_proposed.json` since its content has merged into the
  contract. Add a `width_review` provenance field in the contract
  pointing at the analysis document.

- **Option B**: hold the contract file in its current state, apply
  the width review fix first as a Rhena-side PR against the
  existing `rhineland.rs`, then regenerate `rhineland.contract.json`
  after those widths land. The contract follows Rhena's state.

Option A is faster and keeps the staging directory's "single source
of truth" story intact. Option B is more conservative but gates
contract adoption on a Rhena-side PR that's already gated on
coordinated review.

---

## 6. Field-name drift: `rhena_const` vs `rust_const`  [LOAD-BEARING]

- `src/glyph-names.json` uses `rhena_const`
- `rhineland.contract.json` uses `rust_const`
- `scripts/generate-rhena-glyphs.py` reads `rhena_const` via the
  `GlyphRecord` dataclass

When the font project migrates from local `glyph-names.json` to a
pinned copy of `rhineland.contract.json` (ADR-0003 Phase 3), the
generator breaks because the field it expects doesn't exist. Script
raises `_die(f"{names_map_path}[{i}]: bad rhena_const {rc!r}")`
because `entry.get("rhena_const", "")` returns empty.

Not breaking today (script reads local file), but is a pre-committed
landmine waiting for ADR-0003 Phase 3 to step on it.

Fix: normalize now. Both files should use the same field name. I'd
pick `rust_const` for the contract (it's Rhena-side, and Rhena's
resolver references Rust constants, not "Rhena constants"), and
rename `rhena_const` → `rust_const` in `glyph-names.json` + the
generator + the tests. One-pass rename across six files; caught by
the contract validation test if you miss a spot.

(Alternatively: keep `rhena_const` in the contract. Either name is
fine — what matters is consistency.)

---

## 7. README.md still references archived files  [LOAD-BEARING]

`README.md` §"State of the project" and §"Document map" list:

- `verovio_integration_plan.md` — was moved to
  `docs/archive/verovio_integration_plan.md`
- `examples/mei_encoding_reference.md` — moved to
  `docs/archive/mei_encoding_reference.md`
- `glyph_inventory.md` (v0.4) — moved to
  `docs/archive/glyph_inventory.md`

All three links are dead relative to the top-level project. Lychee
may already be red on `lint-docs.yml` because of this; if not, it
will be as soon as anyone exercises the workflow.

Additionally, the README doesn't mention three directories that are
now core to the project:

- `docs/adr/` — 8 accepted ADRs, the authoritative decision record
- `docs/planning/` — review + response + width review
- `docs/rhena-coordination/` — staged drafts for Rhena adoption

Fix: rewrite the README's state + document map sections to:
(a) point at the new directories, (b) update dead file links to
`docs/archive/*`, (c) add a "what's next" section pointing at the
glyph priority sheet and paleographic drawing briefs so a new
contributor can find the drawing work.

---

## 8. `justfile` comment references .sfd  [NICE]

`justfile:12`:

```make
# Build the OTF + WOFF2 from src/hildegard-neumes.sfd via FontForge
```

`build-font.sh` is correct (UFO3), only the comment drifted. Tiny
fix, but the kind of thing ADR-0001 was supposed to eliminate.

---

## 9. `validate-font.py._path_bbox` is conservative, not accurate  [NICE]

`scripts/validate-font.py:63-79` reads path tokens linearly, treating
every number pair as a point. For `C x1 y1 x2 y2 x y`, it folds the
two control points into the bbox alongside the endpoint. Cubic curves
lie strictly inside the convex hull of their control polygon, so the
bbox computed this way is a **tight upper bound** — which is fine
for overflow detection (false positives only, never false negatives)
but is *conservative*, not *accurate*.

The comment on line 66 says "Accurate for our use case (control
points bound cubic curves; we're checking overflows, not rendering)"
which is half-right. Suggestion: rephrase to "Conservative upper
bound for cubic curves; may flag real glyphs that stay inside their
advance if control points extend past the endpoints." The difference
matters when a designer gets a spurious overflow warning and doesn't
know why.

Not a bug, just documentation polish.

---

## 10. `check-generated` recipe writes to `/tmp`  [NICE]

`justfile:57`:

```make
--out /tmp/rhineland_glyphs_check.rs
```

Works on Linux/macOS, breaks on Windows (no `/tmp`). Not a current
issue — CI is ubuntu, contributors likely macOS — but the wrong
habit to commit. `build/_check/rhineland_glyphs.rs` is portable and
lives in the same `.gitignore`d directory as other build artifacts.

---

## 11. FONTLOG first-author line is a placeholder  [NICE]

`FONTLOG.txt:50-53`:

```
N: (to be filled in when the first shape is authored)
E:
W:
D:
```

SIL's FONTLOG convention expects at least one real author entry in a
published font, even if the shapes haven't landed yet. The project
maintainer should go in now with `D: initial project scaffolding,
ADR set, build pipeline`, even if outlines follow later. Prevents
the "who authored this?" question on first OFL redistribution.

Secondary: the ChangeLog line reads `13 April 2026` but every other
artefact in the project dates to `2026-04-14` (today). Minor
date-drift; fix to 14 April for consistency.

---

## 12. Remaining items from round one

Status check on the first review's open items:

| First-review item | Status now |
| --- | --- |
| §1 UFO3 vs SFD | ✅ ADR-0001 Accepted, `.ufo` path wired in build-font.sh |
| §2 Determinism | ✅ all 5 mitigations in script, ADR-0004, CI gate live |
| §3 Contract ownership | 🟡 ADR-0003 Proposed, contract drafted — blocks on Rhena adoption + field-name normalization (this review §6) |
| §4 License | ✅ OFL.txt + FONTLOG.txt + ADR-0006 |
| §5 Width freeze | ✅ review complete, 3 bugs found, `widths_proposed.json` ready for Rhena — blocks on sequencing (this review §5) |
| §6 Y-axis convention | 🟡 verified by inspection; Rhena-side roundtrip test still deferred |
| §7 Codegen test plan | 🟡 36 tests passing — but TTF-only fixture (this review §1) and smoke safety (§2) still open |
| §8 Metadata sidecar | ⏸ deferred to v2 (correct call) |
| §9 ADR set | ✅ 8 ADRs + README index |
| §10 CI skeleton | 🟡 6 workflows live — but smoke-rhena.yml dishonest (this review §3) |
| §11 Coordinate w/ Rhena active plan | ⏸ still open, awaits Rhena-side ADR-0009 decision |
| §12 v1 checklist | 🟡 steps 1–6 ~90% done, 7–10 (drawing + integration) pending |
| §13 What NOT to do | ✅ reaffirmed in glyph priority sheet + drawing briefs |
| §14 Open questions | Q1-3, Q5-7 answered. Q4 (sequencing) still needs Rhena input. |

The round-one BLOCKERs are all closed. Round two introduces a new set
concentrated in testing integrity (§1, §2) and CI honesty (§3).

---

## 13. Pre-drawing checklist, revised

The glyph priority sheet at `glyph_priority_sheet.md:67-74` lists
four pre-drawing blockers. Adding this review's findings:

| # | Item | Source |
| --- | --- | --- |
| 1 | Coordinated width review PR against Rhena | ADR-0005, round-1 §5 |
| 2 | UFO3 source scaffold at `src/hildegard-neumes.ufo/` | ADR-0001 |
| 3 | Contract ownership migration (optional but recommended) | ADR-0003, round-1 §3 |
| 4 | Codegen test suite | ADR-0002, round-1 §7 |
| 5 | **CFF/OTF test fixture** | this review §1 |
| 6 | **Rhena-safe smoke test (copy, don't mutate)** | this review §2 |
| 7 | **Remove `\|\| true` from `smoke-rhena.yml` cargo test step** | this review §3 |
| 8 | **Reconcile ADR-0009 (sfd→ufo) + contract widths + field names** | this review §§4–6 |
| 9 | **README + justfile doc refresh** | this review §§7–8 |

Items 5–9 are all cheap fixes that close the loop on round one's
infrastructure landing before any `.glif` work begins.

---

## 14. Recommended sequencing for the next session

If the goal is "start drawing glyphs this session," here's the
minimum path:

1. Fix the smoke test safety (§2) — 20 minutes. This is the one
   item where current behavior could actively damage the Rhena repo.
2. Remove `|| true` from smoke-rhena workflow (§3) — 5 minutes.
3. Add a CFF/OTF fixture alongside the TTF (§1) — 1–2 hours. Adds
   a parametrized golden_output test across both formats.
4. Update ADR-0009 (sfd → ufo), reconcile contract widths, decide
   field-name canonicalization (§§4–6) — 30 minutes.
5. README + justfile doc refresh (§§7–8) — 15 minutes.
6. Create `src/hildegard-neumes.ufo/` skeleton via FontForge or
   defcon — 15 minutes.
7. Draw `rh_punctum` as the first Tier-1 glyph per the drawing brief.

Items 1–5 total about 2.5 hours and close every remaining
infrastructure concern. Items 6–7 begin the real v1 content.

Alternate path: if drawing has been deferred while Rhena's width
review PR is pending (§5), use that waiting window for items 1–5,
and begin drawing only after the width PR merges. This is probably
what's going to happen anyway.

---

## 15. Things that could become problems but aren't yet

A short list of things I'd keep an eye on without fixing yet:

- **`generate-rhena-glyphs.py` still accepts Q commands.** ADR-0007
  pins OTF/CFF (cubic), so real output should never contain Q. The
  script's tolerance for Q is defense-in-depth against a TTF source
  slipping through. Not wrong — just worth documenting in ADR-0007's
  consequences section. ("We accept Q in the pipeline for defense
  in depth, but no CFF source will produce it; if you see Q in
  generated output, your source is secretly TTF.")
- **`rhineland.contract.json` and `glyph-names.json` are about to
  become redundant.** ADR-0003 Phase 3 deletes `glyph-names.json`.
  Between now and then, every change needs to land in both. Don't
  let that window widen.
- **`head.created = 0` in `sha256_of_stable_otf()` relies on
  fontTools accepting 0 as a valid epoch.** It does, but future
  fontTools versions could tighten validation. Keep the smoke test
  around for that regression vector.
- **Lychee's `--exclude-path docs/archive` protects archive links,
  but README.md's dead links to archived files are outside the
  archive path.** Lychee will catch them. Which is good — fix them.
- **The `_gen_import.py` workaround for `@dataclass` module
  resolution** (tests/_gen_import.py:8-11) is real and correct, but
  it's also a strong signal that the generator should be a proper
  Python module under `scripts/generate_rhena_glyphs/` or
  `hildegard_neumes_tools/codegen.py`, not a hyphenated script. v2
  cleanup, not now. Note in ADR-0002 for future reference.

---

## Final framing

Round one's complaint was that infrastructure (determinism, contract
ownership, tests, CI) was planned but not engineered. The response
closed almost all of those gaps with real code and real tests.

Round two's complaints are all in the **second-order integrity**
layer: tests that don't exercise the real format (§1), safety nets
that can corrupt sibling projects (§2), CI gates that lie about
success (§3), and drift between documents that were supposed to be
in sync (§§4–6). These are the kinds of issues that appear only
after the first layer is real — there was nothing to critique
earlier because there was nothing implemented to critique.

They're all fixable in an afternoon. The project is genuinely close
to ready for drawing, and the paleographic briefs + priority sheet
are good enough that the first glyph (rh_punctum) could land this
week.

Two things are genuinely not ready and would be unwise to defer:

1. **The CFF/OTF fixture.** The test suite's confidence in the
   pipeline is currently limited to a format the pipeline will
   never see in production. Not drawing-blocking, but
   release-blocking: v0.1.0-dev should not ship without CFF
   coverage.
2. **The Rhena smoke test's file-mutation behavior.** The first
   unhappy interruption will eat the Rhena `rhineland.rs`. Fix
   before running the test on any machine where Rhena matters.

— End of round 2
