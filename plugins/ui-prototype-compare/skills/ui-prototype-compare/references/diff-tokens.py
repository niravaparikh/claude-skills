"""Theme-level diff of extract-tokens.js outputs (prototype vs live), across pages and theme modes.

Usage: python -I -X utf8 diff-tokens.py --proto p1.json p2.json ... --live l1.json l2.json ...
Run once per theme mode (light, dark, brand A ...) with the files captured in that mode.

Prints:
  THEME SET            for each side, every distinct colour / font / size / radius / shadow / spacing value
                       used on any page, with the number of pages it appears on
  ONLY IN PROTOTYPE / ONLY IN LIVE
                       theme values one side uses that the other never does (palette, type scale, radii ...)
  PAGE DRIFT           values used on exactly one page of a side while that side has >= 3 pages: candidates for
                       one-off styling that breaks the theme. Verify before reporting.
  CUSTOM PROPERTIES    declared --vars; names may legitimately differ, so values are compared, not names
  THEME SIGNALS        colour-scheme, prefers-color-scheme rules, theme attributes, loaded fonts, lang
Values are compared exactly (computed rgb()/px strings). Counts are page counts, not element counts.
"""
import json
import re
import sys
from collections import defaultdict


def parse(argv):
    sides, cur = {'--proto': [], '--live': []}, None
    for a in argv:
        if a in sides:
            cur = a
        elif cur:
            sides[cur].append(a)
    return sides['--proto'], sides['--live']


def load(path):
    text = open(path, encoding='utf-8').read()
    return json.loads(re.search(r'\{.*\}', text, re.S).group(0))


def theme_set(pages):
    """{category: {value: set(page urls)}}"""
    out = defaultdict(lambda: defaultdict(set))
    for p in pages:
        for cat, vals in p['tally'].items():
            for v in vals:
                out[cat][v].add(p['url'])
    return out


pfiles, lfiles = parse(sys.argv[1:])
if not pfiles or not lfiles:
    sys.exit('usage: diff-tokens.py --proto a.json ... --live b.json ...')
P, L = [load(f) for f in pfiles], [load(f) for f in lfiles]
pset, lset = theme_set(P), theme_set(L)

print('== THEME SET (value: pages used on) ==')
for name, s, pages in (('prototype', pset, P), ('live', lset, L)):
    print('\n%s (%d pages)' % (name, len(pages)))
    for cat in sorted(s):
        print('  %s: %s' % (cat, '; '.join('%s [%d]' % (v[:48], len(u)) for v, u in sorted(s[cat].items(), key=lambda x: -len(x[1])))))

for name, a, b in (('ONLY IN PROTOTYPE', pset, lset), ('ONLY IN LIVE', lset, pset)):
    print('\n== %s ==' % name)
    for cat in sorted(a):
        extra = sorted(set(a[cat]) - set(b.get(cat, {})))
        if extra:
            print('  %s: %s' % (cat, '; '.join(e[:60] for e in extra)))

print('\n== PAGE DRIFT (value on exactly one page, side has >= 3 pages) ==')
for name, s, pages in (('prototype', pset, P), ('live', lset, L)):
    if len(pages) < 3:
        print('  %s: fewer than 3 pages, not assessed' % name)
        continue
    for cat in sorted(s):
        for v, urls in s[cat].items():
            if len(urls) == 1 and cat in ('color', 'backgroundColor', 'borderColor', 'fontFamily', 'fontSize', 'borderRadius', 'boxShadow'):
                print('  %s %s %s only on %s' % (name, cat, v[:48], next(iter(urls))))

print('\n== CUSTOM PROPERTIES (value-level) ==')
for name, pages in (('prototype', P), ('live', L)):
    merged = {}
    for p in pages:
        merged.update(p['custom'])
    blocked = sum(p.get('blockedStylesheets', 0) for p in pages)
    print('  %s: %d declared%s' % (name, len(merged), ' (%d cross-origin stylesheets unreadable)' % blocked if blocked else ''))
pvals = {v for p in P for v in p['custom'].values()}
lvals = {v for p in L for v in p['custom'].values()}
print('  values declared only in prototype: %s' % sorted(pvals - lvals)[:60])
print('  values declared only in live: %s' % sorted(lvals - pvals)[:60])

print('\n== THEME SIGNALS ==')
for name, pages in (('prototype', P), ('live', L)):
    for p in pages[:1]:
        print('  %s: scheme=%s colorScheme=%s prefersColorSchemeRules=%s signals=%s metaThemeColor=%r lang=%r' % (
            name, p['scheme'], p['colorScheme'], p['prefersColorSchemeRules'], p['themeSignals'], p['metaThemeColor'], p['lang']))
    fonts = sorted({f for p in pages for f in p['fontFaces']})
    print('  %s fonts loaded: %s' % (name, fonts))
