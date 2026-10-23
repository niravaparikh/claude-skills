#!/usr/bin/env python3
"""Send one API request as a saved role and log it as evidence.

Usage:
    python -X utf8 http_call.py --session-dir <dir> --role hr --method POST --path /api/v1/leaves \
        --json '{"employee_id": 1042}' --log <evidence-dir>/<tc-id>/step-1.json

Request options:
    --path P | --url U       path is joined to api_base from run.json; --url is used as-is
    --query k=v              repeatable
    --header "K: V"          repeatable (e.g. Origin, Idempotency-Key, X-Correlation-ID)
    --json STR | --json-file F | --data-file F [--content-type T] | --file field=path (multipart, repeatable)
    --auth auto|bearer|cookie|both|none   auto = bearer if one was captured, else cookies
    --token-variant valid|missing|malformed|expired
        For negative-auth cases: send the valid token, none, an obviously invalid
        string, or the saved token only if it has already expired (else the case is
        reported as Blocked — this helper does not mint tokens).
    --method-override OPTIONS  send a bare preflight-style request with no body
    --no-redirect, --timeout 60, --max-print 4000

stdout: JSON {status, elapsed_ms, headers, body|body_text, body_saved_to}. Token, cookie and
Authorization values are never printed or logged. Exit 3 = SESSION_EXPIRED, 4 = NO_SESSION.
"""
import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_session import decode_jwt, load_role, load_run, token_expired  # noqa: E402

SECRET_HEADERS = {"authorization", "cookie", "set-cookie", "proxy-authorization", "x-api-key"}
# An unmistakably invalid JWT-shaped string: three non-decodable segments. Used to
# verify the server rejects non-valid tokens. It is not signed and carries no real claims.
MALFORMED_TOKEN = "invalid.invalid.invalid"


def redact(headers):
    return {k: ("<redacted>" if k.lower() in SECRET_HEADERS else v) for k, v in dict(headers).items()}


def parse_kv(items, sep):
    out = {}
    for it in items or []:
        if sep not in it:
            raise SystemExit(f"Expected key{sep}value, got {it!r}")
        k, v = it.split(sep, 1)
        out[k.strip()] = v.strip()
    return out


def build_auth(role_data, auth_mode, variant):
    """Return (headers, cookies_dict, note). Never returns the raw token to the caller's log."""
    auth = role_data["auth"]
    token = auth.get("bearer")
    headers, cookies, note = {}, {}, None

    if auth_mode in ("bearer", "both", "auto"):
        want_bearer = auth_mode in ("bearer", "both") or (auth_mode == "auto" and token)
        if want_bearer:
            if variant == "missing":
                note = "token-variant=missing: no Authorization header sent"
            elif variant == "malformed":
                headers["Authorization"] = f"Bearer {MALFORMED_TOKEN}"
                note = "token-variant=malformed: sent an invalid token string"
            elif variant == "expired":
                if not token:
                    raise SystemExit("BLOCKED token-variant=expired: no token was captured for this role.")
                if not token_expired(auth, skew=0):
                    raise SystemExit("BLOCKED token-variant=expired: the saved token is still valid; "
                                     "cannot test expiry without an expired token. Report as Blocked.")
                headers["Authorization"] = f"Bearer {token}"
                note = "token-variant=expired: sent the saved token, which has passed its exp"
            else:  # valid
                if not token:
                    raise SystemExit("BLOCKED: role has no captured bearer token; use --auth cookie or log in again.")
                headers["Authorization"] = f"Bearer {token}"

    if auth_mode in ("cookie", "both") or (auth_mode == "auto" and not token):
        for c in role_data["state"].get("cookies", []):
            cookies[c["name"]] = c["value"]
        if auth_mode == "auto" and not token:
            note = "auth=auto: no bearer captured, sent session cookies"
    return headers, cookies, note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-dir", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--method", default="GET")
    ap.add_argument("--path")
    ap.add_argument("--url")
    ap.add_argument("--query", action="append")
    ap.add_argument("--header", action="append")
    ap.add_argument("--json")
    ap.add_argument("--json-file")
    ap.add_argument("--data-file")
    ap.add_argument("--content-type")
    ap.add_argument("--file", action="append", help="multipart field=path")
    ap.add_argument("--auth", default="auto", choices=["auto", "bearer", "cookie", "both", "none"])
    ap.add_argument("--token-variant", default="valid", choices=["valid", "missing", "malformed", "expired"])
    ap.add_argument("--no-redirect", action="store_true")
    ap.add_argument("--timeout", type=float, default=60)
    ap.add_argument("--max-print", type=int, default=4000)
    ap.add_argument("--log", help="write the full request/response record here")
    a = ap.parse_args()

    role_data = load_role(a.session_dir, a.role)  # exits NO_SESSION if absent
    if a.token_variant == "valid" and a.auth in ("auto", "bearer", "both") and token_expired(role_data["auth"]):
        print(json.dumps({"error": "SESSION_EXPIRED", "role": a.role,
                          "hint": "Ask the user to log in again for this role."}))
        sys.exit(3)

    run = load_run(a.session_dir)
    if a.url:
        url = a.url
    else:
        base = run.get("api_base")
        if not base:
            raise SystemExit("No api_base in run.json and --url not given. Confirm the API base URL first.")
        url = urljoin(base.rstrip("/") + "/", (a.path or "").lstrip("/"))

    headers = parse_kv(a.header, ":")
    auth_headers, cookies, auth_note = build_auth(role_data, a.auth, a.token_variant)
    headers.update(auth_headers)

    body_kwargs = {}
    if a.json is not None:
        body_kwargs["json"] = json.loads(a.json)
    elif a.json_file:
        body_kwargs["json"] = json.loads(Path(a.json_file).read_text(encoding="utf-8"))
    elif a.data_file:
        body_kwargs["data"] = Path(a.data_file).read_bytes()
        if a.content_type:
            headers.setdefault("Content-Type", a.content_type)
    if a.file:
        body_kwargs["files"] = {f.split("=", 1)[0]: open(f.split("=", 1)[1], "rb") for f in a.file}

    t0 = time.time()
    try:
        resp = requests.request(a.method.upper(), url, params=parse_kv(a.query, "="), headers=headers,
                                cookies=cookies or None, allow_redirects=not a.no_redirect,
                                timeout=a.timeout, **body_kwargs)
    except requests.RequestException as e:
        rec = {"error": "REQUEST_FAILED", "detail": str(e), "url": url, "method": a.method.upper()}
        print(json.dumps(rec, indent=2))
        if a.log:
            Path(a.log).parent.mkdir(parents=True, exist_ok=True)
            Path(a.log).write_text(json.dumps(rec, indent=2), encoding="utf-8")
        sys.exit(1)
    elapsed_ms = round((time.time() - t0) * 1000)

    ctype = resp.headers.get("content-type", "")
    body, body_text = None, None
    if "json" in ctype:
        try:
            body = resp.json()
        except ValueError:
            body_text = resp.text
    else:
        body_text = resp.text if len(resp.content) < 200_000 else f"<{len(resp.content)} bytes {ctype}>"

    record = {
        "request": {"method": a.method.upper(), "url": url, "query": parse_kv(a.query, "="),
                    "headers": redact(headers), "auth_mode": a.auth, "token_variant": a.token_variant,
                    "auth_note": auth_note, "role": a.role,
                    "body": body_kwargs.get("json", "<raw/multipart>" if body_kwargs else None)},
        "response": {"status": resp.status_code, "elapsed_ms": elapsed_ms,
                     "headers": redact(resp.headers), "body": body, "body_text": body_text},
    }
    if a.log:
        Path(a.log).parent.mkdir(parents=True, exist_ok=True)
        Path(a.log).write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

    printed = dict(record["response"])
    if printed.get("body_text") and len(printed["body_text"]) > a.max_print:
        printed["body_text"] = printed["body_text"][:a.max_print] + f"... <+{len(printed['body_text']) - a.max_print} chars>"
    printed["body_saved_to"] = a.log
    printed["auth_note"] = auth_note
    print(json.dumps(printed, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
