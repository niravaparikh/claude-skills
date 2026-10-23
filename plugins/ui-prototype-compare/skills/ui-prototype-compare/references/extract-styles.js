// Run via the browser evaluate tool on both prototype and live page.
// Returns computed styles for visible interactive and text elements so the two can be diffed
// with references/diff-extracts.py.
// - text is the FULL visible text (capped at 400 chars), never a short prefix.
// - shape is the text with digits, currency amounts, month/day names and clock times masked,
//   so "£343" and "£0" or "18 Apr 2026" and "12 Oct 2026" have the same shape. The differ pairs
//   elements by shape and treats value changes as dynamic data, not as deviations.
// - state records disabled/checked/selected/pressed/expanded/locked flags. The differ keeps
//   style differences between elements in different states out of the findings.
// Password field values are never read.
(() => {
  const props = [
    'fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'textTransform', 'color',
    'backgroundColor', 'borderTopColor', 'borderTopWidth', 'borderTopStyle', 'borderRadius', 'boxShadow',
    'marginTop', 'marginRight', 'marginBottom', 'marginLeft',
    'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
    'width', 'height', 'display', 'position', 'opacity', 'cursor', 'transition'
  ];
  const sel = 'h1,h2,h3,h4,h5,h6,p,a,button,input,select,textarea,label,nav,header,footer,li,th,td,[role=button],[role=status]';
  const months = '(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*';
  const days = '(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*';
  const shapeOf = t => t
    .replace(/[£$€]\s?\d[\d,]*(?:\.\d+)?/g, '<money>')
    .replace(new RegExp('\\b' + months + '\\b', 'gi'), '<mon>')
    .replace(new RegExp('\\b' + days + '\\b', 'gi'), '<day>')
    .replace(/\d+/g, '#')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase();
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
  return {
    vw: innerWidth, vh: innerHeight, dpr: devicePixelRatio, url: location.href,
    els: [...document.querySelectorAll(sel)]
      .filter(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; })
      .slice(0, 600)
      .map(el => {
        const cs = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        const isPassword = el.type === 'password';
        const text = isPassword ? '' : (el.innerText || el.value || '').trim().slice(0, 400);
        return {
          path: path(el),
          text,
          shape: shapeOf(text),
          state: stateOf(el),
          rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) },
          style: Object.fromEntries(props.map(p => [p, cs[p]]))
        };
      })
  };
})();
