# Width Review — 2026-04-14

Status: v1 analysis, pre-drawing
Purpose: fulfil the coordinated width-review pass mandated by `docs/adr/ADR-0005-width-freeze-scope.md` before the first UFO3 glyph is authored.
Scope: analyze each of the 19 Rhineland atom advance widths in Rhena's abandoned `crates/rhena-core/src/render_ir/glyphs/rhineland.rs` against the glyph body bbox derived from the committed path strings. Surface inconsistencies and bugs for coordinated resolution in a Rhena-side PR.

Methodology is text-based (no FontForge required): bbox is computed from the union of on-curve points and Bézier control points in each path. Cubic curves can marginally exceed their control polygon, but for advance-width sanity the control-polygon bbox is a tight upper bound.

---

## 1. Per-glyph bbox vs advance

Origin convention legend:
- **C** = centred-origin (origin at visual centre, advance ≈ body width)
- **L** = LSB-0 origin (origin at left edge, body extends only to the right)
- **?** = asymmetric / neither pure (body extends to both sides unevenly)

| # | Glyph | Path x extrema | body width | advance | conv | status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `rh_punctum` | [-120, +120] | 240 | 240 | C | ✓ clean |
| 2 | **`rh_virga`** | **[-20, +55]** | **75** | **65** | ? | **❌ overflow by 10 (LSB interp) / 22.5 (centred interp)** |
| 3 | `rh_punctum_inclinatum` | [-60, +60] | 120 | 120 | C | ✓ clean |
| 4 | `rh_quilisma` | [-50, +120] | 170 | 170 | ? | ⚠ left-biased origin, zero RSB |
| 5 | `rh_oriscus` | [-100, +100] | 200 | 200 | C | ✓ clean |
| 6 | `rh_strophicus` | [-80, +80] | 160 | 160 | C | ✓ clean |
| 7 | `rh_pressus` | [-150, +150] | 300 | 300 | C | ✓ clean (but shape is wrong; see § 3) |
| 8 | **`rh_liquescent_asc`** | **[-70, +75]** | **145** | **140** | C | **⚠ overflow by 5 + open subpath bug** |
| 9 | **`rh_liquescent_desc`** | **[-70, +75]** | **145** | **140** | C | **⚠ overflow by 5 + open subpath bug** |
| 10 | `rh_deminutum` | [-50, +50] | 100 | 100 | C | ✓ clean |
| 11 | `rh_c_clef` | [0, +110] | 110 | 110 | L | ✓ clean (different convention from ##1–10) |
| 12 | `rh_f_clef` | [0, +160] | 160 | 160 | L | ✓ (different convention, also missing the dots per paleographic brief) |
| 13 | `rh_divisio_minima` | [0, +16] | 16 | 16 | L | ✓ clean |
| 14 | `rh_divisio_maior` | [0, +16] | 16 | 16 | L | ✓ clean |
| 15 | `rh_divisio_maxima` | [0, +16] | 16 | 16 | L | ✓ clean |
| 16 | `rh_divisio_finalis` | [0, +56] | 56 | 56 | L | ✓ clean |
| 17 | `rh_virgula` | [0, +12] | 12 | 12 | L | ✓ clean |
| 18 | `rh_pes_line` | [-6, +6] | 12 | 12 | C | ⚠ centred while its peer connector (`rh_flexa_line`) uses LSB |
| 19 | `rh_flexa_line` | [0, +172] | 172 | 172 | L | ✓ clean |

**Summary**:

- **10 glyphs use centred origin**: `rh_punctum`, `rh_virga`, `rh_punctum_inclinatum`, `rh_quilisma`, `rh_oriscus`, `rh_strophicus`, `rh_pressus`, `rh_liquescent_asc`, `rh_liquescent_desc`, `rh_deminutum`, `rh_pes_line`. Most are consistent; `rh_virga`, `rh_liquescent_asc`, `rh_liquescent_desc`, `rh_quilisma` have either bbox-vs-advance mismatches or asymmetric origins.
- **8 glyphs use LSB-0 origin**: the two clefs, the four divisio bars, `rh_virgula`, `rh_flexa_line`. All clean within that convention.
- **Three hard overflows**: `rh_virga`, `rh_liquescent_asc`, `rh_liquescent_desc`. These are bugs: the glyph body physically cannot fit inside the declared advance.
- **One origin oddity**: `rh_quilisma` has body extent [-50, +120] with advance 170 — the advance *width* equals the body width, but the origin is left-biased (LSB = -50, RSB = 0). No overflow, but conceptually inconsistent with the other centred glyphs.
- **Two connector-family inconsistencies**: `rh_pes_line` (centred, width 12) vs `rh_flexa_line` (LSB-0, width 172). Both are supposed to be "thin connector strokes" but use different conventions.

---

## 2. Detailed per-glyph notes on the problem glyphs

### 2.1 `rh_virga` — hard overflow (bug)

Path: `M-20 20 L-12 -8 L-8 500 L8 500 L12 -5 L55 25 L40 35 Z`

Interpreted as a continuous pen gesture: head at top-left (around x=-20 to -12, y=0 to 20), stem along x=±8 from y=0 up to y=500, foot extending from x=12 down and right to x=55.

- **x range**: -20 to +55. Body width = 75.
- **Advance**: 65.
- **Bug**: advance < body width. The foot at x=+55 physically extends past the advance boundary no matter which origin convention you use.
  - If centred-origin: half-width would need to be ≥ 55, giving advance ≥ 110.
  - If LSB-0 origin: the glyph starts at x=-20 (negative LSB of -20) and extends to x=+55; total advance would need to be ≥ 75 (20 LSB compensation + 55 right extent). At LSB=-20 the advance 65 leaves only 45 for the right side, 10 short of the +55 right extreme.
- **Recommendation**: advance 65 → **90**. 90 accommodates either convention with a small right sidebearing. (Alternative fix: redraw the foot shorter, keeping advance 65. Calligraphically the foot should be a small hook, not a wide triangular flap; a shorter foot is more paleographically honest per the drawing brief.)

### 2.2 `rh_liquescent_asc` — small overflow + open subpath (bug)

Path: `M-70 10 L-20 -40 L70 -10 L20 40 Z M10 -30 C25 -140 50 -210 75 -280`

- **Subpath 1**: a closed diamond head at roughly x ∈ [-70, +70], y ∈ [-40, +40].
- **Subpath 2**: an OPEN cubic Bézier tail from (10, -30) ending at (75, -280). No `Z` close.
- **x range**: -70 to +75. Body width = 145.
- **Advance**: 140.
- **Bug 1 (overflow)**: advance 140 < body 145. Tail endpoint at x=+75 overflows the centred half-width of 70 by 5 units.
- **Bug 2 (open subpath)**: the tail is unclosed. SVG's default fill rule will phantom-close from (75, -280) back to (10, -30), producing a filled tail region. If Rhena's backend applies `fill="currentColor"` (the default), this is probably what the original author intended — a filled tail shape. If the intention was a stroked hairline tail, a `stroke` attribute would be needed, which the Rhena backend doesn't emit. The current rendering is thus a filled triangle-ish tail, not a thin hairline. Whether this matches the desired liquescent-tail appearance needs visual verification.
- **Recommendation**: advance 140 → **160**. Also: in the UFO3 redraw, either close the tail with a return path (two adjacent lines to give it a thin stroke appearance as a filled outline) or accept the filled-tail rendering as intentional. Per the drawing brief, the tail should be a curved calligraphic stroke with tapering pressure — that's better expressed as a filled two-boundary shape, so close it in the redraw.

### 2.3 `rh_liquescent_desc` — same as ascending

Mirror of `rh_liquescent_asc`. Same overflow (5 units), same open-subpath bug. Same recommendation: advance 140 → **160**.

### 2.4 `rh_quilisma` — left-biased origin, zero RSB

Path: `M-50 50 L30 -15 L-45 -100 L30 -190 L-45 -280 L20 -370 L-8 -470 L12 -470 L60 -370 L120 -280 L35 -190 L120 -100 L35 -15 L90 50 Z`

- **x range**: -50 to +120. Body width = 170.
- **Advance**: 170.
- No overflow — advance exactly equals body width.
- **Oddity**: origin is 50 units *inside* the body from the left edge. Effective LSB = -50, RSB = 0. This is valid OpenType (negative LSB is legal) but inconsistent with the other centred glyphs in the font.
- Visually: placed at origin O in layout, the glyph body occupies O-50 to O+120, and the next glyph's origin is at O+170 = (O+120) + 50. So the gap to the next glyph is 50 units (not zero — I miscomputed in the table; corrected here). That's actually a sensible gap, not tight at all.
- **Diagnosis**: this is not a bug, it's an unusual origin convention. The visible behaviour is acceptable. Recommend leaving the advance at 170 but redrawing the path to centre the body on origin (shift all x values by -35 so the body sits at [-85, +85]) for consistency with the other centred glyphs in the font.
- **Recommendation**: advance 170 → **170** (unchanged). Redraw path with centred origin.

### 2.5 Connector-family inconsistency

`rh_pes_line` (centred, body [-6, +6], advance 12) and `rh_flexa_line` (LSB-0, body [0, +172], advance 172) use different origin conventions despite being described as a single "connector" family in the abandoned attempt's comments and in the paleographic brief.

- **Diagnosis**: cosmetic inconsistency. Neither is broken.
- **Recommendation**: in the UFO3 redraw, unify to LSB-0 for consistency with the bar family. Change `rh_pes_line` to x ∈ [0, 12] (move both vertical edges right by 6). Advance unchanged at 12.

### 2.6 `rh_pressus` — clean width, wrong shape

The advance is internally consistent (width 300, centred body [-150, +150]), but the path is a scaled-up version of `rh_punctum` (parallelogram with cubic smoothing), not the "vertical line attached to a short undulating line" that Gardiner p. 94 describes and `docs/paleographic_drawing_briefs.md` § 7 specifies. The advance 300 may or may not suit the correct shape once drawn; re-evaluate after the redraw. Flag this as "advance preserved provisionally, re-verify after shape is correct."

### 2.7 `rh_f_clef` — clean width, incomplete shape

Path has vertical bar + two horizontal bars. The drawing brief specifies the F-clef also has two small dots flanking the upper bar on the right (traditional F-clef markers). Those are missing from the abandoned attempt. Advance 160 should accommodate them (vertical at x=[0, 40], upper bar at x=[60, 160], lower bar at x=[60, 130]; room remains at x ≈ 140–160 for dots). No width change needed; shape redraw required.

---

## 3. Findings

### Finding 3.1 — Mixed origin conventions (architectural)

The font currently uses two origin conventions simultaneously. This is not a bug per se (OpenType permits it, and layout math works if the engine is consistent), but it is surprising for external consumers and internal contributors.

**Which convention is "right"?**

- **SMuFL/Bravura convention**: LSB-0 origin. Origin at left edge; body extends to the right only; advance = LSB-to-LSB distance. This is what every mainstream SMuFL font uses. External consumers (Verovio, LilyPond, Illustrator, MuseScore) will expect this.
- **Centred-origin convention**: Origin at visual centre; body straddles the origin. Useful for glyphs whose position on a staff is keyed to their geometric centre (e.g. a punctum at pitch P means "centre of mass at pitch P"). Rhena's SVG backend currently uses this for 10 of 19 glyphs.

**Unified recommendation (v2)**: migrate all glyphs to LSB-0 convention for external consumability. This is an architectural change that touches every glyph's path data and every `<use xlink:href>` call site in Rhena's SVG backend. It is **out of scope for v1**, which is a pure shape-quality replacement. Flag as a v2 ADR in a follow-up.

**v1 approach**: preserve the mixed conventions as they exist today. Only fix the overflow bugs (§§ 2.1–2.3). Do not touch the origin convention of any glyph unless required to fix a bug.

### Finding 3.2 — Three glyphs overflow their advance (bugs)

`rh_virga` (75 body / 65 advance), `rh_liquescent_asc` (145 / 140), `rh_liquescent_desc` (145 / 140). These are real bugs that would have surfaced as visual clipping or layout overlap in a live render. The advance-width proposals in § 4 below fix them.

### Finding 3.3 — Pressus and F-clef have wrong shapes but correct widths

`rh_pressus` and `rh_f_clef` carry shapes that disagree with the paleographic drawing briefs and Gardiner (for pressus). The advance widths happen to be large enough to accommodate the correct shapes, but this is incidental and should be re-verified once the glyphs are redrawn in UFO3.

### Finding 3.4 — Open subpaths in the liquescents

Both liquescents have an open cubic Bézier for the tail, which SVG's default fill renders as a phantom-closed filled shape. This may or may not be intentional. Flag for redraw: in the UFO3 source, either explicitly close the tail (turning it into a closed calligraphic stroke with outline) or accept the fill-based rendering. The drawing brief prefers a closed two-boundary shape.

### Finding 3.5 — Divisio trio widths (16 each) are not a bug

The review agent's concern that `rh_divisio_minima`, `rh_divisio_maior`, `rh_divisio_maxima` all share width 16 was worth asking. Analysis confirms it's fine: all three are purely vertical rectangles of the same thickness (16 em-units); their visible distinction is the *height* (one staff space, four staff spaces, four-plus-overhang), not the width. Advance of 16 exactly matches body width under LSB-0 convention. No adjustment needed.

### Finding 3.6 — Connector family (pes_line vs flexa_line) origin split

Cosmetic inconsistency: `rh_pes_line` centred, `rh_flexa_line` LSB-0. Not a bug. Recommendation in § 2.5: unify to LSB-0 in the UFO3 redraw. Low priority.

---

## 4. Proposed width changes for v1

A coordinated Rhena-side PR should land these width adjustments together with any diplomatic-mode golden-snapshot updates.

| Glyph | Current | Proposed | Reason |
| --- | --- | --- | --- |
| `rh_virga` | 65 | **90** | Overflow fix (foot extends to +55 in current path; proposed 90 accommodates either origin convention with a small RSB). Alternative: redraw with a shorter foot and keep advance 65. |
| `rh_liquescent_asc` | 140 | **160** | Overflow fix (tail endpoint at +75 exceeds centred half-width of 70 by 5; 160 gives 80-unit half-width with 5 units RSB). |
| `rh_liquescent_desc` | 140 | **160** | Same as asc (mirror shape). |

All other widths are preserved as v1-frozen values.

**Update 2026-04-19**: the corrected widths have been merged into `docs/rhena-coordination/rhineland.contract.json` and `src/widths.json`; the separate staging file `widths_proposed.json` was deleted (round-3 review §0). The coordinated Rhena-side PR now takes its diff from `rhineland.contract.json` directly.

### Updated `widths.json` (in the font project)

After Rhena accepts the proposed changes, `src/widths.json` in this project updates to match:

```json
{
  "rh_virga": 90,
  "rh_liquescent_asc": 160,
  "rh_liquescent_desc": 160
}
```

(All other entries unchanged.)

### Rhena-side snapshot update

After widths change in `rhineland.rs`, running `just check` in Rhena will churn diplomatic-mode golden snapshots. Each churned snapshot MUST be visually reviewed against the Dendermonde reference (`docs/research/images/o_ecclesia_rhineland_line_01.png`). Expected diff is small (only neumes using virga or liquescents move).

---

## 5. Redraw guidance (v1 UFO3 authoring)

Fold these observations into the drawing brief at `docs/paleographic_drawing_briefs.md`:

1. **`rh_virga` (§ 2.1)**: after the width increase to 90, the foot has room to extend further right. Alternatively, keep advance at 65 and draw a shorter, calligraphically more honest foot hook — a small right-turning ductus mark, not the wide triangular flap of the current abandoned path.
2. **`rh_liquescent_asc`, `rh_liquescent_desc` (§§ 2.2–2.3)**: close the tail subpath in UFO3 so it renders as an explicit closed stroke. Two-boundary calligraphic tail tapering from ~30 em-units at base to ~10 em-units at tip.
3. **`rh_quilisma` (§ 2.4)**: centre the body on origin. Current path has x ∈ [-50, +120]; after redraw, x ∈ [-85, +85]. Advance unchanged.
4. **`rh_pressus` (§ 2.6)**: total redraw. Follow the drawing brief's "vertical line attached to a short undulating line" specification. Preserve advance 300 provisionally; re-verify after the shape is correct.
5. **`rh_f_clef` (§ 2.7)**: add the two missing dots flanking the upper bar. Place in x ≈ [140, 160], y ≈ upper-bar level ± small offset.
6. **`rh_pes_line` (§ 2.5)**: shift x values so body is at [0, +12] (LSB-0), matching the other connector `rh_flexa_line`.

---

## 6. Deferred to v2

- Full origin-convention unification (all 19 glyphs → LSB-0). Architectural change; needs its own ADR in the font project AND a Rhena-side ADR AND a full golden-snapshot pass. Estimated effort: 1–2 days plus review cycles.
- Re-derivation of all advance widths from musicological principles (current widths are inherited from the abandoned attempt, not derived from pen-width + interval spacing first principles).
- Visual PNG overlay rendering per the review's original recommendation (advance-width bbox over actual rendered glyph). The text-based analysis in this document is a cheaper first pass; PNG overlays can follow if the width-change PR surfaces visual issues.

---

## 7. Proposed workflow for this pass

1. Review this document + the corrected widths in `docs/rhena-coordination/rhineland.contract.json` (previously staged separately as `widths_proposed.json`; merged 2026-04-19) with the Rhena maintainer.
2. Rhena opens a PR that:
   - Updates `crates/rhena-core/src/render_ir/glyphs/rhineland.rs` with the three proposed width changes (this is a temporary edit to the abandoned file; it will be replaced entirely when the real font ships, but the intermediate correct state is needed for snapshot stability).
   - Runs `cargo test` and accepts the diplomatic-mode snapshot diffs after visual review.
   - Lands as one commit.
3. This font project updates `src/widths.json` to match the post-PR Rhena values.
4. ADR-0005 (`Width freeze scope for v1`) status changes from "Accepted" (provisional policy) to a follow-up note: "Widths frozen at post-review values."
5. Drawing phase unblocked.

Estimated total effort: 1 hour of Rhena maintainer time (read + PR + visual review), plus 5 minutes on the font-project side to update `widths.json`.

---

## 8. Source

This analysis read the path strings from `/Users/xaviermac/Documents/2_Areas/Coding-Projects/hildegard/crates/rhena-core/src/render_ir/glyphs/rhineland.rs` as committed at 2026-04-14. If that file has been modified since (either as part of Rhena's backend-hardening pass or as a result of this document's recommendations), re-run the bbox analysis before trusting the tables in § 1.

The author of this document is the font-project Claude instance; the review was invited by the Rhena-project Claude instance at `docs/planning/claude-review-2026-04-14.md` § 5.
