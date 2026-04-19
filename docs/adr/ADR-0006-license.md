# ADR-0006: Licence — SIL OFL 1.1 with Reserved Font Name

- Status: Accepted
- Date: 2026-04-14
- Deciders: project maintainers
- Consulted: claude-review-2026-04-14 § 4
- Tags: license, distribution, compatibility

## Context

The font project will ship an `.otf` artefact, a generated Rust source file, UFO3 source, and project documentation. These distribute under one or more licences. The choice affects:

- Compatibility with Rhena (MIT + Apache-2.0 dual-licensed).
- Fork/derivative-work expectations (RFN protections for a paleographically specific name).
- Ecosystem familiarity (Gregorio, Bravura, and most chant fonts are OFL).

## Decision

The font (OTF, WOFF2, UFO3 source) is licensed under the **SIL Open Font License 1.1 with Reserved Font Name "Hildegard Neumes"**. Committed artefacts:

- `OFL.txt` — official SIL OFL 1.1 text.
- `FONTLOG.txt` — SIL-standard changelog.
- `README.md` licence section cites both.

The generated Rust file (`generated/rhineland_glyphs.rs` and its downstream copy in Rhena) is a derivative work of the font that extracts vector path data. Under OFL §1 this extraction is permitted without relicensing the consumer (no "Font Software" is being distributed — only derived vector coordinates embedded in a Rust source file). When the file lives in Rhena's source tree, it retains its OFL provenance via a note in Rhena's NOTICE / README, even though Rhena itself is MIT + Apache-2.0.

The RFN clause (OFL §3) means any derivative font released under a different name MUST rename to avoid using "Hildegard Neumes". This is standard for named paleographic fonts.

Documentation (`*.md`, `*.json`, scripts) is licensed under MIT + Apache-2.0 (dual, matching Rhena). This dual licensing applies only to non-font content; the OTF and UFO are OFL.

## Alternatives considered

1. **MIT + Apache-2.0 for everything**. Rejected: these licences have no font-aware protections (RFN, "not sold by itself" clauses) that the OFL was designed for. Derivatives could reuse the name "Hildegard Neumes" for incompatible forks.
2. **Public domain / CC0**. Rejected: gives up attribution and RFN protections without gaining compatibility. Also prevents some jurisdictional edge cases.
3. **GPL-family**. Rejected: incompatible with Rhena's MIT + Apache-2.0 downstream consumers. Chant ecosystem is firmly OFL; GPL would be an outlier.
4. **OFL without RFN**. Rejected: the whole point of the RFN clause is to keep "Hildegard Neumes" meaning a specific paleographic artefact. Forks can call themselves anything they want; they just can't call themselves this.

## Consequences

### Positive
- Compatible with Rhena's MIT + Apache-2.0 (OFL imposes no constraints on consumers of derived vector data per §1).
- Compatible with the chant ecosystem (Gregorio, Bravura, Greciliae, Caeciliae all OFL).
- RFN protects the paleographic specificity of the name.
- Contributors recognize the licence immediately.

### Negative
- Derivative fonts must rename. This is a feature, not a bug, but it surprises some users.
- The generated-code relicensing argument (OFL §1 covers extracted vector data) is defensible but has not been tested in court. If strict legal review reveals ambiguity, consult SIL directly — they answer licence questions without charge.

### Neutral
- OFL is text-only; there is no binary package or cargo-style licence metadata that needs updating.

## References

- `OFL.txt` — committed licence text
- `FONTLOG.txt` — committed changelog
- SIL OFL 1.1 FAQ: https://openfontlicense.org/ofl-faq/
- Reproducible Builds OFL discussion: https://reproducible-builds.org/
- `claude-review-2026-04-14.md` § 4
