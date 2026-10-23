# claude-skills

My Claude skills, distributed as a Claude Code plugin marketplace (one plugin per skill).

## Install a plugin (applies to every skill here)

### From GitHub (no clone needed)
```
/plugin marketplace add niravaparikh/claude-skills
/plugin install <skill-name>@claude-skills
```

### From a local clone (to try changes before pushing)
```
/plugin marketplace add <path-to-local-claude-skills-folder>
/plugin install <skill-name>@claude-skills
```

Restart Claude Code or run `/reload-plugins` if the skill doesn't appear. Update with `/plugin marketplace update claude-skills`.

### Prerequisites
Some skills need extra tools. Check each plugin's `SKILL.md`. For example, `ui-prototype-compare` needs the Playwright MCP server:
```
claude mcp add playwright npx @playwright/mcp@latest
```
`pr-review` needs the GitHub CLI authenticated: `gh auth login` (the skill only reads via `gh`).
`qa-test-execution` needs Python with `playwright`, `requests` and `openpyxl`, plus a browser for Playwright:
```
pip install playwright requests openpyxl
python -m playwright install chromium   # or rely on an installed Chrome/Edge
```

## Available skills
| Plugin | Purpose |
|---|---|
| `ui-prototype-compare` | Compare a UI/UX prototype against the live website and write an evidence-backed report to `reports/` |
| `pr-review` | Review a GitHub PR against the project's own Claude rules/standards (read-only via `gh`), with core/component blast-radius analysis, into an evidence-backed report in `reports/` |
| `qa-test-execution` | Execute a folder of `[API]`/`[Browser]` test cases (Excel/CSV) against a live app with parallel agents and a login the user performs themselves, into a feature-wise HTML results report in `reports/` |

## Add a skill
1. Copy `plugins/_template/` to `plugins/<name>/` and rename `skill-name` everywhere.
2. Write the spec and rules in `SKILL.md` (long rules in `references/`).
3. Add an entry to `.claude-plugin/marketplace.json`:
   `{ "name": "<name>", "source": "./plugins/<name>", "description": "..." }`
4. `python scripts/validate.py`, then push to `main` (CI re-runs the check).

Each skill is self-contained, so different skills can have different specs, tool permissions and rules without affecting each other.
