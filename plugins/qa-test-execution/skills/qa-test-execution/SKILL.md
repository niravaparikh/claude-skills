---
name: qa-test-execution
description: Executes a folder of written test cases (Excel/CSV, each test marked [API] or [Browser] in its title or description) against a live web app and writes a feature-wise HTML results report with per-test status (Pass/Fail/Blocked/Skipped/Needs review), issues and screenshot/response evidence. The user gives only a URL and the test-case folder path — never credentials; the user logs in themselves in a browser the skill opens, once per distinct role, and the skill reuses that session (cookies + bearer token) for both browser and API tests. Runs the test cases in parallel across a few agents to finish faster. Use this whenever the user wants to run, execute or "go through" a folder/sheet/suite of test cases or a test plan against a site, do QA/regression/smoke/API test execution, turn a test-case spreadsheet into results, or get a pass/fail report per feature — even if they do not say "execute".
# allowed-tools: Bash, Read, Write, Glob, Grep, Agent, mcp__playwright__browser_navigate, mcp__playwright__browser_snapshot
---

# QA Test Execution

Run a folder of written test cases against a live app and report, per feature, what passed, what failed, and what could not be judged — with evidence a developer can act on without re-running anything.

The test cases are the source of truth for *intent*; the live app is the source of truth for *behaviour*. The job is to compare them honestly and never fabricate a result.

## Hard rules (and why)

- **Never ask for, read, type, log or store credentials.** Open the URL in a browser the user controls and let them log in themselves (`scripts/login_capture.py`). The skill captures only the resulting session — cookies and whatever bearer token the app itself sends. Credentials in chat or files leak into transcripts and git.
- **Session files live outside the repo and are deleted at the end.** They go in a session dir under the system temp area, never in the repo tree. Delete the whole dir when the run ends (and on failure). A saved session is as sensitive as a password.
- **Never print a token or cookie value.** The bundled scripts redact `Authorization`, `Cookie` and similar. When you quote a request in the report, quote the redacted form. Decoded JWT *claims* (roles, tenant, exp) are fine to show — they help explain a 403.
- **Only touch data the run created.** Many cases write data. Tag every record you create with a recognisable marker (e.g. `ZZ-QA-<timestamp>` in a name/reason field where the schema allows) and keep a list. At the end, delete only records on that list, via the API. Never edit or delete data you did not create. If you cannot tell whether a record is yours, leave it and say so.
- **Do not forge credentials.** For negative-auth cases, verify rejection by sending *no* token, a *malformed* token string, or an *already-expired* captured token (`--token-variant` in `http_call.py`). That proves the server rejects non-valid tokens. Do **not** mint signed tokens (alg:none, re-signed HS256, altered claims); if a case strictly needs one, mark it **Blocked** with that reason.
- **Same origin only.** API calls go to the confirmed API base; browser tests stay on the app's origin. Do not follow links to other origins.
- **Never assume. Ask when something is genuinely ambiguous**, in one batch, before running (see Gaps). Do not invent a URL, a role, an API base, or a missing expected result.

## Inputs to collect first

The user gives a **URL** and a **test-case folder path**. Confirm these, then ask only for what is missing:
1. Project name — used in the report file name.
2. Any role whose login the user can provide (see Roles). Do not ask yet *which* roles; the parse tells you.

## Workflow

### 1. Parse the test cases

```
python -I -X utf8 <skill>/scripts/parse_testcases.py "<folder>" "<session-dir>/inventory.json"
```

Each file is one **feature** (the file name). Each sheet/CSV is a **story**. The parser recovers full story names from truncated Excel sheet tabs, reads the header row wherever it sits, picks up the `[API]`/`[Browser]` marker, the `Execution Order:` row, cross-feature references, and every `[NEEDS CLARIFICATION]` note. It prints a per-file summary and a **Gaps** list. Read `references/testcase-format.md` for the format it expects and the gap kinds.

### 2. Resolve gaps — ask once, in one batch

Before running anything, collect everything the parser flagged plus anything you cannot act on, and ask the user in a single batch. Do not start partial. Typical gaps:
- A test with no `[API]`/`[Browser]` marker, or both.
- Steps or expected result too short to judge.
- A header row the parser could not map (tell the user which columns it saw).
- An `Execution Order` naming a story that is not present.

`[NEEDS CLARIFICATION]` notes are **not** a blocker to ask about up front. Run those cases, record the actual behaviour, and mark the case **Needs review** with the question attached (see Statuses). Only ask up front when a case cannot run at all without the answer.

### 3. Capture the login — once per distinct role

Scan the preconditions for the distinct identities the suite needs (e.g. HR with `attendance.leaves.manage`, a viewer with only `analytics.view`, a second tenant, a machine credential). List them for the user and, for each role they can provide, run the capture in the background:

```
python -X utf8 <skill>/scripts/login_capture.py --url "<app-url>" --role <label> --session-dir "<session-dir>" &
```

It opens a visible browser at the URL. Ask the user to log in as that role **and open one data screen** (so the app makes an authenticated API call the capture can learn from). When they say they are done, create the sentinel the script is waiting for:

```
touch "<session-dir>/<label>.done"
```

The script then saves `<label>.state.json` (cookies + localStorage) and `<label>.auth.json` (bearer token, decoded claims, API hosts seen) and prints a summary — no secret values. Roles the user cannot provide: every case needing them is **Blocked** with that reason. See `references/sessions-and-auth.md`.

### 4. Confirm the API base URL

API steps use paths like `/api/v1/...`. Take the API host from the capture summary's `api_hosts` (the origin that carried the bearer token), show it to the user, and on confirmation write it:

```
echo '{"api_base":"<confirmed>","app_url":"<app-url>"}' > "<session-dir>/run.json"
```

If no API host was seen, ask the user for the API base URL. Never guess it.

### 5. Plan the parallel run (max 3 agents)

Build a run plan from the inventory:
- **Dependencies stay in order.** Within a feature file, stories linked by `Execution Order` run in that sequence; a case marked `depends_on_previous` runs after its predecessor in the same story. Never parallelise inside a dependency chain.
- **Independent features run in parallel, up to 3 agents at once.** Start with features that have no cross-feature reference and no shared write target. Group the 9 sample features into at most 3 lanes so each lane is internally ordered and lanes are independent; launch 3, then feed the next feature to a lane as it frees up.
- Give each agent one feature (or one ordered chain) so there is no collision on shared data. Read `references/runner-agent.md` and pass it to each agent verbatim as its instructions, with the feature, session dir, inventory path, API base, and results/evidence dirs filled in.

Spawn the agents with the Agent tool. Each agent executes its cases with `scripts/http_call.py` (API) or `scripts/qa_session.py`'s `open_page` (Browser), writes one `<id>.json` result per case into `<results-dir>/<feature>/`, saves evidence beside it, tracks created records, and returns a short summary.

### 6. Build the report

When all agents finish:

```
python -I -X utf8 <skill>/scripts/build_report.py \
  --results "<results-dir>" --inventory "<session-dir>/inventory.json" \
  --out "reports/<project>_<YYYY-MM-DD>.html" --project "<name>" \
  --app-url "<app-url>" --notes "roles: … · api_base: …"
```

One self-contained HTML file, grouped by feature then story, with the status mix per feature, an **Open questions** section (every Needs-review question), a **Data created** table with cleanup status, and per-case expected/actual, issues and embedded evidence. Planned cases with no result show as *Not run*.

### 7. Clean up

Delete every record the run created (via the API, only from your list), then delete the session dir. Report anything that could not be cleaned up. Tell the user the report path and give them the headline status mix. Do not commit or push — the user does that.

## Statuses (use exactly these)

- **Pass** — ran, behaviour matched the expected result.
- **Fail** — ran, behaviour contradicted a clear expected result. Attach the issue and evidence.
- **Blocked** — could not run: missing role/session, unmet precondition you could not set up, forged-token-only case, dependency that failed. Say why.
- **Skipped** — deliberately not run (e.g. it would modify pre-existing data you must not touch). Say why.
- **Needs review** — ran, but the expected result is ambiguous (a `[NEEDS CLARIFICATION]` note, or the spec allows more than one outcome). Record the actual behaviour and the exact question.

## Severity of issues

- **Critical** — security/permission bypass, data corruption, wrong data returned, 5xx on a valid request, a flow that cannot complete.
- **Major** — wrong status code or contract shape, a documented validation that does not fire, a filter/pagination that returns wrong rows.
- **Minor** — message wording, ordering, non-breaking field differences.

## Output

- Report: `reports/<project>_<YYYY-MM-DD>.html` (the `reports/` folder is committed empty; its contents are gitignored). Do not overwrite an existing same-day report; append `_2`, `_3`.
- Never write session files, tokens or test content into the repo. Evidence lives under the results dir and is embedded into the HTML, which is the only artefact that belongs in `reports/`.

## Reference files

- `references/testcase-format.md` — the sheet/CSV layout, markers, execution order, gap kinds.
- `references/sessions-and-auth.md` — login capture, roles, API base discovery, token variants, cleanup.
- `references/runner-agent.md` — the instruction block to hand each parallel runner agent.
