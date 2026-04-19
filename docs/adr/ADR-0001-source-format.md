# ADR-0001: Source format — UFO3, not SFD

- Status: Accepted
- Date: 2026-04-14
- Deciders: project maintainers
- Consulted: claude-review-2026-04-14 § 1, rhena_integration_plan.md § 4
- Tags: font-source, tooling, git-workflow

## Context

The font needs a source-of-truth format that a designer can iterate in and that reviewers can diff in a pull request. FontForge's native `.sfd` is a single file in a binary-ish line-oriented text format; it round-trips cleanly through FontForge but is opaque to git review and locks the project to one tool.

## Decision

The canonical source format for `hildegard-neumes` is **UFO3** (Unified Font Object, version 3), stored at `src/hildegard-neumes.ufo/` as a directory of per-glyph `.glif` XML files plus `fontinfo.plist`, `metainfo.plist`, and `layercontents.plist`.

Build tools MUST read from this UFO. The build script (`scripts/build-font.sh`) opens the UFO with FontForge in headless mode and generates `hildegard-neumes.otf` and `hildegard-neumes.woff2` into `build/`.

## Alternatives considered

1. **`.sfd` (FontForge native)**. Rejected: single-file diffs are opaque, git merge conflicts are whole-file, tool lock-in is absolute.
2. **`.glyphs` (Glyphs.app proprietary)**. Rejected: commercial-only authoring tool, XML-ish but tool-specific, smaller community.
3. **UFO2**. Rejected: UFO3 is the current standard (2012), has better multi-layer support, and is what defcon/fontTools/fontmake all target.

## Consequences

### Positive
- Per-glyph `.glif` files produce PR-reviewable diffs: a single-glyph change shows up as a single-file change.
- Tool neutral: FontForge, Glyphs, FontLab, RoboFont, and any defcon-based pipeline can open and edit UFO3.
- Merge conflicts on concurrent glyph edits are per-file and typically trivial.
- Contributors don't need FontForge specifically — any UFO-aware tool suffices.

### Negative
- UFO3 is a directory, not a file. `.gitignore` and tooling need to handle this.
- FontForge's UFO support is slightly less featureful than its native SFD (e.g., some obscure shape primitives don't round-trip).

### Neutral
- The `.otf` / `.woff2` build artefacts are unchanged regardless of source format.
- ADR-0004 determinism requirements apply equally to UFO3 and SFD source.

## References

- UFO3 specification: https://unifiedfontobject.org/versions/ufo3/
- `rhena_integration_plan.md` § 4 (build pipeline)
- `claude-review-2026-04-14.md` § 1
