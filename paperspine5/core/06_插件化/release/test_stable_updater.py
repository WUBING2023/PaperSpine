from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

import stable_updater as updater


class StableUpdaterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="paperspine-stable-updater-")
        self.root = Path(self.tmp.name)
        self.skill = self.root / "codex" / "skills" / "paper-spine"
        self.control = self.root / "control"
        self.data = self.root / "paper-data"
        self.data.mkdir()
        (self.data / "task.json").write_bytes(b"user task bytes")
        self.source = self.root / "candidate.zip"
        self.new_bootstrap = b"# verified candidate bootstrap, intentionally distinct from the caller\n"
        with zipfile.ZipFile(self.source, "w") as bundle:
            bundle.writestr("updater-protocol.json", json.dumps({
                "protocol": updater.PROTOCOL, "product": "paperspine",
                "adapter": "release/stable_update_adapter.py", "python_min": [3, 12]}))
            bundle.writestr("standalone/paper-spine/SKILL.md",
                            "---\nname: paper-spine\ndescription: V5\n---\n")
            bundle.writestr("release/stable_updater.py", self.new_bootstrap)
        self.sha = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def tearDown(self):
        self.tmp.cleanup()

    def test_detects_legacy_without_executing_it(self):
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text(
            "---\nname: paper-spine\ndescription: legacy\n---\n", encoding="utf-8")
        (self.skill / "old-task.json").write_bytes(b"old user state")
        result = updater.detect(self.skill)
        self.assertEqual(result["kind"], "legacy-standalone")

    def test_successful_update_preserves_data_and_receipt(self):
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text(
            "---\nname: paper-spine\ndescription: V3\n---\n", encoding="utf-8")
        (self.skill / "old-task.json").write_bytes(b"old user state")

        def fake_adapter(suite, prepared, action, tx):
            if action == "prepare":
                prepared.mkdir()
                (prepared / "SKILL.md").write_text(
                    "---\nname: paper-spine\ndescription: V5\n---\n", encoding="utf-8")
            return {"protocol": updater.PROTOCOL, "status": "PASS",
                    "build_id": "test", "product_version": "5", "task_schema_migrated": False}

        with mock.patch.object(updater, "adapter_call", side_effect=fake_adapter):
            result = updater.apply(self.source, sha256=self.sha, skill_root=self.skill,
                                   control_root=self.control, data_roots=[self.data], confirmed=True)
        self.assertEqual(result["status"], "committed")
        self.assertEqual((self.skill / "SKILL.md").read_text(encoding="utf-8").count("V5"), 1)
        self.assertEqual((self.data / "task.json").read_bytes(), b"user task bytes")
        receipt = self.control / "transactions" / result["operation_id"] / "receipt.json"
        saved = json.loads(receipt.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "committed")
        self.assertTrue(Path(saved["legacy_files"]).is_dir())
        self.assertFalse((self.skill / "old-task.json").exists())
        self.assertEqual((self.control / "paperspine_update.py").read_bytes(), self.new_bootstrap)

    def test_failure_after_switch_restores_old_install(self):
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text(
            "---\nname: paper-spine\ndescription: V3\n---\n", encoding="utf-8")

        def fake_adapter(suite, prepared, action, tx):
            if action == "prepare":
                prepared.mkdir()
                (prepared / "SKILL.md").write_text("old", encoding="utf-8")
            return {"protocol": updater.PROTOCOL, "status": "PASS", "build_id": "test",
                    "product_version": "5", "task_schema_migrated": False}

        with mock.patch.object(updater, "adapter_call", side_effect=fake_adapter):
            with self.assertRaises(RuntimeError):
                updater.apply(self.source, sha256=self.sha, skill_root=self.skill,
                              control_root=self.control, confirmed=True, fault_at="after_switch")
        self.assertIn("V3", (self.skill / "SKILL.md").read_text(encoding="utf-8"))

    def test_direct_archive_requires_hash(self):
        with self.assertRaises(ValueError):
            updater.candidate(self.source, None, self.root / "scratch")

    def test_failed_fresh_install_leaves_no_partial_skill(self):
        fresh = self.root / "fresh" / "paper-spine"

        def fake_adapter(suite, prepared, action, tx):
            if action == "prepare":
                prepared.mkdir()
                (prepared / "SKILL.md").write_text("candidate", encoding="utf-8")
            return {"protocol": updater.PROTOCOL, "status": "PASS", "build_id": "test",
                    "product_version": "5", "task_schema_migrated": False}

        with mock.patch.object(updater, "adapter_call", side_effect=fake_adapter):
            with self.assertRaises(RuntimeError):
                updater.apply(self.source, sha256=self.sha, skill_root=fresh,
                              control_root=self.control, confirmed=True, fault_at="after_switch")
        self.assertFalse(fresh.exists())

    def channel(self, *, multi=True):
        bundle = {"url": self.source.name, "sha256": self.sha,
                  "build_id": "test", "product_version": "5"}
        value = {"protocol": updater.PROTOCOL, "product": "paperspine"}
        value.update({"bundles": {key: bundle for key in (
            "windows-amd64", "linux-x86_64", "macos-arm64", "macos-x86_64")}}
                     if multi else {"bundle": bundle})
        path = self.root / "channel.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def fake_adapter(self, suite, prepared, action, tx):
        if action == "prepare":
            shutil.copytree(suite / "standalone" / "paper-spine", prepared)
            updater.write(prepared / "references" / "installed-suite.json", {
                "contract": "paperspine5.installed-suite-pointer", "build_id": "test",
                "product_version": "5", "archive_sha256": self.sha,
                "suite_root": str(suite), "platform": updater.current_platform(),
                "updater_entry": "release/stable_updater.py",
            })
        return {"protocol": updater.PROTOCOL, "status": "PASS", "build_id": "test",
                "product_version": "5", "platform": updater.current_platform()}

    def apply_fixture(self, source=None, **kwargs):
        source = source or self.source
        with mock.patch.object(updater, "adapter_call", side_effect=self.fake_adapter):
            return updater.apply(source, sha256=self.sha if source == self.source else None,
                                 skill_root=self.skill, control_root=self.control,
                                 data_roots=[self.data], confirmed=True, **kwargs)

    def test_selects_native_platform_and_rejects_unsupported(self):
        channel = updater.read(self.channel())
        for system, machine, selected in (
            ("Windows", "AMD64", "windows-amd64"), ("Linux", "x86_64", "linux-x86_64"),
            ("Darwin", "arm64", "macos-arm64"), ("Darwin", "x86_64", "macos-x86_64"),
        ):
            with self.subTest(selected=selected), mock.patch.object(updater.platform, "system", return_value=system), mock.patch.object(updater.platform, "machine", return_value=machine):
                self.assertEqual(updater.select_bundle(channel)["platform"], selected)
        with mock.patch.object(updater.platform, "system", return_value="Linux"), mock.patch.object(updater.platform, "machine", return_value="aarch64"):
            with self.assertRaisesRegex(ValueError, "unsupported update platform"):
                updater.select_bundle(channel)

    def test_legacy_channel_does_not_default_nonwindows_to_windows(self):
        channel = updater.read(self.channel(multi=False))
        with mock.patch.object(updater, "current_platform", return_value="windows-amd64"):
            self.assertEqual(updater.select_bundle(channel)["sha256"], self.sha)
        with mock.patch.object(updater, "current_platform", return_value="macos-arm64"):
            with self.assertRaisesRegex(ValueError, "does not provide"):
                updater.select_bundle(channel)

    def test_missing_or_conflicting_platform_bundle_is_rejected(self):
        channel = updater.read(self.channel())
        channel["bundles"] = {"windows-amd64": channel["bundles"]["windows-amd64"]}
        with mock.patch.object(updater, "current_platform", return_value="linux-x86_64"):
            with self.assertRaisesRegex(ValueError, "exactly one bundle"):
                updater.select_bundle(channel)
        with mock.patch.object(updater, "current_platform", return_value="windows-amd64"):
            channel["bundles"]["windows-amd64"]["platform"] = "linux-x86_64"
            with self.assertRaisesRegex(ValueError, "platform differs"):
                updater.select_bundle(channel)

    def test_current_version_checks_metadata_without_downloading_archive(self):
        channel = self.channel()
        self.apply_fixture(channel)
        fetch = updater.fetch
        fetched = []
        def metadata_only(source, target, limit=updater.LIMIT):
            fetched.append(str(source))
            self.assertEqual(Path(source), channel)
            return fetch(source, target, limit)
        with mock.patch.object(updater, "fetch", side_effect=metadata_only):
            result = updater.auto(channel, skill_root=self.skill, control_root=self.control, confirmed=True)
        self.assertEqual(result["status"], "up_to_date")
        self.assertFalse(result["bootstrap_updated"])
        self.assertEqual(fetched, [str(channel)])

    def test_check_does_not_install_and_auto_requires_authorization(self):
        channel = self.channel()
        with mock.patch.object(updater, "apply") as apply:
            result = updater.auto(channel, skill_root=self.skill, control_root=self.control)
        self.assertEqual(result["status"], "update_available")
        apply.assert_not_called()
        self.assertFalse(self.skill.exists())
        self.assertFalse(self.control.exists())

    def test_auto_installs_new_release_once_and_retains_data(self):
        channel = self.channel()
        with mock.patch.object(updater, "adapter_call", side_effect=self.fake_adapter):
            result = updater.auto(channel, skill_root=self.skill, control_root=self.control,
                                  data_roots=[self.data], confirmed=True)
        self.assertEqual(result["status"], "committed")
        self.assertEqual(updater.check(channel, skill_root=self.skill, control_root=self.control)["status"], "up_to_date")
        self.assertEqual((self.data / "task.json").read_bytes(), b"user task bytes")

    def test_same_version_different_archive_is_an_update(self):
        channel = self.channel()
        self.apply_fixture(channel)
        metadata = updater.read(channel)
        for bundle in metadata["bundles"].values():
            bundle["sha256"] = "1" * 64
        updater.write(channel, metadata)
        result = updater.check(channel, skill_root=self.skill, control_root=self.control)
        self.assertEqual(result["status"], "update_available")

    def test_channel_race_and_bundle_identity_mismatch_do_not_switch(self):
        with self.assertRaisesRegex(ValueError, "channel changed"):
            self.apply_fixture(expected_identity="1" * 64)
        self.assertFalse(self.skill.exists())
        channel = self.channel()
        metadata = updater.read(channel)
        for bundle in metadata["bundles"].values():
            bundle["build_id"] = "different"
        updater.write(channel, metadata)
        with self.assertRaisesRegex(ValueError, "build_id differs"):
            self.apply_fixture(channel)
        self.assertFalse(self.skill.exists())

    def test_bootstrap_failure_restores_product_and_control_files(self):
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("---\nname: paper-spine\n---\nold", encoding="utf-8")
        self.control.mkdir()
        (self.control / "paperspine_update.py").write_bytes(b"previous updater")
        updater.write(self.control / "settings.json", {"channel": "previous-channel", "data_roots": [str(self.data)]})
        old_controls = updater._control_inventory(self.control)
        before = updater.inventory(self.skill)
        with self.assertRaisesRegex(RuntimeError, "after bootstrap"):
            self.apply_fixture(fault_at="after_bootstrap")
        self.assertEqual(updater.inventory(self.skill), before)
        self.assertEqual(updater._control_inventory(self.control), old_controls)
        self.assertEqual(updater.read(self.control / "transaction.json")["status"], "rolled_back")

    def test_explicit_rollback_restores_bootstrap_and_settings(self):
        self.control.mkdir()
        (self.control / "paperspine_update.py").write_bytes(b"previous updater")
        updater.write(self.control / "settings.json", {"channel": "previous-channel"})
        before = updater._control_inventory(self.control)
        self.apply_fixture(self.channel())
        result = updater._recover(self.control, explicit=True)
        self.assertEqual(result["status"], "rolled_back")
        self.assertFalse(self.skill.exists())
        self.assertEqual(updater._control_inventory(self.control), before)

    def legacy_handoff(self):
        channel = self.channel()
        result = self.apply_fixture(channel)
        result.pop("control_before")
        result.pop("control_after")
        updater.write(self.control / "transaction.json", result)
        (self.control / "paperspine_update.py").write_bytes(b"old bootstrap copied by old updater")
        return channel, result

    def test_current_suite_repairs_bootstrap_left_by_legacy_updater(self):
        channel, _ = self.legacy_handoff()
        result = updater.auto(channel, skill_root=self.skill, control_root=self.control, confirmed=True)
        self.assertEqual(result["status"], "up_to_date")
        self.assertTrue(result["bootstrap_updated"])
        self.assertEqual((self.control / "paperspine_update.py").read_bytes(), self.new_bootstrap)
        updater._recover(self.control, explicit=True)
        self.assertEqual((self.control / "paperspine_update.py").read_bytes(), b"old bootstrap copied by old updater")

    def test_legacy_bootstrap_repair_rejects_tampered_source(self):
        channel, journal = self.legacy_handoff()
        source = Path(journal["transaction_root"]) / "suite" / "release" / "stable_updater.py"
        source.write_bytes(b"tampered updater")
        with self.assertRaisesRegex(ValueError, "differs from its verified archive"):
            updater.auto(channel, skill_root=self.skill, control_root=self.control, confirmed=True)
        self.assertEqual((self.control / "paperspine_update.py").read_bytes(), b"old bootstrap copied by old updater")

    def test_legacy_bootstrap_repair_rejects_tampered_archive(self):
        channel, journal = self.legacy_handoff()
        (Path(journal["transaction_root"]) / "bundle.zip").write_bytes(b"tampered archive")
        with self.assertRaisesRegex(ValueError, "archive differs"):
            updater.auto(channel, skill_root=self.skill, control_root=self.control, confirmed=True)

    def test_pending_transaction_requires_recovery_in_read_only_check(self):
        channel = self.channel()
        self.control.mkdir()
        updater.write(self.control / "transaction.json", {"status": "switching"})
        result = updater.check(channel, skill_root=self.skill, control_root=self.control)
        self.assertEqual(result["status"], "recovery_required")


    def test_direct_archive_for_another_platform_does_not_switch(self):
        def wrong_platform(suite, prepared, action, tx):
            result = self.fake_adapter(suite, prepared, action, tx)
            result["platform"] = "linux-x86_64"
            return result
        with mock.patch.object(updater, "current_platform", return_value="windows-amd64"), mock.patch.object(updater, "adapter_call", side_effect=wrong_platform):
            with self.assertRaisesRegex(ValueError, "differs from this computer"):
                updater.apply(self.source, sha256=self.sha, skill_root=self.skill,
                              control_root=self.control, confirmed=True)
        self.assertFalse(self.skill.exists())

    def test_adapter_records_current_release_and_next_updater_entry(self):
        import stable_update_adapter as adapter
        suite = self.root / "adapter-suite"
        skill = suite / "standalone" / "paper-spine"
        (skill / "references").mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: paper-spine\n---", encoding="utf-8")
        prepared = self.root / "adapter-prepared"
        verified = {"build_id": "next", "product_version": "5.1", "archive_sha256": self.sha,
                    "content_index_sha256": "0" * 64, "platform": "windows-amd64",
                    "manifest": {"runtime": {"executable_paths": []}}}
        with mock.patch.object(adapter, "verify_bundle", return_value=verified), mock.patch.object(adapter, "current_platform", return_value="windows-amd64"), mock.patch.object(adapter.subprocess, "run", return_value=mock.Mock(returncode=0, stdout="launch host")):
            result = adapter.handle({"protocol": updater.PROTOCOL, "bundle_root": str(suite),
                                     "bundle_archive": str(self.source), "prepared_root": str(prepared),
                                     "action": "prepare"})
        pointer = updater.read(prepared / "references" / "installed-suite.json")
        self.assertEqual(pointer["archive_sha256"], self.sha)
        self.assertEqual(pointer["product_version"], "5.1")
        self.assertEqual(pointer["updater_entry"], "release/stable_updater.py")
        self.assertEqual(result["platform"], "windows-amd64")


    def test_adapter_rejects_wrong_platform_even_for_an_old_bootstrap(self):
        import stable_update_adapter as adapter
        prepared = self.root / "must-not-prepare"
        with mock.patch.object(adapter, "verify_bundle", return_value={"platform": "windows-amd64"}), mock.patch.object(adapter, "current_platform", return_value="linux-x86_64"):
            with self.assertRaisesRegex(ValueError, "does not support"):
                adapter.handle({"protocol": updater.PROTOCOL, "bundle_root": str(self.root),
                                "bundle_archive": str(self.source), "prepared_root": str(prepared),
                                "action": "prepare"})
        self.assertFalse(prepared.exists())


    def test_auto_rejects_control_inside_skill_before_writing(self):
        nested = self.skill / "control"
        with self.assertRaisesRegex(ValueError, "outside Skill discovery"):
            updater.auto(self.channel(), skill_root=self.skill, control_root=nested, confirmed=True)
        self.assertFalse(nested.exists())


    def test_adapter_restores_legacy_posix_executable_modes_without_content_changes(self):
        import stable_update_adapter as adapter
        suite = self.root / "posix-suite"
        executable = suite / "runtime/bin/python3"
        executable.parent.mkdir(parents=True)
        executable.write_bytes(b"runtime bytes")
        verified = {"manifest": {"runtime": {"executable_paths": ["runtime/bin/python3"]}}}
        with mock.patch.object(Path, "stat", return_value=mock.Mock(st_mode=0o100644)), mock.patch.object(Path, "chmod") as chmod:
            adapter.restore_executables(suite, verified, posix=True)
        chmod.assert_called_once_with(0o755)
        self.assertEqual(executable.read_bytes(), b"runtime bytes")

    def test_adapter_rejects_executable_escape_and_links_before_chmod(self):
        import stable_update_adapter as adapter
        suite = self.root / "posix-suite"
        suite.mkdir()
        for relative in ("../outside", "/outside", "runtime/../outside", "runtime\\python3"):
            verified = {"manifest": {"runtime": {"executable_paths": [relative]}}}
            with self.subTest(relative=relative), mock.patch.object(Path, "chmod") as chmod:
                with self.assertRaisesRegex(ValueError, "inside the verified suite"):
                    adapter.restore_executables(suite, verified, posix=True)
                chmod.assert_not_called()
        (suite / "python3").write_bytes(b"runtime")
        verified = {"manifest": {"runtime": {"executable_paths": ["python3"]}}}
        with mock.patch.object(Path, "is_symlink", return_value=True), mock.patch.object(Path, "chmod") as chmod:
            with self.assertRaisesRegex(ValueError, "non-linked"):
                adapter.restore_executables(suite, verified, posix=True)
            chmod.assert_not_called()



if __name__ == "__main__":
    unittest.main()
