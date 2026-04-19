# Hildegard Neumes font project — task runner
#
# Matches Rhena's `just`-based workflow for consistency.
# See rhena_integration_plan.md § 4 for the full build pipeline rationale.

set shell := ["bash", "-euo", "pipefail", "-c"]

# Default: list available recipes
default:
    @just --list

# Build the OTF + WOFF2 from src/hildegard-neumes.ufo/ via FontForge (headless, UFO3 source per ADR-0001)
build-font:
    bash scripts/build-font.sh

# Generate rhineland_glyphs.rs from build/hildegard-neumes.otf
generate-rhena:
    mkdir -p generated
    python scripts/generate-rhena-glyphs.py \
        --in build/hildegard-neumes.otf \
        --names-map src/glyph-names.json \
        --widths-table src/widths.json \
        --out generated/rhineland_glyphs.rs

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
    if [ ! -f generated/rhineland_glyphs.rs ]; then
        echo "error: generated/rhineland_glyphs.rs not found. Run 'just generate-rhena' first." >&2
        exit 2
    fi
    cp generated/rhineland_glyphs.rs "$target"
    echo "Copied to $target"
    echo "Next: cd {{RHENA}} && just check  (review and accept golden snapshot diffs)"

# Remove build artifacts and generated files
clean:
    rm -rf build/*.otf build/*.woff2 build/*.ttf
    rm -f generated/rhineland_glyphs.rs

# Check that the generated file is up to date with the font source (useful in CI)
check-generated: build-font
    mkdir -p build/_check
    python scripts/generate-rhena-glyphs.py \
        --in build/hildegard-neumes.otf \
        --names-map src/glyph-names.json \
        --widths-table src/widths.json \
        --out build/_check/rhineland_glyphs.rs \
        --timestamp 2026-01-01T00:00:00Z
    diff -q build/_check/rhineland_glyphs.rs generated/rhineland_glyphs.rs || \
        (echo "error: generated/rhineland_glyphs.rs is stale. Run 'just build' and commit." >&2; exit 1)

# Print the glyph contract (names + widths)
show-contract:
    @python -c "import json; n=json.load(open('src/glyph-names.json')); w=json.load(open('src/widths.json')); [print(f\"{g['rust_const']:25s} {g['font_name']:25s} w={w['widths'][g['font_name']]:4d}\") for g in n['glyphs']]"

# Run the codegen test suite (pytest). Skips the Rhena smoke test.
test:
    pytest -v --deselect tests/test_rhena_smoke.py

# Run the Rhena smoke test explicitly (requires Rhena checkout at ../hildegard)
test-rhena-smoke:
    pytest -v tests/test_rhena_smoke.py

# Validate the built OTF against the contract (bbox vs advance, path commands)
validate-font:
    python scripts/validate-font.py \
        --in build/hildegard-neumes.otf \
        --names-map src/glyph-names.json \
        --widths-table src/widths.json

# Full CI-style check: build, validate, generate, test
ci-check: build-font validate-font generate-rhena test check-generated
