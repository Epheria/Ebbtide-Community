"""Deterministic receipt, source-version and reservation guard tests."""
import copy
import csv
import io
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
import voice_submission_core as core


def csv_text(fields, rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


class VoiceCoreTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = pathlib.Path(temp.name)
        self.source_path = self.root / "voice/scripts/rifleman.csv"
        self.source_path.parent.mkdir(parents=True)
        self.fields = ["file", "situation", "tone", "line", "current_voices"]
        self.rows = [{"file": "Ready", "situation": "Order confirmed", "tone": "Calm",
                      "line": "Ready.", "current_voices": "Rifleman"},
                     {"file": "Hold", "situation": "[Wording not confirmed]", "tone": "Calm",
                      "line": "Hold.", "current_voices": "Rifleman"}]
        self.write_source()
        self.source = core.get_source(self.root, "en", "rifleman")
        self.assignment = {"issue": 12, "kind": "voice-audio", "locale": "en", "table": "rifleman",
                           "casting_slot": "alpha", "recording_version": 1, "contributor": "Actor",
                           "reviewer": "Reviewer", "spreadsheet_id": "s" * 44,
                           "tab": "Voice Outbox", "keys": ["Ready"],
                           "script_hash": core.script_hash(self.source)}
        self.receipt = {"Work order": "12", "Take file": "Ready",
                        "Drive snapshot": "https://drive.google.com/file/d/" + "f" * 32 + "/view",
                        "SHA256": "a" * 64, "Bytes": "1024", "MIME type": "audio/wav",
                        "Revision": "b" * 64, "Submitted": "2026-10-20T01:02:03Z",
                        "Script SHA256": self.assignment["script_hash"]}

    def write_source(self):
        self.source_path.write_text(csv_text(self.fields, self.rows), encoding="utf-8")

    def snapshot(self, rows=None):
        snap = core.parse_snapshot(csv_text(core.OUTBOX_FIELDS, rows or [self.receipt]),
                                   self.assignment, self.source)
        snap["target_hash"] = core.target_hash(self.root, self.assignment)
        snap["digest"] = core.snapshot_hash(snap)
        return snap

    def test_manifest_contains_only_receipts_and_truthful_verification(self):
        path, text = core.build_export(self.root, self.assignment, self.snapshot())
        self.assertEqual("voice/submissions/en/rifleman/alpha/12.json", path)
        manifest = json.loads(text)
        self.assertEqual([self.receipt], manifest["receipts"])
        self.assertIn("did not download", manifest["verification"])
        self.assertNotIn("audio_bytes", manifest)

    def test_source_context_changes_invalidate_assignment(self):
        self.rows[0]["tone"] = "Urgent"
        self.write_source()
        with self.assertRaisesRegex(core.WorkflowError, "script or approved"):
            core.build_export(self.root, self.assignment, self.snapshot())

    def test_held_source_cannot_be_assigned(self):
        self.assignment["keys"] = ["Hold"]
        with self.assertRaisesRegex(core.WorkflowError, "on hold"):
            core.validate_assignment(self.assignment, self.source)

    def test_localized_recording_requires_committed_translation(self):
        with self.assertRaisesRegex(core.WorkflowError, "committed reviewed"):
            core.get_source(self.root, "ja", "rifleman")

    def write_translation(self, status="", english="Ready.", translated="準備完了。"):
        path = self.root / "voice/translations/ja/rifleman.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(csv_text(["key", "en", "translation", "status"], [
            {"key": "Ready", "en": english, "translation": translated, "status": status}]), encoding="utf-8")

    def test_only_approved_current_localized_lines_are_recordable(self):
        for status, english, translated in [("review", "Ready.", "準備"),
                                             ("outdated", "Ready.", "準備"),
                                             ("", "Old.", "準備"), ("", "Ready.", "")]:
            with self.subTest(status=status, english=english, translated=translated):
                self.write_translation(status, english, translated)
                source = core.get_source(self.root, "ja", "rifleman")
                self.assignment.update(locale="ja", script_hash=core.script_hash(source))
                with self.assertRaisesRegex(core.WorkflowError, "approved spoken"):
                    core.validate_assignment(self.assignment, source)
        self.write_translation()
        source = core.get_source(self.root, "ja", "rifleman")
        self.assertTrue(source[0]["ready"])
        self.assertEqual("準備完了。", source[0]["spoken"])

    def test_unsafe_scope_and_self_review_rejected(self):
        for field, value in [("casting_slot", "../alpha"), ("table", "x/y"),
                             ("locale", "../../ja"), ("reviewer", "actor"),
                             ("recording_version", True), ("keys", ["Ready", "Ready"])]:
            with self.subTest(field=field):
                assignment = copy.deepcopy(self.assignment)
                assignment[field] = value
                with self.assertRaises(core.WorkflowError):
                    core.validate_assignment(assignment, self.source)

    def test_active_overlap_and_issue_reuse_rejected(self):
        state = core.reserve({"schema": 1, "assignments": []}, self.assignment, self.source)
        candidate = {**self.assignment, "issue": 13, "recording_version": 2}
        with self.assertRaisesRegex(core.WorkflowError, "overlaps active"):
            core.reserve(state, candidate, self.source)
        with self.assertRaisesRegex(core.WorkflowError, "already reserved"):
            core.reserve(state, self.assignment, self.source)
        candidate["casting_slot"] = "bravo"
        self.assertEqual(2, len(core.reserve(state, candidate, self.source)["assignments"]))

    def test_completed_take_requires_deliberate_higher_version(self):
        state = {"assignments": [{**self.assignment, "status": "completed"}]}
        candidate = {**self.assignment, "issue": 13}
        with self.assertRaisesRegex(core.WorkflowError, "higher recording version"):
            core.reserve(state, candidate, self.source)
        candidate["recording_version"] = 2
        self.assertEqual(2, len(core.reserve(state, candidate, self.source)["assignments"]))

    def test_invalid_receipt_metadata_rejected(self):
        invalid = [("Drive snapshot", "https://example.com/audio.wav"),
                   ("SHA256", "A" * 64), ("Bytes", "0"), ("Bytes", "999999999"),
                   ("MIME type", "text/html"), ("Revision", "1"),
                   ("Submitted", "TRUE"), ("Submitted", "2026-02-30T01:02:03Z"),
                   ("Script SHA256", "c" * 64), ("Take file", "Unknown")]
        for field, value in invalid:
            with self.subTest(field=field, value=value):
                with self.assertRaises(core.WorkflowError):
                    self.snapshot([{**self.receipt, field: value}])

    def test_duplicate_or_missing_receipts_rejected(self):
        with self.assertRaisesRegex(core.WorkflowError, "duplicate"):
            self.snapshot([self.receipt, self.receipt])
        with self.assertRaisesRegex(core.WorkflowError, "every assigned"):
            self.snapshot([{**self.receipt, "Work order": "99"}])

    def test_appended_complete_revision_supersedes_historical_receipts(self):
        old = self.snapshot()
        new = {**self.receipt, "Revision": "c" * 64, "SHA256": "d" * 64,
               "Submitted": "2026-10-21T01:02:03Z"}
        snap = self.snapshot([self.receipt, new])
        self.assertEqual([new], snap["rows"])
        self.assertNotEqual(old["digest"], snap["digest"])

    def test_incomplete_latest_revision_never_falls_back_to_old_batch(self):
        self.assignment["keys"] = ["Ready", "Hold"]
        self.source[1]["ready"] = True
        self.assignment["script_hash"] = core.script_hash(self.source)
        self.receipt["Script SHA256"] = self.assignment["script_hash"]
        hold = {**self.receipt, "Take file": "Hold"}
        partial = {**self.receipt, "Revision": "c" * 64}
        with self.assertRaisesRegex(core.WorkflowError, "every assigned"):
            self.snapshot([self.receipt, hold, partial])

    def test_changed_receipt_invalidates_review_digest(self):
        snap = self.snapshot()
        snap["rows"][0]["Bytes"] = "2048"
        with self.assertRaisesRegex(core.WorkflowError, "digest is invalid"):
            core.build_export(self.root, self.assignment, snap)

    def test_spoken_text_in_preview_is_frozen_and_cannot_be_forged(self):
        snap = self.snapshot()
        self.assertEqual("Ready.", snap["script"][0]["spoken"])
        self.assertEqual("Calm", snap["script"][0]["tone"])
        snap["script"][0]["spoken"] = "Different words."
        snap["digest"] = core.snapshot_hash(snap)
        with self.assertRaisesRegex(core.WorkflowError, "spoken text or context differs"):
            core.build_export(self.root, self.assignment, snap)

    def test_snapshot_bound_to_casting_slot_and_contributor(self):
        snap = self.snapshot()
        for field, value in [("casting_slot", "bravo"), ("contributor", "Another")]:
            with self.subTest(field=field):
                with self.assertRaisesRegex(core.WorkflowError, "different voice assignment"):
                    core.build_export(self.root, {**self.assignment, field: value}, snap)

    def test_existing_manifest_cannot_be_overwritten(self):
        snap = self.snapshot()
        path = self.root / core.manifest_path(self.assignment)
        path.parent.mkdir(parents=True)
        path.write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(core.WorkflowError, "already has a committed"):
            core.build_export(self.root, self.assignment, snap)

    def test_extra_columns_and_wrong_order_rejected(self):
        with self.assertRaisesRegex(core.WorkflowError, "columns must be"):
            core.parse_snapshot(csv_text(list(reversed(core.OUTBOX_FIELDS)), [self.receipt]),
                                self.assignment, self.source)


if __name__ == "__main__":
    unittest.main()
