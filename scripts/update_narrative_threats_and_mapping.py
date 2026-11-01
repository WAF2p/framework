#!/usr/bin/env python3
"""Update Begründung/Rationale and Regulatorisches Mapping/Regulatory Mapping sections
in existing narrative control pages after YAML threat and framework mapping changes.

Applies to both language repositories.
"""
import glob
import re
import yaml
from pathlib import Path

REPOS = {
    "de": ".",
    "en": "../framework-en",
}

SECTION_TITLES = {
    "de": {
        "rationale": "Begründung",
        "requirements": "Anforderungen",
        "mapping": "Regulatorisches Mapping",
        "risk_label": "Risiko",
        "desc_label": "Beschreibung",
    },
    "en": {
        "rationale": "Rationale",
        "requirements": "Requirements",
        "mapping": "Regulatory Mapping",
        "risk_label": "Risk",
        "desc_label": "Description",
    },
}


def load_yaml(repo_root, cid):
    path = Path(repo_root) / "modules" / "controls" / "controls" / f"{cid}.yml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_narrative_path(repo_root, cid):
    pillar = cid.split("-")[1].lower()
    prefix_to_module = {
        "sec": "pillar-security",
        "cost": "pillar-cost",
        "perf": "pillar-efficiancy",
        "rel": "pillar-reliability",
        "ops": "pillar-excellence",
        "sus": "pillar-sustainability",
        "sov": "pillar-sovereign",
        "agn": "pillar-agentic",
    }
    module = prefix_to_module.get(pillar, f"pillar-{pillar}")
    path = Path(repo_root) / "modules" / module / "pages" / "controls" / f"{cid}.adoc"
    return path if path.exists() else None


def build_rationale_section(data, labels):
    threats = data.get("threat") or []
    if not threats:
        threats = ["No specific threats documented."]
    lines = [
        f"== {labels['rationale']}",
        "",
        '[cols="1,3"]',
        "|===",
        f"|{labels['risk_label']} |{labels['desc_label']}",
        "",
    ]
    for t in threats:
        lines.append(f"|*Risk* |{t}")
        lines.append("")
    lines.append("|===")
    lines.append("")
    lines.append("")
    return "\n".join(lines)


def build_mapping_section(data, labels):
    mapping = data.get("regulatory_mapping") or []
    if not mapping:
        return ""
    lines = [
        f"== {labels['mapping']}",
        "",
        '[cols="2,4", options="header"]',
        "|===",
        f"|Framework |Controls",
        "",
    ]
    for entry in mapping:
        fw = entry.get("framework", "")
        controls = entry.get("controls", [])
        if not controls:
            continue
        control_lines = "\n".join(f"* {c}" for c in controls)
        lines.append(f"|{fw} |{control_lines}")
        lines.append("")
    lines.append("|===")
    lines.append("")
    lines.append("")
    return "\n".join(lines)


def replace_section(content, start_marker, end_marker, replacement):
    """Replace section starting with start_marker and ending before end_marker."""
    pattern = re.compile(
        rf"(^== {re.escape(start_marker)}\n.*?)(?=^== {re.escape(end_marker)}\n)",
        re.MULTILINE | re.DOTALL,
    )
    return pattern.sub(replacement, content)


def update_page(path, data, lang):
    labels = SECTION_TITLES[lang]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace rationale section (ends before requirements)
    rationale_replacement = build_rationale_section(data, labels)
    content = replace_section(
        content,
        labels["rationale"],
        labels["requirements"],
        rationale_replacement,
    )

    # Replace regulatory mapping section (last section, goes to end)
    mapping_replacement = build_mapping_section(data, labels)
    if mapping_replacement:
        content = re.sub(
            rf"^== {re.escape(labels['mapping'])}\n.*",
            mapping_replacement.rstrip(),
            content,
            flags=re.MULTILINE | re.DOTALL,
        )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def main():
    for lang, repo_root in REPOS.items():
        updated = 0
        for path in sorted(Path(repo_root).glob("modules/controls/controls/WAF-*.yml")):
            cid = path.stem
            narrative_path = find_narrative_path(repo_root, cid)
            if not narrative_path:
                print(f"  Missing narrative page for {cid} in {repo_root}")
                continue
            data = load_yaml(repo_root, cid)
            if update_page(narrative_path, data, lang):
                updated += 1
        print(f"Updated {updated} narrative pages in {repo_root} ({lang})")


if __name__ == "__main__":
    main()
