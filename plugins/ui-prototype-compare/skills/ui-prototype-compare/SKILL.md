---
name: ui-prototype-compare
description: Compares a UI/UX prototype (HTML/CSS/JS files, screenshots, PDF, or a Figma export/spec at a local path) against the live website at a given URL using the Playwright MCP browser. Takes the prototype path and the URL as arguments, never credentials (the user logs in in the browser). Inventories and compares every UI element page by page, then runs a theme pass over the whole site (design tokens, shared components, light/dark and brand themes), checking fonts, colours, spacing, layout, behaviour, hover/focus states, responsive breakpoints, accessibility and content. Writes an evidence-backed report as Markdown and as one self-contained HTML file. Use this whenever the user mentions comparing a prototype, mockup, design or Figma to the live/deployed/staging site, UI/UX review, design QA, design fidelity, theme or design-token consistency, "does the build match the design", pixel or CSS differences, or visual regression against a prototype, even if they do not say "compare".
---

# UI Prototype vs Live UI Comparison

The prototype is the source of truth. The job is to find every place the live site deviates from it and prove each deviation with evidence, so a developer can fix it without re-investigating. "Every place" is literal: every UI element on every page (the inventory), and the site's theme as a whole (the theme pass).

Arguments: the prototype path and the live URL, in either order. Nothing else is passed in. Everything else (project name, roles, breakpoints, themes, dynamic-content handling) is derived from the prototype and the live site, with the source of each value recorded in the report. Derived is not assumed: a value comes from evidence you can cite. Only when evidence is missing or contradicts itself do you ask the user, and until they answer, that part goes under Not verified.

## Hard rules (and why)

- **Never store prototypes in this repo.** The prototype stays at the path the user gave. Read it in place; do not copy it here. If it must be served over HTTP (see `references/prototype-sources.md`), serve it from its own folder.
- **Never ask for, read, log or store credentials.** Open the live URL in the Playwright MCP browser and ask the user to log in themselves in that window, then wait for them to say they are done. Do not type into login fields, do not screenshot the login form, do not save cookies or storage state to disk. Credentials in chat or files would end up in transcripts or git.
- **Destructive actions are allowed only on data you created.** Create test records with a recognisable marker (e.g. `ZZ-UIQA-<timestamp>`), keep a list of everything you create, and delete only items from that list. Never edit or delete pre-existing data. If you cannot tell whether a record is yours, leave it alone and note the behaviour as untested.
- **Same-origin only.** Do not follow links to other origins.
- Do not fill a gap with an assumption. Derive from evidence (below); if evidence is missing or contradictory, ask, and until answered list that part under Not verified with the reason, never as a finding.

## Deriving everything except the two arguments

Work these out yourself and write each value and its source into the report header. Ask only on the exceptions named.

| Value | How to derive it | Ask the user only if |
|---|---|---|
| Project name | Prototype folder path (the product or feature folder name) and the live hostname | the path and hostname give conflicting names |
| Prototype type | File extensions in the path: HTML/CSS/JS, images/PDF, Figma export or spec | the contents are an unfamiliar export (see `prototype-sources.md`) |
| Roles | Prototype file names, page titles, nav and role labels; on live, the role label after login, the nav and the route table. Screens per role are matched in step 4 | a screen's role cannot be told from either side |
| Breakpoints | Every `@media` width condition in the prototype's CSS (and inline styles), compared on live with the same widths, plus one common desktop width | never: if the prototype defines none, compare at desktop width only and list responsive behaviour as Not verified ("prototype defines no breakpoints") |
| Themes and switch method | See `references/theme-pass.md` section 1: CSS signals on both sides, then look for a theme control on live | a second theme is detected but no way to switch to it is found |
| Data parity | Count live records against the prototype's sample data once the live site is open | never: if live is empty and the prototype is seeded, say so in the report and compare static parts only unless marked test records are agreed |
| Logins | One login per role the live site exposes | always the user, in the browser; never credentials |

## Dynamic content: classify every difference, report all of them

This is not a user setting. Every visible difference is reported, none is hidden; the class decides where it is listed (`references/dynamic-content.md`):
- class S (static) differences are the findings, with severity;
- classes D, I, T, ST, C are listed in "Dynamic differences", tagged with their class and why they are dynamic, counted in their own summary column and never mixed into the static counts;
- P and E go under Needs confirmation and Observations.
Reporting everything tagged, rather than filtering, means nothing is silently dropped and the reader can overrule any classification.

## Dynamic content rules (how to classify)

A prototype is sample data, one user, one date and one UI state. The live site shows real data, the logged-in user, today's date and its current state. Names, counts, money, dates, periods, empty states, disabled buttons, unselected options and data- or role-dependent elements will differ without being defects. Read `references/dynamic-content.md` before comparing and classify every difference (S static, D data, I identity/role, T time/period, ST state, C conditional, P prototype inconsistency, E environment) before rating it. Only class S is rated straight away. In short:

- Never rate data values, usernames, dates, periods or counts; compare their format and styling for severity, and list the value difference as dynamic.
- Put the live page in the prototype's state where you can. A state-dependent difference (disabled, unselected, locked, empty, unpaired) is listed as dynamic (ST), never rated; what could not be aligned goes under Not verified.
- Never call an element missing until you know whether it is conditional. If you cannot tell, it goes under Needs confirmation.
- Never compare truncated text, and open collapsed controls before judging them.
- If the live site is empty and the prototype is seeded, say so up front in the report and compare the static parts only. Create marked test records (`ZZ-UIQA-...`) only if the user already told you to, and delete them afterwards.

## Workflow

1. **Load the prototype** per `references/prototype-sources.md`. Build an inventory of screens and, where possible, tokens (fonts, colours, sizes, spacing, radii, shadows).
2. **Open the live site** in the Playwright MCP browser, navigate to the start URL, and ask the user to log in inside that window if needed. Wait for confirmation. Repeat per role.
3. **Crawl** same-origin pages reachable from the start URL, recording each page's URL and title.
   Do not stop at the nav. Single-page apps answer HTTP 200 for every path, so also read the live app's route table (for example the router config in its JS bundle) to find screens that no link reaches, such as display screens or role-gated areas. Report routes you cannot open (role, token, no data) as Not verified with the reason.
4. **Match screens to live pages** automatically (title, route, heading, filename). If any match is ambiguous or missing, list the candidates and confirm with the user before comparing. Report unmatched prototype screens and unmatched live pages as gaps.
5. **Page-wise pass.** For each matched pair, at each breakpoint and theme mode, align state first (same role, same screen state, data as agreed), then:
   - Capture the **full inventory** of both sides with `references/extract-inventory.js` through the browser's evaluate tool (wrap the file's text as `() => (<script>)`, pass `filename` so the result is written to disk instead of flooding the context: one page is ~300 KB; repeat with OFFSET until `next` is null), and diff with `python -I -X utf8 references/diff-extracts.py proto.json[,chunk2.json] live.json[,chunk2.json]`. The differ separates static style diffs from dynamic text, state-differs, weak-paired and unpaired elements, and prints a COVERAGE section that must add up. Do not hand-copy mismatches from screenshots.
   - Trigger every hidden-until-interaction element (menus, modals, drawers, tooltips, dropdown options, tab panels, accordions, validation messages) and capture the inventory again in that state, so those elements are compared too.
   - Give every unpaired element a disposition (finding, Needs confirmation, or excluded with class). Before writing any wording difference, search the prototype source for the live wording (class P).
   - For static prototypes, compare against what is visible or specified and say that values are estimated.
6. **Theme pass** per `references/theme-pass.md`, after all pages are captured: run `references/extract-tokens.js` on every page of both sides, diff with `references/diff-tokens.py`, compare each shared component type once at theme level, and repeat for each theme mode the user confirmed.
7. **Test behaviour** on both sides where the prototype is interactive: hover, focus, active, disabled, click results, form validation messages, modals, menus, tabs. Static prototypes cannot prove behaviour; record behaviour checks as "not verifiable from prototype" rather than inventing an expectation.
8. **Capture proof** for every mismatch: a screenshot of the live element or page (and the prototype side when it can be rendered), plus the measured values. Save under the evidence folder below.
9. **Clean up**: delete only records you created, stop any local server you started, and close nothing the user opened.
10. **Write the report** from `references/report-template.md`, then render the HTML with `python -I -X utf8 scripts/render_html_report.py <report.md>`. Check the page-by-page coverage table before finishing: a page whose coverage does not add up, or whose inventory was incomplete, is listed as Not verified, not as compared.

## Severity

- **Critical**: missing/broken element or flow, behaviour that fails, content that is wrong, keyboard or accessibility blocker.
- **Major**: wrong font family, colour, size, layout structure or breakpoint behaviour that is visibly different.
- **Minor**: small spacing, radius, shadow, weight or timing differences.

Tokens are exact-match: report any difference, however small, and rate it by the above. Do not silently round or accept near-matches. This applies to static tokens (class S) only; see "Dynamic content".

Every finding carries a **confidence**: *Confirmed* (static, same state, measured on both sides) or *Needs confirmation* (possibly conditional, time-bound or prototype-inconsistent). Only Confirmed findings get a severity and count in the summary. Needs-confirmation items are listed separately with the question to answer. Things that are not prototype deviations (console or CSP errors, labels that look wrong against the real date) go under Observations and are not counted.

## Output

- Report: `reports/<project_name>_<YYYY-MM-DD>.md` and the same report as one self-contained `reports/<project_name>_<YYYY-MM-DD>.html` (the reports folder is in the repo; its contents are gitignored, only the empty folder is committed).
- Evidence: `reports/<project_name>_<YYYY-MM-DD>_evidence/`, referenced from the report by relative path. Every Critical, Major and Minor finding must link to its proof.
- Use the user's local date for `<YYYY-MM-DD>`. Do not overwrite an existing report with the same name; append `_2`, `_3`.
- Do not commit or push anything; the user does that.
- The report's "Dynamic differences" section lists every non-static difference with its class, so readers can see nothing was hidden and overrule a classification.
- The HTML file is built by `scripts/render_html_report.py`: screenshots embedded as data URIs, no external scripts, fonts or images, so it opens in any browser without an account. Do not hand-write it.
