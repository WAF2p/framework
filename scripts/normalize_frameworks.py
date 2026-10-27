#!/usr/bin/env python3
"""Normalize framework names and prune obvious mis-mappings in YAML controls.

Applies canonical framework aliases and drops frameworks that do not fit a
control's pillar or category (e.g. GAIA-X outside sovereign, FinOps outside cost).
"""
import glob
import re
import yaml
from pathlib import Path

CANONICAL = {
    "ISO/IEC 27001:2022": "ISO 27001:2022",
    "BSI C5:2022": "BSI C5:2020",
    "DevOps Research and Assessment (DORA)": "DORA",
    "SOC 2": "SOC 2 Type II",
    "Google SRE Book": "SRE Book (Google)",
    "ISO 20000": "ISO/IEC 20000-1",
}

# Frameworks that only belong to a specific pillar or category.
PILLAR_ONLY = {
    "GAIA-X": ["sovereign"],
    "FinOps Foundation": ["cost"],
    "GHG Protocol": ["sustainability"],
    "Green Software Foundation": ["sustainability"],
    "SBTi (Science Based Targets initiative)": ["sustainability"],
    "EU CSRD (Corporate Sustainability Reporting Directive)": ["sustainability", "cost"],
    "Internal Governance": ["cost", "excellence", "sustainability", "sovereign", "agentic"],
    "ISO 14001": ["sustainability"],
    "NIS2": ["security", "sovereign"],
    "DORA": ["security", "sovereign", "reliability"],
    "HIPAA": ["security", "sovereign"],
    "ITIL 4": ["excellence", "reliability"],
    "ISO/IEC 20000-1": ["excellence", "reliability"],
    "COBIT 2019": ["excellence", "governance"],
    "TOGAF": ["excellence"],
    "SLSA": ["security"],
    "CNCF Cloud Native Security": ["security"],
    "ISO 22301": ["reliability"],
    "NIST SP 800-161": ["security", "sovereign"],
}

# Very niche frameworks with low coverage that are likely mis-mapped or irrelevant.
LOW_COVERAGE_DROP = {
    "ISO/IEC 29119",  # software testing
    "ISO/IEC 12207",  # software lifecycle
    "MEITY CSMP",
    "PDPA SG",
    "LGPD",
    "DPDP Act",
    "PIPEDA",
    "CCPA",
    "HDS",
}


def normalize(framework):
    return CANONICAL.get(framework, framework)


def should_keep(framework, pillar, category):
    if framework in LOW_COVERAGE_DROP:
        return False
    allowed_pillars = PILLAR_ONLY.get(framework)
    if allowed_pillars is not None and pillar not in allowed_pillars:
        return False
    return True


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data or not data.get("id"):
        return 0, 0
    pillar = data.get("pillar", "")
    category = data.get("category", "")
    mappings = data.get("regulatory_mapping", [])
    if not mappings:
        return 0, 0

    original_count = len(mappings)
    new_mappings = []
    canonicalized = 0
    for entry in mappings:
        fw = normalize(entry.get("framework", ""))
        if not fw:
            continue
        if fw != entry.get("framework"):
            canonicalized += 1
        if not should_keep(fw, pillar, category):
            continue
        entry["framework"] = fw
        # Deduplicate controls inside the same framework entry
        if "controls" in entry and isinstance(entry["controls"], list):
            seen = []
            for c in entry["controls"]:
                if c not in seen:
                    seen.append(c)
            entry["controls"] = seen
        new_mappings.append(entry)

    # Deduplicate framework entries by framework name (keep first)
    seen_fw = set()
    deduped = []
    for entry in new_mappings:
        fw = entry.get("framework")
        if fw not in seen_fw:
            seen_fw.add(fw)
            deduped.append(entry)

    data["regulatory_mapping"] = deduped
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=1000)
    removed = original_count - len(deduped)
    return canonicalized, removed


def process_repo(repo_root):
    files = sorted(Path(repo_root).glob("modules/controls/controls/WAF-*.yml"))
    total_canon = 0
    total_removed = 0
    for path in files:
        c, r = process_file(path)
        total_canon += c
        total_removed += r
    print(f"Processed {len(files)} files in {repo_root}: {total_canon} canonicalized, {total_removed} mappings removed")


def main():
    import sys
    roots = sys.argv[1:] or ["."]
    for repo_root in roots:
        process_repo(repo_root)


if __name__ == "__main__":
    main()
