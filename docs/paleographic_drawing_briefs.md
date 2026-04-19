# Paleographic Drawing Briefs

Status: v1, 2026-04-14.
Scope: per-glyph authoring briefs for the 19 Rhineland atoms. Written to guide a font designer opening FontForge (or any UFO3-aware tool) for the first time. Based on direct reading of the Dendermonde Cod. 9 fol. 168v reference captures at `hildegard/docs/research/images/` and the paleographic scholarship in `research_synthesis.md` + `research_v2_findings.md`.

See also:
- `glyph_priority_sheet.md` — drawing order (MVP → full v1)
- `docs/adr/ADR-0001-source-format.md` — UFO3 source format
- `docs/adr/ADR-0004-determinism.md` — coordinate/path normalization constraints
- `docs/adr/ADR-0005-width-freeze-scope.md` — advance-width provisional freeze
- `docs/adr/ADR-0008-paleographic-fidelity-policy.md` — source arbitration

---

## Image reading notes

### `o_ecclesia_rhineland_line_01.png` — Dendermonde fol. 168v, line 1

The line opens with a large decorative red capital "O" followed by the Rhineland C clef on the second line of the staff — a small horizontal bar with a compact curled C hanging below it, sitting just left of centre. Above the word *ecclesia* the characteristic Rhineland neumation: a tall thin virga rising well above the top staff line, then a pair of angular punctum-inclinatum diamonds trailing down and right (the climacus), then a low compact quilisma (wavy mark), a pressus-like cluster with a vertical stroke joined to a short horizontal wave, and several isolated puncta sitting on the staff lines. The marks are all drawn in brown iron-gall ink. Every shape is **light** — the strokes are thin, fluid, and calligraphic, not the thick square noteheads of later square notation. The virga is a single gesture, not a head+stem construct. The puncta are small diagonal dashes, not rectangles. Pen-pressure variation is visible in each stroke: thicker where the nib is fully loaded, thinner where it lifts. The staff is a four-line drypoint/red staff spanning roughly one third of the image height, with baseline text beneath in a Caroline minuscule hand.

### `o_ecclesia_rhineland_line_02.png` — line 2

Same stroke register. The line shows *et aures tue monti bethel et nasus tuus e[st]*. Several distinct neume types: isolated puncta (small angular dashes touching staff lines), a clear pes (two puncta joined by an ascending thin diagonal — lower note noticeably left of and below the upper, with a thin hairline between them), a descending sequence of three or four inclined diamonds (a climacus), and a couple of compact wavy shapes that are either oriscus or quilisma inside larger neumes. Everything is compact, tilted at roughly 25–30°, and drawn with a narrow nib whose angle is constant throughout the line. No clef on this line — staff continues from line 1.

### `punctum.png`

An isolated single punctum, centred on what appears to be the second staff line. The shape is a tiny tilted lozenge or flattened parallelogram — roughly twice as wide as tall. The top-left edge shows the crisp entry of the nib; the bottom-right shows a small tail or hairline where the pen lifted. **Not** a square filled block — a calligraphic dash made by a broad-nib pen pressed at ~30° above horizontal and drawn diagonally downward-right for ~a quarter of a staff space. The mass concentrates in a roughly diamond body with softened (but not fully rounded) corners.

### `virda.png` (the virga reference; filename typo)

A tall, narrow vertical stroke extending from above the top staff line down to roughly the middle of the staff. The stroke begins at the top with a small **head** — a brief thickening or flag-like triangle tipping slightly to the right, like the head of a flagged quarter note but thinner and more calligraphic. From that head a thin stem descends straight down. At the bottom: a small angular **foot** — the stroke widens or hooks very slightly to the right before terminating. The whole gesture is continuous: one pen movement, not two. The top head is the darkest/thickest part; the stem is a uniform thin line; the foot is a small calligraphic ductus mark. Total height ~3 staff spaces.

### `flexa.png`

A single compact gesture that reads as a small hook or comma lying on its side, at the top of the staff. Starts with a thickened head at upper-left (like the virga head), then turns downward and rightward in a gentle arc, tapering. The whole shape is ~1.3× wider than tall and occupies 1–1.5 staff spaces. It's a single-stroke clivis-head — a high note that dips. No second note drawn separately; the descending motion is implied by the curve of the stroke itself.

### `climacus.png`

A vertical virga-like stroke at the top-left, followed to its right and below by two (possibly three) small diagonal diamond marks stepping downward and rightward. The diamonds are noticeably smaller than an isolated punctum — perhaps half the mass. Each diamond sits at a different staff pitch, cascading. Spacing ~one staff-space diagonally. Visual rhythm: TALL stroke, tiny dot, tiny dot, tiny dot, each one lower and further right.

### `climacus_flat.png`

Similar construction but flatter slope — shorter virga, more gradual descent. Confirms that the inclinatum diamond is reusable: the scribe draws the same tiny lozenge regardless of slope, and slope is determined by placement on the staff.

### `quilisma.png`

A small, low-contrast wavy mark. Two or three gentle undulations — NOT a sharp saw-tooth, more like a loose "mm" or a compressed series of tiny humps. ~1.3× wider than tall. Peaks are soft calligraphic humps, not sharp angular points. The mark is heavy at its midline; peaks barely rise above. Very different from geometric sawtooth rendering.

### `quilisma+pressus.png`

A wavy quilisma-like shape on the left flows directly into a vertical-plus-undulation pressus form on the right — the pen never lifts. Confirms Gardiner's description: *"a vertical line attached to a short undulating line"*. The vertical is short (~1 staff space), the undulation at its base or side is small and compact.

### `pressus.png`

Compact mark with two clearly distinct parts: (1) short vertical or near-vertical stroke, (2) a small horizontal wavy hook attached to its top or side. Vertical ~1–1.5 staff spaces tall; wave ~half the vertical's height in horizontal reach. Squat and dense compared to the quilisma, which is all undulation and no vertical.

### `c_clef.png`

A small horizontal dash (the "pitch indicator tick") at the top, and directly below it a thick curled C-shape — open side facing right. The C is a single continuous stroke with pen-angle-driven thick/thin contrast: thickest along the left-side vertical, thinning around top and bottom curves. Total height ~2 staff spaces. The dash is ~1/3 the width of the C. Not two separate strokes glued together — a pen-rest / pitch marker written first, with the C under it.

### `pes_long.png` / `pes_short.png`

Two pitches connected by a thin diagonal: a small punctum/foot-mark at the bottom-left, a thin straight stroke rising up and slightly right, and a second mark (small flag or head) at the top. The ascending line is noticeably thinner than the punctum. `pes_long` spans ~3 staff spaces, `pes_short` ~1. Confirms the pes is a **composite** neume: punctum + thin line + virga/head. The scribe draws each part separately but spacing is tight.

### `o_ecclesia_modern_line_01.png` / line 02

Modern transcription by Beverly Lomer for pitch reference. Labels above the staff in line 1 read: `pes, flexa, v, climacus, v, p, quilisma, flexa, v, p, v, pressus, p, v, pes, climacus`. Line 2: `pes, v, p, v, v, pressus, p, p, quilisma & pressus, pes, v, pes, flexa, v, v, v`. Confirms quilisma, pressus, pes, flexa, virga, punctum are the high-frequency atoms; climacus appears but less often.

### `Hildegard_of_Bingen_Symphonia_Neume_Transcription_Chart.jpg`

Comprehensive table by Beverly Lomer (ISHvBS), reproduced in Gardiner 2022 as Fig. 4. Each neume name paired with its pitch-content interpretation: virga, climacus, punctum, scandicus, pes, pes flexa, flexa, flexa resupina, apostropha, bistropha, tristropha, epiphonus, cephalicus, pes liquescens, pes flexa liquescens, pressus, pressus liquescens, quilisma, quilisma perpressa, flexa resupina + subpunctis, flexa torpia + pressus liquescens, pes + cephalicus, flexa + pes, quilisma + pressus, quilisma + pressus liquescens. This chart is the pitch-content Rosetta stone, **not** a paleographic model — the noteheads in it are modern ovals, not Rhineland calligraphy — but it confirms which compound neumes Rhena must render from the 19 atoms.

---

## Stroke register (common to all atoms)

Twelfth-century German square-ish notation, "between St Gall and Hufnagelschrift" (van Poucke via Gardiner pp. 25–26). The scribe writes with a narrow, rectangular-cut quill nib held at a **constant angle of approximately 25–35° above horizontal** (the conventional Caroline/Rhenish writing angle). This constant angle produces a consistent thick-thin contrast:

- Strokes from upper-left to lower-right: thick (full nib width)
- Strokes from lower-left to upper-right: thin (corner of the nib)
- Vertical strokes: intermediate thickness

Every glyph in this font MUST respect this single pen angle. Visualize a rectangular nib ~60 em-units wide rotated ~28° counter-clockwise, and imagine dragging it along each stroke's path — the resulting mark IS the glyph outline.

**Round, not square.** The marks are calligraphic, not typographic. NOT square notation (no filled rectangular noteheads). NOT 13th-century Hufnagelschrift (no thick rhomboid "nail-head" virga). NOT the hair-thin gestural St Gall adiastematic neumes (those have no heightness and no body). **Rounder than Hufnagel, heavier than St Gall** — every stroke has visible body (you can see the nib's footprint), but the body is shaped organically by the pen's motion, with slightly curved top and bottom edges.

**Liquescents lighter.** Following Gardiner p. 92, liquescent forms are *"rounded off, lighter stroke"* — the nib is lifted slightly, producing a thinner, more rapid mark. In em-unit terms, liquescent strokes should be ~70% of the nib thickness of the main atoms. Tails curve organically (not geometric arcs) and taper off at termination.

**Origin is the pitch anchor, not the bottom of the glyph.** For a Rhineland font where pitch is conveyed by vertical offset at layout time, each atom's (0, 0) origin should sit at its visual pitch anchor — the vertical centre of the note's "musical meaning". For a punctum, that's the centre of its body. For a virga, that's the centre of its HEAD (which is the pitched element), NOT the bottom of its foot. The stem descends BELOW (0, 0). This matches Bravura-style SMuFL convention and makes layout math trivial.

---

## Per-glyph briefs

### 1. `rh_punctum` (width 240)

- **Reference**: `punctum.png`; isolated puncta in `o_ecclesia_rhineland_line_01.png`. Small tilted calligraphic lozenge, ~2× wider than tall, crisp nib entry at upper-left, slight tail at lower-right.
- **Shape**: calligraphic parallelogram-lozenge. Nib (~75 em-units) pressed at ~28° and drawn ~80 em-units to the lower-right. Thick diagonal body, two long parallel edges (top-left and bottom-right) running at the pen angle, two short blunt edges (left and right) where the nib started/ended. Corners **slightly** softened by ink spread — not sharp, not rounded circles. Upper edge very subtly concave, lower edge very subtly convex, giving a soft leaf-like swell.
- **Stroke register**: one pen-stroke, full nib pressure throughout, no tapering. Nib angle 28°, nib width ~75 em-units. Darkest glyph in the font alongside virga head and pressus vertical.
- **Key features**: (1) Tilted body — long axis runs upper-left to lower-right at the pen angle; (2) blunt short edges (not pointed diamond tips — left/right ends are flat corners of the nib); (3) softened, organically-swelling long edges.
- **Proportions**: width 240 em-units, height ~130 em-units. Body ~220×110 with 10 units of ink bleed on each side.
- **Registration**: centred on origin. Bounding box ~(-120, -65) to (+120, +65). Pitch anchor = geometric centre of body.
- **NOT**: square filled rectangle (square notation); sharp four-pointed diamond (that's the inclinatum, #3); ellipse or oval (modern notation); rigid straight edges.

### 2. `rh_virga` (width 90)

- **Reference**: `virda.png` (filename typo, this IS the virga); virga instances throughout `o_ecclesia_rhineland_line_01.png`. Tall thin vertical pen stroke with small head at top, long thin stem, small angular foot at bottom curving slightly right. One continuous gesture.
- **Shape**: three joined segments drawn with one pen motion.
  - **Top — HEAD**: small calligraphic flag ~60–80 em-units tall. Starts at upper-left, pulls down and very slightly right, forming a little flag or triangular cap. The pitch-bearing mark.
  - **Middle — STEM**: from the head's lower-right corner, a thin near-vertical stem descends ~500 em-units, tapering just a hair thinner as it goes. ~3–5° right lean.
  - **Bottom — FOOT**: pen turns rightward and slightly downward for ~40 em-units, creating a tiny angular hook, then terminates. Not a flat serif, not a sharp point — a calligraphic ductus finish with a blunt-ish end.
- **Stroke register**: head: full nib, dark, ~75-unit nib at 28°. Stem: narrow, ~18–22 em-units wide (vertical strokes hit the nib across its narrow axis). Foot: brief return to fuller weight as the pen rotates into the ductus finish. Head:stem:foot thick-thin contrast ~4:1:3.
- **Key features**: (1) Single continuous gesture — head, stem, foot must feel like one pen movement; (2) distinct HEAD flag at top (distinguishes virga from a divisio bar); (3) FOOT hooks right — the "angular foot extension", distinguishes Rhineland from footless Metz-style.
- **Proportions**: width 90 em-units (post-review width; head is widest component), total height ~620 (head 80 + stem 500 + foot 40).
- **Registration**: origin (0, 0) at the centre of the HEAD, NOT the bottom of the foot. Head spans ~(-20, -40) to (+45, +40). Stem runs from (0, -40) down to (0, -540). Foot extends to ~(+40, -560). Pitch anchor = head.
- **NOT**: thick rectangular nail-head Hufnagel virga (13th-century, too heavy); stem with no head (that's a divisio bar); symmetric flag (the head leans right); foot as a flat horizontal serif (it's an angular hook, same pen motion as the stem).

### 3. `rh_punctum_inclinatum` (width 120)

- **Reference**: `climacus.png`, `climacus_flat.png`. Small tilted diamonds cascading down-right, noticeably smaller (~50% mass) than isolated puncta, with sharper corners.
- **Shape**: small four-pointed tilted diamond. Unlike the punctum (blunt-ended parallelogram), the inclinatum has **sharper points** at its left and right extremes because the nib enters and exits with a lift. Top-left and bottom-right edges run at the pen angle (~28°); left and right points are sharper. Aspect: width ~1.8× height.
- **Stroke register**: one short pen stroke with nib lift-in and lift-out (creating pointed ends). Nib at 28°, nib width ~55 em-units.
- **Key features**: (1) Small — ~half the visual mass of `rh_punctum`, so cascading groups feel light and dot-like; (2) sharper diamond points (especially left/right) vs punctum's blunt edges; (3) consistent shape regardless of slope (scribe draws the same mark; pitch from staff position).
- **Proportions**: width 120, height ~90.
- **Registration**: centred on origin. Bounding box (-60, -45) to (+60, +45).
- **NOT**: miniature `rh_punctum` (sharper points, not blunt); square-notation lozenge (no rigid straight edges); large (distinctly smaller than punctum).

### 4. `rh_quilisma` (width 170)

- **Reference**: `quilisma.png`, `quilisma+pressus.png`, the quilisma above "oculi tui" in line 1. Small low-contrast wavy mark with 2–3 gentle undulations — NOT sharp saw-tooth, soft compressed "mm"-like shape with rounded calligraphic humps, ~1.3× wider than tall, sitting heavy at its midline.
- **Shape**: short horizontal calligraphic stroke that the scribe undulates as they draw it. Pen enters at the left at baseline, rises in a small rounded hump, returns to baseline, rises in a second hump, returns, and optionally rises in a third smaller hump before exiting at the right. Humps are **soft and rounded** — NOT sharp V-shaped teeth. Compact, like a tiny cursive "w" upside-down. First and last humps slightly larger than the middle. **Wide and short** (aspect ~3:1 or 4:1 — flatter than a naive reading suggests).
- **Stroke register**: one continuous pen motion with subtle pressure modulation at each hump peak. Nib at 28°, nib width ~50 em-units (lighter than punctum). Ink mass concentrated along a horizontal band; hump peaks show slightly lighter stroke because the pen moves faster at each apex.
- **Key features**: (1) **Soft rounded undulations** — curved calligraphic humps, not sharp angular saw-teeth; (2) WIDE and SHORT aspect ratio; (3) 2–3 clearly distinguishable undulations visible at rendered scale.
- **Proportions**: width 170, height ~60 (flat!). Hump amplitude ~25 above/below a midline at origin.
- **Registration**: centred on origin. Bounding box ~(-85, -30) to (+85, +30). Pitch anchor = horizontal midline.
- **NOT**: three pointed sharp teeth (wrong — real quilisma has rounded humps); Solesmes three-lobed rising flourish (chant-book, not Rhineland); tall (it's flat and compact); uniform sine wave (humps are asymmetric and calligraphic).

### 5. `rh_oriscus` (width 200)

- **Reference**: no dedicated image. Gardiner pp. 93–94: *"a small note, similar to a punctum or apostropha, that has a wavy component"*. Cross-reference `quilisma+pressus.png` for the wavy vocabulary.
- **Shape**: small compact mark with TWO components: (1) a slightly flattened punctum-like body on the LEFT, and (2) a small wavy S-curve or single-hump tail extending to the RIGHT. A punctum that ended with a quick flick into a small rightward undulation. Body ~2/3 of total width, wavy tail ~1/3. Unlike quilisma (all undulation, no body), oriscus has a clear dense body with only a small wavy affix. One pen motion.
- **Stroke register**: body at full nib pressure as for punctum. Tail at lightening pressure. Nib at 28°, nib width ~60 em-units.
- **Key features**: (1) Distinct solid body (unlike quilisma's all-wave); (2) wavy component is small and subordinate — a single S-curve or hump, not multiple undulations; (3) wave on the RIGHT (trailing edge), not surrounding.
- **Proportions**: width 200, height ~90. Body ~130 wide, tail ~70 wide, tail amplitude ~30 above/below body centreline.
- **Registration**: centred on origin. Bounding box ~(-100, -45) to (+100, +45). Pitch anchor = centre of body (left half of glyph).
- **NOT**: full horizontal S or figure-eight (pure wave with no body); as tall as virga (single-note mark); quilisma's multi-hump form (oriscus has ONE body and ONE wave).

### 6. `rh_strophicus` (width 160)

- **Reference**: no dedicated image. Extrapolate from isolated puncta in O Ecclesia lines 1–2 plus the Beverly Lomer chart (apostropha/bistropha/tristropha rows). In Rhena, apostropha/bistropha/tristropha all collapse to this atom.
- **Shape**: small angular calligraphic mark similar to `rh_punctum` but with a slight hook or upturned flick at one end to distinguish it visually. A punctum whose right end doesn't blunt-end but tapers up into a tiny rightward flick. Body is a tilted parallelogram; flick is a small tapering tail. Smaller than punctum (160 vs 240) and slightly denser.
- **Stroke register**: one short pen-stroke with a quick pressure lift at the end. Nib at 28°, nib width ~55 em-units. Flick is the lightest part.
- **Key features**: (1) **Smaller than `rh_punctum`** — strophic groups read as lighter dots; (2) **asymmetric** — one end (right/top) has a small flick, the other is blunt; (3) angular, not wavy — NOT an oriscus or quilisma.
- **Proportions**: width 160, height ~100. Body ~130×90, flick tail ~30×20.
- **Registration**: centred on origin. Bounding box ~(-80, -50) to (+80, +50). Pitch anchor = centre of body.
- **NOT**: three separate marks (Rhena stamps multiple copies for bi/tristropha); identical to punctum or inclinatum (needs its own identity via flick); large/curly flick (it's a tiny pen-lift).

### 7. `rh_pressus` (width 300)

- **Reference**: `pressus.png`, `quilisma+pressus.png`. Gardiner p. 94: *"a vertical line attached to a short undulating line"*.
- **Shape**: TWO clearly distinct joined components:
  - **VERTICAL**: thin calligraphic line ~180–220 em-units tall, on the left side
  - **HORIZONTAL WAVE**: single S-curve or pair of small humps, ~140 em-units wide, joined to the upper portion of the vertical
  Vertical placed LEFT of centre; wave runs to the RIGHT from the top of the vertical. Like a lowercase "r" where the stem is short and the shoulder is a wave. One continuous pen motion from the bottom of the vertical up through its top and out into the wave.
- **Stroke register**: vertical ~25-unit nib width (vertical hits nib's narrow axis). Wave ~40-unit nib width with pressure modulation at the humps.
- **Key features**: (1) **Vertical + wave split** — the distinguishing feature; unique in combining a clear vertical with a compact undulation; (2) vertical is SHORT (not a virga — no head, no foot, ~1 staff space tall); (3) wave is compact — 1–2 humps, not a long ripple.
- **Proportions**: width 300, total height ~280. Vertical ~25×220 at x≈-100. Wave ~180×70 at ~(+20, +80).
- **Registration**: origin at the junction where vertical meets wave (upper portion of the vertical). Bounding box ~(-110, -200) to (+190, +80). Pitch anchor = top of vertical where the wave joins.
- **NOT**: a wider punctum (the abandoned attempt was wrong — no vertical, no wave); a virga with a wave (vertical much shorter than a virga, no head, no foot); big or ornate wave (small flourish).

### 8. `rh_liquescent_asc` (width 160)

- **Reference**: no dedicated image. Gardiner p. 92: *"rounded off, lighter stroke"*. Reference family: virga and flexa for how the pen moves, imagined lighter.
- **Shape**: small angular head (like a miniature virga head) at the LOWER-LEFT, then a thin calligraphic tail curving UPWARD and RIGHTWARD from the top of the head. Head is a compact tilted parallelogram ~80×50 em-units. Tail is a smooth arc starting thin (where it leaves the head), curving up-right, tapering even thinner as it rises, terminating at ~(+75, +280). Continuous motion, lighter than solid atoms.
- **Stroke register**: head at medium nib pressure, ~50 em-units nib width. Tail at very light pressure, tapering from ~30 em-units at base to ~10 em-units at tip. Nib angle 28°.
- **Key features**: (1) Head + curved ascending tail — one-gesture compound mark; (2) **LIGHTER stroke** than main atoms (per Gardiner); (3) tail curves organically, not as a geometric arc.
- **Proportions**: width 160 (post-review width), height ~320.
- **Registration**: origin at centre of head. Bounding box ~(-70, -40) to (+80, +280). Pitch anchor = head centre.
- **NOT**: straight geometric line for the tail (must curve organically); head as large as a punctum (smaller to indicate liquescent diminution); dark/full stroke (consistently lighter).

### 9. `rh_liquescent_desc` (width 160)

- **Reference**: Same as ascending but mirrored in spirit. Extrapolate from `flexa.png`.
- **Shape**: small angular head at the UPPER-LEFT and a thin calligraphic tail curving DOWNWARD and RIGHTWARD from the bottom of the head. Same compact tilted parallelogram head (~80×50). Tail starts thin and tapers as it descends, curving right and down, terminating at ~(+75, -280).
- **Stroke register**: same as ascending — lighter, rounder-off stroke per Gardiner.
- **Key features**: (1) Head + curved descending tail (mirror of asc); (2) organic downward curve; (3) same lighter weight.
- **Proportions**: width 160 (post-review width), height ~320.
- **Registration**: origin at centre of head. Bounding box ~(-70, -280) to (+80, +40). Pitch anchor = head centre (STARTING pitch of the liquescent).
- **NOT**: simple vertical reflection of ascending (head orientation should subtly reflect the descending pen direction); straight; dark.

### 10. `rh_deminutum` (width 100)

- **Reference**: no dedicated image. Extrapolate from smaller marks following larger neumes in O Ecclesia and from `rh_punctum_inclinatum` (shares mass).
- **Shape**: very small, compact angular mark — smaller than both `rh_punctum` and `rh_punctum_inclinatum`. A miniature tilted lozenge at ~70% the size of the inclinatum, same calligraphic pen-angle body but no distinguishing features beyond its smallness. Used for diminutive-liquescent positions where the note is reduced to near-nothing.
- **Stroke register**: one brief pen touch with a small drag. Nib at 28°, nib width ~40 em-units. Light pressure.
- **Key features**: (1) **Smallest** of the note atoms — clearly tinier than inclinatum; (2) simple lozenge (no flick, no tail, no wave); (3) lighter stroke (like liquescents).
- **Proportions**: width 100, height ~70.
- **Registration**: centred on origin. Bounding box (-50, -35) to (+50, +35).
- **NOT**: same size as inclinatum (smaller); with a tail or flick (simplest possible dot-like mark); so small it disappears.

### 11. `rh_c_clef` (width 110)

- **Reference**: `c_clef.png` + the clef at the start of `o_ecclesia_rhineland_line_01.png`. Small horizontal dash at top, thick calligraphic C below, open side facing right, single continuous pen motion per component with clear thick-thin contrast.
- **Shape**: two stacked components:
  - **DASH** at top: short thickened calligraphic bar ~90 em-units wide and ~20 em-units thick, slightly tilted with the pen angle.
  - **C** directly below: single continuous pen stroke that begins at the upper-right, curves up and around to the left forming the top of the C, turns down along the left side (**thickest part** — nib fully on), curves around the bottom, exits at the lower-right. Opening faces right. Total C height ~400 em-units (~2 staff spaces). Dash sits just above the C, aligned with its left-right midpoint.
- **Stroke register**: dash at full nib pressure, one quick drag. C at single continuous stroke with characteristic broad-nib thick-thin contrast — thick on the left vertical, thin at top/bottom curves. Nib ~75 em-units.
- **Key features**: (1) Two-part construction (dash + C) — what makes it recognisable as a clef; (2) C opens **RIGHT** (scribe's convention for "this line is C"); (3) calligraphic thick-thin contrast on the C — NOT a uniform outline stroke.
- **Proportions**: width 110, total height ~500 (dash 20 + gap 60 + C 420).
- **Registration**: origin at the geometric centre of the C body (NOT the top or the dash) — where the clef designates its pitch (middle C). Bounding box ~(0, -210) to (+110, +290). X-origin at left edge for left-aligned placement.
- **NOT**: modern treble/alto-style ornate clef (15th-century+); filled semicircle C (must be a calligraphic stroke with visible thick-thin contrast); omit the dash (part of the Rhineland C clef identity).

### 12. `rh_f_clef` (width 160)

- **Reference**: no dedicated image — not used in O Ecclesia. Extrapolate from Riesencodex F-clef conventions and the C clef's calligraphic register.
- **Shape**: calligraphic F — short vertical stroke on the left with two small horizontal bars extending to the right. Upper bar longer and thicker (the "top of the F"); lower bar shorter, at mid-height. Both bars drawn with the same nib angle, showing thick-thin contrast. To the RIGHT of the upper bar, two small dots or punctum-like marks — the "F-clef dots" flanking the staff line designating F. Compact.
- **Stroke register**: vertical ~25-unit nib width. Bars ~35-unit nib width. Dots as small full-pressure punctums. Nib at 28° throughout.
- **Key features**: (1) Vertical + two horizontal bars — distinctly F-shaped; (2) two small dots flanking the upper bar on the right — traditional F-clef markers; (3) compact and calligraphic, matching the C clef's weight.
- **Proportions**: width 160, total height ~500.
- **Registration**: origin at the F line level — Y-coordinate of the upper horizontal bar (since that bar designates F). Bounding box ~(0, -250) to (+160, +250).
- **NOT**: modern bass clef stylisation; omit the dots; larger than the C clef (balanced as a clef family). If unclear, fall back to a simple geometric form (acceptable stopgap).

### Geometric glyphs §§ 13–19 — SMuFL-aligned conventions

Per **ADR-0009** (SMuFL alignment for tradition-agnostic glyphs, 2026-04-19): divisio family and virgula adopt Bravura's SMuFL conventions exactly — widths, heights, and **path-intrinsic y-positioning**. Compositional primitives (`rh_pes_line`, `rh_flexa_line`) have no SMuFL equivalent and keep their own conventions for Rhena's resolver. Units are design units (du); 1 staff space = 250 du in our 1000-UPM scale.

### 13. `rh_divisio_minima` (width 16 du)

- **Shape**: thin vertical bar, 16 du wide × 250 du tall (1 staff space).
- **Stroke register**: flat geometric, uniform thickness.
- **Key features**: (1) Shortest of the divisio family; (2) positioned **above the staff** (SMuFL y ∈ [+250, +500] = staff spaces [+1.0, +2.0]); (3) same thickness as maior/maxima (16 du).
- **Registration**: bbox (0, +250) to (+16, +500). Path-intrinsic y: the outline carries its SMuFL placement, no per-consumer transform needed.
- **NOT**: centred on staff midline (that's maior); touching or crossing the staff lines; as tall as maior.

### 14. `rh_divisio_maior` (width 16 du)

- **Shape**: thin vertical bar, 16 × 500 du (2 staff spaces).
- **Stroke register**: flat geometric.
- **Key features**: centred on staff midline (SMuFL y ∈ [-250, +250] = staff spaces [-1.0, +1.0]); same thickness as minima/maxima.
- **Registration**: bbox (0, -250) to (+16, +250). Path-intrinsic y.
- **NOT**: extending past the staff (that's maxima); as short as minima; above the staff (that's minima).

### 15. `rh_divisio_maxima` (width 16 du)

- **Shape**: thin vertical bar, 16 × 750 du (3 staff spaces).
- **Stroke register**: flat geometric.
- **Key features**: tallest single-bar divisio; extends slightly past standard staff bounds (SMuFL y ∈ [-375, +375] = staff spaces [-1.5, +1.5]); same thickness as minima/maior.
- **Registration**: bbox (0, -375) to (+16, +375). Path-intrinsic y.
- **NOT**: conflate with divisio_finalis (which has TWO bars; maxima has ONE).

### 16. `rh_divisio_finalis` (width 120 du)

- **Shape**: **two** 16-du-wide vertical bars separated by an 88-du gap (total 120 du wide), each 750 du tall (3 staff spaces). Left bar at x ∈ [0, 16]; right bar at x ∈ [104, 120].
- **Stroke register**: flat geometric.
- **Key features**: (1) **TWO bars** — defining feature; (2) both bars equal thickness (no modern "thick-thin" convention — this is chant finalis); (3) same height as maxima; (4) wide enough gap to be visually distinct from maxima.
- **Registration**: bbox (0, -375) to (+120, +375). Path-intrinsic y matches divisio_maxima.
- **NOT**: one bar thicker than the other (modern "final" bar convention); narrower than Bravura (we match SMuFL exactly — 120 du total, 88 du gap).

### 17. `rh_virgula` (width 91 du)

- **Shape**: breath mark above the top staff line. Placeholder is a 91 × 245 du rectangle; final shape may be a calligraphic hook (Bravura ships a curvy hook at this bbox). For v1 the rectangle is good enough for SMuFL-compatible positioning; Phase C can refine if Rhineland manuscripts attest a distinct virgula shape.
- **Stroke register**: flat geometric (placeholder); optionally calligraphic hook in Phase C if manuscript evidence warrants.
- **Key features**: (1) **above the staff** (SMuFL y ∈ [+255, +500]); (2) 91 du wide (matches Bravura chantVirgula); (3) a breath mark, not a phrase break.
- **Registration**: bbox (0, +255) to (+91, +500). Path-intrinsic y.
- **NOT**: spanning the staff; as thin as the 12-du hairline it used to be in the abandoned `rhineland.rs` (written off per ADR-0009).

### 18. `rh_pes_line` (width 12 du)

- **Shape**: thin vertical rectangle, 12 du wide × 250 du tall (1 staff space). LSB-0.
- **Stroke register**: geometric hairline, uniform thickness.
- **Key features**: (1) thin (12 du); (2) drawn vertical in the source; (3) no heads or feet — pure connector. Rhena's resolver rotates/scales this at render time to span whatever interval the pes covers.
- **Registration**: bbox (0, 0) to (+12, +250). No SMuFL equivalent — this is a compositional primitive; Rhena-internal convention applies.
- **NOT**: heads or feet (those are separate atoms); calligraphic; pre-rotated (the resolver handles rotation).

### 19. `rh_flexa_line` (width 172 du)

- **Shape**: descending diagonal parallelogram, 172 du wide × 260 du tall, 12 du thick. Top edge at y=0 spanning x ∈ [0, 12]; bottom edge at y=-260 spanning x ∈ [160, 172].
- **Stroke register**: geometric hairline, uniform thickness. Matches pes_line in weight.
- **Key features**: (1) **DIAGONAL** (unlike pes_line which is vertical); (2) descends left-to-right (reflects the flexa's downward motion); (3) thin hairline weight.
- **Registration**: bbox (0, -260) to (+172, 0). No SMuFL equivalent — compositional primitive; Rhena-internal convention.
- **NOT**: vertical (that's pes_line); with heads (heads are separate atoms); calligraphic (hairline).

---

## Drawing-order priority (condensed)

See `glyph_priority_sheet.md` at the project root for the full tier breakdown. Summary:

- **Tier 1 — MVP** (6 glyphs): `rh_punctum`, `rh_virga`, `rh_c_clef`, `rh_punctum_inclinatum`, `rh_quilisma`, `rh_pressus`. Targets O Ecclesia line 1 validation.
- **Tier 2 — O Ecclesia full coverage** (6 glyphs): `rh_oriscus`, `rh_strophicus`, `rh_liquescent_asc`, `rh_liquescent_desc`, `rh_pes_line`, `rh_flexa_line`.
- **Tier 3 — Structural + auxiliary** (7 glyphs): `rh_divisio_minima/maior/maxima/finalis`, `rh_virgula`, `rh_deminutum`, `rh_f_clef`.
