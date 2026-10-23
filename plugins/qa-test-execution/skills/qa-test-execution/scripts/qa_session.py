"""Shared helpers: browser launch, saved-session loading, JWT handling.

Session files live in the run's session dir (outside the repo, deleted at the end):
    <role>.state.json   Playwright storageState (cookies + localStorage)
    <role>.auth.json    captured bearer token, decoded claims, API hosts seen
    run.json            {"api_base": ..., "app_url": ...} written once the user confirms

Nothing here prints a token or cookie value.
"""
import base64
import json
import time
from contextlib import contextmanager
from pathlib import Path


def launch_browser(p, headless=True):
    """Bundled Chromium first, then the machine's Chrome or Edge."""
    errors = []
    for channel in (None, "chrome", "msedge"):
        try:
            return p.chromium.launch(headless=headless, channel=channel) if channel else p.chromium.launch(headless=headless)
        except Exception as e:  # noqa: BLE001 - try the next channel
            errors.append(f"{channel or 'chromium'}: {str(e).splitlines()[0]}")
    raise RuntimeError("No usable browser. Run `python -m playwright install chromium`.\n" + "\n".join(errors))


def b64url_decode(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def decode_jwt(token):
    """Return (header, claims) or (None, None) if it is not a JWT."""
    try:
        h, c, _ = token.split(".")
        return json.loads(b64url_decode(h)), json.loads(b64url_decode(c))
    except Exception:  # noqa: BLE001
        return None, None


def load_run(session_dir):
    p = Path(session_dir) / "run.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def load_role(session_dir, role):
    d = Path(session_dir)
    state_p, auth_p = d / f"{role}.state.json", d / f"{role}.auth.json"
    if not state_p.exists():
        raise SystemExit(f"NO_SESSION role={role}: {state_p} not found. Ask the user to log in for this role.")
    auth = json.loads(auth_p.read_text(encoding="utf-8")) if auth_p.exists() else {}
    return {"state_path": str(state_p), "state": json.loads(state_p.read_text(encoding="utf-8")), "auth": auth}


def token_expired(auth, skew=30):
    exp = (auth.get("claims") or {}).get("exp")
    return bool(exp) and exp < time.time() + skew


@contextmanager
def open_page(session_dir, role, headless=True, viewport=(1440, 900)):
    """Playwright page already logged in as `role`. For Browser test cases.

        import sys; sys.path.insert(0, r"<skill>/scripts")
        from qa_session import open_page
        with open_page(SESSION_DIR, "hr") as page:
            page.goto(APP_URL + "/leaves"); page.screenshot(path=".../step-1.png")
    """
    from playwright.sync_api import sync_playwright
    s = load_role(session_dir, role)
    if token_expired(s["auth"]):
        raise SystemExit(f"SESSION_EXPIRED role={role}")
    with sync_playwright() as p:
        browser = launch_browser(p, headless=headless)
        ctx = browser.new_context(storage_state=s["state_path"],
                                  viewport={"width": viewport[0], "height": viewport[1]})
        # sessionStorage is not part of storageState; restore it per origin before any page script runs.
        for origin, items in (s["auth"].get("session_storage") or {}).items():
            ctx.add_init_script(
                "(() => { if (location.origin !== %s) return; const d = %s;"
                " for (const k in d) if (sessionStorage.getItem(k) === null) sessionStorage.setItem(k, d[k]); })()"
                % (json.dumps(origin), json.dumps(items)))
        page = ctx.new_page()
        try:
            yield page
        finally:
            ctx.close()
            browser.close()
