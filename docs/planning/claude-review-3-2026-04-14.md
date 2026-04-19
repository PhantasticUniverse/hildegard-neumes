# Third planning review — hildegard-neumes v1

Author: Claude (Opus 4.6), advisory review round 3
Date: 2026-04-14 (later afternoon pass)
Prior reviews: `claude-review-2026-04-14.md` (round 1),
`claude-review-2-2026-04-14.md` (round 2)
Prior response: `response-to-claude-review-2026-04-14.md`

Scope: third pass after round 2's findings landed. Verifying the
round-2 blockers actually closed at the code level (not just in docs),
running the test suite, and surfacing anything new introduced during
the fix pass.

Priority tags as before: **[BLOCKER]** = fix before the first `.glif`,
**[LOAD-BEARING]** = cheap now / expensive later, **[NICE]** = polish.

---

## 0. What landed between round 2 and now

Verified by reading code, not just docs. The round-2 blockers are
genuinely closed:

| Round 2 finding | Status now |
| --- | --- |
| §1 CFF/OTF fixture | ✅ `tests/fixtures/make_minimal_otf.py` uses `FontBuilder(isTTF=False)` + `T2CharStringPen` with a real `curveTo()` so extracted paths contain `C` commands. `conftest.py` exposes `minimal_otf` and `minimal_ttf` in parallel. Determinism + golden-output tests are parametrized over both. New `test_ttf_and_otf_differ` is a canary that fails if the two codepaths ever produce identical output. |
| §2 Rhena smoke safety | ✅ `test_rhena_smoke.py` now builds a `shutil.copytree` of the Rhena checkout into `tmp_path` (ignoring `target/`, `.git/`, `*.rlib`, `*.rmeta`, `*.d`), operates only on the copy, and pytest cleans up on teardown. `RHENA_PATH` env var override with `../hildegard` default. The original Rhena repo is genuinely never mutated. |
| §3 `smoke-rhena.yml` dishonesty | ✅ `cargo test \|\| true` removed. `cargo check -p rhena-core` is now the sole compile gate. `schedule:` trigger removed (was cronning against a non-existent repo). Header comment explains why. |
| §4 ADR-0009 SFD → UFO | ✅ Lines 40 and 177 updated. No remaining SFD references. |
| §5 Contract widths | ✅ `rhineland.contract.json` now carries 90/160/160 for `rh_virga`/`liquescent_asc`/`liquescent_desc`. `src/widths.json` matches. ADR-0005 has a "Post-decision note" adopting option A (font project leads Rhena). `widths_proposed.json` has been deleted. |
| §6 Field-name drift | ✅ `rust_const` across `glyph-names.json`, `rhineland.contract.json`, `generate-rhena-glyphs.py`, the dataclass, all tests. One miss — see §1 below. |
| §7 README refresh | 🟡 Top half thoroughly rewritten with a "Start here" contributor block, updated document map, new references to `docs/adr/`, `docs/planning/`, `docs/rhena-coordination/`, and explicit Tier-1 drawing pointer. Bottom half still stale — see §2 below. |
| §8 Justfile comment | ✅ Line 12 now references `src/hildegard-neumes.ufo/`. |
| §9 `validate-font.py._path_bbox` comment | ✅ Rewrote to call out conservative-upper-bound semantics explicitly, with a reference back to round-2 §9. |
| §10 `/tmp` portability | ✅ `check-generated` recipe moved to `build/_check/`. `.gitignore` updated. |
| §11 FONTLOG author | ✅ Date corrected to 14 April. `N:` filled in as "Hildegard Neumes Project maintainers". `D:` expanded with the real v0.1.0-dev scope. |

Net new: `.github/workflows/codegen.yml` and `reproducibility.yml`
both gained a `strategy.matrix: fmt: [ttf, otf]` so every CI run
exercises both fixtures. Test count went 36 → 40. All 40 pass (`just
test` green). The parametrized `test_double_run_byte_identical[minimal_otf]`
is the one that actually proves determinism holds for production's
intended format.

This is a very thorough landing. I want to say that out loud before
the next round of complaints.

---

## 1. `just show-contract` is broken — regression from the field-name rename  [BLOCKER]

Verified by running it:

```
$ python3 -c "import json; n=json.load(open('src/glyph-names.json')); w=json.load(open('src/widths.json')); [print(f\"{g['rhena_const']:25s} ...\") for g in n['glyphs']]"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
KeyError: 'rhena_const'
```

`justfile:65` still references `g['rhena_const']` in the embedded
Python one-liner. The round-2 §6 field rename pass touched the
script, the dataclass, the contract file, the glyph-names JSON,
`test_contract_validation.py`, ADR references — but not this
justfile one-liner, because nothing executes it in CI and no test
shells out to it.

This is a real regression, not a cosmetic drift: the recipe will
crash for any user who runs `just show-contract` as a workflow
sanity check. It's the exact command someone opening the project
for the first time might reach for.

**Fix:** one-word change in `justfile:65`:

```make
show-contract:
    @python -c "import json; n=json.load(open('src/glyph-names.json')); w=json.load(open('src/widths.json')); [print(f\"{g['rust_const']:25s} {g['font_name']:25s} w={w['widths'][g['font_name']]:4d}\") for g in n['glyphs']]"
```

**Deeper fix** (recommended, one test case): add a pytest that
shells out to `just show-contract` (or to the underlying Python
one-liner) and asserts exit 0. Protects against this class of
regression permanently. Place in `test_contract_validation.py`
since it's a contract-level check.

```python
def test_show_contract_one_liner_runs(scripts_dir, names_map_path, widths_path):
    """just show-contract must not regress — the one-liner is a
    CLI surface that tests don't otherwise exercise."""
    code = (
        "import json;"
        f"n=json.load(open('{names_map_path}'));"
        f"w=json.load(open('{widths_path}'));"
        "[print(g['rust_const']) for g in n['glyphs']]"
    )
    result = subprocess.run([sys.executable, "-c", code],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
```

That one test would have caught this and will catch the next rename.

---

## 2. README `Future additions` + `MVP path` sections are stale  [LOAD-BEARING]

The README top was thoroughly rewritten — "State of the project"
now lists ADRs, rhena-coordination, planning, paleographic briefs,
and a new "Start here (for contributors drawing glyphs)" section
that tells a new reader exactly what to do. All good.

But `README.md:162-178` still has the pre-pivot v1 plan text:

```md
Future additions during v1 build:
- `src/hildegard-neumes.sfd` — FontForge source         ← WRONG (UFO3)
- `build/hildegard-neumes.otf`, `build/hildegard-neumes.woff2` — exported font
- `scripts/build-font.sh`, `scripts/generate-rhena-glyphs.py` — build pipeline  ← already exist
- `generated/rhineland_glyphs.rs` — codegen output
- `src/glyph-names.json`, `src/widths.json` — machine-readable API contract  ← already exist

## MVP path (v1)

1. **Set up FontForge source.** `src/hildegard-neumes.sfd` ...  ← WRONG
...
5. **Write `scripts/generate-rhena-glyphs.py`** (~200 lines using fontTools + svgpathtools).  ← already exists, is 787 lines, does not use svgpathtools
```

Three stale claims in two adjacent sections:

- `hildegard-neumes.sfd` — contradicts ADR-0001 and the new Start here block
- `scripts/generate-rhena-glyphs.py` described as a "future addition" that needs writing
- "~200 lines using fontTools + svgpathtools" — the script is 787 lines and `pyproject.toml` doesn't list svgpathtools (it's not needed; `generate-rhena-glyphs.py` uses a hand-rolled normalizer because `SVGPathPen` already emits absolute uppercase)

**Fix:** either delete the two stale sections entirely (the new
"Start here" block + the existing `rhena_integration_plan.md § 5`
already cover the v1 plan in current-state terms) or rewrite them
as a "v1 status" checklist showing what's done vs what remains.
The former is cleaner — the README doesn't need to document the
plan; that's what `rhena_integration_plan.md` is for.

If rewriting, the sections should read something like:

```md
## v1 status snapshot

Done:
- UFO3 source format fixed (ADR-0001) — scaffold creation pending FontForge
- OTF→Rust codegen pipeline (scripts/generate-rhena-glyphs.py, 787 lines)
- Determinism: 5/5 ADR-0004 mitigations + CI byte-identity gate
- Width review: 3 overflow bugs found and corrected in src/widths.json
- 8 ADRs, 6 CI workflows, 40 passing pytest cases (parametrized TTF+OTF)
- OFL 1.1 + FONTLOG + rhena-coordination staging

Remaining (gated on drawing start):
- src/hildegard-neumes.ufo/ skeleton creation in FontForge
- Coordinated Rhena-side PR for post-review widths + snapshot update
- Tier 1 drawing: rh_punctum, rh_virga, rh_c_clef, rh_punctum_inclinatum,
  rh_quilisma, rh_pressus (per glyph_priority_sheet.md)
- Tier 2 + Tier 3
- Tag v0.1.0 + file Rhena ADR-0009
```

Same fact set, accurate to today.

---

## 3. `smoke-rhena.yml` still references a non-existent repo  [LOAD-BEARING]

Round 2 §3 flagged two things: (a) the dishonest `|| true`, and
(b) the hardcoded `hildegard-project/hildegard` repo slug that
doesn't exist on github.com. The first landed; the second did not.

`smoke-rhena.yml:48`:

```yaml
- name: Clone Rhena
  uses: actions/checkout@v4
  with:
    repository: hildegard-project/hildegard
    ref: ${{ env.RHENA_REF }}
    path: hildegard
```

The schedule trigger was correctly removed, so this no longer
cron-fails — but a human running `workflow_dispatch` will hit a 404
on the checkout step. The workflow is effectively dead until the
Rhena repo is either published publicly at that slug or the
workflow is rewritten.

Three options:

1. **Parametrize the repo slug.** Add `rhena_repo` as a
   workflow_dispatch input (default `hildegard-project/hildegard`),
   so anyone running it can point at their own fork without
   editing the file.
2. **Delete the workflow.** It's currently unreachable, and the
   local `tests/test_rhena_smoke.py` does the same job for anyone
   with a sibling checkout. Shipping a CI workflow that can't run
   is worse than not shipping one.
3. **Leave it, document it as placeholder.** The comment block at
   the top of the file is already doing this — it says "the
   schedule is disabled until (a) the real OTF exists ... and (b)
   a public Rhena repo exists to clone from." OK, but then the
   `workflow_dispatch` trigger is also broken under the same
   condition (b), and the comment doesn't say that. At minimum,
   add a note on `workflow_dispatch` too.

Option 1 is the lowest-regret fix — it makes the workflow
reachable for the user's current local-only setup without
pretending a public repo exists.

Also note: `continue-on-error: true` (line 37) is still set.
With `schedule` removed, this means "when a human triggers this,
allow failure." That might be intentional ("flaky infra gate, OK
to fail") but nothing documents it. If the intent is "this is a
hard gate before releases," drop `continue-on-error`. If the
intent is "this is a diagnostic tool, runs on demand, failure is
informational," say so in the comment block.

---

## 4. ADR-0002 references only one fixture  [LOAD-BEARING]

`ADR-0002-codegen-toolchain.md:23`:

> The script MUST have its own test suite at `tests/`, with a
> hand-crafted minimal OTF fixture (`tests/fixtures/minimal.otf`)
> that exercises the pipeline without requiring FontForge at test
> time.

Stale after round 2 §1. There are now two fixtures (`minimal.ttf`
and `minimal.otf`), parametrized across tests, and both live in
the CI matrix. The ADR should say so explicitly — it's load-bearing
because a future contributor reading the ADR will expect one
fixture and then find the TTF path and be confused about whether
it's supposed to exist.

**Fix:** one-paragraph update:

```md
The script MUST have its own test suite at `tests/` exercising
both outline formats:

- `tests/fixtures/make_minimal_otf.py` — CFF (cubic) fixture,
  matching production per ADR-0007.
- `tests/fixtures/make_minimal_ttf.py` — TrueType (quadratic)
  fixture for defense-in-depth coverage of the glyf codepath.

Fixtures are regenerated programmatically at pytest session start
(via `conftest.py`), not committed as binary blobs. Tests that
depend on format-specific behaviour parametrize over both.
```

---

## 5. Build workflow skips silently when UFO3 is absent  [LOAD-BEARING]

`build-font.yml` has a "Check UFO3 source exists" step that outputs
`skip=true` when `src/hildegard-neumes.ufo/` is missing, then every
downstream step is `if: steps.check_ufo.outputs.skip == 'false'`.
The job ends **green** regardless.

This is fine during the pre-drawing phase — there's no UFO yet, so
skipping is correct. But the signal is silent: the workflow reports
"green" whether the UFO is "expected missing" or "unexpected missing
because a developer accidentally deleted it." There's no indication
on the PR UI that the build actually did nothing.

**Fix:** emit a notice annotation when skipping, so reviewers
see a yellow banner in the PR:

```yaml
- name: Annotate skipped build
  if: steps.check_ufo.outputs.skip == 'true'
  run: |
    echo "::notice::src/hildegard-neumes.ufo/ not found; build-font job skipped. This is expected in the pre-drawing phase."
```

One step, zero behaviour change, preserves the "green when
skipping" outcome while giving reviewers a signal to read. The
day the UFO lands, this notice stops firing and the workflow does
real work.

Same pattern applies to the "Validate font" and "Upload OTF
artifact" steps (all conditional on `skip == 'false'`).

---

## 6. Reproducibility workflow still writes to `/tmp`  [NICE]

`reproducibility.yml:56,67,72,74` use `/tmp/run1.${{ matrix.fmt }}.rs`
paths. The `check-generated` recipe was moved to `build/_check/`
per round 2 §10, but the CI workflow that tests the same invariant
stayed on `/tmp`.

On ubuntu-latest this works fine — the point of round 2 §10 was
Windows portability, and Windows isn't in the CI matrix. But the
inconsistency is worth closing: if someone adds `windows-latest`
to the matrix later, the workflow breaks silently.

**Fix:** one-line change per run step:

```yaml
--out ${{ runner.temp }}/run1.${{ matrix.fmt }}.rs
```

`runner.temp` is the portable GitHub Actions variable for a
runner-specific temp directory. Works on all three runner OSes.

---

## 7. No test exercises the justfile recipes  [NICE]

This is the meta-observation behind §1. The justfile has 12
recipes; nothing in CI invokes any of them. Tests go through
`pytest` directly, CI workflows inline the commands that would
otherwise be justfile recipes, and the two are kept in sync by
hand.

The consequence: every justfile recipe is implicitly "assumed
working" but only one (`just test`) is exercised, and that's only
because a contributor happens to run it. `just build`, `just
generate-rhena`, `just show-contract`, `just validate-font`, `just
ci-check`, `just copy-to-rhena` — none of these have verification.
The `show-contract` regression in §1 could have been caught by a
one-line "does `just show-contract` exit 0" test.

**Fix:** add a small workflow (`just-recipes.yml` or a job inside
`validate-contract.yml`) that runs:

```yaml
- run: just show-contract
- run: just test
- run: just generate-rhena --help  # if the recipe has --help wiring
```

At minimum `just show-contract`. That's the one that's already
broken and the easiest to protect.

Alternatively: inline a pytest that shells out to each recipe. The
justfile stays the authoritative interface and the test suite
stays self-contained.

---

## 8. `smoke-rhena.yml` `continue-on-error: true` is undocumented  [NICE]

The comment block at the top of the workflow explains:
- why schedule was removed
- why `cargo test` was removed

It does **not** explain why `continue-on-error: true` is set. This
flag converts a red run into yellow — "ran but failed, treat as
warning." With schedule removed and workflow_dispatch only, this
means a human-triggered run that fails will look "mostly OK" in
the status checks list. Almost certainly not what anyone wants.

Intent check: if the idea is "this is a best-effort smoke test,
failures don't block anything because nothing depends on it," the
comment should say so. If the idea is "I removed the schedule but
left this flag accidentally," just delete the flag.

**Fix:** either remove `continue-on-error: true` (recommended —
the workflow exists to gate, not to soft-warn) or add a line to
the comment block:

```yaml
# continue-on-error: this workflow is best-effort and advisory.
# It should not block merges; if it reports red, investigate but
# don't revert.
```

My recommendation: remove the flag. If someone triggers a smoke
test manually, they want to know whether it passed.

---

## 9. What's still deferred (and correctly so)

These were flagged in rounds 1 or 2 and consciously deferred. They
should stay deferred — I'm listing them so the reader of this
review doesn't wonder whether I forgot:

- **Y-axis roundtrip test in Rhena** (round 1 §6). Still open. It's
  a Rhena-side test, not a font-project test, and depends on
  Rhena-side coordination. Defer until the coordinated width PR
  lands — the Y-axis test can ride in on the same commit.
- **Metadata sidecar** (round 1 §8). v2. Correct call.
- **Rhena-side adoption of `rhineland.contract.json`** (round 1 §3,
  round 2 §5). Blocks on a Rhena PR. Not a font-project
  responsibility. ADR-0003 stays Proposed until Rhena adopts.
- **`codepoints.json` extraction** (round 1 notes). SMuFL codepoints
  still live inside `glyph-names.json`'s `smufl_codepoint` fields.
  Equivalent for current use; refactor if it becomes painful.
- **`examples/` population** (round 1 notes). Directory still empty.
  Populate with one "use this font in HTML/LilyPond" recipe before
  v0.1.0 tag, but not blocking pre-drawing.
- **Codegen script as a proper module** (round 2 notes). Still a
  hyphenated standalone script with `_gen_import.py` workaround.
  v2 refactor.

---

## 10. Pre-drawing checklist, revised for round 3

Updated from the round-2 §13 list:

| # | Item | Status | Time |
| --- | --- | --- | --- |
| 1 | Coordinated width-review PR against Rhena | ⏸ pending Rhena maintainer | N/A to font project |
| 2 | UFO3 source scaffold at `src/hildegard-neumes.ufo/` | ⏸ pending FontForge session | 15 min |
| 3 | Contract ownership migration | ⏸ pending Rhena maintainer | N/A to font project |
| 4 | Codegen test suite | ✅ 40 tests, 5/5 ADR-0004 mitigations verified | done |
| 5 | CFF/OTF test fixture | ✅ round 2 fix landed | done |
| 6 | Rhena-safe smoke test (copy, don't mutate) | ✅ round 2 fix landed | done |
| 7 | Remove `\|\| true` from `smoke-rhena.yml` | ✅ round 2 fix landed | done |
| 8 | Reconcile ADR-0009 (sfd→ufo) + contract widths + field names | ✅ round 2 fix landed | done |
| 9 | README + justfile doc refresh | 🟡 **incomplete** — see §2 | 10 min |
| **10** | **Fix `just show-contract` regression** | ❌ **new in round 3** | 1 min |
| **11** | **Add recipe-level smoke test** | ❌ **new in round 3** | 15 min |
| **12** | **Annotate skipped build-font job** | ❌ **new in round 3** | 5 min |
| **13** | **Parametrize or delete smoke-rhena.yml repo slug** | ❌ **new in round 3** | 5 min |
| **14** | **Update ADR-0002 to reference both fixtures** | ❌ **new in round 3** | 5 min |

Items 10-14 total ≈ 30 minutes. Items 9 + those = 40 minutes. Then
items 1-3 unblock and drawing begins.

---

## 11. Short take on trajectory

Three review rounds, each smaller than the last. Round 1 found
structural gaps (16 items, 4 blockers). Round 2 found integrity
gaps introduced by round 1's fixes (14 items, 3 blockers). Round 3
finds polish-level gaps introduced by round 2's fixes (8 items, 1
blocker) — and the one blocker is a one-word typo in a justfile
one-liner that would be caught immediately by any recipe-level
smoke test.

This is the expected shape of a well-run iterative review: each
pass gets shorter, findings shift from "missing foundation" to
"missing polish," and the blockers become less structural and
more cosmetic. The work is essentially ready for drawing.

Two things are worth naming explicitly:

1. **The CFF fixture is a legitimate technical achievement.**
   Programmatically building a CFF-based OTF via `FontBuilder` +
   `T2CharStringPen` is harder than the TTF path, and the
   `test_ttf_and_otf_differ` canary is exactly the right defense
   against accidentally making the two fixtures produce the same
   output. This is the kind of test someone writes only after
   having been bitten by a format-blind test suite.
2. **The `shutil.copytree` smoke-test rewrite is the right
   abstraction.** The earlier `try/finally` pattern was a classic
   "works on the happy path, fails on the interesting path" bug.
   The new version operates on a throwaway copy and is genuinely
   impossible to regress into mutating the sibling repo. Worth
   keeping as the shape for any future cross-project smoke tests.

Credit where due.

---

## 12. What I would do next, specifically

If the next session is 90 minutes:

1. Fix `justfile:65` (one word: `rhena_const` → `rust_const`)
2. Add `test_show_contract_one_liner_runs` to
   `tests/test_contract_validation.py` (as sketched in §1)
3. Strip `README.md:162-178` and replace with a v1-status snapshot
   per §2's template
4. Update `.github/workflows/smoke-rhena.yml` to either parametrize
   `rhena_repo` as a workflow input or delete the file — I'd
   parametrize, since someone may want to test against a fork
5. Update `ADR-0002-codegen-toolchain.md:23` to reference both
   fixtures
6. Add a `::notice::` annotation to `build-font.yml` skip path
7. Open FontForge, create `src/hildegard-neumes.ufo/` with 19
   empty glyph slots named per `src/glyph-names.json`, em=1000,
   save, commit as "feat(font): scaffold UFO3 source per ADR-0001"
8. Begin drawing `rh_punctum` per `paleographic_drawing_briefs.md §1`

Items 1-6 are the round-3 infrastructure close. Items 7-8 begin
the actual v1 content.

At step 7, the project transitions from "infrastructure build-out"
to "glyph authoring," which is the phase the paleographic briefs
and glyph priority sheet were written to support.

— End of round 3
