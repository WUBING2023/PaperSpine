"""Standalone Skill launcher for the shared MCP/HostBridge runtime."""

from __future__ import annotations

import json
import os
import runpy
import sys
from pathlib import Path

# The managed suite is content-addressed and must remain byte-for-byte immutable
# after normal Skill use.  Prevent local imports from creating __pycache__ there.
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def project_root() -> Path:
    skill_root = Path(__file__).resolve().parents[1]
    explicit = os.environ.get("PAPERSPINE5_PROJECT_ROOT")
    if explicit:
        return Path(explicit).resolve()
    installed = skill_root / "references" / "installed-suite.json"
    if installed.is_file():
        payload = json.loads(installed.read_text(encoding="utf-8-sig"))
        if payload.get("contract") != "paperspine5.installed-suite-pointer":
            raise SystemExit(f"PaperSpine5 installed-suite pointer is invalid: {installed}")
        return Path(payload["suite_root"]).resolve()
    development = skill_root / "references" / "local-project.json"
    if development.is_file():
        return Path(json.loads(development.read_text(encoding="utf-8-sig"))["project_root"]).resolve()
    for parent in skill_root.parents:
        if (parent / "suite-manifest.json").is_file():
            return parent
    raise SystemExit("PaperSpine5 suite root is not configured")


root = project_root()
runtime = root / "06_插件化" / "runtime" / "paperspine5_runtime.py"
if not runtime.is_file():
    raise SystemExit(f"PaperSpine5 runtime is missing: {runtime}")
runtime_directory = str(runtime.parent)
# runpy preserves the launcher's import path rather than installing the
# executed runtime's directory.  The shared runtime imports sibling adapters
# lazily, so retain that directory for the full bridge process lifetime.
if runtime_directory not in sys.path:
    sys.path.insert(0, runtime_directory)
runpy.run_path(str(runtime), run_name="__main__")
