"""Shared helpers: browser launch, saved-session loading, JWT handling.

Session files live in the run's session dir (outside the repo, deleted at the end):
    <role>.state.json   Playwright storageState (cookies + localStorage)
    <role>.auth.json    captured bearer token, decoded claims, API hosts seen
    run.json            {"api_base": ..., "app_url": ...} written once the user confirms

Nothing here prints a token or cookie value.
"""
import base64
import json
import os
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


def _oauth_endpoint(auth):
    """(token_url, client_id) if the session came from an OAuth2/OIDC identity provider, else None.

    Uses what login_capture recorded (refresh_url + refresh_style "oauth" + oauth_client_id).
    For sessions captured before that existed, falls back to the access token's own claims:
    `iss` -> OIDC discovery -> token_endpoint, and `azp`/`client_id` as the client id.
    """
    claims = auth.get("claims") or {}
    client_id = auth.get("oauth_client_id") or claims.get("azp") or claims.get("client_id")
    if auth.get("refresh_style") == "oauth" and auth.get("refresh_url") and client_id:
        return auth["refresh_url"], client_id
    iss = claims.get("iss")
    issued_by = auth.get("refresh_issued_by") or ""
    if not (iss and client_id and (issued_by.endswith("/token") or not issued_by)):
        return None
    try:
        import requests
        conf = requests.get(iss.rstrip("/") + "/.well-known/openid-configuration", timeout=15).json()
        token_url = conf.get("token_endpoint")
    except Exception:  # noqa: BLE001 - not an OIDC issuer
        return None
    return (token_url, client_id) if token_url else None


def _sync_stored_tokens(auth, old_rt, found):
    """Swap the renewed tokens into any sessionStorage entry that held the old refresh token
    (e.g. oidc-client's `oidc.user:<iss>:<client>`), so a browser opened later starts fresh."""
    exp = (decode_jwt(found["bearer"])[1] or {}).get("exp")
    for items in (auth.get("session_storage") or {}).values():
        for k, v in list(items.items()):
            if not (isinstance(v, str) and old_rt in v):
                continue
            try:
                obj = json.loads(v)
            except Exception:  # noqa: BLE001 - not JSON, leave it
                continue
            if not (isinstance(obj, dict) and obj.get("refresh_token") == old_rt):
                continue
            obj["access_token"] = found["bearer"]
            obj["refresh_token"] = found.get("refresh_token", old_rt)
            if found.get("id_token"):
                obj["id_token"] = found["id_token"]
            if exp and "expires_at" in obj:
                obj["expires_at"] = exp
            items[k] = json.dumps(obj)


def refresh_session(session_dir, role, api_base, refresh_path=None, wait=20):
    """Renew `role`'s access token with the refresh token the app itself issued at login.

    This is the app's normal token flow, not token forging. The server rotates the refresh token,
    so the new pair is written back to <role>.auth.json. A lock file serialises parallel callers:
    one that waited re-reads the file and skips the call if another process just refreshed.
    Returns True if a valid token is available afterwards, False if the user must log in again.
    Never prints a token.
    """
    import os
    import requests
    d = Path(session_dir)
    auth_p, lock_p = d / f"{role}.auth.json", d / f"{role}.refresh.lock"
    deadline = time.time() + wait
    while True:
        try:
            os.close(os.open(lock_p, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        except FileExistsError:
            if time.time() > deadline:
                try:
                    if time.time() - lock_p.stat().st_mtime > 60:  # stale lock
                        lock_p.unlink(missing_ok=True)
                        continue
                except FileNotFoundError:
                    continue
                return False
            time.sleep(0.3)
    try:
        auth = json.loads(auth_p.read_text(encoding="utf-8"))
        if not token_expired(auth, skew=60):
            return True  # another process refreshed while we waited
        rt = auth.get("refresh_token")
        if not rt:
            return False
        oauth = _oauth_endpoint(auth)
        if oauth and not refresh_path:
            # OAuth2/OIDC IdP (Keycloak, Auth0, Entra, Cognito...): the standard refresh grant,
            # form-encoded, to the same token endpoint the app itself used at login.
            url, client_id = oauth
            r = requests.post(url, data={"grant_type": "refresh_token", "refresh_token": rt,
                                         "client_id": client_id}, timeout=30)
            path = url
        else:
            # App-specific JSON refresh: only the path the capture actually saw, never a guessed one.
            path = refresh_path or auth.get("refresh_path") or auth.get("refresh_url") or auth.get("refresh_issued_by")
            if not path:
                return False
            field = auth.get("refresh_field") or "refreshToken"
            url = path if path.startswith("http") else api_base.rstrip("/") + "/" + path.lstrip("/")
            r = requests.post(url, json={field: rt}, timeout=30)
        if r.status_code >= 400:
            return False
        found, stack = {}, [r.json()]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                for k, v in cur.items():
                    kl = k.lower().replace("_", "")
                    if isinstance(v, str) and v and kl == "accesstoken":
                        found["bearer"] = v
                    elif isinstance(v, str) and v and kl == "refreshtoken":
                        found["refresh_token"] = v
                    elif isinstance(v, str) and v and kl == "idtoken":
                        found["id_token"] = v
                    elif isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(cur, list):
                stack.extend(x for x in cur if isinstance(x, (dict, list)))
        if "bearer" not in found:
            return False
        _sync_stored_tokens(auth, rt, found)
        found.pop("id_token", None)
        auth.update(found)
        auth["refresh_path"] = path
        _, claims = decode_jwt(found["bearer"])
        if claims:
            auth["claims"] = claims
        tmp = auth_p.with_suffix(".tmp")
        tmp.write_text(json.dumps(auth, indent=2), encoding="utf-8")
        os.replace(tmp, auth_p)
        return True
    finally:
        lock_p.unlink(missing_ok=True)


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
        base = load_run(session_dir).get("api_base")
        if not (base and os.environ.get("QA_ALLOW_REFRESH") == "1" and refresh_session(session_dir, role, base)):
            raise SystemExit(f"SESSION_EXPIRED role={role}")
        s = load_role(session_dir, role)
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
