"""Start the legacy PaperSpine5 loopback UI without a visible console."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

# Legacy recovery remains public compatibility surface.  It must not create
# bytecode in the same content-addressed suite that it is recovering from.
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open the local PaperSpine5 workspace")
    parser.add_argument("job", help="Path to integration_job.json")
    parser.add_argument("--no-open", action="store_true", help="Start without opening the default browser")
    return parser.parse_args()


def project_root() -> Path:
    skill_root = Path(__file__).resolve().parents[1]
    value = os.environ.get("PAPERSPINE5_PROJECT_ROOT")
    installed = skill_root / "references" / "installed-suite.json"
    development = skill_root / "references" / "local-project.json"
    if value:
        root = Path(value).resolve()
    elif installed.is_file():
        payload = json.loads(installed.read_text(encoding="utf-8-sig"))
        if payload.get("contract") != "paperspine5.installed-suite-pointer":
            raise RuntimeError(f"PaperSpine5 installed-suite pointer is invalid: {installed}")
        root = Path(payload["suite_root"]).resolve()
    elif development.is_file():
        root = Path(json.loads(development.read_text(encoding="utf-8-sig"))["project_root"]).resolve()
    else:
        root = next(
            (parent for parent in skill_root.parents if (parent / "suite-manifest.json").is_file()),
            skill_root,
        )
    if not (root / "03_联合开发" / "scripts" / "paperspine_figure.py").is_file():
        raise RuntimeError(
            "The legacy job workspace launcher is unavailable in this exact suite. "
            "Use scripts/paperspine5_bridge.py with the Product Web/HostBridge instead: "
            f"{root}"
        )
    return root


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def server_creationflags(platform_name: str = os.name) -> int:
    """Return a console-free Windows flag without detached/process-group mixing."""
    if platform_name != "nt":
        return 0
    return int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))


def start_server(command: list[str], *, root: Path, log_path: Path) -> subprocess.Popen[bytes]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with log_path.open("ab") as log:
        return subprocess.Popen(
            command,
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            close_fds=True,
            creationflags=server_creationflags(),
            env=environment,
        )


def main() -> int:
    args = parse_args()
    root = project_root()
    candidate = Path(args.job)
    job = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        job.relative_to(root)
    except ValueError as exc:
        raise SystemExit("job must stay inside the PaperSpine5 project root") from exc
    if not job.is_file():
        raise SystemExit(f"integration job does not exist: {job}")

    port = free_port()
    address = f"http://127.0.0.1:{port}/"
    log_dir = job.parent / ".paperspine5"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"ui-{port}.log"
    command = [
        sys.executable,
        "-B",
        str(root / "03_联合开发" / "scripts" / "paperspine_figure.py"),
        "serve",
        str(job),
        "--port",
        str(port),
    ]
    if not args.no_open:
        command.append("--open")
    process = start_server(command, root=root, log_path=log_path)
    for _ in range(60):
        if process.poll() is not None:
            break
        try:
            with urlopen(address + "api/snapshot", timeout=0.5) as response:
                if response.status == 200:
                    print(json.dumps({"status": "READY", "address": address, "pid": process.pid, "job_path": str(job), "log": str(log_path)}, ensure_ascii=False, indent=2))
                    return 0
        except OSError:
            time.sleep(0.1)
    if process.poll() is None:
        process.terminate()
    print(json.dumps({"status": "FAIL", "error": "workspace did not become ready", "log": str(log_path)}, ensure_ascii=False), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
