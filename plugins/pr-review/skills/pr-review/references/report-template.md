# Report template

Write to `reports/<owner>-<repo>-PR<n>_<YYYY-MM-DD>.md`. Fill every section; if a section is empty, say so explicitly. Each finding cites `path:line` on the PR head and the project rule or caller it concerns.

```markdown
# PR Review — <owner>/<repo> #<n>: <title>

- **PR:** <url>
- **Author:** <author> · **Base:** <baseRefName> ← **Head:** <headRefName> (`<headRefOid>`)
- **Size:** +<additions> / -<deletions> across <changedFiles> files
- **Reviewed:** <YYYY-MM-DD> · **Config:** project-configs/<owner>__<repo>.md (loaded | built this run)
- **Standards basis:** <key rule files consulted>

## Verdict
<1–3 sentences: overall risk, and the single most important thing to fix. If an open CHANGES_REQUESTED review is still unaddressed, lead with that. State it's a read-only review; nothing was posted to GitHub.>

## Prior review status
<From step 0.5. Existing review verdict(s) and who gave them (e.g. "CHANGES_REQUESTED by @x, 2026-08-19, 16 inline comments"). Then, per prior comment: Addressed | Not addressed | Partially | Can't tell, with evidence (head file:line, or `compare` showing files_changed: 0). Note any revert-then-reapply / force-push that left the reviewed code unchanged. Flag which of your own findings overlap a prior comment, and any prior point you consider invalid with why. If there is no prior review, say "No prior reviews or review comments on this PR.">


## Summary (Confirmed findings)
| Severity | Count |
|---|---|
| Blocker | n |
| Major | n |
| Minor | n |
| Nit | n |

## Core / component changes & blast radius
For each core/shared/component file changed:
### <path>
- **Contract change:** <what changed>
- **Call sites checked:** <k found via search + m from diff>
  - `<caller path:line>` — safe | **broken** | needs-confirmation — <reason>
- **Search coverage:** <what was verified; which blind spots apply (default-branch only / dynamic refs / volume)>

## Findings
For each (most severe first):
### [Blocker|Major|Minor|Nit] <short title>  — <Confirmed|Needs confirmation>
- **Where:** `<path:line>`
- **What:** <the defect>
- **Why it matters / rule:** <the project rule cited, or the caller/behaviour that breaks>
- **Evidence:** <diff hunk / caller snippet / cited rule text>
- **Suggested fix:** <concise, optional>

## Systemic issues (duplication / repeated patterns)
From the redundancy sweep. One entry per pattern that repeats across ≥3 files or many times in one — not one per copy.
### <short title> — <N occurrences across M files>
- **Pattern:** <the repeated logic/expression/locator-anchor/block>
- **Where:** <representative `path:line` sites + the count>
- **Rule:** <project's Duplicate-Utilities / cross-file promotion rule>
- **Single fix:** <the one extraction — helper/constant/base method — that removes all N>
If the sweep found nothing beyond localized one-off dups (already under Findings), say "No systemic duplication beyond the localized items above."

## Needs confirmation
Items that depend on something not verifiable via the gh API (unreachable callers, runtime behaviour). Each with the exact question to resolve it.

## Standards & nomenclature notes
Deviations from the project's documented conventions, each citing the source rule.

## Tests
What's covered, what's missing against the project's test policy.

## Security
Anything found, or "none observed in the diff."

## PR hygiene
Template/guideline compliance; scope; stray files.

## Observations (not findings)
Pre-existing issues, context, suggestions outside scope.

## Review coverage
- Files reviewed fully: <...>
- Files given lighter treatment: <... and why>
- Not verifiable via gh API: <...>
```
