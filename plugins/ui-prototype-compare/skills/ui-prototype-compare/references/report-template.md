# Report template

File: `reports/<project_name>_<YYYY-MM-DD>.md`

```markdown
# UI comparison: <project_name> (<YYYY-MM-DD>)

- Prototype: <path> (<type>) - never copied into the repo
- Live site: <start URL>
- Breakpoints: <widths>
- Pages compared: <n matched> / unmatched prototype screens: <n> / unmatched live pages: <n>

## Summary
| Severity | Count |
|---|---|
| Critical | |
| Major | |
| Minor | |

## Screen mapping
| Prototype screen | Live page | Match basis | Confirmed by user |
|---|---|---|---|

## Findings (confirmed: static, same state, measured on both sides)
### <screen> @ <width>px
| # | Severity | Category | Element | Prototype | Live | Evidence |
|---|---|---|---|---|---|---|
| 1 | Major | Colour | `button.primary` bg | #0A5CFF | #0B5BEF | ![](<project>_<date>_evidence/001-live.png) |

## Needs confirmation (not counted in the summary)
Differences that may be conditional, time-bound or caused by the prototype contradicting itself. No severity until answered.
| # | Screen | Element | Prototype | Live | Why unconfirmed | Question |
|---|---|---|---|---|---|---|
| N1 | Users | subtitle | "...from fleetmastr" | "...from Prolius" | prototype says Prolius on every other screen | Which wording is intended? |

## Excluded as dynamic or state-dependent
So readers can see what was filtered. Class codes are in `references/dynamic-content.md`.
| Screen | Element | Prototype | Live | Class |
|---|---|---|---|---|
| any | header user chip | Helen Marsden | Super-Admin | I |
| Scoreboard | fleet bonus remaining | £343 | £0 | D |
| Settings | Save Changes button | enabled | disabled (nothing edited) | ST |

## Observations (not prototype deviations, not counted)
Console/CSP errors, labels that look wrong against the real date, sample rows with odd characters.

## Not verified
Behaviour or states that could not be tested, with the reason (static prototype, no safe way to test, empty live data, role-gated route, pairing token needed, etc.).

## Test data created and cleaned up
List of records created and confirmation that each was deleted.
```

Evidence images go in `reports/<project_name>_<YYYY-MM-DD>_evidence/` with numbered file names matching finding numbers. Do not capture credentials or login screens. Choose or crop elements so real user data on the live site is not captured, and note when a screenshot had to be omitted for that reason.
