# Hildegard Neumes font project — task runner
#
# Matches Rhena's `just`-based workflow for consistency.
# See rhena_integration_plan.md § 4 for the full build pipeline rationale.

set shell := ["bash", "-euo", "pipefail", "-c"]

# Default: list available recipes
default:
    @just --list

# Scaffold src/hildegard-neumes.ufo/ from the 19-atom contract. Phase A —
# produces a UFO3 with placeholder rectangle outlines ready for a designer
# to open in FontForge and redraw per docs/paleographic_drawing_briefs.md.
scaffold-ufo:
    python scripts/scaffold-ufo.py

# Regenerate the UFO3 source from the contract, overwriting any existing
# scaffold. Use sparingly — this wipes in-progress glyph work.
rescaffold-ufo:
    python scripts/scaffold-ufo.py --force

# Build the OTF + WOFF + WOFF2 from src/hildegard-neumes.ufo/ via FontForge
# (headless, UFO3 source per ADR-0001; dual WOFF delivery per Rhena ADR-0012)
build-font:
    bash scripts/build-font.sh

# Generate rhineland.rs from the authoritative contract (post-ADR-0012: no
# more OTF-to-Rust path codegen; the font IS the artifact, this script just
# emits codepoint + composition metadata)
generate-rhena:
    mkdir -p generated
    python scripts/generate-rhena-glyphs.py \
        --contract docs/rhena-coordination/rhineland.contract.json \
        --out generated/rhineland.rs

# Full pipeline: build font then regenerate Rhena glyphs
build: build-font generate-rhena

# Copy the generated file into Rhena's source tree. Requires hildegard
# checkout at ../hildegard. Coordinate snapshot updates in Rhena after this.
copy-to-rhena RHENA="../hildegard":
    #!/usr/bin/env bash
    set -euo pipefail
    target="{{RHENA}}/crates/rhena-core/src/render_ir/glyphs/rhineland.rs"
    if [ ! -d "{{RHENA}}" ]; then
        echo "error: Rhena project not found at {{RHENA}}" >&2
        exit 2
    fi
    if [ ! -f generated/rhineland.rs ]; then
        echo "error: generated/rhineland.rs not found. Run 'just generate-rhena' first." >&2
        exit 2
    fi
    cp generated/rhineland.rs "$target"
    echo "Copied to $target"
    echo "Next: cd {{RHENA}} && just check  (review and accept golden snapshot diffs)"

# Remove build artifacts and generated files
clean:
    rm -rf build/*.otf build/*.woff build/*.woff2 build/*.ttf build/_check
    rm -f generated/rhineland.rs

# Check that the generated file is up to date with the contract (useful in CI).
# Uses a pinned SOURCE_DATE_EPOCH so the @generated-header timestamp is
# deterministic across runs.
check-generated:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p build/_check
    SOURCE_DATE_EPOCH=$(python3 -c 'import datetime; print(int(datetime.datetime(2026, 4, 20, tzinfo=datetime.timezone.utc).timestamp()))') \
        python scripts/generate-rhena-glyphs.py \
            --contract docs/rhena-coordination/rhineland.contract.json \
            --out build/_check/rhineland.rs
    diff -q build/_check/rhineland.rs generated/rhineland.rs || \
        (echo "error: generated/rhineland.rs is stale. Run 'just generate-rhena' (with the pinned epoch if needed) and commit." >&2; exit 1)

# Print the glyph contract (names + widths)
show-contract:
    @python -c "import json; n=json.load(open('src/glyph-names.json')); w=json.load(open('src/widths.json')); [print(f\"{g['rust_const']:25s} {g['font_name']:25s} w={w['widths'][g['font_name']]:4d}\") for g in n['glyphs']]"

# Run the codegen test suite (pytest). Skips the Rhena smoke test.
test:
    pytest -v --deselect tests/test_rhena_smoke.py

# Run the Rhena smoke test explicitly (requires Rhena checkout at ../hildegard)
test-rhena-smoke:
    pytest -v tests/test_rhena_smoke.py

# Validate the built OTF against the contract (cmap + advance-width checks)
validate-font:
    python scripts/validate-font.py \
        --in build/hildegard-neumes.otf \
        --contract docs/rhena-coordination/rhineland.contract.json
    python scripts/validate-font.py \
        --in build/hildegard-neumes.woff \
        --contract docs/rhena-coordination/rhineland.contract.json
    python scripts/validate-font.py \
        --in build/hildegard-neumes.woff2 \
        --contract docs/rhena-coordination/rhineland.contract.json

# Full CI-style check: build, validate, generate, test
ci-check: build-font validate-font generate-rhena test check-generated
