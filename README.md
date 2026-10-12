# claude-skills

My Claude skills, distributed as a Claude Code plugin marketplace (one plugin per skill).

## Use (no clone needed)
```
/plugin marketplace add niravaparikh/claude-skills
/plugin install <skill-name>@claude-skills
```

## Add a skill
1. Copy `plugins/_template/` to `plugins/<name>/` and rename `skill-name` everywhere.
2. Write the spec and rules in `SKILL.md` (long rules in `references/`).
3. Add an entry to `.claude-plugin/marketplace.json`:
   `{ "name": "<name>", "source": "./plugins/<name>", "description": "..." }`
4. `python scripts/validate.py`, then push to `main` (CI re-runs the check).

Each skill is self-contained, so different skills can have different specs, tool permissions and rules without affecting each other.
