#!/usr/bin/env python3
"""Generate compliance dashboard and add compliance tags to catalog tables.

Creates a new compliance-dashboard.adoc page and updates the summary tables in
modules/controls/pages/catalog.adoc to include a 'Compliance' column with
compact framework badges.
"""
import glob
import re
import yaml
from collections import Counter, defaultdict
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

FRAMEWORK_BADGES = {
    "ISO 27001:2022": ("ISO", "iso-270012022"),
    "BSI C5:2020": ("BSI", "bsi-c52020"),
    "SOC 2 Type II": ("SOC2", "soc-2-type-ii"),
    "GDPR": ("GDPR", "gdpr"),
    "DORA": ("DORA", "dora"),
    "EUCS (ENISA)": ("EUCS", "eucs-enisa"),
    "NIS2": ("NIS2", "nis2"),
    "PCI DSS v4.0": ("PCI", "pci-dss-v4-0"),
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

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def load_controls(repo_root):
    controls = {}
    for path in sorted(Path(repo_root).glob("modules/controls/controls/WAF-*.yml")):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        controls[data["id"]] = {
            "pillar": data.get("pillar", ""),
            "severity": data.get("severity", "medium"),
            "frameworks": [
                m.get("framework") for m in data.get("regulatory_mapping", [])
            ],
        }
    return controls


def badge_for_framework(framework, lang):
    if framework not in FRAMEWORK_BADGES:
        return None
    label, slug = FRAMEWORK_BADGES[framework]
    return f"xref:controls:frameworks/{slug}.adoc[{label}]"


def compliance_cell(frameworks, lang):
    badges = []
    for fw in TARGET_FRAMEWORKS:
        if fw in frameworks:
            badge = badge_for_framework(fw, lang)
            if badge:
                badges.append(badge)
    if not badges:
        return "—"
    return " · ".join(badges)


def generate_dashboard(controls, lang):
    total = len(controls)
    labels = {
        "de": {
            "title": "Compliance-Dashboard",
            "intro": "Diese Seite zeigt, wie gut der Wombat Control-Katalog die wichtigsten Compliance-Rahmenwerke abdeckt, und hilft Auditoren bei der Gap-Analyse.",
            "summary": "Zusammenfassung",
            "frameworks": "Frameworks",
            "total_controls": "Wombat Controls insgesamt",
            "avg_coverage": "Durchschnittliche Abdeckung",
            "coverage_table": "Abdeckung pro Framework",
            "col_framework": "Framework",
            "col_controls": "Controls",
            "col_coverage": "Abdeckung",
            "col_severity": "Schweregrad-Verteilung",
            "col_pillars": "Top-Säulen",
            "pillar_breakdown": "Säulen-Abdeckung pro Framework",
            "gaps": "Lücken und Empfehlungen",
            "no_gaps": "Alle priorisierten Frameworks erreichen mindestens 10 % Abdeckung. Fokus liegt auf ISO 27001, BSI C5, GDPR und SOC 2 als Kernthemen.",
            "see_frameworks": "Framework-spezifische Mappings",
            "see_central": "Zentrales regulatorisches Mapping",
            "footnote": "Abdeckung = Anteil der Wombat Controls, die mindestens eine Anforderung des Frameworks abbilden.",
        },
        "en": {
            "title": "Compliance Dashboard",
            "intro": "This page shows how well the Wombat control catalog covers the most important compliance frameworks and helps auditors with gap analysis.",
            "summary": "Summary",
            "frameworks": "Frameworks",
            "total_controls": "Total Wombat controls",
            "avg_coverage": "Average coverage",
            "coverage_table": "Coverage per framework",
            "col_framework": "Framework",
            "col_controls": "Controls",
            "col_coverage": "Coverage",
            "col_severity": "Severity distribution",
            "col_pillars": "Top pillars",
            "pillar_breakdown": "Pillar coverage per framework",
            "gaps": "Gaps and recommendations",
            "no_gaps": "All prioritized frameworks reach at least 10 % coverage. Focus is on ISO 27001, BSI C5, GDPR, and SOC 2 as core themes.",
            "see_frameworks": "Framework-specific mappings",
            "see_central": "Central regulatory mapping",
            "footnote": "Coverage = share of Wombat controls that map to at least one requirement of the framework.",
        },
    }[lang]

    # Aggregate per framework
    fw_stats = {}
    for cid, c in controls.items():
        for fw in c["frameworks"]:
            if fw not in fw_stats:
                fw_stats[fw] = {
                    "controls": set(),
                    "severity": Counter(),
                    "pillars": Counter(),
                }
            fw_stats[fw]["controls"].add(cid)
            fw_stats[fw]["severity"][c["severity"]] += 1
            fw_stats[fw]["pillars"][c["pillar"]] += 1

    lines = [
        f"= {labels['title']}",
        ":page-toc: right",
        f":description: {labels['title']}",
        "",
        labels["intro"],
        "",
        f"== {labels['summary']}",
        "",
        '[cols="1,1,1"]',  # 3 columns not 4 to avoid blank cells
        "|===",
        f"|{labels['frameworks']} |{labels['total_controls']} |{labels['avg_coverage']}",
        "",
        f"|{len(fw_stats)} |{total} |{sum(len(s['controls']) for s in fw_stats.values()) // max(len(fw_stats), 1)} %",
        "",
        "|===",
        "",
        f"== {labels['coverage_table']}",
        "",
        '[cols="2,1,1,3,3", options="header"]',
        "|===",
        f"|{labels['col_framework']} |{labels['col_controls']} |{labels['col_coverage']} |{labels['col_severity']} |{labels['col_pillars']}",
        "",
    ]

    for fw in TARGET_FRAMEWORKS:
        stats = fw_stats.get(fw, {"controls": set(), "severity": Counter(), "pillars": Counter()})
        count = len(stats["controls"])
        coverage = round(count / total * 100)
        slug = FRAMEWORK_BADGES.get(fw, (None, None))[1] or ""
        severity_cell = " ".join(
            f"{SEVERITY_EMOJI.get(sv, '')} {stats['severity'].get(sv, 0)}"
            for sv in ["critical", "high", "medium", "low"]
        )
        top_pillars = ", ".join(
            PILLAR_LABELS[lang].get(p, p)
            for p, _ in stats["pillars"].most_common(3)
        ) or "—"
        lines.append(
            f"|xref:controls:frameworks/{slug}.adoc[{fw}] |{count} |{coverage} % |{severity_cell} |{top_pillars}"
        )
        lines.append("")

    lines.append("|===")
    lines.append("")

    # Pillar breakdown per framework
    lines.append(f"== {labels['pillar_breakdown']}")
    lines.append("")
    lines.append('[cols="2,1,1,1,1,1,1,1,1", options="header"]')
    lines.append("|===")
    lines.append(f"|{labels['col_framework']} |Security |Cost |Perf |Rel |Ops |Sus |Sov |Agn")
    lines.append("")

    for fw in TARGET_FRAMEWORKS:
        stats = fw_stats.get(fw, {"pillars": Counter()})
        row = [f"|xref:controls:frameworks/{FRAMEWORK_BADGES[fw][1]}.adoc[{FRAMEWORK_BADGES[fw][0]}]"]
        for p in ["security", "cost", "efficiancy", "reliability", "excellence", "sustainability", "sovereign", "agentic"]:
            row.append(str(stats["pillars"].get(p, 0)))
        lines.append(" |".join(row))
        lines.append("")

    lines.append("|===")
    lines.append("")

    # Gaps
    lines.append(f"== {labels['gaps']}")
    lines.append("")
    low_coverage = [
        fw for fw in TARGET_FRAMEWORKS
        if len(fw_stats.get(fw, {"controls": set()})["controls"]) / total < 0.10
    ]
    if low_coverage:
        lines.append("The following frameworks have < 10 % coverage and may need additional controls:")
        lines.append("")
        for fw in low_coverage:
            lines.append(f"* {fw}")
        lines.append("")
    else:
        lines.append(labels["no_gaps"])
        lines.append("")

    lines.append(f"* xref:controls:catalog.adoc[{labels['see_frameworks']}]")
    lines.append(f"* xref:ROOT:resources/regulatory-mapping.adoc[{labels['see_central']}]")
    lines.append("")
    lines.append(f"_{labels['footnote']}_")
    lines.append("")

    return "\n".join(lines)


SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
}


def update_catalog_table(repo_root, controls, lang):
    path = Path(repo_root) / "modules" / "controls" / "pages" / "catalog.adoc"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace all [cols="1,3,1,1,1"] with [cols="1,3,1,1,1,2"]
    content = content.replace('[cols="1,3,1,1,1"]', '[cols="1,3,1,1,1,2"]')

    # Add Compliance header to each table (idempotent)
    if "|Control ID |Title |Severity |Provider |Category |Compliance" not in content:
        content = content.replace(
            "|Control ID |Title |Severity |Provider |Category",
            "|Control ID |Title |Severity |Provider |Category |Compliance",
        )

    # Add compliance cell to each control row in summary tables.
    # We target rows like:
    # |xref:#WAF-SEC-010[WAF-SEC-010]
    # |...
    # |...
    # |...
    # |...
    #
    # followed by a blank line and the next row or |===

    def row_replacer(match):
        lines = match.group(0).split("\n")
        m = re.match(r"\|xref:#(WAF-[A-Z]{3,4}-\d{3})\[", lines[0])
        if not m:
            return match.group(0)
        cid = m.group(1)
        fw = controls.get(cid, {}).get("frameworks", [])
        badge = compliance_cell(fw, lang)
        # Drop trailing empty lines, then append compliance cell and row separator
        new_lines = [l for l in lines if l]
        new_lines.append(f"|{badge}")
        new_lines.append("")
        return "\n".join(new_lines)

    # Match a 5-cell row block starting with |xref:#WAF-... and ending with blank line.
    # The 5th cell must be the category (lowercase word with hyphens). This makes
    # the replacement idempotent: rows that already have a 6th Compliance cell are
    # skipped because category is followed by |compliance, not a blank line.
    pattern = re.compile(
        r"^\|xref:#WAF-[A-Z]{3,4}-\d{3}\[.*?\n\|.*?\n\|.*?\n\|.*?\n\|[a-z][a-z0-9-]*\n\n",
        re.MULTILINE,
    )
    content = pattern.sub(row_replacer, content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def write_dashboard(repo_root, controls, lang):
    out_dir = Path(repo_root) / "modules" / "controls" / "pages"
    out_dir.mkdir(parents=True, exist_ok=True)
    content = generate_dashboard(controls, lang)
    (out_dir / "compliance-dashboard.adoc").write_text(content, encoding="utf-8")


def update_nav(repo_root, lang):
    path = Path(repo_root) / "modules" / "controls" / "nav.adoc"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    label = "Compliance-Dashboard" if lang == "de" else "Compliance Dashboard"
    new_entry = f"** xref:controls:compliance-dashboard.adoc[{label}]"

    if new_entry not in content:
        content = content.replace(
            "** xref:controls:catalog.adoc[Controls-Katalog]\n",
            f"** xref:controls:catalog.adoc[Controls-Katalog]\n{new_entry}\n",
        )
        content = content.replace(
            "** xref:controls:catalog.adoc[Controls Catalog]\n",
            f"** xref:controls:catalog.adoc[Controls Catalog]\n{new_entry}\n",
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def update_index(repo_root, lang):
    path = Path(repo_root) / "modules" / "controls" / "pages" / "index.adoc"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    label = "Compliance-Dashboard" if lang == "de" else "Compliance Dashboard"
    new_line = f"* Der vollständige Katalog mit Details ist unter xref:catalog.adoc[Controls-Katalog] verfügbar, zusammen mit dem xref:compliance-dashboard.adoc[{label}] für Compliance-Abdeckung."
    en_line = "* The full catalog with details is available at xref:catalog.adoc[Controls Catalog], together with the xref:compliance-dashboard.adoc[Compliance Dashboard] for compliance coverage."

    if "xref:compliance-dashboard.adoc" not in content:
        content = content.replace(
            "* Der vollständige Katalog mit Details ist unter xref:catalog.adoc[Controls-Katalog] verfügbar",
            new_line,
        )
        content = content.replace(
            "* The complete catalog with details can be found at xref:catalog.adoc[Controls Catalog]",
            en_line,
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def process_repo(repo_root, lang):
    controls = load_controls(repo_root)
    write_dashboard(repo_root, controls, lang)
    update_catalog_table(repo_root, controls, lang)
    nav_updated = update_nav(repo_root, lang)
    index_updated = update_index(repo_root, lang)
    print(
        f"Generated compliance-dashboard.adoc, updated catalog.adoc, "
        f"nav={'updated' if nav_updated else 'unchanged'}, "
        f"index={'updated' if index_updated else 'unchanged'} in {repo_root} ({lang})"
    )


def main():
    for lang, repo_root in REPOS.items():
        process_repo(repo_root, lang)


if __name__ == "__main__":
    main()
