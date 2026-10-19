"""Network-free command authorization, CAS-race and interrupted-PR recovery tests."""
import copy
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
import voice_submission_bot as bot
import voice_submission_core as core
from test_contribution_bot import FakeGitHub, MemoryState, bot as fixture_bot
from test_voice_submission_core import csv_text


class VoiceGitHub(FakeGitHub):
    def __init__(self):
        super().__init__()
        self.approval = {}

    def api(self, path, method="GET", data=None):
        if path == "/issues/comments/42":
            return copy.deepcopy(self.approval)
        try:
            return super().api(path, method, data)
        except fixture_bot.ApiError as error:
            raise bot.ApiError(error.status, "Fake GitHub error") from error


class VoiceBotTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = pathlib.Path(temp.name)
        path = self.root / "voice/scripts/rifleman.csv"
        path.parent.mkdir(parents=True)
        self.source_text = csv_text(["file", "situation", "tone", "line", "current_voices"], [
            {"file": "Ready", "situation": "Order confirmed", "tone": "Calm", "line": "Ready.",
             "current_voices": "Rifleman"}])
        path.write_text(self.source_text, encoding="utf-8")
        self.source_path = path
        self.source = core.get_source(self.root, "en", "rifleman")
        self.assignment = {"issue": 12, "kind": "voice-audio", "locale": "en", "table": "rifleman",
                           "casting_slot": "alpha", "recording_version": 1, "contributor": "Actor",
                           "reviewer": "Reviewer", "spreadsheet_id": "s" * 44, "tab": "Voice Outbox",
                           "keys": ["Ready"], "script_hash": core.script_hash(self.source), "status": "assigned"}
        self.receipt = {"Work order": "12", "Take file": "Ready",
                        "Drive snapshot": "https://drive.google.com/file/d/" + "f" * 32 + "/view",
                        "SHA256": "a" * 64, "Bytes": "1024", "MIME type": "audio/wav",
                        "Revision": "b" * 64, "Submitted": "2026-10-20T01:02:03Z",
                        "Script SHA256": self.assignment["script_hash"]}
        self.sheet = csv_text(core.OUTBOX_FIELDS, [self.receipt])
        self.gh = VoiceGitHub()
        self.store = MemoryState([self.assignment])
        self.issue = {"number": 12, "state": "open", "body": self.body()}
        self.patches = [mock.patch.object(bot, "ROOT", self.root),
                        mock.patch.object(bot, "fetch_sheet", side_effect=lambda _: self.sheet),
                        mock.patch.dict(os.environ, {"CHECKED_OUT_SHA": "base-sha"}),
                        mock.patch.object(bot.urllib.request, "urlopen",
                                          side_effect=AssertionError("unexpected network request"))]
        for patch in self.patches:
            patch.start()
            self.addCleanup(patch.stop)

    def body(self, **changes):
        values = {"Locale": "en", "Voice role": "rifleman", "Casting slot": "alpha", "Recording version": "1",
                  "Contributor": "Actor", "Reviewer": "Reviewer",
                  "Spreadsheet URL": "https://docs.google.com/spreadsheets/d/" + "s" * 44 + "/edit",
                  "Sheet tab": "Voice Outbox", "First take": "Ready", "Last take": "Ready"}
        values.update(changes)
        return "\n\n".join(f"### {key}\n\n{value}" for key, value in values.items())

    def run_command(self, command, actor="maintainer", digest=None, comment_id=42):
        return bot.process(self.gh, self.store, self.issue, actor, command, digest, comment_id)

    def preview(self):
        self.run_command("preview", "Actor")
        digest = self.store.state["assignments"][0]["candidate"]
        self.gh.approval = {"user": {"login": "Reviewer"}, "body": f"/voice approve {digest}",
                            "issue_url": f"https://api.github.com/repos/{self.gh.repo}/issues/12"}
        return digest

    def test_unauthorized_assign_cannot_reserve(self):
        self.store = MemoryState()
        with self.assertRaisesRegex(core.WorkflowError, "Only repository maintainers"):
            self.run_command("assign", "intruder")
        self.assertEqual(0, self.store.mutations)

    def test_issue_assignment_freezes_casting_version_and_script(self):
        assignment, source = bot.assignment_from_issue(self.issue, self.root)
        self.assertEqual("alpha", assignment["casting_slot"])
        self.assertEqual(1, assignment["recording_version"])
        self.assertEqual(core.script_hash(source), assignment["script_hash"])
        self.issue["body"] = self.body(**{"Casting slot": "../alpha"})
        with self.assertRaises(core.WorkflowError):
            bot.assignment_from_issue(self.issue, self.root)

    def test_only_participants_or_maintainer_can_preview(self):
        with self.assertRaisesRegex(core.WorkflowError, "Only the assigned"):
            self.run_command("preview", "intruder")
        self.assertEqual(0, self.store.mutations)
        self.preview()
        self.assertEqual(1, len([p for p in self.store.files if p.endswith(".json")]))

    def test_approval_requires_independent_designated_reviewer(self):
        digest = self.preview()
        for actor in ("Actor", "maintainer", "intruder"):
            with self.subTest(actor=actor):
                with self.assertRaisesRegex(core.WorkflowError, "designated reviewer"):
                    self.run_command("approve", actor, digest)
        self.assertEqual(0, self.gh.pr_creations)

    def test_approval_requires_live_exact_comment_on_same_issue(self):
        digest = self.preview()
        original = copy.deepcopy(self.gh.approval)
        for changed in [{"body": "/voice approve " + "c" * 64}, {"user": {"login": "Actor"}},
                        {"issue_url": f"https://api.github.com/repos/{self.gh.repo}/issues/99"}]:
            self.gh.approval = {**original, **changed}
            with self.assertRaisesRegex(core.WorkflowError, "comment is missing"):
                self.run_command("approve", "Reviewer", digest)
        with self.assertRaisesRegex(core.WorkflowError, "live /voice approve"):
            self.run_command("approve", "Reviewer", digest, comment_id=None)
        self.assertEqual(1, self.store.mutations)

    def test_changed_receipts_or_source_invalidate_preview(self):
        digest = self.preview()
        self.sheet = csv_text(core.OUTBOX_FIELDS, [{**self.receipt, "Bytes": "2048"}])
        with self.assertRaisesRegex(core.WorkflowError, "Content changed"):
            self.run_command("approve", "Reviewer", digest)
        self.sheet = csv_text(core.OUTBOX_FIELDS, [self.receipt])
        self.source_path.write_text(self.source_text.replace("Calm", "Urgent"), encoding="utf-8")
        with self.assertRaisesRegex(core.WorkflowError, "script or approved"):
            self.run_command("approve", "Reviewer", digest)
        self.assertEqual(0, self.gh.pr_creations)

    def test_approval_opens_exactly_one_manifest_pr_and_retry_is_idempotent(self):
        digest = self.preview()
        self.run_command("approve", "Reviewer", digest)
        self.run_command("approve", "Reviewer", digest)
        self.assertEqual(1, self.gh.pr_creations)
        self.assertEqual("pr_open", self.store.state["assignments"][0]["status"])
        self.assertEqual(1, len(self.gh.commits))
        _, _, files = self.gh.commits[0]
        self.assertEqual(["voice/submissions/en/rifleman/alpha/12.json"], list(files))
        self.assertEqual([self.receipt], json.loads(next(iter(files.values())))["receipts"])
        self.assertEqual(42, self.store.state["assignments"][0]["approval_comment"])
        self.assertGreaterEqual(self.gh.policy_dispatches, 1)

    def test_interrupted_pr_creation_recovers_same_branch_without_duplicate_commit(self):
        digest = self.preview()
        self.gh.fail_pr_once = True
        with self.assertRaises(bot.ApiError):
            self.run_command("approve", "Reviewer", digest)
        self.assertEqual("reviewed", self.store.state["assignments"][0]["status"])
        self.run_command("approve", "Reviewer", digest)
        self.assertEqual(1, self.gh.pr_creations)
        self.assertEqual(1, len(self.gh.commits))

    def test_default_branch_advance_stops_delivery(self):
        digest = self.preview()
        self.gh.branches["main"] = "new-main-sha"
        with self.assertRaisesRegex(core.WorkflowError, "Default branch advanced"):
            self.run_command("approve", "Reviewer", digest)
        self.assertEqual(0, self.gh.pr_creations)
        self.assertEqual([], self.gh.commits)

    def test_release_and_sync_require_maintainer(self):
        for command in ("release", "sync"):
            with self.assertRaisesRegex(core.WorkflowError, "Only maintainers"):
                self.run_command(command, "Actor")
        self.assertEqual(0, self.store.mutations)

    def test_open_pr_cannot_release_and_merged_pr_completes_reservation(self):
        self.run_command("approve", "Reviewer", self.preview())
        with self.assertRaisesRegex(core.WorkflowError, "Close the unmerged"):
            self.run_command("release")
        pr = next(iter(self.gh.prs.values()))
        pr.update(state="closed", merged_at="2026-10-20T01:02:03Z")
        self.run_command("sync")
        self.run_command("sync")
        self.assertEqual("completed", self.store.state["assignments"][0]["status"])

    def test_cas_race_rechecks_overlap_instead_of_overwriting(self):
        gh = mock.Mock()
        gh.commit_files.return_value = "new-sha"
        gh.api.side_effect = bot.ApiError(422, "not fast-forward")
        store = bot.State(gh)
        winner = {**self.assignment, "issue": 13}
        with mock.patch.object(store, "read", side_effect=[
            ("old", {"assignments": []}),
            ("new", {"assignments": [winner]})]):
            with self.assertRaisesRegex(core.WorkflowError, "overlaps active"):
                store.mutate(lambda state: (core.reserve(state, self.assignment, self.source), {}))
        self.assertEqual(1, gh.commit_files.call_count)
        self.assertEqual(1, gh.api.call_count)


if __name__ == "__main__":
    unittest.main()
