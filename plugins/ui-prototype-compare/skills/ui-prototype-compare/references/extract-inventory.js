// Run via the browser evaluate tool on EVERY prototype page and EVERY live page, at each breakpoint
// and in each theme mode. Returns an inventory of every visible UI element (not a fixed tag list) with
// computed styles, so the two sides can be diffed with references/diff-extracts.py.
// What counts as a UI element: any visible element that has its own text, is a form control / image /
// svg / canvas / video / iframe, is a landmark or list/table part, has a role or aria-label, or paints
// a box (background, border, shadow). Pure layout wrappers with no paint are skipped; their children
// are covered.
// Large pages: set OFFSET/LIMIT below and run again until `next` is null. Save each chunk to its own
// file; diff-extracts.py takes a comma-separated list per side.
// Fields: text = FULL visible text (cap 400); shape = text with digits/money/month/day names masked
// (the differ pairs by shape, so data changes are dynamic, not deviations); label = alt/aria-label/
// title/placeholder/name for textless elements; state = disabled/checked/selected/pressed/expanded/active.
// Password field values are never read.
(() => {
  const OFFSET = 0, LIMIT = 500;
  const props = [
    'fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'textTransform', 'textDecorationLine', 'color',
    'backgroundColor', 'backgroundImage', 'borderTopColor', 'borderTopWidth', 'borderTopStyle', 'borderRightWidth',
    'borderBottomWidth', 'borderLeftWidth', 'borderRadius', 'boxShadow',
    'marginTop', 'marginRight', 'marginBottom', 'marginLeft',
    'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
    'width', 'height', 'display', 'position', 'opacity', 'cursor', 'transition', 'gap', 'fill', 'stroke'
  ];
  const skipTag = new Set(['SCRIPT', 'STYLE', 'LINK', 'META', 'NOSCRIPT', 'TEMPLATE', 'HEAD', 'TITLE', 'BR', 'WBR', 'PATH', 'G', 'DEFS', 'USE']);
  const media = new Set(['IMG', 'SVG', 'CANVAS', 'VIDEO', 'IFRAME', 'INPUT', 'SELECT', 'TEXTAREA', 'BUTTON', 'PROGRESS', 'METER']);
  const landmark = new Set(['NAV', 'HEADER', 'FOOTER', 'ASIDE', 'MAIN', 'SECTION', 'FORM', 'TABLE', 'THEAD', 'TBODY', 'TR', 'TH', 'TD', 'UL', 'OL', 'LI', 'DIALOG']);
  const months = '(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*';
  const days = '(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*';
  const shapeOf = t => t
    .replace(/[£$€₹]\s?\d[\d,]*(?:\.\d+)?/g, '<money>')
    .replace(new RegExp('\\b' + months + '\\b', 'gi'), '<mon>')
    .replace(new RegExp('\\b' + days + '\\b', 'gi'), '<day>')
    .replace(/\d+/g, '#')
    .replace(/\s+/g, ' ').trim().toLowerCase();
  const path = el => {
    const parts = [];
    for (; el && el.nodeType === 1 && parts.length < 4; el = el.parentElement) {
      parts.unshift(el.tagName.toLowerCase() + (el.id ? '#' + el.id : ''));
    }
    return parts.join(' > ');
  };
  const stateOf = el => {
    const cn = typeof el.className === 'string' ? el.className : '';
    return {
      disabled: !!el.disabled || el.getAttribute('aria-disabled') === 'true',
      checked: !!el.checked,
      selected: el.getAttribute('aria-selected') === 'true',
      pressed: el.getAttribute('aria-pressed') === 'true',
      expanded: el.getAttribute('aria-expanded') === 'true',
      active: /\b(on|active|selected|current)\b/.test(cn)
    };
  };
  const ownText = el => [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').trim();
  const painted = cs =>
    (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)') || cs.backgroundImage !== 'none' ||
    cs.boxShadow !== 'none' ||
    ['Top', 'Right', 'Bottom', 'Left'].some(s => parseFloat(cs['border' + s + 'Width']) > 0 && cs['border' + s + 'Style'] !== 'none');
  const all = [...document.querySelectorAll('body, body *')].filter(el => {
    if (skipTag.has(el.tagName.toUpperCase())) return false;
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return false;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') return false;
    const tag = el.tagName.toUpperCase();
    return ownText(el) || media.has(tag) || landmark.has(tag) || /^H[1-6]$|^A$|^LABEL$|^P$/.test(tag) ||
      el.getAttribute('role') || el.getAttribute('aria-label') || painted(cs);
  });
  const slice = all.slice(OFFSET, OFFSET + LIMIT);
  return {
    vw: innerWidth, vh: innerHeight, dpr: devicePixelRatio, url: location.href,
    scheme: matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
    total: all.length, offset: OFFSET, next: OFFSET + LIMIT < all.length ? OFFSET + LIMIT : null,
    els: slice.map(el => {
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      const isPassword = el.type === 'password';
      const text = isPassword ? '' : (ownText(el) || (el.tagName === 'SELECT' ? '' : (el.innerText || el.value || ''))).trim().slice(0, 400);
      const label = (el.getAttribute('alt') || el.getAttribute('aria-label') || el.getAttribute('title') ||
        el.getAttribute('placeholder') || el.getAttribute('name') || '').trim();
      return {
        path: path(el),
        text,
        shape: shapeOf(text),
        label,
        state: stateOf(el),
        rect: { x: Math.round(r.x + scrollX), y: Math.round(r.y + scrollY), w: Math.round(r.width), h: Math.round(r.height) },
        style: Object.fromEntries(props.map(p => [p, cs[p]]))
      };
    })
  };
})();
