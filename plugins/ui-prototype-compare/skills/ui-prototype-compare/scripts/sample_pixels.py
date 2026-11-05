"""Estimate visual styling from a screenshot, for targets that expose no computed styles (Flutter web, canvas apps,
image-only prototypes). Dependency-free: decodes 8-bit PNGs itself.

Usage:
  python -I -X utf8 sample_pixels.py shot.png elements.json out.json [--dpr 1]
    elements.json: {"els":[{"label": "...", "x":..,"y":..,"w":..,"h":..}, ...]}  (CSS px, page coordinates)
    out.json: per element estimated bg colour, text colour, corner radius, plus the page palette

  python -I -X utf8 sample_pixels.py ink shot.png x,y,w,h [x,y,w,h ...]
    prints the tight bounding box of the text/graphics pixels inside each region (rendered text height and width)

  Run the SAME script on the prototype's screenshot as well as the live one, so both sides are measured the same way,
  and compare the estimates with each other (never with exact computed values: antialiasing and scaling add noise).

Every number is an ESTIMATE from pixels (colours quantised to 1 level, radius to ~1px). Report them as "estimated
from pixels". Screenshots must be taken at device scale factor 1 and without scrolling (y relative to the screenshot).
"""
import json
import struct
import sys
import zlib
from collections import Counter


def read_png(path):
    data = open(path, 'rb').read()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise SystemExit('not a PNG: ' + path)
    pos, idat, w = 8, b'', None
    while pos < len(data):
        n, typ = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if typ == b'IHDR':
            w, h, depth, ctype, _, _, interlace = struct.unpack('>IIBBBBB', body)
            if depth != 8 or ctype not in (2, 6) or interlace:
                raise SystemExit('unsupported PNG (need 8-bit RGB/RGBA, non-interlaced)')
            bpp = 3 if ctype == 2 else 4
        elif typ == b'IDAT':
            idat += body
        pos += 12 + n
    raw, stride = zlib.decompress(idat), w * bpp
    rows, prev = [], bytearray(stride)
    for y in range(h):
        f, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + ((a + b) >> 1)) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line)
        prev = line
    return w, h, bpp, rows


def hexc(c):
    return '#%02x%02x%02x' % c


def ink(png, regions):
    """Tight bounding box of the pixels that differ from the region's background, for each x,y,w,h region.
    Measures rendered text (height of a line of caps, width of a string) the same way on both sides."""
    W, H, bpp, rows = read_png(png)
    out = []
    for x, y, w, h in regions:
        pts = [(rows[j][i * bpp], rows[j][i * bpp + 1], rows[j][i * bpp + 2])
               for j in range(y, min(y + h, H)) for i in range(x, min(x + w, W))]
        bg = Counter(pts).most_common(1)[0][0]
        xs, ys = [], []
        for j in range(y, min(y + h, H)):
            for i in range(x, min(x + w, W)):
                c = (rows[j][i * bpp], rows[j][i * bpp + 1], rows[j][i * bpp + 2])
                if abs(c[0] - bg[0]) + abs(c[1] - bg[1]) + abs(c[2] - bg[2]) > 90:
                    xs.append(i)
                    ys.append(j)
        out.append({'region': [x, y, w, h], 'bg': hexc(bg),
                    'ink': [min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1] if xs else None})
    return out


def main():
    if sys.argv[1] == 'ink':
        # sample_pixels.py ink shot.png x,y,w,h [x,y,w,h ...]  -> JSON lines
        for r in ink(sys.argv[2], [tuple(int(v) for v in a.split(',')) for a in sys.argv[3:]]):
            print(json.dumps(r))
        return
    png, els_path, out_path = sys.argv[1:4]
    dpr = float(sys.argv[sys.argv.index('--dpr') + 1]) if '--dpr' in sys.argv else 1.0
    W, H, bpp, rows = read_png(png)

    def px(x, y):
        x, y = min(max(int(x), 0), W - 1), min(max(int(y), 0), H - 1)
        r = rows[y]
        return (r[x * bpp], r[x * bpp + 1], r[x * bpp + 2])

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

    palette = Counter()
    for y in range(0, H, 2):
        r = rows[y]
        for x in range(0, W, 2):
            palette[(r[x * bpp], r[x * bpp + 1], r[x * bpp + 2])] += 1
    total = sum(palette.values())
    result = {'size': [W, H], 'dpr': dpr,
              'palette': [{'hex': hexc(c), 'share': round(n / total, 4)} for c, n in palette.most_common(24)], 'els': []}

    for e in json.load(open(els_path, encoding='utf-8'))['els']:
        x0, y0, w, h = [int(round(e[k] * dpr)) for k in ('x', 'y', 'w', 'h')]
        if w < 4 or h < 4 or x0 >= W or y0 >= H:
            continue
        x1, y1 = min(x0 + w, W) - 1, min(y0 + h, H) - 1
        ring = Counter(px(x, y) for x in range(x0 + 1, x1, 2) for y in (y0 + 2, y1 - 2))
        ring.update(px(x, y) for y in range(y0 + 1, y1, 2) for x in (x0 + 2, x1 - 2))
        bg = ring.most_common(1)[0][0] if ring else (0, 0, 0)
        inner = Counter(px(x, y) for x in range(x0 + 2, x1 - 1, 2) for y in range(y0 + 2, y1 - 1, 2))
        fg = None
        for c, n in inner.most_common(40):
            if dist(c, bg) > 120:
                fg = c
                break
        radius = 0
        for i in range(0, min(w, h) // 2 + 1):          # first pixel on the top row that is the box colour
            if dist(px(x0 + i, y0), bg) < 24 or dist(px(x0 + i, y0 + 1), bg) < 24:
                radius = i
                break
        outside = px(x0 - 3, y0 + h // 2)
        result['els'].append({
            'label': e.get('label', ''), 'rect': [x0, y0, w, h], 'bg': hexc(bg),
            'fg': hexc(fg) if fg else None, 'radius_px_est': radius,
            'edge_outside': hexc(outside), 'box_distinct': dist(bg, outside) > 12})
    json.dump(result, open(out_path, 'w', encoding='utf-8'), indent=1)
    print('wrote %s: %d elements, palette %d colours' % (out_path, len(result['els']), len(result['palette'])))


main()
