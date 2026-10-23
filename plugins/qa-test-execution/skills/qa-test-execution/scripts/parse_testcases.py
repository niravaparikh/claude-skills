#!/usr/bin/env python3
"""Parse a folder of Excel/CSV test cases into one inventory JSON.

Usage:
    python -I -X utf8 parse_testcases.py <test-case-folder> <out-inventory.json>

Each file is a feature. Each sheet (or the whole CSV) is a story. The header row
is found by matching known column names; rows above it are the story intro, and
a row like "Execution Order: A -> B -> C" gives the story order.

The parser never guesses: anything it cannot map with certainty is listed under
"gaps" so the skill can ask the user. Exit code 0 even when gaps exist; the
caller decides what to do with them.
"""
import csv
import json
import re
import sys
from pathlib import Path

# Lower-cased header aliases. A column is mapped only on an exact alias match.
ALIASES = {
    "id": ["id", "tc id", "test case id", "testcase id", "tc no", "tc #", "case id", "test id"],
    "module": ["module", "feature", "area", "component"],
    "title": ["title", "test case", "test case title", "test case name", "name", "summary", "scenario"],
    "description": ["description", "test description", "objective"],
    "type": ["type", "test type", "category"],
    "priority": ["priority", "severity"],
    "preconditions": ["preconditions", "precondition", "pre-conditions", "pre-condition", "prerequisites"],
    "steps": ["steps", "test steps", "steps to reproduce", "procedure"],
    "expected": ["expected results", "expected result", "expected", "expected outcome", "expected behaviour", "expected behavior"],
    "test_data": ["test data", "data"],
    "status": ["status", "result", "actual status"],
    "issues": ["issues", "defects", "bugs"],
    "remarks": ["remarks", "notes", "comments"],
    "tested_by": ["tested by", "tester", "executed by"],
}
REQUIRED = ["title", "steps", "expected"]
MARKER = re.compile(r"\[\s*(API|Browser)\s*\]", re.I)
CLARIFY = re.compile(r"\[?NEEDS CLARIFICATION\]?\s*-?\s*([^|\n]*)", re.I)
EXEC_ORDER = re.compile(r"^\s*execution order\s*:\s*(.+)$", re.I)
PREV_CASE = re.compile(r"previous (test )?case|from the previous|above case|earlier case", re.I)


def norm(v):
    if v is None:
        return ""
    return str(v).strip()


def read_tables(path):
    """Yield (sheet_name, rows) for an xlsx/xlsm or csv file."""
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xlsm"):
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        for ws in wb.worksheets:
            yield ws.title, [[norm(c) for c in r] for r in ws.iter_rows(values_only=True)]
    elif suffix == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as fh:
            yield path.stem, [[norm(c) for c in r] for r in csv.reader(fh)]


def find_header(rows):
    """Return (index, {field: col}) of the best header row in the first 20 rows."""
    best = (None, {})
    for i, row in enumerate(rows[:20]):
        mapping = {}
        for col, cell in enumerate(row):
            key = cell.lower().rstrip(":").strip()
            for field, names in ALIASES.items():
                if key in names and field not in mapping:
                    mapping[field] = col
        if len(mapping) > len(best[1]):
            best = (i, mapping)
    return best if len(best[1]) >= 3 else (None, {})


def story_name(sheet, intro):
    """Sheet names are cut at 31 chars in Excel; prefer the full id from the intro title."""
    if intro:
        head = re.split(r"\s+[—–-]\s+", intro[0], maxsplit=1)[0].strip()
        if head and head.startswith(sheet.rstrip("-")[:20]):
            return head
    return sheet


def parse_file(path, feature_stems):
    feature = {"file": path.name, "feature": path.stem, "stories": [], "execution_order": [],
               "references_features": [], "gaps": []}
    for sheet, rows in read_tables(path):
        rows = [r for r in rows]
        hi, cols = find_header(rows)
        if hi is None:
            if any(any(c for c in r) for r in rows):
                feature["gaps"].append({"kind": "no_header", "where": f"{path.name} / {sheet}",
                                        "detail": "No header row with known column names found in the first 20 rows.",
                                        "first_rows": [r[:12] for r in rows[:6]]})
            continue
        missing = [f for f in REQUIRED if f not in cols]
        header_cells = rows[hi]
        unmapped = [h for c, h in enumerate(header_cells) if h and c not in cols.values()]
        if missing:
            feature["gaps"].append({"kind": "column_mapping", "where": f"{path.name} / {sheet}",
                                    "detail": f"Required columns not found: {missing}",
                                    "header_row": header_cells, "unmapped_headers": unmapped})
            continue
        intro = [next(c for c in r if c) for r in rows[:hi] if any(r)]
        story = {"sheet": sheet, "story": story_name(sheet, intro), "intro": intro,
                 "columns": {f: header_cells[c] for f, c in cols.items()},
                 "unmapped_headers": unmapped, "notes": [], "cases": []}
        n = 0
        for r_i, row in enumerate(rows[hi + 1:], start=hi + 2):
            get = lambda f: row[cols[f]] if f in cols and cols[f] < len(row) else ""
            if not get("title") and not get("steps"):
                text = " ".join(c for c in row if c)
                if text:
                    m = EXEC_ORDER.match(text)
                    if m:
                        order = [s.strip() for s in re.split(r"→|->|=>|,", m.group(1)) if s.strip()]
                        feature["execution_order"] = order
                    else:
                        story["notes"].append(text)
                continue
            n += 1
            title, desc = get("title"), get("description")
            markers = {m.upper() if m.lower() == "api" else "Browser"
                       for m in MARKER.findall(f"{title} {desc} {get('type')}")}
            type_col = get("type").lower()
            if not markers and type_col in ("api", "browser", "ui", "web"):
                markers = {"API" if type_col == "api" else "Browser"}
            all_text = " ".join(c for c in row if c)
            case = {
                "id": get("id") or f"{story['story']}-{n:02d}",
                "row": r_i,
                "type": next(iter(markers)) if len(markers) == 1 else None,
                "module": get("module"), "title": MARKER.sub("", title).strip(), "description": desc,
                "priority": get("priority"), "preconditions": get("preconditions"),
                "steps": get("steps"), "expected": get("expected"), "test_data": get("test_data"),
                "remarks": get("remarks"),
                "existing_status": get("status"),
                "needs_clarification": [c.strip() for c in CLARIFY.findall(all_text) if c.strip()]
                                       or (["(flagged without detail)"] if "NEEDS CLARIFICATION" in all_text.upper() else []),
                "depends_on_previous": bool(PREV_CASE.search(get("preconditions") + " " + get("steps"))),
                "references_features": sorted({s for s in feature_stems if s != path.stem and s in all_text}),
            }
            story["cases"].append(case)
            where = f"{path.name} / {sheet} / row {r_i} ({case['id']})"
            if len(markers) > 1:
                feature["gaps"].append({"kind": "conflicting_marker", "where": where, "detail": "Has both [API] and [Browser]."})
            elif not markers:
                feature["gaps"].append({"kind": "missing_marker", "where": where, "detail": "No [API] or [Browser] marker."})
            for f in ("steps", "expected"):
                if len(get(f)) < 10:
                    feature["gaps"].append({"kind": f"vague_{f}", "where": where,
                                            "detail": f"'{cols and story['columns'][f]}' is empty or too short to judge: {get(f)!r}"})
            if case["existing_status"]:
                feature["gaps"].append({"kind": "existing_status", "where": where,
                                        "detail": f"Status column already holds {case['existing_status']!r}. Run it again anyway?"})
        feature["references_features"] = sorted({s for st in [story] for c in st["cases"] for s in c["references_features"]}
                                                | set(feature["references_features"]))
        feature["stories"].append(story)
    if feature["execution_order"]:
        known = {s["story"] for s in feature["stories"]} | {s["sheet"] for s in feature["stories"]}
        unknown = [s for s in feature["execution_order"] if s not in known]
        if unknown:
            feature["gaps"].append({"kind": "execution_order_unknown_story", "where": path.name,
                                    "detail": f"Execution Order names stories not found as sheets: {unknown}"})
    return feature


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    folder, out = Path(sys.argv[1]), Path(sys.argv[2])
    files = sorted(p for p in folder.rglob("*") if p.suffix.lower() in (".xlsx", ".xlsm", ".csv") and not p.name.startswith("~$"))
    skipped = sorted(str(p.relative_to(folder)) for p in folder.rglob("*")
                     if p.is_file() and p not in files and not p.name.startswith("~$"))
    stems = {p.stem for p in files}
    features = [parse_file(p, stems) for p in files]
    inv = {"source_folder": str(folder.resolve()), "features": features, "skipped_files": skipped}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")

    # Human summary (no test content beyond titles).
    total = {"API": 0, "Browser": 0, None: 0}
    print(f"Inventory: {out}")
    for f in features:
        cases = [c for s in f["stories"] for c in s["cases"]]
        for c in cases:
            total[c["type"]] += 1
        nc = sum(1 for c in cases if c["needs_clarification"])
        print(f"- {f['file']}: {len(f['stories'])} stories, {len(cases)} cases "
              f"(API {sum(c['type'] == 'API' for c in cases)}, Browser {sum(c['type'] == 'Browser' for c in cases)}, "
              f"unmarked {sum(c['type'] is None for c in cases)}), needs-clarification {nc}"
              + (f", order: {' -> '.join(f['execution_order'])}" if f["execution_order"] else "")
              + (f", references: {', '.join(f['references_features'])}" if f["references_features"] else ""))
    print(f"Totals: API {total['API']}, Browser {total['Browser']}, unmarked {total[None]}")
    gaps = [g for f in features for g in f["gaps"]]
    print(f"Gaps: {len(gaps)}")
    for g in gaps:
        print(f"  [{g['kind']}] {g['where']}: {g['detail']}")
    if skipped:
        print(f"Files ignored (not .xlsx/.xlsm/.csv): {skipped}")


if __name__ == "__main__":
    main()
