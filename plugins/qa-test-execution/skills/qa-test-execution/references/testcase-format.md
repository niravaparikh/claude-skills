# Test-case format the parser expects

`parse_testcases.py` reads `.xlsx`, `.xlsm` and `.csv`. One file = one **feature** (the
file name without extension). Each worksheet (or the whole CSV) = one **story**.

## Within a sheet

- **Intro rows** (above the header) are the story title and summary — kept as context, not test cases.
- **Header row**: the first row (within the first 20) that matches at least 3 known column
  names. Aliases are matched case-insensitively and trimmed of a trailing `:`. Known fields:
  `id, module, title, description, type, priority, preconditions, steps, expected,
  test_data, status, issues, remarks, tested_by`. `title`, `steps` and `expected` are required;
  a sheet missing any of them is reported as a `column_mapping` gap with the headers it saw.
- **Case rows**: every row below the header that has a title or steps.
- **Execution Order row**: a cell starting `Execution Order:` followed by story names joined by
  `→`, `->`, `=>` or commas. It sets the run order of stories in that feature.
- Other non-case rows become story `notes`.

## Marking a case API or Browser

The marker is `[API]` or `[Browser]` anywhere in the title, description or a `type` column
(a `Type` column value of `api`/`browser`/`ui`/`web` also counts). Exactly one marker is
required. The parser normalises the type and flags:
- `missing_marker` — no marker found.
- `conflicting_marker` — both `[API]` and `[Browser]` present.

## Needs-clarification and references

- `[NEEDS CLARIFICATION] - <text>` in any cell (usually Remarks) is captured per case. These are
  **not** asked up front; the case runs and is marked **Needs review** with the question.
- A case that mentions another feature file's name is recorded under `references_features` so the
  planner keeps those features from racing on shared data.
- A precondition/step mentioning "previous case", "above case", etc. sets `depends_on_previous`,
  so the runner keeps it after its predecessor.

## Gap kinds (all surfaced for one batched question)

| kind | meaning |
|---|---|
| `no_header` | no header row found in the first 20 rows |
| `column_mapping` | header found but a required column (title/steps/expected) is missing |
| `missing_marker` / `conflicting_marker` | API/Browser marker absent or doubled |
| `vague_steps` / `vague_expected` | that field is empty or under 10 characters |
| `existing_status` | the Status column already holds a value — run again anyway? |
| `execution_order_unknown_story` | the order names a story not present as a sheet |

The inventory JSON holds the full parsed content; the skill reads it to plan and to let the
report show planned-but-not-run cases. It is written to the session dir, never the repo.
