"""Helper for loading `scripts/generate-rhena-glyphs.py` in tests.

The script's filename contains hyphens, which prevents normal
`import generate_rhena_glyphs` syntax. importlib.util.spec_from_file_location
works, but the module MUST be registered in `sys.modules` *before* its code
is executed — otherwise `@dataclass` decorators fail with
`'NoneType' object has no attribute '__dict__'` because Python's dataclass
machinery looks up the declaring module in `sys.modules` at decoration time.

This helper centralizes both workarounds so each test file can do a clean:

    from _gen_import import import_generator
    _gen = import_generator()
    load_contract = _gen.load_contract
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SCRIPT_PATH = _PROJECT_ROOT / "scripts" / "generate-rhena-glyphs.py"
_CACHED_MODULE: ModuleType | None = None


def import_generator() -> ModuleType:
    """Load the generator script as a module. Caches on first call."""
    global _CACHED_MODULE
    if _CACHED_MODULE is not None:
        return _CACHED_MODULE

    if not _SCRIPT_PATH.is_file():
        raise RuntimeError(f"generator script not found: {_SCRIPT_PATH}")

    spec = importlib.util.spec_from_file_location(
        "generate_rhena_glyphs", _SCRIPT_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not create import spec for {_SCRIPT_PATH}")

    module = importlib.util.module_from_spec(spec)
    # CRITICAL: register before exec so @dataclass can resolve cls.__module__
    sys.modules["generate_rhena_glyphs"] = module
    spec.loader.exec_module(module)

    _CACHED_MODULE = module
    return module
