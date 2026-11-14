"""Public Web launcher and thin MCP transport for PaperSpine.

Both reuse the same ApplicationService and saved profile. No state reconstruction,
research execution or command retries. The optional host wait repeats only normal
read-only timeouts in one attached session. Private subprocess modes are not Agent workers.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
import runpy
import subprocess
import sys
import time
import traceback
import uuid
import webbrowser
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from urllib.request import urlopen

sys.dont_write_bytecode = True


def _path(value: str | Path, base: Path | None = None) -> Path:
    path = Path(value).expanduser()
    return ((base / path) if base and not path.is_absolute() else path).resolve()


def _profile_preference() -> Path:
    return Path.home() / '.paperspine5/current-profile.json'


def selected_profile(args: argparse.Namespace) -> Path | None:
    explicit = getattr(args, 'profile_root', None) or os.environ.get('PAPERSPINE5_PROFILE_ROOT')
    if explicit:
        return _path(explicit)
    # Explicit source bindings must not inherit an unrelated remembered profile.
    if getattr(args, 'output_dir', None) or os.environ.get('PAPERSPINE5_USER_DATA_ROOT'):
        return None
    preference = _profile_preference()
    if preference.is_file():
        saved = json.loads(preference.read_text(encoding='utf-8-sig'))
        return _path(saved['profile_root'])
    return None


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def resolve_binding(args: argparse.Namespace, project_root: Path) -> dict[str, str]:
    """Reuse saved profile paths or explicit source-runtime paths; never migrate."""
    saved: dict[str, Any] = {}
    profile = selected_profile(args)
    if profile:
        candidates = [profile / "data/product-config.json", profile / "product-config.json"]
        config_path = next((p for p in candidates if p.is_file()), None)
        if config_path is None:
            raise ValueError("Profile has no product-config.json; supply the existing --user-data-root, --core-root and --domain-database instead. No profile was created.")
        saved = json.loads(config_path.read_text(encoding="utf-8-sig"))
        if not isinstance(saved, dict):
            raise ValueError("product-config.json must be an object")

    def selected(flag: str, field: str, env: str, default: str | Path | None = None) -> Path:
        explicit = getattr(args, flag, None) or os.environ.get(env)
        stored = saved.get(field)
        stored_path = _path(stored, profile) if stored else None
        if explicit and stored_path and _path(explicit) != stored_path:
            raise ValueError(f"--{flag.replace('_', '-')} differs from the saved profile; select one existing profile instead of mixing task stores")
        value = explicit or stored_path or default
        if value is None:
            raise ValueError("Provide --profile-root or --user-data-root (alias --output-dir) for the same Web task. The host does not select a different profile.")
        return _path(value)

    user = selected("output_dir", "user_data_root", "PAPERSPINE5_USER_DATA_ROOT")
    events = selected("domain_database", "domain_database", "PAPERSPINE5_DOMAIN_DATABASE",
                      user / "registry/application.sqlite3")
    # The installed launcher fixes core to the active install. Read that pointer
    # only; do not run prepare/install/migrate or change the active build.
    core_default = project_root
    if profile and not saved.get("core_root") and not getattr(args, "core_root", None):
        state_file = profile / ".paperspine5-lifecycle/profile-state.json"
        if state_file.is_file():
            state = json.loads(state_file.read_text(encoding="utf-8-sig"))
            enabled = [x for x in state.get("enabled_entries", []) if x.get("enabled")
                       and x.get("build_id") == state.get("active_build_id")]
            if len(enabled) != 1:
                raise ValueError("Cannot identify this profile's active core; supply its existing --core-root")
            core_default = _path(enabled[0]["install_root"], profile)
    core = selected("core_root", "core_root", "PAPERSPINE5_CORE_ROOT", core_default)
    contracts = selected("contracts_root", "contracts_root", "PAPERSPINE5_CONTRACTS_ROOT",
                         project_root / "03_联合开发/contracts")
    if not core.is_dir() or not contracts.is_dir():
        raise ValueError("The selected core/contracts directory does not exist")
    # Existing stores must never be silently split by the default events path.
    if user.is_dir() and any(user.iterdir()) and not events.is_file():
        raise ValueError("Existing user-data has no database at the selected path. Pass the Web process's exact --domain-database; no replacement event store was created.")
    reviewer = getattr(args, "trusted_reviewer_id", None)
    if reviewer is not None and not reviewer.strip():
        raise ValueError("--trusted-reviewer-id must be the actual reviewer's non-empty runtime identity")
    binding = {"project_root": str(project_root), "user_data_root": str(user),
            "core_root": str(core), "domain_database": str(events), "contracts_root": str(contracts),
            "principal_id": getattr(args, "principal_id", None) or "paper-spine-host"}
    # Never infer reviewer authority from a task, request body, profile or writer.
    if reviewer is not None:
        binding["reviewer_id"] = reviewer
    return binding


def _enable_dependencies(root: Path) -> None:
    """Use this interpreter, or the existing bundled runtime; never install."""
    try:
        from mcp.server.mcpserver import MCPServer  # noqa: F401
        return
    except ImportError:
        pass
    for vendor in (root / "runtime_vendor/windows-py312", root / "06_插件化/runtime_vendor/windows-py312"):
        if vendor.is_dir() and sys.version_info[:2] == (3, 12):
            sys.path[:0] = [str(p) for p in (vendor, vendor / "win32", vendor / "win32/lib",
                                            vendor / "pythonwin", vendor / "pywin32_system32")]
            if os.name == "nt" and hasattr(os, "add_dll_directory"):
                globals()["_DLL_HANDLE"] = os.add_dll_directory(str(vendor / "pywin32_system32"))
            from mcp.server.mcpserver import MCPServer  # noqa: F401
            return
    raise RuntimeError("MCP2 is unavailable in this Python. Run with the product's existing Python environment or --python-executable; no install or login is needed.")


def _python(args: argparse.Namespace, root: Path) -> str:
    explicit = getattr(args, "python_executable", None) or os.environ.get("PAPERSPINE5_PYTHON")
    candidates = [explicit] if explicit else [sys.executable,
        str(root / "runtime_vendor/windows-py312/python.exe"),
        str(root / "06_插件化/runtime_vendor/windows-py312/python.exe")]
    diagnostics = []
    for executable in dict.fromkeys(x for x in candidates if x):
        if not Path(executable).is_file():
            continue
        try:
            result = subprocess.run([executable, "-B", "-X", "utf8", str(Path(__file__).resolve()), "--probe", str(root)],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except subprocess.TimeoutExpired as exc:
            diagnostics.append(exc.stderr or b"")
            continue
        if result.returncode == 0:
            return executable
        diagnostics.append(result.stderr or result.stdout)
    for diagnostic in diagnostics:
        _forward_stderr(diagnostic)
    raise RuntimeError("No existing MCP2 Python runtime found. Run this CLI with the working Python environment or pass --python-executable <python>; no task was changed.")


def _public_name(name: str) -> bool:
    return name.startswith("paperspine_") and not name.startswith("paperspine_runner_")


def bind_task(arguments: dict[str, Any], task_id: str | None) -> dict[str, Any]:
    """Bind transport arguments without filling versions, options or academic facts."""
    value = json.loads(json.dumps(arguments))
    target = value.get("request", value)
    if not isinstance(target, dict):
        raise ValueError("MCP request must be an object")
    supplied = [x for x in (value.get("task_id"), target.get("task_id")) if x is not None]
    if task_id and any(x != task_id for x in supplied):
        raise ValueError("MCP arguments refer to a different task than --task-id")
    if task_id:
        target["task_id"] = task_id
    return value


def _web_state(profile: Path) -> Path:
    return profile / '.paperspine5-web/public-workspace.json'


def _process_running(pid: Any) -> bool:
    if type(pid) is not int or pid <= 0:
        return False
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() != 87  # unknown/access denied is not proof of exit
        try:
            code = wintypes.DWORD()
            return not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value == 259
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _starting_state(profile: Path) -> dict[str, Any]:
    try:
        return json.loads(_web_state(profile).with_name('public-starting.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def _web_ready(state: dict[str, Any]) -> bool:
    port = state.get('port')
    if type(port) is not int or not 0 < port < 65536 or not state.get('instance_id'):
        return False
    try:
        # Readiness must not scan every task/material directory; instance identity remains mandatory.
        with urlopen(f'http://127.0.0.1:{port}/api/v1/session', timeout=2) as response:
            return response.status == 200 and response.headers.get('X-PaperSpine-Instance') == state['instance_id']
    except (OSError, ValueError):
        return False


def _read_web_state(profile: Path) -> dict[str, Any]:
    try:
        value = json.loads(_web_state(profile).read_text(encoding='utf-8-sig'))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def _runtime_code_identity(binding: dict[str, str]) -> dict[str, Any]:
    """Identify reload-sensitive first-party inputs, never task or vendor data."""
    files = {Path(__file__).resolve()}
    for key in ("project_root", "core_root"):
        source = Path(binding[key]) / "03_联合开发/src/paperspine_figure_integration"
        files.update(path.resolve() for path in source.rglob("*.py")
                     if path.is_file() and "__pycache__" not in path.parts)
    files.update(path.resolve() for path in Path(binding["contracts_root"]).rglob("*.json")
                 if path.is_file())
    digest = hashlib.sha256()
    for path in sorted(files, key=str):
        digest.update(str(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return {"sha256": digest.hexdigest(), "file_count": len(files)}


def _runtime_code_status(state: dict[str, Any], binding: dict[str, str]) -> str:
    recorded = state.get("runtime_code") or {}
    if not recorded.get("sha256"):
        return "unverified"  # An older receipt cannot attest which code was loaded.
    return "current" if recorded == _runtime_code_identity(binding) else "changed"


def web_status(args: argparse.Namespace, root: Path) -> int:
    profile = selected_profile(args) or Path.home() / '.paperspine5/profiles/default'
    binding = resolve_binding(argparse.Namespace(**{**vars(args), 'profile_root': str(profile)}), root)
    state = _read_web_state(profile)
    ready = _web_ready(state)
    matches = all(state.get('binding', {}).get(k) == binding[k]
                  for k in ('project_root', 'user_data_root', 'core_root', 'domain_database', 'contracts_root'))
    code_status = _runtime_code_status(state, binding) if ready and matches else 'unverified'
    live = _process_running(state.get('process_id')) or _process_running(_starting_state(profile).get('process_id'))
    status = 'READY' if ready and matches else 'DIFFERENT_RUNTIME' if ready else 'UNCONFIRMED' if live else 'STOPPED'
    if ready and matches and code_status == 'changed':
        status = 'STALE_CODE'
    print(json.dumps({'status': status,
                      'profile_root': str(profile), 'address': state.get('address') if ready else None,
                      'binding_matches': matches, 'runtime_code_status': code_status,
                      'process_id': state.get('process_id')}, ensure_ascii=False))
    return 0 if status == 'READY' else 1


def _stop_request(ready: Path, instance: str) -> Path:
    if not isinstance(instance, str) or len(instance) != 32 or any(c not in '0123456789abcdef' for c in instance):
        raise ValueError('Invalid workbench instance identity')
    return ready.with_name(f'public-stop-{instance}')


def web_stop(args: argparse.Namespace, root: Path) -> int:
    profile = selected_profile(args)
    if profile is None:
        raise ValueError('An explicit workbench profile is required')
    state = _read_web_state(profile)
    pid = state.get('process_id')
    if _web_ready(state):
        if state.get('binding', {}).get('project_root') != str(root) or state.get('stop_supported') is not True:
            raise ValueError('This workbench belongs to another runtime or predates managed shutdown')
        request = _stop_request(_web_state(profile), state['instance_id'])
        request.touch()
        deadline = time.monotonic() + 15
        while _process_running(pid) and time.monotonic() < deadline:
            time.sleep(.2)
    if _process_running(pid) or _process_running(_starting_state(profile).get('process_id')):
        raise RuntimeError('The workbench has not confirmed shutdown. Check status before replacing it.')
    print(json.dumps({'status': 'STOPPED', 'profile_root': str(profile)}, ensure_ascii=False))
    return 0


def web_launch(args: argparse.Namespace, root: Path) -> int:
    """Start/reuse the same public facade; no Agent, task creation or migration."""
    profile = selected_profile(args) or Path.home() / '.paperspine5/profiles/default'
    profile = profile.resolve()
    if profile == root or root in profile.parents or profile in root.parents:
        raise ValueError('Keep the local profile separate from installed product files')
    configs = [profile / 'data/product-config.json', profile / 'product-config.json']
    config = next((p for p in configs if p.is_file()), None)
    if config is None:
        supplied = [getattr(args, key, None) for key in ('output_dir', 'core_root', 'domain_database')]
        if any(supplied) and not all(supplied):
            raise ValueError('Binding an existing Web requires its exact user-data, core and event database paths together')
        if all(supplied):
            if not Path(supplied[0]).is_dir() or not Path(supplied[1]).is_dir() or not Path(supplied[2]).is_file():
                raise ValueError('Existing Web paths do not exist; no profile was changed')
            user, core, events = map(_path, supplied)
        else:
            if profile.exists() and any(profile.iterdir()):
                raise ValueError('Nonempty profile has no binding. Supply its existing Web paths; no replacement task store was created')
            user, core, events = profile / 'user', root, profile / 'events.db'
        config = profile / 'product-config.json'
        _write_json(config, {'schema_version': 1, 'user_data_root': str(user), 'core_root': str(core),
                             'domain_database': str(events)})
    bound_args = argparse.Namespace(**{**vars(args), 'profile_root': str(profile)})
    binding = resolve_binding(bound_args, root)
    state = _read_web_state(profile)
    if _web_ready(state):
        if any(state.get('binding', {}).get(k) != binding[k]
               for k in ('project_root', 'user_data_root', 'core_root', 'domain_database', 'contracts_root')):
            raise ValueError('This profile already has a live different runtime. Preserve it and stop its exact owned process before switching code; no duplicate server started')
        code_status = _runtime_code_status(state, binding)
        if code_status == 'changed':
            raise RuntimeError(f"Web code changed after process {state.get('process_id')} started. Restart that same owned service with this profile and port; no task/configuration was changed and no duplicate server was started.")
        state = {**state, 'reused': True, 'runtime_code_status': code_status}
    else:
        if _process_running(state.get('process_id')) or _process_running(_starting_state(profile).get('process_id')):
            raise RuntimeError('The recorded Web process is still live but its response is unconfirmed. Inspect that same process; no duplicate server started')
        port = getattr(args, 'port', 0) or state.get('port', 0)
        if type(port) is not int or not 0 <= port < 65536:
            raise ValueError('Port must be an integer from 0 to 65535')
        ready = _web_state(profile)
        ready.parent.mkdir(parents=True, exist_ok=True)
        ready.unlink(missing_ok=True)
        log_path = ready.with_suffix('.log')
        job = {'binding': binding, 'ready_file': str(ready), 'port': port}
        with log_path.open('ab') as log:
            process = subprocess.Popen([_python(args, root), '-B', '-X', 'utf8', str(Path(__file__).resolve()),
                                        '--web-server', json.dumps(job)], stdin=subprocess.DEVNULL,
                stdout=log, stderr=subprocess.STDOUT, cwd=profile,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        _write_json(ready.with_name('public-starting.json'), {'process_id': process.pid, 'binding': binding})
        deadline = time.monotonic() + max(1, min(getattr(args, 'wait_seconds', 20), 50))
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f'Public Web did not start (exit {process.returncode}); details: {log_path}')
            state = _read_web_state(profile)
            if _web_ready(state):
                break
            time.sleep(.2)
        else:
            # The child may still start; preserve its handle and never claim failure
            # means no effect. A later status reads this same runtime file.
            raise RuntimeError(f'Web startup still unconfirmed; inspect status before retrying. Process {process.pid}; log: {log_path}')
        state = {**state, 'reused': False, 'runtime_code_status': _runtime_code_status(state, binding)}
    if getattr(args, 'remember', False) or profile == (Path.home() / '.paperspine5/profiles/default').resolve():
        _write_json(_profile_preference(), {'profile_root': str(profile)})
    browser_opened = False
    if not getattr(args, 'no_open', True):
        browser_opened = bool(webbrowser.open(state['address']))
    print(json.dumps({**state, 'status': 'READY', 'profile_root': str(profile),
                      'scientific_agent_started': False,
                      'browser_opened': browser_opened,
                      'browser_owner': 'host' if getattr(args, 'no_open', True) else 'external'}, ensure_ascii=False, indent=2))
    return 0


def _web_server(job: dict[str, Any]) -> int:
    binding = job['binding']
    root = Path(binding['project_root'])
    code_identity = _runtime_code_identity(binding)
    _enable_dependencies(root)
    sys.path.insert(0, str(root / '03_联合开发/src'))
    from paperspine_figure_integration.p2_facades import build_application, create_business_server
    service, kernel = build_application(**{k: binding[k] for k in
        ('user_data_root', 'core_root', 'domain_database', 'contracts_root')})
    server = create_business_server(service, principal_id='paperspine-web-user',
        session_id='local-public-web', reviewer_id=None, port=job['port'])
    instance = uuid.uuid4().hex
    ready = Path(job['ready_file'])
    stop_request = _stop_request(ready, instance)
    original_handler = server.RequestHandlerClass
    class BoundHandler(original_handler):
        def end_headers(self):
            self.send_header('X-PaperSpine-Instance', instance)
            super().end_headers()
    server.RequestHandlerClass = BoundHandler
    if code_identity != _runtime_code_identity(binding):
        server.server_close()
        kernel.close()
        raise RuntimeError('Product code changed during Web startup; retry this same profile after the update finishes.')
    _write_json(ready, {'address': f'http://127.0.0.1:{server.server_port}/',
        'port': server.server_port, 'process_id': os.getpid(), 'instance_id': instance,
        'binding': binding, 'runtime_code': code_identity, 'stop_supported': True})
    try:
        server.timeout = .25
        server.daemon_threads = False
        while not stop_request.is_file():
            server.handle_request()
    finally:
        server.server_close()
        kernel.close()
        stop_request.unlink(missing_ok=True)
    return 0


def _method_guidance(payload: dict[str, Any], args: argparse.Namespace,
                     binding: dict[str, str]) -> dict[str, Any]:
    """Attach local advice after a successful public read, without changing its facts."""
    usage = [sys.executable, str(Path(__file__).resolve().with_name("paperspine5_web.py")),
             "host", "methods", "--task-id", args.task_id]
    for field, flag in (("project_root", "--project-root"), ("user_data_root", "--user-data-root"),
                        ("core_root", "--core-root"), ("domain_database", "--domain-database"),
                        ("contracts_root", "--contracts-root"), ("principal_id", "--principal-id")):
        usage.extend([flag, binding[field]])
    if getattr(args, "python_executable", None):
        usage.extend(["--python-executable", args.python_executable])
    if getattr(args, "stage", None) is not None:
        usage.extend(["--stage", args.stage])
    for focus in getattr(args, "focus", []) or []:
        usage.extend(["--focus", focus])
    for resource in getattr(args, "resource", []) or []:
        usage.extend(["--resource", resource])
    try:
        from paperspine_methods import DEFAULT_TEXT_MAX_CHARS, method_guidance, skill_root_for_script
        max_chars = getattr(args, "max_chars", None)
        if getattr(args, "format", "json") == "text" and max_chars is None:
            max_chars = DEFAULT_TEXT_MAX_CHARS
        guidance = method_guidance(payload, skill_root_for_script(__file__), task_id=args.task_id,
            stage=getattr(args, "stage", None), focuses=getattr(args, "focus", None),
            resources=getattr(args, "resource", None),
            include_text=getattr(args, "include_text", False), compact=args.host_command == "snapshot",
            start_line=getattr(args, "start_line", 1), max_lines=getattr(args, "max_lines", None),
            max_chars=max_chars, expect_sha256=getattr(args, "expect_sha256", None))
    except Exception as exc:
        # Advice must not erase a valid task even if its helper is missing/broken.
        guidance = {"advisory": True, "status": "unavailable", "selected_count": None,
                    "available_count": None, "returned_source_count": 0, "paths": [], "errors": [
                        {"code": "method_guidance_unavailable", "message": str(exc)}],
                    "compatibility_instruction": "Method guidance is unavailable; no Skill coverage, reading, execution or review is established."}
    guidance["usage_argv"] = usage
    guidance["usage_instruction"] = (
        "Run usage_argv as an argument vector with this same task/store binding to list descriptors and catalog_paths first. "
        "Then append --resource <one exact catalog path> --include-text and retrieve originals one file at a time "
        "with their current_application notes. Prefer --format text --max-chars 8000 for a directly readable "
        "single-resource frame; follow its next line with --expect-sha256 <returned content hash>. "
        "Require BEGIN, END and returned_chars in the displayed page; missing END means retry with a smaller limit. "
        "Use the complete local_file via an authorized file reader if a line cannot fit; never repeat a non-advancing cursor. "
        "Default JSON remains available; --max-lines and --max-chars bound source text there. "
        "text_complete means only that the helper returned the whole source in this reply, not that the host displayed "
        "it or the Agent read/applied it. Explicit resources override selection filters, not task state or research scope."
    )
    return guidance


def local_methods(args: argparse.Namespace) -> int:
    """Read explicit installed method data; do not claim a current task observation."""
    from paperspine_methods import DEFAULT_TEXT_MAX_CHARS, format_method_text, method_guidance, skill_root_for_script
    if not args.resource:
        raise ValueError("Local reading requires an explicit registered resource")
    text_mode = getattr(args, "format", "json") == "text"
    budget = getattr(args, "max_chars", None)
    if text_mode and budget is None:
        budget = DEFAULT_TEXT_MAX_CHARS
    guidance = method_guidance({"task_id": args.task_id}, skill_root_for_script(__file__),
        task_id=args.task_id, stage=getattr(args, "stage", None),
        focuses=getattr(args, "focus", []), resources=args.resource,
        include_text=getattr(args, "include_text", False) or text_mode,
        start_line=getattr(args, "start_line", 1), max_lines=getattr(args, "max_lines", None),
        max_chars=budget, expect_sha256=getattr(args, "expect_sha256", None))
    guidance["task_observation"] = {"observed": False, "task_id_is_context_only": True,
        "instruction": "Use the previously read actual task scope. This local method read does not observe or change configuration, choices, versions or permissions."}
    guidance["context"]["configuration_source"] = "not observed (local method read)"
    if getattr(args, "stage", None) is None:
        guidance["context"]["stage_source"] = "not observed (local method read)"
    if text_mode and guidance.get("status") == "ok":
        observation = ("task_observation: false; task_id is context only.\n"
                       "configuration_source: not observed (local method read); no defaults applied.\n"
                       "Task scope, choices, version and permissions must come from the actual task read.\n")
        rendered = observation + format_method_text(guidance, budget - len(observation))
        if hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer.write(rendered.encode("utf-8"))
            sys.stdout.buffer.flush()
        else:
            sys.stdout.write(rendered)
    else:
        print(json.dumps({"method_guidance": guidance}, ensure_ascii=False, indent=2))
    return 0 if guidance.get("status") == "ok" else 1


def _forward_stderr(value: str | bytes | None) -> None:
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    if value:
        sys.stderr.write(value)
        if not value.endswith("\n"):
            sys.stderr.write("\n")


def _task_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Compact saved facts. A public read cannot observe the external host's life."""
    names = ("artifacts", "domain_artifacts", "decisions", "domain_decisions", "milestones")
    counts = {name: len(payload.get(name) or []) for name in names}
    decisions = payload.get("domain_decisions", payload.get("decisions")) or []
    pending = [d for d in decisions if d.get("status") == "pending" and not d.get("stale")]
    summary = {key: payload[key] for key in (
        "task_id", "task_version", "stage", "effective_stage", "stage_source", "status", "summary",
        "workspace_root", "configuration", "configuration_source", "configuration_stale", "skill_bridge",
        "created_at", "updated_at"
    ) if key in payload}
    # The bridge includes discovered candidates for Web. A host summary only
    # needs its file locations; retaining that array can recreate a huge reply.
    if isinstance(summary.get("skill_bridge"), dict):
        bridge = summary["skill_bridge"]
        summary["skill_bridge"] = {key: value for key, value in bridge.items()
                                   if key != "figure_candidates"}
        counts["figure_candidates"] = len(bridge.get("figure_candidates") or [])
    summary.update(counts=counts, pending_decisions=[
        {k: d[k] for k in ("decision_id", "decision_type", "prompt", "figure") if k in d} for d in pending],
        summary_only=True, host_observation={
            "live_status": "not_observed", "source": "public task snapshot",
            "boundary": "task_version/stage/status are saved task facts. This read does not observe whether the external host is running, stalled or stopped. Missing/null summaries establish none of those states."},
        recovery_hint="Use this same profile/task_id. Read the saved skill_bridge files and paperspine_list_task_events, compare task_version, and inspect the actual host session before deciding what work remains; this summary issues no continuation command.")
    return summary


def _publish_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    """A host view only: retain command/event facts, omit the repeated projection."""
    if (payload.get("contract") != "paperspine.command-result"
            or payload.get("result_type") != "completed" or payload.get("error")
            or not isinstance(payload.get("projection"), dict)):
        return payload
    return {**{key: value for key, value in payload.items() if key != "projection"},
            "contract": "paperspine.host-command-receipt", "schema_version": "1.0",
            "source_contract": payload["contract"], "source_schema_version": payload.get("schema_version"),
            "projection_omitted": True,
            "full_read": {"tool": "paperspine_get_task", "arguments": {"task_id": payload["task_id"]}},
            "full_response_hint": "Omit --summary to retain the original command result, including its projection"}


def _run_public_job(args: argparse.Namespace, root: Path, job: dict[str, Any]) -> subprocess.CompletedProcess:
    # A working current interpreter can run the same MCP client here. Both
    # transports use the public server; no ApplicationService call bypasses MCP.
    # Explicit alternate runtimes retain the existing probe/child boundary.
    if (not (getattr(args, "python_executable", None) or os.environ.get("PAPERSPINE5_PYTHON"))
            and importlib.util.find_spec("mcp") is not None):
        try:
            _enable_dependencies(root)
        except Exception:
            pass  # Dependency selection only, before any public request.
        else:
            async def bounded_client():
                if job["operation"] == "wait":
                    # Session enforces each RPC timeout; a normal API timeout
                    # does not impose a lifetime limit on the attached process.
                    return await _client(job)
                return await asyncio.wait_for(_client(job), timeout=job["timeout"] + 10)
            try:
                payload, status = asyncio.run(bounded_client())
            except Exception as exc:
                # Includes ExceptionGroup: keep the root traceback and unknown
                # write outcome. Never restart/retry after entering the client.
                traceback.print_exception(exc, file=sys.stderr)
                message = ("Public MCP reply timed out; outcome unknown. Read the same task/events before retrying a write."
                           if isinstance(exc, TimeoutError) else str(exc))
                payload = {"error": {"code": "public_transport_failed", "message": message},
                           "automatic_retry": False}
                status = 1
            return subprocess.CompletedProcess([], status, json.dumps(payload, ensure_ascii=True), "")
    return subprocess.run([_python(args, root), "-B", "-X", "utf8", str(Path(__file__).resolve()), "--client"],
        input=json.dumps(job), capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=None if job["operation"] == "wait" else args.timeout_seconds + 10,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})


def call(args: argparse.Namespace, root: Path) -> int:
    if args.host_command == "methods":
        from paperspine_methods import validate_paging
        args.include_text = getattr(args, "include_text", False) or getattr(args, "format", "json") == "text"
        validate_paging(resources=getattr(args, "resource", None), include_text=args.include_text,
                        start_line=getattr(args, "start_line", 1), max_lines=getattr(args, "max_lines", None),
                        max_chars=getattr(args, "max_chars", None), expect_sha256=getattr(args, "expect_sha256", None),
                        output_format=getattr(args, "format", "json"))
    arguments: dict[str, Any] = {}
    name = getattr(args, "tool", None)
    if args.host_command in ("snapshot", "methods"):
        name = "paperspine_get_task"
        arguments = {"task_id": args.task_id}
    elif args.host_command == "wait":
        name = "paperspine_wait_for_task_change"
        arguments = {"task_id": args.task_id, "after_version": args.after_version,
                     "timeout_seconds": args.wait_seconds}
    elif args.host_command == "call":
        raw = sys.stdin.read() if args.arguments_file == "-" else Path(args.arguments_file).read_text(encoding="utf-8-sig")
        arguments = json.loads(raw)
        if not isinstance(arguments, dict):
            raise ValueError("--arguments-file must contain one MCP arguments object")
        arguments = bind_task(arguments, args.task_id)
    if name and not _public_name(name):
        raise ValueError(f"Invalid public tool name {name!r}. Use the exact paperspine_* public tool name returned by host tools, with the same profile and task. Do not switch a current-host task to --legacy-runner to repair a tool-name error; that flag is only for an explicitly requested legacy Runner task.")
    binding = resolve_binding(args, root)
    if args.host_command == "tools" and getattr(args, "task_id", None):
        _forward_stderr("host tools: --task-id is compatibility context only; schemas are process-wide. No task was read or used to filter tools; --tool selects an exact public name.")
    # The new method view uses exactly the existing snapshot public read shape.
    operation = "snapshot" if args.host_command == "methods" else args.host_command
    job = {"binding": binding, "operation": operation, "name": name, "arguments": arguments,
           "timeout": args.timeout_seconds}
    try:
        result = _run_public_job(args, root, job)
    except subprocess.TimeoutExpired as exc:
        _forward_stderr(exc.stderr)
        raise RuntimeError("Public MCP reply timed out; outcome unknown. Read the same task/events before retrying a write; no automatic retry was made.") from exc
    # Forward diagnostics before parsing: empty/malformed JSON must not hide the
    # actual child failure (including nested MCP ExceptionGroup tracebacks).
    _forward_stderr(result.stderr)
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except ValueError as exc:
            raise RuntimeError(f"Public MCP returned invalid JSON (exit {result.returncode}); outcome unknown. See stderr; no automatic retry was made.") from exc
        if (args.host_command in ("snapshot", "methods") and result.returncode == 0
                and isinstance(payload, dict) and not payload.get("error")):
            guidance = _method_guidance(payload, args, binding)
            if args.host_command == "methods":
                # Keep the actual saved scope, but do not bury original method text
                # behind a task's potentially huge artifact/history projections.
                payload = {key: payload[key] for key in (
                    "task_id", "task_version", "stage", "effective_stage", "status", "configuration"
                ) if key in payload}
            if args.host_command == "snapshot" and getattr(args, "summary", False):
                payload = _task_summary(payload)
            payload = {**payload, "method_guidance": guidance}
            if args.host_command == "methods" and getattr(args, "format", "json") == "text" and guidance.get("status") == "ok":
                from paperspine_methods import DEFAULT_TEXT_MAX_CHARS, format_method_text
                rendered = format_method_text(guidance, getattr(args, "max_chars", None) or DEFAULT_TEXT_MAX_CHARS)
                # Bypass Windows stdout newline translation; the source length
                # and raw-byte hash must still be reconstructible after capture.
                if hasattr(sys.stdout, "buffer"):
                    sys.stdout.buffer.write(rendered.encode("utf-8"))
                    sys.stdout.buffer.flush()
                else:
                    sys.stdout.write(rendered)
                return 0
        if (args.host_command == "call" and name == "paperspine_publish_artifact"
                and result.returncode == 0 and isinstance(payload, dict)
                and getattr(args, "summary", False)):
            payload = _publish_receipt(payload)
        print(json.dumps(payload, ensure_ascii=args.host_command != "methods", indent=2))
    else:
        raise RuntimeError("Public MCP returned no JSON reply; outcome unknown. Check this runtime's stderr and the same task before retrying.")
    if (args.host_command == "methods" and not result.returncode
            and isinstance(payload, dict) and payload.get("method_guidance", {}).get("status") in ("partial", "unavailable")):
        return 1
    return result.returncode


@asynccontextmanager
async def _stdio_session(job: dict[str, Any]) -> AsyncIterator[Any]:
    """The existing isolated stdio child; the transport outside Windows."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    binding = job["binding"]
    params = StdioServerParameters(command=sys.executable,
        args=["-B", "-X", "utf8", str(Path(__file__).resolve()), "--server", json.dumps(binding)],
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    async with stdio_client(params) as streams:
        async with ClientSession(*streams, read_timeout_seconds=job["timeout"]) as session:
            yield session


@asynccontextmanager
async def _memory_session(job: dict[str, Any]) -> AsyncIterator[Any]:
    """Serve the identical public MCP server in-process over official memory streams.

    A stdio child needs OS pipes that Windows forbids in this sandbox, so the
    same p2_facades server, schemas, validation, identity binding and lazy
    startup are kept while the transport becomes a pair of in-memory streams.
    The kernel is always closed, including on failure or cancellation.
    """
    import anyio
    from mcp import ClientSession
    from mcp.shared.memory import create_client_server_memory_streams

    binding = job["binding"]
    sys.path.insert(0, str(Path(binding["project_root"]) / "03_联合开发/src"))
    from paperspine_figure_integration.p2_facades import build_application, create_mcp_server
    service, kernel = build_application(
        **{key: binding[key] for key in ("user_data_root", "core_root", "domain_database", "contracts_root")},
        initialize_on_startup=False)
    try:
        server = create_mcp_server(service, principal_id=binding["principal_id"],
                                   reviewer_id=binding.get("reviewer_id"))
        lowlevel = server._lowlevel_server
        async with create_client_server_memory_streams() as (client_streams, server_streams):
            async with anyio.create_task_group() as task_group:
                task_group.start_soon(lowlevel.run, server_streams[0], server_streams[1],
                                      lowlevel.create_initialization_options())
                try:
                    async with ClientSession(*client_streams, read_timeout_seconds=job["timeout"]) as session:
                        yield session
                finally:
                    # The server task ends only on stream EOF or cancellation;
                    # never leave it serving after the session or any failure.
                    task_group.cancel_scope.cancel()
    finally:
        kernel.close(flush=not service._startup_pending)


async def _client(job: dict[str, Any]) -> tuple[dict[str, Any], int]:
    binding = job["binding"]
    _enable_dependencies(Path(binding["project_root"]))
    # Confined Windows hosts may deny asyncio named pipes. Select the exact
    # same public MCP server over memory streams before any request. Other
    # platforms keep the existing stdio route; the operation body below is shared.
    transport = _memory_session(job) if os.name == "nt" else _stdio_session(job)
    async with transport as session:
        await session.initialize()
        inventory = await session.list_tools()
        tools = [x.model_dump(mode="json", by_alias=True, exclude_none=True) for x in inventory.tools
                 if _public_name(x.name)]
        while getattr(inventory, "next_cursor", None):
            inventory = await session.list_tools(params={"cursor": inventory.next_cursor})
            tools.extend(x.model_dump(mode="json", by_alias=True, exclude_none=True) for x in inventory.tools
                         if _public_name(x.name))
        matches = [x for x in tools if x["name"] == job["name"]]
        if job["name"] == "paperspine_submit_review" and not matches:
            return {"error": {"code": "tool_unavailable", "message":
                "Independent review is not enabled in this process. The actual reviewer must explicitly use --trusted-reviewer-id with their existing runtime identity; the writer must not invent or substitute one."}}, 1
        if job["operation"] == "tools":
            if job["name"] and not matches:
                return {"error": {"code": "tool_unavailable", "message": f"Tool {job['name']!r} is not exposed by this public MCP process; use an exact name from host tools"}}, 1
            return (matches[0] if job["name"] else {"tools": tools}), 0
        if not matches:
            return {"error": {"code": "tool_unavailable", "message": f"Tool {job['name']!r} is not exposed. Read host tools for this public process; no alternate execution route was used"}}, 1
        if job["operation"] == "wait":
            return await _wait_for_change(session, job["arguments"])
        result, failed = _tool_result(await session.call_tool(job["name"], job["arguments"]))
        # Reads never register/migrate a legacy-only task as a side effect.
        if failed and job["operation"] == "snapshot" and (result.get("error") or {}).get("code") == "not_found":
            result["hint"] = "Check the exact Web domain database. For a Kernel-only historical task, explicit --legacy-runner snapshot remains available; no resume/import was submitted."
        return result, 1 if failed else 0


def _tool_result(response: Any) -> tuple[dict[str, Any], bool]:
    result = response.structured_content
    if result is None:
        text = "\n".join(x.text for x in response.content if getattr(x, "type", None) == "text")
        try:
            result = json.loads(text)
        except ValueError:
            result = {"message": text}
    result = dict(result)
    return result, bool(response.is_error or result.get("error"))


async def _wait_for_change(session: Any, arguments: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """Repeat only successful empty waits; return real changes/errors unchanged."""
    request = dict(arguments)
    loop = asyncio.get_running_loop()
    while True:
        started = loop.time()
        result, failed = _tool_result(await session.call_tool("paperspine_wait_for_task_change", request))
        if failed:
            return result, 1
        version, changed = result.get("task_version"), result.get("changed")
        if (result.get("task_id") != request["task_id"] or type(version) is not int
                or version < request["after_version"] or type(changed) is not bool
                or (changed and version <= request["after_version"])):
            return {"error": {"code": "invalid_wait_response",
                    "message": "Task-change reply has an invalid or non-advancing cursor; read the same task before resuming."},
                    "response": result}, 1
        if changed:
            return result, 0  # The host, not transport, interprets the saved input.
        request = {**request, "after_version": version}
        # Valid API timeouts already waited. Pace an unexpectedly early empty
        # reply at the requested API interval, rather than spin on one cursor.
        remaining = request["timeout_seconds"] - (loop.time() - started)
        if remaining > 0:
            await asyncio.sleep(remaining)


def _main() -> int:
    if sys.argv[1] == '--web-server':
        return _web_server(json.loads(sys.argv[2]))
    if sys.argv[1] == "--probe":
        _enable_dependencies(Path(sys.argv[2]))
        return 0
    if sys.argv[1] == "--server":
        binding = json.loads(sys.argv[2])
        _enable_dependencies(Path(binding["project_root"]))
        sys.path.insert(0, str(Path(binding["project_root"]) / "03_联合开发/src"))
        sys.argv = ["p2_facades", "mcp-stdio"]
        for field in ("user_data_root", "core_root", "domain_database", "contracts_root", "principal_id"):
            sys.argv.extend(["--" + field.replace("_", "-"), binding[field]])
        if binding.get("reviewer_id"):
            sys.argv.extend(["--reviewer-id", binding["reviewer_id"]])
        runpy.run_module("paperspine_figure_integration.p2_facades", run_name="__main__")
        return 0
    if sys.argv[1] == "--client":
        job = json.load(sys.stdin)
        result, status = asyncio.run(_client(job))
        print(json.dumps(result, ensure_ascii=True))
        return status
    raise ValueError("Use paperspine5_web.py host tools/snapshot/call/wait")


if __name__ == "__main__":
    server_mode = sys.argv[1:2] == ["--server"]
    try:
        raise SystemExit(_main())
    except Exception as exc:
        traceback.print_exception(exc, file=sys.stderr)
        print(json.dumps({"error": {"code": "public_transport_failed", "message": str(exc)},
                          "automatic_retry": False}), file=sys.stderr if server_mode else sys.stdout)
        raise SystemExit(1) from exc
