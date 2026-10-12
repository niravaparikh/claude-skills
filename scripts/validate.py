#!/usr/bin/env python3
"""Validate marketplace and skills. Exit 1 on any problem."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def frontmatter(path):
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return fields


market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
for p in market.get("plugins", []):
    src = ROOT / p["source"]
    if not (src / ".claude-plugin" / "plugin.json").is_file():
        errors.append(f"marketplace entry '{p['name']}': missing {p['source']}/.claude-plugin/plugin.json")

for plugin in sorted((ROOT / "plugins").iterdir()):
    if not plugin.is_dir() or plugin.name.startswith("_"):
        continue
    pj = plugin / ".claude-plugin" / "plugin.json"
    if not pj.is_file():
        errors.append(f"{plugin.name}: missing plugin.json")
    for skill_md in plugin.glob("skills/*/SKILL.md"):
        fm = frontmatter(skill_md)
        if fm is None:
            errors.append(f"{skill_md.relative_to(ROOT)}: missing frontmatter")
            continue
        if fm.get("name") != skill_md.parent.name:
            errors.append(f"{skill_md.relative_to(ROOT)}: name must equal folder '{skill_md.parent.name}'")
        if not fm.get("description"):
            errors.append(f"{skill_md.relative_to(ROOT)}: missing description")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("OK")
