"""Portable launcher for the repository-owned PaperSpine5 runtime."""

from __future__ import annotations

import json
import os
import runpy
import sys
from pathlib import Path

# Installed suite roots are immutable, hash-verified release objects.  Keep
# imports from creating __pycache__ entries inside that object.
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def project_root() -> Path:
    plugin_root = Path(__file__).resolve().parents[1]
    embedded_runtime = plugin_root / "06_插件化" / "runtime" / "paperspine5_runtime.py"
    embedded_core = (
        plugin_root
        / "03_联合开发"
        / "src"
        / "paperspine_figure_integration"
        / "product_kernel.py"
    )
    if embedded_runtime.is_file() and embedded_core.is_file():
        return plugin_root
    configured = os.environ.get("PAPERSPINE5_PROJECT_ROOT")
    if not configured:
        config = plugin_root / "config" / "local-project.json"
        configured = json.loads(config.read_text(encoding="utf-8-sig"))["project_root"]
    root = Path(configured).resolve()
    runtime = root / "06_插件化" / "runtime" / "paperspine5_runtime.py"
    if not runtime.is_file():
        raise SystemExit(f"PaperSpine5 runtime is missing: {runtime}")
    return root


if __name__ == "__main__":
    root = project_root()
    runtime = root / "06_插件化" / "runtime" / "paperspine5_runtime.py"
    runtime_directory = str(runtime.parent)
    # runpy does not give the executed file normal script import semantics.
    # Keep sibling runtime modules (for example web_agent_runtime) importable
    # when they are loaded lazily after the public bridge has started.
    if runtime_directory not in sys.path:
        sys.path.insert(0, runtime_directory)
    runpy.run_path(str(runtime), run_name="__main__")
