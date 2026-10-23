# Sessions, roles, auth and cleanup

## The session dir

Create one dir for the run under the system temp area (never in the repo), e.g.
`$TEMP/qa-exec-<project>-<timestamp>/`. It holds `inventory.json`, `run.json`, and per role
`<role>.state.json` + `<role>.auth.json`. **Delete the whole dir at the end of the run and on
failure.** These files grant access to the app.

## Login capture

`login_capture.py` opens a visible browser (bundled Chromium, else the machine's Chrome or
Edge) at the app URL and waits. The user logs in by hand — Claude never sees or types
credentials. Ask the user to **open one data screen after logging in**, so the app fires an
authenticated API call the capture can learn the API host and bearer token from.

When the user confirms they are done, create `<role>.done` in the session dir. The script then:
- writes `<role>.state.json` — Playwright `storageState` (cookies + localStorage),
- writes `<role>.auth.json` — the bearer token the app sent (or a JWT found in storage),
  its decoded claims, captured `sessionStorage`, and the API hosts seen with request counts,
- prints a summary with the claims (roles, tenant, `expires_in_min`) and `api_hosts` — **no**
  token or cookie values.

If the summary shows no `api_hosts`, the user did not trigger an API call; ask them to open a
data screen and re-run the capture for that role.

## Roles

Suites need several identities. Read the preconditions to list the distinct roles (permission
set + tenant). Capture one session per role the user can provide. A case whose role was not
captured is **Blocked** with that reason — never run it under the wrong role and call it a pass.

`http_call.py --role <label>` and `open_page(session_dir, "<label>")` select the session.

## API base URL

The portal URL is not the API host. Take the API base from the capture summary's top
`api_hosts` entry (the origin that carried the bearer token), confirm it with the user, and
write `run.json`: `{"api_base":"https://...","app_url":"https://..."}`. `http_call.py` joins
`--path` onto `api_base`; `--url` overrides for an absolute URL.

## Auth per request

`http_call.py --auth`:
- `auto` (default) — bearer if one was captured for the role, else session cookies.
- `bearer` / `cookie` / `both` / `none` — force the scheme (e.g. a CORS case needs `cookie`
  with an explicit `--header "Origin: ..."`; a no-auth case needs `none`).

`--token-variant` for negative-auth cases:
- `valid` (default), `missing` (no header), `malformed` (an invalid token string),
- `expired` — sends the saved token only if it has actually passed its `exp`; otherwise the
  call exits `BLOCKED` and you report the case Blocked. The helper never mints or re-signs
  tokens; a case that strictly needs a forged signed token is **Blocked**.

Exit codes: `3` = SESSION_EXPIRED (ask the user to log in again for that role), `4` = NO_SESSION.

## Expiry mid-run

If any call returns SESSION_EXPIRED, pause that role's lane, ask the user to log in again for
that role (re-run the capture, same label), and resume. Other lanes continue.

## Data you create, and cleanup

- Tag created records with a marker like `ZZ-QA-<timestamp>` wherever the schema has a free text
  field (name, reason, note). Keep a list: for each, how to delete it (endpoint + ids).
- At the end, delete only records on your list, via the API. Record each as
  `created_records: [{what, cleanup: deleted|left|failed, detail}]` in the case result so the
  report's **Data created** table is accurate.
- Never delete or edit data you did not create. If unsure whether a record is yours, leave it
  and note it.
