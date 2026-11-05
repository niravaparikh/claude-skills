# Theme pass: compare the site's theme, not just its pages

A page can match while the theme drifts (a one-off grey, a second font, a radius nobody designed). The theme pass checks the system the pages are built from. Run it after the page-wise pass, because the page data (`extract-tokens.js` per page) feeds it.

## 1. Derive which themes exist (no arguments, no guessing)

Find the themes from evidence on both sides, and write the evidence into the report:
1. **Prototype source:** search its CSS/JS for `prefers-color-scheme`, `color-scheme`, `[data-theme]`/`data-bs-theme`/theme classes, additional sets of custom properties under a theme selector, and theme names or tenant/brand names in switchers.
2. **Live runtime:** read `themeSignals`, `colorScheme` and `prefersColorSchemeRules` from `extract-tokens.js`, then look in the live UI (header, user menu, settings, footer) for a theme or brand control and check the route table for theme or tenant settings.
3. **Switch method:** the control you found (UI toggle, setting, URL parameter, tenant selection), or OS colour scheme when the CSS has `prefers-color-scheme` rules and no control exists.
4. **No signals and no control on either side** means "single theme on both sides (no theme signals or controls found)". Skip modes. Do not invent a dark mode to test.
5. **Ask the user only** when a second theme is detected (a signal or a control) but you cannot find how to switch to it, or when the two sides disagree about which themes exist. Until answered, that theme is Not verified.

## 2. Switch and capture, per theme mode

- UI toggle, URL parameter or tenant setting: use the switch you found, in the browser, on both sides.
- OS colour scheme: the Playwright `browser_emulate_media` tool with `colorScheme` set to `light` or `dark`, only when the CSS defines `prefers-color-scheme` rules for it. Record that the mode was emulated.
- Tenant or account themes that need another login: ask the user to log in as that tenant in the browser window. Never request or store credentials.
- Capture every page again in each mode (`extract-inventory.js` and `extract-tokens.js`). A theme mode that was not recaptured is "Not verified", never "matches".

## 3. Compare token sets

Per mode, run `python -I -X utf8 references/diff-tokens.py --proto <all prototype token files> --live <all live token files>`. It reports:
- Colours, fonts, sizes, weights, line-heights, letter-spacing, radii, shadows and spacing used on one side but never on the other.
- Values used on a single page only (page drift): candidates for one-off styling that breaks the theme. Verify in the page extract before reporting.
- Declared CSS custom properties, compared by value (names may differ without a defect).
- Theme signals, loaded fonts, `lang`.
Compare **computed values** exactly. A token that exists on the live site only through a library default is still a live value; report it.

## 4. Shared components, once at theme level

For each component type (header, sidebar/nav, footer, page title bar, buttons by variant, inputs/selects/textareas, tables, cards, badges/chips, modals, toasts, tabs, pagination, empty states), pick one prototype instance and one live instance, compare every property of the checklist, then confirm every other instance on each side uses the same values. Record a component-level finding once ("primary button radius 8px vs 6px, all 31 instances") instead of repeating it per page; the page-wise table then references it.

## 5. Theme findings

Rate with the same severity scale as pages. Theme findings that affect every page are counted once in the summary and list the number of pages affected. Anything where the prototype itself is inconsistent across its pages (class P) goes under Needs confirmation.
