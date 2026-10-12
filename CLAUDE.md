# Repo conventions

This repo is a Claude Code plugin marketplace. One plugin per skill under `plugins/<name>/`.

- Start a new skill by copying `plugins/_template/` and renaming `skill-name` (folder, `plugin.json`, SKILL.md `name`).
- SKILL.md `name` must equal its folder name; `description` is required.
- Skill-specific specs and rules live inside that skill's folder only. Never put them here.
- Register each new plugin in `.claude-plugin/marketplace.json` with `"source": "./plugins/<name>"`.
- Run `python scripts/validate.py` before committing.

## Git push policy
- Claude must never run `git push` (including force pushes or pushes via `gh`). Claude has no push access to this repo.
- Claude may stage and commit locally when asked; only the user performs the final push to `main`.
