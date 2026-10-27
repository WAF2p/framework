#!/usr/bin/env python3
"""Fix navigation entries inserted by generate_new_controls_100.py.

Moves new control entries from wrong subsections into the correct control
list and deduplicates them.
"""
from pathlib import Path
import re

REPOS = {
    "de": ".",
    "en": "../framework-en",
}

PILLAR_TO_PREFIX = {
    "pillar-security": "SEC",
    "pillar-cost": "COST",
    "pillar-efficiancy": "PERF",
    "pillar-reliability": "REL",
    "pillar-excellence": "OPS",
    "pillar-sustainability": "SUS",
    "pillar-sovereign": "SOV",
    "pillar-agentic": "AGN",
}


def fix_nav(path: Path):
    text = path.read_text(encoding="utf-8")
    prefix = PILLAR_TO_PREFIX[path.parent.name]
    cids = [f"WAF-{prefix}-{n:03d}" for n in range(110, 170)]
    lines = text.splitlines()

    # Collect and remove all lines referencing the new controls
    entries = []
    positions = []
    for i, line in enumerate(lines):
        if any(f"controls/{c}.adoc" in line for c in cids):
            entries.append(line.strip())
            positions.append(i)

    if not entries:
        return

    # Determine the indentation depth used for control entries
    control_prefix = "****"
    for line in lines:
        if f"controls/WAF-{prefix}-" in line:
            m = re.match(r"^(\*+) ", line)
            if m:
                control_prefix = m.group(1)
                break

    normalized_entries = []
    for e in entries:
        m = re.match(r"\*+\s+(xref:controls/WAF-[^\[]+)\[(.+)\]", e)
        if m:
            normalized_entries.append(f"{control_prefix} {m.group(1)}[{m.group(2)}]")
        else:
            normalized_entries.append(e)

    # Dedupe by control ID
    seen = set()
    deduped = []
    for e in normalized_entries:
        m = re.search(r"WAF-[A-Z]{3,4}-\d{3}", e)
        if not m:
            continue
        key = m.group(0)
        if key not in seen:
            seen.add(key)
            deduped.append(e)

    # Remove entries from wrong positions (reverse order)
    for pos in reversed(positions):
        del lines[pos]

    # Find the last existing control line to insert after it
    last_idx = None
    prefix_re = re.compile(rf"controls/WAF-{prefix}-\d{{3}}\.adoc")
    for i, line in enumerate(lines):
        if prefix_re.search(line) and "controls/WAF-" in line:
            last_idx = i

    if last_idx is None:
        print(f"WARNING: Could not locate control list in {path}")
        return

    for e in reversed(deduped):
        lines.insert(last_idx + 1, e)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    for lang, repo_root in REPOS.items():
        for pillar in PILLAR_TO_PREFIX:
            path = Path(repo_root) / "modules" / pillar / "nav.adoc"
            if path.exists():
                fix_nav(path)
        print(f"Fixed navigation in {repo_root}")


if __name__ == "__main__":
    main()
