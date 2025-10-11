import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "repair_portal"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if "repair_portal" not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        "repair_portal",
        PACKAGE_ROOT / "__init__.py",
        submodule_search_locations=[str(PACKAGE_ROOT)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["repair_portal"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    module.__path__ = [str(PACKAGE_ROOT)]

CORE_ROOT = PACKAGE_ROOT / "core"
if "repair_portal.core" not in sys.modules:
    core_spec = importlib.util.spec_from_file_location(
        "repair_portal.core",
        CORE_ROOT / "__init__.py",
        submodule_search_locations=[str(CORE_ROOT)],
    )
    core_module = importlib.util.module_from_spec(core_spec)
    sys.modules["repair_portal.core"] = core_module
    core_spec.loader.exec_module(core_module)  # type: ignore[union-attr]
    core_module.__path__ = [str(CORE_ROOT)]
