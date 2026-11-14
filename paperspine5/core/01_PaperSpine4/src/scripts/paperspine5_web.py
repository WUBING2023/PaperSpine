#!/usr/bin/env python3
"""Launch and reuse the shared PaperSpine5 Product Web without a terminal UI.

This is a thin standalone host adapter. Default host tools use the existing
P2 public MCP facade. Task facts remain in its event store; research and file
work remain with the host Agent. Old Runner transport is explicit compatibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse, urlunparse
from urllib.request import Request, urlopen

# A content-addressed installed suite is a release object, not a Python cache
# location.  Set both the current-interpreter flag and the inherited process
# contract before importing any module that can reach the bundled product core.
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
# Windows' bundled Python uses an isolated ._pth and omits the script directory.
# Import only this launcher's shipped sibling transport, not the working folder.
sys.path.insert(0, str(Path(__file__).resolve().parent))


READY_CONTRACT = "paperspine5.web-workspace-receipt"
DEFAULT_OUTPUT_DIR = "paper_rewriting_output"


class WebLaunchError(RuntimeError):
    """A stable, user-facing standalone Web launch failure."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PaperSpine5 standalone Web workspace")
    subparsers = parser.add_subparsers(dest="command", required=True)

    launch = subparsers.add_parser("launch", help="start or reuse the local Web workspace")
    launch.add_argument("--output-dir", "--user-data-root", dest="output_dir")
    launch.add_argument("--project-root")
    launch.add_argument("--profile-root")
    launch.add_argument("--core-root")
    launch.add_argument("--domain-database")
    launch.add_argument("--python-executable")
    launch.add_argument("--port", type=int, default=0)
    launch.add_argument("--remember", action="store_true", help="remember this local profile for later host calls")
    launch.add_argument("--legacy-runner", action="store_true", help="explicit old token-bound Web compatibility")
    browser = launch.add_mutually_exclusive_group()
    browser.add_argument("--no-open", dest="no_open", action="store_true",
                         help="Return the service URL without opening a browser (default).")
    browser.add_argument("--open-browser", dest="no_open", action="store_false",
                         help="Explicitly open the external default browser; do not also open a host panel.")
    launch.set_defaults(no_open=True)
    launch.add_argument("--wait-seconds", type=float, default=20.0)

    status = subparsers.add_parser("status", help="check the persisted Web workspace")
    status.add_argument("--output-dir")
    status.add_argument("--project-root")
    status.add_argument("--profile-root")
    status.add_argument("--legacy-runner", action="store_true")

    stop = subparsers.add_parser("stop", help="stop the owned public Web workspace and keep its tasks")
    stop.add_argument("--profile-root", required=True)
    stop.add_argument("--project-root")

    api = subparsers.add_parser(
        "api",
        help="call the authenticated loopback API for Agent-side automation",
    )
    api.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    api.add_argument("--project-root")
    api.add_argument("--method", choices=("GET", "POST"), default="GET")
    api.add_argument("--path", required=True)
    api.add_argument("--body-file")

    host = subparsers.add_parser(
        "host", help="public MCP tools for the current host; no old MCP connection required",
        description="Use P2 public tools against the same Web profile. The host does the "
                    "research and file work. --legacy-runner is an explicit compatibility option.",
    )
    host_commands = host.add_subparsers(dest="host_command", required=True)
    for name, help_text in (
        ("tools", "list the connected P2 public tool schemas"),
        ("snapshot", "read the current public task and its Skill/Web file locations"),
        ("methods", "read applicable original Skill methods for the same public task (advisory)"),
        ("call", "call a public MCP tool with its actual argument object"),
        ("wait", "stay attached until a real task version changes; interrupt to cancel"),
    ):
        command = host_commands.add_parser(name, help=help_text)
        command.add_argument("--project-root")
        command.add_argument("--profile-root", required=name == "wait",
                             help="existing profile with data/product-config.json")
        command.add_argument("--output-dir", "--user-data-root", dest="output_dir",
                             help="same user-data root as the Web service")
        command.add_argument("--core-root", help="same core identity as the Web service")
        command.add_argument("--domain-database", help="exact existing Web event database")
        command.add_argument("--contracts-root")
        command.add_argument("--principal-id", default="paper-spine-host")
        command.add_argument("--trusted-reviewer-id",
                             help="explicit existing identity of the actual independent reviewer; enables P2 review tool")
        command.add_argument("--python-executable", help="existing Python with MCP2; never installs dependencies")
        command.add_argument("--timeout-seconds", type=float, default=60.0)
        command.add_argument("--legacy-runner", action="store_true",
                             help="explicit old Runner transport; does not migrate a task")
        if name == "tools":
            command.add_argument("--tool", help="one exact public tool schema")
            command.add_argument("--task-id", help="compatibility context only; inventory is process-wide, with no task read or filtering")
        else:
            command.add_argument("--task-id", required=name in ("snapshot", "methods", "wait"))
        if name == "wait":
            command.add_argument("--after-version", type=int, required=True, help="last observed task_version")
            command.add_argument("--wait-seconds", type=float, default=50.0,
                                 help="each public API wait, 1–50 seconds (default 50); normal timeouts continue")
        if name == "snapshot":
            command.add_argument("--summary", action="store_true", help="compact task/configuration and counts; read bridge files for full choices/results")
        if name == "methods":
            command.add_argument("--local", action="store_true",
                                 help="read explicit shipped resources without a task/MCP read; task ID is context only")
            command.add_argument("--format", choices=("json", "text"), default="json",
                                 help="text: one framed, directly readable source page; implies --include-text; default JSON is unchanged")
            command.add_argument("--start-line", type=int, default=1, help="one-based first source line")
            command.add_argument("--max-lines", type=int, help="bounded source page; follow next_start_line until complete")
            command.add_argument("--max-chars", type=int,
                                 help="character ceiling: entire text frame (default 8000), or source text in JSON; whole lines only")
            command.add_argument("--expect-sha256", help="reject continuation if the original content SHA-256 changed")
            command.add_argument("--include-text", action="store_true", help="return full selected original files with compatibility instructions")
            command.add_argument("--stage", choices=("intake", "research", "contribution", "evidence", "draft", "figure", "review", "delivery"),
                                 help="action stage for selection only; does not change the task stage")
            command.add_argument("--focus", action="append", default=[], help="explicit extra operation focus; repeat for multiple focuses")
            command.add_argument("--resource", action="append", default=[],
                                 help="read only this exact registered path; repeat for multiple originals; overrides selection filters, never task state")
        if name == "call":
            command.add_argument("--tool", required=True)
            command.add_argument("--summary", action="store_true",
                                 help="omit the repeated task projection for successful artifact publishes; other results and the default full response are unchanged")
            command.add_argument("--arguments-file", required=True,
                                 help="MCP arguments JSON, including request wrapper when required; - reads stdin")
    args = parser.parse_args()
    if args.command == "host" and args.host_command == "wait":
        if args.legacy_runner:
            parser.error("host wait uses the public task-change tool; --legacy-runner is unsupported")
        if not args.profile_root.strip() or not args.task_id.strip() or args.after_version < 0:
            parser.error("host wait requires an explicit profile, task and nonnegative --after-version")
        if not math.isfinite(args.wait_seconds) or not 1 <= args.wait_seconds <= 50:
            parser.error("--wait-seconds must be between 1 and 50")
        if not math.isfinite(args.timeout_seconds) or args.timeout_seconds <= args.wait_seconds:
            parser.error("--timeout-seconds is the per-request transport limit and must exceed --wait-seconds")
    if args.command == "host" and args.host_command == "methods":
        from paperspine_methods import validate_paging
        args.include_text = args.include_text or args.format == "text"
        if args.local and (not args.resource or args.legacy_runner):
            parser.error("--local requires explicit --resource and does not use --legacy-runner")
        try:
            validate_paging(resources=args.resource, include_text=args.include_text,
                            start_line=args.start_line, max_lines=args.max_lines,
                            max_chars=args.max_chars, expect_sha256=args.expect_sha256, output_format=args.format)
        except ValueError as exc:
            parser.error(str(exc))
    return args


def _skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _installed_suite_root() -> Path | None:
    pointer_path = _skill_root() / "references" / "installed-suite.json"
    if not pointer_path.is_file():
        return None
    try:
        pointer = json.loads(pointer_path.read_text(encoding="utf-8-sig"))
        root = Path(str(pointer["suite_root"])).resolve()
        manifest = json.loads((root / "suite-manifest.json").read_text(encoding="utf-8-sig"))
    except (KeyError, OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise WebLaunchError(f"installed suite identity is unreadable: {pointer_path}") from exc
    if (
        pointer.get("contract") != "paperspine5.installed-suite-pointer"
        or pointer.get("schema_version") != "1.0"
        or pointer.get("product_id") != "paperspine5"
        or manifest.get("contract") != "paperspine5.suite-manifest"
        or manifest.get("schema_version") != "1.0"
        or manifest.get("suite", {}).get("product_id") != "paperspine5"
        or manifest.get("suite", {}).get("build_id") != pointer.get("build_id")
        or manifest.get("content", {}).get("index_sha256")
        != pointer.get("content_index_sha256")
    ):
        raise WebLaunchError("installed suite pointer and manifest identity do not match")
    return root


def locate_product_root(explicit: str | Path | None = None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    if os.environ.get("PAPERSPINE5_PROJECT_ROOT"):
        candidates.append(Path(os.environ["PAPERSPINE5_PROJECT_ROOT"]))
    installed = _installed_suite_root()
    if installed is not None:
        candidates.append(installed)
    candidates.append(_skill_root() / "_paperspine5")
    candidates.extend(Path(__file__).resolve().parents)

    for candidate in candidates:
        root = candidate.expanduser().resolve()
        runtime = root / "06_插件化" / "runtime" / "paperspine5_runtime.py"
        product_core = (
            root
            / "03_联合开发"
            / "src"
            / "paperspine_figure_integration"
            / "product_kernel.py"
        )
        if runtime.is_file() and product_core.is_file():
            return root
    raise WebLaunchError(
        "The standalone PaperSpine5 Web core is missing. Rebuild/install the current "
        "self-contained paper-spine Skill; do not fall back to the terminal intake UI."
    )


def _user_data_root(output_dir: str | Path) -> Path:
    candidate = Path(output_dir).expanduser()
    return (candidate if candidate.is_absolute() else Path.cwd() / candidate).resolve()


def _is_default_output_dir(output_dir: str | Path) -> bool:
    """Return whether the caller kept the launcher's conventional default.

    The default is intentionally recognized by its path shape rather than by
    the current working directory.  This lets the standalone launcher keep a
    stable project-local identity while still accepting ``./paper_rewriting_output``.
    Explicit paths retain their exact meaning and are never silently relocated.
    """

    candidate = Path(output_dir).expanduser()
    return not candidate.is_absolute() and candidate.parts == (DEFAULT_OUTPUT_DIR,)


def _default_user_data_root(product_root: str | Path) -> Path:
    """Return the stable, non-core data root for the conventional launch path.

    Product code is often run with its repository as the current directory.
    Keeping task state under a per-product user-data directory avoids placing
    writable SQLite/task files below the immutable core while preserving the
    same path across repeated launches of the same installed suite.
    """

    root = Path(product_root).expanduser().resolve()
    digest = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:16]
    return (Path.home() / ".paperspine5" / "workspaces" / digest / DEFAULT_OUTPUT_DIR).resolve()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _resolved_user_data_root(
    output_dir: str | Path,
    *,
    product_root: str | Path | None = None,
) -> Path:
    """Resolve a launcher output root without allowing core/data overlap.

    Only the conventional default is redirected.  A caller-provided path that
    overlaps the product core fails clearly instead of changing its meaning.
    """

    candidate = _user_data_root(output_dir)
    if product_root is None:
        return candidate
    core = Path(product_root).expanduser().resolve()
    if not (_is_relative_to(candidate, core) or _is_relative_to(core, candidate)):
        return candidate
    if _is_default_output_dir(output_dir):
        return _default_user_data_root(core)
    raise WebLaunchError(
        "Output root must be separate from the PaperSpine5 product core; "
        "choose a directory outside --project-root"
    )


def state_path(output_dir: str | Path, *, product_root: str | Path | None = None) -> Path:
    return _resolved_user_data_root(output_dir, product_root=product_root) / ".paperspine5-web" / "workspace.json"


def _output_root_facts(user_data_root: Path) -> dict[str, bool]:
    """Describe pre-launch root state without conflating it with server reuse."""

    if not user_data_root.exists():
        return {
            "output_root_preexisting": False,
            "output_root_had_entries": False,
        }
    if not user_data_root.is_dir():
        raise WebLaunchError(f"Output root is not a directory: {user_data_root}")
    return {
        "output_root_preexisting": True,
        "output_root_had_entries": next(user_data_root.iterdir(), None) is not None,
    }


def _read_state(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or payload.get("contract") != READY_CONTRACT:
        return None
    return payload


def _session_context(address: str) -> tuple[str, str]:
    parsed = urlparse(address)
    token = (parse_qs(parsed.fragment).get("session") or [""])[0]
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or not token:
        raise WebLaunchError("Persisted workspace address is not a token-bound loopback URL")
    base = urlunparse((parsed.scheme, parsed.netloc, "/", "", "", ""))
    return base.rstrip("/"), token


def _request_json(
    address: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: float = 1.5,
) -> dict[str, Any]:
    base, token = _session_context(address)
    route = "/api/v1/session" if path == "session" else path
    if not route.startswith("/api/v1/"):
        raise WebLaunchError("Only /api/v1/ loopback routes are allowed")
    headers = {"X-PaperSpine5-Session": token}
    data = None
    if method == "POST":
        session = _request_json(address, "session", timeout=timeout)
        csrf = session.get("csrf_token")
        if not isinstance(csrf, str) or not csrf:
            raise WebLaunchError("Workspace session did not provide a CSRF token")
        headers.update(
            {
                "Content-Type": "application/json",
                "X-PaperSpine5-CSRF": csrf,
                "Origin": base,
            }
        )
        data = (json.dumps(payload or {}, ensure_ascii=False) + "\n").encode("utf-8")
    request = Request(base + route, data=data, headers=headers, method=method)
    with urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not isinstance(result, dict):
        raise WebLaunchError("Workspace API returned a non-object response")
    return result


def workspace_is_ready(state: dict[str, Any] | None) -> bool:
    if not state or not isinstance(state.get("address"), str):
        return False
    try:
        payload = _request_json(state["address"], "session")
    except (OSError, ValueError, WebLaunchError, json.JSONDecodeError):
        return False
    return payload.get("status") == "PASS"


def _python_for_background() -> str:
    executable = Path(sys.executable)
    if os.name == "nt" and executable.name.lower() == "python.exe":
        pythonw = executable.with_name("pythonw.exe")
        if pythonw.is_file():
            return str(pythonw)
    return str(executable)


def _creation_flags(platform_name: str = os.name) -> int:
    if platform_name != "nt":
        return 0
    return int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))


def _start_runtime(
    product_root: Path,
    user_data_root: Path,
    ready_file: Path,
    log_file: Path,
) -> subprocess.Popen[bytes]:
    runtime = product_root / "06_插件化" / "runtime" / "paperspine5_runtime.py"
    command = [
        _python_for_background(),
        "-B",
        str(runtime),
        "web",
        "--project-root",
        str(product_root),
        "--user-data-root",
        str(user_data_root),
        "--ready-file",
        str(ready_file),
    ]
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("ab") as log:
        return subprocess.Popen(
            command,
            cwd=product_root,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            close_fds=True,
            creationflags=_creation_flags(),
            env=environment,
        )


def launch(args: argparse.Namespace) -> int:
    product_root = locate_product_root(args.project_root)
    user_data_root = _resolved_user_data_root(args.output_dir, product_root=product_root)
    root_facts = _output_root_facts(user_data_root)
    ready_file = state_path(args.output_dir, product_root=product_root)
    existing = _read_state(ready_file)
    if workspace_is_ready(existing):
        receipt = {
            **existing,
            "reused": True,
            "server_reused": True,
            **root_facts,
        }
        if not args.no_open:
            webbrowser.open(existing["address"])
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0

    control_root = ready_file.parent
    control_root.mkdir(parents=True, exist_ok=True)
    log_file = control_root / "workspace.log"
    process = _start_runtime(product_root, user_data_root, ready_file, log_file)
    deadline = time.monotonic() + max(args.wait_seconds, 1.0)
    current: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            break
        current = _read_state(ready_file)
        if workspace_is_ready(current):
            receipt = {
                **current,
                "reused": False,
                "server_reused": False,
                **root_facts,
                "log": str(log_file),
            }
            if not args.no_open:
                webbrowser.open(current["address"])
            print(json.dumps(receipt, ensure_ascii=False, indent=2))
            return 0
        time.sleep(0.1)
    raise WebLaunchError(
        f"PaperSpine5 Web did not become ready (exit={process.poll()}); see {log_file}"
    )


def status(args: argparse.Namespace) -> int:
    product_root = locate_product_root(args.project_root)
    path = state_path(args.output_dir, product_root=product_root)
    current = _read_state(path)
    payload = {
        "status": "RUNNING" if workspace_is_ready(current) else "STOPPED",
        "state_file": str(path),
        "workspace": current,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "RUNNING" else 1


def api_call(args: argparse.Namespace) -> int:
    product_root = locate_product_root(args.project_root)
    current = _read_state(state_path(args.output_dir, product_root=product_root))
    if not workspace_is_ready(current):
        raise WebLaunchError("PaperSpine5 Web is not running for this output directory")
    payload = None
    if args.body_file:
        value = json.loads(Path(args.body_file).read_text(encoding="utf-8-sig"))
        if not isinstance(value, dict):
            raise WebLaunchError("API body file must contain a JSON object")
        payload = value
    result = _request_json(current["address"], args.path, method=args.method, payload=payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _host_rpc(product_root: Path, request: dict[str, Any]) -> dict[str, Any]:
    """Use the sole runtime MCP dispatcher, including its lease cleanup at EOF.

    This child is Python transport, not a Codex child or a second stage worker.
    Request data stays on stdin, never command-line arguments or a Web receipt.
    There is deliberately no retry: a lost reply does not prove non-commit.
    """
    runtime = product_root / "06_插件化" / "runtime" / "paperspine5_runtime.py"
    completed = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", str(runtime), "mcp",
         "--project-root", str(product_root)],
        input=json.dumps(request, ensure_ascii=False) + "\n",
        capture_output=True, text=True, encoding="utf-8", errors="strict",
        creationflags=_creation_flags(),
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )
    try:
        response = json.loads(completed.stdout)
    except (ValueError, TypeError) as exc:
        raise WebLaunchError(
            "Host transport returned no valid reply; outcome is unknown. "
            "Read the same task snapshot/command result before deciding what to do; do not blindly retry."
        ) from exc
    if not isinstance(response, dict) or response.get("id") != request["id"]:
        raise WebLaunchError("Host transport response identity mismatch; do not blindly retry")
    if completed.returncode or "error" in response:
        raise WebLaunchError("Host runtime rejected the RPC; no automatic retry was attempted")
    return response["result"]


def _legacy_host_call(args: argparse.Namespace) -> int:
    product_root = locate_product_root(args.project_root)
    request: dict[str, Any] = {"jsonrpc": "2.0", "id": "current-host"}
    if args.host_command == "tools":
        request["method"] = "tools/list"
        result = _host_rpc(product_root, request)
        if args.tool:
            matches = [tool for tool in result["tools"] if tool["name"] == args.tool]
            if len(matches) != 1:
                raise WebLaunchError("The requested tool is not present in this runtime")
            result = matches[0]
        # ASCII JSON framing survives Windows PowerShell's capture code page;
        # decoding restores every Unicode path/schema character unchanged.
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0

    user_data_root = _resolved_user_data_root(args.output_dir, product_root=product_root)
    if not user_data_root.is_dir():
        raise WebLaunchError("host requires the existing task's output/user-data directory")
    tool_name = "paperspine5_runner_snapshot"
    arguments: dict[str, Any] = {}
    if args.host_command == "call":
        tool_name = args.tool
        # Only same-task Runner tools are meaningful in this one-shot adapter.
        # Tool existence, argument schema and all business decisions stay runtime-owned.
        if not tool_name.startswith("paperspine5_runner_"):
            raise WebLaunchError("host call accepts existing same-task paperspine5_runner_* tools only")
        raw = (sys.stdin.read() if args.arguments_file == "-"
               else Path(args.arguments_file).read_text(encoding="utf-8-sig"))
        arguments = json.loads(raw)
        if not isinstance(arguments, dict):
            raise WebLaunchError("Host arguments must be a JSON object")
    if "task_id" in arguments and arguments["task_id"] != args.task_id:
        raise WebLaunchError("Host argument task_id does not match the explicit current task")
    if "user_data_root" in arguments:
        supplied_root = arguments["user_data_root"]
        if (
            not isinstance(supplied_root, str)
            or _resolved_user_data_root(supplied_root, product_root=product_root) != user_data_root
        ):
            raise WebLaunchError("Host argument user_data_root does not match --output-dir")
    arguments = {**arguments, "task_id": args.task_id, "user_data_root": str(user_data_root)}
    request.update(method="tools/call", params={"name": tool_name, "arguments": arguments})
    result = _host_rpc(product_root, request)
    payload = json.loads(result["content"][0]["text"])
    failed = bool(result.get("isError") or payload.get("status") == "FAIL")
    if args.host_command == "snapshot" and not failed:
        # Runner pointers are run-relative; obtain their existing Kernel anchor
        # rather than guessing directory layouts or manufacturing an input packet.
        request["params"] = {"name": "paperspine5_get_task", "arguments": arguments}
        task_result = _host_rpc(product_root, request)
        task_payload = json.loads(task_result["content"][0]["text"])
        if task_result.get("isError") or task_payload.get("status") != "PASS":
            payload, failed = task_payload, True
        else:
            task = task_payload["task"]
            snapshot = payload["snapshot"]
            runner_state = task.get("state", {}).get("runner") or {}
            if (
                task["task_id"] != args.task_id
                or task["revision"] != snapshot["revision"]
                or any(snapshot.get(field) != runner_state.get(field) for field in (
                    "successor_migration", "material_inventory", "run_contract",
                    "academic_inputs", "academic_artifacts", "academic_base_artifacts",
                ))
            ):
                raise WebLaunchError("Task changed during the read; obtain a fresh host snapshot before answering")
            payload = {**payload, "task": task}
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    return 1 if failed else 0


def host_call(args: argparse.Namespace) -> int:
    if args.timeout_seconds <= 0:
        raise WebLaunchError("--timeout-seconds must be positive")
    if args.legacy_runner:
        if args.host_command == "methods":
            raise WebLaunchError("host methods reads the current public task; --legacy-runner is unsupported")
        if args.host_command != "tools" and (not args.output_dir or not args.task_id):
            raise WebLaunchError("Legacy reads/calls require the existing --output-dir and --task-id")
        return _legacy_host_call(args)
    from paperspine_public_client import call, local_methods
    if args.host_command == "methods" and getattr(args, "local", False):
        return local_methods(args)
    return call(args, locate_product_root(args.project_root))


def main() -> int:
    args = parse_args()
    try:
        if args.command == "launch":
            if args.legacy_runner:
                args.output_dir = args.output_dir or DEFAULT_OUTPUT_DIR
                return launch(args)
            from paperspine_public_client import web_launch
            return web_launch(args, locate_product_root(args.project_root))
        if args.command == "status":
            if args.legacy_runner:
                args.output_dir = args.output_dir or DEFAULT_OUTPUT_DIR
                return status(args)
            from paperspine_public_client import web_status
            return web_status(args, locate_product_root(args.project_root))
        if args.command == "stop":
            from paperspine_public_client import web_stop
            return web_stop(args, locate_product_root(args.project_root))
        if args.command == "host":
            return host_call(args)
        return api_call(args)
    except KeyboardInterrupt:
        if args.command != "host" or args.host_command != "wait":
            raise
        print("PaperSpine host wait cancelled.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "error": str(exc),
                    "frontend": "current-host" if args.command == "host" else "web",
                    "terminal_fallback_used": False,
                },
                ensure_ascii=args.command == "host",
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
