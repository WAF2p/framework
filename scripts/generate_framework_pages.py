#!/usr/bin/env python3
"""Generate framework-specific catalog pages from YAML controls.

Creates one AsciiDoc page per target framework under
modules/controls/pages/frameworks/, listing every WAF++ control that maps to
that framework together with severity, pillar and category.
"""
import glob
import re
import yaml
from collections import defaultdict
from pathlib import Path

REPOS = {
    "de": ".",
    "en": "../framework-en",
}

# Frameworks for which we generate dedicated pages.
TARGET_FRAMEWORKS = [
    "ISO 27001:2022",
    "BSI C5:2020",
    "SOC 2 Type II",
    "GDPR",
    "DORA",
    "EUCS (ENISA)",
    "NIS2",
    "PCI DSS v4.0",
]

PAGE_TITLES = {
    "de": {
        "ISO 27001:2022": "ISO 27001:2022 – Control Mapping",
        "BSI C5:2020": "BSI C5:2020 – Control Mapping",
        "SOC 2 Type II": "SOC 2 Type II – Control Mapping",
        "GDPR": "GDPR – Control Mapping",
        "DORA": "DORA – Control Mapping",
        "EUCS (ENISA)": "EUCS (ENISA) – Control Mapping",
        "NIS2": "NIS2 – Control Mapping",
        "PCI DSS v4.0": "PCI DSS v4.0 – Control Mapping",
    },
    "en": {
        "ISO 27001:2022": "ISO 27001:2022 – Control Mapping",
        "BSI C5:2020": "BSI C5:2020 – Control Mapping",
        "SOC 2 Type II": "SOC 2 Type II – Control Mapping",
        "GDPR": "GDPR – Control Mapping",
        "DORA": "DORA – Control Mapping",
        "EUCS (ENISA)": "EUCS (ENISA) – Control Mapping",
        "NIS2": "NIS2 – Control Mapping",
        "PCI DSS v4.0": "PCI DSS v4.0 – Control Mapping",
    },
}

SECTION_LABELS = {
    "de": {
        "intro": "Diese Seite zeigt für {framework}, welche WAF++ Controls welche Anforderungen dieses Rahmenwerks abdecken.",
        "table_control": "Framework-Control",
        "table_requirement": "Anforderung",
        "table_waf_controls": "WAF++ Controls",
        "table_severity": "Schweregrad",
        "table_pillar": "Säule",
        "table_category": "Kategorie",
        "see_also": "Siehe auch",
        "all_frameworks": "Alle Compliance-Mappings",
        "central_mapping": "Zentrales regulatorisches Mapping",
    },
    "en": {
        "intro": "This page shows which WAF++ controls cover which requirements of {framework}.",
        "table_control": "Framework Control",
        "table_requirement": "Requirement",
        "table_waf_controls": "WAF++ Controls",
        "table_severity": "Severity",
        "table_pillar": "Pillar",
        "table_category": "Category",
        "see_also": "See also",
        "all_frameworks": "All compliance mappings",
        "central_mapping": "Central regulatory mapping",
    },
}

PILLAR_LABELS = {
    "de": {
        "security": "Security",
        "cost": "Cost Optimization",
        "efficiancy": "Performance Efficiency",
        "reliability": "Reliability",
        "excellence": "Operational Excellence",
        "sustainability": "Sustainability",
        "sovereign": "Sovereign Cloud",
        "agentic": "Agentic",
    },
    "en": {
        "security": "Security",
        "cost": "Cost Optimization",
        "efficiancy": "Performance Efficiency",
        "reliability": "Reliability",
        "excellence": "Operational Excellence",
        "sustainability": "Sustainability",
        "sovereign": "Sovereign Cloud",
        "agentic": "Agentic",
    },
}

SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
}


def load_controls(repo_root):
    controls = {}
    for path in sorted(Path(repo_root).glob("modules/controls/controls/WAF-*.yml")):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        controls[data["id"]] = {
            "pillar": data.get("pillar", ""),
            "category": data.get("category", ""),
            "severity": data.get("severity", "medium"),
            "title": data.get("title", ""),
            "frameworks": {
                m.get("framework"): m.get("controls", [])
                for m in data.get("regulatory_mapping", [])
            },
        }
    return controls


def collect_framework_entries(controls, framework):
    """Return list of (framework_control, requirement, [waf_control_ids])."""
    entries = defaultdict(list)
    for cid, c in controls.items():
        fw_controls = c["frameworks"].get(framework, [])
        if not fw_controls:
            continue
        for fw_control in fw_controls:
            entries[fw_control].append(cid)
    return entries


def filename_for_framework(framework):
    return framework.lower().replace(" ", "-").replace(":", "").replace(".", "-").replace("(", "").replace(")", "") + ".adoc"


def xref_control(cid, lang):
    pillar = cid.split("-")[1].lower()
    # Map pillar abbreviations back to module names
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
    return f"xref:{module}:controls/{cid}.adoc[{cid}]"


def sort_fw_control(key):
    """Sort so that numeric ISO controls (e.g. A.8.2) come before long textual ones."""
    parts = re.findall(r"[A-Za-z]+|\d+(?:\.\d+)*", key)
    result = []
    for p in parts:
        if p.replace(".", "").isdigit():
            result.append(tuple(int(x) for x in p.split(".")))
        else:
            result.append((0, p))
    return result


def generate_page(framework, controls, lang):
    labels = SECTION_LABELS[lang]
    title = PAGE_TITLES[lang][framework]
    entries = collect_framework_entries(controls, framework)

    lines = [
        f"= {title}",
        ":page-toc: right",
        f":description: {title}",
        "",
        labels["intro"].format(framework=framework),
        "",
        f"[cols=\"1,3,2,1,1,1\", options=\"header\"]",
        "|===",
        f"|{labels['table_control']} |{labels['table_requirement']} |{labels['table_waf_controls']} |{labels['table_severity']} |{labels['table_pillar']} |{labels['table_category']}",
        "",
    ]

    for fw_control in sorted(entries.keys(), key=sort_fw_control):
        cids = sorted(entries[fw_control])
        # Build aggregate severity/pillar/category for the row
        severities = sorted({controls[c]["severity"] for c in cids}, key=lambda s: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(s, 4))
        pillars = sorted({controls[c]["pillar"] for c in cids})
        categories = sorted({controls[c]["category"] for c in cids})
        severity_cell = " ".join(SEVERITY_EMOJI.get(s, "") for s in severities)
        pillar_cell = ", ".join(PILLAR_LABELS[lang].get(p, p) for p in pillars)
        category_cell = ", ".join(categories)
        controls_cell = " · ".join(xref_control(cid, lang) for cid in cids)
        lines.append(f"|{fw_control} |{fw_control} |{controls_cell} |{severity_cell} |{pillar_cell} |{category_cell}")
        lines.append("")

    lines.append("|===")
    lines.append("")
    lines.append(f"== {labels['see_also']}")
    lines.append("")
    lines.append(f"* xref:controls:catalog.adoc[{labels['all_frameworks']}]")
    lines.append(f"* xref:ROOT:resources/regulatory-mapping.adoc[{labels['central_mapping']}]")
    lines.append("")

    return "\n".join(lines)


def process_repo(repo_root, lang):
    controls = load_controls(repo_root)
    out_dir = Path(repo_root) / "modules" / "controls" / "pages" / "frameworks"
    out_dir.mkdir(parents=True, exist_ok=True)
    for framework in TARGET_FRAMEWORKS:
        content = generate_page(framework, controls, lang)
        filename = filename_for_framework(framework)
        (out_dir / filename).write_text(content, encoding="utf-8")
    print(f"Generated {len(TARGET_FRAMEWORKS)} framework pages in {out_dir} ({lang})")


def main():
    for lang, repo_root in REPOS.items():
        process_repo(repo_root, lang)


if __name__ == "__main__":
    main()
