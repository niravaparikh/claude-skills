# gh command reference (read-only)

All commands read only. Never run `gh pr comment`, `gh pr review`, `gh pr merge`, `gh pr edit`, or any push. Never print `gh auth token` or echo a token.

Set once per session for convenience (shell): `R=<owner>/<repo>` and `N=<pr-number>`.

## Auth and access
```bash
gh auth status                      # must succeed; if not, ask user to run: ! gh auth login
gh repo view "$R" --json nameWithOwner,defaultBranchRef,visibility
```

## PR metadata and description
```bash
gh pr view "$N" --repo "$R" --json number,title,author,state,url,body,\
baseRefName,headRefName,headRefOid,additions,deletions,changedFiles
```

## Changed files and the diff
```bash
gh pr view "$N" --repo "$R" --json files      # path, additions, deletions, status per file
gh pr diff "$N" --repo "$R"                    # unified diff
gh pr diff "$N" --repo "$R" --patch            # patch form if you need per-file hunks
```

## Fetch file contents (no clone)
GitHub contents API returns base64; decode it. Use the PR head SHA for the new version, the base ref for the old.
```bash
# New version at PR head:
gh api "repos/$R/contents/<path>?ref=<headRefOid>" --jq '.content' | base64 -d
# Old/base version:
gh api "repos/$R/contents/<path>?ref=<baseRefName>" --jq '.content' | base64 -d
# Blob SHA only (for config staleness checks):
gh api "repos/$R/contents/<path>?ref=<baseRefName>" --jq '.sha'
```

## Monorepo note
Many repos hold several subprojects. Paths below are relative to the **project root** (the nearest ancestor of the PR's changed files with a `CLAUDE.md`/`.claude/`/build file), which may be a subdirectory — e.g. prefix with `prolius-ui-automation-core/`. A root-level probe 404 usually means the project is in a subdirectory, not that the file is absent; list the repo root (`gh api "repos/$R/contents?ref=<branch>"`) to find subprojects.

## Discover the project's rule/guideline files
```bash
# List a directory (returns names + sha + type):
gh api "repos/$R/contents/.claude/rules?ref=<baseRefName>" --jq '.[].path'
gh api "repos/$R/contents/.github?ref=<baseRefName>" --jq '.[].path'
# Probe for single files (404 means absent — that's fine):
for f in CLAUDE.md AGENTS.md .cursorrules GitGuidelines.md CONTRIBUTING.md \
         PR_TEMPLATE.md .github/pull_request_template.md; do
  gh api "repos/$R/contents/$f?ref=<baseRefName>" --jq '.path' 2>/dev/null
done
```

## Prior reviews and existing comments (step 0.5)
Read what reviewers already said, and check whether it was fixed in the head you're reviewing. Read-only — never reply, resolve, or react.
```bash
# Review verdicts (APPROVED / CHANGES_REQUESTED / COMMENTED) with author and time:
gh api "repos/$R/pulls/$N/reviews" --paginate \
  --jq '.[] | {user: .user.login, state, submitted_at, body}'
# Inline (diff) review comments — path, line, the commit they were made on, thread replies:
gh api "repos/$R/pulls/$N/comments" --paginate \
  --jq '.[] | {id, path, line: (.line // .original_line), original_commit_id, in_reply_to_id, user: .user.login, body}'
# General PR (issue) comments:
gh api "repos/$R/issues/$N/comments" --paginate --jq '.[] | {user: .user.login, body}'
# Did the head actually change since a comment's commit? files_changed: 0 ⇒ identical tree ⇒ nothing fixed.
# Catches revert-then-reapply and force-push histories where a newer HEAD == an already-reviewed commit.
gh api "repos/$R/compare/<original_commit_id>...<headRefOid>" \
  --jq '{status, ahead_by, behind_by, files_changed: (.files | length)}'
# Full commit list (spot reverts/reapplies/force-pushes):
gh api "repos/$R/pulls/$N/commits" --paginate \
  --jq '.[] | "\(.sha[0:8])  \(.commit.author.date)  \(.commit.message | split("\n")[0])"'
```
Then confirm in the head file itself that each flagged construct is still present — don't rely on the comment's GitHub `position` alone.

## Code search for call sites (blast radius)
See `blast-radius.md` for method and caveats.
```bash
gh search code "<symbol>" --repo "$R" --json path,textMatches --limit 100
gh search code "<symbol>" --repo "$R" --language java --limit 100
```

## Notes
- `gh api` paginates; add `--paginate` for directory listings that may exceed one page.
- Code search indexes the **default branch only** and tokenizes — treat misses as "not found by search", not "no callers".
- Rate limits: search API is limited (~30 req/min). Batch symbols; don't search the same term repeatedly.
