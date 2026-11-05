// Run via the browser evaluate tool once per page, per theme mode, on both sides. Returns the theme
// facts of that page: declared CSS custom properties, every distinct value actually used on screen
// (colours, fonts, sizes, radii, shadows, spacing) with usage counts, loaded font faces, and theme
// signals (colour-scheme, prefers-color-scheme rules, theme attributes). Compare with
// references/diff-tokens.py.
(() => {
  const root = document.documentElement;
  const rcs = getComputedStyle(root);
  const custom = {};
  let blocked = 0;
  const hasDarkRule = { value: false };
  const walk = rules => {
    for (const rule of rules) {
      if (rule.media && /prefers-color-scheme/.test(rule.media.mediaText)) hasDarkRule.value = true;
      if (rule.cssRules) walk(rule.cssRules);
      if (rule.style) {
        for (const name of rule.style) {
          if (name.startsWith('--') && /^(:root|html|body)$/.test((rule.selectorText || '').trim())) {
            custom[name] = rcs.getPropertyValue(name).trim();
          }
        }
      }
    }
  };
  for (const sheet of document.styleSheets) {
    try { walk(sheet.cssRules); } catch (e) { blocked++; }   // cross-origin sheet is unreadable: say so in the report
  }
  const tally = {};
  const bump = (k, v) => { if (v) { tally[k] = tally[k] || {}; tally[k][v] = (tally[k][v] || 0) + 1; } };
  const clear = v => v && v !== 'rgba(0, 0, 0, 0)' && v !== 'none' && v !== '0px' && v !== 'normal';
  for (const el of document.body.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) continue;
    const cs = getComputedStyle(el);
    const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (hasText) {
      bump('color', cs.color); bump('fontFamily', cs.fontFamily); bump('fontSize', cs.fontSize);
      bump('fontWeight', cs.fontWeight); bump('lineHeight', cs.lineHeight);
      if (clear(cs.letterSpacing)) bump('letterSpacing', cs.letterSpacing);
    }
    if (clear(cs.backgroundColor)) bump('backgroundColor', cs.backgroundColor);
    if (clear(cs.borderTopColor) && parseFloat(cs.borderTopWidth) > 0) bump('borderColor', cs.borderTopColor);
    if (clear(cs.borderRadius)) bump('borderRadius', cs.borderRadius);
    if (clear(cs.boxShadow)) bump('boxShadow', cs.boxShadow);
    for (const p of ['paddingTop', 'paddingLeft', 'marginTop', 'marginLeft', 'gap']) if (clear(cs[p])) bump('spacing', cs[p]);
  }
  const fonts = [...document.fonts].map(f => f.family.replace(/["']/g, '') + ' ' + f.weight + ' ' + f.status);
  const sig = [];
  for (const a of ['data-theme', 'data-bs-theme', 'data-color-mode', 'class']) {
    const v = root.getAttribute(a) || document.body.getAttribute(a);
    if (v && (a !== 'class' || /dark|light|theme/i.test(v))) sig.push(a + '=' + v);
  }
  const metaTheme = document.querySelector('meta[name=theme-color]');
  return {
    url: location.href, title: document.title, vw: innerWidth, lang: root.lang || '',
    scheme: matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
    colorScheme: rcs.colorScheme, prefersColorSchemeRules: hasDarkRule.value,
    themeSignals: sig, metaThemeColor: metaTheme ? metaTheme.content : '',
    bodyBackground: getComputedStyle(document.body).backgroundColor,
    custom, blockedStylesheets: blocked, fontFaces: fonts, tally
  };
})();
