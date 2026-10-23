# Per-project review config — schema

One file per repo at `plugins/pr-review/skills/pr-review/project-configs/<owner>__<repo>.md` (the `project-configs/` folder beside this `references/` folder), committed so repo research runs once and is reused. Built in step 1 from the project's own rule/guideline files. **Never record secrets or tokens.** Record the project's conventions in *its* words where possible, and cite the source file for each so a reviewer can trust and update it.

Use this template:

```markdown
---
repo: <owner>/<repo>
project_root: <path within the repo, e.g. "." or "prolius-ui-automation-core">
default_branch: <branch>
generated: <YYYY-MM-DD>
generated_from_sha: <base commit SHA the research was done against>
stack: <e.g. Java 17 / Maven / Playwright, or TypeScript / React / Vite>
---

# PR review config — <owner>/<repo>

## Source files (for staleness detection)
| File | Blob SHA | Summary of what it governs |
|---|---|---|
| CLAUDE.md | <sha> | ... |
| .claude/rules/coding-standards.md | <sha> | ... |
| ... | ... | ... |

## Coding standards (project's own)
- <rule> — source: <file>
- ...

## Nomenclature / naming conventions
- Classes: <convention>; methods: <...>; test classes: <...>; page objects: <...>
- Package / folder layout rules: <...>
- source: <file(s)>

## Architecture & layering rules
- <e.g. tests must not instantiate driver directly; pages extend BasePage; no business logic in tests>
- source: <file(s)>

## Core / shared / component files (HIGHEST review priority)
Globs and anchors whose change forces blast-radius analysis:
- `src/.../base/**`  — base classes every page extends
- `src/.../components/**` or `.../widgets/**`
- `src/.../utils/**` or shared helpers
- design-system / shared UI components
- config/constants that many modules import
- source + reasoning: <file(s)>

## Test policy
- When are tests required; coverage expectations; test data rules; forbidden patterns (e.g. static waits).
- source: <file(s)>

## Quality gates / lint
- <PMD ruleset path / eslint config / tsconfig strictness / formatter>; what fails CI.
- source: <build file>

## PR hygiene requirements
- PR template fields that must be filled; commit message / branch naming rules; linked-issue requirement.
- source: <PR_TEMPLATE.md / GitGuidelines.md / CONTRIBUTING.md>

## Security notes
- Project-specific security expectations (secrets handling, authz patterns, input handling).

## Reviewer notes
- Gaps: what the project does NOT document (so the reviewer flags rather than invents a standard).
- Known blast-radius blind spots for this repo (reflection, dynamic locators, generated code).
```

Keep it concise and skimmable — this is a checklist the review reads every run, not an essay. If a section has no basis in the project's files, write "not documented" rather than inventing one.
