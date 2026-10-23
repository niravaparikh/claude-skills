---
name: ui-prototype-compare
description: Compares a UI/UX prototype (HTML/CSS/JS files, screenshots, PDF, or a Figma export/spec at a local path) against the live website at a given URL using the Playwright MCP browser, checking fonts, colours, spacing, layout, button and form behaviour, hover/focus states, responsive breakpoints, accessibility and content, and writes an evidence-backed Markdown report. Use this whenever the user mentions comparing a prototype, mockup, design or Figma to the live/deployed/staging site, UI/UX review, design QA, design fidelity, "does the build match the design", pixel or CSS differences, or visual regression against a prototype, even if they do not say "compare".
---

# UI Prototype vs Live UI Comparison

The prototype is the source of truth. The job is to find every place the live site deviates from it and prove each deviation with evidence, so a developer can fix it without re-investigating.

## Hard rules (and why)

- **Never store prototypes in this repo.** The prototype stays at the path the user gave. Read it in place; do not copy it here. If it must be served over HTTP (see `references/prototype-sources.md`), serve it from its own folder.
- **Never ask for, read, log or store credentials.** Open the live URL in the Playwright MCP browser and ask the user to log in themselves in that window, then wait for them to say they are done. Do not type into login fields, do not screenshot the login form, do not save cookies or storage state to disk. Credentials in chat or files would end up in transcripts or git.
- **Destructive actions are allowed only on data you created.** Create test records with a recognisable marker (e.g. `ZZ-UIQA-<timestamp>`), keep a list of everything you create, and delete only items from that list. Never edit or delete pre-existing data. If you cannot tell whether a record is yours, leave it alone and note the behaviour as untested.
- **Same-origin only.** Do not follow links to other origins.
- Do not guess missing inputs. If the project name, URL, prototype path or breakpoints are unknown or ambiguous, ask.

## Inputs to collect first

Ask for anything not yet provided:
1. Project name (used in the report file name).
2. Prototype path (file or folder) and its type: HTML/CSS/JS, images/PDF, Figma export or spec.
3. Live site start URL.
4. Responsive breakpoints to compare (no defaults; ask every run).
5. Data and role parity, asked once the live site is open: does the live environment hold data comparable to the prototype's sample data, and which role does the prototype show? See "Dynamic content" below.

## Dynamic content: do not report it as a mismatch

A prototype is sample data, one user, one date and one UI state. The live site shows real data, the logged-in user, today's date and its current state. Names, counts, money, dates, periods, empty states, disabled buttons, unselected options and data- or role-dependent elements will differ without being defects. Read `references/dynamic-content.md` before comparing and classify every difference (S static, D data, I identity/role, T time/period, ST state, C conditional, P prototype inconsistency, E environment) before rating it. Only class S is rated straight away. In short:

- Never compare data values, usernames, dates, periods or counts; compare their format and styling.
- Never report a state-dependent difference (disabled, unselected, locked, empty, unpaired). Put the live page in the prototype's state, or list it under Not verified.
- Never call an element missing until you know whether it is conditional. If you cannot tell, it goes under Needs confirmation.
- Never compare truncated text, and open collapsed controls before judging them.
- If the live site is empty and the prototype is seeded, say so up front and ask how to proceed (populated environment, marked test records, or static parts only).

## Workflow

1. **Load the prototype** per `references/prototype-sources.md`. Build an inventory of screens and, where possible, tokens (fonts, colours, sizes, spacing, radii, shadows).
2. **Open the live site** in the Playwright MCP browser, navigate to the start URL, and ask the user to log in inside that window if needed. Wait for confirmation.
3. **Crawl** same-origin pages reachable from the start URL, recording each page's URL and title.
   Do not stop at the nav. Single-page apps answer HTTP 200 for every path, so also read the live app's route table (for example the router config in its JS bundle) to find screens that no link reaches, such as display screens or role-gated areas. Report routes you cannot open (role, token, no data) as Not verified with the reason.
4. **Match screens to live pages** automatically (title, route, heading, filename). If any match is ambiguous or missing, list the candidates and confirm with the user before comparing. Report unmatched prototype screens and unmatched live pages as gaps.
5. **Align state, then compare each matched pair** at each breakpoint using `references/checklist.md`. First put both sides in comparable state (same role, same screen state, data as agreed). For runnable HTML prototypes and live pages, extract computed styles with `references/extract-styles.js` through the browser's evaluate tool, save each result to a file, and diff the pair with `python -I -X utf8 references/diff-extracts.py proto.json live.json`. The differ already separates static style diffs from dynamic text, state-differs and unpaired elements; do not hand-copy mismatches from screenshots. Before writing any wording difference, search the prototype source for the live wording (class P). For static prototypes, compare against what is visible or specified and say that values are estimated.
6. **Test behaviour** on both sides where the prototype is interactive: hover, focus, active, disabled, click results, form validation messages, modals, menus, tabs. Static prototypes cannot prove behaviour; record behaviour checks as "not verifiable from prototype" rather than inventing an expectation.
7. **Capture proof** for every mismatch: a screenshot of the live element or page (and the prototype side when it can be rendered), plus the measured values. Save under the evidence folder below.
8. **Clean up**: delete only records you created, stop any local server you started, and close nothing the user opened.
9. **Write the report** from `references/report-template.md`.

## Severity

- **Critical**: missing/broken element or flow, behaviour that fails, content that is wrong, keyboard or accessibility blocker.
- **Major**: wrong font family, colour, size, layout structure or breakpoint behaviour that is visibly different.
- **Minor**: small spacing, radius, shadow, weight or timing differences.

Tokens are exact-match: report any difference, however small, and rate it by the above. Do not silently round or accept near-matches. This applies to static tokens (class S) only; see "Dynamic content".

Every finding carries a **confidence**: *Confirmed* (static, same state, measured on both sides) or *Needs confirmation* (possibly conditional, time-bound or prototype-inconsistent). Only Confirmed findings get a severity and count in the summary. Needs-confirmation items are listed separately with the question to answer. Things that are not prototype deviations (console or CSP errors, labels that look wrong against the real date) go under Observations and are not counted.

## Output

- Report: `reports/<project_name>_<YYYY-MM-DD>.md` (the reports folder is in the repo; its contents are gitignored, only the empty folder is committed).
- Evidence: `reports/<project_name>_<YYYY-MM-DD>_evidence/`, referenced from the report by relative path. Every Critical, Major and Minor finding must link to its proof.
- Use the user's local date for `<YYYY-MM-DD>`. Do not overwrite an existing report with the same name; append `_2`, `_3`.
- Do not commit or push anything; the user does that.
- Include the "Excluded as dynamic or state-dependent" list from the template so readers can see what was filtered and overrule a classification.
- If the user asks for a single-page shareable report, build one self-contained HTML file with the screenshots embedded as data URIs, no external scripts, fonts or images, so it opens in any browser without an account.
