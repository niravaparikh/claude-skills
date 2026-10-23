# Static vs dynamic: what counts as a deviation

A prototype is sample data, one user, one date and one UI state. The live site is real data, the logged-in user, today and whatever state it is in. Most text and many elements legitimately differ. A difference is only a finding if it would still be there with the same data, user, date and state.

Classify every difference into one class **before** rating it. Only class S can be rated Critical, Major or Minor straight away.

| Class | What it is | Examples (from a real run) | What to do |
|---|---|---|---|
| **S** Static | Same on every load for every user: layout, labels, headings, tokens, icons, fixed microcopy | `h1` 20px vs 26px; column header "Bonus remaining" vs "Base pot"; button colours; literal text `version undefined` | Compare exactly and rate. |
| **D** Data | Values from records: names, counts, money, percentages, rankings, table rows, column widths that depend on cell content | "Helen Marsden" vs "Super-Admin"; "£343" vs "£0"; "8 Green" vs "0"; audit rows; auto-sized table columns | Never compare values. Compare only the format (currency symbol, decimals, units, truncation, empty-state wording) and the styling of the element. |
| **I** Identity or role | The logged-in user's name, initials, avatar, role label, role-gated menus | Header chip name; "Super Admin" badge | Compare only if the user told you which role the prototype shows and the live session matches it. Otherwise treat as D. |
| **T** Time or period | Dates, weeks, quarters, "today", clocks, "Q2 2026 - Week 3 of 13", period-named buttons ("Export Q2 2026 Payout"), time-bound copy ("for the September pilot quarter") | "18 Apr 2026" vs "12 Oct 2026"; "Export Q2 2026 Payout" vs "Export Payout" | Compare the pattern ("<D Mon YYYY>"), not the value. Say when copy looks time-bound. |
| **ST** State | Depends on current state: disabled/enabled, selected/unselected, open/closed, locked, loading, empty, error, unpaired | Save button disabled (nothing edited); no radio selected (no setting stored); "Screen not set up"; "Locked for the current cycle" notice | Do not report. Put the state in "Not verified" and, where possible, put the live page into the prototype's state and compare again. |
| **C** Conditional element | Only rendered when data, role or state allows it | Podium, RAG chips with counts, "Employee of the Month" banner, header counters, per-row actions such as Suspend | Find the condition before calling it missing: read the prototype's render code and, on live, open collapsed controls and check other states. If you cannot confirm it is unconditional, report it as **Needs confirmation**, not Critical. |
| **P** Prototype inconsistency | The prototype contradicts itself | "Drivers auto-synced from fleetmastr" on one screen, "Prolius" on every other screen | Do not rate. List it under Needs confirmation and ask which wording is intended. |
| **E** Environment | Not a prototype comparison: CSP errors, console errors, network failures, hard-coded labels that look wrong against the real date | Console `font-src 'self'` violations; "Q2 2026" heading above a 2026-10-01 to 2026-12-31 period | List under Observations. Keep out of the severity counts. |

## Rules

1. **Align state before comparing.** Same role, same screen state, same breakpoint. If the live site is empty and the prototype is seeded, tell the user in the first status message and ask whether to (a) use a populated environment, (b) create marked test records (`ZZ-UIQA-...`) that you later delete, or (c) compare static parts only. Do not silently proceed and then list the missing data as findings.
2. **Never compare truncated text.** Compare the full string. Truncating to 60 characters made two subtitles look reworded when only their tails differed.
3. **Interactive controls must be opened.** A dropdown, tab, accordion or toggle that is collapsed on live must be opened and screenshotted before saying it differs from a row of buttons in the prototype.
4. **Element width and height are not tokens** for table cells, flex children and anything that auto-sizes. Compare them only for fixed-size elements (buttons, inputs, icons, sidebar, header).
5. **Missing is not Critical until the condition is known.** Missing and unconditional = Critical. Missing and possibly conditional = Needs confirmation.
6. **Check the prototype against itself.** Search its source for the live wording before reporting a wording difference. If the live wording appears elsewhere in the prototype, class P.
7. **Show your filtering.** The report lists what was excluded as D, I, T, ST, so a reader can see nothing was hidden and can overrule a classification.
