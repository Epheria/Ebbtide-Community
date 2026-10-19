"""No-network checks for the trusted, read-only translation delivery gate."""

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
SPEC = importlib.util.spec_from_file_location("sheet_delivery_under_test", TOOLS / "check_sheet_delivery.py")
delivery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(delivery)
import contribution_core as core


class MemoryState:
    def __init__(self, assignment, snapshot):
        self.sha = "state-1"
        self.ledger = {"schema": 1, "assignments": [copy.deepcopy(assignment)]}
        self.snapshot = copy.deepcopy(snapshot)
        self.reads = 0
        self.snapshot_refs = []
        self.change_on_second_read = False
        self.error = None

    def read(self):
        if self.error:
            raise self.error
        self.reads += 1
        sha = "state-2" if self.change_on_second_read and self.reads > 1 else self.sha
        return sha, copy.deepcopy(self.ledger)

    def read_file(self, path, ref):
        self.snapshot_refs.append((path, ref))
        return copy.deepcopy(self.snapshot)


class FakeGitHub:
    repo = "Epheria/Ebbtide-Community"

    def __init__(self, assignment, content):
        self.calls = []
        self.head_sha = "b" * 40
        self.default_sha = "a" * 40
        self.pr_reads = 0
        self.change_head_on_recheck = False
        self.change_base_on_recheck = False
        self.path = "localization/translations/ja/TacticalHUD.csv"
        self.pr = {"number": 77, "state": "open", "changed_files": 1,
                   "head": {"sha": self.head_sha, "ref": assignment["branch"], "repo": {"full_name": self.repo}},
                   "base": {"ref": "main", "repo": {"full_name": self.repo}},
                   "body": "This text is deliberately not trusted."}
        self.files = [{"filename": self.path, "status": "added"}]
        self.comment = {"user": {"login": "Reviewer"}, "body": f"/work approve {assignment['candidate']}",
                        "issue_url": f"https://api.github.com/repos/{self.repo}/issues/{assignment['issue']}"}
        self.content = content
        self.mode = "100644"
        self.truncated = False
        self.error_path = None
        self.error_status = 503
        self.statuses = []

    def api(self, path, method="GET", data=None):
        self.calls.append((path, method, data))
        if path == "/statuses/" + self.head_sha and method == "POST":
            self.statuses.append(copy.deepcopy(data))
            return {"state": data["state"]}
        if method != "GET" or data is not None:
            raise AssertionError("Delivery checker attempted a mutation")
        if path == self.error_path:
            raise delivery.ApiError(self.error_status, "Unavailable")
        if path == "/pulls/77":
            self.pr_reads += 1
            result = copy.deepcopy(self.pr)
            if self.change_head_on_recheck and self.pr_reads > 1:
                result["head"]["sha"] = "c" * 40
            if self.change_base_on_recheck and self.pr_reads > 1:
                result["base"]["ref"] = "different-base"
            return result
        if path.startswith("/pulls/77/files?per_page=100&page="):
            page = int(path.rsplit("=", 1)[1])
            return copy.deepcopy(self.files[(page - 1) * 100:page * 100])
        if path == "/issues/comments/1001":
            return copy.deepcopy(self.comment)
        if path == "":
            return {"default_branch": "main"}
        if path == "/git/ref/heads/main":
            return {"object": {"sha": self.default_sha}}
        if path == f"/git/trees/{self.head_sha}?recursive=1":
            return {"truncated": self.truncated, "tree": [{"path": self.path, "type": "blob", "mode": self.mode}]}
        if path == f"/contents/{self.path}?ref={self.head_sha}":
            return {"type": "file", "encoding": "base64", "content": base64.b64encode(self.content.encode()).decode()}
        raise AssertionError(f"Unexpected API call: {path}")


class SheetDeliveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name)
        source_path = self.root / "localization/source/strings/TacticalHUD.csv"
        source_path.parent.mkdir(parents=True)
        source_path.write_text("key,en,ko\na,Ready {0}.,\nb,Hold.,\n", encoding="utf-8")
        source = core.get_source(self.root, "ui", "TacticalHUD")
        self.assignment = {"issue": 12, "kind": "ui", "locale": "ja", "table": "TacticalHUD",
                           "contributor": "Volunteer", "reviewer": "Reviewer", "spreadsheet_id": "a" * 44,
                           "tab": "TacticalHUD", "keys": ["a"], "source_hash": core.source_hash(source)}
        sheet = "key,en,translation,status\na,Ready {0}.,準備完了 {0}。,\nb,Hold.,,\n"
        self.snapshot = core.parse_snapshot(sheet, self.assignment, source)
        self.snapshot["target_hash"] = core.target_hash(self.root, self.assignment)
        digest = core.snapshot_hash(self.snapshot)
        self.snapshot["digest"] = digest
        _, text = core.build_export(self.root, self.assignment, self.snapshot)
        self.assignment.update(status="pr_open", candidate=digest, approved_by="Reviewer", approval_comment=1001,
                               pr=77, branch=f"community/sheet-12-{digest[:12]}")
        self.gh = FakeGitHub(self.assignment, text)
        self.state = MemoryState(self.assignment, self.snapshot)

    def check(self):
        return delivery.check_delivery(self.gh, self.state, 77, self.root, checked_out_sha="a" * 40)

    def test_exact_reviewed_delivery_passes_read_only_and_uses_pinned_state(self):
        self.assertIn("PASS: PR #77", self.check())
        self.assertEqual(2, self.state.reads)
        self.assertTrue(all(method == "GET" for _, method, _ in self.gh.calls))
        self.assertEqual("state-1", self.state.snapshot_refs[0][1])

    def test_non_translation_pr_passes_without_registry_access(self):
        self.gh.files = [{"filename": "voice/scripts/squad_leader.csv", "status": "modified"}]
        self.state.error = delivery.ApiError(404, "Missing")
        self.assertIn("no controlled", self.check())
        self.assertEqual(0, self.state.reads)

    def test_non_translation_fast_path_rejects_racing_head_and_base(self):
        self.gh.files = [{"filename": "docs/info.md", "status": "modified"}]
        self.gh.change_head_on_recheck = True
        with self.assertRaisesRegex(core.WorkflowError, "head or base changed"):
            self.check()
        self.gh.change_head_on_recheck = False
        self.gh.pr_reads = 0
        self.gh.change_base_on_recheck = True
        with self.assertRaisesRegex(core.WorkflowError, "head or base changed"):
            self.check()
        self.assertEqual(0, self.state.reads)

    def test_non_translation_other_base_cannot_publish_shared_head_success(self):
        self.gh.files = [{"filename": "docs/info.md", "status": "modified"}]
        self.gh.pr["base"]["ref"] = "community/bot-branch"
        with self.assertRaisesRegex(core.WorkflowError, "default branch"):
            self.check()
        self.assertFalse(any("/files?" in path for path, _, _ in self.gh.calls))

    def test_paginated_non_translation_files_are_all_inspected(self):
        self.gh.files = [{"filename": f"docs/file-{i}.md", "status": "modified"} for i in range(101)]
        self.gh.pr["changed_files"] = 101
        self.assertIn("no controlled", self.check())
        self.assertTrue(any("page=2" in path for path, _, _ in self.gh.calls))

    def test_nested_uppercase_and_rename_bypasses_are_blocked(self):
        for file in ({"filename": "localization/translations/ja/nested/file.csv", "status": "added"},
                     {"filename": "voice/translations/ja/role.CSV", "status": "added"},
                     {"filename": "docs/moved.csv", "previous_filename": self.gh.path, "status": "renamed"},
                     {"filename": self.gh.path, "previous_filename": "localization/source/strings/TacticalHUD.csv", "status": "renamed"}):
            self.gh.files = [file]
            with self.subTest(file=file), self.assertRaises(core.WorkflowError):
                self.check()

    def test_delivery_cannot_mix_unrelated_changes(self):
        self.gh.files.append({"filename": "tools/check_sheet_delivery.py", "status": "modified"})
        self.gh.pr["changed_files"] = 2
        with self.assertRaisesRegex(core.WorkflowError, "exactly one"):
            self.check()

    def test_no_registry_missing_or_ambiguous_reservation_blocks_direct_pr(self):
        self.state.error = delivery.ApiError(404, "Missing")
        with self.assertRaisesRegex(core.WorkflowError, "work-order"):
            self.check()
        self.state.error = None
        self.state.ledger["assignments"] = []
        with self.assertRaisesRegex(core.WorkflowError, "no unique"):
            self.check()
        self.state.ledger["assignments"] = [self.assignment, copy.deepcopy(self.assignment)]
        with self.assertRaisesRegex(core.WorkflowError, "no unique"):
            self.check()

    def test_inactive_approval_mismatch_and_self_approval_fail(self):
        original = copy.deepcopy(self.state.ledger["assignments"][0])
        for changes in ({"status": "released"}, {"approved_by": "Other"}, {"contributor": "REVIEWER"},
                        {"candidate": "short"}):
            self.state.ledger["assignments"] = [{**original, **changes}]
            with self.subTest(changes=changes), self.assertRaises(core.WorkflowError):
                self.check()

    def test_comment_author_digest_issue_and_edit_are_verified_live(self):
        original = copy.deepcopy(self.gh.comment)
        for changes in ({"user": {"login": "Volunteer"}}, {"body": "/work approve " + "e" * 64},
                        {"body": original["body"] + "\nextra"},
                        {"issue_url": f"https://api.github.com/repos/{self.gh.repo}/issues/999"}):
            self.gh.comment = {**original, **changes}
            with self.subTest(changes=changes), self.assertRaisesRegex(core.WorkflowError, "approval comment"):
                self.check()

    def test_dispatch_approval_without_comment_is_allowed_from_trusted_registry(self):
        self.state.ledger["assignments"][0]["approval_comment"] = None
        self.assertIn("PASS", self.check())

    def test_snapshot_tampering_or_reassigned_scope_is_rejected(self):
        self.state.snapshot["rows"][0]["translation"] = "Changed {0}"
        with self.assertRaisesRegex(core.WorkflowError, "digest"):
            self.check()
        self.state.snapshot = copy.deepcopy(self.snapshot)
        self.state.ledger["assignments"][0]["contributor"] = "SomeoneElse"
        with self.assertRaisesRegex(core.WorkflowError, "different assignment"):
            self.check()

    def test_fork_arbitrary_branch_base_and_old_checkout_fail(self):
        original = copy.deepcopy(self.gh.pr)
        for part, changes in (("head", {"repo": {"full_name": "attacker/fork"}}),
                              ("head", {"ref": "arbitrary"}),
                              ("base", {"ref": "other"}),
                              ("base", {"repo": {"full_name": "other/repo"}})):
            self.gh.pr = copy.deepcopy(original)
            self.gh.pr[part].update(changes)
            with self.subTest(part=part, changes=changes), self.assertRaises(core.WorkflowError):
                self.check()
        self.gh.pr = original
        self.gh.default_sha = "c" * 40
        with self.assertRaisesRegex(core.WorkflowError, "fresh trusted checkout"):
            self.check()

    def test_file_content_and_git_mode_must_match_reviewed_snapshot(self):
        self.gh.content += "\n"
        with self.assertRaisesRegex(core.WorkflowError, "differs"):
            self.check()
        self.gh.content = self.gh.content[:-1]
        self.gh.mode = "120000"
        with self.assertRaisesRegex(core.WorkflowError, "symlink"):
            self.check()
        self.gh.mode = "100644"
        self.gh.truncated = True
        with self.assertRaisesRegex(core.WorkflowError, "complete delivery Git tree"):
            self.check()

    def test_source_and_target_changes_invalidate_delivery(self):
        source = self.root / "localization/source/strings/TacticalHUD.csv"
        original = source.read_text(encoding="utf-8")
        source.write_text(original.replace("Hold.", "Changed."), encoding="utf-8")
        with self.assertRaisesRegex(core.WorkflowError, "source changed"):
            self.check()
        source.write_text(original, encoding="utf-8")
        target = self.root / self.gh.path
        target.parent.mkdir(parents=True)
        target.write_text(self.gh.content, encoding="utf-8")
        with self.assertRaisesRegex(core.WorkflowError, "target changed"):
            self.check()

    def test_racing_head_or_state_fails_closed(self):
        self.gh.change_head_on_recheck = True
        with self.assertRaisesRegex(core.WorkflowError, "PR changed"):
            self.check()
        self.gh.change_head_on_recheck = False
        self.state.reads = 0
        self.state.change_on_second_read = True
        with self.assertRaisesRegex(core.WorkflowError, "Reservation or default"):
            self.check()

    def test_api_errors_fail_closed(self):
        self.gh.error_path = "/issues/comments/1001"
        with self.assertRaises(delivery.ApiError):
            self.check()

    def test_main_requires_checkout_and_exits_one_on_invalid_inputs(self):
        with mock.patch.dict(os.environ, {"PR_NUMBER": "77", "GITHUB_REPOSITORY": self.gh.repo,
                                         "GH_TOKEN": "fake-test-token"}, clear=True), \
                mock.patch("sys.stderr", new_callable=io.StringIO) as stderr:
            self.assertEqual(1, delivery.main())
            self.assertIn("CHECKED_OUT_SHA", stderr.getvalue())
            self.assertNotIn("fake-test-token", stderr.getvalue())

    def test_main_publishes_success_on_exact_pinned_pr_head(self):
        environment = {"PR_NUMBER": "77", "GITHUB_REPOSITORY": self.gh.repo, "GH_TOKEN": "fake-test-token",
                       "CHECKED_OUT_SHA": "a" * 40, "GITHUB_RUN_ID": "12345"}
        with mock.patch.dict(os.environ, environment, clear=True), \
                mock.patch.object(delivery, "GitHub", return_value=self.gh), \
                mock.patch.object(delivery, "State", return_value=self.state), \
                mock.patch.object(delivery, "check_delivery", return_value="PASS: approved") as check, \
                mock.patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(0, delivery.main())
        self.assertEqual(self.gh.head_sha, check.call_args.kwargs["expected_head_sha"])
        self.assertEqual("reviewed-sheet", self.gh.statuses[-1]["context"])
        self.assertEqual("success", self.gh.statuses[-1]["state"])
        self.assertEqual(f"https://github.com/{self.gh.repo}/actions/runs/12345", self.gh.statuses[-1]["target_url"])

    def test_main_publishes_failure_and_returns_one_when_policy_fails(self):
        environment = {"PR_NUMBER": "77", "GITHUB_REPOSITORY": self.gh.repo, "GH_TOKEN": "fake-test-token",
                       "CHECKED_OUT_SHA": "a" * 40}
        with mock.patch.dict(os.environ, environment, clear=True), \
                mock.patch.object(delivery, "GitHub", return_value=self.gh), \
                mock.patch.object(delivery, "State", return_value=self.state), \
                mock.patch.object(delivery, "check_delivery", side_effect=core.WorkflowError("Direct PR blocked")), \
                mock.patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(1, delivery.main())
        self.assertEqual("failure", self.gh.statuses[-1]["state"])

    def test_expected_pr_head_cannot_change_before_check_begins(self):
        with self.assertRaisesRegex(core.WorkflowError, "before verification"):
            delivery.check_delivery(self.gh, self.state, 77, self.root, expected_head_sha="d" * 40)

    def approval_event(self, action="edited", **changes):
        event = {"action": action, "comment": {"id": 1001, "body": "untrusted edited text"},
                 "issue": {"number": 12}, "changes": {"body": {"from": "/work approve " + self.assignment["candidate"]}}}
        event.update(changes)
        return event

    def test_comment_event_resolves_only_exact_registered_comment_and_issue(self):
        for action in ("edited", "deleted"):
            self.assertEqual(77, delivery.resolve_pr_number(self.state, self.approval_event(action)))
        self.assertIsNone(delivery.resolve_pr_number(self.state, self.approval_event(issue={"number": 999})))
        self.assertIsNone(delivery.resolve_pr_number(self.state, self.approval_event(comment={"id": 999})))
        self.assertIsNone(delivery.resolve_pr_number(self.state, self.approval_event(
            comment={"id": 999, "body": "/work approve " + self.assignment["candidate"]})))

    def test_comment_event_missing_registry_skips_and_ambiguous_registry_fails(self):
        self.state.error = delivery.ApiError(404, "Missing")
        self.assertIsNone(delivery.resolve_pr_number(self.state, self.approval_event()))
        self.state.error = None
        self.state.ledger["assignments"].append(copy.deepcopy(self.assignment))
        with self.assertRaisesRegex(core.WorkflowError, "unique"):
            delivery.resolve_pr_number(self.state, self.approval_event())

    def test_explicit_pr_resolution_does_not_read_state(self):
        self.state.error = AssertionError("State must not be read")
        self.assertEqual(77, delivery.resolve_pr_number(self.state, raw_number="77"))
        self.assertEqual(77, delivery.resolve_pr_number(self.state, {"inputs": {"number": "77"}}))
        self.assertEqual(77, delivery.resolve_pr_number(self.state, {"pull_request": {"number": 77}}))
        for number in ("0", "-1", "1; command", True):
            with self.subTest(number=number), self.assertRaises(core.WorkflowError):
                delivery.resolve_pr_number(self.state, raw_number=number)

    def test_main_edited_or_deleted_approval_posts_failure_to_recorded_pr_head(self):
        for action in ("edited", "deleted"):
            event_path = self.root / "event.json"
            event_path.write_text(json.dumps(self.approval_event(action)), encoding="utf-8")
            environment = {"GITHUB_EVENT_PATH": str(event_path), "GITHUB_REPOSITORY": self.gh.repo,
                           "GH_TOKEN": "fake-test-token", "CHECKED_OUT_SHA": "a" * 40}
            # Calling the real delivery checker would need the test source root;
            # wrapping it keeps the entire authorization and API flow real.
            actual_check = delivery.check_delivery
            def local_check(gh, store, number, **kwargs):
                return actual_check(gh, store, number, self.root, **kwargs)
            self.gh.comment["body"] = "approval revoked"
            self.gh.error_path = "/issues/comments/1001" if action == "deleted" else None
            self.gh.error_status = 404 if action == "deleted" else 503
            with self.subTest(action=action), mock.patch.dict(os.environ, environment, clear=True), \
                    mock.patch.object(delivery, "GitHub", return_value=self.gh), \
                    mock.patch.object(delivery, "State", return_value=self.state), \
                    mock.patch.object(delivery, "check_delivery", side_effect=local_check), \
                    mock.patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(1, delivery.main())
                self.assertEqual("failure", self.gh.statuses[-1]["state"])

    def test_main_unbound_comment_skips_without_posting_status(self):
        event_path = self.root / "event.json"
        event_path.write_text(json.dumps(self.approval_event(comment={"id": 9876})), encoding="utf-8")
        environment = {"GITHUB_EVENT_PATH": str(event_path), "GITHUB_REPOSITORY": self.gh.repo,
                       "GH_TOKEN": "fake-test-token", "CHECKED_OUT_SHA": "a" * 40}
        with mock.patch.dict(os.environ, environment, clear=True), \
                mock.patch.object(delivery, "GitHub", return_value=self.gh), \
                mock.patch.object(delivery, "State", return_value=self.state), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(0, delivery.main())
        self.assertIn("SKIP", stdout.getvalue())
        self.assertEqual([], self.gh.statuses)


if __name__ == "__main__":
    unittest.main()
