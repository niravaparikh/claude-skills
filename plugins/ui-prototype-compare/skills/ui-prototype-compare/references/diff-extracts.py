"""Diff two extract-inventory.js outputs (prototype vs live) without producing false mismatches.

Usage: python -I -X utf8 diff-extracts.py proto.json[,proto-2.json] live.json[,live-2.json]
(a comma-separated list merges chunks of one page that were extracted with OFFSET/LIMIT)

Sections printed:
  COVERAGE               every inventoried element ends up in exactly one bucket; the numbers must add up
  STATIC STYLE DIFFS     elements paired by tag + text shape (or tag + label), same state: real candidates for findings
  STATE-DIFFERS          paired but in different states (disabled/selected/...): do not report, align state first
  DYNAMIC TEXT           paired by shape but the text value differs (names, money, dates): never a finding
  ONLY IN PROTOTYPE / ONLY IN LIVE
                         unpaired elements: may be conditional (data, role, state). Verify the condition
                         before rating; see references/dynamic-content.md rule 5.
  WEAK-PAIRED            textless, unlabeled elements (icons, painted boxes) paired only by tag and order.
                         Treat as Needs confirmation, never as a rated finding on their own.
Width and height are skipped for table cells and other auto-sized elements; rect sizes are shown only for
fixed-size controls (button, input, select, a, h1-h6).
"""
import json
import re
import sys
from collections import defaultdict

FIXED = {'button', 'input', 'select', 'a', 'h1', 'h2', 'h3', 'textarea', 'img', 'svg'}
SKIP_ALWAYS = {'width', 'height'}


def load(arg):
    merged = None
    for path in arg.split(','):
        text = open(path, encoding='utf-8').read()
        data = json.loads(re.search(r'\{.*\}', text, re.S).group(0))
        if merged is None:
            merged = data
        else:
            merged['els'] = merged['els'] + data['els']
            merged['next'] = data.get('next')
    return merged


def tag(e):
    return e['path'].split(' > ')[-1].split('#')[0]


def norm(s):
    return re.sub(r'\s+', ' ', s).strip().lower()


def build(data):
    """Return (strong, weak): strong groups keyed by tag|shape or tag|@label; weak is textless unlabeled by tag."""
    strong, weak = defaultdict(list), defaultdict(list)
    for e in data['els']:
        shape = e.get('shape') or norm(e['text'])
        label = norm(e.get('label', ''))
        if shape:
            strong[tag(e) + '|' + shape].append(e)
        elif label:
            strong[tag(e) + '|@' + label].append(e)
        else:
            weak[tag(e)].append(e)
    return strong, weak


proto, live = load(sys.argv[1]), load(sys.argv[2])
(ps, pw), (ls, lw) = build(proto), build(live)
print('viewport proto %sx%s live %sx%s | scheme proto %s live %s' % (
    proto['vw'], proto['vh'], live['vw'], live['vh'], proto.get('scheme', '?'), live.get('scheme', '?')))
for side, d in (('prototype', proto), ('live', live)):
    if d.get('next') is not None:
        print('WARNING: %s inventory is incomplete (next=%s); extract the remaining chunk before concluding' % (side, d['next']))

static, state_diff, dynamic, weak_pairs = [], [], [], []
only_p, only_l = [], []
for k, plist in ps.items():
    llist = ls.get(k, [])
    for a, b in zip(plist, llist):
        if a.get('state') != b.get('state'):
            state_diff.append((k, a, b))
        else:
            static.append((k, a, b))
            if norm(a['text']) != norm(b['text']):
                dynamic.append((k, a, b))
    only_p += [(k, e) for e in plist[len(llist):]]
for k, llist in ls.items():
    plist = ps.get(k, [])
    only_l += [(k, e) for e in llist[len(plist):]]
for t in set(pw) | set(lw):
    a_list, b_list = pw.get(t, []), lw.get(t, [])
    for a, b in zip(a_list, b_list):
        weak_pairs.append((t, a, b))
    only_p += [(t + '|(no text, no label)', e) for e in a_list[len(b_list):]]
    only_l += [(t + '|(no text, no label)', e) for e in b_list[len(a_list):]]

n_proto, n_live = len(proto['els']), len(live['els'])
paired = len(static) + len(state_diff)
print('\n== COVERAGE ==')
print('prototype elements %d = paired %d + weak-paired %d + only-in-prototype %d' % (n_proto, paired, len(weak_pairs), len(only_p)))
print('live elements      %d = paired %d + weak-paired %d + only-in-live %d' % (n_live, paired, len(weak_pairs), len(only_l)))
if n_proto != paired + len(weak_pairs) + len(only_p) or n_live != paired + len(weak_pairs) + len(only_l):
    print('COVERAGE MISMATCH: some elements are unaccounted for, do not report this page as complete')


def style_diffs(a, b):
    diffs = [(p, a['style'][p], b['style'].get(p)) for p in a['style']
             if a['style'][p] != b['style'].get(p) and p not in SKIP_ALWAYS]
    size = ''
    if tag(a) in FIXED and (a['rect']['w'], a['rect']['h']) != (b['rect']['w'], b['rect']['h']):
        size = ' size proto %sx%s live %sx%s' % (a['rect']['w'], a['rect']['h'], b['rect']['w'], b['rect']['h'])
    return diffs, size


print('\n== STATIC STYLE DIFFS (same state) ==')
n = 0
for k, a, b in static:
    diffs, size = style_diffs(a, b)
    if diffs or size:
        n += 1
        print('\n[%s]%s' % (k[:70], size))
        for p, x, y in diffs:
            print('   %s: proto=%s | live=%s' % (p, str(x)[:70], str(y)[:70]))
print('\nelements with style diffs: %d of %d paired' % (n, len(static)))

print('\n== STATE-DIFFERS (do not report; align state and re-check) ==')
for k, a, b in state_diff:
    print('  %s  proto-state=%s live-state=%s' % (k[:60], {s: v for s, v in a['state'].items() if v}, {s: v for s, v in b['state'].items() if v}))

print('\n== DYNAMIC TEXT (same shape, different value: data/time, never a finding) ==')
for k, a, b in dynamic:
    print('  %s: proto=%r live=%r' % (tag(a), a['text'][:60], b['text'][:60]))

print('\n== WEAK-PAIRED (textless, unlabeled; Needs confirmation only) ==')
for t, a, b in weak_pairs:
    diffs, size = style_diffs(a, b)
    if diffs or size:
        print('  %s at proto(%d,%d) live(%d,%d)%s: %s' % (
            t, a['rect']['x'], a['rect']['y'], b['rect']['x'], b['rect']['y'], size,
            ', '.join('%s %s->%s' % (p, str(x)[:24], str(y)[:24]) for p, x, y in diffs[:6])))

print('\n== ONLY IN PROTOTYPE (check condition before calling it missing) ==')
for k, e in only_p:
    print('  ' + k[:100])
print('\n== ONLY IN LIVE ==')
for k, e in only_l:
    print('  ' + k[:100])
