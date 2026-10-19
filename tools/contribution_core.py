"""Deterministic, standard-library core for reviewed community contributions.

This module performs no network requests and never writes files. Callers own issue
authorization, persistence, spreadsheet downloads, pull requests and human approval.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
import pathlib
import re


class WorkflowError(ValueError):
    """The candidate cannot safely continue through the contribution workflow."""


UI_FIELDS = ["key", "en", "translation", "status"]
VOICE_FIELDS = [
    "Take file", "English source", "Translation", "Review status", "Notes", "Role",
    "Situation", "Tone", "Current voices", "Source readiness", "Source file", "Source record",
]
ACTIVE_STATUSES = frozenset({"assigned", "reviewed", "pr_open"})
TERMINAL_STATUSES = frozenset({"completed", "merged", "released", "cancelled", "rejected", "stale"})
TRANSLATION_STATUSES = frozenset({"", "review", "outdated"})
MAX_KEYS = 200
_LANG = re.compile(r"^[a-z]{2,3}(?:-(?:[A-Z]{2}|[A-Za-z]{4}))?$")
_STEM = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$")
_USER = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
_SHEET = re.compile(r"^[A-Za-z0-9_-]{20,120}$")
_HASH = re.compile(r"^[0-9a-f]{64}$")
_PLACEHOLDERS = re.compile(r"\{[^{}]*\}|<[^<>]+>|\\n")


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _text(value: object, name: str, *, allow_blank: bool = False) -> str:
    if not isinstance(value, str) or (not allow_blank and not value.strip()):
        raise WorkflowError(f"{name} must be a nonempty string")
    return value


def _scope(assignment: dict) -> tuple[str, str, str]:
    if not isinstance(assignment, dict):
        raise WorkflowError("assignment must be an object")
    kind = assignment.get("kind")
    if not isinstance(kind, str) or kind not in {"ui", "voice-text"}:
        raise WorkflowError("kind must be ui or voice-text")
    locale = assignment.get("locale")
    table = assignment.get("table")
    if not isinstance(locale, str) or not _LANG.fullmatch(locale):
        raise WorkflowError("locale must be a language code such as ja, pt-BR or zh-Hans")
    if not isinstance(table, str) or not _STEM.fullmatch(table):
        raise WorkflowError("table must be a safe source table or role name")
    return kind, locale, table


def _safe_path(root: str | pathlib.Path, relative: pathlib.PurePath) -> pathlib.Path:
    base = pathlib.Path(root).resolve()
    path = (base / relative).resolve()
    if not path.is_relative_to(base):
        raise WorkflowError("path leaves the repository")
    return path


def _csv_rows(text: str, expected: list[str], *, voice: bool = False) -> list[dict[str, str]]:
    if not isinstance(text, str) or len(text) > 20_000_000:
        raise WorkflowError("CSV must be text no larger than 20 MB")
    try:
        reader = csv.reader(io.StringIO(text.lstrip("\ufeff"), newline=""), strict=True)
        header = next(reader, None)
        if header is None:
            raise WorkflowError("CSV has no header")
        if voice:
            # Native Sheets exports use title case and spaces; no aliases or column
            # reordering are accepted beyond presentation case/whitespace.
            normalize = lambda value: " ".join(value.split()).casefold()
            if len(header) < len(expected) or list(map(normalize, header[:len(expected)])) != list(map(normalize, expected)):
                raise WorkflowError("voice CSV must begin with the twelve documented columns")
            if len(set(map(normalize, header))) != len(header):
                raise WorkflowError("CSV contains duplicate column names")
        elif header != expected:
            raise WorkflowError("CSV columns must be " + ",".join(expected))
        rows = []
        for line, values in enumerate(reader, 2):
            if not values or not any(value for value in values):
                continue
            if len(values) != len(header):
                raise WorkflowError(f"CSV line {line} has the wrong number of fields")
            rows.append(dict(zip(expected if voice else header, values[:len(expected)])))
        return rows
    except (csv.Error, UnicodeError) as error:
        raise WorkflowError(f"cannot read CSV: {error}") from error


def _source_index(source: list[dict]) -> dict[str, dict]:
    if not isinstance(source, list) or not source:
        raise WorkflowError("source table is empty")
    index = {}
    for row in source:
        if not isinstance(row, dict):
            raise WorkflowError("source rows must be objects")
        key = _text(row.get("key"), "source key")
        _text(row.get("en"), "source English", allow_blank=True)
        if key in index:
            raise WorkflowError(f"source key appears twice: {key}")
        index[key] = row
    return index


def get_source(root: str | pathlib.Path, kind: str, table: str) -> list[dict]:
    """Load source text; voice holds are kept and marked source_ready=False."""
    _scope({"kind": kind, "locale": "en", "table": table})
    relative = (pathlib.Path("localization/source/strings") / f"{table}.csv" if kind == "ui"
                else pathlib.Path("voice/scripts") / f"{table}.csv")
    path = _safe_path(root, relative)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        raise WorkflowError(f"cannot read source {relative}: {error}") from error
    expected = ["key", "en", "ko"] if kind == "ui" else ["file", "situation", "tone", "line", "current_voices"]
    rows = _csv_rows(text, expected)
    if kind == "ui":
        source = [{"key": row["key"], "en": row["en"]} for row in rows]
    else:
        source = [{"key": row["file"], "en": row["line"],
                   "source_ready": "wording not confirmed" not in row["situation"].casefold()}
                  for row in rows]
    _source_index(source)
    return source


def source_hash(source: list[dict]) -> str:
    """Hash the whole table's ordered key/English pairs, independent of metadata."""
    _source_index(source)
    return hashlib.sha256(_canonical([{"key": row["key"], "en": row["en"]} for row in source])).hexdigest()


def validate_assignment(assignment: dict, source: list[dict]) -> dict:
    """Return a validated copy with keys ordered by the current source table."""
    _scope(assignment)
    issue = assignment.get("issue")
    if type(issue) is not int or issue <= 0:
        raise WorkflowError("issue must be a positive integer")
    for field in ("contributor", "reviewer"):
        value = assignment.get(field)
        if not isinstance(value, str) or not _USER.fullmatch(value):
            raise WorkflowError(f"{field} must be a GitHub username without @")
    if assignment["contributor"].casefold() == assignment["reviewer"].casefold():
        raise WorkflowError("contributor and reviewer must be different people")
    sheet = assignment.get("spreadsheet_id")
    if not isinstance(sheet, str) or not _SHEET.fullmatch(sheet):
        raise WorkflowError("spreadsheet_id is invalid")
    tab = _text(assignment.get("tab"), "tab")
    if len(tab) > 100 or any(ord(char) < 32 for char in tab):
        raise WorkflowError("tab is invalid")
    keys = assignment.get("keys")
    if not isinstance(keys, list) or not 1 <= len(keys) <= MAX_KEYS:
        raise WorkflowError(f"an assignment must contain 1 to {MAX_KEYS} keys")
    if any(not isinstance(key, str) or not key.strip() for key in keys) or len(set(keys)) != len(keys):
        raise WorkflowError("assignment keys must be unique nonempty strings")
    expected_hash = assignment.get("source_hash")
    if not isinstance(expected_hash, str) or not _HASH.fullmatch(expected_hash):
        raise WorkflowError("source_hash must be a lowercase SHA256 digest")
    if expected_hash != source_hash(source):
        raise WorkflowError("source changed; create a fresh assignment or review preview")
    index = _source_index(source)
    for key in keys:
        if key not in index:
            raise WorkflowError(f"unknown assigned source key: {key}")
        if not index[key]["en"].strip() or index[key].get("source_ready") is False:
            raise WorkflowError(f"source wording is on hold: {key}")
    result = copy.deepcopy(assignment)
    result["keys"] = [row["key"] for row in source if row["key"] in set(keys)]
    return result


def reserve(state: dict, assignment: dict, source: list[dict]) -> dict:
    """Return a new ledger; active overlaps and any reused issue fail."""
    candidate = validate_assignment(assignment, source)
    if not isinstance(state, dict) or not isinstance(state.get("assignments", []), list):
        raise WorkflowError("state must contain an assignments list")
    scope = _scope(candidate)
    for existing in state.get("assignments", []):
        if not isinstance(existing, dict):
            raise WorkflowError("state contains an invalid assignment")
        status = existing.get("status")
        if status not in ACTIVE_STATUSES | TERMINAL_STATUSES:
            raise WorkflowError("state contains an unknown assignment status")
        if existing.get("issue") == candidate["issue"]:
            raise WorkflowError("this issue already has an assignment; open a new issue")
        if status not in ACTIVE_STATUSES:
            continue
        existing_scope = _scope(existing)
        existing_keys = existing.get("keys")
        if not isinstance(existing_keys, list) or any(not isinstance(key, str) for key in existing_keys):
            raise WorkflowError("state contains invalid assignment keys")
        if existing_scope == scope and set(existing_keys).intersection(candidate["keys"]):
            raise WorkflowError(f"assigned keys overlap active issue #{existing['issue']}")
    result = copy.deepcopy(state)
    candidate["status"] = "assigned"
    result.setdefault("assignments", []).append(candidate)
    return result


def _bound_assignment(assignment: dict) -> dict:
    fields = ("issue", "kind", "locale", "table", "contributor", "reviewer",
              "spreadsheet_id", "tab", "keys", "source_hash")
    return {field: copy.deepcopy(assignment[field]) for field in fields}


def _check_translation(key: str, english: str, translated: str) -> None:
    if not translated.strip():
        raise WorkflowError(f"translation is empty: {key}")
    if sorted(_PLACEHOLDERS.findall(english)) != sorted(_PLACEHOLDERS.findall(translated)):
        raise WorkflowError(f"placeholders differ from source: {key}")


def parse_snapshot(csv_text: str, assignment: dict, source: list[dict]) -> dict:
    """Select ready assigned rows from a complete native Sheets CSV export."""
    assigned = validate_assignment(assignment, source)
    index = _source_index(source)
    keys = set(assigned["keys"])
    voice = assigned["kind"] == "voice-text"
    rows = _csv_rows(csv_text, VOICE_FIELDS if voice else UI_FIELDS, voice=voice)
    selected = {}
    seen_relevant = set()
    selected_occurrences = {}
    for row in rows:
        key = row["Take file"] if voice else row["key"]
        # Count selected identifiers across the whole voice tab, including a
        # mislabeled role; they must identify exactly one spreadsheet row.
        if key in keys:
            selected_occurrences[key] = selected_occurrences.get(key, 0) + 1
        if voice and row["Role"] != assigned["table"]:
            continue
        if not key.strip():
            raise WorkflowError("a populated CSV row has no key")
        if key in seen_relevant:
            raise WorkflowError(f"CSV key appears twice: {key}")
        seen_relevant.add(key)
        if key not in index:
            raise WorkflowError(f"CSV contains an unknown source key: {key}")
        english = row["English source"] if voice else row["en"]
        if english != index[key]["en"]:
            raise WorkflowError(f"spreadsheet English differs from current source: {key}")
        if not voice and row["status"] not in TRANSLATION_STATUSES:
            raise WorkflowError(f"CSV status is invalid: {key}")
        if key not in keys:
            continue
        if voice:
            if row["Review status"] != "Approved":
                raise WorkflowError(f"voice translation is not Approved: {key}")
            readiness = row["Source readiness"].casefold()
            if any(word in readiness for word in ("hold", "unconfirmed", "not confirmed", "draft", "blocked")):
                raise WorkflowError(f"spreadsheet source wording is on hold: {key}")
            translated = row["Translation"]
        else:
            if row["status"] != "":
                raise WorkflowError(f"UI translation still needs review or updating: {key}")
            translated = row["translation"]
        _check_translation(key, english, translated)
        selected[key] = {"key": key, "en": english, "translation": translated}
    for key in assigned["keys"]:
        if selected_occurrences.get(key, 0) != 1 or key not in selected:
            raise WorkflowError(f"assigned key must occur exactly once in the correct role: {key}")
    return {"schema": 1, "assignment": _bound_assignment(assigned),
            "source_hash": assigned["source_hash"],
            "rows": [selected[key] for key in assigned["keys"]]}


def snapshot_hash(snapshot: dict) -> str:
    """Bind every snapshot field, including optional target_hash, except digest."""
    if not isinstance(snapshot, dict):
        raise WorkflowError("snapshot must be an object")
    return hashlib.sha256(_canonical({key: value for key, value in snapshot.items() if key != "digest"})).hexdigest()


def _target_relative(assignment: dict) -> pathlib.PurePath:
    kind, locale, table = _scope(assignment)
    parent = pathlib.Path("localization/translations") if kind == "ui" else pathlib.Path("voice/translations")
    return parent / locale / f"{table}.csv"


def target_hash(root: str | pathlib.Path, assignment: dict) -> str:
    """Hash destination bytes, or the literal MISSING marker for a new file."""
    path = _safe_path(root, _target_relative(assignment))
    try:
        content = path.read_bytes() if path.exists() else b"MISSING"
    except OSError as error:
        raise WorkflowError(f"cannot read translation target: {error}") from error
    return hashlib.sha256(content).hexdigest()


def _validate_snapshot(snapshot: dict, assignment: dict, source: list[dict]) -> dict[str, dict]:
    validated = validate_assignment(assignment, source)
    if snapshot.get("schema") != 1 or snapshot.get("assignment") != _bound_assignment(validated):
        raise WorkflowError("snapshot is bound to a different assignment")
    if snapshot.get("source_hash") != source_hash(source):
        raise WorkflowError("snapshot source changed")
    if "digest" in snapshot and snapshot["digest"] != snapshot_hash(snapshot):
        raise WorkflowError("snapshot digest does not match its content")
    rows = snapshot.get("rows")
    if not isinstance(rows, list):
        raise WorkflowError("snapshot rows must be a list")
    current = _source_index(source)
    index = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"key", "en", "translation"}:
            raise WorkflowError("snapshot row columns are invalid")
        key = row["key"]
        if not isinstance(key, str) or key not in validated["keys"] or key in index:
            raise WorkflowError("snapshot contains duplicate or unassigned keys")
        if row["en"] != current[key]["en"] or not isinstance(row["translation"], str):
            raise WorkflowError(f"snapshot differs from source: {key}")
        _check_translation(key, row["en"], row["translation"])
        index[key] = row
    if [row["key"] for row in rows] != validated["keys"]:
        raise WorkflowError("snapshot must contain every assigned key in source order")
    return index


def build_export(root: str | pathlib.Path, assignment: dict, snapshot: dict) -> tuple[str, str]:
    """Return a full canonical CSV, replacing only approved assigned rows."""
    source = get_source(root, assignment.get("kind"), assignment.get("table"))
    selected = _validate_snapshot(snapshot, assignment, source)
    if not isinstance(snapshot.get("target_hash"), str) or not _HASH.fullmatch(snapshot["target_hash"]):
        raise WorkflowError("snapshot must bind the translation target hash before review")
    if snapshot["target_hash"] != target_hash(root, assignment):
        raise WorkflowError("translation target changed after preview; review a fresh snapshot")
    relative = _target_relative(assignment)
    path = _safe_path(root, relative)
    existing = {}
    source_index = _source_index(source)
    if path.exists():
        try:
            rows = _csv_rows(path.read_text(encoding="utf-8-sig"), UI_FIELDS)
        except (OSError, UnicodeError) as error:
            raise WorkflowError(f"cannot read existing translation: {error}") from error
        for row in rows:
            key = row["key"]
            if key in existing or key not in source_index:
                raise WorkflowError(f"existing translation contains duplicate or unknown key: {key}")
            if row["en"] != source_index[key]["en"]:
                raise WorkflowError(f"existing translation source needs updating first: {key}")
            if row["status"] not in TRANSLATION_STATUSES:
                raise WorkflowError(f"existing translation status is invalid: {key}")
            existing[key] = row
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=UI_FIELDS, lineterminator="\n")
    writer.writeheader()
    for source_row in source:
        key = source_row["key"]
        if key in selected:
            row = {**selected[key], "status": ""}
        else:
            row = existing.get(key, {"key": key, "en": source_row["en"], "translation": "", "status": ""})
        writer.writerow(row)
    return relative.as_posix(), output.getvalue()


def snapshot_review(snapshot: dict) -> str:
    """Render the exact candidate and its digest for a human review comment."""
    assignment = snapshot["assignment"]
    # JSON quoting keeps literal control characters and multiline translations
    # readable. HTML escaping prevents contribution text from altering the table.
    def cell(value: object) -> str:
        text = json.dumps(value, ensure_ascii=False) if isinstance(value, str) else str(value)
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        for char in "|`@[]!*_~":
            text = text.replace(char, f"&#{ord(char)};")
        return text
    lines = ["## Contribution review preview", "",
             f"Issue: #{assignment['issue']}",
             f"Scope: {cell(assignment['kind'])} / {cell(assignment['locale'])} / {cell(assignment['table'])}",
             f"Contributor: @{assignment['contributor']}; reviewer: @{assignment['reviewer']}",
             f"Sheet: {cell(assignment['spreadsheet_id'])}; tab: {cell(assignment['tab'])}",
             f"Source SHA256: `{snapshot['source_hash']}`",
             f"Target SHA256: `{snapshot.get('target_hash', 'not bound')}`",
             f"Snapshot SHA256: `{snapshot_hash(snapshot)}`", "",
             "Approval applies only to the snapshot digest above.", "",
             "| Key | English source | Proposed translation |", "| --- | --- | --- |"]
    lines.extend("| " + " | ".join(cell(row[field]) for field in ("key", "en", "translation")) + " |"
                 for row in snapshot["rows"])
    return "\n".join(lines) + "\n"
