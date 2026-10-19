"""Behavioral tests for assignments, immutable previews and safe table exports."""

import copy
import csv
import hashlib
import importlib.util
import io
import pathlib
import tempfile
import unittest


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "contribution_core.py"
SPEC = importlib.util.spec_from_file_location("contribution_core", MODULE_PATH)
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


def csv_text(fields, rows):
    text = io.StringIO(newline="")
    writer = csv.DictWriter(text, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return text.getvalue()


class ContributionCoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name)
        self.source = [{"key": "a", "en": "Ready {0}."}, {"key": "b", "en": "Hold."}]
        path = self.root / "localization/source/strings/TacticalHUD.csv"
        path.parent.mkdir(parents=True)
        path.write_text(csv_text(["key", "en", "ko"], [{**row, "ko": ""} for row in self.source]), encoding="utf-8")
        self.assignment = {"issue": 12, "kind": "ui", "locale": "ja", "table": "TacticalHUD",
                           "contributor": "Volunteer", "reviewer": "Reviewer", "spreadsheet_id": "a" * 44,
                           "tab": "TacticalHUD", "keys": ["a"], "source_hash": core.source_hash(self.source)}

    def sheet(self, **changes):
        rows = [{"key": "a", "en": "Ready {0}.", "translation": "準備完了 {0}。", "status": ""},
                {"key": "b", "en": "Hold.", "translation": "", "status": ""}]
        rows[0].update(changes)
        return csv_text(core.UI_FIELDS, rows)

    def snapshot(self):
        snapshot = core.parse_snapshot(self.sheet(), self.assignment, self.source)
        snapshot["target_hash"] = core.target_hash(self.root, self.assignment)
        snapshot["digest"] = core.snapshot_hash(snapshot)
        return snapshot

    def test_reserve_overlap_is_blocked_until_release_without_mutating_inputs(self):
        state = {"assignments": []}
        reserved = core.reserve(state, self.assignment, self.source)
        self.assertEqual([], state["assignments"])
        self.assertNotIn("status", self.assignment)
        other = {**self.assignment, "issue": 13}
        with self.assertRaisesRegex(core.WorkflowError, "overlap"):
            core.reserve(reserved, other, self.source)
        reserved["assignments"][0]["status"] = "released"
        self.assertEqual(2, len(core.reserve(reserved, other, self.source)["assignments"]))

    def test_claims_can_share_table_for_different_keys_or_locales(self):
        state = core.reserve({}, self.assignment, self.source)
        for other in ({**self.assignment, "issue": 13, "keys": ["b"]},
                      {**self.assignment, "issue": 14, "locale": "ko"}):
            self.assertEqual(2, len(core.reserve(state, other, self.source)["assignments"]))

    def test_issue_cannot_have_two_active_claims(self):
        state = core.reserve({}, self.assignment, self.source)
        with self.assertRaisesRegex(core.WorkflowError, "already has"):
            core.reserve(state, {**self.assignment, "locale": "ko"}, self.source)

    def test_terminal_issues_cannot_be_reused_but_completed_claims_release_keys(self):
        state = core.reserve({}, self.assignment, self.source)
        for status in ("completed", "released", "cancelled"):
            state["assignments"][0]["status"] = status
            with self.subTest(status=status), self.assertRaisesRegex(core.WorkflowError, "new issue"):
                core.reserve(state, self.assignment, self.source)
            new_claim = {**self.assignment, "issue": 13}
            self.assertEqual(2, len(core.reserve(state, new_claim, self.source)["assignments"]))

    def test_assignment_rejects_self_review_path_injection_and_too_many_keys(self):
        for change in ({"reviewer": "VOLUNTEER"}, {"locale": "../ja"}, {"table": "../TacticalHUD"},
                       {"spreadsheet_id": "https://example.com"}, {"issue": True},
                       {"keys": ["a", "a"]}, {"keys": ["x"] * 201}):
            with self.subTest(change=change), self.assertRaises(core.WorkflowError):
                core.validate_assignment({**self.assignment, **change}, self.source)

    def test_source_changes_and_blank_or_held_wording_block_assignment(self):
        changed = copy.deepcopy(self.source)
        changed[0]["en"] = "Changed."
        with self.assertRaisesRegex(core.WorkflowError, "source changed"):
            core.validate_assignment(self.assignment, changed)
        for replacement in ({"key": "a", "en": ""}, {"key": "a", "en": "Ready {0}.", "source_ready": False}):
            source = [replacement, self.source[1]]
            with self.assertRaisesRegex(core.WorkflowError, "on hold"):
                core.validate_assignment({**self.assignment, "source_hash": core.source_hash(source)}, source)

    def test_snapshot_rejects_bad_source_status_placeholder_and_blank_translation(self):
        for change in ({"en": "Tampered."}, {"status": "review"}, {"status": "outdated"},
                       {"translation": "No token"}, {"translation": "   "}):
            with self.subTest(change=change), self.assertRaises(core.WorkflowError):
                core.parse_snapshot(self.sheet(**change), self.assignment, self.source)

    def test_unknown_duplicate_missing_and_malformed_rows_fail_closed(self):
        valid = self.sheet()
        cases = [valid + "a,Ready {0}.,other {0},\n", valid + "unknown,Other.,Other.,\n",
                 csv_text(core.UI_FIELDS, [{"key": "b", "en": "Hold.", "translation": "", "status": ""}]),
                 valid + '"unterminated', valid.replace("key,en,translation,status", "key,en,translation,state"),
                 valid + "a,Ready {0}.,short\n"]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(core.WorkflowError):
                core.parse_snapshot(text, self.assignment, self.source)

    def test_snapshot_hash_binds_text_people_scope_and_target_but_ignores_digest(self):
        snapshot = self.snapshot()
        digest = core.snapshot_hash(snapshot)
        self.assertEqual(digest, core.snapshot_hash({**snapshot, "digest": "irrelevant"}))
        for key, value in (("target_hash", "f" * 64), ("source_hash", "e" * 64)):
            self.assertNotEqual(digest, core.snapshot_hash({**snapshot, key: value}))
        changed = copy.deepcopy(snapshot)
        changed["assignment"]["reviewer"] = "SomebodyElse"
        self.assertNotEqual(digest, core.snapshot_hash(changed))
        changed = copy.deepcopy(snapshot)
        changed["rows"][0]["translation"] = "別の翻訳 {0}。"
        self.assertNotEqual(digest, core.snapshot_hash(changed))

    def test_export_preserves_other_translations_and_outputs_every_source_key(self):
        target = self.root / "localization/translations/ja/TacticalHUD.csv"
        target.parent.mkdir(parents=True)
        target.write_text(csv_text(core.UI_FIELDS, [
            {"key": "a", "en": "Ready {0}.", "translation": "old {0}", "status": "review"},
            {"key": "b", "en": "Hold.", "translation": "待機。", "status": "review"}]), encoding="utf-8")
        before = target.read_bytes()
        relative, text = core.build_export(self.root, self.assignment, self.snapshot())
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual("localization/translations/ja/TacticalHUD.csv", relative)
        self.assertEqual(["a", "b"], [row["key"] for row in rows])
        self.assertEqual("準備完了 {0}。", rows[0]["translation"])
        self.assertEqual("", rows[0]["status"])
        self.assertEqual({"key": "b", "en": "Hold.", "translation": "待機。", "status": "review"}, rows[1])
        self.assertEqual(before, target.read_bytes())

    def test_missing_target_fills_unassigned_rows_without_blank_overwrite(self):
        relative, text = core.build_export(self.root, self.assignment, self.snapshot())
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual("", rows[1]["translation"])
        self.assertEqual(hashlib.sha256(b"MISSING").hexdigest(), core.target_hash(self.root, self.assignment))
        self.assertFalse((self.root / relative).exists())

    def test_export_requires_target_baseline_binding(self):
        snapshot = core.parse_snapshot(self.sheet(), self.assignment, self.source)
        with self.assertRaisesRegex(core.WorkflowError, "target hash"):
            core.build_export(self.root, self.assignment, snapshot)

    def test_export_blocks_changed_target_source_assignment_or_snapshot(self):
        snapshot = self.snapshot()
        target = self.root / "localization/translations/ja/TacticalHUD.csv"
        target.parent.mkdir(parents=True)
        target.write_text(self.sheet(), encoding="utf-8")
        with self.assertRaisesRegex(core.WorkflowError, "target changed"):
            core.build_export(self.root, self.assignment, snapshot)
        target.unlink()
        changed = copy.deepcopy(snapshot)
        changed["rows"][0]["translation"] = "changed {0}"
        with self.assertRaisesRegex(core.WorkflowError, "digest"):
            core.build_export(self.root, self.assignment, changed)
        with self.assertRaisesRegex(core.WorkflowError, "different assignment"):
            core.build_export(self.root, {**self.assignment, "reviewer": "OtherReviewer"}, snapshot)
        source_file = self.root / "localization/source/strings/TacticalHUD.csv"
        source_file.write_text(source_file.read_text(encoding="utf-8").replace("Hold.", "Changed."), encoding="utf-8")
        with self.assertRaisesRegex(core.WorkflowError, "source changed"):
            core.build_export(self.root, self.assignment, snapshot)

    def test_export_rejects_existing_changed_source_and_duplicate_keys(self):
        target = self.root / "localization/translations/ja/TacticalHUD.csv"
        target.parent.mkdir(parents=True)
        for text in (self.sheet().replace("Hold.", "Wrong."), self.sheet() + "b,Hold.,duplicate,\n"):
            target.write_text(text, encoding="utf-8")
            with self.subTest(text=text), self.assertRaises(core.WorkflowError):
                core.build_export(self.root, self.assignment, self.snapshot())

    def voice_setup(self):
        path = self.root / "voice/scripts/squad_leader.csv"
        path.parent.mkdir(parents=True)
        rows = [dict(file="SL_Select", situation="Selected.", tone="Calm", line="<callsign>. Ready.", current_voices="Leader"),
                dict(file="SL_Hold", situation="Wording not confirmed", tone="Calm", line="Hold.", current_voices="Leader")]
        path.write_text(csv_text(["file", "situation", "tone", "line", "current_voices"], rows), encoding="utf-8")
        source = core.get_source(self.root, "voice-text", "squad_leader")
        assignment = {**self.assignment, "kind": "voice-text", "table": "squad_leader", "tab": "Japanese",
                      "keys": ["SL_Select"], "source_hash": core.source_hash(source)}
        row = dict.fromkeys(core.VOICE_FIELDS, "")
        row.update({"Take file": "SL_Select", "English source": "<callsign>. Ready.",
                    "Translation": "<callsign>。準備完了。", "Review status": "Approved",
                    "Role": "squad_leader", "Source readiness": "Ready"})
        return source, assignment, row

    def test_voice_filters_other_roles_requires_approval_and_exports_canonical_schema(self):
        source, assignment, row = self.voice_setup()
        other = {**row, "Role": "rifleman", "Take file": "RF_Select", "English source": "Other."}
        snapshot = core.parse_snapshot(csv_text(core.VOICE_FIELDS, [other, row]), assignment, source)
        snapshot["target_hash"] = core.target_hash(self.root, assignment)
        relative, text = core.build_export(self.root, assignment, snapshot)
        self.assertEqual("voice/translations/ja/squad_leader.csv", relative)
        self.assertEqual(core.UI_FIELDS, next(csv.reader(io.StringIO(text))))
        self.assertEqual(2, len(list(csv.DictReader(io.StringIO(text)))))
        for change in ({"Review status": "Draft"}, {"Review status": "approved"},
                       {"Source readiness": "Wording not confirmed"}, {"Role": "rifleman"}):
            with self.subTest(change=change), self.assertRaises(core.WorkflowError):
                core.parse_snapshot(csv_text(core.VOICE_FIELDS, [{**row, **change}]), assignment, source)

    def test_voice_duplicate_selected_key_even_under_another_role_fails(self):
        source, assignment, row = self.voice_setup()
        with self.assertRaisesRegex(core.WorkflowError, "exactly once"):
            core.parse_snapshot(csv_text(core.VOICE_FIELDS, [row, {**row, "Role": "rifleman"}]), assignment, source)
        held = {**assignment, "keys": ["SL_Hold"]}
        with self.assertRaisesRegex(core.WorkflowError, "on hold"):
            core.validate_assignment(held, source)

    def test_review_is_deterministic_and_escapes_contributor_markup(self):
        snapshot = self.snapshot()
        snapshot["rows"][0]["translation"] = "<callsign> | `test`\nnext @user ![link](https://example.com)"
        review = core.snapshot_review(snapshot)
        self.assertEqual(review, core.snapshot_review(snapshot))
        self.assertIn("&lt;callsign&gt; &#124; &#96;test&#96;\\nnext", review)
        self.assertNotIn("@user", review)
        self.assertNotIn("![link]", review)
        self.assertIn(core.snapshot_hash(snapshot), review)


if __name__ == "__main__":
    unittest.main()
