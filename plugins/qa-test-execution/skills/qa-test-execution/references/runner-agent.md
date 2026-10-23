# Runner agent instructions

Hand this to each parallel runner agent, with the `<...>` placeholders filled in. One agent owns
one feature (or one ordered chain), so agents never collide on shared data.

---

You are executing the test cases of **one feature** against a live app and writing one result
file per case. Be exact and honest: never fabricate a result, never mark a case Pass unless the
app's actual behaviour matched the expected result.

**Your inputs**
- Feature: `<feature-name>` — cases are in the inventory at `<session-dir>/inventory.json` under
  this feature. Read only this feature's stories and cases.
- Session dir: `<session-dir>` (holds the saved role sessions and `run.json` with the API base).
- Skill scripts: `<skill>/scripts/` — use `http_call.py` for API cases and `qa_session.open_page`
  for Browser cases. Do not write your own HTTP or browser-launch code.
- Results dir: `<results-dir>/<feature-name>/` — write `<case-id>.json` per case here.
- Evidence dir: same folder; save screenshots/response dumps and reference them by path relative
  to `<results-dir>`.

**Order**
Run the feature's stories in `execution_order` if present, else sheet order. Within a story, run
cases top to bottom; a case with `depends_on_previous` must run after its predecessor. Later
cases often rely on data an earlier case created — do not reorder a chain.

**For each case**
1. Pick the role from the preconditions. If its session is not in the session dir, write a result
   with status **Blocked** ("role <x> not provided") and move on — do not run under another role.
2. Check preconditions you can verify with read calls (e.g. "no leave exists for 1042 in June").
   If a precondition is unmet and you cannot set it up with your own marked data, mark **Blocked**
   with the reason. Do not force it by touching pre-existing data.
3. Run the steps:
   - **API**: `python -X utf8 <skill>/scripts/http_call.py --session-dir "<session-dir>" --role <r>
     --method <M> --path <p> [--json '...'] [--header "Origin: ..."] [--token-variant ...]
     --log <evidence-dir>/<case-id>/step-<n>.json`. The log file is your evidence.
   - **Browser**: `from qa_session import open_page` (add `<skill>/scripts` to `sys.path`), drive the
     page, and `page.screenshot(path=...)` at the asserted moment. Capture a shot of the state the
     expected result is about.
4. Compare actual vs expected and choose the status (Pass / Fail / Blocked / Skipped / Needs
   review — definitions in SKILL.md). A `needs_clarification` note on the case, or an expected
   result that allows more than one outcome, means **Needs review**: record what actually happened
   and keep the question.
5. If a step wrote data, tag it with `ZZ-QA-<timestamp>` where a free text field allows, and record
   it for cleanup (what it is, how to delete it).
6. If any call returns `SESSION_EXPIRED` (exit 3), stop and report `SESSION_EXPIRED <role>` in your
   summary so the orchestrator can get the user to log in again; do not guess a pass.

**Write the result** `<results-dir>/<feature-name>/<case-id>.json`:
```json
{
  "id": "...", "feature": "<feature-name>", "story": "...", "title": "...", "type": "API",
  "status": "Pass", "role": "hr", "duration_ms": 0,
  "summary": "one line on what happened",
  "expected": "<the expected result text>", "actual": "<what the app did>",
  "steps": [{"n": 1, "request": "POST /api/v1/leaves", "result": "201", "evidence": "<feature>/<id>/step-1.json"}],
  "issues": ["defect, with the contract or security impact"],
  "needs_clarification": ["the open question, if any"],
  "evidence": ["<feature>/<id>/step-1.json", "<feature>/<id>/state.png"],
  "created_records": [{"what": "...", "cleanup": "deleted|left|failed", "detail": "..."}]
}
```
Evidence paths are relative to the results dir so the report can embed them.

**Return** a short summary: counts per status, any `SESSION_EXPIRED`, and the list of records you
created so the orchestrator can confirm cleanup. Do not clean up created data yourself unless told
to — the orchestrator deletes at the end so dependent cases can still use it.
