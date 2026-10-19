"""Pure validation for private Drive recording receipts and manifest-only delivery.

Audio bytes are never downloaded here. Receipts describe owner-frozen Drive copies;
their authenticity and listening review belong to the private Drive coordinator.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
import pathlib
import re
from datetime import datetime

from contribution_core import WorkflowError, _canonical, _csv_rows, _safe_path

OUTBOX_FIELDS = ["Work order", "Take file", "Drive snapshot", "SHA256", "Bytes",
                 "MIME type", "Revision", "Submitted", "Script SHA256"]
ACTIVE = {"assigned", "reviewed", "pr_open"}
TERMINAL = {"completed", "released", "cancelled", "rejected", "stale"}
MAX_KEYS = 200
MAX_BYTES = 250 * 1024 * 1024
HASH = re.compile(r"^[0-9a-f]{64}$")
STEM = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
LANG = re.compile(r"^[a-z]{2,3}(?:-(?:[A-Z]{2}|[A-Za-z]{4}))?$")
USER = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
BOUND_FIELDS = ("issue", "kind", "locale", "table", "casting_slot", "recording_version",
                "contributor", "reviewer", "spreadsheet_id", "tab", "keys", "script_hash")


def _digest(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def scope(assignment):
    if not isinstance(assignment, dict) or assignment.get("kind") != "voice-audio":
        raise WorkflowError("kind must be voice-audio")
    for key in ("table", "casting_slot"):
        if not isinstance(assignment.get(key), str) or not STEM.fullmatch(assignment[key]):
            raise WorkflowError(f"{key} must be a safe ASCII name")
    if not isinstance(assignment.get("locale"), str) or not LANG.fullmatch(assignment["locale"]):
        raise WorkflowError("locale is invalid")
    return assignment["locale"], assignment["table"], assignment["casting_slot"]


def get_source(root, locale, table):
    """Read exact role IDs, context and approved spoken text from trusted Git files."""
    scope({"kind": "voice-audio", "locale": locale, "table": table, "casting_slot": "check"})
    path = _safe_path(root, pathlib.Path("voice/scripts") / f"{table}.csv")
    try:
        rows = _csv_rows(path.read_text(encoding="utf-8-sig"),
                         ["file", "situation", "tone", "line", "current_voices"])
    except (OSError, UnicodeError) as error:
        raise WorkflowError(f"cannot read voice script: {error}") from error
    if not rows:
        raise WorkflowError("voice source is empty")
    translated = {}
    if locale != "en":
        target = _safe_path(root, pathlib.Path("voice/translations") / locale / f"{table}.csv")
        try:
            translated_rows = _csv_rows(target.read_text(encoding="utf-8-sig"),
                                        ["key", "en", "translation", "status"])
        except (OSError, UnicodeError) as error:
            raise WorkflowError("localized recordings require a committed reviewed voice translation") from error
        for row in translated_rows:
            if row["key"] in translated:
                raise WorkflowError("voice translation has duplicate keys")
            translated[row["key"]] = row
    result, seen = [], set()
    for row in rows:
        key = row["file"]
        if not STEM.fullmatch(key) or key in seen:
            raise WorkflowError("source contains duplicate or unsafe take IDs")
        seen.add(key)
        spoken, ready = row["line"], bool(row["line"].strip())
        ready = ready and "wording not confirmed" not in row["situation"].casefold()
        if locale != "en":
            target = translated.get(key)
            approved = bool(target and target["en"] == row["line"]
                            and target["translation"].strip() and target["status"] == "")
            spoken = target["translation"] if target else ""
            ready = ready and approved
        result.append({"key": key, "en": row["line"], "situation": row["situation"],
                       "tone": row["tone"], "current_voices": row["current_voices"],
                       "spoken": spoken, "ready": ready})
    if set(translated) - seen:
        raise WorkflowError("voice translation contains unknown source IDs")
    return result


def script_hash(source):
    if not isinstance(source, list) or not source:
        raise WorkflowError("source is empty")
    return _digest(source)


def bound_assignment(assignment):
    return {field: copy.deepcopy(assignment[field]) for field in BOUND_FIELDS}


def validate_assignment(assignment, source):
    scope(assignment)
    if type(assignment.get("issue")) is not int or assignment["issue"] <= 0:
        raise WorkflowError("issue must be a positive integer")
    if type(assignment.get("recording_version")) is not int or assignment["recording_version"] <= 0:
        raise WorkflowError("recording_version must be a positive integer")
    for field in ("contributor", "reviewer"):
        if not isinstance(assignment.get(field), str) or not USER.fullmatch(assignment[field]):
            raise WorkflowError(f"{field} must be a GitHub login")
    if assignment["contributor"].casefold() == assignment["reviewer"].casefold():
        raise WorkflowError("contributor and reviewer must be different people")
    if not re.fullmatch(r"[A-Za-z0-9_-]{20,120}", assignment.get("spreadsheet_id", "")):
        raise WorkflowError("spreadsheet_id is invalid")
    tab = assignment.get("tab")
    if not isinstance(tab, str) or not tab.strip() or len(tab) > 100 or any(ord(c) < 32 for c in tab):
        raise WorkflowError("tab is invalid")
    keys = assignment.get("keys")
    if (not isinstance(keys, list) or not 1 <= len(keys) <= MAX_KEYS
            or any(not isinstance(k, str) for k in keys) or len(set(keys)) != len(keys)):
        raise WorkflowError("keys must contain 1 to 200 unique take IDs")
    index = {r["key"]: r for r in source}
    for key in keys:
        if key not in index or not index[key]["ready"]:
            raise WorkflowError(f"take is unknown, on hold or has no approved spoken text: {key}")
    if assignment.get("script_hash") != script_hash(source):
        raise WorkflowError("script or approved spoken text changed; create a new assignment")
    result = copy.deepcopy(assignment)
    result["keys"] = [r["key"] for r in source if r["key"] in set(keys)]
    return result


def reserve(state, assignment, source):
    candidate = validate_assignment(assignment, source)
    if not isinstance(state, dict) or not isinstance(state.get("assignments"), list):
        raise WorkflowError("voice registry is invalid")
    for old in state["assignments"]:
        if old.get("status") not in ACTIVE | TERMINAL:
            raise WorkflowError("voice registry contains an unknown status")
        if old.get("issue") == candidate["issue"]:
            raise WorkflowError("issue is already reserved; use a new voice work order")
        if scope(old) != scope(candidate) or not set(old["keys"]).intersection(candidate["keys"]):
            continue
        if old["status"] in ACTIVE:
            raise WorkflowError(f"take scope overlaps active issue #{old['issue']}")
        if old["status"] == "completed" and candidate["recording_version"] <= old["recording_version"]:
            raise WorkflowError("a completed take requires a deliberately higher recording version")
    result = copy.deepcopy(state)
    candidate["status"] = "assigned"
    result["assignments"].append(candidate)
    return result


def manifest_path(assignment):
    locale, role, slot = scope(assignment)
    number = assignment.get("issue")
    if type(number) is not int or number <= 0:
        raise WorkflowError("issue is invalid")
    return f"voice/submissions/{locale}/{role}/{slot}/{number}.json"


def target_hash(root, assignment):
    path = _safe_path(root, pathlib.Path(manifest_path(assignment)))
    if path.exists():
        raise WorkflowError("this work order already has a committed manifest; use a new issue and version")
    return hashlib.sha256(b"MISSING").hexdigest()


def parse_snapshot(csv_text, assignment, source):
    assigned = validate_assignment(assignment, source)
    rows = _csv_rows(csv_text, OUTBOX_FIELDS)
    relevant = [row for row in rows if row["Work order"] == str(assigned["issue"])]
    # The owner bridge appends complete revisions. Only the last appended batch
    # is current; historical receipts remain useful without blocking retakes.
    if not relevant:
        raise WorkflowError("every assigned take needs exactly one owner-frozen receipt")
    revision = relevant[-1]["Revision"]
    rows = [row for row in relevant if row["Revision"] == revision]
    selected = {}
    for row in rows:
        key = row["Take file"]
        if key not in assigned["keys"] or key in selected:
            raise WorkflowError("outbox has an unassigned or duplicate take for this issue")
        if not re.fullmatch(r"https://drive\.google\.com/file/d/[A-Za-z0-9_-]{20,120}/view", row["Drive snapshot"]):
            raise WorkflowError("receipt must link to a private frozen Drive file")
        if not HASH.fullmatch(row["SHA256"]) or not HASH.fullmatch(row["Revision"]):
            raise WorkflowError("recording and revision hashes must be lowercase SHA256")
        if row["Script SHA256"] != assigned["script_hash"]:
            raise WorkflowError("receipt belongs to a different script version")
        if not re.fullmatch(r"[1-9][0-9]*", row["Bytes"]) or not 0 < int(row["Bytes"]) <= MAX_BYTES:
            raise WorkflowError("recording byte count must be between 1 and 250 MiB")
        if row["MIME type"] not in {"audio/wav", "audio/flac"}:
            raise WorkflowError("receipt must identify WAV or FLAC audio")
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", row["Submitted"]):
                raise ValueError()
            datetime.strptime(row["Submitted"], "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise WorkflowError("Submitted must be a UTC receipt timestamp") from None
        selected[key] = row
    if set(selected) != set(assigned["keys"]):
        raise WorkflowError("every assigned take needs exactly one owner-frozen receipt")
    if len({r["Revision"] for r in selected.values()}) != 1:
        raise WorkflowError("all takes must come from the same frozen submission revision")
    if len({r["Submitted"] for r in selected.values()}) != 1:
        raise WorkflowError("all takes must share the frozen revision's submission time")
    return {"schema": 1, "assignment": bound_assignment(assigned),
            "script": [copy.deepcopy(row) for row in source if row["key"] in set(assigned["keys"])],
            "rows": [selected[key] for key in assigned["keys"]]}


def snapshot_hash(snapshot):
    if not isinstance(snapshot, dict):
        raise WorkflowError("snapshot must be an object")
    return _digest({k: v for k, v in snapshot.items() if k != "digest"})


def build_export(root, assignment, snapshot):
    source = get_source(root, assignment.get("locale"), assignment.get("table"))
    valid = validate_assignment(assignment, source)
    if snapshot.get("schema") != 1 or snapshot.get("assignment") != bound_assignment(valid):
        raise WorkflowError("snapshot is bound to a different voice assignment")
    if snapshot.get("digest") != snapshot_hash(snapshot):
        raise WorkflowError("snapshot digest is invalid")
    if snapshot.get("target_hash") != target_hash(root, valid):
        raise WorkflowError("manifest destination changed after preview")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=OUTBOX_FIELDS, lineterminator="\n")
    writer.writeheader()
    try:
        writer.writerows(snapshot["rows"])
    except (ValueError, KeyError, TypeError):
        raise WorkflowError("snapshot receipt structure is invalid") from None
    canonical = parse_snapshot(output.getvalue(), valid, source)
    if canonical["rows"] != snapshot["rows"]:
        raise WorkflowError("snapshot takes must be in source order")
    if canonical["script"] != snapshot.get("script"):
        raise WorkflowError("snapshot spoken text or context differs from the approved script")
    manifest = {"schema": 1, "kind": "private-drive-recording-manifest",
                "assignment": bound_assignment(valid), "snapshot_sha256": snapshot["digest"],
                "script": snapshot["script"],
                "receipts": snapshot["rows"],
                "verification": "Receipt metadata only. GitHub did not download, listen to, or verify audio bytes."}
    return manifest_path(valid), json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"


def snapshot_review(snapshot):
    a = snapshot["assignment"]
    # JSON fenced data prevents receipt text from changing the review instructions.
    return ("## Private Drive recording review\n\n"
            f"Work order: #{a['issue']}\n\n"
            f"Script SHA256: `{a['script_hash']}`\n\n"
            "Open the private frozen copies and listen to every take. Check performance, spoken text, "
            "consent and file metadata. GitHub validates receipt metadata only and never fetches the audio.\n\n"
            f"Digest: `{snapshot_hash(snapshot)}`\n\n"
            f"Only @{a['reviewer']} may approve: `/voice approve {snapshot_hash(snapshot)}`\n\n"
            "```json\n" + json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n```\n")
