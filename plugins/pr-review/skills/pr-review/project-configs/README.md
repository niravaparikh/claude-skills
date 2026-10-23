# Per-project PR-review configs

One committed file per repo: `<owner>__<repo>.md` (e.g. `Prolius__imastr-automation-test-e2e.md`).

Built by the `pr-review` skill the first time it reviews a repo, by reading that repo's own
CLAUDE.md, `.claude/rules`, git/PR guidelines and build files. Reused on later reviews so the
research isn't repeated. Schema: `../references/config-schema.md`.

Refresh a config when the source rule files change (the skill compares stored blob SHAs) or when
you ask for a rebuild. Never store secrets or tokens here.
