---
name: pr-review
description: Reviews a GitHub pull request against the project's own coding standards and Claude rules, using gh to fetch PR data and the diff (read-only, no writes to GitHub). Fetches the target repo's CLAUDE.md, .claude/rules, .cursorrules and related guideline files to learn its patterns, nomenclature and standards before reviewing. Treats changes to core/shared/component files as highest priority and traces their blast radius — every call site — via GitHub code search to check the change does not break existing callers. Saves reusable per-project review config so repo research is not repeated. Writes an evidence-backed Markdown report. Use whenever the user asks to review a PR, pull request, review a diff on GitHub, check a PR, "will this break anything", code review of a gh PR, or a PR safety/standards review.
# allowed-tools: Bash, Read, Write, Grep, Glob
---

# GitHub PR Review

Review a pull request the way a senior maintainer of *that* project would: against the project's own rules and conventions, with the heaviest scrutiny on core/shared/component code and everything it could break. The job is to find real problems and prove each one with evidence (file, line, the rule or caller it violates), so the author can act without re-investigating.

## Hard rules (and why)

- **Read-only to GitHub.** Use `gh` only to *read* (PR metadata, diff, file contents, code search, and existing reviews/comments). Never post comments, never submit a review verdict, never approve/request-changes, never reply to / resolve / react to a review thread, never push, never edit the PR or its branch. The delivery is a local Markdown report plus a chat summary — nothing is sent to GitHub. (If the user later wants comments posted, that is a separate, explicitly-authorized action.)
- **Never read, log or store credentials or tokens.** Rely on the user's existing `gh auth`. Do not print `gh auth token`, do not echo `GITHUB_TOKEN`, do not write any token into the report, config, or evidence. If `gh auth status` fails, stop and ask the user to run `gh auth login` themselves (suggest they type `! gh auth login`).
- **gh API only — do not assume a local clone.** Fetch the diff and file contents through `gh`. Do not `git clone`, `git checkout`, or `git fetch` the target repo, and do not assume its working tree is on disk. Blast-radius search is done with `gh search code` / the search API — see `references/blast-radius.md`.
- **Do not guess inputs.** If the repo or PR number is missing or ambiguous, ask. If the project's standards are unclear from its own files, say what is missing rather than inventing a standard.
- **The project's rules win.** When this skill's generic checklist conflicts with the target project's documented conventions, the project's documented convention is authoritative. Report deviations from *their* standard, not from yours.
- **Classify before rating.** A diff line that merely differs from your preference is not a finding. Only report things that break behaviour, violate a documented project rule, break a caller, or are defects on their own terms.

## Inputs to collect first

Ask for anything not provided:
1. The PR: a number, or a full PR URL. (A URL gives the repo too.)
2. The repo `owner/name`, if not derivable from the above.
3. Optionally, a focus (e.g. "just the security angle", "only the core module"). Default is a full review.

Confirm `gh auth status` succeeds and that the authenticated account can read the repo before doing anything else.

## Workflow

### 0. Resolve the PR and verify access
- Resolve `owner/repo` and PR number from the input. `gh pr view <n> --repo <owner/repo> --json number,title,author,baseRefName,headRefName,headRefOid,state,url,body,additions,deletions,changedFiles` to confirm it exists and capture metadata and the PR description.
- `references/gh-commands.md` has the exact command set.

### 0.5 Read prior reviews and existing comments — and check whether they're addressed
A PR often already carries a human (or bot) review. Never re-litigate it from scratch or silently duplicate it — read what exists first, then verify its state against the exact head you're reviewing. **Do this before writing findings**, so your report builds on the prior review rather than ignoring it.
- Fetch existing reviews and their verdicts, inline (diff) review comments, and issue comments (see `references/gh-commands.md`). For each inline comment capture its `path`, line, `body`, the `original_commit_id` it was made on, and whether it is a reply within a thread.
- Decide, for each prior point, whether it **still applies to the head under review**:
  - Compare the commit the comment was made on against `headRefOid`: `gh api repos/<owner>/<repo>/compare/<original_commit_id>...<headRefOid>`. `files_changed: 0` means the trees are identical — nothing was fixed. Watch for **revert-then-reapply or force-push** histories: a newer HEAD can be byte-identical to an already-reviewed commit, so "there are newer commits" does **not** mean the comments were addressed.
  - Confirm directly in the head file that the flagged construct is (or is not) still present — don't infer from the comment's GitHub `position` alone.
- If there is an open `CHANGES_REQUESTED` verdict whose points are still unaddressed, that is a **top-line result**: state it in the Verdict and summary, and do not imply the PR is near-mergeable while a standing review is unresolved.
- Reading reviews/comments is read-only and allowed; **do not reply to, resolve, or react to** any thread on GitHub.

### 1. Locate the project root (handle monorepos)
Do not assume the project lives at the repo root — many repos are monorepos holding several subprojects, each with its own rules and build file. Determine the **project root** = the nearest ancestor directory of the PR's changed files that contains a `CLAUDE.md`, a `.claude/` dir, or a build file (`pom.xml`, `package.json`, `build.gradle`, …). If the PR spans several subprojects, treat each as its own project root (its own config, its own core globs). If none can be found above the changes, fall back to the repo root. All paths in steps below (rule files, core/component globs) are relative to the project root, not necessarily the repo root.

### 2. Load or build the project review config
The reusable per-project config lives in **this** repo at `plugins/pr-review/skills/pr-review/project-configs/<owner>__<repo>[__<project-root-slug>].md` (committed, so research is done once) — add the project-root slug when the project root is a subdirectory of a monorepo. Resolve the folder relative to this skill directory — it is the `project-configs/` folder beside this `references/` folder.

- **If it exists:** read it and use it. Check whether the source rule files it recorded have changed (compare the blob SHAs it stored against `gh api repos/<owner>/<repo>/contents/<path>` — see `references/gh-commands.md`). If they changed, or the user asks for a refresh, rebuild it.
- **If it does not exist (or is stale):** do repo research, then write it per `references/config-schema.md`:
  - Fetch and read the project's Claude/agent rules and guideline files, all resolved **under the project root**: `CLAUDE.md` (project root and any nested ones), `.claude/rules/*`, `.claude/docs/*`, `.cursorrules`, `.clinerules`, `AGENTS.md`, `GitGuidelines.md`, `CONTRIBUTING.md`, `PR_TEMPLATE.md` / `.github/pull_request_template.md`, and any `.github/` review config. Fetch directory listings with the contents API, then fetch each file. (`.github/` is resolved at the repo root even for a subproject.)
  - Identify the stack and its lint/quality gates from the project root's build files (`pom.xml` → PMD/Checkstyle, `package.json` → eslint/prettier/tsconfig, etc.).
  - Derive, **from the project's own words where possible**: coding standards, naming/nomenclature conventions, architecture/layering rules, test policy, and — importantly — the globs (relative to the project root) that identify **core / shared / base / component** files (e.g. base-page classes, shared utilities, design-system components). These drive step 4.
  - Write the config file. Record each source file's path and blob SHA so staleness can be detected next time. Never record secrets.
- Tell the user whether you loaded an existing config or built a new one.

### 3. Fetch the PR diff and changed-file list
- `gh pr diff <n> --repo <owner/repo>` for the unified diff; `gh pr view <n> --json files` for the structured file list with per-file additions/deletions/status.
- For any changed file you need full context on, fetch the **new** version at the PR head (`?ref=<headRefOid>`) and, when judging a change, the **base** version too. Don't review hunks in isolation when the surrounding code decides correctness.

### 4. Triage changed files — core/component first
- Tag each changed file against the config's core/shared/component globs. **Review tagged files first and most thoroughly.** A one-line change to a base class or shared component outranks a large change to a leaf test.
- For each core/component file, understand *what contract changed*: signatures, parameters, return types, exceptions, defaults, side effects, selectors/locators, exported names, public behaviour.

### 5. Blast radius — trace every call site (core/component changes)
For each changed public symbol in a core/shared/component file, follow `references/blast-radius.md`:
- Find all call sites across the repo with `gh search code`, plus in-PR usages from the diff.
- Fetch each caller and check the change doesn't break it: changed/removed signature or param order, renamed or removed method/export, narrowed return, new required argument, changed default or thrown exception, changed selector contract, changed nullability.
- **Note the search's blind spots in the report**: GitHub code search indexes the default branch only and matches on tokens, so new symbols on the PR branch, reflection/dynamic dispatch, string-built references and non-default-branch callers can be missed. List what you could and could not verify. If the blast radius is too large to verify by API within reason, say so and name the highest-risk callers rather than implying full coverage.

### 6. Review the rest against the project's standards
Using the loaded config and `references/review-checklist.md`, check: correctness and logic; adherence to the project's documented coding standards and **nomenclature**; architecture/layering rules; error handling; test coverage and the project's test policy; security (injected input, secrets committed, unsafe deserialization, authz); and PR hygiene (does it satisfy the project's PR template / guidelines). Prefer the project's rule as the citation for every standards finding.

**Run the redundancy & duplication sweep as a deliberate pass** (its own section in `references/review-checklist.md`), not opportunistically: look for the same logic/expression/locator-anchor/setup-block repeated across the diff, custom code re-implementing an existing or same-PR utility, and new methods whose body duplicates another. **Count occurrences and name the single extraction that removes them.** Promote any pattern spanning **≥3 files (or repeated many times in one)** to a single **Systemic** finding — do not file one finding per copy. Judge by maintenance cost: if a future change must be made in N places with nothing failing when only one is updated, it is a finding.

### 7. Rate findings
- **Severity:** `Blocker` (breaks a caller, breaks behaviour, security hole, violates a hard project rule) · `Major` (likely bug, significant standard/nomenclature violation, missing required tests) · `Minor` (localized issue, style against a documented rule) · `Nit` (optional).
- **Confidence:** `Confirmed` (verified against code/callers/a cited rule) · `Needs confirmation` (plausible but depends on something you could not verify — e.g. a caller the search can't reach, or runtime behaviour). Only `Confirmed` findings carry a severity in the summary count; `Needs confirmation` items are listed separately with the exact question to resolve them.
- Every finding cites evidence: `path:line` on the PR head, the diff hunk, and the specific project rule or the specific caller affected.

### 8. Write the report and summarize
- Write the report per `references/report-template.md` to `reports/<owner>-<repo>-PR<n>_<YYYY-MM-DD>.md` (use the user's local date; append `_2`, `_3` rather than overwriting).
- Include a **Prior review status** section (from step 0.5): the existing verdict(s) and who gave them; for each prior comment whether it is **Addressed / Not addressed / Partially / Can't tell**, with evidence; which of your own findings **overlap** a prior comment (so they aren't double-counted); and any prior point you judge invalid, with why.
- End with a short chat summary: counts by severity, the single biggest risk, any blast-radius blind spots, **and the status of any prior review** (e.g. "standing CHANGES_REQUESTED, 16 comments, none addressed"). Do not commit or push anything — the user does that.

## Scope notes
- This skill reviews; it does not fix. If asked to fix, that is follow-up work in the target repo, not part of the report.
- If the PR touches many unrelated areas, review core/component changes fully and summarize the rest, stating what was given lighter treatment.
