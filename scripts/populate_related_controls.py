#!/usr/bin/env python3
"""Populate references.related_controls for all YAML controls.

Rules:
1. All controls in the same category are related (cross-pillar).
2. Semantically linked categories are related when in the same pillar or when
   the related control is critical/high severity.
3. Result is sorted and capped to keep each control focused.
"""
import glob
import yaml
from collections import defaultdict
from pathlib import Path

CROSS_LINKS = {
    "identity-access": ["secret-management", "network-security", "logging-monitoring"],
    "network-security": ["identity-access", "network-encryption", "logging-monitoring"],
    "network-encryption": ["network-security", "data-governance", "identity-access"],
    "container-security": ["secret-management", "data-governance", "logging-monitoring"],
    "secret-management": ["identity-access", "container-security", "data-governance"],
    "data-governance": ["cost-governance", "container-security", "secret-management", "logging-monitoring"],
    "cost-governance": ["data-governance", "logging-monitoring"],
    "logging-monitoring": ["identity-access", "network-security", "container-security", "deployment-automation"],
    "deployment-automation": ["logging-monitoring", "reliability-design", "data-governance"],
    "reliability-design": ["backup-recovery", "deployment-automation", "logging-monitoring"],
    "backup-recovery": ["reliability-design", "data-governance"],
    "encryption-key-management": ["data-governance", "identity-access", "network-encryption"],
    "agentic-governance": ["identity-access", "logging-monitoring"],
    "sustainability-efficiency": ["cost-governance", "data-governance"],
}

MAX_RELATED = 12


def load_controls(repo_root):
    controls = {}
    for path in sorted(Path(repo_root).glob("modules/controls/controls/WAF-*.yml")):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        controls[data["id"]] = {
            "path": path,
            "pillar": data.get("pillar", ""),
            "category": data.get("category", ""),
            "severity": data.get("severity", "medium"),
            "title": data.get("title", ""),
            "data": data,
        }
    return controls


def compute_related(controls):
    related = defaultdict(set)
    for cid, c in controls.items():
        cat = c["category"]
        for other_id, oc in controls.items():
            if cid == other_id:
                continue
            # Same category always relates
            if oc["category"] == cat:
                related[cid].add(other_id)
                continue
            # Semantic cross-links, limited by severity
            if oc["category"] in CROSS_LINKS.get(cat, []):
                if oc["pillar"] == c["pillar"] or oc["severity"] in ("critical", "high"):
                    related[cid].add(other_id)
    return related


def rank_related(cid, related_ids, controls):
    scored = []
    for rid in related_ids:
        oc = controls[rid]
        score = 0
        # Same pillar is stronger
        if oc["pillar"] == controls[cid]["pillar"]:
            score += 20
        # Same category is strongest
        if oc["category"] == controls[cid]["category"]:
            score += 30
        # Higher severity matters
        severity_score = {"critical": 10, "high": 7, "medium": 4, "low": 1}
        score += severity_score.get(oc["severity"], 0)
        # Prefer nearby IDs (similar number within same pillar)
        try:
            my_num = int(cid.split("-")[-1])
            other_num = int(rid.split("-")[-1])
            if oc["pillar"] == controls[cid]["pillar"]:
                score += max(0, 10 - abs(my_num - other_num) // 10)
        except ValueError:
            pass
        scored.append((score, rid))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [rid for _, rid in scored[:MAX_RELATED]]


def write_related(path, data, related_sorted):
    data["references"] = data.get("references") or {}
    data["references"]["related_controls"] = related_sorted
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=1000)


def process_repo(repo_root):
    controls = load_controls(repo_root)
    related = compute_related(controls)
    for cid, c in controls.items():
        ranked = rank_related(cid, related[cid], controls)
        write_related(c["path"], c["data"], ranked)
    print(f"Updated {len(controls)} controls in {repo_root}")


def main():
    import sys
    roots = sys.argv[1:] or ["."]
    for repo_root in roots:
        process_repo(repo_root)


if __name__ == "__main__":
    main()
