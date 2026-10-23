"""Diff two extract-styles.js outputs (prototype vs live) without producing false mismatches.

Usage: python -I -X utf8 diff-extracts.py proto.json live.json

Sections printed:
  STATIC STYLE DIFFS     elements paired by tag + text shape, same state: real candidates for findings
  STATE-DIFFERS          paired but in different states (disabled/selected/...): do not report, align state first
  DYNAMIC TEXT           paired by shape but the text value differs (names, money, dates): never a finding
  ONLY IN PROTOTYPE / ONLY IN LIVE
                         unpaired elements: may be conditional (data, role, state). Verify the condition
                         before rating; see references/dynamic-content.md rule 5.
Width and height are skipped for table cells and other auto-sized elements; rect sizes are shown only for
fixed-size controls (button, input, select, a, h1-h6).
"""
import json
import re
import sys
from collections import defaultdict

FIXED = {'button', 'input', 'select', 'a', 'h1', 'h2', 'h3', 'textarea'}
SKIP_ALWAYS = {'width', 'height'}


def load(path):
    text = open(path, encoding='utf-8').read()
    return json.loads(re.search(r'\{.*\}', text, re.S).group(0))


def tag(e):
    return e['path'].split(' > ')[-1].split('#')[0]


def key(e):
    return tag(e) + '|' + (e.get('shape') or re.sub(r'\s+', ' ', e['text']).lower())


def index(data):
    groups = defaultdict(list)
    for e in data['els']:
        if e['text']:
            groups[key(e)].append(e)
    return groups


def norm(s):
    return re.sub(r'\s+', ' ', s).strip().lower()


proto, live = load(sys.argv[1]), load(sys.argv[2])
pi, li = index(proto), index(live)
print('viewport proto %sx%s live %sx%s' % (proto['vw'], proto['vh'], live['vw'], live['vh']))

static, state_diff, dynamic = [], [], []
for k, plist in pi.items():
    if k not in li:
        continue
    # pair the n-th occurrence on each side
    for a, b in zip(plist, li[k]):
        if a.get('state') != b.get('state'):
            state_diff.append((k, a, b))
        elif norm(a['text']) != norm(b['text']):
            dynamic.append((k, a, b))
            static.append((k, a, b))  # still compare styles of the element
        else:
            static.append((k, a, b))

print('\n== STATIC STYLE DIFFS (same state) ==')
n = 0
for k, a, b in static:
    t = tag(a)
    diffs = [(p, a['style'][p], b['style'][p]) for p in a['style']
             if a['style'][p] != b['style'][p] and p not in SKIP_ALWAYS]
    size = ''
    if t in FIXED and (a['rect']['w'], a['rect']['h']) != (b['rect']['w'], b['rect']['h']):
        size = ' size proto %sx%s live %sx%s' % (a['rect']['w'], a['rect']['h'], b['rect']['w'], b['rect']['h'])
    if diffs or size:
        n += 1
        print('\n[%s]%s' % (k[:70], size))
        for p, x, y in diffs:
            print('   %s: proto=%s | live=%s' % (p, x[:70], y[:70]))
print('\nelements with style diffs: %d' % n)

print('\n== STATE-DIFFERS (do not report; align state and re-check) ==')
for k, a, b in state_diff:
    print('  %s  proto-state=%s live-state=%s' % (k[:60], {s: v for s, v in a['state'].items() if v}, {s: v for s, v in b['state'].items() if v}))

print('\n== DYNAMIC TEXT (same shape, different value: data/time, never a finding) ==')
for k, a, b in dynamic:
    print('  %s: proto=%r live=%r' % (tag(a), a['text'][:60], b['text'][:60]))

print('\n== ONLY IN PROTOTYPE (check condition before calling it missing) ==')
for k in pi:
    if k not in li:
        print('  ' + k[:100])
print('\n== ONLY IN LIVE ==')
for k in li:
    if k not in pi:
        print('  ' + k[:100])
