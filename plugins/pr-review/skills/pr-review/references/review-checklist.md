# Review checklist

Apply with the project's config as the authority. Cite the project's own rule for every standards finding; use this list to make sure nothing is skipped, not as the standard itself.

## Correctness
- Logic errors, off-by-one, inverted conditions, wrong operator, unhandled branch.
- Null/empty/boundary handling; resource leaks (unclosed streams, drivers, connections).
- Concurrency: shared mutable state, race conditions, non-thread-safe singletons.
- Error handling matches the project's pattern; no silently swallowed exceptions unless the project allows it.

## Core / component & blast radius (highest priority)
- Changed public contracts are consistent with all callers (see `blast-radius.md`).
- All subclasses/implementers/overrides updated when a base signature changes.
- No breaking change to a widely-imported constant/config/type without updating dependents.

## Standards & nomenclature (from config)
- Naming of classes, methods, variables, files, packages matches the documented convention.
- Layering/architecture rules respected (e.g. tests don't touch the driver directly; pages extend the base; no business logic where it's banned).
- File/folder placement matches the project layout.
- Formatting/lint: would the project's PMD/Checkstyle/eslint/tsconfig gate pass? Flag likely violations.

## Tests
- New/changed behaviour covered per the project's test policy.
- Tests assert something meaningful; no disabled/`@Ignore`/`.skip` left silently; no committed `.only`.
- Forbidden patterns avoided (e.g. static/hard waits, sleeps, real network in unit tests) if the project bans them.
- Test data handled per the project's rules (no hard-coded secrets, no shared mutable fixtures if disallowed).

## Redundancy & duplication (run as a deliberate sweep, not opportunistically)
- Same logic/expression repeated across the diff that could be one helper — **count the occurrences** and name the extraction (e.g. "`new X(driver).goToY()` navigation prologue ×N → `openY()` helper"). A couple of repeats is a Minor; a pattern in **≥3 files (or many times in one)** is promoted to a single **Systemic** finding per the project's cross-file rule, not one finding per site.
- Custom code that re-implements an existing utility/base method — including one added **in this same PR** (e.g. a local date-format when `DateUtil` already has it). Name the exact replacement.
- New method whose body is line-for-line another method from the status-set/action onward (only a guard or label differs) — collapse to the shared method keeping the guard.
- Near-identical setup/teardown/step blocks differing only by a value (date offset, registration, label) — extract a parameterised helper; check the file's *other* half (e.g. teardown) hasn't already done the extraction that setup skipped.
- Repeated literal anchors in locator constants / inline XPath (shared id or section prefix built again and again) — factor the common prefix into one constant.
- Judge by maintenance cost: would a future change have to be made in N places, with nothing failing if only one is updated? If yes, it's a finding.

## Security
- No secrets, tokens, keys, credentials, or private endpoints committed in the diff.
- External input validated; no injection (SQL, command, XPath/CSS from untrusted input), no unsafe deserialization.
- AuthZ/authN checks not weakened; no debug/backdoor left enabled.
- Dependencies added are reputable and pinned per project norms.

## PR hygiene (from config)
- PR description satisfies the project's template/guidelines; linked issue if required.
- Scope is coherent; no unrelated drive-by changes mixed in; no large generated/vendored blobs that shouldn't be committed.
- Commit/branch naming follows the project's git guidelines.

## Not a finding
- Personal style preferences not backed by a project rule.
- Pre-existing issues the PR doesn't touch (mention as an observation at most).
- Data/environment differences, generated artifacts the project intends to commit.
