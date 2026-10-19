"""Read-only live smoke check of the two supported public Sheet schemas."""
import csv
import io
from contribution_bot import fetch_sheet
from contribution_core import UI_FIELDS, VOICE_FIELDS, WorkflowError


def main():
    fixtures = [
        ("ui", "1YegbTot6iaszCQV2_3O_yM_oCkkGGqeUVl1m52xzmbM", "SaveSlots", UI_FIELDS),
        ("voice-text", "1ObgnTm9lYXfxNpR1gkrFSkhU_OmkFCkIqfEqps0S-Vs", "Japanese", VOICE_FIELDS),
    ]
    for kind, sheet_id, tab, header in fixtures:
        text = fetch_sheet({"kind": kind, "spreadsheet_id": sheet_id, "tab": tab})
        rows = list(csv.reader(io.StringIO(text)))
        if not rows or rows[0] != header or len(rows) < 2:
            raise WorkflowError("Unexpected live Sheet schema: " + tab)
        print(f"OK: {kind} / {tab}: {len(rows) - 1} source rows readable; no data written")


if __name__ == "__main__":
    main()
