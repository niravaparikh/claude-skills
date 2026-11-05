# Report template

Files (same base name, written together):
- `reports/<project_name>_<YYYY-MM-DD>.md`: the Markdown report
- `reports/<project_name>_<YYYY-MM-DD>.html`: the same content as one self-contained HTML file, produced from the Markdown with `python -I -X utf8 scripts/render_html_report.py <md path>`. The script fails if an evidence image is missing; fix that before handing the report over.
- `reports/<project_name>_<YYYY-MM-DD>_evidence/`: screenshots and raw extracts

```markdown
# UI comparison: <project_name> (<YYYY-MM-DD>)

- Prototype: <path> (<type>) - never copied into the repo
- Live site: <start URL>
- Project name: <name> (derived from: <path / hostname>)
- Role(s) compared: <role per screen> (derived from: <file names, nav, role labels>)
- Breakpoints: <widths> (derived from: prototype @media rules), or "none defined by the prototype; desktop width only"
- Theme modes compared: <modes and how each was switched> (derived from: <CSS signals / theme control>), or "single theme on both sides (no theme signals or controls found)"
- Pages compared: <n matched> / unmatched prototype screens: <n> / unmatched live pages: <n>
- Elements inventoried: prototype <n>, live <n> (all accounted for, see Element coverage)

## Summary
| Severity | Static (S) | Theme-level (counted once) |
|---|---|---|---|
| Critical | | | |
| Major | | | |
| Minor | | | |

## Screen mapping
| Prototype screen | Live page | Role | Match basis | Confirmed by user |
|---|---|---|---|---|

## Element coverage
Every inventoried element, per page and breakpoint. The numbers must add up (diff-extracts.py COVERAGE).
| Screen @ width @ mode | Proto elements | Live elements | Paired | Weak-paired | Only in proto | Only in live | Each unpaired element listed below? |
|---|---|---|---|---|---|---|---|

## Theme findings
### Token set (<mode>)
| # | Severity | Category | Token | Prototype | Live | Pages affected | Evidence |
|---|---|---|---|---|---|---|---|
### Shared components
| # | Severity | Component | Property | Prototype | Live | Instances / pages | Evidence |
|---|---|---|---|---|---|---|---|
### Theme modes
| Mode | Prototype | Live | Result |
|---|---|---|---|

## Page findings (confirmed: static, same state, measured on both sides)
### <screen> @ <width>px, <mode>
| # | Severity | Class | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | Major | S | Colour | `button.primary` bg | #0A5CFF | #0B5BEF | ![](<project>_<date>_evidence/001-live.png) |

## Dynamic differences (not rated, not counted in the summary)
Every D, I, T, ST and C difference, tagged and kept apart from static findings. Each row says why it is dynamic so the reader can overrule. Class codes are in `references/dynamic-content.md`.
| # | Screen | Element | Class | Prototype | Live | Why dynamic | Evidence |
|---|---|---|---|---|---|---|---|
| D1 | any | header user chip | I | Helen Marsden | Super-Admin | logged-in user | |
| D2 | Scoreboard | fleet bonus remaining | D | £343 | £0 | record value | |
| D3 | Settings | Save Changes button | ST | enabled | disabled | nothing edited | |

## Needs confirmation (not counted in the summary)
Differences that may be conditional, time-bound or caused by the prototype contradicting itself, plus every unpaired or weak-paired element whose condition is unknown. No severity until answered.
| # | Screen | Element | Prototype | Live | Why unconfirmed | Question |
|---|---|---|---|---|---|---|
| N1 | Users | subtitle | "...from fleetmastr" | "...from Prolius" | prototype says Prolius on every other screen | Which wording is intended? |

## Observations (not prototype deviations, not counted)
Console/CSP errors, labels that look wrong against the real date, sample rows with odd characters.

## Not verified
Behaviour, states, themes, roles or routes that could not be tested, with the reason (static prototype, no safe way to test, empty live data, role-gated route, pairing token needed, theme not recaptured, etc.).

## Test data created and cleaned up
List of records created and confirmation that each was deleted.
```

Evidence images go in `reports/<project_name>_<YYYY-MM-DD>_evidence/` with numbered file names matching finding numbers. Do not capture credentials or login screens. Choose or crop elements so real user data on the live site is not captured, and note when a screenshot had to be omitted for that reason. Raw extracts (`extract-inventory.js` / `extract-tokens.js` output and differ output) go in `evidence/raw/`.
