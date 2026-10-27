#!/usr/bin/env python3
"""Enrich control rationale and maturity_levels based on control metadata.

Generates control-specific rationale text (risk/business context) and
five-level maturity criteria that fit the control type and category.
Applies to all 83 YAML controls in both language repositories.
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

PILLAR_ORDER = ["security", "cost", "efficiancy", "reliability", "excellence", "sustainability", "sovereign", "agentic"]

CATEGORY_LABELS = {
    "de": {
        "identity-access": "Identitäts- und Zugriffsmanagement",
        "network-security": "Netzwerksicherheit",
        "network-encryption": "Netzwerkverschlüsselung",
        "container-security": "Container-Sicherheit",
        "secret-management": "Secrets-Management",
        "data-governance": "Daten-Governance",
        "cost-governance": "Kosten-Governance",
        "logging-monitoring": "Logging und Monitoring",
        "deployment-automation": "Deployment-Automation",
        "reliability-design": "Zuverlässigkeitsdesign",
        "backup-recovery": "Backup und Wiederherstellung",
        "encryption-key-management": "Schlüsselmanagement",
        "agentic-governance": "Agentic-Governance",
        "sustainability-efficiency": "Nachhaltigkeitseffizienz",
    },
    "en": {
        "identity-access": "Identity and Access Management",
        "network-security": "Network Security",
        "network-encryption": "Network Encryption",
        "container-security": "Container Security",
        "secret-management": "Secrets Management",
        "data-governance": "Data Governance",
        "cost-governance": "Cost Governance",
        "logging-monitoring": "Logging and Monitoring",
        "deployment-automation": "Deployment Automation",
        "reliability-design": "Reliability Design",
        "backup-recovery": "Backup and Recovery",
        "encryption-key-management": "Encryption Key Management",
        "agentic-governance": "Agentic Governance",
        "sustainability-efficiency": "Sustainability Efficiency",
    },
}

RISK_SENTENCES = {
    "de": {
        "identity-access": "Unkontrollierte Identitäten und übermäßige Berechtigungen ermöglichen Datendiebstahl, Lateral Movement und unautorisierte Änderungen an Produktivsystemen.",
        "network-security": "Offene Netzwerke und unzureichende Segmentierung erlauben Angriffe von außen sowie das Ausbreiten von Bedrohungen innerhalb der Infrastruktur.",
        "network-encryption": "Unverschlüsselte Datenübertragung ermöglicht Abhören, Man-in-the-Middle-Angriffe und Verstöße gegen Datenschutz- und Compliance-Anforderungen.",
        "container-security": "Unsichere Container und Images führen zu Angriffsflächen, Supply-Chain-Risiken und der Verbreitung von Malware in Produktivumgebungen.",
        "secret-management": "Hardcodierte oder schlecht verwaltete Secrets ermöglichen unautorisierten Zugriff, Datenlecks und Eskalation innerhalb des Cloud-Ökosystems.",
        "data-governance": "Fehlende Datenklassifizierung, -eigentümerschaft und Lifecycle-Steuerung erhöhen Compliance-Risiken, Kosten und die Wahrscheinlichkeit von Datenverlusten.",
        "cost-governance": "Mangelnde Kostentransparenz und fehlende Governance führen zu Budgetüberschreitungen, Cloud-Waste und nicht nachvollziehbaren Ausgaben.",
        "logging-monitoring": "Unzureichende Beobachtbarkeit verzögert die Erkennung von Incidents, erschwert die Fehleranalyse und verhindert wirksame Audit-Nachweise.",
        "deployment-automation": "Manuelle Deployments und fehlende Qualitätsgates erhöhen das Risiko von Ausfällen, menschlichen Fehlern und nicht reproduzierbaren Umgebungen.",
        "reliability-design": "Mangelhafte Ausfallsicherheit und Planung führen zu Serviceunterbrechungen, Datenverlust und Vertrauensverlust bei Kunden und Stakeholdern.",
        "backup-recovery": "Fehlende oder ungetestete Wiederherstellungspläne verlängern Ausfallzeiten, erhöhen den Datenverlust und gefährden die Geschäftskontinuität.",
        "encryption-key-management": "Schwaches oder zentralisiertes Schlüsselmanagement ermöglicht Entschlüsselung durch Angreifer, Insider-Bedrohungen und Compliance-Verstöße.",
        "agentic-governance": "Ungouvernierte Agenten treffen unreviewte Entscheidungen, verarbeiten sensible Daten ungeschützt und hinterlassen keine nachvollziehbare Audit-Spur.",
        "sustainability-efficiency": "Ineffiziente Ressourcennutzung erhöht Energieverbrauch, CO₂-Fußabdruck und Kosten, ohne Mehrwert für das Geschäft zu schaffen.",
    },
    "en": {
        "identity-access": "Uncontrolled identities and excessive permissions enable data theft, lateral movement, and unauthorized changes to production systems.",
        "network-security": "Open networks and insufficient segmentation allow external attacks and the spread of threats inside the infrastructure.",
        "network-encryption": "Unencrypted data transfer enables eavesdropping, man-in-the-middle attacks, and violations of data-protection and compliance requirements.",
        "container-security": "Insecure containers and images create attack surface, supply-chain risk, and malware propagation in production environments.",
        "secret-management": "Hardcoded or poorly managed secrets enable unauthorized access, data leakage, and escalation within the cloud ecosystem.",
        "data-governance": "Missing data classification, ownership, and lifecycle control increase compliance risk, cost, and the likelihood of data loss.",
        "cost-governance": "Lack of cost transparency and governance leads to budget overruns, cloud waste, and unaccountable spending.",
        "logging-monitoring": "Insufficient observability delays incident detection, complicates troubleshooting, and prevents effective audit evidence.",
        "deployment-automation": "Manual deployments and missing quality gates increase the risk of outages, human error, and non-reproducible environments.",
        "reliability-design": "Poor fault tolerance and planning lead to service interruptions, data loss, and loss of trust from customers and stakeholders.",
        "backup-recovery": "Missing or untested recovery plans prolong downtime, increase data loss, and endanger business continuity.",
        "encryption-key-management": "Weak or centralized key management enables decryption by attackers, insider threats, and compliance violations.",
        "agentic-governance": "Ungoverned agents make unreviewed decisions, process sensitive data without protection, and leave no traceable audit trail.",
        "sustainability-efficiency": "Inefficient resource usage increases energy consumption, carbon footprint, and cost without creating business value.",
    },
}


def clean_text(text):
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()


def first_sentence(text):
    text = clean_text(text)
    if not text:
        return ""
    # Take first sentence up to a period, avoiding decimals and abbreviations.
    match = re.match(r"([^.]+(?:\.\s+[A-Z][^.]*)?\.)?", text)
    if match:
        return match.group(0).strip()
    return text[:160]


def describe_in_words(cid, category, lang):
    labels = CATEGORY_LABELS[lang]
    cat_label = labels.get(category, category.replace("-", " ").title())
    if lang == "de":
        return f"die Anforderungen des Bereichs '{cat_label}'"
    return f"the requirements of the '{cat_label}' area"


def generate_rationale(data, lang):
    category = data.get("category", "")
    base = RISK_SENTENCES[lang].get(category, "")
    if not base:
        base = RISK_SENTENCES[lang].get("data-governance")
    control_desc = clean_text(data.get("description", ""))
    # Shorten the control description for the rationale, keep the normative core.
    if len(control_desc) > 160:
        # Try to end at a sentence boundary
        idx = control_desc.rfind(". ", 0, 160)
        if idx == -1:
            idx = control_desc.rfind(" ", 0, 160)
        control_desc = control_desc[:idx] + "." if idx > 0 else control_desc[:160]
    # Normalize case so the rationale sentence starts with a capital letter and reads well.
    control_desc = re.sub(r"^\s*[a-z]", lambda m: m.group(0).upper(), control_desc)
    if lang == "de":
        return f"{base} Dieses Control adressiert {describe_in_words(data['id'], category, lang)} und stellt sicher, dass {control_desc}"
    return f"{base} This control addresses {describe_in_words(data['id'], category, lang)} and ensures that {control_desc}"


def generate_maturity_levels(data, lang):
    category = data.get("category", "")
    ctype = data.get("type", [])
    title = clean_text(data.get("title", ""))
    # Use a short action phrase based on the description if title is too long/generic
    short_action = title
    if len(title) > 60 or title.lower().startswith("all ") or title.lower().startswith("every "):
        desc = clean_text(data.get("description", ""))
        # Extract the first normative sentence (ending before the next sentence).
        sentences = re.split(r"(?<=[.!?])\s+", desc)
        normative_sentence = ""
        for s in sentences:
            if re.search(r"\b(MUST|SHOULD|SHALL|MUST NOT)\b", s):
                normative_sentence = s
                break
        if not normative_sentence:
            normative_sentence = first_sentence(desc)
        # Strip modal verbs and leading filler, keep the meaningful noun phrase + verb phrase.
        cleaned = re.sub(r"\b(MUST|SHOULD|SHALL|MUST NOT)\b", "", normative_sentence)
        # Remove trailing enumerations/clauses that make the phrase too long
        cleaned = re.sub(r"\s+(,|;|:)\s+.*", "", cleaned)
        # Also truncate after parenthetical lists
        cleaned = re.sub(r"\s+\([^)]{15,}\).*", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip().rstrip(".")
        if len(cleaned) > 70:
            cleaned = cleaned[:67] + "..."
        short_action = cleaned
    short_action = re.sub(r"\s+", " ", short_action).strip()
    if len(short_action) > 80:
        short_action = short_action[:77] + "..."

    if isinstance(ctype, str):
        ctype = [ctype]
    has_governance = "governance" in ctype
    has_config = "configuration" in ctype or "automation" in ctype
    has_process = "process" in ctype

    if lang == "de":
        l1 = "Die Anforderung ist nicht einheitlich umgesetzt; Nachweis existiert nur punktuell oder fehlt."
        if has_governance:
            l2 = "Eine dokumentierte Policy oder ein Standard beschreibt die Anforderung."
        elif has_process:
            l2 = "Ein dokumentierter Prozess und Verantwortlicher sind festgelegt."
        else:
            l2 = "Die Anforderung ist dokumentiert; erste Ressourcen zeigen die gewünschte Konfiguration."

        if has_config:
            l3 = "Terraform-Checks oder IaC-Gates prüfen die Anforderung automatisch in CI/CD."
        else:
            l3 = "Die Umsetzung wird regelmäßig überprüft und in Reviews nachgewiesen."

        l4 = "Abdeckung, Ausnahmen und Qualitätsmetriken werden quartalsweise berichtet."
        l5 = "Die Effektivität wird kontinuierlich gemessen und automatisch optimiert."
    else:
        l1 = "The requirement is not consistently implemented; evidence exists only ad-hoc or is missing."
        if has_governance:
            l2 = "A documented policy or standard describes the requirement."
        elif has_process:
            l2 = "A documented process and owner are defined."
        else:
            l2 = "The requirement is documented; initial resources show the intended configuration."

        if has_config:
            l3 = "Terraform checks or IaC gates automatically validate the requirement in CI/CD."
        else:
            l3 = "Implementation is regularly reviewed and evidenced in reviews."

        l4 = "Coverage, exceptions, and quality metrics are reported quarterly."
        l5 = "Effectiveness is continuously measured and automatically improved."

    return {
        "level_1": {"description": "Ad hoc – control not consistently applied", "criteria": [l1]},
        "level_2": {"description": "Standardised – policy defined and communicated", "criteria": [l2]},
        "level_3": {"description": "Integrated – automated validation in CI/CD", "criteria": [l3]},
        "level_4": {"description": "Auditable – metrics and exceptions tracked", "criteria": [l4]},
        "level_5": {"description": "Optimised – continuous improvement based on data", "criteria": [l5]},
    }


def enrich_file(path, lang):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data or not data.get("id"):
        return False

    data["rationale"] = generate_rationale(data, lang)
    data["maturity_levels"] = generate_maturity_levels(data, lang)

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=1000)
    return True


def process_repo(repo_root, lang):
    files = sorted(Path(repo_root).glob("modules/controls/controls/WAF-*.yml"))
    count = 0
    for path in files:
        if enrich_file(path, lang):
            count += 1
    print(f"Enriched {count} controls in {repo_root} ({lang})")


def main():
    for lang, repo_root in REPOS.items():
        process_repo(repo_root, lang)


if __name__ == "__main__":
    main()
