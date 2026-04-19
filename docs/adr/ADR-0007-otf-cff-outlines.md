# ADR-0007: OpenType/CFF outlines, not TrueType

- Status: Accepted
- Date: 2026-04-14
- Deciders: project maintainers
- Consulted: claude-review-2026-04-14 § 9, Bravura precedent
- Tags: format, outlines

## Context

OpenType fonts ship with either CFF (Compact Font Format, cubic Bézier) or TrueType (quadratic Bézier) outlines. Which to choose affects build tooling, file format, and — most importantly for this project — whether the extracted SVG path data uses cubic or quadratic commands.

## Decision

The font ships as `.otf` with **CFF (cubic Bézier) outlines**.

Rhena's SVG backend accepts `M`, `L`, `C`, `Q`, `Z` commands. CFF's native cubics map directly to `C` commands without conversion. If the font were TrueType, `SVGPathPen` would emit `Q` commands (quadratics), which Rhena also accepts but which require different curve-fitting heuristics if the designer later wants smooth higher-order curves.

Calligraphic strokes benefit from cubic curves because they can express weight variation along a stroke (two control points let you shape asymmetric widening and tapering independently). Quadratic curves can approximate this but need more segments.

## Alternatives considered

1. **TrueType (`.ttf`) with quadratic outlines**. Rejected: `.otf` is the convention for calligraphic/design-heavy fonts. Bravura (SMuFL reference font) ships as `.otf` with CFF. Matching this precedent reduces surprise for SMuFL-aware tools.
2. **Variable font (CFF2 or GVAR-based TTF)**. Rejected: no axes needed in v1. Single static cut.
3. **Ship both `.otf` and `.ttf`**. Rejected: doubles the build surface for no benefit. External consumers can convert `.otf` to `.ttf` if they really need TTF-only engines.

## Consequences

### Positive
- Cubic curves give the designer direct control over calligraphic stroke shape.
- Matches Bravura / Greciliae / chant-ecosystem convention.
- `SVGPathPen` emits `C` commands directly, no quadratic-to-cubic conversion pass.

### Negative
- Some legacy engines (older Android, very old Windows) prefer TTF. None of the target consumers (Rhena, Verovio, modern browsers, Illustrator, LilyPond) have this constraint.

### Neutral
- `.woff2` output wraps the same CFF outlines for web delivery.

## References

- OpenType specification, CFF table: https://learn.microsoft.com/en-us/typography/opentype/spec/cff
- Bravura SMuFL reference font: https://github.com/steinbergmedia/bravura
- `claude-review-2026-04-14.md` § 9
