#!/usr/bin/env python3
"""Open a visible browser at the app URL, let the user log in, then save the session.

Usage (run in the background, it waits for the user):
    python -X utf8 login_capture.py --url <app-url> --role <label> --session-dir <dir> [--timeout 1800]

The user logs in by hand. Claude never sees or types credentials. When the user
says they are done, Claude creates <session-dir>/<role>.done and this script:
  - saves Playwright storageState to <role>.state.json
  - records sessionStorage and the bearer token the app itself sends, to <role>.auth.json
  - prints a summary (API hosts seen, token claims such as exp/roles/permissions),
    never the token or cookie values.
"""
import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_session import decode_jwt, launch_browser  # noqa: E402

JWT_RE = re.compile(r"eyJ[\w-]+\.[\w-]+\.[\w-]*")
CLAIM_KEYS_SHOWN = ("sub", "email", "preferred_username", "tenant_id", "tenant", "org", "roles", "role",
                    "permissions", "scope", "scp", "aud", "iss", "exp", "iat")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--session-dir", required=True)
    ap.add_argument("--timeout", type=int, default=1800, help="seconds to wait for the user")
    a = ap.parse_args()

    from playwright.sync_api import sync_playwright
    sdir = Path(a.session_dir)
    sdir.mkdir(parents=True, exist_ok=True)
    done = sdir / f"{a.role}.done"
    done.unlink(missing_ok=True)

    hosts = defaultdict(lambda: {"requests": 0, "with_auth": 0, "paths": set()})
    bearer = {"token": None, "origin": None}

    def on_request(req):
        if req.resource_type not in ("xhr", "fetch"):
            return
        u = urlsplit(req.url)
        origin = f"{u.scheme}://{u.netloc}"
        h = hosts[origin]
        h["requests"] += 1
        if len(h["paths"]) < 8:
            h["paths"].add(u.path)
        auth = req.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            h["with_auth"] += 1
            bearer["token"], bearer["origin"] = auth[7:].strip(), origin

    with sync_playwright() as p:
        browser = launch_browser(p, headless=False)
        ctx = browser.new_context(viewport=None)
        ctx.on("request", on_request)
        page = ctx.new_page()
        page.goto(a.url)
        print(f"WAITING role={a.role}: browser open at {a.url}. Create {done} after the user has logged in.", flush=True)

        deadline = time.time() + a.timeout
        while not done.exists():
            if time.time() > deadline:
                print("TIMEOUT: user did not finish logging in.", flush=True)
                browser.close()
                sys.exit(2)
            if not browser.is_connected() or not ctx.pages:
                print("BROWSER_CLOSED: the window was closed before the session was saved.", flush=True)
                sys.exit(3)
            ctx.pages[0].wait_for_timeout(500)  # keeps request events flowing

        page = ctx.pages[-1]
        state_path = sdir / f"{a.role}.state.json"
        ctx.storage_state(path=str(state_path))
        session_storage = {}
        for pg in ctx.pages:
            try:
                origin = pg.evaluate("location.origin")
                session_storage[origin] = pg.evaluate("Object.fromEntries(Object.entries(sessionStorage))")
            except Exception:  # noqa: BLE001 - page may be mid-navigation
                pass

        # Fall back to a JWT the app keeps in storage when no request carried one.
        source = "request-header" if bearer["token"] else None
        if not bearer["token"]:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            stores = [(f"localStorage:{o['origin']}:{i['name']}", i["value"])
                      for o in state.get("origins", []) for i in o.get("localStorage", [])]
            stores += [(f"sessionStorage:{o}:{k}", v) for o, d in session_storage.items() for k, v in d.items()]
            for where, val in stores:
                m = JWT_RE.search(val or "")
                if m and decode_jwt(m.group(0))[1]:
                    bearer["token"], source = m.group(0), where
                    break

        _, claims = decode_jwt(bearer["token"]) if bearer["token"] else (None, None)
        cookies = json.loads(state_path.read_text(encoding="utf-8")).get("cookies", [])
        auth = {
            "role": a.role, "app_url": a.url, "final_url": page.url, "captured_at": int(time.time()),
            "bearer": bearer["token"], "bearer_source": source, "bearer_origin": bearer["origin"],
            "claims": claims or {}, "session_storage": session_storage,
            "api_hosts": [{"origin": o, "requests": v["requests"], "with_auth": v["with_auth"],
                           "sample_paths": sorted(v["paths"])}
                          for o, v in sorted(hosts.items(), key=lambda kv: -kv[1]["with_auth"] * 1000 - kv[1]["requests"])],
            "cookie_names": sorted({f"{c['domain']}:{c['name']}" for c in cookies}),
        }
        (sdir / f"{a.role}.auth.json").write_text(json.dumps(auth, indent=2), encoding="utf-8")
        browser.close()

    shown = {k: claims[k] for k in CLAIM_KEYS_SHOWN if claims and k in claims}
    if "exp" in shown:
        shown["expires_in_min"] = round((shown["exp"] - time.time()) / 60)
    print(json.dumps({
        "SAVED": a.role, "final_url": auth["final_url"],
        "bearer_found": bool(bearer["token"]), "bearer_source": source,
        "claims": shown, "cookies": len(cookies),
        "api_hosts": auth["api_hosts"][:6],
        "hint": None if auth["api_hosts"] else "No XHR/fetch calls seen. Ask the user to open a data screen, then log in again.",
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
