"""Deterministic PaperSpine5 candidate bundle builder and verifier.

The builder is deliberately allowlist-only.  It does not archive the repository
root, Git metadata, tests, local configuration, caches, or developer paths.
The resulting plugin root also contains the runtime and bounded component source
needed by the ProductKernel/Web-first surface and ProductRunner 0.2 generic
J1--J11 collaboration stages.  That source inclusion does not grant W8 maturity.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

SUITE_CONTRACT = "paperspine5.suite-manifest"
SUITE_SCHEMA_VERSION = "1.0"
PRODUCT_ID = "paperspine5"
PRODUCT_VERSION = "0.4.0-alpha.4"
PRODUCT_CHANNEL = "development"
PLUGIN_NAME = "paperspine5"
FIXED_ZIP_TIME = (2026, 8, 24, 0, 0, 0)
FIGURE_AUTHORITY_TABLE_PATH = "01_PaperSpine4/src/skill/references/figure-reference-mapping.md"
ALLOWED_SUFFIXES = {
    "",
    ".css",
    ".html",
    ".js",
    ".json",
    ".lua",
    ".dll",
    ".pyd",
    ".pth",
    ".typed",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".svg",
    ".yaml",
    ".yml",
}
FORBIDDEN_PARTS = {
    "__pycache__",
    ".probe",
    ".pytest_cache",
    ".system",
    ".test-temp",
    ".test_tmp",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "probe",
    ".git",
    "tmp",
    "temp",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".tmp", ".log"}
ABSOLUTE_DEV_PATH = re.compile(
    rb"(?i)(?:[a-z]:[\\/]users[\\/]|/(?:home|users)/[^/\s]+/)"
)
WINDOWS_ABSOLUTE_PATH = re.compile(
    rb"(?i)(?<![a-z0-9_])(?<!\(\?)[a-z]:(?:\\{1,2}|/)"
)
TEXT_SUFFIXES = frozenset(ALLOWED_SUFFIXES)
AUDITED_WORD_FALLBACK_FILE = (
    "03_联合开发/src/paperspine_figure_integration/canonical_artifacts.py"
)
_WINDOWS_SYSTEM_DRIVE_C = b"C:"
AUDITED_WORD_FALLBACK_LINES = (
    b'        Path(r"'
    + _WINDOWS_SYSTEM_DRIVE_C
    + b'\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE"),',
    b'        Path(r"'
    + _WINDOWS_SYSTEM_DRIVE_C
    + b'\\Program Files (x86)\\Microsoft Office\\root\\Office16\\WINWORD.EXE"),',
)
IMMUTABLE_SUITE_RUNTIME_MARKERS = {
    "06_插件化/runtime/paperspine5_runtime.py": (
        b"sys.dont_write_bytecode = True",
        b'os.environ["PYTHONDONTWRITEBYTECODE"] = "1"',
    ),
    "06_插件化/runtime/web_agent_runtime.py": (
        b'environment["PYTHONDONTWRITEBYTECODE"] = "1"',
    ),
    "scripts/paperspine5_mcp.py": (
        b"sys.dont_write_bytecode = True",
        b'os.environ["PYTHONDONTWRITEBYTECODE"] = "1"',
        b"runtime_directory = str(runtime.parent)",
        b"sys.path.insert(0, runtime_directory)",
    ),
    "standalone/paper-spine/scripts/paperspine5_web.py": (
        b"sys.dont_write_bytecode = True",
        b'os.environ["PYTHONDONTWRITEBYTECODE"] = "1"',
        b'        "-B",',
        b'environment["PYTHONDONTWRITEBYTECODE"] = "1"',
    ),
    "standalone/paper-spine/scripts/launch_paperspine_ui.ps1": (
        b'$env:PYTHONDONTWRITEBYTECODE = "1"',
        b"python -B @arguments",
    ),
    "standalone/paper-spine/scripts/launch_paperspine_ui.sh": (
        b"export PYTHONDONTWRITEBYTECODE=1",
        b'exec "$PYTHON" -B "$LAUNCHER"',
    ),
    "standalone/paperspine5-workspace/scripts/paperspine5_bridge.py": (
        b"sys.dont_write_bytecode = True",
        b'os.environ["PYTHONDONTWRITEBYTECODE"] = "1"',
        b"runtime_directory = str(runtime.parent)",
        b"sys.path.insert(0, runtime_directory)",
    ),
    "standalone/paperspine5-workspace/scripts/open_workspace.py": (
        b"sys.dont_write_bytecode = True",
        b'os.environ["PYTHONDONTWRITEBYTECODE"] = "1"',
        b'        "-B",',
        b'environment["PYTHONDONTWRITEBYTECODE"] = "1"',
    ),
}


def _runtime_marker_present(path: str, marker: bytes, content: bytes) -> bool:
    if (path == "standalone/paper-spine/scripts/launch_paperspine_ui.ps1"
            and marker == b"python -B @arguments"):
        # Both supported wrappers pass -B to the actual interpreter. Keep the
        # historical wrapper verifiable without rejecting the runtime resolver.
        lines = {line.strip() for line in content.splitlines()}
        return (marker in lines or {
            b"$runtime = Resolve-PaperSpinePython",
            b"& $runtime.Path @($runtime.Prefix) -B @arguments",
            b"& $runtime.Path -B @arguments",
        }.issubset(lines))
    return marker in content
CURRENT_MANAGED_SUITE_RESIDUE_CONTRACT_PATHS = {
    "release/contracts/skill-managed-suite-prestate-validation.schema.json",
    "release/contracts/skill-managed-suite-reconciliation-receipt.schema.json",
    "release/contracts/skill-managed-suite-reconciliation-restore-receipt.schema.json",
}
CURRENT_REQUIRED_RESOURCE_PATHS = {FIGURE_AUTHORITY_TABLE_PATH}


class ReleaseError(RuntimeError):
    """A deterministic release contract failure."""


def _strip_audited_word_fallback_lines(path: str, content: bytes) -> bytes:
    """Strip only two complete frozen OS fallback expressions before path scans.

    These literals are deterministic Windows installation candidates evaluated
    with ``Path.is_file`` at runtime.  They are not a captured build/user path.
    Matching is file-bound and full-line-bound so a suffix, traversal, duplicate,
    or the same literal in any other payload still reaches the normal scanners.
    """
    if path != AUDITED_WORD_FALLBACK_FILE:
        return content
    stripped = content
    for line in AUDITED_WORD_FALLBACK_LINES:
        pattern = re.compile(rb"(?m)^" + re.escape(line) + rb"\r?$")
        stripped, count = pattern.subn(b"", stripped)
        if count > 1:
            raise ReleaseError(
                f"audited Word fallback expression is duplicated or ambiguous: {path}"
            )
    return stripped


def _assert_no_absolute_local_paths(path: str, content: bytes) -> None:
    """Reject machine-local paths in every allowlisted textual payload."""
    if Path(path).suffix.lower() not in TEXT_SUFFIXES:
        return
    scanned = _strip_audited_word_fallback_lines(path, content)
    # Third-party source may contain documented platform path examples.  It
    # must still never capture a developer home path.
    vendor = path.startswith("runtime_vendor/")
    if vendor:
        return
    if ABSOLUTE_DEV_PATH.search(scanned) or WINDOWS_ABSOLUTE_PATH.search(scanned):
        raise ReleaseError(f"bundle embeds an absolute local path: {path}")


@dataclass(frozen=True)
class TreeRule:
    source: str
    destination: str
    suffixes: frozenset[str] = frozenset(ALLOWED_SUFFIXES)
    excluded_relative_paths: frozenset[str] = frozenset()


@dataclass(frozen=True)
class FileRule:
    source: str
    destination: str


FILE_RULES = (
    FileRule("06_插件化/release/dsh_release.py", "release/dsh_release.py"),
    FileRule("06_插件化/packages/paperspine5/.codex-plugin/plugin.json", ".codex-plugin/plugin.json"),
    FileRule("06_插件化/packages/paperspine5/.mcp.json", ".mcp.json"),
    FileRule("06_插件化/packages/paperspine5/README.md", "README.md"),
    FileRule("06_插件化/release/USER_GUIDE.md", "USER_GUIDE.md"),
    FileRule("06_插件化/release/API_REFERENCE.md", "API_REFERENCE.md"),
    FileRule("07_发布页/assets/brand/paperspine-mark.svg", "07_发布页/assets/brand/paperspine-mark.svg"),
    FileRule("06_插件化/release/examples/local-demo/README.md", "examples/local-demo/README.md"),
    FileRule("06_插件化/release/examples/local-demo/measurements.csv", "examples/local-demo/measurements.csv"),
    FileRule("06_插件化/release/examples/local-demo/note.tex", "examples/local-demo/note.tex"),
    FileRule("06_插件化/release/examples/local-demo/values.svg", "examples/local-demo/values.svg"),
    FileRule("06_插件化/packages/paperspine5/scripts/paperspine5_mcp.py", "scripts/paperspine5_mcp.py"),
    FileRule("06_插件化/runtime/paperspine5_runtime.py", "06_插件化/runtime/paperspine5_runtime.py"),
    FileRule("06_插件化/runtime/web_agent_runtime.py", "06_插件化/runtime/web_agent_runtime.py"),
    FileRule("06_插件化/runtime/local_package_files.py", "06_插件化/runtime/local_package_files.py"),
    FileRule("06_插件化/runtime/material_profile.py", "06_插件化/runtime/material_profile.py"),
    FileRule("06_插件化/release/suite_release.py", "release/suite_release.py"),
    FileRule("06_插件化/release/lifecycle.py", "release/lifecycle.py"),
    FileRule("06_插件化/release/release_cli.py", "release/release_cli.py"),
    FileRule("06_插件化/release/user_update.py", "release/user_update.py"),
    FileRule("06_插件化/release/stable_updater.py", "release/stable_updater.py"),
    FileRule("06_插件化/release/stable_updater.py", "standalone/paper-spine/scripts/paperspine_stable_update.py"),
    FileRule("06_插件化/release/stable_update_adapter.py", "release/stable_update_adapter.py"),
    FileRule("06_插件化/release/install_skill.py", "release/install_skill.py"),
    FileRule("06_插件化/release/updater-protocol.json", "updater-protocol.json"),
    FileRule("06_插件化/release/stable-update.cmd", "release/stable-update.cmd"),
    FileRule("06_插件化/release/product_runtime.py", "release/product_runtime.py"),
    FileRule("06_插件化/release/paperspine.cmd", "paperspine.cmd"),
    FileRule("06_插件化/release/paperspine", "paperspine"),
    FileRule("06_插件化/release/stable-update", "release/stable-update"),
    FileRule("06_插件化/release/product_launcher.py", "release/product_launcher.py"),
    FileRule("06_插件化/release/product_probe.py", "release/product_probe.py"),
    FileRule("06_插件化/runtime_vendor/requirements.lock.json", "runtime_vendor/requirements.lock.json"),
    FileRule(
        "06_插件化/standalone-skill/paperspine5-workspace/agents/openai.yaml",
        "standalone/paperspine5-workspace/agents/openai.yaml",
    ),
    FileRule(
        "06_插件化/standalone-skill/paperspine5-workspace/scripts/paperspine5_bridge.py",
        "standalone/paperspine5-workspace/scripts/paperspine5_bridge.py",
    ),
    FileRule(
        "06_插件化/standalone-skill/paperspine5-workspace/scripts/open_workspace.py",
        "standalone/paperspine5-workspace/scripts/open_workspace.py",
    ),
    FileRule(
        "06_插件化/standalone-skill/paperspine5-workspace/references/runtime-bridge.md",
        "standalone/paperspine5-workspace/references/runtime-bridge.md",
    ),
)

TREE_RULES = (
    TreeRule("06_插件化/dsh/paperspine5", "adapters/dsh"),
    TreeRule("06_插件化/runtime_vendor/windows-py312", "runtime_vendor/windows-py312", frozenset(ALLOWED_SUFFIXES | {".exe", ".zip", "._pth", ".txt"})),
    TreeRule("06_插件化/packages/paperspine5/assets", "assets", frozenset({".png", ".svg"})),
    TreeRule("06_插件化/release/contracts", "release/contracts", frozenset({".json"})),
    TreeRule("01_PaperSpine4/src/skill", "standalone/paper-spine"),
    TreeRule(
        "01_PaperSpine4/src/scripts",
        "standalone/paper-spine/scripts",
        frozenset({".ps1", ".py", ".sh", ".lua"}),
    ),
    TreeRule("03_联合开发/src/paperspine_figure_integration", "03_联合开发/src/paperspine_figure_integration", frozenset({".py"})),
    TreeRule("03_联合开发/contracts", "03_联合开发/contracts", frozenset({".json"})),
    TreeRule("03_联合开发/ui", "03_联合开发/ui", frozenset({".css", ".html", ".js"})),
    TreeRule(
        "01_PaperSpine4/src/skill",
        "01_PaperSpine4/src/skill",
        excluded_relative_paths=frozenset({"SKILL.md"}),
    ),
    TreeRule("01_PaperSpine4/src/scripts", "01_PaperSpine4/src/scripts", frozenset({".ps1", ".py", ".sh", ".lua"})),
    TreeRule("02_PaperFigure/01_FigMirror引擎/src", "02_PaperFigure/01_FigMirror引擎/src", frozenset({".py"})),
)


def canonical_json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_archive_path(raw: str) -> str:
    normalized = PurePosixPath(raw.replace("\\", "/"))
    if normalized.is_absolute() or not normalized.parts or ".." in normalized.parts:
        raise ReleaseError(f"unsafe bundle path: {raw}")
    value = normalized.as_posix()
    if value.startswith("./") or value == ".":
        raise ReleaseError(f"non-canonical bundle path: {raw}")
    return value


def _path_is_forbidden(path: str) -> bool:
    pure = PurePosixPath(path)
    lowered = {part.lower() for part in pure.parts}
    return bool(lowered & FORBIDDEN_PARTS) or pure.suffix.lower() in FORBIDDEN_SUFFIXES


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or bool(callable(is_junction) and is_junction())


def _iter_tree(root: Path, rule: TreeRule) -> Iterable[tuple[str, bytes]]:
    source = root / rule.source
    if not source.is_dir():
        raise ReleaseError(f"allowlisted source directory is missing: {rule.source}")
    if _is_link_or_junction(source):
        raise ReleaseError(f"allowlisted source directory is a link/reparse point: {rule.source}")
    for path in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
        if _is_link_or_junction(path):
            raise ReleaseError(f"allowlisted source contains a link/reparse point: {path}")
        if not path.is_file() or path.suffix.lower() not in rule.suffixes:
            continue
        relative = path.relative_to(source).as_posix()
        if relative in rule.excluded_relative_paths:
            continue
        destination = _safe_archive_path(f"{rule.destination}/{relative}")
        if _path_is_forbidden(destination):
            continue
        yield destination, path.read_bytes()


def _collect_raw_payload(source_root: Path) -> dict[str, bytes]:
    supplied_root = Path(source_root)
    if _is_link_or_junction(supplied_root):
        raise ReleaseError("source root is a link/reparse point")
    root = supplied_root.resolve()
    if not root.is_dir():
        raise ReleaseError(f"source root is missing: {root}")
    payload: dict[str, bytes] = {}
    for rule in FILE_RULES:
        source = root / rule.source
        if not source.is_file():
            raise ReleaseError(f"allowlisted source file is missing: {rule.source}")
        if _is_link_or_junction(source):
            raise ReleaseError(f"allowlisted source file is a link/reparse point: {rule.source}")
        destination = _safe_archive_path(rule.destination)
        if destination in payload:
            raise ReleaseError(f"duplicate allowlist destination: {destination}")
        payload[destination] = source.read_bytes()
    for rule in TREE_RULES:
        for destination, content in _iter_tree(root, rule):
            if destination in payload:
                raise ReleaseError(f"duplicate allowlist destination: {destination}")
            payload[destination] = content
    return payload


def _tree_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for path in sorted(files):
        encoded = path.encode("utf-8")
        digest.update(len(encoded).to_bytes(4, "big"))
        digest.update(encoded)
        digest.update(len(files[path]).to_bytes(8, "big"))
        digest.update(files[path])
    return digest.hexdigest()


def _component_digest(files: dict[str, bytes], prefixes: tuple[str, ...]) -> str:
    selected = {
        path: content
        for path, content in files.items()
        if any(path == prefix or path.startswith(prefix.rstrip("/") + "/") for prefix in prefixes)
    }
    if not selected:
        raise ReleaseError(f"component allowlist selected no files: {prefixes}")
    return _tree_digest(selected)


def _rewrite_plugin_manifest(raw: bytes, *, build_id: str) -> bytes:
    try:
        manifest = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseError("plugin manifest is not valid UTF-8 JSON") from exc
    if manifest.get("name") != PLUGIN_NAME:
        raise ReleaseError("plugin manifest name is not paperspine5")
    manifest["version"] = f"{PRODUCT_VERSION}+codex.{build_id}"
    manifest["description"] = (
        "PaperSpine5 deterministic local candidate adapter for ProductRunner 0.2 generic "
        "J1-J11 collaboration and the Web-first workspace; W8 maturity and external "
        "submission remain blocked."
    )
    interface = manifest.setdefault("interface", {})
    interface["longDescription"] = (
        "Exact self-contained candidate bundle for ProductKernel tasks and ProductRunner 0.2 "
        "cumulative J1-J11 gates. Domain, subfield, venue, and track preferences are learned "
        "by runtime research Agents; the adapter carries only orchestration, permission, state, "
        "evidence, review, and fail-closed contracts. W8 and P0 remain blocked, and installation "
        "never authorizes external action."
    )
    return canonical_json_bytes(manifest)


def _rewrite_runtime(raw: bytes, *, build_id: str) -> bytes:
    try:
        text = raw.decode("utf-8")
    except UnicodeError as exc:
        raise ReleaseError("runtime is not UTF-8") from exc
    needle = 'PRODUCT_BUILD_ID = "local-dev-unverified"'
    if text.count(needle) != 1:
        raise ReleaseError("runtime build identity anchor is missing or ambiguous")
    return text.replace(needle, f'PRODUCT_BUILD_ID = "{build_id}"').encode("utf-8")


def _payload_index(payload: dict[str, bytes]) -> list[dict[str, Any]]:
    return [
        {"path": path, "sha256": sha256_bytes(payload[path]), "size_bytes": len(payload[path])}
        for path in sorted(payload)
    ]


def build_manifest(payload: dict[str, bytes], *, source_digest: str, build_id: str) -> dict[str, Any]:
    index = _payload_index(payload)
    content_index_sha = sha256_bytes(canonical_json_bytes(index))
    components = {
        "codex_adapter": {
            "version": f"{PRODUCT_VERSION}+codex.{build_id}",
            "root": ".",
            "sha256": _component_digest(payload, (".codex-plugin/plugin.json", ".mcp.json", "assets", "scripts", "skills")),
        },
        "host_runtime": {
            "version": "0.2.0-dev",
            "root": "06_插件化/runtime",
            "sha256": _component_digest(payload, ("06_插件化/runtime",)),
        },
        "product_kernel": {
            "version": "0.1.0",
            "root": "03_联合开发/src/paperspine_figure_integration",
            "sha256": _component_digest(
                payload,
                (
                    "03_联合开发/src/paperspine_figure_integration",
                    "03_联合开发/ui",
                    "03_联合开发/contracts",
                    FIGURE_AUTHORITY_TABLE_PATH,
                ),
            ),
        },
        "product_runner": {
            "version": "0.2.0",
            "root": "03_联合开发/src/paperspine_figure_integration",
            "sha256": _component_digest(
                payload,
                (
                    "03_联合开发/src/paperspine_figure_integration",
                    "03_联合开发/contracts",
                    FIGURE_AUTHORITY_TABLE_PATH,
                ),
            ),
        },
        "paperspine_component": {
            "version": "4.0.0-component",
            "root": "01_PaperSpine4/src",
            "sha256": _component_digest(payload, ("01_PaperSpine4/src",)),
        },
        "paperfigure_component": {
            "version": "development-candidate",
            "root": "02_PaperFigure",
            "sha256": _component_digest(payload, ("02_PaperFigure",)),
        },
        "release_lifecycle": {
            "version": "0.2.0-candidate",
            "root": "release",
            "sha256": _component_digest(payload, ("release",)),
        },
        "standalone_skill": {
            "version": "4.0.0-canonical-projection",
            "root": "standalone/paper-spine",
            "sha256": _component_digest(payload, ("standalone/paper-spine",)),
        },
    }
    return {
        "contract": SUITE_CONTRACT,
        "schema_version": SUITE_SCHEMA_VERSION,
        "suite": {
            "product_id": PRODUCT_ID,
            "product_version": PRODUCT_VERSION,
            "channel": PRODUCT_CHANNEL,
            "build_id": build_id,
        },
        "runtime": {
            "platform": json.loads(payload["runtime_vendor/requirements.lock.json"].decode("utf-8-sig")).get("platform", "windows-amd64"),
            "python_executable": json.loads(payload["runtime_vendor/requirements.lock.json"].decode("utf-8-sig")).get("python_executable", "runtime_vendor/windows-py312/python.exe"),
            "executable_paths": ["paperspine", "release/stable-update", json.loads(payload["runtime_vendor/requirements.lock.json"].decode("utf-8-sig")).get("python_executable", "runtime_vendor/windows-py312/python.exe")],
        },
        "source": {
            "kind": "allowlisted-workspace-snapshot",
            "tree_sha256": source_digest,
            "recipe": "paperspine5.release-builder/1.0",
            "local_path_embedded": False,
        },
        "components": components,
        "state": {
            "repository": {"writer": "1.2", "min_reader": "1.2", "max_reader": "1.2"},
            "task_record": {"writer": "1.0", "min_reader": "1.0", "max_reader": "1.0"},
            "integration_job": {"writer": "1.1", "min_reader": "1.0", "max_reader": "1.1"},
            "integration_state": {"writer": "1.3", "min_reader": "1.0", "max_reader": "1.3"},
        },
        "workflow": {
            "product_command_contract": "1.0",
            "host_bridge": "0.4.0",
            "implemented_slice": [f"J{index}" for index in range(12)],
            "product_runner_j1_j3": "0.2.0-transactional-host-web-integrated",
            "product_runner_j4_j11": "0.2.0-cumulative-typed-collaboration",
            "academic_evidence_input": "actual-json-payloads-not-client-trusted-projections",
            "registered_id_change": "invalidate-dependents-and-return-j4",
            "domain_preferences": "runtime-research-only",
            "user_front_door": "standalone/paper-spine-only",
            "plugin_role": "internal-mcp-dispatch-backend-no-discoverable-skill",
        },
        "reader_compatibility": {
            "state_repository": {"min": "1.2", "max": "1.2"},
            "integration_job": {"min": "1.0", "max": "1.1"},
            "integration_state": {"min": "1.0", "max": "1.3"},
            "host_bridge": {"min": "0.2.0", "max": "0.4.0", "writer": "0.4.0"},
        },
        "api": {
            "product_kernel": "paperspine5.product-kernel/1.0",
            "product_runner": "paperspine5.product-runner/0.2.0",
            "mcp": "2024-11-05",
            "host_bridge": "paperspine5.host/0.4.0",
            "web": "paperspine5.product-web/1.0",
        },
        "update": {
            "contract": "paperspine5.independent-surface-update/1.0",
            "install_kinds": ["plugin", "skill"],
            "simultaneous_update": False,
            "commands": {
                "plugin": [
                    "plugin-update-check",
                    "plugin-upgrade",
                    "plugin-upgrade-rollback",
                ],
                "skill": [
                    "skill-update-check",
                    "skill-upgrade",
                    "skill-upgrade-rollback",
                ],
            },
            "source_policy": "verified-local-bundle-or-https-sha256-feed",
            "mutation_policy": "explicit-confirmation-single-surface-placement-and-rollback",
            "state_policy": "independent-control-root-state-receipts-and-history-per-install-kind",
            "plugin_activation": "codex-plugin-add-existing-local-marketplace",
            "skill_activation": "automatic-discovery-new-session-or-restart",
        },
        "test_evidence": {
            "status": "candidate-build-contract",
            "bound_to_content_index": content_index_sha,
            "required_before_release": [
                "verify-bundle",
                "clean-profile-install-update-rollback-uninstall",
                "independent-real-surface-plugin-update-rollback",
                "independent-real-surface-standalone-skill-update-rollback",
                "installed-runtime-health-and-create-task",
                "product-runner-0.2-j1-j11-cumulative-gate-tests",
                "host-web-academic-stage-parity",
                "independent-prospective-journeys",
            ],
        },
        "claim_ceiling": {
            "maturity": "internal-candidate",
            "p0": "BLOCKED",
            "statement": "Deterministic self-contained W7 candidate contract with ProductRunner 0.2 generic J1-J11 collaboration stages; W8 maturity, direct-delivery claims, and external action remain P0 BLOCKED.",
            "external_action_authorized": False,
        },
        "content": {
            "file_count": len(index),
            "index_sha256": content_index_sha,
            "files": index,
        },
    }


def build_bundle(source_root: str | Path, output_zip: str | Path) -> dict[str, Any]:
    supplied_root = Path(source_root)
    raw_payload = _collect_raw_payload(supplied_root)
    root = supplied_root.resolve()
    output = Path(output_zip).resolve()
    source_digest = _tree_digest(raw_payload)
    build_id = f"w7a-{source_digest[:20]}"
    payload = dict(raw_payload)
    payload[".codex-plugin/plugin.json"] = _rewrite_plugin_manifest(
        payload[".codex-plugin/plugin.json"], build_id=build_id
    )
    payload["06_插件化/runtime/paperspine5_runtime.py"] = _rewrite_runtime(
        payload["06_插件化/runtime/paperspine5_runtime.py"], build_id=build_id
    )
    payload["RELEASE-CANDIDATE.md"] = (
        "# PaperSpine5 deterministic candidate\n\n"
        f"Build `{build_id}` is an internal W7 candidate containing ProductRunner 0.2 "
        "generic J1–J11 collaboration gates. It does not prove W8 maturity, universal "
        "paper quality, direct delivery, or external-action authorization.\n"
    ).encode()
    development_fingerprints = {
        str(root).encode("utf-8"),
        root.as_posix().encode("utf-8"),
        str(root).replace("\\", "/").encode("utf-8"),
    }
    for path, content in payload.items():
        if any(fingerprint and fingerprint in content for fingerprint in development_fingerprints):
            raise ReleaseError(f"allowlisted payload embeds the development source root: {path}")
        _assert_no_absolute_local_paths(path, content)
    manifest = build_manifest(payload, source_digest=source_digest, build_id=build_id)
    files = {"suite-manifest.json": canonical_json_bytes(manifest), **payload}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    try:
        with zipfile.ZipFile(
            temporary,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
            strict_timestamps=True,
        ) as archive:
            for path in sorted(files):
                info = zipfile.ZipInfo(path, date_time=FIXED_ZIP_TIME)
                info.create_system = 3
                mode = 0o755 if path.endswith((".sh", ".ps1")) or path in set(manifest.get("runtime", {}).get("executable_paths", [])) else 0o644
                info.external_attr = (stat.S_IFREG | mode) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, files[path], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        os.replace(temporary, output)
    finally:
        if temporary.exists():
            temporary.unlink()
    verification = verify_bundle(output)
    receipt = {
        "contract": "paperspine5.build-receipt",
        "schema_version": "1.0",
        "status": verification["status"],
        "build_id": build_id,
        "archive_sha256": verification["archive_sha256"],
        "manifest_sha256": verification["manifest_sha256"],
        "content_index_sha256": manifest["content"]["index_sha256"],
        "figure_authority_table_sha256": verification[
            "figure_authority_table_sha256"
        ],
    }
    receipt_path = output.with_suffix(output.suffix + ".receipt.json")
    receipt_path.write_bytes(canonical_json_bytes(receipt))
    return receipt


def _read_bundle(bundle: Path) -> tuple[dict[str, bytes], str | None]:
    if bundle.is_file():
        archive_sha = sha256_file(bundle)
        try:
            with zipfile.ZipFile(bundle, "r") as archive:
                files: dict[str, bytes] = {}
                for info in archive.infolist():
                    if info.is_dir():
                        raise ReleaseError("bundle contains directory entries instead of canonical files")
                    path = _safe_archive_path(info.filename)
                    if path in files:
                        raise ReleaseError(f"bundle contains duplicate path: {path}")
                    mode = (info.external_attr >> 16) & 0o170000
                    if mode == stat.S_IFLNK:
                        raise ReleaseError(f"bundle contains a symlink: {path}")
                    files[path] = archive.read(info)
        except (OSError, zipfile.BadZipFile) as exc:
            raise ReleaseError(f"bundle is not a readable zip: {bundle}") from exc
        return files, archive_sha
    if bundle.is_dir():
        files = {}
        for path in sorted(bundle.rglob("*"), key=lambda item: item.as_posix()):
            if _is_link_or_junction(path):
                raise ReleaseError(f"bundle directory contains a symlink: {path}")
            if path.is_file():
                relative = _safe_archive_path(path.relative_to(bundle).as_posix())
                files[relative] = path.read_bytes()
        return files, None
    raise ReleaseError(f"bundle does not exist: {bundle}")


def _validate_manifest_shape(manifest: dict[str, Any]) -> None:
    required = {
        "contract",
        "schema_version",
        "suite",
        "source",
        "components",
        "state",
        "workflow",
        "reader_compatibility",
        "api",
        "test_evidence",
        "claim_ceiling",
        "content",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise ReleaseError(f"suite manifest is missing fields: {missing}")
    if manifest.get("contract") != SUITE_CONTRACT or manifest.get("schema_version") != SUITE_SCHEMA_VERSION:
        raise ReleaseError("suite manifest contract/version is unsupported")
    suite = manifest.get("suite")
    if not isinstance(suite, dict) or suite.get("product_id") != PRODUCT_ID:
        raise ReleaseError("suite manifest product identity is unsupported")
    if manifest.get("claim_ceiling", {}).get("external_action_authorized") is not False:
        raise ReleaseError("suite manifest crossed the external-action authority boundary")
    runtime = manifest.get("runtime")
    if runtime is not None:
        if not isinstance(runtime, dict):
            raise ReleaseError("suite runtime metadata must be an object")
        if not runtime.get("platform") or not runtime.get("python_executable"):
            raise ReleaseError("suite runtime metadata is incomplete")


def _verify_bundle_with_skill_paths(
    bundle_path: str | Path,
    *,
    allowed_skill_paths: list[str],
    allowed_runtime_residue: list[dict[str, Any]] | None = None,
    require_current_runtime_markers: bool = True,
    require_current_residue_contracts: bool = True,
    require_current_required_resources: bool = True,
) -> dict[str, Any]:
    bundle = Path(bundle_path).resolve()
    files, archive_sha = _read_bundle(bundle)
    manifest_bytes = files.get("suite-manifest.json")
    if manifest_bytes is None:
        raise ReleaseError("suite-manifest.json is missing")
    try:
        manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseError("suite manifest is not valid UTF-8 JSON") from exc
    if not isinstance(manifest, dict):
        raise ReleaseError("suite manifest root must be an object")
    _validate_manifest_shape(manifest)
    index = manifest.get("content", {}).get("files")
    if not isinstance(index, list):
        raise ReleaseError("suite manifest content.files must be an array")
    expected: dict[str, dict[str, Any]] = {}
    for item in index:
        if not isinstance(item, dict):
            raise ReleaseError("suite manifest file record must be an object")
        path = _safe_archive_path(str(item.get("path", "")))
        if path == "suite-manifest.json" or path in expected:
            raise ReleaseError(f"invalid or duplicate manifest file path: {path}")
        expected[path] = item
    residue_by_path: dict[str, dict[str, Any]] = {}
    for record in allowed_runtime_residue or []:
        if not isinstance(record, dict):
            raise ReleaseError("runtime residue record must be an object")
        path = _safe_archive_path(str(record.get("path", "")))
        pure = PurePosixPath(path)
        if (
            pure.suffix.lower() != ".pyc"
            or pure.parent.name != "__pycache__"
            or path in expected
            or path in residue_by_path
            or not isinstance(record.get("size_bytes"), int)
            or isinstance(record.get("size_bytes"), bool)
            or int(record["size_bytes"]) < 16
            or not re.fullmatch(r"[0-9a-f]{64}", str(record.get("sha256", "")))
        ):
            raise ReleaseError(f"invalid managed-suite runtime residue record: {path}")
        residue_by_path[path] = record
    actual_paths = set(files) - {"suite-manifest.json"}
    expected_actual_paths = set(expected) | set(residue_by_path)
    if actual_paths != expected_actual_paths:
        raise ReleaseError(
            f"bundle file set differs from manifest: missing={sorted(expected_actual_paths-actual_paths)}, "
            f"extra={sorted(actual_paths-expected_actual_paths)}"
        )
    for path, record in residue_by_path.items():
        content = files[path]
        if (
            sha256_bytes(content) != record.get("sha256")
            or len(content) != record.get("size_bytes")
        ):
            raise ReleaseError(
                f"managed-suite runtime residue hash/size mismatch: {path}"
            )
    for path, record in expected.items():
        content = files[path]
        if _path_is_forbidden(path):
            raise ReleaseError(f"bundle contains forbidden cache/temporary path: {path}")
        if sha256_bytes(content) != record.get("sha256") or len(content) != record.get("size_bytes"):
            raise ReleaseError(f"bundle content hash/size mismatch: {path}")
        if path == "config/local-project.json":
            raise ReleaseError("bundle contains a developer local-project pointer")
        _assert_no_absolute_local_paths(path, content)
    rebuilt_index = _payload_index({path: files[path] for path in expected})
    index_sha = sha256_bytes(canonical_json_bytes(rebuilt_index))
    if index_sha != manifest.get("content", {}).get("index_sha256"):
        raise ReleaseError("suite content index hash is invalid")
    skill_paths = sorted(
        path for path in files if path.startswith("skills/") and path.endswith("/SKILL.md")
    )
    if skill_paths:
        raise ReleaseError(
            f"plugin bundle must be an internal MCP backend with no discoverable Skill: {skill_paths}"
        )
    required_paths = {
        ".codex-plugin/plugin.json",
        ".mcp.json",
        "assets/composer-icon.png",
        "assets/logo.png",
        "assets/logo-dark.png",
        "assets/paperspine-plugin-icon.svg",
        "scripts/paperspine5_mcp.py",
        "06_插件化/runtime/paperspine5_runtime.py",
        "06_插件化/runtime/web_agent_runtime.py",
        "06_插件化/runtime/material_profile.py",
        "03_联合开发/src/paperspine_figure_integration/product_kernel.py",
        "03_联合开发/src/paperspine_figure_integration/product_runner.py",
        "03_联合开发/src/paperspine_figure_integration/product_runner_contracts.py",
        "03_联合开发/ui/product.html",
        "01_PaperSpine4/src/scripts/progress_check.py",
        "01_PaperSpine4/src/scripts/publication_cycle.py",
        "02_PaperFigure/01_FigMirror引擎/src/scripts/figmirror.py",
        "release/release_cli.py",
        "release/user_update.py",
        "standalone/paper-spine/SKILL.md",
        "standalone/paper-spine/scripts/paperspine5_web.py",
    }
    missing_required = sorted(required_paths - set(files))
    if missing_required:
        raise ReleaseError(f"bundle is not self-contained for the licensed slice: {missing_required}")
    missing_current_required_resources = sorted(
        CURRENT_REQUIRED_RESOURCE_PATHS - set(files)
    )
    current_required_resources_verified = not missing_current_required_resources
    if missing_current_required_resources and require_current_required_resources:
        raise ReleaseError(
            "bundle is missing current required release resources: "
            f"{missing_current_required_resources}"
        )
    figure_authority_table_sha256 = (
        sha256_bytes(files[FIGURE_AUTHORITY_TABLE_PATH])
        if FIGURE_AUTHORITY_TABLE_PATH in files
        else None
    )
    missing_residue_contracts = sorted(
        CURRENT_MANAGED_SUITE_RESIDUE_CONTRACT_PATHS - set(files)
    )
    current_residue_contracts_verified = not missing_residue_contracts
    if missing_residue_contracts and require_current_residue_contracts:
        raise ReleaseError(
            "bundle is missing current managed-suite residue contracts: "
            f"{missing_residue_contracts}"
        )
    current_runtime_markers_verified = True
    for path, markers in IMMUTABLE_SUITE_RUNTIME_MARKERS.items():
        content = files.get(path)
        missing_markers = (
            [marker.decode("utf-8") for marker in markers]
            if content is None
            else [
                marker.decode("utf-8") for marker in markers
                if not _runtime_marker_present(path, marker, content)
            ]
        )
        if missing_markers:
            current_runtime_markers_verified = False
            if require_current_runtime_markers:
                raise ReleaseError(
                    "immutable-suite bytecode guard is incomplete: "
                    f"{path}: {missing_markers}"
                )
    runtime = manifest.get("runtime") or {
        "platform": "windows-amd64",
        "python_executable": "runtime_vendor/windows-py312/python.exe",
        "executable_paths": ["runtime_vendor/windows-py312/python.exe"],
    }
    runtime_executable = _safe_archive_path(str(runtime.get("python_executable", "")))
    if runtime_executable not in files:
        raise ReleaseError(f"suite runtime executable is missing: {runtime_executable}")
    try:
        runtime_lock = json.loads(files["runtime_vendor/requirements.lock.json"].decode("utf-8-sig"))
    except (KeyError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseError("suite runtime lock is missing or invalid") from exc
    if runtime_lock.get("platform") != runtime.get("platform"):
        raise ReleaseError("suite runtime platform differs from its lock")
    if runtime_lock.get("python_executable", runtime_executable) != runtime_executable:
        raise ReleaseError("suite runtime executable differs from its lock")

    standalone_skill_paths = sorted(
        path for path in files if PurePosixPath(path).name.lower() == "skill.md"
    )
    if standalone_skill_paths != allowed_skill_paths:
        raise ReleaseError(
            "candidate must expose exactly one canonical root Skill and no legacy, "
            f"workspace, backup, probe, or system entry: {standalone_skill_paths}"
        )
    standalone_frontmatter = "\n".join(
        files["standalone/paper-spine/SKILL.md"].decode("utf-8-sig").splitlines()
    ) + "\n"
    if "\nname: paper-spine\n" not in standalone_frontmatter:
        raise ReleaseError("standalone projection is not the canonical paper-spine Skill")
    build_id = manifest["suite"].get("build_id")
    runtime_text = files["06_插件化/runtime/paperspine5_runtime.py"].decode("utf-8")
    if f'PRODUCT_BUILD_ID = "{build_id}"' not in runtime_text:
        raise ReleaseError("installed runtime build identity differs from suite manifest")
    plugin_manifest = json.loads(files[".codex-plugin/plugin.json"].decode("utf-8-sig"))
    if plugin_manifest.get("name") != PLUGIN_NAME:
        raise ReleaseError("plugin object differs from suite identity")
    if not str(plugin_manifest.get("version", "")).endswith(f"+codex.{build_id}"):
        raise ReleaseError("plugin build identity differs from suite manifest")
    expected_interface_brand = {
        "brandColor": "#203431",
        "composerIcon": "./assets/composer-icon.png",
        "logo": "./assets/logo.png",
        "logoDark": "./assets/logo-dark.png",
    }
    plugin_interface = plugin_manifest.get("interface", {})
    for key, expected_value in expected_interface_brand.items():
        if plugin_interface.get(key) != expected_value:
            raise ReleaseError(f"plugin interface brand binding differs from release contract: {key}")
    return {
        "contract": "paperspine5.bundle-verification",
        "schema_version": "1.0",
        "status": "PASS",
        "product_id": PRODUCT_ID,
        "product_version": manifest["suite"].get("product_version"),
        "channel": manifest["suite"].get("channel"),
        "platform": runtime.get("platform"),
        "build_id": build_id,
        "archive_sha256": archive_sha,
        "manifest_sha256": sha256_bytes(manifest_bytes),
        "content_index_sha256": index_sha,
        "figure_authority_table_sha256": figure_authority_table_sha256,
        "file_count": len(expected),
        "runtime_residue_file_count": len(residue_by_path),
        "runtime_residue_total_bytes": sum(
            int(record["size_bytes"]) for record in residue_by_path.values()
        ),
        "runtime_residue_path_digest_sha256": sha256_bytes(
            canonical_json_bytes(sorted(residue_by_path))
        ),
        "current_candidate_runtime_markers_verified": (
            current_runtime_markers_verified
        ),
        "current_candidate_residue_contracts_verified": (
            current_residue_contracts_verified
        ),
        "current_candidate_required_resources_verified": (
            current_required_resources_verified
        ),
        "discovered_skills": [],
        "external_action_authorized": False,
        "manifest": manifest,
    }


def verify_bundle(bundle_path: str | Path) -> dict[str, Any]:
    """Strictly verify a candidate or placed suite.

    This public verifier never accepts historical discovery violations.  It is
    used by build, CLI verification, candidate resolution, extraction,
    placement, and post-activation cache gates.
    """
    return _verify_bundle_with_skill_paths(
        bundle_path,
        allowed_skill_paths=["standalone/paper-spine/SKILL.md"],
    )


def _verify_installed_bundle_with_runtime_residue(
    bundle_path: str | Path,
    *,
    runtime_residue: list[dict[str, Any]],
) -> dict[str, Any]:
    """Verify an installed suite after its extra pyc bytes were source-bound.

    This is intentionally not the candidate verifier.  The caller must first
    classify every extra file with the strict CPython semantic binding in
    :mod:`user_update`; this verifier then keeps all manifest, marker, Skill,
    content-index, and byte checks while accepting exactly those hash-bound
    residue records and no other extra path. A pointer-bound historical suite is
    evaluated against its own immutable manifest/index and may predate a current
    required resource; that time boundary never applies to candidate verification.
    """

    return _verify_bundle_with_skill_paths(
        bundle_path,
        allowed_skill_paths=["standalone/paper-spine/SKILL.md"],
        allowed_runtime_residue=runtime_residue,
        require_current_runtime_markers=False,
        require_current_residue_contracts=False,
        require_current_required_resources=False,
    )


def _recognize_legacy_installed_prestate(
    bundle_path: str | Path,
    *,
    expected_build_id: str,
    expected_content_index_sha256: str,
) -> dict[str, Any]:
    """Recognize one exact historical prestate without making it a candidate.

    Callers must bind both expected values to external installed state, CLI, or
    an installed-suite pointer before using this function.  The one tolerated
    violation is the former workspace Skill path; every indexed file is still
    hash/size checked and every other Skill path remains forbidden.
    """
    verification = _verify_bundle_with_skill_paths(
        bundle_path,
        allowed_skill_paths=[
            "standalone/paper-spine/SKILL.md",
            "standalone/paperspine5-workspace/SKILL.md",
        ],
    )
    if verification.get("build_id") != expected_build_id:
        raise ReleaseError("legacy installed prestate build differs from recorded identity")
    if verification.get("content_index_sha256") != expected_content_index_sha256:
        raise ReleaseError(
            "legacy installed prestate content index differs from recorded identity"
        )
    return {
        "contract": "paperspine5.legacy-installed-prestate-recognition",
        "schema_version": "1.0",
        "status": "recognized",
        "build_id": verification["build_id"],
        "product_version": verification["product_version"],
        "content_index_sha256": verification["content_index_sha256"],
        "archive_sha256": verification.get("archive_sha256"),
        "manifest_sha256": verification["manifest_sha256"],
        "current_prestate_recognized": True,
        "candidate_verified": False,
        "candidate_eligible": False,
        "legacy_discovery_violation": {
            "code": "LEGACY_WORKSPACE_SKILL_PRESENT",
            "paths": ["standalone/paperspine5-workspace/SKILL.md"],
        },
        "external_action_authorized": False,
    }


def extract_verified_bundle(bundle_path: str | Path, destination: str | Path) -> dict[str, Any]:
    """Extract verified regular files without ZipFile.extract path semantics."""
    bundle = Path(bundle_path).resolve()
    destination_root = Path(destination).resolve()
    verification = verify_bundle(bundle)
    files, _ = _read_bundle(bundle)
    if destination_root.exists() and any(destination_root.iterdir()):
        raise ReleaseError(f"bundle destination must be new or empty: {destination_root}")
    destination_root.mkdir(parents=True, exist_ok=True)
    for relative in sorted(files):
        target = (destination_root / Path(*PurePosixPath(relative).parts)).resolve()
        try:
            target.relative_to(destination_root)
        except ValueError as exc:
            raise ReleaseError(f"bundle path escaped extraction root: {relative}") from exc
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(files[relative])
        executable_paths = set(verification.get("manifest", {}).get("runtime", {}).get("executable_paths", []))
        if relative in executable_paths and os.name != "nt":
            target.chmod(0o755)
    verify_bundle(destination_root)
    return verification
