#!/usr/bin/env python3
"""Install PaperSpine's standalone, modular or workbench edition."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import time
import zipfile
from pathlib import Path, PurePosixPath

from stable_updater import digest, fetch, inventory, lock, plain, read, remove_tree, write

FORMAT = "paperspine-editions/1"
MODES = ("skill", "skills-pack", "web-plugin")
ENTRY = "paper-spine"
STAGES = tuple(f"{ENTRY}-{stage}" for stage in ("study", "followwriting", "figures", "review", "deliver"))
MANAGED = frozenset((ENTRY, *STAGES))
WEB_ENTRY = "paper-spine-web"
MARKETPLACE = "paperspine-editions"
PLUGIN_SKILLS_POINTER = f"marketplace/plugins/{WEB_ENTRY}/skills/{WEB_ENTRY}/skills-root.json"
MAX_SIZE = 250 * 1024 * 1024
CHECK_INTERVAL = 12 * 60 * 60
MANAGER_LAUNCHER = """\
import runpy
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
active = root / "active" / "edition_manager.py"
entry = active if active.is_file() and not (root / "transaction").exists() else root / "edition_manager.py"
sys.dont_write_bytecode = True
sys.path.insert(0, str(entry.parent))
runpy.run_path(str(entry), run_name="__main__")
"""


def names(mode: str) -> tuple[str, ...]:
    if mode not in MODES:
        raise ValueError(f"Unknown edition: {mode}")
    return (ENTRY,) if mode == "skill" else (ENTRY, *STAGES)


def require_web_platform() -> None:
    if sys.platform != "win32" or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise ValueError("This workbench package requires Windows x64. The other editions work without it.")


def extract(archive: Path, destination: Path) -> None:
    """Extract the verified distribution without following links or overwriting files."""
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len(entries) > 15000 or sum(entry.file_size for entry in entries) > MAX_SIZE:
            raise ValueError("Edition archive exceeds installation limits")
        seen: set[str] = set()
        for entry in entries:
            raw = entry.filename
            path = PurePosixPath(raw)
            mode = entry.external_attr >> 16
            if (
                path.is_absolute() or "\\" in raw or path.as_posix() != raw
                or not path.parts or ".." in path.parts
                or any(
                    re.search(r'[:<>|?*"\x00-\x1f]', part) or part.endswith((".", " "))
                    or part.split(".")[0].lower() in {
                        "con", "prn", "aux", "nul",
                        *(f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)),
                    }
                    for part in path.parts
                )
                or entry.is_dir() or stat.S_IFMT(mode) not in (0, stat.S_IFREG)
                or raw.casefold() in seen
            ):
                raise ValueError(f"Unsupported edition archive path: {raw}")
            seen.add(raw.casefold())
            output = destination.joinpath(*path.parts)
            output.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(entry) as source, output.open("xb") as target:
                shutil.copyfileobj(source, target)


def edition(root: Path) -> dict:
    metadata = read(root / "edition.json")
    if metadata.get("format") != FORMAT:
        raise ValueError("Unknown PaperSpine edition format")
    mode = metadata["edition"]
    if metadata["skills"] != list(names(mode)):
        raise ValueError("Edition has an incorrect Skill set")
    if type(metadata["sequence"]) is not int or metadata["sequence"] < 1:
        raise ValueError("Edition has an invalid release sequence")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9.]+)?", metadata["version"]):
        raise ValueError("Edition has an invalid version")
    update_feed = metadata.get("channel_url")
    if update_feed is not None and (not isinstance(update_feed, str) or not update_feed.startswith("https://")):
        raise ValueError("The embedded release channel must use HTTPS")
    return metadata


def verified_payload(root: Path, *, skills_root: Path | None = None) -> dict:
    metadata = edition(root)
    expected = metadata["files"]
    found = inventory(root)
    found.pop("edition.json")
    if skills_root is not None and metadata["edition"] == "web-plugin":
        if read(root / PLUGIN_SKILLS_POINTER) != {"skills_root": str(skills_root)}:
            raise ValueError("Stored plugin-to-Skills binding does not match this installation")
        found.pop(PLUGIN_SKILLS_POINTER)
    if found != expected:
        raise ValueError("Edition files do not match their manifest")
    for item in metadata["skills"]:
        skill = root / "skills" / item / "SKILL.md"
        if not re.search(rf"(?m)^name: {item}$", skill.read_text(encoding="utf-8")):
            raise ValueError(f"Incorrect Skill identity: {item}")
    if metadata["edition"] == "web-plugin":
        require_web_platform()
        if not (root / "runtime/runtime_vendor/windows-py312/python.exe").is_file():
            raise ValueError("Web runtime is missing from the package")
        plugin = read(root / "marketplace/plugins" / WEB_ENTRY / ".codex-plugin/plugin.json")
        if plugin.get("name") != WEB_ENTRY or plugin.get("version") != metadata.get("plugin_version"):
            raise ValueError("Codex Web adapter does not match the edition manifest")
    return metadata


def reference(channel: str, archive: str) -> str:
    if archive.startswith("https://"):
        return archive
    if "://" in channel or "://" in archive or Path(archive).name != archive:
        raise ValueError("A remote channel must use HTTPS archives, a local channel may use sibling ZIPs")
    return str(Path(channel).parent / archive)


def source_path(value: str) -> str:
    if "://" in value and not value.startswith("https://"):
        raise ValueError("Update channels use a local file or HTTPS")
    return value if value.startswith("https://") else str(Path(value).expanduser().absolute())


def codex_skills() -> Path:
    return plain(Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex") / "skills")


class Installation:
    def __init__(self, skills_root: Path):
        self.skills_root = plain(skills_root)
        self.control = plain(self.skills_root.parent / f".paperspine-{self.skills_root.name}")
        self.live = self.control / "active"
        self.previous = self.control / "previous"
        self.txn = self.control / "transaction"
        self.settings = self.control / "settings.json"

    def active(self) -> dict | None:
        plain(self.live)
        return edition(self.live) if self.live.exists() else None

    def settings_data(self) -> dict:
        plain(self.settings)
        return read(self.settings) if self.settings.is_file() else {}

    def profile(self) -> Path:
        return plain(self.settings_data().get("profile_root", self.control / "profile"))

    def result(self, status: str, **extra) -> dict:
        metadata = self.active() or {}
        return {
            "status": status, "edition": metadata.get("edition"), "version": metadata.get("version"),
            "skills_root": str(self.skills_root), "skills": metadata.get("skills", []),
            "manager": str(self.control / "manage.py"),
            "profile_root": str(self.profile()),
            "marketplace": str(self.live / "marketplace") if metadata.get("edition") == "web-plugin" else None,
            **extra,
        }

    def recover(self) -> None:
        if not self.txn.exists():
            return
        plain(self.txn)
        journal = self.txn / "journal.json"
        if journal.is_file() and not (self.txn / "committed").is_file():
            data = read(journal)
            for index in range(data["attempted"] - 1, -1, -1):
                source, destination = data["moves"][index]
                source, destination = plain(source), plain(destination)
                allowed = (self.control, *(self.skills_root / name for name in MANAGED))
                if not all(any(path.is_relative_to(root) for root in allowed) for path in (source, destination)):
                    raise ValueError("PaperSpine transaction path escaped its installation")
                if destination.exists() and not source.exists():
                    destination.rename(source)
                elif destination.exists() or not source.exists():
                    raise ValueError(f"Cannot recover changed installation paths: {source} and {destination}")
                data["attempted"] = index
                write(journal, data)
            if data.get("plugin_attempted"):
                self.sync_plugin(data["old_plugin"])
        remove_tree(self.txn, self.control)

    def transaction(self, moves: list[tuple[Path, Path]], old_plugin: str | None, new_plugin: str | None) -> None:
        journal = self.txn / "journal.json"
        data = {"moves": [[str(source), str(destination)] for source, destination in moves],
                "attempted": 0, "old_plugin": old_plugin}
        try:
            if old_plugin and not new_plugin:
                data["plugin_attempted"] = True
                write(journal, data)
                self.sync_plugin(None)
            for index, (source, destination) in enumerate(moves, start=1):
                plain(source)
                plain(destination)
                if destination.exists():
                    raise ValueError(f"Install destination already exists: {destination}")
                data["attempted"] = index
                write(journal, data)
                source.rename(destination)
            if new_plugin:
                data["plugin_attempted"] = True
                write(journal, data)
                self.sync_plugin(new_plugin)
            (self.txn / "committed").touch()
        finally:
            self.recover()

    def stopped_web(self, *, stop: bool = False) -> None:
        if not self.active() or self.active()["edition"] != "web-plugin":
            return
        status = self.web_status()
        if stop and status not in {"STOPPED", "UNINITIALIZED"}:
            subprocess.run(self.web_command(["stop"]), check=True, stdout=subprocess.DEVNULL, timeout=20)
            status = self.web_status()
        if status not in {"STOPPED", "UNINITIALIZED"}:
            raise ValueError("Save your work and run 'web stop' before replacing or removing the workbench")

    def replace(self, staged: Path, metadata: dict, *, archive_existing: bool = False) -> dict:
        current = self.active()
        if current and metadata["sequence"] < current["sequence"]:
            raise ValueError("Use rollback to return to an earlier installed release")
        if current and metadata["sequence"] == current["sequence"] and metadata["edition"] == current["edition"]:
            if metadata != current:
                raise ValueError("This release sequence already identifies a different installed build")
            if all((self.skills_root / item / "installation.json").is_file() for item in current["skills"]):
                if current.get("plugin_version"):
                    self.sync_plugin(current["plugin_version"])
                return self.result("up_to_date")
        self.stopped_web(stop=True)
        return self.activate(staged, metadata, archive_existing=archive_existing)

    def activate(self, staged: Path | None, metadata: dict | None, *, archive_existing: bool = False,
                 restore_legacy: bool = False, keep_previous: bool = True) -> dict:
        current = self.active()
        old_plugin = current.get("plugin_version") if current else None
        new_plugin = metadata.get("plugin_version") if metadata else None
        if old_plugin or new_plugin:
            self.marketplace_registered()
        if current:
            verified_payload(self.live, skills_root=self.skills_root)
        if self.previous.exists() and staged != self.previous:
            verified_payload(self.previous, skills_root=self.skills_root)
        old_names = set(current["skills"]) if current else set()
        new_names = set(metadata["skills"]) if metadata else set()
        legacy = self.control / "archived-original"
        moves: list[tuple[Path, Path]] = []
        self.skills_root.mkdir(parents=True, exist_ok=True)
        for item in sorted(new_names - old_names):
            destination = plain(self.skills_root / item)
            if not destination.exists():
                continue
            inventory(destination)
            if item != ENTRY or not archive_existing or legacy.exists():
                raise ValueError(f"An unmanaged Skill already uses {destination}; choose another install root")
            if not re.search(r"(?m)^name:\s*['\"]?paper-spine['\"]?\s*$",
                             (destination / "SKILL.md").read_text(encoding="utf-8-sig")):
                raise ValueError("Existing directory has no recognized PaperSpine Skill to archive")
            moves.append((destination, legacy))

        old = self.txn / "outgoing"
        old.mkdir()
        current_files = current["files"] if current else {}
        for item in sorted(old_names):
            installed = plain(self.skills_root / item)
            if not installed.exists():
                continue
            prefix = f"skills/{item}/"
            expected = {key[len(prefix):]: value for key, value in current_files.items() if key.startswith(prefix)}
            actual = inventory(installed)
            identity = actual.pop("installation.json", None)
            if identity is None or read(installed / "installation.json") != self.skill_pointer():
                raise ValueError(f"Unrecognized Skill at {installed}")
            if actual != expected:
                raise ValueError(f"Installed Skill has local edits. Move this copy to a safe folder before continuing: {installed}")
            moves.append((installed, old / item))

        if self.live.exists():
            moves.append((self.live, self.txn / "old-active"))
        if staged is not None and metadata is not None:
            projected = self.txn / "discovery"
            projected.mkdir()
            for item in metadata["skills"]:
                target = projected / item
                shutil.copytree(staged / "skills" / item, target)
                write(target / "installation.json", self.skill_pointer())
                moves.append((target, self.skills_root / item))
            if new_plugin:
                write(staged / PLUGIN_SKILLS_POINTER, {"skills_root": str(self.skills_root)})

        if staged is not None:
            moves.append((staged, self.live))
        if self.previous.exists() and staged != self.previous:
            if not current and not restore_legacy:
                raise ValueError("A previous install still exists. Inspect its status before installing.")
            moves.append((self.previous, self.txn / "discarded-previous"))
        if current and keep_previous:
            moves.append((self.txn / "old-active", self.previous))
        if restore_legacy and legacy.exists():
            if ENTRY not in old_names and (self.skills_root / ENTRY).exists():
                raise ValueError("The original Skill cannot be restored over another installed directory")
            moves.append((legacy, self.skills_root / ENTRY))

        self.transaction(moves, old_plugin, new_plugin)
        return self.result("installed" if staged is not None else "uninstalled",
                           restored_original=restore_legacy and (self.skills_root / ENTRY).is_dir())

    def skill_pointer(self) -> dict:
        return {"manager": str(self.control / "manage.py"), "skills_root": str(self.skills_root)}

    def codex(self, *args: str) -> dict:
        if self.skills_root != codex_skills():
            raise ValueError("The Codex Web plugin requires the active Codex user Skill directory")
        result = subprocess.run(["codex", "plugin", *args, "--json"], cwd=self.control,
                                capture_output=True, timeout=25, check=False)
        if result.returncode:
            message = (result.stdout or result.stderr).decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"Codex plugin {args[0]} failed: {message[:2000]}")
        return json.loads(result.stdout)

    def marketplace_registered(self) -> bool:
        for market in self.codex("marketplace", "list")["marketplaces"]:
            if market["name"] == MARKETPLACE:
                if plain(market["root"]) != self.live / "marketplace":
                    raise ValueError(f"Codex marketplace {MARKETPLACE} belongs to another location")
                return True
        return False

    def sync_plugin(self, version: str | None) -> None:
        registered = self.marketplace_registered()
        selector = f"{WEB_ENTRY}@{MARKETPLACE}"
        if not registered and not version:
            return
        if not registered:
            self.codex("marketplace", "add", str(self.live / "marketplace"))
        plugins = self.codex("list", "--marketplace", MARKETPLACE)["installed"]
        current = next((item for item in plugins if item.get("pluginId") == selector), None)
        if current and current["version"] == version:
            return
        if current:
            self.codex("remove", selector)
        if version:
            self.codex("add", selector)
            matches = self.codex("list", "--marketplace", MARKETPLACE)["installed"]
            if not any(item.get("pluginId") == selector and item.get("version") == version for item in matches):
                raise RuntimeError("Codex did not activate the requested workbench plugin version")
        else:
            remaining = self.codex("list", "--marketplace", MARKETPLACE)["installed"]
            if any(item.get("pluginId") == selector for item in remaining):
                raise RuntimeError("Codex still reports the workbench plugin installed")
            if not remaining:
                self.codex("marketplace", "remove", MARKETPLACE)

    def bootstrap(self) -> None:
        for name in ("stable_updater.py", "edition_manager.py"):
            target = plain(self.control / name)
            source = Path(__file__).with_name(name)
            if not target.exists():
                scratch = self.control / (name + ".new")
                shutil.copyfile(source, scratch)
                scratch.replace(target)
        launcher = plain(self.control / "manage.py")
        if not launcher.exists():
            scratch = self.control / "manage.py.new"
            scratch.write_text(MANAGER_LAUNCHER, encoding="utf-8")
            scratch.replace(launcher)

    def install(self, archive: Path, expected: str, *, archive_existing: bool = False,
                entry: dict | None = None) -> dict:
        if not re.fullmatch(r"[a-f0-9]{64}", expected) or digest(archive) != expected:
            raise ValueError("Edition archive SHA-256 does not match")
        stage = self.txn / "staged"
        stage.mkdir(parents=True)
        extract(archive, stage)
        metadata = verified_payload(stage)
        if entry and any(metadata[key] != entry[key] for key in ("edition", "sequence", "version")):
            raise ValueError("Edition archive identity differs from the update channel")
        self.bootstrap()
        return self.replace(stage, metadata, archive_existing=archive_existing)

    def update(self, channel: str, action: str) -> dict:
        current = self.active()
        if not current:
            raise ValueError("Install an edition first")
        if not channel:
            return self.result("channel_not_set")
        settings = self.settings_data()
        if action == "preflight":
            if not settings.get("auto_update", True):
                return self.result("auto_update_off")
            if time.time() - settings.get("checked_at", 0) < CHECK_INTERVAL:
                return self.result("recently_checked")
        self.txn.mkdir(exist_ok=True)
        channel_file = self.txn / "channel.json"
        try:
            fetch(channel, channel_file, limit=256 * 1024)
        except OSError as exc:
            if action == "preflight":
                return self.result("offline", message=str(exc))
            raise
        index = read(channel_file)
        if index.get("format") != FORMAT:
            raise ValueError("Unknown update channel format")
        mode = current["edition"]
        entry = index["editions"][mode]
        if entry["edition"] != mode or type(entry["sequence"]) is not int or entry["sequence"] < 1:
            raise ValueError("Update channel points to a different or invalid edition")
        if entry["sequence"] <= current["sequence"]:
            if action != "check":
                write(self.settings, {**settings, "checked_at": time.time()})
            return self.result("up_to_date")
        if action == "check":
            return self.result("update_available", available=entry["version"])
        if mode == "web-plugin" and action == "preflight" and self.web_status() not in {"STOPPED", "UNINITIALIZED"}:
            return self.result("update_pending", available=entry["version"],
                               message="Save your work and stop the workbench before updating.")
        archive = self.txn / "release.zip"
        try:
            fetch(reference(channel, entry["file"]), archive, limit=MAX_SIZE)
        except OSError as exc:
            if action == "preflight":
                return self.result("offline", message=str(exc))
            raise
        if archive.stat().st_size != entry["bytes"]:
            raise ValueError("Edition ZIP size differs from the channel")
        result = self.install(archive, entry["sha256"], entry=entry)
        write(self.settings, {**settings, "checked_at": time.time()})
        return {**result, "status": "updated"}

    def web_command(self, args: list[str]) -> list[str]:
        runtime = self.live / "runtime"
        if not (runtime / "suite-manifest.json").is_file():
            raise ValueError("Install the Web Plugin edition first")
        require_web_platform()
        if not args or args[0] not in {"launch", "status", "stop", "host"}:
            raise ValueError("Use 'web launch', 'web status', 'web stop' or 'web host ...'")
        managed = {"--profile-root", "--project-root", "--legacy-runner", "--remember",
                   "--output-dir", "--user-data-root", "--core-root", "--domain-database", "--contracts-root"}
        if any(arg.startswith("--") and any(flag.startswith(arg.split("=")[0]) for flag in managed)
               for arg in args):
            raise ValueError("The managed workbench uses its installed runtime and saved profile")
        return [
            str(runtime / "runtime_vendor/windows-py312/python.exe"), "-B", "-X", "utf8",
            str(runtime / "standalone/paper-spine/scripts/paperspine5_web.py"),
            *args, "--profile-root", str(self.profile()),
        ]

    def web_status(self) -> str:
        profile = self.profile()
        states = profile / ".paperspine5-web"
        if not any((states / name).exists() for name in ("public-workspace.json", "public-starting.json")):
            return "UNINITIALIZED"
        response = subprocess.run(self.web_command(["status"]), capture_output=True, timeout=20, check=False)
        try:
            return json.loads(response.stdout)["status"]
        except (ValueError, KeyError) as exc:
            raise ValueError("Could not confirm the current workbench state") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-root", type=Path, default=codex_skills())
    commands = parser.add_subparsers(dest="command", required=True)
    install = commands.add_parser("install")
    install.add_argument("archive", type=Path)
    install.add_argument("--sha256", required=True)
    install.add_argument("--channel")
    install.add_argument("--profile-root", type=Path)
    install.add_argument("--archive-existing", action="store_true", help="archive an existing canonical PaperSpine Skill")
    install.add_argument("--no-auto-update", action="store_true")
    for name in ("check", "update", "preflight"):
        commands.add_parser(name)
    toggle = commands.add_parser("auto-update")
    toggle.add_argument("state", choices=("on", "off"))
    commands.add_parser("status")
    commands.add_parser("rollback")
    commands.add_parser("uninstall")
    web = commands.add_parser("web")
    web.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    manager = Installation(args.skills_root.expanduser())
    passthrough = None

    with lock(manager.control):
        manager.recover()
        try:
            if args.command == "install":
                settings = manager.settings_data()
                if args.profile_root:
                    profile = plain(args.profile_root.expanduser())
                    protected = (manager.live, manager.previous, manager.txn, manager.skills_root)
                    if any(profile.is_relative_to(path) or path.is_relative_to(profile) for path in protected):
                        raise ValueError("Choose a profile outside the program and Skill directories")
                    if manager.active() and profile != manager.profile():
                        raise ValueError("This installation already has a profile. Use its existing binding.")
                    settings["profile_root"] = str(profile)
                if args.channel:
                    settings["channel"] = source_path(args.channel)
                    settings["checked_at"] = 0
                if args.no_auto_update:
                    settings["auto_update"] = False
                result = manager.install(args.archive, args.sha256, archive_existing=args.archive_existing)
                update_feed = manager.active().get("channel_url")
                if update_feed and not settings.get("channel"):
                    settings["channel"] = update_feed
                write(manager.settings, settings)
                result = manager.result(result["status"])
            elif args.command in ("check", "update", "preflight"):
                result = manager.update(manager.settings_data().get("channel"), args.command)
            elif args.command == "status":
                result = manager.result("installed" if manager.active() else "uninstalled",
                                        auto_update=manager.settings_data().get("auto_update", True),
                                        channel=manager.settings_data().get("channel"))
            elif args.command == "auto-update":
                write(manager.settings, {**manager.settings_data(), "auto_update": args.state == "on", "checked_at": 0})
                result = manager.result(f"auto_update_{args.state}")
            elif args.command == "rollback":
                metadata = verified_payload(manager.previous, skills_root=manager.skills_root)
                manager.stopped_web(stop=True)
                manager.txn.mkdir()
                manager.activate(manager.previous, metadata)
                write(manager.settings, {**manager.settings_data(), "checked_at": time.time()})
                result = manager.result("rolled_back")
            elif args.command == "uninstall":
                manager.stopped_web(stop=True)
                manager.txn.mkdir()
                result = manager.activate(None, None, restore_legacy=True, keep_previous=False)
            elif args.args and args.args[0] in {"launch", "stop"}:
                passthrough = subprocess.call(manager.web_command(args.args))
            else:
                # Read-only status and scientific host calls do not hold the install lock.
                deferred = manager.web_command(args.args)
        finally:
            manager.recover()
    if args.command == "web":
        return subprocess.call(deferred) if passthrough is None else passthrough
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError,
            zipfile.BadZipFile) as error:
        print(f"PaperSpine: {error}", file=sys.stderr)
        sys.exit(1)
