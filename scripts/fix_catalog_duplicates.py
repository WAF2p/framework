#!/usr/bin/env python3
"""Clean up the catalog rows added by generate_new_controls_100.py.

For each pillar table: remove duplicate/leading misplaced rows for the new
controls and re-insert exactly one row per new control in ID order just before
the table's closing |===.
"""
import re
from pathlib import Path

REPOS = {
    "de": ".",
    "en": "../framework-en",
}

NEW_CONTROLS = {
    "Pillar 1 · Security – WAF-SEC": [
        ("WAF-SEC-140", "Web Application Firewall and DDoS protection MUST be enabled for public endpoints", "high", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "network-security"),
        ("WAF-SEC-150", "Vulnerability and patch management MUST cover compute instances, operating systems, and endpoints", "high", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "container-security"),
        ("WAF-SEC-160", "Security-relevant logs MUST be centrally collected and protected against tampering", "high", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "logging-monitoring"),
    ],
    "Pillar 2 · Cost Optimization – WAF-COST": [
        ("WAF-COST-110", "Spot and preemptible instances MUST be explicitly allowed and documented where workload characteristics permit", "medium", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "data-governance"),
        ("WAF-COST-120", "Reserved capacity and savings plans MUST be reviewed and documented for steady-state workloads", "medium", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "cost-governance"),
    ],
    "Pillar 3 · Performance Efficiency – WAF-PERF": [
        ("WAF-PERF-110", "Caching strategies MUST be defined for workloads with repeated read patterns or latency-sensitive endpoints", "medium", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "network-security"),
        ("WAF-PERF-120", "Database workloads MUST undergo regular index and query performance reviews", "medium", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "logging-monitoring"),
    ],
    "Pillar 4 · Reliability – WAF-REL": [
        ("WAF-REL-110", "Circuit breaker, backpressure, and rate limiting MUST be defined for downstream dependencies", "high", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "reliability-design"),
        ("WAF-REL-120", "Graceful degradation and fallback strategies MUST be documented and tested", "high", "Any", "reliability-design"),
        ("WAF-REL-130", "Disaster recovery plans MUST be tested at least annually and updated based on test results", "high", "Any", "backup-recovery"),
    ],
    "Pillar 5 · Operational Excellence – WAF-OPS": [
        ("WAF-OPS-110", "GitOps-based deployments SHOULD be preferred for Kubernetes and container workloads", "medium", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "deployment-automation"),
        ("WAF-OPS-120", "Feature flags MUST be available and documented for high-risk changes", "medium", "Any", "deployment-automation"),
    ],
    "Pillar 6 · Sustainability – WAF-SUS": [
        ("WAF-SUS-110", "Regional carbon intensity MUST be considered and documented in location decisions", "medium", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "data-governance"),
        ("WAF-SUS-120", "Batch and HPC workloads SHOULD run off-peak where SLA constraints allow", "low", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "sustainability-efficiency"),
    ],
    "Pillar 7 · Sovereign Cloud – WAF-SOV": [
        ("WAF-SOV-110", "Cryptographic keys for sensitive data MUST be managed in HSM or sovereign key management services", "critical", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "encryption-key-management"),
        ("WAF-SOV-120", "Data processing agreements MUST be documented for every sub-processor", "high", "Any", "data-governance"),
    ],
    "Pillar 8 · Agentic – WAF-AGN": [
        ("WAF-AGN-110", "Agent outputs and actions MUST be validated, sandboxed, and restricted to allowlists", "high", "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**", "agentic-governance"),
    ],
}

SEVERITY_EMOJI = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}


def clean_catalog(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    section_starts = {}
    section_order = []
    for i, line in enumerate(lines):
        m = re.match(r"^== (Pillar \d+ · .+ – WAF-[A-Z]{3,4})\s*$", line)
        if m:
            section_starts[m.group(1)] = i
            section_order.append(m.group(1))

    new_lines = []
    last_end = 0
    for idx, section in enumerate(section_order):
        start = section_starts[section]
        end = section_starts[section_order[idx + 1]] if idx + 1 < len(section_order) else len(lines)
        chunk = lines[start:end]

        new_cids = {r[0] for r in NEW_CONTROLS.get(section, [])}
        cleaned = []
        i = 0
        while i < len(chunk):
            line = chunk[i]
            m = re.match(r"\|xref:#(WAF-[A-Z]{3,4}-\d{3})\[WAF-[A-Z]{3,4}-\d{3}\]", line)
            if m and m.group(1) in new_cids:
                # skip this row and the following lines until we hit an empty line or |=== or another control row
                while i + 1 < len(chunk):
                    nxt = chunk[i + 1]
                    if nxt.strip() == "" or nxt.strip() == "|===" or nxt.startswith("|xref:#WAF-"):
                        break
                    i += 1
                i += 1
                continue
            # drop stray duplicate header rows inside table bodies
            if line.startswith("|Control ID |Title |Severity |Provider |Category |Compliance") and cleaned.count("|===") > 0:
                i += 1
                continue
            cleaned.append(line)
            i += 1

        # Re-insert rows before the final |=== of this section
        rows = NEW_CONTROLS.get(section, [])
        if rows:
            inserted = []
            for cid, title, sev, providers, category in rows:
                emoji = SEVERITY_EMOJI[sev]
                sev_word = sev.title()
                inserted.extend([
                    f"|xref:#{cid}[{cid}]",
                    f"|{title}",
                    f"|{emoji} {sev_word}",
                    f"|{providers}",
                    f"|{category}",
                    "",
                ])
            # find last |=== in cleaned (table end)
            for j in range(len(cleaned) - 1, -1, -1):
                if cleaned[j].strip() == "|===":
                    cleaned = cleaned[:j] + [""] + inserted + cleaned[j:]
                    break

        new_lines.extend(lines[last_end:start])
        new_lines.extend(cleaned)
        last_end = end

    new_lines.extend(lines[last_end:])
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def main():
    for lang, repo_root in REPOS.items():
        path = Path(repo_root) / "modules" / "controls" / "pages" / "catalog.adoc"
        clean_catalog(path)
        print(f"Cleaned catalog in {repo_root}")


if __name__ == "__main__":
    main()
