"""Render the Markdown comparison report as ONE self-contained HTML file.

Usage: python -I -X utf8 render_html_report.py reports/<project>_<date>.md [out.html]

Images referenced in the Markdown (the evidence folder), whether as ![](img) or as a link to an image file, are
embedded as data: URIs (links become an expandable inline image), so the file opens in any
browser with no account, no external scripts, fonts or images. No third-party packages. Supports headings,
tables, images, links, bullet and numbered lists, bold, inline code, fenced code and horizontal rules, which
is everything references/report-template.md uses.
Exit 1 if a referenced image is missing, so a broken evidence link is caught before the report is shared.
"""
import base64
import html
import mimetypes
import re
import sys
from pathlib import Path

CSS = """
:root{--bg:#fff;--fg:#111827;--muted:#6b7280;--line:#e5e7eb;--head:#f3f4f6;--code:#f3f4f6;--link:#1d4ed8;
--crit:#b91c1c;--major:#b45309;--minor:#1d4ed8}
@media (prefers-color-scheme:dark){:root{--bg:#0f172a;--fg:#e5e7eb;--muted:#94a3b8;--line:#334155;--head:#1e293b;
--code:#1e293b;--link:#93c5fd;--crit:#fca5a5;--major:#fcd34d;--minor:#93c5fd}}
body{font:14px/1.55 system-ui,-apple-system,Segoe UI,sans-serif;background:var(--bg);color:var(--fg);margin:0 auto;
max-width:1200px;padding:24px 16px}
h1{font-size:24px}h2{font-size:19px;margin-top:32px;border-bottom:1px solid var(--line);padding-bottom:4px}
h3{font-size:16px;margin-top:24px}a{color:var(--link)}
table{border-collapse:collapse;width:100%;margin:12px 0;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}th{background:var(--head)}
code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:12.5px}
pre{background:var(--code);padding:12px;border-radius:6px;overflow-x:auto}pre code{padding:0}
img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:4px;display:block;margin:6px 0}
td img{max-width:360px}details{margin:2px 0}summary{cursor:pointer;color:var(--link)}hr{border:0;border-top:1px solid var(--line)}
.sev-Critical{color:var(--crit);font-weight:600}.sev-Major{color:var(--major);font-weight:600}
.sev-Minor{color:var(--minor);font-weight:600}
"""


def embed(src, base, missing):
    p = (base / src).resolve()
    if not p.is_file():
        missing.append(src)
        return src
    mime = mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
    return 'data:%s;base64,%s' % (mime, base64.b64encode(p.read_bytes()).decode())


def inline(text, base, missing):
    out = html.escape(text, quote=False)
    out = re.sub(r'!\[([^\]]*)\]\(&lt;?([^)&]+?)&gt;?\)|!\[([^\]]*)\]\(([^)]+)\)',
                 lambda m: '<img alt="%s" src="%s">' % (
                     html.escape(m.group(1) or m.group(3) or '', quote=True),
                     embed(html.unescape(m.group(2) or m.group(4)).strip('<>'), base, missing)), out)
    def link(m):
        target = html.unescape(m.group(2))
        if re.search(r'\.(png|jpe?g|gif|webp|svg)$', target, re.I) and not re.match(r'\w+://', target):
            # a link to a local evidence image: embed it, collapsed under the link text (browsers block data: navigation)
            return '<details><summary>%s</summary><img alt="%s" src="%s"></details>' % (
                m.group(1), html.escape(m.group(1), quote=True), embed(target, base, missing))
        return '<a href="%s">%s</a>' % (html.escape(target, quote=True), m.group(1))
    out = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, out)
    out = re.sub(r'`([^`]+)`', r'<code>\1</code>', out)
    out = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', out)
    out = re.sub(r'\b(Critical|Major|Minor)\b(?=\s*$)', r'<span class="sev-\1">\1</span>', out)
    return out


def render(md, base, missing):
    lines, out, i = md.splitlines(), [], 0
    title = 'UI comparison report'
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('```'):
            j = i + 1
            while j < len(lines) and not lines[j].startswith('```'):
                j += 1
            out.append('<pre><code>%s</code></pre>' % html.escape('\n'.join(lines[i + 1:j])))
            i = j + 1
        elif re.match(r'^#{1,6} ', ln):
            n = len(ln) - len(ln.lstrip('#'))
            text = ln[n:].strip()
            if n == 1 and title == 'UI comparison report':
                title = text
            out.append('<h%d>%s</h%d>' % (n, inline(text, base, missing), n))
            i += 1
        elif ln.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s:|-]+\|?\s*$', lines[i + 1]):
            cells = lambda s: [c.strip() for c in s.strip().strip('|').split('|')]
            head, rows, i = cells(ln), [], i + 2
            while i < len(lines) and lines[i].startswith('|'):
                rows.append(cells(lines[i]))
                i += 1
            t = '<table><thead><tr>%s</tr></thead><tbody>' % ''.join('<th>%s</th>' % inline(c, base, missing) for c in head)
            for r in rows:
                t += '<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c, base, missing) for c in r)
            out.append(t + '</tbody></table>')
        elif re.match(r'^\s*([-*]|\d+\.) ', ln):
            tag = 'ol' if re.match(r'^\s*\d+\.', ln) else 'ul'
            items = []
            while i < len(lines) and re.match(r'^\s*([-*]|\d+\.) ', lines[i]):
                items.append(re.sub(r'^\s*([-*]|\d+\.) ', '', lines[i]))
                i += 1
            out.append('<%s>%s</%s>' % (tag, ''.join('<li>%s</li>' % inline(x, base, missing) for x in items), tag))
        elif re.match(r'^-{3,}\s*$', ln):
            out.append('<hr>')
            i += 1
        elif ln.strip():
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,6} |```|\||\s*([-*]|\d+\.) )', lines[i]):
                para.append(lines[i])
                i += 1
            out.append('<p>%s</p>' % inline(' '.join(para), base, missing))
        else:
            i += 1
    return title, '\n'.join(out)


def main():
    src = Path(sys.argv[1])
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix('.html')
    missing = []
    title, body = render(src.read_text(encoding='utf-8'), src.parent, missing)
    dest.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width,initial-scale=1"><title>%s</title>'
                    '<style>%s</style></head><body>%s</body></html>' % (html.escape(title), CSS, body), encoding='utf-8')
    print('wrote %s (%d KB)' % (dest, dest.stat().st_size // 1024))
    if missing:
        print('MISSING IMAGES (not embedded):\n  ' + '\n  '.join(sorted(set(missing))))
        sys.exit(1)


main()
