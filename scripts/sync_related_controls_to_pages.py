#!/usr/bin/env python3
"""Synchronize references.related_controls from YAML into narrative .adoc pages.

Reads every control YAML, finds the matching German and English narrative page,
and replaces the 'Related Controls' / 'Verwandte Controls' section with the
current list of related controls, rendered as cross-pillar xrefs.
"""
import re
import yaml
from pathlib import Path

REPOS = {
    "de": ".",
    "en": "../framework-en",
}

PILLAR_MODULE = {
    "security": "pillar-security",
    "cost": "pillar-cost",
    "efficiancy": "pillar-efficiancy",
    "reliability": "pillar-reliability",
    "excellence": "pillar-excellence",
    "sustainability": "pillar-sustainability",
    "sovereign": "pillar-sovereign",
    "agentic": "pillar-agentic",
}

PILLAR_FROM_ID = {
    "sec": "pillar-security",
    "cost": "pillar-cost",
    "perf": "pillar-efficiancy",
    "rel": "pillar-reliability",
    "ops": "pillar-excellence",
    "sus": "pillar-sustainability",
    "sov": "pillar-sovereign",
    "agn": "pillar-agentic",
}


def pillar_for_control_id(cid: str) -> str:
    middle = cid.split("-")[1].lower()
    return PILLAR_FROM_ID[middle]


def related_section_lines(related: list[str], lang: str) -> list[str]:
    title = "Verwandte Controls" if lang == "de" else "Related Controls"
    none_msg = (
        "Keine verwandten Controls definiert."
        if lang == "de"
        else "No related controls defined."
    )
    lines = [f"== {title}", ""]
    if not related:
        lines.append(none_msg)
        lines.append("")
        return lines
    for rc in related:
        lines.append(f"* xref:{pillar_for_control_id(rc)}:controls/{rc}.adoc[{rc}]")
    lines.append("")
    return lines


def replace_related_section(text: str, related: list[str], lang: str) -> str:
    title = "Verwandte Controls" if lang == "de" else "Related Controls"
    # Match the section header and everything up to the next == heading or EOF.
    pattern = re.compile(rf"^== {title}\n.*?\n(?=^== |\Z)", re.M | re.S)
    new_section = "\n".join(related_section_lines(related, lang))
    new_text, count = pattern.subn(new_section, text, count=1)
    if count == 0:
        # Try to insert before Regulatory Mapping / Regulatorisches Mapping
        next_title = "Regulatorisches Mapping" if lang == "de" else "Regulatory Mapping"
        insert_pattern = re.compile(rf"^(== {next_title}\n)", re.M)
        new_text, insert_count = insert_pattern.subn(new_section + r"\1", text, count=1)
        if insert_count == 0:
            raise ValueError(f"Could not find '{title}' or '{next_title}' section")
    return new_text


def process_repo(repo_root: str, lang: str) -> int:
    root = Path(repo_root)
    updated = 0
    for path in sorted((root / "modules" / "controls" / "controls").glob("WAF-*.yml")):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        cid = data["id"]
        pillar = data.get("pillar", "")
        if pillar not in PILLAR_MODULE:
            print(f"WARNING: unknown pillar {pillar} for {cid}")
            continue
        module = PILLAR_MODULE[pillar]
        adoc_path = root / "modules" / module / "pages" / "controls" / f"{cid}.adoc"
        if not adoc_path.exists():
            print(f"WARNING: missing narrative page {adoc_path}")
            continue
        related = (data.get("references") or {}).get("related_controls", [])
        text = adoc_path.read_text(encoding="utf-8")
        new_text = replace_related_section(text, related, lang)
        if new_text != text:
            adoc_path.write_text(new_text, encoding="utf-8")
            updated += 1
    return updated


def main():
    for lang, repo_root in REPOS.items():
        updated = process_repo(repo_root, lang)
        print(f"Updated {updated} narrative pages in {repo_root}")


if __name__ == "__main__":
    main()
