# Blast-radius analysis (gh API only)

Goal: for every public contract that a core/shared/component file changes, find everything that depends on it and verify the change does not break those dependents — without a local clone.

## 1. Extract the changed contracts
From the diff + the new/old file versions, list what changed about each **public** symbol:
- method/function signature: name, parameter list & order, types, return type, generics
- new *required* parameter or removed parameter; changed default value
- thrown/declared exceptions; nullability; return narrowing
- removed or renamed public method / exported name / constant
- for UI automation: changed locator/selector strategy or element contract on a base/component class
- behavioural change behind the same signature (different side effect, different order)

Private/internal-only changes have a blast radius bounded by the file — note that and move on.

## 2. Find the call sites
For each changed symbol:
```bash
gh search code "<symbol>" --repo "$R" --limit 100 --json path,textMatches
```
- Narrow with `--language` when the stack is known.
- Search the *declaring type/class name* too, since callers often qualify calls (`BasePage.waitFor`, `import { Foo }`).
- Add the in-PR usages visible in the diff itself — search can't see the PR branch.
- Fetch each candidate caller file (`gh api .../contents/<path>?ref=<headRefOid>`) and read the actual usage; discard token matches that aren't real calls.

## 3. Verify each caller survives
For every real call site, check the changed contract against how it's used:
- Does the caller pass the right number/order/type of args after the change?
- Does it rely on a return/default/exception the change altered?
- Does it reference a name the change renamed or removed?
- For overrides/implementations of a changed base method: does the signature still match (did the PR update all subclasses/implementers)?
- For locator/selector changes: do dependent pages/components still resolve the element?

Record each as: caller `path:line` → safe / broken / needs-confirmation, with the reason.

## 4. State coverage honestly
GitHub code search has real blind spots. Always report which applied:
- **Default-branch only:** callers that exist only on another branch, or symbols new on the PR branch, won't be found.
- **Tokenized matching:** partial/substring and operator-heavy queries behave unexpectedly; very common names return noise.
- **Dynamic references:** reflection, dependency injection, string-built method/locator names, code generation, and config-driven wiring won't appear.
- **Volume:** if a symbol has more call sites than you can fetch and read within reason, say so, verify the highest-risk ones, and mark the remainder `Needs confirmation` — never imply full coverage you didn't achieve.

A finding that a change is safe is only `Confirmed` if the search blind spots don't plausibly hide a caller; otherwise it's `Needs confirmation` with the exact gap named.
