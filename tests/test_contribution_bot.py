"""Network-free authorization, concurrency and recovery checks for the coordinator."""

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
import urllib.parse
from unittest import mock


TOOLS = pathlib.Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location("contribution_bot_under_test", TOOLS / "contribution_bot.py")
bot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bot)


def csv_text(fields, rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


class MemoryState:
    """Persist callbacks and snapshot files without GitHub or a filesystem branch."""

    def __init__(self, assignments=None):
        self.state = {"schema": 1, "assignments": copy.deepcopy(assignments or [])}
        self.files = {}
        self.mutations = 0
        self.ensures = 0

    def ensure(self):
        self.ensures += 1

    def read(self):
        return "state-sha", copy.deepcopy(self.state)

    def read_file(self, path, ref):
        return json.loads(self.files[path])

    def mutate(self, operation):
        state, files = operation(copy.deepcopy(self.state))
        self.state = copy.deepcopy(state)
        self.files.update(files)
        self.mutations += 1
        return copy.deepcopy(state)


class FakeGitHub:
    """Only the coordinator API surface; unexpected calls fail the test."""

    repo = "Epheria/Ebbtide-Community"

    def __init__(self):
        self.calls = []
        self.comments = []
        self.maintainers = {"maintainer"}
        self.branches = {"main": "base-sha"}
        self.commits = []
        self.prs = {}
        self.pr_creations = 0
        self.dispatches = 0
        self.policy_dispatches = 0
        self.fail_pr_once = False
        self.fail_check_once = False
        self.fail_policy_once = False

    def is_maintainer(self, login):
        return login.casefold() in self.maintainers

    def comment(self, issue, text):
        self.comments.append((issue, text))

    def commit_files(self, parent, files, message):
        sha = f"commit-{len(self.commits) + 1}"
        self.commits.append((sha, parent, copy.deepcopy(files)))
        return sha

    def api(self, path, method="GET", data=None):
        self.calls.append((path, method, copy.deepcopy(data)))
        if path == "" and method == "GET":
            return {"default_branch": "main"}
        if path.startswith("/git/ref/heads/") and method == "GET":
            branch = urllib.parse.unquote(path.removeprefix("/git/ref/heads/"))
            if branch not in self.branches:
                raise bot.ApiError(404, "Not Found")
            return {"object": {"sha": self.branches[branch]}}
        if path == "/git/refs" and method == "POST":
            branch = data["ref"].removeprefix("refs/heads/")
            if branch in self.branches:
                raise bot.ApiError(422, "Reference already exists")
            self.branches[branch] = data["sha"]
            return {"ref": data["ref"]}
        if path.startswith("/contents/") and method == "GET":
            item_path, ref = path.removeprefix("/contents/").split("?ref=", 1)
            ref = urllib.parse.unquote(ref)
            files = next((files for sha, _, files in self.commits if sha == ref), {})
            if item_path not in files:
                raise bot.ApiError(404, "File not found")
            return {"content": base64.b64encode(files[item_path].encode("utf-8")).decode()}
        if path.startswith("/pulls?state=open&head="):
            head = urllib.parse.unquote(path.split("head=", 1)[1]).split(":", 1)[1]
            return [copy.deepcopy(pr) for pr in self.prs.values()
                    if pr["state"] == "open" and pr["head"]["ref"] == head]
        if path == "/pulls" and method == "POST":
            if self.fail_pr_once:
                self.fail_pr_once = False
                raise bot.ApiError(503, "Temporary failure")
            self.pr_creations += 1
            number = 100 + self.pr_creations
            pr = {"number": number, "state": "open", "merged_at": None,
                  "html_url": f"https://github.com/{self.repo}/pull/{number}",
                  "head": {"ref": data["head"]}}
            self.prs[number] = pr
            return copy.deepcopy(pr)
        if path.startswith("/pulls/") and method == "GET":
            return copy.deepcopy(self.prs[int(path.rsplit("/", 1)[1])])
        if path == "/actions/workflows/check.yml/dispatches" and method == "POST":
            if self.fail_check_once:
                self.fail_check_once = False
                raise bot.ApiError(503, "Check dispatch temporarily unavailable")
            self.dispatches += 1
            return None
        if path == "/actions/workflows/delivery-policy.yml/dispatches" and method == "POST":
            if self.fail_policy_once:
                self.fail_policy_once = False
                raise bot.ApiError(503, "Policy dispatch temporarily unavailable")
            self.policy_dispatches += 1
            return None
        raise AssertionError(f"Unexpected GitHub API call: {method} {path}")


class ContributionBotTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name)
        self.root_patch = mock.patch.object(bot, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.addCleanup(mock.patch.stopall)
        self.environment = mock.patch.dict(os.environ, {"CHECKED_OUT_SHA": "base-sha"})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.source_rows = [{"key": "a", "en": "Ready {0}.", "ko": ""},
                            {"key": "b", "en": "Hold.", "ko": ""}]
        self.source_path = self.root / "localization/source/strings/TacticalHUD.csv"
        self.source_path.parent.mkdir(parents=True)
        self.source_path.write_text(csv_text(["key", "en", "ko"], self.source_rows), encoding="utf-8")
        source = bot.get_source(self.root, "ui", "TacticalHUD")
        self.assignment = {"issue": 12, "kind": "ui", "locale": "ja", "table": "TacticalHUD",
                           "contributor": "Volunteer", "reviewer": "Reviewer", "spreadsheet_id": "s" * 44,
                           "tab": "Japanese", "keys": ["a"], "source_hash": bot.source_hash(source),
                           "status": "assigned"}
        self.issue = {"number": 12, "state": "open", "body": self.issue_body()}
        self.gh = FakeGitHub()
        self.store = MemoryState([self.assignment])
        self.sheet_text = self.sheet()
        self.fetch = mock.patch.object(bot, "fetch_sheet", side_effect=lambda _: self.sheet_text).start()
        # No test is allowed to accidentally reach the real network.
        self.network = mock.patch.object(bot.urllib.request, "urlopen",
                                         side_effect=AssertionError("Unexpected network request")).start()

    def issue_body(self, **changes):
        values = {"Kind": "ui", "Locale": "ja", "Table or voice role": "TacticalHUD",
                  "Contributor": "Volunteer", "Reviewer": "Reviewer",
                  "Spreadsheet URL": "https://docs.google.com/spreadsheets/d/" + "s" * 44 + "/edit",
                  "Sheet tab": "Japanese", "First key": "a", "Last key": "a"}
        values.update(changes)
        return "\n\n".join(f"### {key}\n\n{value}" for key, value in values.items())

    def sheet(self, translated="準備完了 {0}。"):
        return csv_text(["key", "en", "translation", "status"], [
            {"key": "a", "en": "Ready {0}.", "translation": translated, "status": ""},
            {"key": "b", "en": "Hold.", "translation": "", "status": ""}])

    def run_command(self, command, actor="maintainer", digest=None):
        return bot.process(self.gh, self.store, self.issue, actor, command, digest, comment_id=42)

    def preview(self):
        self.run_command("preview", "Volunteer")
        return self.store.state["assignments"][0]["candidate"]

    def test_unauthorized_assign_has_no_network_or_state_side_effect(self):
        self.store = MemoryState()
        with self.assertRaisesRegex(bot.WorkflowError, "Only repository maintainers"):
            self.run_command("assign", "intruder")
        self.assertEqual([], self.store.state["assignments"])
        self.assertEqual(0, self.store.mutations)
        self.network.assert_not_called()

    def test_assign_validates_existing_users_and_freezes_source_order_range(self):
        self.store = MemoryState()
        self.issue["body"] = self.issue_body(**{"Last key": "b"})
        self.network.side_effect = None
        self.network.return_value = mock.MagicMock()
        parse_issue = bot.assignment_from_issue
        with mock.patch.object(bot, "assignment_from_issue", side_effect=lambda issue: parse_issue(issue, self.root)):
            self.run_command("assign")
        item = self.store.state["assignments"][0]
        self.assertEqual(["a", "b"], item["keys"])
        self.assertEqual(self.assignment["source_hash"], item["source_hash"])
        self.assertEqual({"Volunteer", "Reviewer"},
                         {call.args[0].full_url.rsplit("/", 1)[1] for call in self.network.call_args_list})

    def test_issue_url_login_and_range_validation_fail_closed(self):
        bad = [{"Spreadsheet URL": "https://docs.google.com.evil.example/spreadsheets/d/" + "s" * 44},
               {"Spreadsheet URL": "https://user@docs.google.com/spreadsheets/d/" + "s" * 44},
               {"Spreadsheet URL": "http://docs.google.com/spreadsheets/d/" + "s" * 44},
               {"Spreadsheet URL": "https://docs.google.com:443/spreadsheets/d/" + "s" * 44},
               {"Reviewer": "VOLUNTEER"}, {"First key": "b", "Last key": "a"},
               {"First key": "future_id"}, {"Table or voice role": "../TacticalHUD"}]
        for change in bad:
            issue = {**self.issue, "body": self.issue_body(**change)}
            with self.subTest(change=change), self.assertRaises(bot.WorkflowError):
                bot.assignment_from_issue(issue, self.root)

    def test_unauthorized_preview_cannot_read_sheet_or_replace_candidate(self):
        with self.assertRaisesRegex(bot.WorkflowError, "Only the assigned"):
            self.run_command("preview", "intruder")
        self.fetch.assert_not_called()
        self.assertEqual(0, self.store.mutations)

    def test_preview_uses_frozen_assignment_even_if_issue_body_is_edited(self):
        self.issue["body"] = self.issue_body(**{"Reviewer": "intruder", "Sheet tab": "Other"})
        digest = self.preview()
        snapshot = self.store.read_file(f"snapshots/12/{digest}.json", bot.STATE_BRANCH)
        self.assertEqual("Reviewer", snapshot["assignment"]["reviewer"])
        self.assertEqual("Japanese", self.fetch.call_args.args[0]["tab"])
        self.assertIn(digest, self.store.files[f"snapshots/12/{digest}.md"])

    def test_maintainer_and_reviewer_can_preview_with_case_insensitive_logins(self):
        for actor in ("maintainer", "rEvIeWeR", "vOlUnTeEr"):
            with self.subTest(actor=actor):
                self.run_command("preview", actor)
        self.assertEqual(3, self.fetch.call_count)

    def test_only_designated_reviewer_can_approve_even_if_actor_is_maintainer(self):
        digest = self.preview()
        self.fetch.reset_mock()
        for actor in ("Volunteer", "maintainer", "intruder"):
            with self.subTest(actor=actor), self.assertRaisesRegex(bot.WorkflowError, "designated reviewer"):
                self.run_command("approve", actor, digest)
        self.fetch.assert_not_called()
        self.assertEqual(0, self.gh.pr_creations)

    def test_wrong_or_partial_digest_does_not_fetch_or_create_pr(self):
        digest = self.preview()
        self.fetch.reset_mock()
        for invalid in (None, digest[:12], "f" * 64, digest.upper()):
            with self.subTest(digest=invalid), self.assertRaisesRegex(bot.WorkflowError, "64-character"):
                self.run_command("approve", "Reviewer", invalid)
        self.fetch.assert_not_called()
        self.assertEqual(0, self.gh.pr_creations)

    def test_sheet_change_after_preview_requires_new_review(self):
        digest = self.preview()
        self.sheet_text = self.sheet("別の表現 {0}。")
        with self.assertRaisesRegex(bot.WorkflowError, "changed since preview"):
            self.run_command("approve", "Reviewer", digest)
        self.assertEqual(0, self.gh.pr_creations)
        self.assertEqual("assigned", self.store.state["assignments"][0]["status"])

    def test_target_change_after_preview_cannot_be_overwritten(self):
        digest = self.preview()
        target = self.root / "localization/translations/ja/TacticalHUD.csv"
        target.parent.mkdir(parents=True)
        target.write_text(self.sheet(), encoding="utf-8")
        before = target.read_bytes()
        with self.assertRaises(bot.WorkflowError):
            self.run_command("approve", "Reviewer", digest)
        self.assertEqual(before, target.read_bytes())
        self.assertEqual(0, self.gh.pr_creations)

    def test_source_change_after_preview_cannot_import_old_text(self):
        digest = self.preview()
        self.source_rows[1]["en"] = "New order."
        self.source_path.write_text(csv_text(["key", "en", "ko"], self.source_rows), encoding="utf-8")
        with self.assertRaisesRegex(bot.WorkflowError, "source changed"):
            self.run_command("approve", "Reviewer", digest)
        self.assertEqual(0, self.gh.pr_creations)

    def test_tampered_stored_snapshot_is_rejected_before_sheet_download(self):
        digest = self.preview()
        path = f"snapshots/12/{digest}.json"
        snapshot = json.loads(self.store.files[path])
        snapshot["rows"][0]["translation"] = "tampered {0}"
        self.store.files[path] = json.dumps(snapshot)
        self.fetch.reset_mock()
        with self.assertRaisesRegex(bot.WorkflowError, "changed since preview"):
            self.run_command("approve", "Reviewer", digest)
        self.fetch.assert_not_called()
        self.assertEqual(0, self.gh.pr_creations)

    def test_approval_creates_one_scoped_commit_pr_and_explicit_check_dispatch(self):
        digest = self.preview()
        result = self.run_command("approve", "rEvIeWeR", digest)
        item = self.store.state["assignments"][0]
        self.assertEqual("pr_open", item["status"])
        self.assertEqual(42, item["approval_comment"])
        self.assertIn("/pull/101", result)
        self.assertEqual(1, self.gh.pr_creations)
        self.assertEqual(1, self.gh.dispatches)
        self.assertEqual(1, self.gh.policy_dispatches)
        policy_calls = [data for path, _, data in self.gh.calls
                        if path == "/actions/workflows/delivery-policy.yml/dispatches"]
        self.assertEqual([{"ref": "main", "inputs": {"number": "101"}}], policy_calls)
        self.assertEqual(1, len(self.gh.commits))
        files = self.gh.commits[0][2]
        self.assertEqual(["localization/translations/ja/TacticalHUD.csv"], list(files))
        self.assertIn("準備完了 {0}。", next(iter(files.values())))
        self.assertFalse(any(path.endswith("/merge") for path, _, _ in self.gh.calls))

    def test_repeated_approval_reuses_recorded_pr_without_another_commit(self):
        digest = self.preview()
        self.run_command("approve", "Reviewer", digest)
        result = self.run_command("approve", "Reviewer", digest)
        self.assertIn("already exists", result)
        self.assertEqual(1, self.gh.pr_creations)
        self.assertEqual(1, len(self.gh.commits))
        self.assertEqual(2, self.gh.dispatches)
        self.assertEqual(2, self.gh.policy_dispatches)

    def test_retry_after_pr_api_failure_reuses_existing_bot_branch(self):
        digest = self.preview()
        self.gh.fail_pr_once = True
        with self.assertRaises(bot.ApiError):
            self.run_command("approve", "Reviewer", digest)
        self.assertEqual("reviewed", self.store.state["assignments"][0]["status"])
        self.assertEqual(1, len(self.gh.commits))
        self.run_command("approve", "Reviewer", digest)
        self.assertEqual(1, len(self.gh.commits))
        self.assertEqual(1, self.gh.pr_creations)

    def test_retry_rejects_existing_bot_branch_changed_after_initial_export(self):
        digest = self.preview()
        self.gh.fail_pr_once = True
        with self.assertRaises(bot.ApiError):
            self.run_command("approve", "Reviewer", digest)
        files = self.gh.commits[0][2]
        path = "localization/translations/ja/TacticalHUD.csv"
        files[path] = files[path].replace("準備完了", "改変された文章")
        with self.assertRaisesRegex(bot.WorkflowError, "branch differs"):
            self.run_command("approve", "Reviewer", digest)
        self.assertEqual(0, self.gh.pr_creations)
        self.assertEqual(0, self.gh.dispatches)

    def test_retry_after_check_or_policy_dispatch_failure_recovers_recorded_pr(self):
        for failure in ("fail_check_once", "fail_policy_once"):
            with self.subTest(failure=failure):
                self.gh = FakeGitHub()
                self.store = MemoryState([self.assignment])
                digest = self.preview()
                setattr(self.gh, failure, True)
                with self.assertRaises(bot.ApiError):
                    self.run_command("approve", "Reviewer", digest)
                self.assertEqual("pr_open", self.store.state["assignments"][0]["status"])
                self.run_command("approve", "Reviewer", digest)
                self.assertEqual(1, self.gh.pr_creations)
                self.assertEqual(1, len(self.gh.commits))
                self.assertGreaterEqual(self.gh.dispatches, 1)
                self.assertEqual(1, self.gh.policy_dispatches)

    def test_sync_open_pr_redispatches_checks_without_another_export_or_sheet_read(self):
        digest = self.preview()
        self.run_command("approve", "Reviewer", digest)
        self.fetch.reset_mock()
        self.run_command("sync")
        self.fetch.assert_not_called()
        self.assertEqual("pr_open", self.store.state["assignments"][0]["status"])
        self.assertEqual(2, self.gh.dispatches)
        self.assertEqual(2, self.gh.policy_dispatches)
        self.assertEqual(1, self.gh.pr_creations)
        self.assertEqual(1, len(self.gh.commits))

    def test_advanced_default_branch_stops_pr_creation(self):
        digest = self.preview()
        self.gh.branches["main"] = "new-default-sha"
        with self.assertRaisesRegex(bot.WorkflowError, "Default branch advanced"):
            self.run_command("approve", "Reviewer", digest)
        self.assertEqual(0, len(self.gh.commits))
        self.assertEqual(0, self.gh.pr_creations)

    def test_unauthorized_release_and_sync_leave_reservation_active(self):
        for command in ("release", "sync"):
            with self.subTest(command=command), self.assertRaisesRegex(bot.WorkflowError, "Only maintainers"):
                self.run_command(command, "Volunteer")
        self.assertEqual("assigned", self.store.state["assignments"][0]["status"])
        self.assertEqual(0, self.store.mutations)

    def test_open_pr_blocks_release_then_closed_unmerged_pr_releases(self):
        digest = self.preview()
        self.run_command("approve", "Reviewer", digest)
        with self.assertRaisesRegex(bot.WorkflowError, "Close the unmerged PR"):
            self.run_command("release")
        self.gh.prs[101]["state"] = "closed"
        self.run_command("sync")
        self.assertEqual("released", self.store.state["assignments"][0]["status"])

    def test_merged_task_does_not_block_new_nonoverlapping_reservations(self):
        digest = self.preview()
        self.run_command("approve", "Reviewer", digest)
        self.gh.prs[101].update(state="closed", merged_at="2026-10-20T00:00:00Z")
        self.run_command("sync")
        next_assignment = {**self.assignment, "issue": 13, "keys": ["b"]}
        source = bot.get_source(self.root, "ui", "TacticalHUD")
        reserved = bot.reserve(self.store.state, next_assignment, source)
        self.assertEqual(2, len(reserved["assignments"]))

    def test_released_issue_cannot_create_a_second_ambiguous_registry_entry(self):
        self.run_command("release")
        source = bot.get_source(self.root, "ui", "TacticalHUD")
        with self.assertRaises(bot.WorkflowError):
            bot.reserve(self.store.state, self.assignment, source)

    def test_event_parser_ignores_pr_comments_and_embedded_or_edited_commands(self):
        event_path = self.root / "event.json"
        environment = {"GITHUB_EVENT_PATH": str(event_path), "GITHUB_REPOSITORY": self.gh.repo,
                       "GH_TOKEN": "fake-test-token", "GITHUB_ACTOR": "maintainer"}
        base = {"action": "created", "issue": {"number": 12},
                "comment": {"id": 9, "body": "/work preview", "user": {"login": "intruder"}}}
        events = [copy.deepcopy(base) for _ in range(4)]
        events[0]["issue"]["pull_request"] = {"url": "https://example.invalid"}
        events[1]["comment"]["body"] = "Please run /work preview"
        events[2]["comment"]["body"] = "/work preview\n/work release"
        events[3]["action"] = "edited"
        with mock.patch.dict(os.environ, environment), mock.patch.object(bot, "GitHub", return_value=self.gh), \
                mock.patch.object(bot, "State", return_value=self.store), mock.patch.object(bot, "process") as process:
            for event in events:
                event_path.write_text(json.dumps(event), encoding="utf-8")
                bot.main()
            process.assert_not_called()
        self.assertEqual(0, self.store.ensures)


class StateCompareAndSwapTests(unittest.TestCase):
    def test_conflict_reloads_state_and_reruns_operation_instead_of_replaying_a_write(self):
        class RacingGitHub:
            def __init__(self):
                self.sha = "original"
                self.states = {"original": {"schema": 1, "assignments": [], "count": 0},
                               "competitor": {"schema": 1, "assignments": [], "count": 10}}
                self.reads = 0
                self.patches = 0
                self.commits = {}

            def api(self, path, method="GET", data=None):
                if path == "/git/ref/heads/" + bot.STATE_BRANCH:
                    self.reads += 1
                    return {"object": {"sha": self.sha}}
                if path.startswith("/contents/registry.json?ref="):
                    ref = urllib.parse.unquote(path.rsplit("=", 1)[1])
                    return {"content": base64.b64encode(json.dumps(self.states[ref]).encode()).decode()}
                if path == "/git/refs/heads/" + bot.STATE_BRANCH and method == "PATCH":
                    self.patches += 1
                    if self.patches == 1:
                        self.sha = "competitor"
                        raise bot.ApiError(422, "Not a fast forward")
                    self.sha = data["sha"]
                    return {}
                raise AssertionError((path, method))

            def commit_files(self, parent, files, message):
                sha = f"candidate-{len(self.commits)}"
                self.commits[sha] = parent
                self.states[sha] = json.loads(files["registry.json"])
                return sha

        gh = RacingGitHub()
        observed = []

        def increment(state):
            observed.append(state["count"])
            state["count"] += 1
            return state, {}

        final = bot.State(gh).mutate(increment)
        self.assertEqual([0, 10], observed)
        self.assertEqual(11, final["count"])
        self.assertEqual(2, gh.reads)
        self.assertEqual(2, gh.patches)
        self.assertEqual("competitor", gh.commits[gh.sha])


if __name__ == "__main__":
    unittest.main()
