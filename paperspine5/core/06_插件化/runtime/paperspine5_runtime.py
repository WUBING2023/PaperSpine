"""Host-neutral local MCP and JSON bridge for PaperSpine5.

The runtime intentionally contains no paper-writing logic.  It locates the
project's canonical integration core and translates host calls into that API.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import secrets
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO

# This module can be invoked directly, through runpy, or as a Product Web child.
# Establish the immutable-suite contract before any product-core import and pass
# it to every descendant process through the environment.
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


for _stream in (sys.stdin, sys.stdout, sys.stderr):
    reconfigure = getattr(_stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="strict")


SERVER_NAME = "paperspine5-local"
RUNTIME_COMPONENT_VERSION = "0.2.0-dev"
PRODUCT_VERSION = "0.4.0-alpha.4"
PRODUCT_CHANNEL = "development"
PRODUCT_BUILD_ID = "local-dev-unverified"
BRIDGE_PROTOCOL = "paperspine5.host"
BRIDGE_VERSION = "0.4.0"
LEGACY_BRIDGE_VERSIONS = {"0.2.0", "0.3.0"}
SUPPORTED_HOSTS = {"codex", "claude-code", "dsh", "standalone-skill"}
_SERVERS: dict[str, tuple[Any, threading.Thread]] = {}
_KERNELS: dict[str, Any] = {}
_RUNNERS: dict[str, Any] = {}
_SERVICES: dict[str, Any] = {}
_LEASED_TASKS: dict[str, dict[str, str]] = {}
_RUNTIME_INSTANCE_ID = secrets.token_hex(16)
_RUNTIME_LOCK = threading.RLock()

CLAIM_CEILING = (
    "ProductRunner 0.2 generic J1-J11 academic stages are Host/Web integrated; "
    "target_package_ready is local-only, external actions remain unauthorized, "
    "and P0 remains BLOCKED"
)


class RuntimeErrorWithContext(RuntimeError):
    """A user-facing runtime failure with a stable message."""

    def __init__(self, message: str, *, code: str = "RUNTIME_ERROR") -> None:
        super().__init__(message)
        self.code = code


def _error_payload(exc: Exception) -> dict[str, Any]:
    return {
        "status": "FAIL",
        "error_code": getattr(exc, "code", "RUNTIME_ERROR"),
        "error": str(exc),
        "external_action_authorized": False,
    }


def _trace(event: str, **fields: Any) -> None:
    """Write opt-in protocol diagnostics without recording tool arguments."""
    target = os.environ.get("PAPERSPINE5_MCP_TRACE")
    if not target:
        return
    record = {
        "at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event": event,
        **fields,
    }
    try:
        with Path(target).open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _runtime_dir() -> Path:
    return Path(__file__).resolve().parent


def locate_project_root(explicit: str | Path | None = None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    if os.environ.get("PAPERSPINE5_PROJECT_ROOT"):
        candidates.append(Path(os.environ["PAPERSPINE5_PROJECT_ROOT"]))

    config_paths = [
        _runtime_dir() / "local-project.json",
        _runtime_dir().parent / "config" / "local-project.json",
    ]
    for config_path in config_paths:
        if not config_path.is_file():
            continue
        try:
            value = json.loads(config_path.read_text(encoding="utf-8-sig")).get("project_root")
        except (OSError, ValueError, AttributeError):
            value = None
        if isinstance(value, str) and value.strip():
            candidate = Path(value)
            candidates.append(candidate if candidate.is_absolute() else config_path.parent / candidate)

    candidates.extend([_runtime_dir(), *_runtime_dir().parents])
    for candidate in candidates:
        root = candidate.resolve()
        expected = root / "03_联合开发" / "src" / "paperspine_figure_integration" / "coordinator.py"
        if expected.is_file():
            return root
    raise RuntimeErrorWithContext(
        "PaperSpine5 project root was not found; set PAPERSPINE5_PROJECT_ROOT or update config/local-project.json"
    )


def _load_core(project_root: Path) -> tuple[Any, Any]:
    source = project_root / "03_联合开发" / "src"
    source_text = str(source)
    if source_text not in sys.path:
        sys.path.insert(0, source_text)
    try:
        from paperspine_figure_integration.coordinator import IntegrationCoordinator
        from paperspine_figure_integration.ui_server import create_server
    except ImportError as exc:  # pragma: no cover - only possible in a broken install
        raise RuntimeErrorWithContext(f"PaperSpine5 core import failed: {exc}") from exc
    return IntegrationCoordinator, create_server


def _load_product_core(project_root: Path) -> tuple[Any, Any, Any]:
    source = project_root / "03_联合开发" / "src"
    source_text = str(source)
    if source_text not in sys.path:
        sys.path.insert(0, source_text)
    try:
        from paperspine_figure_integration.product_kernel import ProductKernel
        from paperspine_figure_integration.product_runner import ProductRunner
        from paperspine_figure_integration.ui_server import create_product_server
    except ImportError as exc:  # pragma: no cover - only possible in a broken install
        raise RuntimeErrorWithContext(f"PaperSpine5 Product Kernel import failed: {exc}") from exc
    return ProductKernel, ProductRunner, create_product_server


def _user_data_root(raw: Any = None) -> Path:
    configured = raw or os.environ.get("PAPERSPINE5_USER_DATA_ROOT")
    if isinstance(configured, (str, Path)) and str(configured).strip():
        return Path(configured).expanduser().resolve()

    candidates: list[Path] = []
    try:
        user_home: Path | None = Path.home()
    except RuntimeError:
        user_home = None
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            candidates.append(Path(local_app_data) / "PaperSpine5")
        if user_home is not None:
            candidates.append(user_home / "AppData" / "Local" / "PaperSpine5")
    else:
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            candidates.append(Path(xdg_data_home) / "paperspine5")
        if user_home is not None:
            candidates.append(user_home / ".local" / "share" / "paperspine5")
    if user_home is not None:
        candidates.append(user_home / ".paperspine5")

    failures: list[str] = []
    for candidate in candidates:
        root = candidate.expanduser().resolve()
        probe = root / f".write-probe-{os.getpid()}-{secrets.token_hex(4)}"
        try:
            root.mkdir(parents=True, exist_ok=True)
            with probe.open("x", encoding="utf-8") as stream:
                stream.write("paperspine5\n")
            probe.unlink()
            return root
        except OSError as exc:
            failures.append(f"{root}: {exc}")
            try:
                if probe.exists():
                    probe.unlink()
            except OSError:
                pass
    raise RuntimeErrorWithContext(
        "No writable PaperSpine5 user data root was found; set "
        "PAPERSPINE5_USER_DATA_ROOT to an explicit writable directory. "
        + " | ".join(failures),
        code="USER_DATA_ROOT_UNWRITABLE",
    )


def _suite_manifest(project_root: Path) -> dict[str, Any]:
    return {
        "contract": "paperspine5.product-manifest",
        "schema_version": "1.0",
        "product_id": "paperspine5",
        "product_version": PRODUCT_VERSION,
        "channel": PRODUCT_CHANNEL,
        "build_id": PRODUCT_BUILD_ID,
        "core_root": str(project_root.resolve()),
        "component_versions": {
            "product_kernel": "0.1.0",
            "product_runner": "0.2.0",
            "host_runtime": RUNTIME_COMPONENT_VERSION,
            "host_bridge": BRIDGE_VERSION,
        },
        "compatibility": {
            "integration_job_reader": ["1.0", "1.1"],
            "integration_state_reader": ["1.0", "1.1", "1.2", "1.3"],
            "integration_state_writer": "1.3",
            "product_runner_protocol": "1.0",
        },
    }


def _suite_verifier(project_root: Path) -> Any:
    candidates = [
        project_root / "release" / "suite_release.py",
        project_root / "06_插件化" / "release" / "suite_release.py",
    ]
    path = next((item for item in candidates if item.is_file()), None)
    if path is None:
        raise RuntimeErrorWithContext(
            "PaperSpine5 installed suite verifier is missing",
            code="SUCCESSOR_AUTHORITY_UNAVAILABLE",
        )
    module_name = "paperspine5_suite_release_" + hashlib.sha256(
        str(path.resolve()).encode("utf-8")
    ).hexdigest()[:16]
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeErrorWithContext(
            "PaperSpine5 installed suite verifier cannot be loaded",
            code="SUCCESSOR_AUTHORITY_UNAVAILABLE",
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    verifier = getattr(module, "verify_bundle", None)
    if not callable(verifier):
        raise RuntimeErrorWithContext(
            "PaperSpine5 installed suite verifier has no verify_bundle API",
            code="SUCCESSOR_AUTHORITY_UNAVAILABLE",
        )
    return verifier


def _resolve_unique_successor_authority(
    request: dict[str, Any],
    *,
    project_root: Path,
    control_roots: dict[str, Path],
    suite_verifier: Any,
    authority_resolver: Any,
) -> dict[str, Any]:
    """Select the one updater surface fully bound to this active runtime root."""

    resolved: list[dict[str, Any]] = []
    failures: list[str] = []
    for install_kind, control_root in control_roots.items():
        try:
            resolved.append(
                authority_resolver(
                    install_kind=install_kind,
                    control_root=control_root,
                    current_suite_root=project_root,
                    source_build_id=str(request.get("source_build_id") or ""),
                    target_build_id=str(request.get("target_build_id") or ""),
                    suite_verifier=suite_verifier,
                )
            )
        except Exception as exc:
            failures.append(f"{install_kind}: {exc}")
    if len(resolved) == 0 and str(request.get("source_build_id") or "") == "local-dev-unverified":
        development_root = os.environ.get("PAPERSPINE5_DEVELOPMENT_SOURCE_ROOT")
        if development_root:
            try:
                from paperspine_figure_integration.successor_authority import (
                    resolve_development_bootstrap_authority,
                )

                resolved.append(
                    resolve_development_bootstrap_authority(
                        development_source_root=development_root,
                        current_suite_root=project_root,
                        source_build_id=str(request.get("source_build_id") or ""),
                        target_build_id=str(request.get("target_build_id") or ""),
                        source_runner_version=str(
                            request.get("source_runner_version") or ""
                        ),
                        suite_verifier=suite_verifier,
                    )
                )
            except Exception as exc:
                failures.append(f"development-bootstrap: {exc}")
    if len(resolved) != 1:
        detail = "; ".join(failures) if not resolved else "multiple exact surfaces matched"
        raise RuntimeErrorWithContext(
            f"same-task successor authority is unavailable or ambiguous: {detail}",
            code="SUCCESSOR_AUTHORITY_UNAVAILABLE",
        )
    return resolved[0]


def _successor_authority_resolver(project_root: Path) -> Any:
    from paperspine_figure_integration.successor_authority import (
        resolve_installed_successor_authority,
    )

    home = Path.home().resolve()
    control_roots = {
        "plugin": Path(
            os.environ.get(
                "PAPERSPINE5_PLUGIN_UPDATE_CONTROL_ROOT",
                home / ".paperspine5" / "plugin-updates",
            )
        ).expanduser().resolve(),
        "skill": Path(
            os.environ.get(
                "PAPERSPINE5_SKILL_UPDATE_CONTROL_ROOT",
                home / ".paperspine5" / "skill-updates",
            )
        ).expanduser().resolve(),
    }

    def resolve(request: dict[str, Any]) -> dict[str, Any]:
        if (
            request.get("contract") != "paperspine5.successor-authority-request"
            or request.get("schema_version") != "1.0"
            or request.get("target_core_root") != str(project_root.resolve())
            or request.get("external_action_authorized") is not False
        ):
            raise RuntimeErrorWithContext(
                "same-task successor authority request is invalid",
                code="SUCCESSOR_AUTHORITY_INVALID",
            )
        return _resolve_unique_successor_authority(
            request,
            project_root=project_root,
            control_roots=control_roots,
            suite_verifier=_suite_verifier(project_root),
            authority_resolver=resolve_installed_successor_authority,
        )

    return resolve


def _product_runtime(project_root: Path, raw_user_data_root: Any = None) -> tuple[Any, Any]:
    user_data_root = _user_data_root(raw_user_data_root)
    key = str(user_data_root)
    with _RUNTIME_LOCK:
        kernel = _KERNELS.get(key)
        if kernel is None:
            ProductKernel, ProductRunner, _ = _load_product_core(project_root)
            from paperspine_figure_integration.bridges import FigMirrorBridge

            kernel = ProductKernel(
                user_data_root,
                core_root=project_root,
                product_manifest=_suite_manifest(project_root),
            )
            figure_bridge = FigMirrorBridge(
                {
                    "project_root": str(project_root),
                    "figure": {
                        "job_dir": str(
                            user_data_root / ".paperspine5-figure-executor"
                        ),
                        "figmirror_cli": str(
                            project_root
                            / "02_PaperFigure"
                            / "01_FigMirror引擎"
                            / "src"
                            / "scripts"
                            / "figmirror.py"
                        ),
                    },
                }
            )
            figure_review_host: dict[str, Any] = {}

            def review_figure_correction(context: dict[str, Any]) -> dict[str, Any]:
                manager = figure_review_host.get("manager")
                if manager is None:
                    from web_agent_runtime import ProductWebAgentRuntime

                    manager = ProductWebAgentRuntime(
                        kernel=kernel,
                        runner=runner,
                        project_root=project_root,
                        user_data_root=user_data_root,
                        runner_writer_owner=_runtime_writer_owner,
                        runner_writer_used=lambda task_id, writer_id: _mark_runtime_lease(
                            str(user_data_root), task_id, writer_id
                        ),
                    )
                    figure_review_host["manager"] = manager
                return manager.review_figure_correction(context)

            runner = ProductRunner(
                kernel,
                expected_build_id=kernel.product_manifest["build_id"],
                figure_correction_executor=figure_bridge.execute_correction,
                figure_correction_reviewer=review_figure_correction,
                successor_authority_resolver=_successor_authority_resolver(
                    project_root
                ),
            )
            _KERNELS[key] = kernel
            _RUNNERS[key] = runner
        else:
            runner = _RUNNERS.get(key)
            if runner is None:
                raise RuntimeErrorWithContext(
                    "ProductKernel exists without its sealed ProductRunner registration",
                    code="RUNNER_REGISTRATION_MISSING",
                )
    return kernel, runner


def _product_application_service(project_root: Path, raw_user_data_root: Any = None) -> Any:
    """Return the ApplicationService bound to the same Kernel/Runner runtime.

    Product Web used to expose ``ui_server.create_product_server`` directly,
    which meant the new configuration/material REST routes in the P2 facade
    were never reachable from the installed launcher.  Keep one Kernel and one
    Runner, then add the durable domain event store beside the Kernel registry
    so the business facade and legacy academic stages share their task roots.
    Existing Kernel-only tasks are represented by a read-only ``resume`` event
    on first access; this preserves their files and Runner state while making
    them visible to the new projection.
    """
    user_data_root = _user_data_root(raw_user_data_root)
    key = str(user_data_root)
    with _RUNTIME_LOCK:
        service = _SERVICES.get(key)
        if service is not None:
            return service
        kernel, runner = _product_runtime(project_root, user_data_root)
        from paperspine_figure_integration.p1_application import (
            ApplicationService,
            DomainEventStore,
            LegacyStageAdapter,
            business_open_task,
        )

        database = user_data_root / "registry" / "application.sqlite3"
        contracts_root = project_root / "03_联合开发" / "contracts"
        service = ApplicationService(
            DomainEventStore(database),
            LegacyStageAdapter(kernel, runner),
            contracts_root=contracts_root,
        )
        # Migrate only the task identity into the domain projection.  No source
        # files, artifacts, decisions, or Runner pointers are copied or
        # rewritten; all of those remain owned by the existing Kernel/Runner.
        existing = {item.get("task_id") for item in service.list_tasks()}
        for task in kernel.list_tasks():
            task_id = task.get("task_id")
            if not isinstance(task_id, str) or task_id in existing:
                continue
            command_id = "runtime-migrate-" + hashlib.sha256(task_id.encode("utf-8")).hexdigest()[:24]
            try:
                business_open_task(
                    service,
                    {
                        "command_id": command_id,
                        "task_id": task_id,
                        "expected_version": 0,
                        "payload": {"mode": "resume", "requested_task_id": task_id},
                    },
                    principal_id="local-user",
                    session_id="runtime-migration",
                )
            except Exception:
                # A malformed/partially imported legacy task must remain
                # readable through the legacy runner; do not block the whole
                # product workspace on an opportunistic projection.
                continue
        _SERVICES[key] = service
        return service


def _product_kernel(project_root: Path, raw_user_data_root: Any = None) -> Any:
    """Compatibility accessor; construction still registers exactly one Runner."""
    return _product_runtime(project_root, raw_user_data_root)[0]


def _runtime_writer_owner(task_id: str) -> str:
    task_digest = hashlib.sha256(task_id.encode("utf-8")).hexdigest()[:16]
    return f"paperspine5-runtime:{_RUNTIME_INSTANCE_ID}:{task_digest}"


def _reject_client_writer(arguments: dict[str, Any]) -> None:
    if "writer_id" in arguments:
        raise RuntimeErrorWithContext(
            "writer_id is runtime-owned and cannot be supplied by a client",
            code="RUNNER_WRITER_SPOOFED",
        )


def _mark_runtime_lease(user_data_key: str, task_id: str, writer_id: str) -> None:
    with _RUNTIME_LOCK:
        _LEASED_TASKS.setdefault(user_data_key, {})[task_id] = writer_id


def _release_runtime_leases(user_data_key: str, kernel: Any) -> list[str]:
    with _RUNTIME_LOCK:
        owned = _LEASED_TASKS.pop(user_data_key, {})
    released: list[str] = []
    for task_id, writer_id in owned.items():
        try:
            if kernel.release_writer_lease(task_id, writer_id):
                released.append(task_id)
        except Exception:
            # Kernel close remains best-effort during process teardown. A crash or
            # failed release is fenced by the repository lease expiry.
            continue
    return released


def _close_kernels() -> None:
    with _RUNTIME_LOCK:
        kernels = list(_KERNELS.items())
        _KERNELS.clear()
        _RUNNERS.clear()
        _SERVICES.clear()
    for key, kernel in kernels:
        _release_runtime_leases(key, kernel)
        close = getattr(kernel, "close", None)
        if callable(close):
            close()


def _job_path(project_root: Path, raw: Any) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise RuntimeErrorWithContext("job_path is required")
    candidate = Path(raw)
    resolved = candidate.resolve() if candidate.is_absolute() else (project_root / candidate).resolve()
    try:
        resolved.relative_to(project_root)
    except ValueError as exc:
        raise RuntimeErrorWithContext("job_path must stay inside the PaperSpine5 project root") from exc
    if not resolved.is_file():
        raise RuntimeErrorWithContext(f"integration job does not exist: {resolved}")
    try:
        job = json.loads(resolved.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise RuntimeErrorWithContext(f"integration job is not readable JSON: {resolved}") from exc
    if isinstance(job, dict) and job.get("schema_version") == "1.1" and job.get("core_root"):
        raise RuntimeErrorWithContext(
            "Product Kernel task jobs cannot use the legacy job_path adapter; use task_id and paperspine5_command"
        )
    return resolved


def health(project_root: Path, *, detailed: bool = True) -> dict[str, Any]:
    IntegrationCoordinator, _ = _load_core(project_root)
    result: dict[str, Any] = {
        "status": "PASS",
        "product_id": "paperspine5",
        "product_version": PRODUCT_VERSION,
        "channel": PRODUCT_CHANNEL,
        "build_id": PRODUCT_BUILD_ID,
        "component_versions": _suite_manifest(project_root)["component_versions"],
        "runtime": {"name": SERVER_NAME, "component_version": RUNTIME_COMPONENT_VERSION},
    }
    if detailed:
        result.update(
            {
                "project_root": str(project_root),
                "core": f"{IntegrationCoordinator.__module__}.{IntegrationCoordinator.__name__}",
                "transport": ["mcp-stdio", "json-bridge"],
                "hosts": sorted(SUPPORTED_HOSTS),
                "product_api": "paperspine5.product-kernel/1.0",
                "runner_api": "paperspine5.product-runner/0.2.0",
                "claim_ceiling": CLAIM_CEILING,
            }
        )
    return result


def dispatch(action: str, arguments: dict[str, Any], project_root: Path) -> dict[str, Any]:
    _trace("dispatch.start", action=action)
    if action == "health":
        # Tool results may be sent to a hosted model; keep local paths on-device.
        result = health(project_root, detailed=False)
        _trace("dispatch.complete", action=action, status=result.get("status"))
        return result

    host = arguments.get("host")
    if host is not None and host not in SUPPORTED_HOSTS:
        raise RuntimeErrorWithContext(f"unsupported host: {host}")

    if action in {
        "create_task",
        "import_legacy_task",
        "list_tasks",
        "get_task",
        "list_artifacts",
        "readiness",
        "command",
        "runner_snapshot",
        "runner_bootstrap",
        "runner_renew_delegated_grant",
        "runner_add_materials",
        "runner_answer_issue",
        "runner_answer_academic_stage",
        "runner_answer_host_materialized_stage",
        "runner_register_figure_candidate",
        "runner_register_final_mapping",
        "runner_resume",
        "runner_request_revision",
        "open_product_workspace",
        "workspace_status",
        "stop_workspace",
    }:
        kernel, runner = _product_runtime(project_root, arguments.get("user_data_root"))
        user_data_root = kernel.user_data_root
        if action == "create_task":
            materials_roots = arguments.get("materials_roots") or []
            if not isinstance(materials_roots, list) or not all(
                isinstance(item, str) and item.strip() for item in materials_roots
            ):
                raise RuntimeErrorWithContext(
                    "materials_roots must be an array of non-empty directory paths"
                )
            return kernel.create_task(
                command_id=arguments.get("command_id"),
                materials_roots=tuple(materials_roots),
                title=arguments.get("title"),
                host=host or "codex",
                task_id=arguments.get("task_id"),
            )
        if action == "import_legacy_task":
            job_path = arguments.get("job_path")
            if not isinstance(job_path, str) or not job_path:
                raise RuntimeErrorWithContext("job_path is required")
            return kernel.import_legacy_job(
                job_path,
                command_id=arguments.get("command_id"),
                title=arguments.get("title"),
                task_id=arguments.get("task_id"),
                host=host or "codex",
            )
        if action == "list_tasks":
            return {"status": "PASS", "tasks": kernel.list_tasks(arguments.get("status"))}
        if action == "get_task":
            task_id = arguments.get("task_id")
            if not isinstance(task_id, str) or not task_id:
                raise RuntimeErrorWithContext("task_id is required")
            return {"status": "PASS", "task": kernel.get_task(task_id)}
        if action == "list_artifacts":
            task_id = arguments.get("task_id")
            artifact_type = arguments.get("artifact_type")
            revision = arguments.get("revision")
            if not isinstance(task_id, str) or not task_id:
                raise RuntimeErrorWithContext("task_id is required")
            if artifact_type is not None and (not isinstance(artifact_type, str) or not artifact_type):
                raise RuntimeErrorWithContext("artifact_type must be a non-empty string")
            if revision is not None and (isinstance(revision, bool) or not isinstance(revision, int) or revision < 0):
                raise RuntimeErrorWithContext("revision must be a non-negative integer")
            return {
                "status": "PASS",
                "artifacts": kernel.list_artifacts(
                    task_id,
                    artifact_type=artifact_type,
                    subject_revision=revision,
                ),
            }
        if action == "readiness":
            task_id = arguments.get("task_id")
            revision = arguments.get("revision")
            if not isinstance(task_id, str) or not task_id:
                raise RuntimeErrorWithContext("task_id is required")
            if revision is not None and (isinstance(revision, bool) or not isinstance(revision, int) or revision < 0):
                raise RuntimeErrorWithContext("revision must be a non-negative integer")
            return {"status": "PASS", "readiness": kernel.get_readiness(task_id, revision=revision)}
        if action == "command":
            task_id = arguments.get("task_id")
            envelope = arguments.get("envelope")
            if not isinstance(task_id, str) or not task_id:
                raise RuntimeErrorWithContext("task_id is required")
            if not isinstance(envelope, dict):
                raise RuntimeErrorWithContext("envelope must be a Product Kernel command object")
            command_type = envelope.get("command_type")
            if isinstance(command_type, str) and command_type.startswith("runner."):
                raise RuntimeErrorWithContext(
                    "runner.* commands must use the registered ProductRunner facade",
                    code="RUNNER_FACADE_REQUIRED",
                )
            if "writer_id" in envelope:
                raise RuntimeErrorWithContext(
                    "writer_id is runtime-owned and cannot be supplied in a command envelope",
                    code="COMMAND_WRITER_SPOOFED",
                )
            writer_id = _runtime_writer_owner(task_id)
            trusted_envelope = {**envelope, "writer_id": writer_id}
            try:
                result = kernel.submit_command(task_id, trusted_envelope)
            except Exception as exc:
                if exc.__class__.__name__ == "WriterLeaseError":
                    raise RuntimeErrorWithContext(
                        str(exc), code="RUNNER_WRITER_LEASE_HELD"
                    ) from exc
                raise
            _mark_runtime_lease(str(user_data_root), task_id, writer_id)
            return result
        if action.startswith("runner_"):
            task_id = arguments.get("task_id")
            if not isinstance(task_id, str) or not task_id:
                raise RuntimeErrorWithContext("task_id is required", code="RUNNER_INPUT_INVALID")
            if action == "runner_snapshot":
                return {"status": "PASS", "snapshot": runner.snapshot(task_id)}
            _reject_client_writer(arguments)
            command_id = arguments.get("command_id")
            expected_revision = arguments.get("expected_revision")
            actor = arguments.get("actor")
            if not isinstance(command_id, str) or not command_id:
                raise RuntimeErrorWithContext("command_id is required", code="RUNNER_INPUT_INVALID")
            if isinstance(expected_revision, bool) or not isinstance(expected_revision, int) or expected_revision < 0:
                raise RuntimeErrorWithContext(
                    "expected_revision must be a non-negative integer",
                    code="RUNNER_INPUT_INVALID",
                )
            if actor is not None and not isinstance(actor, dict):
                raise RuntimeErrorWithContext("actor must be an object", code="RUNNER_INPUT_INVALID")
            writer_id = _runtime_writer_owner(task_id)
            common = {
                "command_id": command_id,
                "expected_revision": expected_revision,
                "writer_id": writer_id,
                "actor": actor,
            }
            try:
                if action == "runner_bootstrap":
                    result = runner.bootstrap(task_id, **common)
                elif action == "runner_renew_delegated_grant":
                    if not isinstance(actor, dict):
                        raise RuntimeErrorWithContext(
                            "delegated grant renewal requires an explicit user-origin actor",
                            code="RUNNER_AUTHORITY_REQUIRED",
                        )
                    result = runner.renew_delegated_grant(task_id, **common)
                elif action == "runner_add_materials":
                    materials_roots = arguments.get("materials_roots")
                    if not isinstance(materials_roots, list) or not materials_roots or not all(
                        isinstance(item, str) and item for item in materials_roots
                    ):
                        raise RuntimeErrorWithContext(
                            "materials_roots must be a non-empty array of paths",
                            code="RUNNER_INPUT_INVALID",
                        )
                    result = runner.add_materials(task_id, materials_roots, **common)
                elif action in {"runner_answer_issue", "runner_answer_academic_stage"}:
                    issue_id = arguments.get("issue_id")
                    resume_token = arguments.get("resume_token")
                    answer = arguments.get("answer")
                    if not isinstance(issue_id, str) or not issue_id:
                        raise RuntimeErrorWithContext("issue_id is required", code="RUNNER_INPUT_INVALID")
                    if not isinstance(resume_token, str) or not resume_token:
                        raise RuntimeErrorWithContext("resume_token is required", code="RUNNER_INPUT_INVALID")
                    if not isinstance(answer, dict):
                        raise RuntimeErrorWithContext("answer must be an object", code="RUNNER_INPUT_INVALID")
                    if (
                        action == "runner_answer_academic_stage"
                        and answer.get("contract") != "paperspine5.academic-stage-answer"
                    ):
                        raise RuntimeErrorWithContext(
                            "answer must use the paperspine5.academic-stage-answer contract",
                            code="RUNNER_ACADEMIC_ANSWER_REQUIRED",
                        )
                    result = runner.answer_issue(task_id, issue_id, resume_token, answer, **common)
                elif action == "runner_answer_host_materialized_stage":
                    issue_id = arguments.get("issue_id")
                    resume_token = arguments.get("resume_token")
                    answer = arguments.get("answer")
                    review = arguments.get("review")
                    if not isinstance(issue_id, str) or not issue_id:
                        raise RuntimeErrorWithContext("issue_id is required", code="RUNNER_INPUT_INVALID")
                    if not isinstance(resume_token, str) or not resume_token:
                        raise RuntimeErrorWithContext("resume_token is required", code="RUNNER_INPUT_INVALID")
                    if not isinstance(answer, dict) or answer.get("contract") != "paperspine5.academic-stage-answer":
                        raise RuntimeErrorWithContext(
                            "answer must use the paperspine5.academic-stage-answer contract",
                            code="RUNNER_ACADEMIC_ANSWER_REQUIRED",
                        )
                    current = runner.snapshot(task_id)
                    stage = current.get("stage")
                    supported_stages = {
                        "awaiting_canonical",
                        "awaiting_review",
                        "awaiting_package",
                    }
                    if stage not in supported_stages:
                        raise RuntimeErrorWithContext(
                            "host materialization is only available at J8, J9, or J10",
                            code="HOST_MATERIALIZATION_STAGE_UNSUPPORTED",
                        )
                    if current.get("revision") != expected_revision:
                        raise RuntimeErrorWithContext(
                            "host materialization revision is stale",
                            code="RUNNER_REVISION_CONFLICT",
                        )
                    open_issues = current.get("open_issues", [])
                    matching_issues = [
                        item
                        for item in open_issues
                        if isinstance(item, dict) and item.get("issue_id") == issue_id
                    ]
                    if (
                        len(open_issues) != 1
                        or len(matching_issues) != 1
                        or matching_issues[0].get("resume_token") != resume_token
                    ):
                        raise RuntimeErrorWithContext(
                            "host materialization issue is not the sole current issue",
                            code="RUNNER_ISSUE_STALE",
                        )
                    from web_agent_runtime import (
                        INDEPENDENT_REVIEW_STAGES,
                        RUNNER_RESERVED_STAGE_FIELDS,
                        ProductWebAgentRuntime,
                    )

                    operation_token = hashlib.sha256(command_id.encode("utf-8")).hexdigest()[:24]
                    job = {
                        "job_id": f"host-materialized-{operation_token}",
                        "task_id": task_id,
                        "revision": expected_revision,
                        "issue_id": issue_id,
                        "stage": stage,
                    }
                    manager = ProductWebAgentRuntime(
                        kernel=kernel,
                        runner=runner,
                        project_root=project_root,
                        user_data_root=user_data_root,
                        runner_writer_owner=_runtime_writer_owner,
                        runner_writer_used=lambda owned_task_id, owned_writer_id: _mark_runtime_lease(
                            str(user_data_root), owned_task_id, owned_writer_id
                        ),
                    )
                    try:
                        if stage == "awaiting_package" and review is not None:
                            raise ValueError("J10 host materialization review must be null")
                        from jsonschema import Draft202012Validator

                        if stage == "awaiting_package":
                            errors = list(Draft202012Validator(HOST_MATERIALIZED_STAGE_ANSWER).iter_errors(answer))
                            if errors:
                                raise ValueError("J10 host answer schema mismatch: " + errors[0].message)
                        payload = manager._extract_stage_payload(
                            json.dumps(answer, ensure_ascii=False), job
                        )
                        for field in RUNNER_RESERVED_STAGE_FIELDS:
                            payload.pop(field, None)
                        payload = manager._materialize_stage_inputs(
                            task=kernel.get_task(task_id),
                            snapshot=current,
                            payload=payload,
                            user_message=None,
                            final_mappings=manager._package_mappings(kernel.get_task(task_id), current, runner),
                        )
                        if stage in INDEPENDENT_REVIEW_STAGES:
                            if not isinstance(review, dict):
                                raise ValueError(
                                    "J8/J9 host materialization requires an independent review"
                                )
                            from jsonschema import Draft202012Validator

                            review_errors = sorted(
                                Draft202012Validator(
                                    HOST_INDEPENDENT_REVIEW
                                ).iter_errors(review),
                                key=lambda item: list(item.absolute_path),
                            )
                            if review_errors:
                                raise ValueError(
                                    "host independent review schema mismatch: "
                                    + review_errors[0].message
                                )
                            manager._validate_review_result(review, job, payload=payload)
                            if review.get("decision") != "pass" and stage != "awaiting_review":
                                raise RuntimeErrorWithContext(
                                    "independent review blocked host materialization",
                                    code="HOST_INDEPENDENT_REVIEW_BLOCKED",
                                )
                            if stage == "awaiting_canonical":
                                payload = manager._finalize_canonical_review(
                                    payload=payload, job=job, review=review
                                )
                            elif stage == "awaiting_review":
                                payload = manager._finalize_publication_review(
                                    payload=payload, job=job, review=review
                                )
                        elif review is not None:
                            raise ValueError("J10 host materialization review must be null")
                        payload = manager._bind_host_identities(
                            payload, job, review=review
                        )
                    except RuntimeErrorWithContext:
                        raise
                    except (OSError, ValueError) as exc:
                        raise RuntimeErrorWithContext(
                            str(exc), code="HOST_MATERIALIZATION_INVALID"
                        ) from exc
                    trusted_answer = {
                        "contract": "paperspine5.academic-stage-answer",
                        "schema_version": "1.0",
                        "answer_id": f"host-materialized-answer-{operation_token}",
                        "issue_id": issue_id,
                        "task_id": task_id,
                        "expected_revision": expected_revision,
                        "stage": stage,
                        "payload": payload,
                        "external_action_authorized": False,
                    }
                    result = runner.answer_issue(
                        task_id,
                        issue_id,
                        resume_token,
                        trusted_answer,
                        **common,
                    )
                elif action == "runner_register_final_mapping":
                    registration = arguments.get("registration")
                    if not isinstance(registration, dict):
                        raise RuntimeErrorWithContext("registration must be a typed final-mapping registration", code="RUNNER_INPUT_INVALID")
                    result = runner.register_final_mapping(task_id, registration, **common)
                elif action == "runner_register_figure_candidate":
                    registration = arguments.get("registration")
                    if not isinstance(registration, dict):
                        raise RuntimeErrorWithContext(
                            "registration must be a figure-candidate-registration object",
                            code="RUNNER_INPUT_INVALID",
                        )
                    result = runner.register_figure_candidate(
                        task_id, registration, **common
                    )
                elif action == "runner_resume":
                    result = runner.resume(task_id, **common)
                elif action == "runner_request_revision":
                    result = runner.request_revision(task_id, feedback=arguments.get("feedback"),
                        scope=arguments.get("scope"), **common)
                else:
                    raise RuntimeErrorWithContext("unsupported ProductRunner action")
            except Exception as exc:
                if exc.__class__.__name__ == "WriterLeaseError":
                    raise RuntimeErrorWithContext(
                        str(exc), code="RUNNER_WRITER_LEASE_HELD"
                    ) from exc
                raise
            _mark_runtime_lease(str(user_data_root), task_id, writer_id)
            return result

        key = f"product:{user_data_root}"
        if action == "workspace_status":
            with _RUNTIME_LOCK:
                current = _SERVERS.get(key)
                running = bool(current and current[1].is_alive())
                port = current[0].server_port if running else None
            return {
                "status": "RUNNING" if running else "STOPPED",
                "address": f"http://127.0.0.1:{port}/" if port else None,
                "surface": "product",
            }
        if action == "stop_workspace":
            with _RUNTIME_LOCK:
                current = _SERVERS.pop(key, None)
            if current is None:
                already_stopped = True
            else:
                server, thread = current
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
                already_stopped = False
            kernel_closed = False
            if arguments.get("close_kernel") is True:
                with _RUNTIME_LOCK:
                    owned = _KERNELS.pop(str(user_data_root), None)
                    _RUNNERS.pop(str(user_data_root), None)
                    _SERVICES.pop(str(user_data_root), None)
                if owned is not None:
                    _release_runtime_leases(str(user_data_root), owned)
                close = getattr(owned, "close", None)
                if callable(close):
                    close()
                    kernel_closed = True
            return {
                "status": "STOPPED",
                "already_stopped": already_stopped,
                "surface": "product",
                "kernel_closed": kernel_closed,
            }
        task_id = arguments.get("task_id")
        if task_id is not None:
            if not isinstance(task_id, str) or not task_id:
                raise RuntimeErrorWithContext("task_id must be a non-empty string")
            kernel.get_task(task_id)
        _, _, _ = _load_product_core(project_root)
        service = _product_application_service(project_root, user_data_root)
        from paperspine_figure_integration.p2_facades import create_business_server
        with _RUNTIME_LOCK:
            current = _SERVERS.get(key)
            reused = bool(current and current[1].is_alive())
            if reused:
                server = current[0]
            else:
                if current is not None:
                    current[0].server_close()
                    _SERVERS.pop(key, None)
                server = create_business_server(
                    service,
                    principal_id="local-user",
                    session_id=f"product-web-{_RUNTIME_INSTANCE_ID}",
                    port=0,
                )
                thread = threading.Thread(
                    target=server.serve_forever,
                    daemon=True,
                    name=f"paperspine5-product-ui-{server.server_port}",
                )
                thread.start()
                _SERVERS[key] = (server, thread)
        return {
            "status": "READY",
            "address": f"http://127.0.0.1:{server.server_port}/",
            "surface": "product",
            "task_id": task_id,
            "reused": reused,
            "lifecycle": "owned-by-mcp-process; explicit status/stop available",
        }

    IntegrationCoordinator, create_server = _load_core(project_root)
    job_path = _job_path(project_root, arguments.get("job_path"))
    coordinator = IntegrationCoordinator(job_path)

    if action == "snapshot":
        result = coordinator.snapshot()
        if host:
            result["host_next"] = coordinator.host_next(host)
        return result
    if action == "save_configuration":
        configuration = arguments.get("configuration")
        if not isinstance(configuration, dict):
            raise RuntimeErrorWithContext("configuration must be a JSON object")
        return coordinator.save_configuration(configuration)
    if action == "advance":
        return coordinator.resume() if coordinator.state()["stage"] == "blocked" else coordinator.advance()
    if action == "record_decision":
        decision = arguments.get("decision")
        if not isinstance(decision, dict):
            raise RuntimeErrorWithContext("decision must be a JSON object")
        return coordinator.record_decision(decision)
    if action == "record_signal":
        signal = arguments.get("signal")
        if not isinstance(signal, dict):
            raise RuntimeErrorWithContext("signal must be a JSON object")
        return coordinator.record_signal(signal)
    if action == "publication_cycle":
        request = arguments.get("request")
        if not isinstance(request, dict):
            raise RuntimeErrorWithContext("request must be a JSON object")
        return coordinator.invoke_publication_cycle(request)
    if action == "manuscript_status":
        return coordinator.manuscript_snapshot()
    if action == "save_manuscript_revision":
        revision = arguments.get("revision")
        if not isinstance(revision, dict):
            raise RuntimeErrorWithContext("revision must be a JSON object")
        return coordinator.save_manuscript_revision(revision)
    if action == "restore_manuscript_revision":
        request = arguments.get("request")
        if not isinstance(request, dict):
            raise RuntimeErrorWithContext("request must be a JSON object")
        return coordinator.restore_manuscript_revision(request)
    if action == "confirm_manuscript_revision":
        confirmation = arguments.get("confirmation")
        if not isinstance(confirmation, dict):
            raise RuntimeErrorWithContext("confirmation must be a JSON object")
        return coordinator.confirm_manuscript_revision(confirmation)
    if action == "answer_user_input":
        resolution = arguments.get("resolution")
        if not isinstance(resolution, dict):
            raise RuntimeErrorWithContext("resolution must be a JSON object")
        return coordinator.resolve_user_input_issue(resolution)
    if action == "open_workspace":
        key = f"legacy:{job_path}"
        with _RUNTIME_LOCK:
            current = _SERVERS.get(key)
            if current and current[1].is_alive():
                server = current[0]
            else:
                server = create_server(job_path, port=0)
                thread = threading.Thread(target=server.serve_forever, daemon=True, name=f"paperspine5-ui-{server.server_port}")
                thread.start()
                _SERVERS[key] = (server, thread)
        return {
            "status": "READY",
            "address": f"http://127.0.0.1:{server.server_port}/",
            "job_path": str(job_path),
            "lifecycle": "owned-by-mcp-process",
        }
    raise RuntimeErrorWithContext(f"unsupported action: {action}")


def _tool(name: str, description: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": properties,
            "required": required,
        },
    }


JOB = {"type": "string", "description": "Absolute path, or project-relative path, to integration_job.json."}
HOST = {"type": "string", "enum": sorted(SUPPORTED_HOSTS), "description": "Host projection for next-action guidance."}
USER_DATA_ROOT = {"type": "string", "description": "Optional isolated PaperSpine5 user-data root; defaults to the local user profile."}
TASK_ID = {"type": "string", "description": "Stable Product Kernel task identifier."}
COMMAND_ID = {"type": "string", "description": "Unique idempotency key; reuse only for a byte-identical lost-ACK retry."}
EXPECTED_REVISION = {"type": "integer", "minimum": 0, "description": "Current Product Kernel revision for CAS."}


def _load_public_contract_schema(filename: str) -> dict[str, Any]:
    """Load one suite-owned public contract that tools/list exposes verbatim."""

    relative = Path("03_联合开发") / "contracts" / filename
    for root in (_runtime_dir(), *_runtime_dir().parents):
        candidate = root / relative
        if candidate.is_file():
            value = json.loads(candidate.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                break
            return value
    raise RuntimeErrorWithContext(
        f"PaperSpine5 public contract is missing: 03_联合开发/contracts/{filename}"
    )


RUN_CONFIGURATION_ANSWER = _load_public_contract_schema(
    "run-configuration.schema.json"
)
ACTOR = {
    "type": "object",
    "additionalProperties": True,
    "required": ["actor_id", "surface"],
    "description": (
        "Optional host actor. Omit this argument for ordinary calls so the runtime derives "
        "its system actor. If supplied, actor_id and surface are required."
    ),
    "properties": {
        "actor_id": {
            "type": "string",
            "pattern": "^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$",
        },
        "surface": {
            "type": "string",
            "enum": [
                "codex",
                "claude-code",
                "dsh",
                "standalone-skill",
                "web",
                "mcp",
                "cli",
                "system",
            ],
        },
        "authority_kind": {
            "type": "string",
            "enum": ["authenticated_local_user_session", "host_user_message"],
            "description": (
                "Supply only for delegated_local_test and match the granting actor exactly."
            ),
        },
    },
}
# The JSON file, ProductRunner issue projection and tools/list are one public
# authority.
ACADEMIC_STAGE_ANSWER = _load_public_contract_schema(
    "academic-stage-answer.schema.json"
)
HOST_INDEPENDENT_REVIEW = _load_public_contract_schema(
    "host-independent-review.schema.json"
)
# Host transport is deliberately not the public Runner answer contract.  J8/J9
# paths are consumed and byte-verified before a pure academic answer is sent.
HOST_MATERIALIZED_STAGE_ANSWER = json.loads(json.dumps(ACADEMIC_STAGE_ANSWER))
HOST_MATERIALIZED_STAGE_ANSWER["$id"] = "https://paperspine5.local/contracts/host-materialized-stage-answer.schema.json"
HOST_MATERIALIZED_STAGE_ANSWER["$defs"]["canonical_payload"]["properties"]["host_canonical_files"] = {
    "type": "object", "required": ["files"],
    "properties": {"files": {"type": "object", "required": ["source", "pdf", "word"], "properties": {
        "source": {"type": "string", "pattern": "\\.tex$"},
        "pdf": {"type": "string", "pattern": "\\.pdf$"},
        "word": {"type": "string", "pattern": "\\.docx$"},
    }},
        "binding_spec_path": {"type": "string", "minLength": 1, "description": "Optional real canonical binding-spec file inside the task workspace."},
    },
}
HOST_MATERIALIZED_STAGE_ANSWER["$defs"]["review_payload"]["required"] = ["host_review_pages"]
HOST_MATERIALIZED_STAGE_ANSWER["$defs"]["review_payload"]["properties"]["host_review_pages"] = {
    "type": "object", "additionalProperties": False, "required": ["pdf", "word"],
    "properties": {kind: {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}} for kind in ("pdf", "word")},
}
HOST_MATERIALIZED_STAGE_ANSWER["$defs"]["package_payload"] = {
    "oneOf": [
        HOST_MATERIALIZED_STAGE_ANSWER["$defs"]["package_payload"],
        {"type": "object", "additionalProperties": False,
         "required": ["requested_scope"],
         "properties": {"requested_scope": {"const": "local_delivery"}},
         "description": "Prepare the existing accepted paper for local delivery. Host derives original J10 fields from current E6/J8/J9 and target receipts, preserves unknown/scoped evidence, and sets archive PASS only after real ZIP verification. review must be null. No external or author facts are inferred."},
    ]
}
FIGURE_CANDIDATE_REGISTRATION = _load_public_contract_schema(
    "figure-candidate-registration.schema.json"
)
FIGURE_FINAL_MAPPING_REGISTRATION = _load_public_contract_schema(
    "figure-final-mapping-registration.schema.json"
)


TOOLS = [
    _tool("paperspine5_runner_register_final_mapping", "Register an exact native PaperSpine reference mapping at J8, or revalidate an unchanged, already-consumed map at J9/J10 after a sealed same-task successor. Runner checks current canonical head, retained ledger membership, independent J7 winner, JSON/binary hashes, actual white-background pixels and exact opaque auxiliaries. No new downstream science, academic revision advance or browser acceptance is authorized.", {"task_id": TASK_ID, "registration": FIGURE_FINAL_MAPPING_REGISTRATION, "command_id": COMMAND_ID, "expected_revision": EXPECTED_REVISION, "actor": ACTOR, "user_data_root": USER_DATA_ROOT}, ["task_id", "registration", "command_id", "expected_revision"]),
    _tool("paperspine5_health", "Verify the shared PaperSpine5 runtime and canonical core location.", {}, []),
    _tool("paperspine5_create_task", "Create a recoverable Product Kernel task from read-only material roots; reuse command_id when retrying after a lost response.", {"command_id": {"type": "string", "description": "Unique idempotency key for this create intent."}, "materials_roots": {"type": "array", "items": {"type": "string"}}, "title": {"type": "string"}, "task_id": TASK_ID, "host": HOST, "user_data_root": USER_DATA_ROOT}, ["command_id", "materials_roots"]),
    _tool("paperspine5_import_legacy_task", "Read-only import of an explicitly supplied legacy 1.0 job into a Product Kernel task; reuse command_id for an identical retry.", {"command_id": {"type": "string"}, "job_path": JOB, "title": {"type": "string"}, "task_id": TASK_ID, "host": HOST, "user_data_root": USER_DATA_ROOT}, ["command_id", "job_path"]),
    _tool("paperspine5_list_tasks", "List recent Product Kernel tasks from the registry instead of scanning for job files.", {"status": {"type": "string"}, "user_data_root": USER_DATA_ROOT}, []),
    _tool("paperspine5_get_task", "Read one Product Kernel task and its current revision.", {"task_id": TASK_ID, "user_data_root": USER_DATA_ROOT}, ["task_id"]),
    _tool("paperspine5_list_artifacts", "List Product Kernel verified artifact projections; stale or missing bytes never appear as fresh payloads.", {"task_id": TASK_ID, "artifact_type": {"type": "string"}, "revision": {"type": "integer", "minimum": 0}, "user_data_root": USER_DATA_ROOT}, ["task_id"]),
    _tool("paperspine5_readiness", "Read the current Product Kernel verified layered readiness projection for manuscript, local delivery, submission, requested-scope completion, and external-action authority; unknown and stale remain blocking.", {"task_id": TASK_ID, "revision": {"type": "integer", "minimum": 0}, "user_data_root": USER_DATA_ROOT}, ["task_id"]),
    _tool("paperspine5_command", "Submit a non-runner versioned command envelope to Product Kernel. runner.* is rejected and must use the typed ProductRunner tools.", {"task_id": TASK_ID, "envelope": {"type": "object"}, "user_data_root": USER_DATA_ROOT}, ["task_id", "envelope"]),
    _tool("paperspine5_runner_snapshot", "Read the version-locked ProductRunner stage, open issues, next actions, and material/run-contract freshness.", {"task_id": TASK_ID, "user_data_root": USER_DATA_ROOT}, ["task_id"]),
    _tool("paperspine5_runner_bootstrap", "Bootstrap J1-J3 through the registered ProductRunner; inventories granted materials and opens typed configuration when required. Omit actor for ordinary calls; writer ownership and the default system actor are runtime-managed.", {"task_id": TASK_ID, "command_id": COMMAND_ID, "expected_revision": EXPECTED_REVISION, "actor": ACTOR, "user_data_root": USER_DATA_ROOT}, ["task_id", "command_id", "expected_revision"]),
    _tool("paperspine5_runner_renew_delegated_grant", "Reopen the same task's J3 configuration after an expired delegated local grant. Requires an explicit authenticated_local_user_session or host_user_message actor; never edits the old grant, and the subsequent typed J3 answer must mint a fresh grant.", {"task_id": TASK_ID, "command_id": COMMAND_ID, "expected_revision": EXPECTED_REVISION, "actor": ACTOR, "user_data_root": USER_DATA_ROOT}, ["task_id", "command_id", "expected_revision", "actor"]),
    _tool("paperspine5_runner_add_materials", "Add read-only material grants through ProductRunner copy-on-write inventory; never writes into source roots. Writer ownership is runtime-managed.", {"task_id": TASK_ID, "materials_roots": {"type": "array", "minItems": 1, "items": {"type": "string"}}, "command_id": COMMAND_ID, "expected_revision": EXPECTED_REVISION, "actor": ACTOR, "user_data_root": USER_DATA_ROOT}, ["task_id", "materials_roots", "command_id", "expected_revision"]),
    _tool("paperspine5_runner_answer_issue", "Answer the persisted configuration.required issue with the exact public J3 schema below. Use its opaque resume_token. Omit actor for guided mode; delegated_local_test requires the exact granting actor. Writer ownership is runtime-managed.", {"task_id": TASK_ID, "issue_id": {"type": "string"}, "resume_token": {"type": "string"}, "answer": RUN_CONFIGURATION_ANSWER, "command_id": COMMAND_ID, "expected_revision": EXPECTED_REVISION, "actor": ACTOR, "user_data_root": USER_DATA_ROOT}, ["task_id", "issue_id", "resume_token", "answer", "command_id", "expected_revision"]),
    _tool("paperspine5_runner_answer_academic_stage", "Submit one issue/revision/stage-bound, domain-neutral paperspine5.academic-stage-answer JSON object through the sole ProductRunner answer_issue CAS facade. This tool never authorizes external action or supplies trusted projections.", {"task_id": TASK_ID, "issue_id": {"type": "string"}, "resume_token": {"type": "string"}, "answer": ACADEMIC_STAGE_ANSWER, "command_id": COMMAND_ID, "expected_revision": EXPECTED_REVISION, "actor": ACTOR, "user_data_root": USER_DATA_ROOT}, ["task_id", "issue_id", "resume_token", "answer", "command_id", "expected_revision"]),
_tool("paperspine5_runner_answer_host_materialized_stage", "Atomically re-read and validate current task-local J8/J9/J10 files, bind a separate typed independent review where required, derive host identities, and submit through ProductRunner CAS without starting a Codex child profile or reading login credentials. J8/J9 require review; J9 block is persisted as REVISION_REQUIRED and returns to J8. J10 accepts exact answer.payload with only requested_scope=local_delivery and review=null; the host derives current accepted inputs while preserving unknown evidence and author facts. Host path transport is consumed before the public answer. External action remains unauthorized.", {"task_id": TASK_ID, "issue_id": {"type": "string"}, "resume_token": {"type": "string"}, "answer": HOST_MATERIALIZED_STAGE_ANSWER, "review": {"oneOf": [HOST_INDEPENDENT_REVIEW, {"type": "null"}]}, "command_id": COMMAND_ID, "expected_revision": EXPECTED_REVISION, "actor": ACTOR, "user_data_root": USER_DATA_ROOT}, ["task_id", "issue_id", "resume_token", "answer", "review", "command_id", "expected_revision"]),
    _tool("paperspine5_runner_register_figure_candidate", "Register one PNG, JPEG, or SVG candidate already staged below the active run_root runner/.staging/figure-candidates subtree. ProductRunner verifies current task/build/revision/J7, path containment, non-reparse bytes, hash, size and media magic; it derives the CAS path, artifact identity, receipt, authority and metadata without advancing the academic revision or deciding a winner.", {"task_id": TASK_ID, "registration": FIGURE_CANDIDATE_REGISTRATION, "command_id": COMMAND_ID, "expected_revision": EXPECTED_REVISION, "actor": ACTOR, "user_data_root": USER_DATA_ROOT}, ["task_id", "registration", "command_id", "expected_revision"]),
    _tool("paperspine5_runner_resume", "Resume ProductRunner from its persisted snapshot. After J3 this opens the current generic J4-J11 academic issue; awaiting stages require the dedicated academic answer tool. Writer ownership is runtime-managed.", {"task_id": TASK_ID, "command_id": COMMAND_ID, "expected_revision": EXPECTED_REVISION, "actor": ACTOR, "user_data_root": USER_DATA_ROOT}, ["task_id", "command_id", "expected_revision"]),
    _tool("paperspine5_runner_request_revision", "Explicitly reopen the current completed local paper for user-requested changes in the same task. scope manuscript returns to J8, figures to J7, figure_mapping to J6. A narrow figures recovery is also allowed for a blocked downstream same-task run when its persisted user feedback still binds an unchanged previous delivery; it atomically trims J7+ and creates a fresh J7 issue. Feedback is not an independent review or PASS. Preserve the previous completed paper/package, write new canonical files, then use the ordinary stages and real review. Normal resume is unchanged.", {"task_id": TASK_ID, "command_id": COMMAND_ID, "expected_revision": EXPECTED_REVISION, "feedback": {"type": "string", "minLength": 1, "maxLength": 8000}, "scope": {"type": "string", "enum": ["manuscript", "figures", "figure_mapping"]}, "actor": ACTOR, "user_data_root": USER_DATA_ROOT}, ["task_id", "command_id", "expected_revision", "feedback", "scope"]),
    _tool("paperspine5_open_product_workspace", "Open or reuse the Web-first PaperSpine5 landing for new and existing tasks.", {"task_id": TASK_ID, "user_data_root": USER_DATA_ROOT}, []),
    _tool("paperspine5_workspace_status", "Report whether the Web-first Product Kernel workspace service is running.", {"user_data_root": USER_DATA_ROOT}, []),
    _tool("paperspine5_stop_workspace", "Stop the Web-first workspace without deleting tasks; close_kernel also releases the cached local repository handle.", {"user_data_root": USER_DATA_ROOT, "close_kernel": {"type": "boolean"}}, []),
    _tool("paperspine5_status", "Legacy job compatibility: read an explicitly supplied repository-owned workflow snapshot.", {"job_path": JOB, "host": HOST}, ["job_path"]),
    _tool("paperspine5_save_configuration", "Legacy job compatibility only: validate and save configuration for an old 1.0 integration job.", {"job_path": JOB, "configuration": {"type": "object"}}, ["job_path", "configuration"]),
    _tool("paperspine5_advance", "Legacy job compatibility only: advance or resume an old 1.0 integration job.", {"job_path": JOB}, ["job_path"]),
    _tool("paperspine5_record_decision", "Legacy job compatibility only: persist a human figure-review decision.", {"job_path": JOB, "decision": {"type": "object"}}, ["job_path", "decision"]),
    _tool("paperspine5_record_signal", "Legacy job compatibility only: persist a host-neutral workflow signal.", {"job_path": JOB, "signal": {"type": "object"}}, ["job_path", "signal"]),
    _tool("paperspine5_publication_cycle", "Legacy job compatibility only: invoke a local Publication Cycle operation.", {"job_path": JOB, "request": {"type": "object"}}, ["job_path", "request"]),
    _tool("paperspine5_manuscript_status", "Legacy job compatibility only: read controlled manuscript source and product hashes.", {"job_path": JOB}, ["job_path"]),
    _tool("paperspine5_save_manuscript_revision", "Legacy job compatibility only: save a controlled source revision and rebuild products.", {"job_path": JOB, "revision": {"type": "object"}}, ["job_path", "revision"]),
    _tool("paperspine5_restore_manuscript_revision", "Legacy job compatibility only: restore a backed-up source revision.", {"job_path": JOB, "request": {"type": "object"}}, ["job_path", "request"]),
    _tool("paperspine5_confirm_manuscript_revision", "Legacy job compatibility only: confirm current rebuilt manuscript hashes.", {"job_path": JOB, "confirmation": {"type": "object"}}, ["job_path", "confirmation"]),
    _tool("paperspine5_answer_user_input", "Legacy job compatibility only: resolve a persisted issue with its resume token.", {"job_path": JOB, "resolution": {"type": "object"}}, ["job_path", "resolution"]),
    _tool("paperspine5_open_workspace", "Legacy job compatibility only: start the old job-specific loopback workspace.", {"job_path": JOB}, ["job_path"]),
]


def _result(payload: dict[str, Any], *, is_error: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}],
    }
    if is_error:
        result["isError"] = True
    return result


def _response(request_id: Any, result: dict[str, Any] | None = None, error: dict[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    payload["error" if error is not None else "result"] = error if error is not None else result
    return payload


def handle_mcp(message: dict[str, Any], project_root: Path) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    if request_id is None:
        return None
    if method == "initialize":
        requested = (message.get("params") or {}).get("protocolVersion")
        return _response(
            request_id,
            {
                "protocolVersion": requested or "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": RUNTIME_COMPONENT_VERSION},
            },
        )
    if method == "ping":
        return _response(request_id, {})
    if method == "tools/list":
        return _response(request_id, {"tools": TOOLS})
    if method == "tools/call":
        params = message.get("params") or {}
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        action = {
            "paperspine5_health": "health",
            "paperspine5_create_task": "create_task",
            "paperspine5_import_legacy_task": "import_legacy_task",
            "paperspine5_list_tasks": "list_tasks",
            "paperspine5_get_task": "get_task",
            "paperspine5_list_artifacts": "list_artifacts",
            "paperspine5_readiness": "readiness",
            "paperspine5_command": "command",
            "paperspine5_runner_snapshot": "runner_snapshot",
            "paperspine5_runner_bootstrap": "runner_bootstrap",
            "paperspine5_runner_renew_delegated_grant": "runner_renew_delegated_grant",
            "paperspine5_runner_add_materials": "runner_add_materials",
            "paperspine5_runner_answer_issue": "runner_answer_issue",
            "paperspine5_runner_answer_academic_stage": "runner_answer_academic_stage",
            "paperspine5_runner_answer_host_materialized_stage": "runner_answer_host_materialized_stage",
            "paperspine5_runner_register_figure_candidate": "runner_register_figure_candidate",
            "paperspine5_runner_register_final_mapping": "runner_register_final_mapping",
            "paperspine5_runner_resume": "runner_resume",
            "paperspine5_runner_request_revision": "runner_request_revision",
            "paperspine5_open_product_workspace": "open_product_workspace",
            "paperspine5_workspace_status": "workspace_status",
            "paperspine5_stop_workspace": "stop_workspace",
            "paperspine5_status": "snapshot",
            "paperspine5_save_configuration": "save_configuration",
            "paperspine5_advance": "advance",
            "paperspine5_record_decision": "record_decision",
            "paperspine5_record_signal": "record_signal",
            "paperspine5_publication_cycle": "publication_cycle",
            "paperspine5_manuscript_status": "manuscript_status",
            "paperspine5_save_manuscript_revision": "save_manuscript_revision",
            "paperspine5_restore_manuscript_revision": "restore_manuscript_revision",
            "paperspine5_confirm_manuscript_revision": "confirm_manuscript_revision",
            "paperspine5_answer_user_input": "answer_user_input",
            "paperspine5_open_workspace": "open_workspace",
        }.get(tool_name)
        if action is None:
            return _response(request_id, _result({"status": "FAIL", "error": f"unknown tool: {tool_name}"}, is_error=True))
        try:
            return _response(request_id, _result(dispatch(action, arguments, project_root)))
        except Exception as exc:  # MCP boundary converts domain errors into tool errors.
            return _response(request_id, _result(_error_payload(exc), is_error=True))
    return _response(request_id, error={"code": -32601, "message": f"method not found: {method}"})


def _write_ready_receipt(path: str | Path, payload: dict[str, Any], *, user_data_root: Path) -> Path:
    target = Path(path).expanduser().resolve()
    try:
        target.relative_to(user_data_root.resolve())
    except ValueError as exc:
        raise RuntimeErrorWithContext(
            "Web ready receipt must stay inside the configured user data root",
            code="READY_RECEIPT_PATH_INVALID",
        ) from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    try:
        os.chmod(temporary, 0o600)
    except OSError:
        pass
    os.replace(temporary, target)
    return target


def serve_product_web(
    project_root: Path,
    *,
    user_data_root: str | Path | None = None,
    port: int = 0,
    ready_file: str | Path | None = None,
) -> int:
    """Run the shared Product Web as a persistent standalone loopback service."""
    kernel, runner = _product_runtime(project_root, user_data_root)
    service = _product_application_service(project_root, user_data_root)
    from paperspine_figure_integration.p2_facades import create_business_server

    server = create_business_server(
        service,
        principal_id="local-user",
        session_id=f"standalone-web-{_RUNTIME_INSTANCE_ID}",
        port=port,
    )
    address = f"http://127.0.0.1:{server.server_port}/"
    receipt = {
        "contract": "paperspine5.web-workspace-receipt",
        "schema_version": "1.0",
        "status": "READY",
        "address": address,
        "host": "127.0.0.1",
        "port": server.server_port,
        "pid": os.getpid(),
        "surface": "product",
        "frontend": "web",
        "terminal_frontend": False,
        "user_data_root": str(kernel.user_data_root),
        "product_version": kernel.product_manifest.get("product_version"),
        "build_id": kernel.product_manifest.get("build_id"),
        "external_action_authorized": False,
    }
    if ready_file is not None:
        _write_ready_receipt(ready_file, receipt, user_data_root=kernel.user_data_root)
    print(json.dumps(receipt, ensure_ascii=False, indent=2), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        _close_kernels()
    return 0


def serve_stdio(project_root: Path, input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout) -> int:
    for line in input_stream:
        if not line.strip():
            continue
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("message must be a JSON object")
            _trace("mcp.received", method=message.get("method"), has_id=message.get("id") is not None)
            response = handle_mcp(message, project_root)
        except Exception as exc:
            _trace("mcp.exception", error=str(exc))
            response = _response(None, error={"code": -32700, "message": str(exc)})
        if response is not None:
            # ASCII-only framing avoids Windows locale encodings corrupting JSON-RPC pipes.
            output_stream.write(json.dumps(response, ensure_ascii=True, separators=(",", ":")) + "\n")
            output_stream.flush()
            _trace("mcp.sent", response_id=response.get("id"), has_error="error" in response)
    for server, thread in list(_SERVERS.values()):
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    _SERVERS.clear()
    _close_kernels()
    return 0


def serve_bridge(project_root: Path, input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout) -> int:
    try:
        envelope = json.load(input_stream)
        if not isinstance(envelope, dict):
            raise RuntimeErrorWithContext("bridge request must be a JSON object")
        if envelope.get("protocol") != BRIDGE_PROTOCOL or envelope.get("version") not in {
            BRIDGE_VERSION,
            *LEGACY_BRIDGE_VERSIONS,
        }:
            raise RuntimeErrorWithContext("bridge protocol or version is unsupported")
        host = envelope.get("host")
        if host not in SUPPORTED_HOSTS:
            raise RuntimeErrorWithContext("bridge host is unsupported")
        arguments = {**(envelope.get("payload") or {}), "job_path": envelope.get("job_path"), "host": host}
        result = dispatch(str(envelope.get("action")), arguments, project_root)
        payload = {"status": "OK", "request_id": envelope.get("request_id"), "result": result}
        code = 0
    except Exception as exc:
        payload = _error_payload(exc)
        code = 1
    output_stream.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    output_stream.flush()
    return code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PaperSpine5 local host runtime")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=("mcp", "bridge", "health", "web"),
        default="mcp",
    )
    parser.add_argument("--project-root")
    parser.add_argument("--user-data-root")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--ready-file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        project_root = locate_project_root(args.project_root)
        if args.mode == "mcp":
            return serve_stdio(project_root)
        if args.mode == "bridge":
            try:
                return serve_bridge(project_root)
            finally:
                # HostBridge is a one-request process. Release only leases this
                # runtime instance recorded and close its cached repository before
                # process exit; a foreign/crashed owner's lease remains fenced.
                _close_kernels()
        if args.mode == "web":
            return serve_product_web(
                project_root,
                user_data_root=args.user_data_root,
                port=args.port,
                ready_file=args.ready_file,
            )
        print(json.dumps(health(project_root), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
