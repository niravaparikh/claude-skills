#!/usr/bin/env python3
"""Build one self-contained HTML results report, grouped by feature.

Usage:
    python -X utf8 build_report.py --results <results-dir> --inventory <inv.json> \
        --out reports/<project>_<date>.html --project "<name>" --app-url <url>

<results-dir> holds one JSON per test case (any depth). Each result file:
{
  "id": "US-mark-leave-01", "feature": "F-leave-management", "story": "US-mark-leave",
  "title": "3-day range expands to one leave row per date", "type": "API",
  "status": "Pass|Fail|Blocked|Skipped|Needs review",
  "summary": "one line on what happened",
  "expected": "...", "actual": "...",
  "issues": ["..."],                 # defects found, if any
  "needs_clarification": ["..."],    # open questions carried from the sheet or found while running
  "steps": [{"n": 1, "request": "POST /api/v1/leaves", "result": "201", "evidence": "rel/path.json"}],
  "evidence": ["rel/path.png", "rel/path.json"],   # paths relative to <results-dir>
  "created_records": [{"what": "leave 1042 2026-06-10..12", "cleanup": "deleted|left|failed", "detail": "..."}],
  "duration_ms": 1234, "role": "hr"
}
Screenshots are embedded as data URIs; JSON/text evidence is inlined in a <details>.
Anything in evidence that looks like a token/cookie is skipped (see SECRET_HINT).
"""
import argparse
import base64
import html
import json
import mimetypes
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

STATUSES = ["Pass", "Fail", "Blocked", "Needs review", "Skipped"]
COLORS = {"Pass": "#1a7f37", "Fail": "#cf222e", "Blocked": "#9a6700",
          "Needs review": "#8250df", "Skipped": "#57606a", "Not run": "#8c959f"}
SECRET_HINT = ("authorization", "set-cookie", "bearer ", "cookie:")
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def esc(x):
    return html.escape(str(x if x is not None else ""))


def data_uri(path):
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def render_evidence(results_dir, rel):
    p = (results_dir / rel)
    if not p.exists():
        return f'<div class="ev-missing">missing evidence: {esc(rel)}</div>'
    ext = p.suffix.lower()
    if ext in IMG_EXT:
        return f'<figure><img loading="lazy" src="{data_uri(p)}" alt="{esc(rel)}"><figcaption>{esc(p.name)}</figcaption></figure>'
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return f'<div class="ev-missing">unreadable evidence: {esc(rel)}</div>'
    if any(h in text.lower() for h in SECRET_HINT) and ext not in (".json",):
        return f'<div class="ev-missing">skipped {esc(p.name)} (may contain a credential)</div>'
    return f'<details><summary>{esc(p.name)}</summary><pre>{esc(text[:20000])}</pre></details>'


def load_results(results_dir):
    out = []
    for p in sorted(results_dir.rglob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict) and d.get("id") and d.get("status"):
            out.append(d)
    return out


def bar(counts, total):
    segs = "".join(
        f'<span style="width:{counts[s] / total * 100:.4f}%;background:{COLORS[s]}" title="{s}: {counts[s]}"></span>'
        for s in STATUSES if counts.get(s))
    return f'<div class="bar">{segs}</div>'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--project", required=True)
    ap.add_argument("--app-url", default="")
    ap.add_argument("--notes", default="", help="run notes shown under the title (e.g. roles, api base)")
    a = ap.parse_args()

    results_dir = Path(a.results)
    inv = json.loads(Path(a.inventory).read_text(encoding="utf-8"))
    results = load_results(results_dir)
    by_id = {r["id"]: r for r in results}

    # Order features and cases by the inventory so planned-but-missing cases still show.
    features = []
    for f in inv["features"]:
        rows = []
        for s in f["stories"]:
            for c in s["cases"]:
                r = by_id.get(c["id"], {"id": c["id"], "title": c["title"], "type": c["type"],
                                        "story": s["story"], "status": "Not run",
                                        "needs_clarification": c.get("needs_clarification", [])})
                r.setdefault("story", s["story"])
                r.setdefault("title", c["title"])
                r.setdefault("type", c["type"])
                rows.append(r)
        features.append((f["feature"], f.get("file", ""), rows))
    # Results whose id is not in the inventory (shouldn't happen, but never drop a result).
    seen = {c["id"] for f in inv["features"] for s in f["stories"] for c in s["cases"]}
    orphans = [r for r in results if r["id"] not in seen]
    if orphans:
        features.append(("(unmatched results)", "", orphans))

    overall = Counter(r["status"] for _, _, rows in features for r in rows)
    total = sum(overall.values()) or 1
    created = [(r["id"], rec) for _, _, rows in features for r in rows for rec in r.get("created_records", [])]
    open_q = [(r["id"], q) for _, _, rows in features for r in rows for q in (r.get("needs_clarification") or [])]

    def chip(s, n):
        return f'<span class="chip" style="--c:{COLORS.get(s, "#888")}">{esc(s)} {n}</span>'

    parts = [f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(a.project)} — test execution</title>
<style>
 :root{{--bg:#fff;--fg:#1f2328;--mut:#57606a;--line:#d1d9e0;--card:#f6f8fa}}
 @media(prefers-color-scheme:dark){{:root{{--bg:#0d1117;--fg:#e6edf3;--mut:#9198a1;--line:#30363d;--card:#161b22}}}}
 *{{box-sizing:border-box}} body{{margin:0;font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--fg)}}
 .wrap{{max-width:1100px;margin:0 auto;padding:24px 16px}}
 h1{{margin:0 0 4px}} .sub{{color:var(--mut);margin-bottom:16px}}
 .chip{{display:inline-block;padding:2px 10px;border-radius:999px;color:#fff;background:var(--c);font-weight:600;font-size:13px;margin:2px 4px 2px 0}}
 .bar{{display:flex;height:10px;border-radius:5px;overflow:hidden;background:var(--card);margin:8px 0}}
 .bar span{{display:block}}
 table{{border-collapse:collapse;width:100%;margin:6px 0 20px}}
 th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
 th{{font-size:13px;color:var(--mut)}}
 .st{{font-weight:600;white-space:nowrap}} .ty{{font-size:12px;color:var(--mut)}}
 details.tc{{border:1px solid var(--line);border-radius:8px;margin:8px 0;background:var(--card)}}
 details.tc>summary{{padding:10px 12px;cursor:pointer;font-weight:600;list-style:none;display:flex;gap:10px;align-items:center}}
 details.tc>summary::-webkit-details-marker{{display:none}}
 .dot{{width:9px;height:9px;border-radius:50%;flex:0 0 auto}}
 .body{{padding:4px 14px 14px}} .kv{{margin:8px 0}} .kv b{{display:block;color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.03em}}
 pre{{white-space:pre-wrap;word-break:break-word;background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:8px;font-size:12.5px;overflow:auto}}
 figure{{margin:8px 0}} img{{max-width:100%;border:1px solid var(--line);border-radius:6px}}
 figcaption{{color:var(--mut);font-size:12px}} .ev-missing{{color:{COLORS['Fail']};font-size:13px}}
 .issue{{border-left:3px solid {COLORS['Fail']};padding-left:10px;margin:6px 0}}
 .q{{border-left:3px solid {COLORS['Needs review']};padding-left:10px;margin:6px 0}}
 section{{margin-top:28px}} h2{{border-bottom:2px solid var(--line);padding-bottom:4px}}
 a{{color:#0969da}} @media(prefers-color-scheme:dark){{a{{color:#4493f8}}}}
 nav a{{margin-right:12px;white-space:nowrap}}
</style></head><body><div class="wrap">
<h1>{esc(a.project)} — test execution report</h1>
<div class="sub">{esc(datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z'))}"""
             + (f' · <a href="{esc(a.app_url)}">{esc(a.app_url)}</a>' if a.app_url else "")
             + (f' · {esc(a.notes)}' if a.notes else "") + "</div>"]

    parts.append("<div>" + "".join(chip(s, overall[s]) for s in STATUSES + ["Not run"] if overall.get(s)) + "</div>")
    parts.append(bar(overall, total))
    parts.append('<nav class="sub">' + "".join(
        f'<a href="#{esc(feat)}">{esc(feat)} ({len(rows)})</a>' for feat, _, rows in features) + "</nav>")

    if open_q:
        parts.append(f'<section><h2>Open questions ({len(open_q)})</h2>'
                     '<p class="sub">Carried from the test sheets or raised during the run. '
                     'Each affects the verdict of the case it belongs to.</p>')
        for cid, q in open_q:
            parts.append(f'<div class="q"><b>{esc(cid)}</b> — {esc(q)}</div>')
        parts.append("</section>")

    if created:
        parts.append(f'<section><h2>Data created during the run ({len(created)})</h2>'
                     '<table><tr><th>Test</th><th>Record</th><th>Cleanup</th><th>Detail</th></tr>')
        for cid, rec in created:
            parts.append(f'<tr><td>{esc(cid)}</td><td>{esc(rec.get("what"))}</td>'
                         f'<td>{esc(rec.get("cleanup"))}</td><td>{esc(rec.get("detail"))}</td></tr>')
        parts.append("</table></section>")

    for feat, ffile, rows in features:
        fc = Counter(r["status"] for r in rows)
        parts.append(f'<section id="{esc(feat)}"><h2>{esc(feat)}</h2>'
                     f'<div class="sub">{esc(ffile)}</div>'
                     + "".join(chip(s, fc[s]) for s in STATUSES + ["Not run"] if fc.get(s))
                     + bar(fc, sum(fc.values()) or 1))
        by_story = defaultdict(list)
        for r in rows:
            by_story[r.get("story", "")].append(r)
        for story, cases in by_story.items():
            parts.append(f'<h3>{esc(story)}</h3>')
            for r in cases:
                color = COLORS.get(r["status"], "#888")
                parts.append(
                    f'<details class="tc"><summary><span class="dot" style="background:{color}"></span>'
                    f'<span class="st" style="color:{color}">{esc(r["status"])}</span>'
                    f'<span class="ty">[{esc(r.get("type") or "?")}]</span>'
                    f'<span>{esc(r["id"])} — {esc(r.get("title"))}</span></summary><div class="body">')
                if r.get("summary"):
                    parts.append(f'<div class="kv">{esc(r["summary"])}</div>')
                for label, key in (("Expected", "expected"), ("Actual", "actual")):
                    if r.get(key):
                        parts.append(f'<div class="kv"><b>{label}</b><pre>{esc(r[key])}</pre></div>')
                if r.get("steps"):
                    parts.append('<div class="kv"><b>Steps</b><table><tr><th>#</th><th>Request</th><th>Result</th></tr>')
                    for st in r["steps"]:
                        parts.append(f'<tr><td>{esc(st.get("n"))}</td><td>{esc(st.get("request"))}</td>'
                                     f'<td>{esc(st.get("result"))}</td></tr>')
                    parts.append("</table></div>")
                for q in r.get("needs_clarification") or []:
                    parts.append(f'<div class="q">Open question: {esc(q)}</div>')
                for iss in r.get("issues") or []:
                    parts.append(f'<div class="issue">{esc(iss)}</div>')
                ev = r.get("evidence") or []
                if ev:
                    parts.append('<div class="kv"><b>Evidence</b>' + "".join(render_evidence(results_dir, e) for e in ev) + "</div>")
                meta = []
                if r.get("role"):
                    meta.append(f'role {esc(r["role"])}')
                if r.get("duration_ms"):
                    meta.append(f'{r["duration_ms"]} ms')
                if meta:
                    parts.append(f'<div class="sub">{" · ".join(meta)}</div>')
                parts.append("</div></details>")
        parts.append("</section>")

    parts.append(f'<section class="sub"><hr>Generated {esc(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))}. '
                 f'{len(results)} of {total} planned cases executed.</section></div></body></html>')

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Report: {out}  ({out.stat().st_size // 1024} KB)")
    print("Status totals: " + ", ".join(f"{s} {overall[s]}" for s in STATUSES + ["Not run"] if overall.get(s)))


if __name__ == "__main__":
    main()
