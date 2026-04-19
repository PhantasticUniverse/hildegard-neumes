# ADR-0008: Paleographic fidelity arbitration policy

- Status: Accepted
- Date: 2026-04-14
- Deciders: project maintainers
- Consulted: claude-review-2026-04-14 § 9 and § 14.7, research_synthesis.md, research_v2_findings.md, docs/paleographic_drawing_briefs.md
- Tags: paleography, fidelity, sources

## Context

The paleographic research for this font draws on multiple sources that sometimes disagree:

- **Direct manuscript inspection** (Dendermonde Cod. 9 via IMSLP, Wiesbaden Riesencodex Hs. 2 via HLB RheinMain CC-BY). The primary visual ground truth.
- **Katie Gardiner, DMA diss. 2022**. The richest single scholarly source, but Gardiner's paleographic treatment is derivative and has known errors (spelling "respinus/respina" instead of "resupinus/resupina"; page-reference drift; no coverage of pen/nib/scribal-hand detail).
- **Peter van Poucke**, Alamire Dendermonde facsimile introduction (1991). Quoted by Gardiner and Welker/Klaper, the source of the "between St Gall and Hufnagelschrift" characterization.
- **Welker & Klaper, Reichert Verlag Riesencodex facsimile** (1998). Not directly consulted in this research pass but cited as authoritative for stroke-weight/pen-angle detail.
- **Humdrum Hildegard representation**. Analytic encoding; introduces splits (torculus rotundus vs quadratus) that Gardiner does not support.
- **Beverly Lomer / ISHvBS chart** (Hildegard Society). Pitch-content transcription reference, not a paleographic source.

When these disagree — e.g. should `rh_quilisma` have 2 or 3 undulations; is there really a torculus rotundus/quadratus distinction in the manuscripts; is the liquescent tail straight or curved — who arbitrates?

## Decision

The project's arbitration policy has two tracks:

**Track 1 — Visual shape questions** (what does a stroke actually look like? how thick is the pen? what is the nib angle?). Authority order, highest first:

1. **Direct manuscript inspection** — open the relevant folio PDF, look at several instances of the glyph, form a judgment.
2. **Welker/Klaper 1998** or **van Poucke 1991** — authoritative facsimile introductions with explicit paleographic commentary.
3. **Gardiner 2022** — secondary synthesis; quote when she is concrete (the four passages on pp. 15, 60, 92–95 are usable; her neume-by-neume figure captions are usable).
4. **Scholarly consensus** — Hiley *Western Plainchant*, Apel *Gregorian Chant*, Cardine *Gregorian Semiology* for general-tradition questions not specific to the Rhineland sources.

**Track 2 — Classification questions** (is this neume a flexa or a clivis; is this a torculus or a pes-flexus; does this family even exist?). Authority order, highest first:

1. **Gardiner 2022 figure captions and tables** — her Fig. 6 labels (virga, punctum, pes, clivis, climacus, scandicus, torculus, porrectus) and neume-by-neume analyses are the project's canonical classification vocabulary.
2. **Humdrum Hildegard representation** — for splits Gardiner does not enumerate (e.g. torculus rotundus vs quadratus), with the caveat that such splits are **Humdrum-only** and MUST be verified against direct manuscript inspection before entering the production glyph set.
3. **Beverly Lomer / ISHvBS chart** — for families outside Gardiner's scope.

**Humdrum-only entries** (tractulus, torculus rotundus/quadratus split, climacus resupinus, pes_subpunctis, epiphonus) are **held for direct manuscript verification** and do not enter the v1 production set until they are confirmed visually. None of them are in Rhena's current 19-atom resolver, so v1 drops them without loss.

**Gardiner's spelling errors** (respinus/respina) are corrected to the classical Latin form (resupinus/resupina) in production naming. Gardiner's variant is noted in the source column as "Gardiner writes respina (sic)" rather than silently fixed.

## Alternatives considered

1. **Always defer to Gardiner**. Rejected: Gardiner's paleographic treatment is derivative and has demonstrable errors; direct manuscript inspection is more authoritative on visual questions.
2. **Always defer to direct manuscript inspection**. Rejected for classification questions: the manuscripts don't name their neumes, and classification is a modern scholarly layer that the manuscripts themselves do not settle.
3. **Majority vote across sources**. Rejected: sources are not independent (Gardiner quotes van Poucke; Lomer is pitch-only; Humdrum is analytic), and a majority-of-three is cheap to game.

## Consequences

### Positive
- Disagreements are resolved on a principled basis rather than ad hoc.
- Contributors know where to look first for each kind of question.
- Gardiner's role is explicit: rich quotable source, not a tiebreaker on visual detail.

### Negative
- Requires direct manuscript access for visual questions. (The manuscripts are digitized and open, so this is a cheap requirement.)
- Welker/Klaper 1998 is not digitally available for free; a print consultation may be needed for stroke-weight questions.

### Neutral
- Does not preclude updating individual glyphs as research deepens; ADRs can be superseded.

## References

- `research_synthesis.md`, `research_v2_findings.md` — canonical paleographic research.
- `docs/paleographic_drawing_briefs.md` — per-glyph drawing briefs (Agent 3 output).
- Gardiner 2022: https://scholarworks.iu.edu/iuswrrest/api/core/bitstreams/1a626db3-354f-4a79-94c2-227cd959eec0/content
- Riesencodex digital facsimile: https://hlbrm.digitale-sammlungen.hebis.de/handschriften-hlbrm/content/titleinfo/449618
- Dendermonde IMSLP facsimile: https://imslp.org/wiki/Dendermonde_Codex_(Hildegard)
- `claude-review-2026-04-14.md` §§ 9, 14.7
