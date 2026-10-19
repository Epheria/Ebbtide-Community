"""Translation helper for Ebbtide. Standard library only.

    python tools/l10n.py init <lang>     create translation files for a new language (e.g. pt-BR)
    python tools/l10n.py update [lang]   sync translations with the current English source
    python tools/l10n.py check [lang]    validate translations (runs on every pull request)
    python tools/l10n.py status          show progress per language

Translation files live in localization/translations/<lang>/<Table>.csv with the columns
key, en, translation, status. Translators fill `translation`. `status` is blank when the row is fine,
"outdated" when the English source changed after it was translated, and "review" when a reviewer
should look again. Clear "outdated" once you have updated the translation.
"""

import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "localization" / "source" / "strings"
TRANSLATIONS_DIR = ROOT / "localization" / "translations"
FIELDS = ["key", "en", "translation", "status"]
STATUSES = {"", "outdated", "review"}
LANG_PATTERN = re.compile(r"^[a-z]{2,3}(-[A-Z]{2}|-[A-Za-z]{4})?$")
PLACEHOLDER_PATTERN = re.compile(r"\{[^{}]*\}|<[^<>]+>|\\n")


def read_csv(path: pathlib.Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def source_tables() -> dict[str, list[dict]]:
    return {path.stem: read_csv(path) for path in sorted(SOURCE_DIR.glob("*.csv"))}


def languages() -> list[str]:
    if not TRANSLATIONS_DIR.exists():
        return []
    return sorted(path.name for path in TRANSLATIONS_DIR.iterdir() if path.is_dir() and not path.name.startswith("_"))


def placeholders(text: str) -> list[str]:
    return sorted(PLACEHOLDER_PATTERN.findall(text))


def sync_language(lang: str, create: bool) -> None:
    lang_dir = TRANSLATIONS_DIR / lang
    if create:
        if not LANG_PATTERN.match(lang):
            sys.exit(f"'{lang}' is not a language code like 'de', 'pt-BR' or 'zh-Hans'.")
        lang_dir.mkdir(parents=True, exist_ok=True)
    elif not lang_dir.exists():
        sys.exit(f"No translations for '{lang}' yet. Run: python tools/l10n.py init {lang}")

    for table, source_rows in source_tables().items():
        path = lang_dir / f"{table}.csv"
        existing = {row["key"]: row for row in read_csv(path)} if path.exists() else {}
        merged, added, outdated = [], 0, 0
        for source in source_rows:
            row = existing.pop(source["key"], None)
            if row is None:
                merged.append({"key": source["key"], "en": source["en"], "translation": "", "status": ""})
                added += 1
                continue
            if row["en"] != source["en"]:
                if row.get("translation", "").strip():
                    row["status"] = "outdated"
                    outdated += 1
                row["en"] = source["en"]
            merged.append({field: row.get(field, "") for field in FIELDS})
        write_csv(path, merged)
        removed = len(existing)
        print(f"{lang}/{table}: {added} new, {outdated} outdated, {removed} removed")


def check_language(lang: str, source: dict[str, list[dict]]) -> int:
    errors = 0
    lang_dir = TRANSLATIONS_DIR / lang
    if not LANG_PATTERN.match(lang):
        print(f"ERROR {lang}: folder name is not a language code like 'de' or 'pt-BR'")
        errors += 1
    for path in sorted(lang_dir.glob("*.csv")):
        if path.stem not in source:
            print(f"ERROR {lang}/{path.name}: there is no source table with this name")
            errors += 1
            continue
        source_keys = {row["key"]: row for row in source[path.stem]}
        try:
            rows = read_csv(path)
        except (csv.Error, UnicodeDecodeError) as error:
            print(f"ERROR {lang}/{path.name}: cannot read the file ({error})")
            errors += 1
            continue
        if rows and list(rows[0].keys()) != FIELDS:
            print(f"ERROR {lang}/{path.name}: columns must be {', '.join(FIELDS)}")
            errors += 1
            continue
        seen = set()
        for line, row in enumerate(rows, start=2):
            where = f"{lang}/{path.name} line {line} ({row['key']})"
            if row["key"] in seen:
                print(f"ERROR {where}: key appears twice")
                errors += 1
            seen.add(row["key"])
            if row["key"] not in source_keys:
                print(f"ERROR {where}: key does not exist in the source")
                errors += 1
                continue
            if row["status"] not in STATUSES:
                print(f"ERROR {where}: status must be blank, 'outdated' or 'review'")
                errors += 1
            translation = row["translation"]
            if translation.strip() and placeholders(translation) != placeholders(source_keys[row["key"]]["en"]):
                print(f"ERROR {where}: keep every {{0}}, <tag> and \\n from the English text")
                errors += 1
    return errors


def command_check(lang: str | None) -> None:
    source = source_tables()
    targets = [lang] if lang else languages()
    errors = sum(check_language(target, source) for target in targets)
    if errors:
        sys.exit(f"{errors} problem(s) found.")
    print(f"OK: {', '.join(targets) if targets else 'no translations yet'}")


def command_status() -> None:
    source = source_tables()
    total = sum(len(rows) for rows in source.values())
    print(f"Source: {total} strings in {len(source)} tables")
    for lang in languages():
        done = outdated = 0
        for path in (TRANSLATIONS_DIR / lang).glob("*.csv"):
            for row in read_csv(path):
                if row["translation"].strip():
                    if row["status"] == "outdated":
                        outdated += 1
                    else:
                        done += 1
        percent = 100 * done / total if total else 0
        print(f"{lang:8} {done:5}/{total} translated ({percent:5.1f}%), {outdated} outdated")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] not in {"init", "update", "check", "status"}:
        sys.exit(__doc__)
    command, lang = args[0], (args[1] if len(args) > 1 else None)
    if command == "init":
        if not lang:
            sys.exit("Usage: python tools/l10n.py init <lang>")
        sync_language(lang, create=True)
    elif command == "update":
        for target in [lang] if lang else languages():
            sync_language(target, create=False)
    elif command == "check":
        command_check(lang)
    else:
        command_status()


if __name__ == "__main__":
    main()
