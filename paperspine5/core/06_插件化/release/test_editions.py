"""Regression checks for edition switches, update recovery and owned uninstall."""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from edition_manager import FORMAT, Installation, extract, names
from stable_updater import digest, write


class EditionsTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.installation = Installation(self.root / "host" / "skills")
        self.installation.control.mkdir(parents=True)
        self.addCleanup(self.installation.recover)

    def release(self, mode, sequence, *, channel=False):
        files = {f"skills/{name}/SKILL.md": f"---\nname: {name}\n---\nRelease {sequence}\n"
                 for name in names(mode)}
        meta = {"format": FORMAT, "edition": mode, "version": f"1.0.{sequence}", "sequence": sequence,
                "skills": list(names(mode)),
                "files": {name: hashlib.sha256(content.encode()).hexdigest() for name, content in files.items()}}
        import json
        archive = self.root / f"{mode}-{sequence}.zip"
        with ZipFile(archive, "w") as output:
            output.writestr("edition.json", json.dumps(meta))
            for name, content in files.items():
                output.writestr(name, content)
        if channel:
            write(self.root / "channel.json", {"format": FORMAT, "editions": {mode: {
                "edition": mode, "sequence": sequence, "version": meta["version"], "file": archive.name,
                "bytes": archive.stat().st_size, "sha256": digest(archive),
            }}})
        return archive

    def install(self, archive, **kwargs):
        try:
            return self.installation.install(archive, digest(archive), **kwargs)
        finally:
            self.installation.recover()

    def test_pack_replaces_single_and_restores_original(self):
        manager = self.installation
        original = manager.skills_root / "paper-spine"
        original.mkdir(parents=True)
        (original / "SKILL.md").write_text("---\nname: paper-spine\n---\nOriginal", encoding="utf-8")
        unrelated = manager.skills_root / "other"
        unrelated.mkdir()
        self.install(self.release("skill", 1), archive_existing=True)
        self.install(self.release("skills-pack", 1))
        self.assertEqual(set(path.name for path in manager.skills_root.iterdir()), {"other", *names("skills-pack")})
        manager.profile().mkdir()
        (manager.profile() / "manuscript.txt").write_text("User paper", encoding="utf-8")
        manager.txn.mkdir()
        manager.activate(None, None, restore_legacy=True, keep_previous=False)
        self.assertIn("Original", (original / "SKILL.md").read_text(encoding="utf-8"))
        self.assertTrue(unrelated.is_dir())
        self.assertEqual((manager.profile() / "manuscript.txt").read_text(encoding="utf-8"), "User paper")
        self.assertEqual(len(list(manager.skills_root.iterdir())), 2)
        self.assertFalse(manager.live.exists() or manager.previous.exists())

    def test_check_and_auto_update_switch_all_skills(self):
        manager = self.installation
        self.install(self.release("skills-pack", 1))
        self.release("skills-pack", 2, channel=True)
        channel = str(self.root / "channel.json")
        self.assertEqual(manager.update(channel, "check")["status"], "update_available")
        self.assertEqual(manager.active()["sequence"], 1)
        self.assertEqual(manager.update(channel, "preflight")["status"], "updated")
        for name in names("skills-pack"):
            self.assertIn("Release 2", (manager.skills_root / name / "SKILL.md").read_text(encoding="utf-8"))
        self.assertEqual(manager.update(channel, "preflight")["status"], "recently_checked")
        self.assertEqual(manager.previous.joinpath("skills/paper-spine/SKILL.md").read_text(encoding="utf-8").splitlines()[-1],
                         "Release 1")

    def test_auto_update_retains_offline_install(self):
        self.install(self.release("skill", 1))
        self.assertEqual(self.installation.update(str(self.root / "offline.json"), "preflight")["status"], "offline")
        self.assertEqual(self.installation.active()["version"], "1.0.1")

    def test_modified_skill_prevents_overwrite(self):
        self.install(self.release("skill", 1))
        entry = self.installation.skills_root / "paper-spine" / "SKILL.md"
        entry.write_text("Custom changes", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "local edits"):
            self.install(self.release("skill", 2))
        self.assertEqual(entry.read_text(encoding="utf-8"), "Custom changes")
        self.assertEqual(self.installation.active()["sequence"], 1)

    def test_rename_failure_keeps_installed_version(self):
        manager = self.installation
        self.install(self.release("skills-pack", 1))
        second = self.release("skills-pack", 2)
        real_rename = Path.rename

        def fail_one(source, target):
            if source.parent == manager.txn / "discovery" and source.name == "paper-spine-study":
                raise OSError("injected activation failure")
            return real_rename(source, target)

        with patch.object(Path, "rename", fail_one), self.assertRaisesRegex(OSError, "injected"):
            self.install(second)
        self.assertFalse(manager.txn.exists())
        self.assertEqual(manager.active()["sequence"], 1)
        for name in names("skills-pack"):
            self.assertIn("Release 1", (manager.skills_root / name / "SKILL.md").read_text(encoding="utf-8"))

    def test_archive_paths_cannot_escape_install(self):
        archive = self.root / "bad.zip"
        with ZipFile(archive, "w") as output:
            output.writestr("../outside.txt", "bad")
        with self.assertRaisesRegex(ValueError, "archive path"):
            extract(archive, self.root / "stage")
        self.assertFalse((self.root / "outside.txt").exists())


if __name__ == "__main__":
    unittest.main()
