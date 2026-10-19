"""Export the game's Unity Localization string tables into localization/source/strings/.

Maintainer tool. Contributors never need to run it.

Usage:
    python tools/export_unity_strings.py --project <path to the Unity project>

Each table collection becomes one CSV with the columns key, en, ko.
English is the source text translators work from; Korean is the original and is kept for reference.
Requires PyYAML (pip install pyyaml).
"""

import argparse
import csv
import datetime
import pathlib
import re
import sys

import yaml

LOCALES = ("en", "ko")
TABLES_DIR = pathlib.Path("Assets/Localization/Tables")
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "localization" / "source" / "strings"


def load_unity_yaml(path: pathlib.Path) -> dict:
    """Unity writes a %TAG header and !u! tags that PyYAML cannot resolve; strip them first."""
    text = path.read_text(encoding="utf-8")
    text = "\n".join(line for line in text.splitlines() if not line.startswith("%"))
    text = re.sub(r"^--- !u!\d+ &\d+", "---", text, flags=re.MULTILINE)
    return yaml.safe_load(text)["MonoBehaviour"]


def export_collection(shared_path: pathlib.Path) -> int:
    shared = load_unity_yaml(shared_path)
    name = shared["m_TableCollectionName"]
    keys = [(entry["m_Id"], entry["m_Key"]) for entry in shared.get("m_Entries") or []]

    values = {}
    for locale in LOCALES:
        table_path = shared_path.with_name(f"{name}_{locale}.asset")
        if not table_path.exists():
            sys.exit(f"Missing table: {table_path}")
        table = load_unity_yaml(table_path)
        values[locale] = {entry["m_Id"]: entry.get("m_Localized") or "" for entry in table.get("m_TableData") or []}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{name}.csv"
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["key", *LOCALES])
        for entry_id, key in sorted(keys, key=lambda item: item[1]):
            writer.writerow([key, *(values[locale].get(entry_id, "") for locale in LOCALES)])
    print(f"{name}: {len(keys)} keys -> {out_path.relative_to(REPO_ROOT)}")
    return len(keys)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", required=True, type=pathlib.Path, help="Unity project root")
    args = parser.parse_args()

    tables_dir = args.project / TABLES_DIR
    shared_files = sorted(tables_dir.glob("* Shared Data.asset"))
    if not shared_files:
        sys.exit(f"No string tables found in {tables_dir}")

    total = sum(export_collection(path) for path in shared_files)
    stamp = datetime.date.today().isoformat()
    (OUT_DIR.parent / "SNAPSHOT").write_text(f"{stamp}\n{total} keys\n", encoding="utf-8")
    print(f"Total: {total} keys, snapshot {stamp}")


if __name__ == "__main__":
    main()
