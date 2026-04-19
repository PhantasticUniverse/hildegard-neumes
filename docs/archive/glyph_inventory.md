# Rhineland / Hildegard Neume Glyph Inventory — v0.4

Primary scope for this phase:

* **Hildegard first**
* preserve the chart labels for traceability
* separate **family meaning** from **chart instance**
* add a **Gregorio/gabc-style construction layer**
* prepare the inventory for actual font decisions
* keep western staff notation out of the naming logic, except where it helps count notes in the chart examples

---

## 1. Hildegard-focused working rules

### Rule 1 — separate family from instance

A label like `pes` names a **family**, not one exact vertical shape.

So we now track two different things:

* **Family cardinality** = what the neume type does in principle
* **Chart exemplar cardinality** = how many notes the supplied chart example happens to show

Example:

* `climacus` = family with variable descending length
* the chart’s `climacus` example = one specific 4-note instance

### Rule 2 — think in staff steps / ambitus, not semitones

For font planning, what matters is vertical span and attachment behavior.

So a neume should be described by:

* contour
* whether it repeats a pitch
* whether its span is variable
* whether its length is fixed or variable

### Rule 3 — not every chart row should become one final glyph

Some chart rows are really:

* true atomic signs
* true neume families
* modified families
* or **composite sequences shown as examples**

Those need to be distinguished before font production.

### Rule 4 — Hildegard needs both semantic and graphic labeling

For Hildegard’s notation, some forms are best treated as:

* semantic family names for the inventory
* graphic components for the font
* and specific chart exemplars for testing

### Rule 5 — add a Gregorio/gabc-style constructor layer

Gregorio/gabc does not begin from a giant inventory of final multinote glyphs. It begins from:

* pitch positions
* note sequences
* special modifiers
* contextual joining behavior

So this inventory now adds:

* **constructor / recipe**
* **pitch-relation pattern**
* **atomic parts used**
* **contextual allograph needs**

This does **not** mean copying square-notation assumptions wholesale. It means borrowing the useful abstraction:

* family first
* construction logic second
* final drawing third

---

## 2. What the type labels mean

### Atomic sign

The smallest reusable graphic sign in the system.

Examples:

* punctum
* virga
* apostropha
* quilisma-form

Atomic **does not mean** “theologically basic” or “musically most important.” It means: smallest practical building block for the font.

### Component

A reusable graphic part that may appear inside larger neumes.
A component may also be an atomic sign, but not always.

Examples:

* quilisma component
* liquescent terminal form
* repeated apostropha-based pattern

### Neume family

A named chant category whose instances can be recognized across occurrences.

Examples:

* pes
* flexa
* climacus
* scandicus
* pressus

### Modified family

A family that adds a systematic feature.

Examples:

* liquescent forms
* prepuncto forms
* subpunctis forms

### Repetition family

A family whose identity depends on pitch repetition.

Examples:

* apostropha family
* bistropha
* tristropha
* pressus core behavior

### Composite sequence

A sequence made from already-known families or modified families.
These usually should **not** become one final encoded glyph.

Examples:

* pes + cephalicus
* flexa + pes
* quilisma + pressus

### Chart exemplar

A specific example shown in the supplied chart.
This is useful for note counting and testing, but it is **not automatically** a final font unit.

---

## 3. Recommended core columns for the build sheet

| Field                       | Meaning                                                                                             |
| --------------------------- | --------------------------------------------------------------------------------------------------- |
| ID                          | Stable internal ID                                                                                  |
| Chart label                 | Exact wording from the chart                                                                        |
| Canonical family label      | Clean working name                                                                                  |
| Semantic type               | Atomic sign / component / neume family / modified family / composite sequence                       |
| Contour                     | Single, ascending, descending, repeated, up-down, down-up, ascending chain, descending chain, mixed |
| Family cardinality          | Fixed / Variable / Subtype-dependent                                                                |
| Chart exemplar cardinality  | Number of notes shown in the chart example                                                          |
| Pitch-relation pattern      | Symbolic relation model such as `+`, `-`, `=`, `+-`, `-+`, `= -`                                    |
| Repeated pitch core?        | Yes / No / Partial                                                                                  |
| Variable ambitus?           | Yes / No                                                                                            |
| Modifier                    | None / Liquescent / Prepuncto / Subpunctis / Composite                                              |
| Constructor / recipe        | Plain-language construction rule                                                                    |
| Atomic parts used           | Reusable pieces involved                                                                            |
| Contextual allograph needs? | Yes / No / Maybe                                                                                    |
| Font strategy               | Atomic component / dedicated glyph / assembly / both                                                |
| Confidence                  | High / Medium / Low                                                                                 |
| Review notes                | Manual-check field                                                                                  |

---

## 4. Hildegard-focused inventory table

| ID     | Chart label                          | Canonical family label                | Semantic type                        | Contour                                     | Family cardinality | Chart exemplar cardinality | Pitch-relation pattern           | Repeated pitch core? | Variable ambitus? | Modifier               | Constructor / recipe                                                            | Atomic parts used                                        | Contextual allograph needs? | Font strategy                                       | Confidence | Review notes                                            |
| ------ | ------------------------------------ | ------------------------------------- | ------------------------------------ | ------------------------------------------- | ------------------ | -------------------------: | -------------------------------- | -------------------- | ----------------- | ---------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------- | --------------------------------------------------- | ---------- | ------------------------------------------------------- |
| RN-001 | virga                                | virga                                 | Atomic sign                          | single                                      | Fixed              |                          1 | `•`                              | No                   | No                | None                   | Single note sign                                                                | virga                                                    | No                          | Atomic component / dedicated glyph                  | High       | Core sign                                               |
| RN-002 | climacus                             | climacus                              | Neume family                         | descending chain                            | Variable           |                          4 | `---` exemplar                   | No                   | Yes               | None                   | Start note followed by descending chain of one or more lower notes              | punctum / virga-family descending sequence               | Yes                         | Assembly + possible common precomposed variants     | High       | Chart shows one 4-note exemplar, not whole family       |
| RN-003 | punctum                              | punctum                               | Atomic sign                          | single                                      | Fixed              |                          1 | `•`                              | No                   | No                | None                   | Single note sign                                                                | punctum                                                  | No                          | Atomic component / dedicated glyph                  | High       | Core sign                                               |
| RN-004 | scandicus                            | scandicus                             | Neume family                         | ascending chain                             | Variable           |                          3 | `++` exemplar                    | No                   | Yes               | None                   | Start note followed by ascending chain of one or more higher notes              | punctum / virga-family ascending sequence                | Yes                         | Assembly + possible common precomposed variants     | High       | Chart shows one 3-note exemplar                         |
| RN-005 | pes                                  | pes                                   | Neume family                         | ascending                                   | Fixed              |                          2 | `+`                              | No                   | Yes               | None                   | Two-note ascent                                                                 | lower note + upper note                                  | No / maybe                  | Dedicated glyph and/or controlled assembly          | High       | 2-note ascent with variable span                        |
| RN-006 | pex flexus                           | pes flexus                            | Neume family                         | up-down                                     | Fixed              |                          3 | `+-`                             | No                   | Yes               | None                   | Two-note ascent followed by descent                                             | pes core + descending terminal                           | Yes                         | Dedicated glyph and/or controlled assembly          | Medium     | Chart spelling likely needs manual correction           |
| RN-007 | flexa                                | flexa                                 | Neume family                         | descending                                  | Fixed              |                          2 | `-`                              | No                   | Yes               | None                   | Two-note descent                                                                | upper note + lower note                                  | No / maybe                  | Dedicated glyph and/or controlled assembly          | High       | 2-note descent with variable span                       |
| RN-008 | flexa resupina                       | flexa resupina                        | Neume family                         | down-up                                     | Fixed              |                          3 | `-+`                             | No                   | Yes               | None                   | Two-note descent followed by rebound upward                                     | flexa core + rising terminal                             | Yes                         | Dedicated glyph and/or controlled assembly          | Medium     | Keep chart term for now                                 |
| RN-009 | apostropha                           | apostropha                            | Atomic sign / repetition family seed | single                                      | Fixed              |                          1 | `•`                              | No                   | No                | None                   | Single repeated-style note sign                                                 | apostropha                                               | No                          | Atomic component / dedicated glyph                  | High       | Important for repeated-pitch family logic               |
| RN-010 | bistropha                            | bistropha                             | Repetition family                    | repeated                                    | Fixed              |                          2 | `=`                              | Yes                  | No                | None                   | Same pitch sounded twice                                                        | apostropha repeated twice or dedicated pair form         | Maybe                       | Dedicated glyph or repeated-component build         | High       | Same pitch repeated twice                               |
| RN-011 | tristropha                           | tristropha                            | Repetition family                    | repeated                                    | Fixed              |                          3 | `==`                             | Yes                  | No                | None                   | Same pitch sounded three times                                                  | apostropha repeated three times or dedicated triple form | Maybe                       | Dedicated glyph or repeated-component build         | High       | Same pitch repeated three times                         |
| RN-012 | cephalicus                           | cephalicus                            | Modified family                      | descending                                  | Fixed              |                          2 | `-`                              | No                   | Yes               | Liquescent             | Descending two-note liquescent form                                             | cephalicus-specific head + liquescent terminal           | Yes                         | Dedicated glyph or family-specific alternate        | High       | Descending liquescent-type form                         |
| RN-013 | epiphonus                            | epiphonus                             | Modified family                      | ascending                                   | Fixed              |                          2 | `+`                              | No                   | Yes               | Liquescent             | Ascending two-note liquescent form                                              | epiphonus-specific head + liquescent terminal            | Yes                         | Dedicated glyph or family-specific alternate        | High       | Ascending liquescent-type form                          |
| RN-014 | pes liquesans                        | pes liquescens                        | Modified family                      | up-down                                     | Fixed              |                          3 | `+-`                             | No                   | Yes               | Liquescent             | Pes-like rise with liquescent descent/ending                                    | pes core + liquescent terminal                           | Yes                         | Dedicated glyph or base+liquescent family build     | Medium     | Chart spelling likely needs normalization               |
| RN-015 | pes flexus liquesans                 | pes flexus liquescens                 | Modified family                      | up-down-down                                | Fixed              |                          4 | `+--`                            | No                   | Yes               | Liquescent             | Pes flexus with additional liquescent descent/ending                            | pes flexus core + liquescent terminal                    | Yes                         | Dedicated glyph or base+liquescent family build     | Medium     | Chart spelling likely needs normalization               |
| RN-016 | pressus                              | pressus                               | Neume family / repetition family     | repeated                                    | Subtype-dependent  |                          2 | `=` core                         | Yes                  | No / limited      | None                   | Same pitch twice in succession; may act as core for larger pressus-family forms | repeated note core                                       | Yes                         | Dedicated glyph plus family logic                   | High       | Core idea is same pitch twice in succession             |
| RN-017 | pressus liquesans                    | pressus liquescens                    | Modified family                      | repeated then falling liquescent ending     | Fixed              |                          3 | `=-`                             | Yes                  | Limited           | Liquescent             | Pressus core followed by liquescent terminal descent                            | pressus repeat core + liquescent terminal                | Yes                         | Dedicated glyph or pressus-family build             | Medium     | Chart spelling likely needs normalization               |
| RN-018 | pressus subpunctis                   | pressus subpunctis                    | Modified family                      | repeated then descending tail               | Fixed              |                          3 | `=-`                             | Yes                  | Limited           | Subpunctis             | Pressus core followed by one or more lower puncta                               | pressus repeat core + descending punctum tail            | Yes                         | Dedicated glyph or pressus-family build             | High       | Strong candidate for dedicated handling                 |
| RN-019 | quilisma                             | quilisma                              | Special sign + neume family          | rising / special-form                       | Subtype-dependent  |                          3 | `+` exemplar                     | No                   | Yes               | None                   | Special quilisma note integrated into a rising formation                        | quilisma component + adjoining notes                     | Yes                         | **Both** atomic component and family-level handling | Medium     | Treat as both reusable sign and chart family            |
| RN-020 | quilisma prepuncto                   | quilisma prepuncto                    | Modified family                      | prefixed rising special-form                | Fixed              |                          4 | `•+` or prefixed rising exemplar | No                   | Yes               | Prepuncto              | Prefix note before quilisma formation                                           | prefix punctum + quilisma component + continuation       | Yes                         | Assembly or dedicated family glyph                  | Medium     | Likely best understood as prefixed quilisma family form |
| RN-021 | flexa respina + pressus + subpunctis | flexa resupina + pressus + subpunctis | Composite sequence                   | mixed                                       | Composite          |                          6 | `-+ =-` composite exemplar       | Partial              | Yes               | Composite              | Sequence of flexa-resupina motion into pressus core with descending tail        | flexa resupina + pressus core + subpunctis tail          | Yes                         | Assembly only                                       | Low        | Composite chart example, not likely one encoded glyph   |
| RN-022 | flexa respina + pressus liquesans    | flexa resupina + pressus liquescens   | Composite sequence                   | mixed                                       | Composite          |                          6 | `-+ =-` composite exemplar       | Partial              | Yes               | Composite + liquescent | Sequence of flexa-resupina motion into pressus core with liquescent ending      | flexa resupina + pressus core + liquescent terminal      | Yes                         | Assembly only                                       | Low        | Composite chart example                                 |
| RN-023 | pes + cephalicus                     | pes + cephalicus                      | Composite sequence                   | up then down                                | Composite          |                          3 | `+-` composite exemplar          | No                   | Yes               | Composite              | Sequence of pes motion into cephalicus ending                                   | pes core + cephalicus form                               | Yes                         | Assembly only                                       | Medium     | Shared pivot note in chart exemplar                     |
| RN-024 | flexa + pes                          | flexa + pes                           | Composite sequence                   | down then up                                | Composite          |                          4 | `-+` composite exemplar          | No                   | Yes               | Composite              | Sequence of descending flexa into rising pes                                    | flexa core + pes core                                    | Yes                         | Assembly only                                       | Medium     | Good test case for sequencing logic                     |
| RN-025 | quilisma + pressus                   | quilisma + pressus                    | Composite sequence                   | rising then repeated                        | Composite          |                          4 | `+=` composite exemplar          | Partial              | Yes               | Composite              | Quilisma formation followed by pressus core                                     | quilisma component + pressus repeat core                 | Yes                         | Assembly only                                       | Medium     | Good test case for quilisma + repetition interaction    |
| RN-026 | quilisma + pressus liquesans         | quilisma + pressus liquescens         | Composite sequence                   | rising then repeated with liquescent ending | Composite          |                          5 | `+=-` composite exemplar         | Partial              | Yes               | Composite + liquescent | Quilisma formation followed by pressus core and liquescent ending               | quilisma component + pressus core + liquescent terminal  | Yes                         | Assembly only                                       | Low        | Chart spelling likely needs normalization               |

---

## 5. Families vs chart exemplars — the key distinction

### Families whose chart example should **not** be mistaken for the whole family

* climacus
* scandicus
* quilisma
* pressus

For these, the chart is showing a useful example, but not the entire design space.

### Families that are much closer to fixed graphical units

* virga
* punctum
* apostropha
* bistropha
* tristropha
* pes
* flexa
* cephalicus
* epiphonus

These still vary in vertical placement, but their identity is more stable.

### Entries that should probably remain **assemblies only**

* flexa resupina + pressus + subpunctis
* flexa resupina + pressus liquescens
* pes + cephalicus
* flexa + pes
* quilisma + pressus
* quilisma + pressus liquescens

---

## 6. Atomic and component layer proposal for the font

This is the strongest current candidate set for truly reusable base material.

| Proposed atomic / component item    | Why                                                               |
| ----------------------------------- | ----------------------------------------------------------------- |
| punctum                             | Core note sign                                                    |
| virga                               | Core note sign                                                    |
| apostropha                          | Core repetition sign                                              |
| quilisma component                  | Needs reuse inside larger forms                                   |
| liquescent terminal form            | Needed across multiple modified families                          |
| pressus repeat core                 | Useful if pressus-family forms are systematized                   |
| descending punctum tail             | Useful for subpunctis-type constructions                          |
| rising / descending connector logic | Needed for assembly behavior even if not drawn as separate glyphs |

Note: this is a **font-engineering layer**, not a musicological claim that every neume is reducible in practice.

---

## 7. What this means for naming

### Good naming pattern

Use names that separate:

* **family**
* **modifier**
* **composite status**

Examples:

* `pes`
* `pes_flexus`
* `pressus`
* `pressus_liquescens`
* `quilisma`
* `quilisma_prepuncto`
* `composite_pes_cephalicus`

### Avoid

Do **not** bake instance details into the family name, such as:

* exact vertical span
* exact pitch positions
* chart-only note counts for variable families

Those belong to rendering logic, not the family name.

---

## 8. Hildegard-vs-Gregorio adjustment summary

### What we borrow from Gregorio/gabc

* sequence / construction thinking
* family vs realized instance separation
* contextual shaping logic
* modifiers treated distinctly from core pitch sequence

### What we do **not** copy blindly

* square-notation assumptions where Hildegard/Rhineland forms differ
* over-flattening distinctive Hildegard forms into generic square-chant behavior
* assuming every family should be entered as bare pitch sequence with no paleographic layer

### Current recommended balance

* Keep a **Hildegard semantic inventory**
* Add a **constructor layer** beneath it
* Reserve dedicated glyphs for the most stable and visually characteristic families
* Treat larger composite examples as assemblies unless manuscript practice strongly argues otherwise

---

## 9. Manual review checklist

Please manually review:

1. **Spellings / canonical terms**

   * `pex flexus` → likely `pes flexus`
   * `liquesans` → likely `liquescens`
   * `respina` → likely `resupina`

2. **Whether you want to keep chart terminology exactly as your production terminology**
   Especially:

   * `flexa`
   * `flexa resupina`
   * `pes liquescens`

3. **Whether any composite chart examples deserve dedicated glyphs anyway for practical reasons**
   This is a production decision, not just a theory question.

4. **Whether quilisma should be treated as one of the formal atomic signs in your build system**
   Current recommendation: yes.

5. **Whether bistropha / tristropha should be encoded as dedicated glyphs or generated from repetition logic**
   Current recommendation: keep both options open until manuscript regularity is reviewed.

---

## 10. Resolved assumptions for v0.5

For this version, we now assume:

* all **canonical labels are correct**
* `pes flexus`, `liquescens`, and `resupina` are final production forms
* `bistropha` and `tristropha` should follow standard production best practice rather than remaining undecided

### Best-practice decision on bistropha / tristropha

Recommended production approach:

* treat **bistropha** and **tristropha** as **dedicated named glyphs in the final inventory**
* also model them internally as members of the **apostropha repetition family**

Why this is the best balance:

* they are stable, conventional, named forms
* users and future tooling will expect to see them as explicit inventory items
* they are common enough to justify dedicated drawing and testing
* but they still benefit from being understood as repetition-derived forms for family logic and styling consistency

So the working rule becomes:

* **inventory level**: dedicated glyphs
* **design-system level**: repetition family derived from apostropha logic

---

## 11. Component-family map

This section converts the semantic inventory into a font-production structure.

### A. Atomic sign layer

These are the smallest stable graphic units worth drawing as primary assets.

| Component ID | Component name      | Role                           | Used by                                                                          |
| ------------ | ------------------- | ------------------------------ | -------------------------------------------------------------------------------- |
| C-001        | punctum             | core note sign                 | punctum, scandicus, climacus, subpunctis tails, quilisma-prefixed forms          |
| C-002        | virga               | core note sign with virga form | virga, scandicus/climacus-family contexts where appropriate                      |
| C-003        | apostropha          | repetition sign                | apostropha, bistropha, tristropha, possibly pressus-family styling logic         |
| C-004        | quilisma core       | special note-form component    | quilisma, quilisma prepuncto, quilisma + pressus, quilisma + pressus liquescens  |
| C-005        | liquescent terminal | shared modified ending         | cephalicus, epiphonus, pes liquescens, pes flexus liquescens, pressus liquescens |
| C-006        | pressus repeat core | repeated-pitch structural core | pressus, pressus liquescens, pressus subpunctis, composite pressus sequences     |
| C-007        | subpunctis tail     | descending punctum tail        | pressus subpunctis, composite subpunctis sequences                               |

### B. Connector / construction layer

These may not become separate encoded glyphs, but they must exist as explicit design logic.

| Logic ID | Logic name                      | Role                                                     | Needed by                                                                    |
| -------- | ------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------- |
| L-001    | ascending connector             | joins lower note to higher continuation                  | pes, scandicus, epiphonus, quilisma-family rising forms                      |
| L-002    | descending connector            | joins upper note to lower continuation                   | flexa, climacus, cephalicus, subpunctis tails                                |
| L-003    | rebound connector               | handles down-up motion                                   | flexa resupina, mixed composite forms                                        |
| L-004    | repeat-pitch join               | handles same-note repercussion linkage                   | bistropha, tristropha, pressus-family forms                                  |
| L-005    | liquescent termination behavior | governs transition into liquescent ending                | cephalicus, epiphonus, pes liquescens, pressus liquescens                    |
| L-006    | composite sequencing spacing    | governs spacing and joining between consecutive families | pes + cephalicus, flexa + pes, quilisma + pressus, large composite sequences |

### C. Family map

This is the core production-level map from family name to build logic.

| Family                       | Type                  | Preferred build                                        | Uses components / logic       |
| ---------------------------- | --------------------- | ------------------------------------------------------ | ----------------------------- |
| virga                        | atomic sign           | dedicated glyph                                        | C-002                         |
| punctum                      | atomic sign           | dedicated glyph                                        | C-001                         |
| apostropha                   | atomic sign           | dedicated glyph                                        | C-003                         |
| bistropha                    | repetition family     | dedicated glyph, derived from repetition family logic  | C-003 + L-004                 |
| tristropha                   | repetition family     | dedicated glyph, derived from repetition family logic  | C-003 + L-004                 |
| pes                          | fixed family          | dedicated glyph with optional parametric spacing model | C-001/C-002 + L-001           |
| flexa                        | fixed family          | dedicated glyph with optional parametric spacing model | C-001/C-002 + L-002           |
| pes flexus                   | fixed family          | dedicated glyph or tightly controlled assembly         | pes logic + L-002             |
| flexa resupina               | fixed family          | dedicated glyph or tightly controlled assembly         | flexa logic + L-003           |
| scandicus                    | variable family       | assembly-first, with optional common presets           | C-001/C-002 + repeated L-001  |
| climacus                     | variable family       | assembly-first, with optional common presets           | C-001/C-002 + repeated L-002  |
| cephalicus                   | modified family       | dedicated glyph or dedicated modified-family drawing   | C-005 + L-002                 |
| epiphonus                    | modified family       | dedicated glyph or dedicated modified-family drawing   | C-005 + L-001                 |
| pes liquescens               | modified family       | dedicated glyph or family assembly                     | pes logic + C-005             |
| pes flexus liquescens        | modified family       | dedicated glyph or family assembly                     | pes flexus logic + C-005      |
| pressus                      | repetition family     | dedicated glyph plus repeat-core model                 | C-006 + L-004                 |
| pressus liquescens           | modified family       | dedicated glyph plus repeat-core model                 | C-006 + C-005 + L-004/L-005   |
| pressus subpunctis           | modified family       | dedicated glyph plus repeat-core model                 | C-006 + C-007 + L-004/L-002   |
| quilisma                     | special sign / family | both atomic component and family-level build           | C-004 + L-001                 |
| quilisma prepuncto           | modified family       | assembly-first, optional dedicated preset              | C-001 + C-004 + L-001         |
| composite families (`X + Y`) | composite sequence    | assembly only                                          | relevant family logic + L-006 |

---

## 12. Standalone vs assembly decision sheet

This is the first practical production decision table.

### A. Definitely standalone in the shipped font

These should exist as explicit final glyphs, even if some are internally derived from a family system.

| Item               | Reason                                                            |
| ------------------ | ----------------------------------------------------------------- |
| virga              | core basic sign                                                   |
| punctum            | core basic sign                                                   |
| apostropha         | core basic sign                                                   |
| bistropha          | stable named repetition form                                      |
| tristropha         | stable named repetition form                                      |
| pes                | stable and frequent fixed family                                  |
| flexa              | stable and frequent fixed family                                  |
| cephalicus         | distinctive modified family                                       |
| epiphonus          | distinctive modified family                                       |
| pressus            | distinctive repeated-pitch family                                 |
| pressus subpunctis | common enough and distinctive enough to justify dedicated testing |

### B. Standalone strongly recommended, but keep construction model underneath

These benefit from being explicit glyphs while still being modeled as families.

| Item                  | Reason                                                                     |
| --------------------- | -------------------------------------------------------------------------- |
| pes flexus            | stable family, but useful to understand compositionally                    |
| flexa resupina        | stable family, but may benefit from construction logic                     |
| pes liquescens        | modified family with reusable liquescent behavior                          |
| pes flexus liquescens | modified family with reusable liquescent behavior                          |
| pressus liquescens    | modified family with reusable liquescent behavior                          |
| quilisma              | special enough to justify direct drawing, but must also exist as component |

### C. Assembly-first, with optional convenience presets

These should primarily be modeled by rules, though common exemplars can be included as shortcuts if testing shows it helps.

| Item               | Reason                                        |
| ------------------ | --------------------------------------------- |
| scandicus          | variable-length ascending family              |
| climacus           | variable-length descending family             |
| quilisma prepuncto | better understood as prefixed quilisma family |

### D. Assembly only

These should not be first-class standalone encoded glyphs in the base inventory.

| Item                                  | Reason             |
| ------------------------------------- | ------------------ |
| flexa resupina + pressus + subpunctis | composite sequence |
| flexa resupina + pressus liquescens   | composite sequence |
| pes + cephalicus                      | composite sequence |
| flexa + pes                           | composite sequence |
| quilisma + pressus                    | composite sequence |
| quilisma + pressus liquescens         | composite sequence |

---

## 13. Finalized internal naming scheme

This version assumes canonical labels are settled and uses a production naming style.

| Family / item                         | Suggested internal production name            |
| ------------------------------------- | --------------------------------------------- |
| virga                                 | `virga`                                       |
| punctum                               | `punctum`                                     |
| apostropha                            | `apostropha`                                  |
| bistropha                             | `bistropha`                                   |
| tristropha                            | `tristropha`                                  |
| pes                                   | `pes`                                         |
| pes flexus                            | `pes_flexus`                                  |
| flexa                                 | `flexa`                                       |
| flexa resupina                        | `flexa_resupina`                              |
| cephalicus                            | `cephalicus`                                  |
| epiphonus                             | `epiphonus`                                   |
| pes liquescens                        | `pes_liquescens`                              |
| pes flexus liquescens                 | `pes_flexus_liquescens`                       |
| pressus                               | `pressus`                                     |
| pressus liquescens                    | `pressus_liquescens`                          |
| pressus subpunctis                    | `pressus_subpunctis`                          |
| quilisma                              | `quilisma`                                    |
| quilisma prepuncto                    | `quilisma_prepuncto`                          |
| flexa resupina + pressus + subpunctis | `composite_flexa_resupina_pressus_subpunctis` |
| flexa resupina + pressus liquescens   | `composite_flexa_resupina_pressus_liquescens` |
| pes + cephalicus                      | `composite_pes_cephalicus`                    |
| flexa + pes                           | `composite_flexa_pes`                         |
| quilisma + pressus                    | `composite_quilisma_pressus`                  |
| quilisma + pressus liquescens         | `composite_quilisma_pressus_liquescens`       |

---

## 14. What to build next

The next production document should be a **codepoint and shaping plan** with four linked parts:

1. **Glyph set sheet**

   * exactly which final glyphs will exist in v1

2. **Component sheet**

   * reusable parts and whether they are encoded or internal-only

3. **Anchors / attachment sheet**

   * where joins and terminals attach

4. **OpenType / layout behavior sheet**

   * ligatures
   * contextual alternates
   * assembly behavior
   * fallback behavior for variable families
