# MEI Encoding Reference — Hildegard Neumes

Status: v1, 2026-04-14.
Scope: shows how each v0.5 inventory family maps to MEI neume-module XML. Serves as both (a) a test corpus for the Verovio fork and (b) authoring reference for transcribers.
Companion: `glyph_inventory_v0.5.md`, `verovio_integration_plan.md`.

---

## 0. Principles

1. **The "Hildegard profile" uses only stock MEI.** No schema extension. All Rhineland-specific classification is carried on `<neume @type>` — a free-form string via `att.typed`, available on every MEI element. Precedent: Aquitanian, Old Hispanic, and St-Gall neume samples in `music-encoding-develop/source/examples/neumes/` use the same mechanism.
2. **Notation mode switch** is `notationtype="neume.rhineland"` on `<staffDef>`. Falls back to `notationtype="neume"` for square rendering in unpatched Verovio.
3. **Staff: 4 lines, movable C-clef.** Yellow C-line and red F-line are applied by the JS post-processor, not encoded in MEI.
4. **Liquescents, oriscus, quilisma** are first-class MEI child elements of `<nc>`, not attributes. Use them.
5. **Repetition families** (apostropha, bistropha, tristropha) are encoded as `<nc>`s on the same pitch, optionally wrapped in a `<neume type="...">` for explicit classification.

---

## 1. Minimum viable document

The smallest MEI file that exercises the Verovio neume pipeline. Three neumes on one syllable.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mei xmlns="http://www.music-encoding.org/ns/mei" meiversion="5.0">
  <meiHead>
    <fileDesc>
      <titleStmt><title>Hildegard MVP test</title></titleStmt>
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
                  <neume type="pes">
                    <nc pname="e" oct="3"/>
                    <nc pname="g" oct="3"/>
                  </neume>
                  <neume type="flexa">
                    <nc pname="g" oct="3"/>
                    <nc pname="e" oct="3"/>
                  </neume>
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

---

## 2. Per-family encoding

Only the `<neume>` fragment is shown for each; wrap in the skeleton from § 1.

### 2.1 Atomic signs

**RN-001 virga** — a single-note stemmed sign. Encode as `<neume>` with one `<nc>` and `@tilt` to indicate the virga's slanted head. Verovio's unpatched path draws this as `chantPunctumVirga` (U+E996); the Rhineland branch draws the Hildegard-register virga at the same codepoint.

```xml
<neume>
  <nc pname="e" oct="3" tilt="ne"/>
</neume>
```

**RN-003 punctum** — bare single note.

```xml
<neume>
  <nc pname="e" oct="3"/>
</neume>
```

**RN-027 tractulus** — encoded as punctum with a Hildegard `@type` marker. (Humdrum-only; defer until verified.)

```xml
<neume type="tractulus">
  <nc pname="e" oct="3"/>
</neume>
```

**RN-009 apostropha / SMuFL chantStrophicus** — use a child `<strophicus>` element or an `@type` on the `<neume>`.

```xml
<neume type="apostropha">
  <nc pname="e" oct="3"/>
</neume>
```

**RN-028 oriscus (asc + desc)** — first-class MEI child.

```xml
<neume>
  <nc pname="e" oct="3">
    <oriscus/>
  </nc>
</neume>
```

### 2.2 Fixed families

**RN-005 pes** — ascending two-note. Rhineland branch draws `hildegardPes` (U+F420).

```xml
<neume type="pes">
  <nc pname="e" oct="3"/>
  <nc pname="g" oct="3"/>
</neume>
```

**RN-006 pes flexus** — up-down three-note. `hildegardPesFlexus` (U+F421).

```xml
<neume type="pes_flexus">
  <nc pname="e" oct="3"/>
  <nc pname="g" oct="3"/>
  <nc pname="f" oct="3"/>
</neume>
```

**RN-007 flexa (= Gardiner "clivis")** — two-note descent. `hildegardFlexa` (U+F422).

```xml
<neume type="flexa">
  <nc pname="g" oct="3"/>
  <nc pname="e" oct="3"/>
</neume>
```

**RN-008 flexa resupina (= Gardiner "porrectus")** — down-up rebound. Note the synonymy in Gardiner p. 91; use one `@type` and map synonyms in the Verovio dispatch.

```xml
<neume type="flexa_resupina">
  <nc pname="g" oct="3"/>
  <nc pname="e" oct="3"/>
  <nc pname="f" oct="3"/>
</neume>
```

### 2.3 Torculus family

**RN-029 torculus rotundus** — round-headed up-down-up.

```xml
<neume type="torculus_rotundus">
  <nc pname="e" oct="3"/>
  <nc pname="g" oct="3"/>
  <nc pname="e" oct="3"/>
</neume>
```

**RN-030 torculus quadratus** — angular up-down-up. Identical contour to rotundus; only the `@type` disambiguates. (Humdrum-only split; verify.)

```xml
<neume type="torculus_quadratus">
  <nc pname="e" oct="3"/>
  <nc pname="g" oct="3"/>
  <nc pname="e" oct="3"/>
</neume>
```

**RN-031 torculus resupinus** — up-down-up-up with resupination.

```xml
<neume type="torculus_resupinus">
  <nc pname="e" oct="3"/>
  <nc pname="g" oct="3"/>
  <nc pname="e" oct="3"/>
  <nc pname="g" oct="3"/>
</neume>
```

### 2.4 Porrectus family

**RN-032 porrectus** — down-up with connecting diagonal body.

```xml
<neume type="porrectus">
  <nc pname="g" oct="3"/>
  <nc pname="e" oct="3"/>
  <nc pname="a" oct="3"/>
</neume>
```

**RN-033 porrectus flexus** — down-up-down.

```xml
<neume type="porrectus_flexus">
  <nc pname="g" oct="3"/>
  <nc pname="e" oct="3"/>
  <nc pname="a" oct="3"/>
  <nc pname="g" oct="3"/>
</neume>
```

### 2.5 Variable families — assembly-first

**RN-002 climacus** — descending chain of virga + dot-puncta. Variable length. Render-time assembly from atoms.

```xml
<neume type="climacus">
  <nc pname="g" oct="3" tilt="ne"/>  <!-- virga head -->
  <nc pname="f" oct="3"/>
  <nc pname="e" oct="3"/>
  <nc pname="d" oct="3"/>
</neume>
```

**RN-004 scandicus** — ascending chain.

```xml
<neume type="scandicus">
  <nc pname="d" oct="3"/>
  <nc pname="e" oct="3"/>
  <nc pname="f" oct="3"/>
  <nc pname="g" oct="3"/>
</neume>
```

**RN-034 climacus resupinus** — descending then rising. Humdrum-only; verify.

```xml
<neume type="climacus_resupinus">
  <nc pname="g" oct="3" tilt="ne"/>
  <nc pname="f" oct="3"/>
  <nc pname="e" oct="3"/>
  <nc pname="d" oct="3"/>
  <nc pname="e" oct="3"/>
</neume>
```

### 2.6 Repetition families

**RN-010 bistropha** — same pitch twice.

```xml
<neume type="bistropha">
  <nc pname="e" oct="3"><strophicus/></nc>
  <nc pname="e" oct="3"><strophicus/></nc>
</neume>
```

**RN-011 tristropha** — same pitch three times.

```xml
<neume type="tristropha">
  <nc pname="e" oct="3"><strophicus/></nc>
  <nc pname="e" oct="3"><strophicus/></nc>
  <nc pname="e" oct="3"><strophicus/></nc>
</neume>
```

### 2.7 Modified (liquescent) family

**RN-012 cephalicus** — descending two-note liquescent. Gardiner p. 60 Ex. 9.

```xml
<neume type="cephalicus">
  <nc pname="g" oct="3"/>
  <nc pname="e" oct="3"><liquescent/></nc>
</neume>
```

**RN-013 epiphonus** — ascending two-note liquescent.

```xml
<neume type="epiphonus">
  <nc pname="e" oct="3"/>
  <nc pname="g" oct="3"><liquescent/></nc>
</neume>
```

**RN-014 pes liquescens** — pes with liquescent terminal.

```xml
<neume type="pes_liquescens">
  <nc pname="e" oct="3"/>
  <nc pname="g" oct="3"><liquescent/></nc>
</neume>
```

**RN-015 pes flexus liquescens** — pes flexus + liquescent.

```xml
<neume type="pes_flexus_liquescens">
  <nc pname="e" oct="3"/>
  <nc pname="g" oct="3"/>
  <nc pname="f" oct="3"><liquescent/></nc>
</neume>
```

### 2.8 Pressus family

**RN-016 pressus** — vertical line + undulation (Gardiner p. 94).

```xml
<neume type="pressus">
  <nc pname="g" oct="3"/>
  <nc pname="g" oct="3"/>
</neume>
```

**RN-017 pressus liquescens** — pressus + rounded liquescent terminal. Gardiner p. 60, Ex. 9 (contrast with cephalicus on *frumentum*).

```xml
<neume type="pressus_liquescens">
  <nc pname="g" oct="3"/>
  <nc pname="g" oct="3"/>
  <nc pname="f" oct="3"><liquescent/></nc>
</neume>
```

**RN-018 pressus subpunctis** — pressus + descending subpunctis tail.

```xml
<neume type="pressus_subpunctis">
  <nc pname="g" oct="3"/>
  <nc pname="g" oct="3"/>
  <nc pname="f" oct="3"/>
  <nc pname="e" oct="3"/>
</neume>
```

### 2.9 Quilisma family

**RN-019 quilisma** — jagged-wave core + attached ascending tail. First-class MEI child `<quilisma>` on the relevant `<nc>`.

```xml
<neume type="quilisma">
  <nc pname="d" oct="3"/>
  <nc pname="e" oct="3"><quilisma/></nc>
  <nc pname="g" oct="3"/>
</neume>
```

**RN-020 quilisma prepuncto** — prefix note before the quilisma+tail. Gardiner p. 60.

```xml
<neume type="quilisma_prepuncto">
  <nc pname="c" oct="3"/>
  <nc pname="d" oct="3"/>
  <nc pname="e" oct="3"><quilisma/></nc>
  <nc pname="g" oct="3"/>
</neume>
```

### 2.10 Hildegard-idiosyncratic compounds

**RN-021 flexa resupina + pressus + subbipunctis** — dedicated glyph per Gardiner p. 16.

```xml
<neume type="flexa_resupina_pressus_subbipunctis">
  <nc pname="g" oct="3"/>
  <nc pname="e" oct="3"/>
  <nc pname="f" oct="3"/>
  <nc pname="f" oct="3"/>
  <nc pname="e" oct="3"/>
  <nc pname="d" oct="3"/>
</neume>
```

**RN-022 flexa resupina + pressus liquescens** — dedicated glyph.

```xml
<neume type="flexa_resupina_pressus_liquescens">
  <nc pname="g" oct="3"/>
  <nc pname="e" oct="3"/>
  <nc pname="f" oct="3"/>
  <nc pname="f" oct="3"/>
  <nc pname="e" oct="3"><liquescent/></nc>
</neume>
```

### 2.11 Composite sequences (assembly-only)

**RN-023 composite_pes_cephalicus**, **RN-024 composite_flexa_pes**, **RN-025 composite_quilisma_pressus**, **RN-026 composite_quilisma_pressus_liquescens** — encode as two consecutive `<neume>`s on the same syllable, each with its own `@type`. The renderer handles inter-neume spacing via existing Verovio logic.

```xml
<!-- RN-024 composite_flexa_pes -->
<syllable>
  <syl>a</syl>
  <neume type="flexa">
    <nc pname="g" oct="3"/>
    <nc pname="e" oct="3"/>
  </neume>
  <neume type="pes">
    <nc pname="f" oct="3"/>
    <nc pname="a" oct="3"/>
  </neume>
</syllable>
```

---

## 3. Open questions for the schema

1. **Gardiner "clivis" / "porrectus" synonymy.** Do we encode as `<neume type="flexa">` or `<neume type="clivis">`? The Verovio dispatch (§ 3.B in `verovio_integration_plan.md`) includes both synonyms mapped to the same enum value. MEI documents should prefer one form for encoding stability; **recommended: `flexa` and `flexa_resupina`** (not clivis / porrectus) because they're more specific to the Rhineland tradition and avoid confusion with square-notation usage.
2. **Torculus rotundus vs quadratus.** Held pending direct manuscript verification. If D/R doesn't distinguish them, drop the split and use plain `@type="torculus"`. If they do, the encoding above already accommodates both.
3. **Staff colours.** No MEI element carries staff-line colour per line. The JS post-processor in `verovio_integration_plan.md` § 3.D handles this. Alternative: MEI's `<staffDef @color>` applies to the whole staff; could hold a baseline colour and let post-processor apply line-specific overrides.
4. **Lyrics / syllable alignment.** The examples above all put one neume per syllable for simplicity. Real antiphons group several neumes per syllable (Gardiner Ex. 9 shows two neumes on the first syllable of "frumentum"). Encode as multiple `<neume>` children of one `<syllable>` — the MEI skeleton already supports this.
5. **Episema / ictus / augmentum.** Only encode if attested in D/R. Verify before using SMuFL U+E9D8, U+E9D0, U+E9D9.
6. **Text language.** All examples use placeholder syllables. Real MEI should carry Latin text in `<syl>` with appropriate `@xml:lang`.

---

## 4. Test corpus roadmap

Post-MVP, build a test corpus of 3–5 short antiphons encoded in this profile, rendered through the Verovio fork, with SVG snapshots checked against direct manuscript reading:

1. **O viridissima virga** (Dendermonde + Riesencodex f. 474r–v) — high priority because Gardiner discusses its cephalicus/pressus liquescens paleography in detail.
2. **O ignis spiritus paracliti** — antiphon to the Holy Spirit, melismatic, exercises quilisma family.
3. **O virga ac diadema** — antiphon to the Virgin Mary, moderate length, mixed family exercise.
4. **Columba aspexit** — sequence for St Maximinus, long, full inventory exercise.
5. Any idiosyncratic-compound candidate where RN-021 or RN-022 is attested.

These MEI files live under `examples/corpus/` when authored. Expected SVG snapshots live next to them for regression testing.
