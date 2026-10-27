#!/usr/bin/env python3
"""Update pillar overview (index.adoc) and group (controls.adoc) pages to include
new controls added in the 83->100 expansion.

The script performs targeted, non-destructive updates:
- refreshes control counts and ID ranges in metadata and prose
- appends new rows to overview tables (controls.adoc and index.adoc)
  without touching existing rows
- appends generated summary sections for new controls in controls.adoc
  (for pillars that already contain per-control sections)
- updates the metrics table and control-range prose in index.adoc
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

PILLAR_PREFIX = {
    "security": "WAF-SEC",
    "cost": "WAF-COST",
    "efficiancy": "WAF-PERF",
    "reliability": "WAF-REL",
    "excellence": "WAF-OPS",
    "sustainability": "WAF-SUS",
    "sovereign": "WAF-SOV",
    "agentic": "WAF-AGN",
}

SEVERITY_DE = {"critical": "Kritisch", "high": "Hoch", "medium": "Mittel", "low": "Niedrig"}
SEVERITY_EN = {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low"}

PILLAR_WITH_SECTIONS = {
    "security": True,
    "cost": False,
    "efficiancy": False,
    "reliability": True,
    "excellence": True,
    "sustainability": False,
    "sovereign": True,
    "agentic": True,
}


def load_controls(repo_root):
    controls = {}
    root = Path(repo_root)
    for path in sorted((root / "modules" / "controls" / "controls").glob("WAF-*.yml")):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        controls[data["id"]] = data
    return controls


def controls_for_pillar(controls, pillar):
    prefix = PILLAR_PREFIX[pillar]
    return {cid: c for cid, c in controls.items() if cid.startswith(prefix + "-")}


def format_range(prefix, ids):
    nums = sorted(int(cid.split("-")[-1]) for cid in ids)
    return f"{prefix}-{nums[0]:03d} bis {prefix}-{nums[-1]:03d}"


def update_heading_count(text, old_count, new_count, prefix):
    """Update headings like '== Schnellübersicht: 10 WAF-SEC Controls'."""
    escaped_prefix = re.escape(prefix)
    # Match a heading line containing: number + prefix + optional middle + Controls
    pattern = re.compile(
        rf"^(== .*?\s){old_count}(\s+{escaped_prefix}(?:-[A-Z]+)?\s+.*Controls.*)$",
        re.M | re.I,
    )
    text = pattern.sub(rf"\g<1>{new_count}\g<2>", text)
    return text


def update_count_text(text, old_count, new_count, lang):
    old_s = str(old_count)
    new_s = str(new_count)

    def repl_generic(m):
        """Preserve the exact prefix/suffix around the number."""
        full = m.group(0)
        idx = full.lower().find(old_s.lower())
        return full[:idx] + new_s + full[idx + len(old_s):]

    if lang == "de":
        text = re.sub(rf"\b{old_s}\s+messbare\s+Controls\b", repl_generic, text, flags=re.I)
        text = re.sub(rf"\ballen\s+{old_s}\s+Controls\b", repl_generic, text, flags=re.I)
        text = re.sub(rf"\balle\s+{old_s}\s+Controls\b", repl_generic, text, flags=re.I)
        text = re.sub(rf"\bdie\s+{old_s}\s+Controls\b", repl_generic, text, flags=re.I)
        text = re.sub(rf"\bdie\s+{old_s}\s+messbaren\s+Controls\b", repl_generic, text, flags=re.I)
        text = re.sub(rf"\b{old_s}\s+Controls\b", repl_generic, text, flags=re.I)
        text = re.sub(rf"\ballen\s+{old_s}\b", repl_generic, text, flags=re.I)
        text = re.sub(rf"\balle\s+{old_s}\b", repl_generic, text, flags=re.I)
        text = re.sub(rf"\bdie\s+{old_s}\b", repl_generic, text, flags=re.I)
    else:
        text = re.sub(rf"\b{old_s}\s+measurable\s+controls\b", repl_generic, text, flags=re.I)
        text = re.sub(rf"\ball\s+{old_s}\s+controls\b", repl_generic, text, flags=re.I)
        text = re.sub(rf"\b{old_s}\s+controls\b", repl_generic, text, flags=re.I)
        text = re.sub(rf"\ball\s+{old_s}\b", repl_generic, text, flags=re.I)
    return text


def update_range_text(text, prefix, old_last, new_last):
    # German
    old_range = f"{prefix}-010 bis {prefix}-{old_last:03d}"
    new_range = f"{prefix}-010 bis {prefix}-{new_last:03d}"
    text = text.replace(old_range, new_range)
    text = text.replace(f"`{prefix}-010` bis `{prefix}-{old_last:03d}`", f"`{prefix}-010` bis `{prefix}-{new_last:03d}`")
    # English
    old_range_en = f"{prefix}-010 through {prefix}-{old_last:03d}"
    new_range_en = f"{prefix}-010 through {prefix}-{new_last:03d}"
    text = text.replace(old_range_en, new_range_en)
    text = text.replace(f"`{prefix}-010` through `{prefix}-{old_last:03d}`", f"`{prefix}-010` through `{prefix}-{new_last:03d}`")
    # Generic "to"
    old_range_to = f"{prefix}-010 to {prefix}-{old_last:03d}"
    new_range_to = f"{prefix}-010 to {prefix}-{new_last:03d}"
    text = text.replace(old_range_to, new_range_to)
    return text


def severity_word(sev, lang):
    return SEVERITY_DE[sev] if lang == "de" else SEVERITY_EN[sev]


def automatable_word(automatable, lang):
    if lang == "de":
        mapping = {
            "High": "Hoch",
            "Medium": "Mittel",
            "Low": "Niedrig",
            "Partial": "Teilweise",
            "Yes": "Ja",
            "No": "Nein",
        }
        return mapping.get(str(automatable), str(automatable))
    return str(automatable)


def infer_table_columns(table_text):
    """Infer the number of table columns from the [cols=...] attribute."""
    cols_match = re.search(r'\[cols="([^"]+)"\]', table_text)
    if cols_match:
        cols_spec = cols_match.group(1)
        # Count comma-separated entries; each entry is one column
        return len([c for c in cols_spec.split(",") if c.strip()])
    # Fallback: count pipe-delimited header cells
    for line in table_text.splitlines()[:8]:
        if line.startswith("|") and not line.startswith("|==="):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if cells:
                return len(cells)
    return 5


def brief_description(data, lang):
    sentences = [s.strip() for s in data["description"].split(". ") if s.strip()]
    desc = sentences[0] + "." if sentences else data["description"]
    if len(desc) > 90:
        desc = desc[:87].rstrip() + "..."
    return desc


def table_row_controls(cid, data, lang, columns):
    title = data["title"]
    display_title = title if len(title) <= 55 else title[:52].rstrip() + "..."
    sev_word = severity_word(data["severity"], lang)
    cat = data.get("category", "").replace("-", " ")
    auto = automatable_word(data.get("automatable", "Medium"), lang)
    desc = brief_description(data, lang)
    cells = [f"|xref:controls/{cid}.adoc[{cid}]", f"|{display_title}", f"|{sev_word}"]
    if columns >= 4:
        cells.append(f"|{cat}")
    if columns >= 5:
        cells.append(f"|{auto}")
    if columns >= 6:
        cells.append(f"|{desc}")
    return "\n".join(cells) + "\n"


def generated_control_section(cid, data, lang):
    title = data["title"]
    sentences = [s.strip() for s in data["description"].split(". ") if s.strip()]
    desc = sentences[0] + "." if sentences else data["description"]
    if lang == "de":
        lines = [
            f"\n[#{cid}]",
            f"== {cid} – {title}",
            "",
            f"*Severity:* {severity_word(data['severity'], 'de')} | *Kategorie:* {data.get('category','').replace('-',' ').title()} | *Automatisierbar:* {automatable_word(data.get('automatable','Medium'), 'de')}",
            "",
            desc,
            "",
            f"*Terraform/Config Checks:* {len(data.get('checks', []))} Checks definiert.",
            "",
            f"xref:controls/{cid}.adoc[Details →]",
            "",
            "---",
            "",
        ]
    else:
        lines = [
            f"\n[#{cid}]",
            f"== {cid} – {title}",
            "",
            f"*Severity:* {severity_word(data['severity'], 'en')} | *Category:* {data.get('category','').replace('-',' ').title()} | *Automatable:* {automatable_word(data.get('automatable','Medium'), 'en')}",
            "",
            desc,
            "",
            f"*Terraform/Config Checks:* {len(data.get('checks', []))} checks defined.",
            "",
            f"xref:controls/{cid}.adoc[Details →]",
            "",
            "---",
            "",
        ]
    return "\n".join(lines)


def find_table_end_after(text, start_pos):
    """Find the closing '\n|===' after start_pos, skipping the opening delimiter."""
    first = text.find("\n|===", start_pos)
    if first == -1:
        return -1
    return text.find("\n|===", first + 1)


def detect_old_state(text, prefix):
    """Detect old_last and old_count from existing control IDs in the file text."""
    existing = sorted(set(re.findall(rf"{prefix}-\d{{3}}", text)))
    if not existing:
        return None, 0
    old_last = max(int(cid.split("-")[-1]) for cid in existing)
    old_count = len(existing)
    return old_last, old_count


def update_controls_adoc(path, controls, pillar, lang):
    text = path.read_text(encoding="utf-8")
    prefix = PILLAR_PREFIX[pillar]
    ids = sorted(controls.keys())
    new_last = max(int(cid.split("-")[-1]) for cid in ids)
    new_count = len(ids)

    old_last, old_count = detect_old_state(text, prefix)
    if old_last is None:
        old_last = new_last
        old_count = new_count

    # Update description / prose counts and ranges
    text = update_range_text(text, prefix, old_last, new_last)
    if old_count and old_count != new_count:
        text = update_count_text(text, old_count, new_count, lang)

    # Append missing controls to overview table
    table_start = text.find("== Controls-Übersicht")
    if table_start == -1:
        table_start = text.find("== Controls Overview")
    if table_start != -1:
        table_end = find_table_end_after(text, table_start)
        if table_end != -1:
            table_text = text[table_start:table_end]
            present = set(re.findall(rf"{prefix}-\d{{3}}", table_text))
            missing = [cid for cid in ids if cid not in present]
            if missing:
                columns = infer_table_columns(table_text)
                rows = "".join(table_row_controls(cid, controls[cid], lang, columns) for cid in missing)
                text = text[:table_end] + "\n" + rows + text[table_end:]

    # Append generated summary sections for pillars that already have sections
    if PILLAR_WITH_SECTIONS[pillar]:
        # Detect sections by anchors or headings, not just ID presence anywhere
        present_sections = set()
        for cid in ids:
            anchor_pat = rf"^\[{re.escape(cid)}\]\s*$"
            heading_pat = rf"^==\s+{re.escape(cid)}\b"
            if re.search(anchor_pat, text, re.M) or re.search(heading_pat, text, re.M):
                present_sections.add(cid)
        missing = [cid for cid in ids if cid not in present_sections]
        if missing:
            final_marker = "== Vollständiger Controls-Katalog"
            final_pos = text.find(final_marker)
            if final_pos == -1:
                final_marker = "== Full Controls Catalog"
                final_pos = text.find(final_marker)
            sections = "".join(generated_control_section(cid, controls[cid], lang) for cid in missing)
            if final_pos != -1:
                text = text[:final_pos] + sections + "\n" + text[final_pos:]
            else:
                text = text.rstrip() + "\n" + sections

    path.write_text(text, encoding="utf-8")
    return new_count


def table_row_index(cid, data, lang, columns):
    """Generate row for index.adoc quick overview table.

    We infer whether the 4th column is severity or automatable from the table header.
    If uncertain, we emit a 3-cell row and let AsciiDoc pad it.
    """
    title = data["title"]
    display_title = title if len(title) <= 55 else title[:52].rstrip() + "..."
    sev_word = severity_word(data["severity"], lang)
    auto = automatable_word(data.get("automatable", "Medium"), lang)
    # columns is 3 or 4 typically
    if columns == 4:
        # guess based on header whether 4th cell should be automatable or category
        return (
            f"|xref:controls.adoc#{cid}[{cid}]\n"
            f"|{display_title}\n"
            f"|{sev_word}\n"
            f"|{auto}\n"
        )
    return (
        f"|xref:controls.adoc#{cid}[{cid}]\n"
        f"|{display_title}\n"
        f"|{sev_word}\n"
    )


def update_index_adoc(path, controls, pillar, lang):
    text = path.read_text(encoding="utf-8")
    prefix = PILLAR_PREFIX[pillar]
    ids = sorted(controls.keys())
    new_last = max(int(cid.split("-")[-1]) for cid in ids)
    new_count = len(ids)

    old_last, old_count = detect_old_state(text, prefix)
    if old_last is None:
        old_last = new_last
        old_count = new_count

    # Update prose counts and ranges
    text = update_range_text(text, prefix, old_last, new_last)
    if old_count and old_count != new_count:
        text = update_count_text(text, old_count, new_count, lang)
        text = update_heading_count(text, old_count, new_count, prefix)

    # Update quick overview table
    section_markers = [
        "== Controls-Überblick",
        "== Controls Overview",
        "== Schnellübersicht",
        "== Quick Overview",
        "== Übersicht",
        "== Overview",
    ]
    section_start = -1
    for marker in section_markers:
        section_start = text.find(marker)
        if section_start != -1:
            break
    if section_start != -1:
        table_end = find_table_end_after(text, section_start)
        if table_end != -1:
            table_text = text[section_start:table_end]
            present = set(re.findall(rf"{prefix}-\d{{3}}", table_text))
            missing = [cid for cid in ids if cid not in present]
            if missing:
                columns = infer_table_columns(table_text)
                rows = "".join(table_row_index(cid, controls[cid], lang, columns) for cid in missing)
                text = text[:table_end] + "\n" + rows + text[table_end:]

    # Update metrics table count
    metric_title = "Controls gesamt" if lang == "de" else "Controls total"
    metric_pattern = re.compile(rf"(\|{metric_title}\n\|)\d+\s*\([^)]*\)", re.M)
    text = metric_pattern.sub(rf"\g<1>{new_count} ({format_range(prefix, ids)})", text)

    path.write_text(text, encoding="utf-8")
    return new_count


def process_repo(repo_root, lang):
    controls = load_controls(repo_root)
    updated = 0
    for pillar, module in PILLAR_MODULE.items():
        pc = controls_for_pillar(controls, pillar)
        if not pc:
            continue
        controls_path = Path(repo_root) / "modules" / module / "pages" / "controls.adoc"
        index_path = Path(repo_root) / "modules" / module / "pages" / "index.adoc"

        if controls_path.exists():
            update_controls_adoc(controls_path, pc, pillar, lang)
        if index_path.exists():
            update_index_adoc(index_path, pc, pillar, lang)
        updated += 1
    return updated


def main():
    for lang, repo_root in REPOS.items():
        process_repo(repo_root, lang)
        print(f"Updated {lang} repo: {repo_root}")


if __name__ == "__main__":
    main()
