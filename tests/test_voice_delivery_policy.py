"""Adversarial no-network checks for the trusted recording-manifest gate."""

import base64
import copy
import csv
import importlib.util
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock


TOOLS = pathlib.Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location("voice_delivery_under_test", TOOLS / "check_sheet_delivery.py")
delivery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(delivery)
import voice_submission_core as core


class MemoryState:
    def __init__(self, assignment=None, snapshot=None):
        self.ledger = {"schema": 1, "assignments": [] if assignment is None else [copy.deepcopy(assignment)]}
        self.snapshot = copy.deepcopy(snapshot)
        self.reads = 0
        self.changed = False
        self.error = None
        self.snapshot_refs = []

    def read(self):
        if self.error:
            raise self.error
        self.reads += 1
        return ("state-2" if self.changed and self.reads > 1 else "state-1"), copy.deepcopy(self.ledger)

    def read_file(self, path, ref):
        self.snapshot_refs.append((path, ref))
        return copy.deepcopy(self.snapshot)


class FakeGitHub:
    repo = "Epheria/Ebbtide-Community"

    def __init__(self, assignment, path, content):
        self.head_sha = "b" * 40
        self.default_sha = "a" * 40
        self.pr = {"number": 77, "state": "open", "changed_files": 1,
                   "head": {"sha": self.head_sha, "ref": assignment["branch"], "repo": {"full_name": self.repo}},
                   "base": {"ref": "main", "repo": {"full_name": self.repo}}}
        self.files = [{"filename": path, "status": "added"}]
        self.path = path
        self.content = content
        self.comment = {"user": {"login": "Reviewer"}, "body": f"/voice approve {assignment['candidate']}",
                        "issue_url": f"https://api.github.com/repos/{self.repo}/issues/{assignment['issue']}"}
        self.mode = "100644"
        self.truncated = False
        self.comment_deleted = False
        self.comment_reads = 0
        self.revoke_on_second_comment = False
        self.change_head = False
        self.change_base = False
        self.pr_reads = 0
        self.calls = []
        self.statuses = []

    def api(self, path, method="GET", data=None):
        self.calls.append((path, method, data))
        if path == "/statuses/" + self.head_sha and method == "POST":
            self.statuses.append(copy.deepcopy(data))
            return data
        if method != "GET" or data is not None:
            raise AssertionError("Manifest policy attempted a mutation")
        if path == "":
            return {"default_branch": "main"}
        if path == "/pulls/77":
            self.pr_reads += 1
            result = copy.deepcopy(self.pr)
            if self.pr_reads > 1 and self.change_head:
                result["head"]["sha"] = "c" * 40
            if self.pr_reads > 1 and self.change_base:
                result["base"]["ref"] = "other"
            return result
        if path.startswith("/pulls/77/files?per_page=100&page="):
            page = int(path.rsplit("=", 1)[1])
            return copy.deepcopy(self.files[(page - 1) * 100:page * 100])
        if path == "/issues/comments/1001":
            self.comment_reads += 1
            if self.comment_deleted:
                raise delivery.ApiError(404, "Deleted")
            result = copy.deepcopy(self.comment)
            if self.revoke_on_second_comment and self.comment_reads > 1:
                result["body"] = "approval revoked during verification"
            return result
        if path == "/git/ref/heads/main":
            return {"object": {"sha": self.default_sha}}
        if path == "/git/trees/" + self.head_sha + "?recursive=1":
            return {"truncated": self.truncated,
                    "tree": [{"path": self.path, "mode": self.mode, "type": "blob"}]}
        if path.startswith("/contents/"):
            return {"type": "file", "encoding": "base64",
                    "content": base64.b64encode(self.content.encode("utf-8")).decode("ascii")}
        raise AssertionError("Unexpected API call: " + path)


class VoiceDeliveryPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        source_path = self.root / "voice/scripts/role.csv"
        source_path.parent.mkdir(parents=True)
        source_path.write_text("file,situation,tone,line,current_voices\ntake_one,Contact,Calm,Contact ahead.,AI\n",
                               encoding="utf-8")
        source = core.get_source(self.root, "en", "role")
        assignment = {"issue": 12, "kind": "voice-audio", "locale": "en", "table": "role",
                      "casting_slot": "main", "recording_version": 1,
                      "contributor": "Volunteer", "reviewer": "Reviewer",
                      "spreadsheet_id": "a" * 30, "tab": "Outbox", "keys": ["take_one"],
                      "script_hash": core.script_hash(source)}
        output = io.StringIO(newline="")
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(core.OUTBOX_FIELDS)
        writer.writerow([12, "take_one", "https://drive.google.com/file/d/" + "x" * 30 + "/view",
                         "c" * 64, 12345, "audio/wav", "d" * 64, "2026-10-20T04:00:00Z",
                         assignment["script_hash"]])
        snapshot = core.parse_snapshot(output.getvalue(), assignment, source)
        snapshot["target_hash"] = core.target_hash(self.root, assignment)
        snapshot["digest"] = core.snapshot_hash(snapshot)
        path, content = core.build_export(self.root, assignment, snapshot)
        assignment.update(status="pr_open", candidate=snapshot["digest"], approved_by="Reviewer",
                          approval_comment=1001, pr=77,
                          branch=f"community/voice-12-{snapshot['digest'][:12]}")
        self.assignment = assignment
        self.snapshot = snapshot
        self.state = MemoryState(assignment, snapshot)
        self.gh = FakeGitHub(assignment, path, content)

    def check(self):
        return delivery.check_voice_delivery(self.gh, 77, self.root, state_store=self.state,
                                             checked_out_sha="a" * 40, expected_head_sha="b" * 40)

    def outer_check(self):
        import voice_submission_bot
        with mock.patch.object(voice_submission_bot, "VoiceState", return_value=self.state):
            return delivery.check_delivery(self.gh, MemoryState(), 77, self.root,
                                            checked_out_sha="a" * 40, expected_head_sha="b" * 40)

    def test_exact_approved_manifest_passes_read_only_from_pinned_state(self):
        self.assertIn("reviewed voice snapshot", self.check())
        self.assertEqual([(f"snapshots/12/{self.assignment['candidate']}.json", "state-1")],
                         self.state.snapshot_refs)
        self.assertTrue(all(method == "GET" for _, method, _ in self.gh.calls))
        self.assertFalse(any("drive.google.com" in path for path, _, _ in self.gh.calls))

    def test_required_sheet_policy_routes_voice_manifest_to_its_own_ledger(self):
        self.assertIn("reviewed voice snapshot", self.outer_check())

    def test_manual_manifest_without_reserved_and_reviewed_state_fails(self):
        self.state.ledger["assignments"] = []
        with self.assertRaisesRegex(core.WorkflowError, "no unique"):
            self.outer_check()
        self.state.error = delivery.ApiError(404, "Missing")
        with self.assertRaisesRegex(core.WorkflowError, "voice work order"):
            self.check()

    def test_forged_manifest_hash_or_bytes_cannot_replace_approved_content(self):
        original = self.gh.content
        for candidate in (original.replace("c" * 64, "e" * 64), original + "\n"):
            self.gh.content = candidate
            with self.subTest(candidate=candidate[-40:]), self.assertRaisesRegex(core.WorkflowError, "differs"):
                self.check()

    def test_mutated_snapshot_or_assignment_fails(self):
        self.state.snapshot["rows"][0]["SHA256"] = "e" * 64
        with self.assertRaisesRegex(core.WorkflowError, "digest"):
            self.check()
        self.state.snapshot = copy.deepcopy(self.snapshot)
        self.state.ledger["assignments"][0]["casting_slot"] = "other"
        with self.assertRaisesRegex(core.WorkflowError, "different voice assignment"):
            self.check()

    def test_approval_requires_independent_reviewer_and_live_exact_comment(self):
        original = copy.deepcopy(self.gh.comment)
        for changes in ({"user": {"login": "Volunteer"}}, {"body": "/voice approve " + "e" * 64},
                        {"body": original["body"] + "\nextra"},
                        {"issue_url": f"https://api.github.com/repos/{self.gh.repo}/issues/999"}):
            self.gh.comment = {**original, **changes}
            with self.subTest(changes=changes), self.assertRaisesRegex(core.WorkflowError, "approval comment"):
                self.check()

    def test_deleted_approval_fails_closed(self):
        self.gh.comment_deleted = True
        with self.assertRaises(delivery.ApiError):
            self.check()

    def test_approval_is_rechecked_after_reading_manifest_and_registry(self):
        self.gh.revoke_on_second_comment = True
        with self.assertRaisesRegex(core.WorkflowError, "approval comment"):
            self.check()
        self.assertEqual(2, self.gh.comment_reads)

    def test_missing_dispatch_or_self_approval_is_never_a_voice_approval(self):
        original = copy.deepcopy(self.assignment)
        for changes in ({"approval_comment": None}, {"approved_by": "Other"},
                        {"contributor": "REVIEWER"}, {"status": "released"}):
            self.state.ledger["assignments"] = [{**original, **changes}]
            with self.subTest(changes=changes), self.assertRaises(core.WorkflowError):
                self.check()

    def test_mixed_code_or_translation_files_fail_before_authority_lookup(self):
        for path in ("tools/voice_submission_core.py", "voice/translations/ja/role.csv"):
            self.gh.files = [{"filename": self.gh.path, "status": "added"},
                             {"filename": path, "status": "modified"}]
            self.gh.pr["changed_files"] = 2
            with self.subTest(path=path), self.assertRaisesRegex(core.WorkflowError, "exactly one"):
                self.outer_check()
        self.assertEqual(0, self.state.reads)

    def test_delete_modify_and_rename_out_of_controlled_root_fail(self):
        for file in ({"filename": self.gh.path, "status": "removed"},
                     {"filename": self.gh.path, "status": "modified"},
                     {"filename": "docs/moved.json", "previous_filename": self.gh.path, "status": "renamed"},
                     {"filename": self.gh.path, "previous_filename": "docs/a.json", "status": "renamed"}):
            self.gh.files = [file]
            with self.subTest(file=file), self.assertRaisesRegex(core.WorkflowError, "exactly one"):
                self.outer_check()

    def test_nested_uppercase_or_non_json_protected_files_cannot_bypass(self):
        for path in ("voice/submissions/en/role/main/nested/12.json",
                     "voice/submissions/en/role/main/12.JSON", "voice/submissions/README.md",
                     "voice/submissions/en/role/main/0.json"):
            self.gh.files = [{"filename": path, "status": "added"}]
            with self.subTest(path=path), self.assertRaisesRegex(core.WorkflowError, "Unsupported voice"):
                self.outer_check()

    def test_wrong_scope_path_and_symlink_or_truncated_tree_fail(self):
        self.gh.files[0]["filename"] = "voice/submissions/en/role/other/12.json"
        with self.assertRaisesRegex(core.WorkflowError, "outside"):
            self.check()
        self.gh.files[0]["filename"] = self.gh.path
        self.gh.mode = "120000"
        with self.assertRaisesRegex(core.WorkflowError, "symlink"):
            self.check()
        self.gh.mode = "100644"
        self.gh.truncated = True
        with self.assertRaisesRegex(core.WorkflowError, "complete delivery Git tree"):
            self.check()

    def test_changed_source_and_existing_target_manifest_fail(self):
        path = self.root / "voice/scripts/role.csv"
        original = path.read_text(encoding="utf-8")
        path.write_text(original.replace("Contact ahead.", "Hold position."), encoding="utf-8")
        with self.assertRaisesRegex(core.WorkflowError, "script or approved spoken text changed"):
            self.check()
        path.write_text(original, encoding="utf-8")
        target = self.root / self.gh.path
        target.parent.mkdir(parents=True)
        target.write_text(self.gh.content, encoding="utf-8")
        with self.assertRaisesRegex(core.WorkflowError, "already has a committed manifest"):
            self.check()

    def test_wrong_branch_fork_or_base_and_old_checkout_fail(self):
        original = copy.deepcopy(self.gh.pr)
        for part, changes in (("head", {"ref": "arbitrary"}), ("head", {"repo": {"full_name": "other/fork"}}),
                              ("base", {"ref": "other"}), ("base", {"repo": {"full_name": "other/repo"}})):
            self.gh.pr = copy.deepcopy(original)
            self.gh.pr[part].update(changes)
            with self.subTest(part=part), self.assertRaises(core.WorkflowError):
                self.check()
        self.gh.pr = original
        self.gh.default_sha = "d" * 40
        with self.assertRaisesRegex(core.WorkflowError, "fresh trusted checkout"):
            self.check()

    def test_racing_pr_and_state_cannot_publish_green_status(self):
        self.gh.change_head = True
        with self.assertRaisesRegex(core.WorkflowError, "PR changed"):
            self.check()
        self.gh.change_head = False
        self.state.reads = 0
        self.state.changed = True
        with self.assertRaisesRegex(core.WorkflowError, "Voice reservation or default"):
            self.check()

    def approval_event(self, action="edited", **changes):
        event = {"action": action, "issue": {"number": 12},
                 "comment": {"id": 1001, "body": "approval revoked"},
                 "changes": {"body": {"from": "/voice approve " + self.assignment["candidate"]}}}
        event.update(changes)
        return event

    def test_voice_comment_event_resolves_only_registered_issue_and_comment(self):
        for action in ("edited", "deleted"):
            self.assertEqual(77, delivery.resolve_pr_number(MemoryState(), self.approval_event(action),
                                                            voice_state_store=self.state))
        for event in (self.approval_event(issue={"number": 999}), self.approval_event(comment={"id": 999})):
            self.assertIsNone(delivery.resolve_pr_number(MemoryState(), event, voice_state_store=self.state))
        with self.assertRaisesRegex(core.WorkflowError, "unique"):
            delivery.resolve_pr_number(self.state, self.approval_event(), voice_state_store=self.state)

    def test_main_revoked_or_deleted_voice_approval_publishes_failure(self):
        import voice_submission_bot
        for action in ("edited", "deleted"):
            event_path = self.root / "event.json"
            event_path.write_text(json.dumps(self.approval_event(action)), encoding="utf-8")
            environment = {"GITHUB_EVENT_PATH": str(event_path), "GITHUB_REPOSITORY": self.gh.repo,
                           "GH_TOKEN": "fake-test-token", "CHECKED_OUT_SHA": "a" * 40}
            actual = delivery.check_delivery
            def local_check(gh, store, number, **kwargs):
                return actual(gh, store, number, self.root, **kwargs)
            self.gh.comment["body"] = "approval revoked"
            self.gh.comment_deleted = action == "deleted"
            with self.subTest(action=action), mock.patch.dict(os.environ, environment, clear=True), \
                    mock.patch.object(delivery, "GitHub", return_value=self.gh), \
                    mock.patch.object(delivery, "State", return_value=MemoryState()), \
                    mock.patch.object(voice_submission_bot, "VoiceState", return_value=self.state), \
                    mock.patch.object(delivery, "check_delivery", side_effect=local_check), \
                    mock.patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(1, delivery.main())
                self.assertEqual("failure", self.gh.statuses[-1]["state"])
                self.assertEqual("reviewed-sheet", self.gh.statuses[-1]["context"])


if __name__ == "__main__":
    unittest.main()
