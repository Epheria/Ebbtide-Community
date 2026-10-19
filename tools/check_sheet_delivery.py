"""Delivery policy executed exclusively from the trusted default branch.

Pull-request code is never downloaded or executed. Translation deliveries must
exactly match an assigned, independently reviewed and frozen sheet snapshot. The
only write is publishing the check result to the inspected PR commit's status.
"""

from __future__ import annotations

import base64
import binascii
import json
import os
import pathlib
import re
import sys
import urllib.parse

from contribution_bot import ApiError, GitHub, State
from contribution_core import WorkflowError, build_export, snapshot_hash


ROOT = pathlib.Path(__file__).resolve().parent.parent
_DELIVERY = re.compile(r"^(?:localization|voice)/translations/[^/]+/[^/]+\.csv$")
_HASH = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_ROOTS = ("localization/translations/", "voice/translations/")


def _positive_integer(value, name):
    if type(value) is not int or value <= 0:
        raise WorkflowError(f"{name} must be a positive integer")
    return value


def _changed_files(gh, number, pr):
    count = pr.get("changed_files")
    if count is not None and (type(count) is not int or not 0 <= count <= 3000):
        raise WorkflowError("PR file list is too large or invalid")
    files = []
    for page in range(1, 32):
        batch = gh.api(f"/pulls/{number}/files?per_page=100&page={page}")
        if not isinstance(batch, list) or len(batch) > 100:
            raise WorkflowError("GitHub returned an invalid PR file list")
        files.extend(batch)
        if len(files) > 3000:
            raise WorkflowError("PR has too many files to verify completely")
        if len(batch) < 100:
            break
    else:
        raise WorkflowError("PR file pagination did not finish")
    if count is not None and count != len(files):
        raise WorkflowError("PR changed during file-list retrieval; rerun the policy check")
    names = [item.get("filename") if isinstance(item, dict) else None for item in files]
    if any(not isinstance(name, str) or not name for name in names) or len(set(names)) != len(names):
        raise WorkflowError("GitHub returned invalid or duplicate changed paths")
    return files


def _translation_paths(files):
    deliveries = []
    for item in files:
        # A rename out of the controlled roots must not silently bypass policy.
        for field in ("filename", "previous_filename"):
            path = item.get(field, "")
            if not isinstance(path, str):
                raise WorkflowError("GitHub returned an invalid changed path")
            if path.startswith(_ROOTS) and path.casefold().endswith(".csv"):
                if not _DELIVERY.fullmatch(path):
                    raise WorkflowError("Unsupported translation CSV path; use a work-order delivery")
                deliveries.append(path)
    return deliveries


def _live_approval(gh, assignment, digest):
    reviewer = assignment.get("reviewer")
    contributor = assignment.get("contributor")
    approved = assignment.get("approved_by")
    if not all(isinstance(value, str) and value for value in (reviewer, contributor, approved)):
        raise WorkflowError("Reservation has no recorded independent reviewer approval")
    if approved.casefold() != reviewer.casefold() or reviewer.casefold() == contributor.casefold():
        raise WorkflowError("Only the designated independent reviewer can approve the snapshot")
    comment_id = assignment.get("approval_comment")
    if comment_id is None:
        # Workflow-dispatch approvals have no comment; the trusted coordinator
        # separately requires maintainer authorization before recording them.
        return
    _positive_integer(comment_id, "approval comment")
    comment = gh.api(f"/issues/comments/{comment_id}")
    if (not isinstance(comment, dict)
            or comment.get("user", {}).get("login", "").casefold() != reviewer.casefold()
            or comment.get("body", "").strip() != f"/work approve {digest}"
            or comment.get("issue_url") != f"https://api.github.com/repos/{gh.repo}/issues/{assignment['issue']}"):
        raise WorkflowError("Recorded approval comment was edited, moved or is not from the assigned reviewer")


def _head_csv(gh, path, head_sha):
    result = gh.api("/contents/" + urllib.parse.quote(path, safe="/")
                    + "?ref=" + urllib.parse.quote(head_sha, safe=""))
    if not isinstance(result, dict) or result.get("type") != "file" or result.get("encoding") != "base64":
        raise WorkflowError("Translation delivery must be a normal UTF-8 file")
    content = result.get("content")
    if not isinstance(content, str) or len(content) > 8 * 1024 * 1024:
        raise WorkflowError("Translation delivery content is missing or too large")
    try:
        return base64.b64decode("".join(content.split()), validate=True).decode("utf-8")
    except (binascii.Error, UnicodeError) as error:
        raise WorkflowError("Translation delivery is not valid UTF-8 content") from error


def _regular_blob(gh, path, head_sha):
    # Contents API can dereference symlinks. Check the actual Git object mode as
    # well, so a link to another CSV cannot impersonate the reviewed file.
    tree = gh.api("/git/trees/" + head_sha + "?recursive=1")
    if not isinstance(tree, dict) or tree.get("truncated") is not False or not isinstance(tree.get("tree"), list):
        raise WorkflowError("Cannot verify the complete delivery Git tree")
    entries = [entry for entry in tree["tree"] if entry.get("path") == path]
    if len(entries) != 1 or entries[0].get("type") != "blob" or entries[0].get("mode") not in {"100644", "100755"}:
        raise WorkflowError("Translation delivery must be a regular Git blob, never a symlink")


def _base_identity(pr):
    base = pr.get("base", {})
    return (base.get("ref"), base.get("repo", {}).get("full_name", "").casefold(), base.get("sha"))


def check_delivery(gh, state_store, pr_number, source_root=ROOT, *, checked_out_sha=None,
                   expected_head_sha=None):
    """Return a pass explanation or raise WorkflowError; all API calls are GET."""
    number = _positive_integer(pr_number, "PR number")
    pr = gh.api(f"/pulls/{number}")
    if not isinstance(pr, dict) or pr.get("number") != number:
        raise WorkflowError("GitHub returned an invalid pull request")
    if expected_head_sha is not None and pr.get("head", {}).get("sha") != expected_head_sha:
        raise WorkflowError("PR head changed before verification; rerun the policy check")
    repository = gh.api("")
    default_branch = repository.get("default_branch")
    base_identity = _base_identity(pr)
    if (not isinstance(default_branch, str) or not default_branch
            or base_identity[0] != default_branch or base_identity[1] != gh.repo.casefold()):
        # A commit status is shared by every PR with the same head SHA. Even a
        # nontranslation PR must target main, or a different-base diff could
        # publish a green result for a delivery that actually fails on main.
        raise WorkflowError("Delivery policy only verifies PRs targeting this repository's default branch")
    files = _changed_files(gh, number, pr)
    deliveries = _translation_paths(files)
    if not deliveries:
        latest = gh.api(f"/pulls/{number}")
        if (latest.get("head", {}).get("sha") != pr.get("head", {}).get("sha")
                or _base_identity(latest) != base_identity
                or gh.api("").get("default_branch") != default_branch):
            raise WorkflowError("PR head or base changed during file-list verification; rerun the policy check")
        return "PASS: no controlled translation CSV delivery in this pull request"
    if len(files) != 1 or len(deliveries) != 1 or files[0].get("status") not in {"added", "modified"}:
        raise WorkflowError("A sheet delivery must change exactly one translation CSV and no other files")
    if pr.get("state") != "open":
        raise WorkflowError("Translation delivery PR is no longer open")
    try:
        state_sha, ledger = state_store.read()
    except ApiError as error:
        if error.status == 404:
            raise WorkflowError("No reservation registry exists; start with a maintainer-assigned work-order issue") from None
        raise
    if not isinstance(ledger, dict) or not isinstance(ledger.get("assignments"), list):
        raise WorkflowError("Reservation registry is invalid")
    matches = [item for item in ledger["assignments"] if isinstance(item, dict) and item.get("pr") == number]
    if len(matches) != 1 or matches[0].get("status") != "pr_open":
        raise WorkflowError("Translation PR has no unique active work-order reservation; use the reviewed sheet workflow")
    assignment = matches[0]
    issue = _positive_integer(assignment.get("issue"), "work-order issue")
    digest = assignment.get("candidate")
    if not isinstance(digest, str) or not _HASH.fullmatch(digest):
        raise WorkflowError("Reservation has no valid reviewed snapshot digest")
    _live_approval(gh, assignment, digest)
    head = pr.get("head", {})
    head_sha = head.get("sha")
    branch = assignment.get("branch")
    expected_branch = f"community/sheet-{issue}-{digest[:12]}"
    if (head.get("repo", {}).get("full_name", "").casefold() != gh.repo.casefold()
            or branch != expected_branch or head.get("ref") != branch
            or not isinstance(head_sha, str) or not _COMMIT.fullmatch(head_sha)):
        raise WorkflowError("PR head must be the recorded delivery branch in this repository")
    default_ref = "/git/ref/heads/" + urllib.parse.quote(default_branch, safe="")
    default_sha = gh.api(default_ref)["object"]["sha"]
    if checked_out_sha is not None and checked_out_sha != default_sha:
        raise WorkflowError("Default branch advanced; rerun with a fresh trusted checkout")
    snapshot = state_store.read_file(f"snapshots/{issue}/{digest}.json", state_sha)
    if not isinstance(snapshot, dict) or snapshot.get("digest") != digest or snapshot_hash(snapshot) != digest:
        raise WorkflowError("Saved snapshot digest is invalid")
    # Passing the live ledger assignment makes core compare every immutable
    # reservation field with the snapshot; PR bodies never provide authority.
    relative, expected_csv = build_export(source_root, assignment, snapshot)
    if relative != files[0]["filename"]:
        raise WorkflowError("Changed translation path is outside the assigned snapshot scope")
    _regular_blob(gh, relative, head_sha)
    if _head_csv(gh, relative, head_sha) != expected_csv:
        raise WorkflowError("PR translation differs from the independently approved snapshot")
    # Changes to the reservation, approval or PR while this read-only check ran
    # require a fresh run, rather than attaching a pass to a moving candidate.
    latest_pr = gh.api(f"/pulls/{number}")
    if (latest_pr.get("head", {}).get("sha") != head_sha or latest_pr.get("state") != "open"
            or _base_identity(latest_pr) != base_identity):
        raise WorkflowError("PR changed during verification; rerun the policy check")
    if (state_store.read()[0] != state_sha or gh.api(default_ref)["object"]["sha"] != default_sha
            or gh.api("").get("default_branch") != default_branch):
        raise WorkflowError("Reservation or default branch changed during verification; rerun")
    # The approval itself can be edited without changing the state branch.
    _live_approval(gh, assignment, digest)
    return f"PASS: PR #{number} exactly matches reviewed snapshot {digest} for work order #{issue}"


def _publish_status(gh, head_sha, success):
    """Publish only this check's outcome, attached to the exact inspected head."""
    data = {"context": "reviewed-sheet", "state": "success" if success else "failure",
            "description": "Sheet delivery policy passed" if success else "Sheet delivery policy failed; see workflow logs"}
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    if re.fullmatch(r"[1-9][0-9]*", run_id):
        data["target_url"] = f"https://github.com/{gh.repo}/actions/runs/{run_id}"
    gh.api("/statuses/" + head_sha, "POST", data)


def resolve_pr_number(state_store, event=None, raw_number=None):
    """Resolve explicit/PR events or a recorded approval's edited/deleted event.

    Comment text never supplies a PR number. A comment event can recheck only
    the PR bound to that exact issue and comment ID in the trusted registry.
    """
    event = event or {}
    number = (raw_number or event.get("pull_request", {}).get("number")
              or event.get("inputs", {}).get("number") or event.get("inputs", {}).get("pr_number"))
    if number:
        if isinstance(number, bool) or not re.fullmatch(r"[1-9][0-9]*", str(number)):
            raise WorkflowError("Set PR_NUMBER to the pull request number")
        return int(number)
    if event.get("action") not in {"edited", "deleted"} or "comment" not in event or "issue" not in event:
        raise WorkflowError("Set PR_NUMBER to the pull request number")
    comment_id = _positive_integer(event["comment"].get("id"), "event comment")
    issue = _positive_integer(event["issue"].get("number"), "event issue")
    try:
        _, ledger = state_store.read()
    except ApiError as error:
        if error.status == 404:
            return None
        raise
    if not isinstance(ledger, dict) or not isinstance(ledger.get("assignments"), list):
        raise WorkflowError("Reservation registry is invalid")
    matches = [item for item in ledger["assignments"] if isinstance(item, dict)
               and item.get("approval_comment") == comment_id and item.get("issue") == issue]
    if not matches or len(matches) == 1 and not matches[0].get("pr"):
        return None
    if len(matches) != 1:
        raise WorkflowError("Approval comment has no unique registered PR")
    return _positive_integer(matches[0]["pr"], "registered PR")


def main():
    gh, status_head = None, None
    try:
        raw_number = os.environ.get("PR_NUMBER")
        event = None
        if not raw_number:
            event = json.loads(pathlib.Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
        gh = GitHub(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"])
        checkout = os.environ.get("CHECKED_OUT_SHA")
        if not checkout or not _COMMIT.fullmatch(checkout):
            raise WorkflowError("CHECKED_OUT_SHA must identify the trusted default-branch checkout")
        store = State(gh)
        number = resolve_pr_number(store, event, raw_number)
        if number is None:
            print("SKIP: edited/deleted comment is not bound to a registered delivery PR")
            return 0
        initial_pr = gh.api(f"/pulls/{number}")
        status_head = initial_pr.get("head", {}).get("sha")
        if not isinstance(status_head, str) or not _COMMIT.fullmatch(status_head):
            status_head = None
            raise WorkflowError("PR head commit is invalid")
        result = check_delivery(gh, store, number, checked_out_sha=checkout,
                                expected_head_sha=status_head)
        _publish_status(gh, status_head, True)
        print(result)
        return 0
    except (WorkflowError, OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(f"FAIL: sheet delivery policy: {error}", file=sys.stderr)
        if gh is not None and status_head is not None:
            try:
                _publish_status(gh, status_head, False)
            except (WorkflowError, OSError, ValueError, KeyError, TypeError, AttributeError) as status_error:
                print(f"FAIL: could not publish reviewed-sheet failure status: {status_error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
