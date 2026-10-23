---
repo: Prolius/imastr-automation-test-e2e
project_root: prolius-ui-automation-core
default_branch: main
generated: 2026-10-14
generated_from_sha: 151b27ace4fec352f2898f56631912c90920bbe2
stack: Java 17 / Maven / Selenium WebDriver / TestNG / Allure (UI test automation; Playwright MCP used only for locator discovery, not runtime)
---

# PR review config — Prolius/imastr-automation-test-e2e (prolius-ui-automation-core)

> Monorepo. This config covers the `prolius-ui-automation-core` subproject only. Sibling
> subprojects (prolius-api-automation-core, prolius-mobile-automation, prolius-web-api-automation,
> …) each need their own config. All paths below are relative to `prolius-ui-automation-core/`.

## Source files (for staleness detection)
| File | Blob SHA | Governs |
|---|---|---|
| CLAUDE.md | 27cc7b36a0e3c48c39463ae0c6ce0dfc2abe1343 | Persona, operating rules, "what Claude gets wrong" do/don't list |
| .claude/rules/code-review-rules.md | 0f03499e737edfcd9648012a7663b41df38b3dad | **Single source of truth for review checks** (pattern table T1–T22, deep-dive checks, severity) |
| .claude/rules/coding-standards.md | ec213d8c8f55fd3092077e608b121818505f06b5 | Naming conventions, Selenium/Java standards |
| .claude/rules/architecture.md | 36bef032c2ddfb7145779ab0036242e83578fa04 | Layering / module structure |
| .claude/rules/framework-patterns.md | 43e6c1e508300e4063db1640771937703c29d710 | Component interaction & locator strategy |
| .claude/rules/base-page-reference.md | fdb2e59cc1c5927e647ce068ef6f1b44f07d1a49 | BasePage API (waits, dropdowns, file ops) |
| .claude/rules/table-base-page-reference.md | 2de7c421117d68893d8bafd21cd90ed7e861bd00 | TableBasePage API |
| .claude/rules/java-maven-guidelines.md | 8d597a6bc0b594582baefa51c663d85dd5ee5049 | Java/Maven conventions |
| .claude/rules/test-data-management.md | 75fc09b192101269f3bcb56da35f9251653328eb | JsonUtil data access patterns |
| .claude/rules/testing-policy.md | 4a8d1d1ade453b6fef68c041b4431882ae0f3949 | Test policy |
| .claude/rules/utilities.md | 6b6194889e1d7be9d90715384fe7ff812c44de0d | Catalogue of existing utilities (don't reinvent) |
| GitGuidelines.md | c137ddf1fb2562a8b2d4ceb7795698e2ebccb01c | Branch/commit/PR naming + PR description template |
| PR_TEMPLATE.md | e7b84def452b36b5b7c5c6771820832e4178c911 | PR body template |
| pom.xml | a8b2884e4c646bcd69c39a5b186b975068d15498 | Build + PMD quality gate |

**When reviewing this project, read `.claude/rules/code-review-rules.md` first** — it is the project's
own review checklist (T1–T22 pattern scan + deep-dive checks). Apply it as the primary standard; the
skill's generic checklist is secondary.

## Coding standards (project's own)
- No PageFactory; use `By`/raw XPath directly — source: coding-standards.md
- Locators defined as `private static final String` raw XPath at the top of the page class — coding-standards.md, CLAUDE.md
- Explicit `WebDriverWait`/`ExpectedConditions` only; **no `Thread.sleep`, no `implicitlyWait`, no mixing wait strategies** — coding-standards.md, code-review-rules.md (T2/T15/T16)
- Java 17, 4-space indent, try-with-resources for IO, Javadoc on public methods — coding-standards.md
- Reporting via `Allure.step("…", () -> {…})`; **never `@Step`** — CLAUDE.md, code-review-rules.md (T3)
- Logging via `LoggerUtil`; **never `System.out.println`** — code-review-rules.md (T20)

## Nomenclature / naming conventions
- Classes `PascalCase`; methods/variables `camelCase`; locator `By`/String constants `UPPER_SNAKE_CASE`; packages `lowercase.dot.separated` — coding-standards.md
- Page objects live in `pages/`, `pages/tabs/`, `pages/dialogs/`, `pages/forms/` — CLAUDE.md
- Dialog page objects extend `DialogBasePage` (not `BasePage`); tests needing data extend `BaseCommonTests` (not `BaseTest` directly) — code-review-rules.md (Architecture Integrity)

## Architecture & layering rules
- **Locators ONLY in page objects.** No XPath/CSS/`By.*` strings in `src/test/java/com/prolius/tests/**` — CLAUDE.md, coding-standards.md, code-review-rules.md (T22)
- **Assertions ONLY in tests via `LoggerUtil`.** No `LoggerUtil.verify/compare/fail/error` inside page objects; no direct `Assert`/`SoftAssert` — code-review-rules.md (T5, T12)
- Page objects must not import test-layer code (no circular deps) — code-review-rules.md
- Test resources in `resources/` (project root), NOT `src/main/resources` or `src/test/resources` — CLAUDE.md

## Core / shared / component files (HIGHEST review priority)
A change here forces blast-radius analysis — nearly every test/page depends on these:
- `src/main/java/com/prolius/base/**` — **framework core**: `BasePage`, `TableBasePage`, `DialogBasePage`, `FormBasePage`, `BaseTest`, `DriverFactory`, `ConfirmationDialog`. Every page/test extends these; a signature or wait-behaviour change ripples repo-wide.
- `src/main/java/com/prolius/utils/**` — **shared utilities**: `DateUtil`, `RandomString`, `JsonUtil`, `FileUtil`, `ConfigReader`, `LoggerUtil`, `XlComparisonUtil`. Imported everywhere.
- `src/test/java/com/prolius/base/**` — shared test base: `BaseCommonTests`, `CommonDefectDetailsPage`.
- `src/test/java/com/prolius/pages/**` (and `tabs/`, `dialogs/`, `forms/`) — reusable **component** page objects; a changed/removed public method or locator constant can break every test using that page.
- `pom.xml`, `testng.xml`, config/constants files — build/run contract.
- **Lower priority (leaf):** `src/test/java/com/prolius/tests/**` — individual test classes. Still scan for policy violations (T-patterns), but these rarely have downstream callers.

## Test policy
- Behaviour must be covered by tests; see testing-policy.md.
- No hardcoded test data — use `JsonUtil.getValue("keyPath")`; no manual dates — use `DateUtil`; no `Math.random`/`UUID` — use `RandomString.generate(length)` — CLAUDE.md, test-data-management.md, code-review-rules.md (T4, T19, T21)
- No `getRequiredData()`/`JsonUtil.getValue()` at field-init (init-order race) — code-review-rules.md (T7)
- Test independence: no instance/static field mutated by one `@Test` and read by another; `dependsOnMethods` only when safe — code-review-rules.md
- No committed placeholder locators (`<replace your own xpath>`, `TODO: Verify`) — code-review-rules.md (T18)

## Quality gates / lint
- `mvn pmd:check` (CLAUDE.md "Check Style/Lints"); build `mvn clean install -DskipTests`; tests `mvn test` / `mvn test -Dtest=ClassName`. Flag likely PMD/thread-safety violations (static non-final/ThreadLocal in `utils/`/`base/` → T1).

## PR hygiene requirements
- Branch: `[feature|bugfix|hotfix|epic|chore]/[ticket]_[short-summary]`, lowercase+hyphens, ticket number required — GitGuidelines.md
- Commit: `[ticket]: [imperative summary]`, ≤72 char subject, one logical change — GitGuidelines.md
- PR title: `[ticket]: [one-line summary]`; PR body should follow PR_TEMPLATE.md / GitGuidelines template (ticket ref, summary, changes, testing steps/Allure, review checklist incl. "no credentials committed")
- Don't push to `main`/`develop`; keep PRs small and single-purpose; squash before merge — GitGuidelines.md

## Security notes
- No secrets/credentials committed (note: repo root historically contains a `*.json` service-account key and `storage.json` — flag any credential/key/token added in a diff). PR checklist explicitly requires "No sensitive data or credentials committed".

## Reviewer notes
- **Primary standard is the project's own `code-review-rules.md`** (Anti-Fabrication Contract: quote verbatim code with confirmed `file:line`; cap 5 findings/category; promote a pattern seen in ≥3 files to a single "Systemic" finding). Map skill severities onto the project's Critical/High/Medium/Low where reporting against this repo.
- Blast-radius blind spots specific to this repo: TestNG wiring via `testng.xml` (reflection), Allure/CDP event callbacks, and locators built by string concatenation won't surface in code search — verify base/util changes against subclasses and `testng.xml` explicitly.
- Not documented: explicit code-coverage thresholds; treat coverage as "tests must exist for new behaviour", not a numeric gate.
