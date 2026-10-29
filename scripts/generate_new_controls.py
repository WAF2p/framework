#!/usr/bin/env python3
"""Generate 17 new Wombat controls (100 total) across all 8 pillars.

Creates YAML control files in both German and English repositories, plus narrative
.adoc pages, nav entries, and catalog updates.
"""
import glob
import yaml
from pathlib import Path

REPOS = {
    "de": ".",
    "en": "../framework-en",
}

# New control definitions. Title/description are in English (YAML is always English).
NEW_CONTROLS = [
    {
        "id": "WAF-SEC-140",
        "pillar": "security",
        "severity": "high",
        "type": ["configuration", "architecture"],
        "category": "network-security",
        "title": "Web Application Firewall and DDoS protection MUST be enabled for public endpoints",
        "description": (
            "All internet-facing applications and APIs MUST be protected by a Web Application Firewall (WAF) with managed rule sets. "
            "Distributed Denial-of-Service (DDoS) protection MUST be enabled at the network and application layers. "
            "WAF rules MUST block common attack patterns (OWASP Top 10) and be reviewed quarterly. "
            "Rate limiting MUST be configured to mitigate abuse and volumetric attacks."
        ),
        "threat": [
            "Unprotected public endpoints are directly exposed to SQL injection, XSS, and other OWASP Top 10 attacks.",
            "Missing DDoS protection allows trivial disruption of services by saturating network or application capacity.",
        ],
        "frameworks": [
            ("ISO 27001:2022", ["A.8.9 – Configuration management", "A.8.16 – Monitoring activities", "A.8.23 – Web filtering"]),
            ("ISO 27017", ["CLD.6.2 – Network security"]),
            ("CIS Controls v8", ["CIS 13 – Network Monitoring and Defense"]),
            ("PCI DSS v4.0", ["Req 1 – Install and maintain network security controls", "Req 6.4 – Prevent common vulnerabilities"]),
            ("SOC 2 Type II", ["CC6.6 – Security infrastructure and software", "CC7.2 – System monitoring"]),
            ("GDPR", ["Art. 32 – Security of processing"]),
            ("NIS2", ["Art. 21(2)(d) – Network and information security"]),
            ("DORA", ["Art. 9 – Protection and prevention"]),
            ("EUCS (ENISA)", ["NS-03 – Network security"]),
            ("BSI C5:2020", ["INF-03 – Network security", "INF-04 – Communication security"]),
            ("NIST SP 800-53", ["SC-7 – Boundary Protection", "SI-4 – Information System Monitoring"]),
            ("NIST CSF 2.0", ["PR.DS-01 – Data security"]),
            ("FedRAMP", ["SC-7, SI-4 (Moderate baseline)"]),
            ("CMMC 2.0", ["SC.L2-3.13.1 – Boundary protection"]),
            ("ASD Essential 8", ["E8.1 – Application control", "E8.6 – Network segmentation"]),
        ],
    },
    {
        "id": "WAF-SEC-150",
        "pillar": "security",
        "severity": "high",
        "type": ["governance", "configuration"],
        "category": "container-security",
        "title": "Vulnerability and patch management MUST cover compute instances, operating systems, and endpoints",
        "description": (
            "All virtual machines, bare-metal servers, and container hosts MUST receive automated security patches within defined SLAs. "
            "Critical vulnerabilities MUST be remediated within 7 days and high vulnerabilities within 30 days. "
            "Endpoint Detection and Response (EDR) MUST be deployed on all production instances. "
            "Patch compliance and scan results MUST be centrally reported and reviewed."
        ),
        "threat": [
            "Unpatched operating systems and endpoints are primary entry points for malware and lateral movement.",
            "Missing EDR delays detection of compromised instances and impedes incident response.",
        ],
        "frameworks": [
            ("ISO 27001:2022", ["A.8.7 – Protection against malware", "A.8.8 – Management of technical vulnerabilities"]),
            ("CIS Controls v8", ["CIS 7 – Continuous Vulnerability Management"]),
            ("PCI DSS v4.0", ["Req 6 – Develop and maintain secure systems and software"]),
            ("SOC 2 Type II", ["CC7.1 – Vulnerability detection"]),
            ("GDPR", ["Art. 32 – Security of processing"]),
            ("NIS2", ["Art. 21(2)(g) – Vulnerability handling and disclosure"]),
            ("DORA", ["Art. 9 – Protection and prevention"]),
            ("BSI C5:2020", ["INF-07 – Vulnerability management"]),
            ("NIST SP 800-53", ["RA-5 – Vulnerability Scanning", "SI-2 – Flaw Remediation"]),
            ("NIST CSF 2.0", ["RS.MA-01 – Vulnerability management"]),
            ("ASD Essential 8", ["E8.2 – Patch applications", "E8.5 – Restrict administrative privileges"]),
        ],
    },
    {
        "id": "WAF-SEC-160",
        "pillar": "security",
        "severity": "high",
        "type": ["governance", "configuration"],
        "category": "logging-monitoring",
        "title": "Security-relevant logs MUST be centrally collected and protected against tampering",
        "description": (
            "All authentication, authorization, data access, and administrative activity logs MUST be forwarded to a central SIEM or log platform. "
            "Log integrity MUST be ensured by write-once storage, cryptographic hashing, or immutable retention. "
            "Forwarding MUST be configured so that logs cannot be disabled or altered at the source without triggering an alert. "
            "Retention periods MUST meet compliance and forensic requirements."
        ),
        "threat": [
            "Locally stored logs can be deleted or modified by attackers to hide evidence of compromise.",
            "Missing centralized log correlation prevents timely detection of multi-stage attacks.",
        ],
        "frameworks": [
            ("ISO 27001:2022", ["A.8.15 – Logging", "A.8.16 – Monitoring activities"]),
            ("CIS Controls v8", ["CIS 8 – Audit Log Management"]),
            ("PCI DSS v4.0", ["Req 10 – Log and monitor access to network resources and cardholder data"]),
            ("SOC 2 Type II", ["CC7.2 – System monitoring", "CC4.1 – Monitoring activities"]),
            ("GDPR", ["Art. 32 – Security of processing", "Art. 33 – Personal data breach notification"]),
            ("NIS2", ["Art. 21(2)(f) – Incident handling"]),
            ("DORA", ["Art. 12 – ICT-related incident reporting"]),
            ("EUCS (ENISA)", ["MON-01 – Logging and monitoring"]),
            ("BSI C5:2020", ["OPS-05 – Logging and monitoring"]),
            ("NIST SP 800-53", ["AU-6 – Audit Review", "AU-9 – Protection of Audit Information"]),
            ("NIST CSF 2.0", ["DE.CM-01 – Networks and physical activities are monitored"]),
        ],
    },
    {
        "id": "WAF-COST-110",
        "pillar": "cost",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "data-governance",
        "title": "Spot and preemptible instances MUST be explicitly allowed and documented where workload characteristics permit",
        "description": (
            "Workloads that tolerate interruption MUST use Spot/Preemptible instances by default unless business justification documents on-demand use. "
            "IaC definitions MUST tag interruptible workloads with spot-eligibility and maximum Spot price or eviction policy. "
            "Auto Scaling Groups and Managed Instance Groups SHOULD define mixed instance policies combining Spot and On-Demand capacity. "
            "Documentation MUST cover workload interruption handling and fallback behavior."
        ),
        "threat": [
            "Always using on-demand compute for interruptible workloads increases cost without reliability benefit.",
            "Undocumented Spot usage leads to inconsistent financial planning and surprise evictions.",
        ],
        "frameworks": [
            ("FinOps Foundation", ["Optimize Phase – Workload Optimization", "Variable Workload Spot/Preemptible Strategy"]),
            ("ISO 14001", ["6.1.2 – Environmental aspects of operational decisions"]),
            ("GHG Protocol", ["Scope 3 – Category 11: purchased services cost-efficiency"]),
        ],
    },
    {
        "id": "WAF-COST-120",
        "pillar": "cost",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "cost-governance",
        "title": "Reserved capacity and savings plans MUST be reviewed and documented for steady-state workloads",
        "description": (
            "Workloads with predictable baseline utilization MUST be evaluated for Reserved Instances, Reserved VM Instances, Committed Use Discounts, or Savings Plans. "
            "The reservation decision and coverage ratio MUST be documented in IaC or a FinOps register. "
            "Unused reservations MUST be reviewed quarterly and reallocated or sold where supported. "
            "Expiration dates MUST be tracked to avoid lapse into on-demand pricing."
        ),
        "threat": [
            "Persistent on-demand usage for predictable workloads wastes up to 60-70% of compute budget.",
            "Unmonitored reservation expiration silently reverts workloads to expensive on-demand rates.",
        ],
        "frameworks": [
            ("FinOps Foundation", ["Optimize Phase – Rate Optimization", "Commitment-Based Discounts"]),
            ("ITIL 4", ["Financial Management – Budgeting and cost optimization"]),
        ],
    },
    {
        "id": "WAF-PERF-110",
        "pillar": "efficiancy",
        "severity": "medium",
        "type": ["configuration", "architecture"],
        "category": "network-security",
        "title": "Caching strategies MUST be defined for workloads with repeated read patterns or latency-sensitive endpoints",
        "description": (
            "Workloads serving repeated content MUST use edge caches (CDN), application caches, or in-memory stores. "
            "Cache invalidation and TTL policies MUST be documented and aligned with data freshness requirements. "
            "Latency-sensitive APIs MUST define cache-control headers or use managed cache layers. "
            "Cache hit ratios and latency percentiles MUST be monitored."
        ),
        "threat": [
            "Uncached repeated requests overload backends and increase latency without business value.",
            "Missing cache invalidation strategies can serve stale or incorrect data to users.",
        ],
        "frameworks": [
            ("AWS Well-Architected Framework", ["PERF 04 – Optimize data patterns and usage"]),
            ("Azure Well-Architected Framework", ["Performance Efficiency – Caching"]),
            ("Google Cloud Architecture Framework", ["Performance Optimization – Caching and content delivery"]),
            ("SRE Book (Google)", ["Chapter 20 – Addressing Cascading Failures (caching)"]),
        ],
    },
    {
        "id": "WAF-PERF-120",
        "pillar": "efficiancy",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "logging-monitoring",
        "title": "Database workloads MUST undergo regular index and query performance reviews",
        "description": (
            "All production databases MUST enable query performance insights, slow-query logging, or execution plan analysis. "
            "Slow queries exceeding defined latency thresholds MUST be reviewed monthly and optimized. "
            "Indexes MUST be justified by query patterns and revisited as access patterns evolve. "
            "Query review results MUST be documented in a performance register."
        ),
        "threat": [
            "Unreviewed slow queries accumulate until they become critical latency or availability incidents.",
            "Missing indexes force full table scans, increasing cost and degrading user experience.",
        ],
        "frameworks": [
            ("AWS Well-Architected Framework", ["PERF 04 – Optimize data patterns"]),
            ("Azure Well-Architected Framework", ["Performance Efficiency – Data storage"]),
            ("SRE Book (Google)", ["Chapter 18 – Software Engineering in SRE"]),
        ],
    },
    {
        "id": "WAF-REL-110",
        "pillar": "reliability",
        "severity": "high",
        "type": ["configuration", "architecture"],
        "category": "reliability-design",
        "title": "Circuit breaker, backpressure, and rate limiting MUST be defined for downstream dependencies",
        "description": (
            "Every downstream HTTP/gRPC dependency MUST have explicit timeout, retry, circuit breaker, and bulkhead configuration. "
            "Services MUST propagate backpressure instead of accepting unbounded load. "
            "Rate limits MUST protect backends from accidental or malicious overload. "
            "Configuration MUST be observable through metrics and tested via chaos or fault injection."
        ),
        "threat": [
            "Cascading failures spread when a single slow dependency saturates all callers.",
            "Unbounded retries during outages amplify load and prevent recovery of failing services.",
        ],
        "frameworks": [
            ("ISO 27001:2022", ["A.17.1 – Information security continuity"]),
            ("SRE Book (Google)", ["Chapter 22 – Addressing Cascading Failures"]),
            ("ITIL 4", ["Service Continuity Management"]),
            ("NIST CSF 2.0", ["RS.RP-01 – Response plan is executed"]),
        ],
    },
    {
        "id": "WAF-REL-120",
        "pillar": "reliability",
        "severity": "high",
        "type": ["governance", "architecture"],
        "category": "reliability-design",
        "title": "Graceful degradation and fallback strategies MUST be documented and tested",
        "description": (
            "Critical user journeys MUST continue in a degraded mode when non-essential dependencies fail. "
            "Fallback behavior, default responses, and feature degradation order MUST be documented. "
            "Degradation paths MUST be tested in staging and during chaos experiments. "
            "Non-critical features MUST be tiered so lower-priority functions can be disabled first."
        ),
        "threat": [
            "Hard dependencies on non-essential services turn partial failures into total outages.",
            "Untested fallback paths often fail when first invoked during a real incident.",
        ],
        "frameworks": [
            ("SRE Book (Google)", ["Chapter 22 – Addressing Cascading Failures"]),
            ("AWS Well-Architected Framework", ["REL 9 – Mitigate deployment risks"]),
            ("Azure Well-Architected Framework", ["Reliability – Failure mode analysis"]),
            ("NIST CSF 2.0", ["RS.RP-01 – Response plan is executed"]),
        ],
    },
    {
        "id": "WAF-REL-130",
        "pillar": "reliability",
        "severity": "high",
        "type": ["governance", "process"],
        "category": "backup-recovery",
        "title": "Disaster recovery plans MUST be tested at least annually and updated based on test results",
        "description": (
            "Every critical workload MUST have a documented disaster recovery plan with defined RTO and RPO. "
            "DR plans MUST be exercised at least annually through tabletop, failover, or full recovery tests. "
            "Test results and corrective actions MUST be documented and tracked to completion. "
            "DR runbooks MUST be reviewed after each test and after significant architecture changes."
        ),
        "threat": [
            "Untested DR plans often miss critical gaps in network, identity, or data dependencies.",
            "Outdated DR procedures extend recovery time and increase data loss during real disasters.",
        ],
        "frameworks": [
            ("ISO 27001:2022", ["A.8.13 – Information backup", "A.8.14 – Redundancy of information processing facilities"]),
            ("BSI C5:2020", ["OPS-06 – Operational continuity / Exit management"]),
            ("DORA", ["Art. 12 – ICT-related incident management"]),
            ("GDPR", ["Art. 32 – Security of processing"]),
            ("SOC 2 Type II", ["A1.2 – Failover and recovery"]),
            ("NIST SP 800-53", ["CP-4 – Contingency Plan Testing"]),
        ],
    },
    {
        "id": "WAF-OPS-110",
        "pillar": "excellence",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "deployment-automation",
        "title": "GitOps-based deployments SHOULD be preferred for Kubernetes and container workloads",
        "description": (
            "Kubernetes and container workloads SHOULD be deployed via GitOps controllers that reconcile desired state from Git. "
            "GitOps repositories MUST enforce peer review, branch protection, and signed commits. "
            "Controllers MUST report sync status, drift, and errors to observability systems. "
            "Manual imperative changes to clusters MUST be reconciled or rejected."
        ),
        "threat": [
            "Imperative cluster changes bypass audit trails and create drift between environments.",
            "Missing GitOps reconciliation leaves clusters in undocumented, non-reproducible states.",
        ],
        "frameworks": [
            ("AWS Well-Architected Framework", ["OPS 5 – Operate as a unified whole"]),
            ("SRE Book (Google)", ["Chapter 7 – The Evolution of Automation at Google"]),
            ("NIST CSF 2.0", ["PR.IP-01 – Baseline configurations"]),
        ],
    },
    {
        "id": "WAF-OPS-120",
        "pillar": "excellence",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "deployment-automation",
        "title": "Feature flags MUST be available and documented for high-risk changes",
        "description": (
            "Risky or customer-visible feature rollouts MUST use feature flags with defined targeting and kill-switch capability. "
            "Feature flag configurations MUST be version-controlled and auditable. "
            "Flag lifecycle MUST be managed so temporary flags are removed after rollout completes. "
            "Critical paths MUST support immediate disablement without requiring a full deployment."
        ),
        "threat": [
            "Releases without feature flags force rollbacks for every production issue, increasing MTTR.",
            "Orphaned feature flags create technical debt and unpredictable code paths.",
        ],
        "frameworks": [
            ("SRE Book (Google)", ["Chapter 16 – Debugging"]),
            ("AWS Well-Architected Framework", ["OPS 8 – Improve processes"]),
            ("Azure Well-Architected Framework", ["Operational Excellence – Safe deployment practices"]),
        ],
    },
    {
        "id": "WAF-SUS-110",
        "pillar": "sustainability",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "data-governance",
        "title": "Regional carbon intensity MUST be considered and documented in location decisions",
        "description": (
            "New workloads and data stores MUST document carbon intensity alongside latency, cost, and compliance factors when selecting regions. "
            "Region selection decisions MUST be captured in an Architecture Decision Record or equivalent register. "
            "Batch and non-latency-sensitive workloads SHOULD prefer lower-carbon regions where data residency allows. "
            "Carbon intensity assumptions MUST be revisited annually using current provider data."
        ),
        "threat": [
            "Ignoring grid carbon intensity when selecting regions increases emissions without business justification.",
            "Undocumented region decisions prevent sustainability audits and optimization over time.",
        ],
        "frameworks": [
            ("EU CSRD (Corporate Sustainability Reporting Directive)", ["ESRS E1 – Climate Change"]),
            ("GHG Protocol", ["Scope 3 – Category 11: purchased cloud services location factor"]),
            ("Green Software Foundation", ["Carbon Aware Computing – location-based optimization"]),
            ("ISO 14001", ["6.1.2 – Environmental aspects"]),
        ],
    },
    {
        "id": "WAF-SUS-120",
        "pillar": "sustainability",
        "severity": "low",
        "type": ["governance", "configuration"],
        "category": "sustainability-efficiency",
        "title": "Batch and HPC workloads SHOULD run off-peak where SLA constraints allow",
        "description": (
            "Batch, report generation, HPC, and data processing workloads SHOULD be scheduled during off-peak or high-renewable-energy hours. "
            "Scheduler configurations MUST document SLA constraints and acceptable time windows. "
            "Preemptible/Spot capacity SHOULD be combined with off-peak scheduling where feasible. "
            "Energy and cost savings of time-shifting MUST be tracked and reported."
        ),
        "threat": [
            "Running batch workloads during peak hours wastes energy from high-carbon grid mix and increases cost.",
            "Missing scheduling constraints can violate SLA or delay critical business processes.",
        ],
        "frameworks": [
            ("EU CSRD (Corporate Sustainability Reporting Directive)", ["ESRS E1 – Climate Change"]),
            ("GHG Protocol", ["Scope 2 – Market-based method"]),
            ("Green Software Foundation", ["Carbon Aware Computing – temporal shifting"]),
            ("ISO 14001", ["6.1.2 – Environmental aspects"]),
        ],
    },
    {
        "id": "WAF-SOV-110",
        "pillar": "sovereign",
        "severity": "critical",
        "type": ["governance", "configuration"],
        "category": "encryption-key-management",
        "title": "Cryptographic keys for sensitive data MUST be managed in HSM or sovereign key management services",
        "description": (
            "Keys for sensitive and classified data MUST be generated and stored in Hardware Security Modules (HSM) or sovereign managed key services. "
            "Key operations MUST enforce role separation, dual control, and audit logging. "
            "Key import, export, and backup MUST follow documented and approved procedures. "
            "Cloud provider managed keys alone MUST NOT be used for sovereign data classes."
        ),
        "threat": [
            "Provider-managed keys may be accessible to cloud operators or subject to foreign jurisdiction.",
            "Missing HSM backing weakens key protection and complicates compliance with sovereignty requirements.",
        ],
        "frameworks": [
            ("GDPR", ["Art. 32 – Security of processing"]),
            ("BSI C5:2020", ["CRY-01 – Cryptography policy", "CRY-02 – Key management"]),
            ("BSI C3A:2026", ["Dimension 4 – Data: HSM-backed key management"]),
            ("EUCS (ENISA)", ["CRY-03 – Key management", "SOV-03 – Customer key control"]),
            ("ISO 27001:2022", ["A.8.24 – Use of cryptography"]),
            ("GAIA-X", ["Sovereign Cloud – Cryptographic self-determination"]),
        ],
    },
    {
        "id": "WAF-SOV-120",
        "pillar": "sovereign",
        "severity": "high",
        "type": ["governance"],
        "category": "data-governance",
        "title": "Data processing agreements MUST be documented for every sub-processor",
        "description": (
            "A current data processing agreement (DPA) or order processing agreement (AVV) MUST exist for each sub-processor handling personal or regulated data. "
            "Sub-processor lists MUST be maintained and reviewed at least annually. "
            "DPA terms MUST cover data location, security measures, breach notification, deletion, and audit rights. "
            "Changes to sub-processors MUST follow a documented approval workflow."
        ),
        "threat": [
            "Missing DPAs violate GDPR Article 28 and similar processor accountability requirements.",
            "Undocumented sub-processors increase supply-chain risk and prevent effective exit management.",
        ],
        "frameworks": [
            ("GDPR", ["Art. 28 – Processor", "Art. 46 – Transfers with appropriate safeguards"]),
            ("BSI C5:2020", ["OPS-02 – Supplier relationships"]),
            ("BSI C3A:2026", ["Dimension 5 – Governance: Processor agreements"]),
            ("DORA", ["Art. 28 – Subcontracting of ICT services"]),
            ("ISO 27001:2022", ["A.5.19 – Information security in supplier relationships"]),
            ("TISAX", ["Information security – Supplier management"]),
        ],
    },
    {
        "id": "WAF-AGN-110",
        "pillar": "agentic",
        "severity": "high",
        "type": ["governance", "configuration"],
        "category": "agentic-governance",
        "title": "Agent outputs and actions MUST be validated, sandboxed, and restricted to allowlists",
        "description": (
            "Agent-generated outputs MUST be validated against schemas, business rules, or human-defined constraints before downstream use. "
            "Agent tool invocations MUST be sandboxed and restricted to an explicit allowlist of functions and parameters. "
            "High-impact actions MUST require confirmation or human-in-the-loop approval. "
            "Validation failures MUST be logged, alerted, and used to refine guardrails."
        ),
        "threat": [
            "Unvalidated agent outputs can trigger incorrect business decisions or data corruption.",
            "Unsandboxed tool access allows prompt injection and unauthorized actions by compromised agents.",
        ],
        "frameworks": [
            ("ISO 27001:2022", ["A.8.3 – Information access restriction", "A.8.27 – Secure system architecture"]),
            ("GDPR", ["Art. 32 – Security of processing"]),
            ("NIST AI Risk Management Framework", ["Measure 1.1 – AI system is validated"]),
            ("EU AI Act", ["Art. 9 – Risk management system"]),
            ("PCI DSS v4.0", ["Req 6.2 – Software security patches"]),
            ("SOC 2 Type II", ["CC6.1 – Logical access controls"]),
        ],
    },
]


def get_category_risk(category):
    """Return a German rationale risk sentence by category."""
    return {
        "network-security": "Unzureichender Netzwerkschutz und fehlende DDoS-Abwehr ermöglichen externe Angriffe, Serviceunterbrechungen und Datendiebstahl.",
        "container-security": "Ungepatchte Systeme und fehlende Endpunkterkennung erweitern die Angriffsfläche und verlängern die Zeit bis zur Incident-Erkennung.",
        "logging-monitoring": "Lokale oder manipulierbare Logs verhindern forensische Analysen und erschweren regulatorische Nachweise erheblich.",
        "data-governance": "Fehlende Datenklassifizierung, Dokumentation oder Standortsteuerung erhöhen Compliance-Risiken, Kosten und Betriebsrisiken.",
        "cost-governance": "Fehlende Commitment-Planung und Dokumentation führen zu Budgetüberschreitungen und verschwendeten Cloud-Ausgaben.",
        "reliability-design": "Fehlende Resilience-Patterns und nicht getestete Degradationsstrategien führen zu kaskadierenden Ausfällen und längerer Wiederherstellungszeit.",
        "backup-recovery": "Ungetestete Disaster-Recovery-Pläne verlängern Ausfallzeiten und erhöhen das Risiko irreversibler Datenverluste.",
        "deployment-automation": "Fehlende GitOps-Praktiken und unverwaltete Feature Flags erhöhen das Risiko menschlicher Fehler und nicht reproduzierbarer Deployments.",
        "sustainability-efficiency": "Ineffiziente Planung von Batch-Workloads verschwendet Energie und erhöht den CO₂-Fußabdruck ohne Mehrwert.",
        "encryption-key-management": "Schlüssel ohne HSM- oder Sovereign-KMS-Unterstützung unterliegen möglicherweise fremden Jurisdiktionen und schwächen den Schutz sensibler Daten.",
        "agentic-governance": "Unvalidierte Agenten-Ausgaben und unsandboxete Tool-Aufrufe ermöglichen Manipulation, Datenkorruption und unautorisierte Aktionen.",
    }.get(category, "Fehlende Umsetzung dieser Kontrolle erhöht das Risiko von Sicherheitsvorfällen, Compliance-Verstößen und Betriebsunterbrechungen.")


def build_rationale(control):
    risk = get_category_risk(control["category"])
    return f"{risk} Dieses Control adressiert die Anforderungen des Bereichs '{control['category'].replace('-', ' ').title()}' und stellt sicher, dass {control['description'][:120]}..."


def build_yaml(control):
    return {
        "id": control["id"],
        "title": control["title"],
        "status": "active",
        "tags": sorted(set([control["pillar"]] + control["type"] + [control["severity"]])),
        "pillar": control["pillar"],
        "severity": control["severity"],
        "type": control["type"],
        "category": control["category"],
        "rationale": build_rationale(control),
        "threat": control["threat"],
        "implementation_guidance": [
            "Document the requirement in a version-controlled policy, ADR, or standard.",
            "Assign ownership and establish a review cadence (e.g., quarterly).",
            "Implement the required configuration as code in Terraform or equivalent IaC.",
        ],
        "maturity_levels": {
            "level_1": {
                "description": "Ad hoc – control not consistently applied",
                "criteria": ["Die Anforderung ist nicht einheitlich umgesetzt; Nachweis existiert nur punktuell oder fehlt."],
            },
            "level_2": {
                "description": "Standardised – policy defined and communicated",
                "criteria": ["Eine dokumentierte Policy oder ein Standard beschreibt die Anforderung."],
            },
            "level_3": {
                "description": "Integrated – automated validation in CI/CD",
                "criteria": ["Terraform-Checks oder IaC-Gates prüfen die Anforderung automatisch in CI/CD."],
            },
            "level_4": {
                "description": "Auditable – metrics and exceptions tracked",
                "criteria": ["Abdeckung, Ausnahmen und Qualitätsmetriken werden quartalsweise berichtet."],
            },
            "level_5": {
                "description": "Optimised – continuous improvement based on data",
                "criteria": ["Die Effektivität wird kontinuierlich gemessen und automatisch optimiert."],
            },
        },
        "evidence": {
            "required": [
                {"kind": "iac", "description": "Terraform configuration implementing the control."},
                {"kind": "governance", "description": "Policy, ADR, or standard documenting the requirement."},
            ],
            "optional": [
                {"kind": "config", "description": "Cloud console or API output confirming runtime state."},
            ],
        },
        "references": {
            "narrative": f"modules/pillar-{prefix_to_module(control['id'])}/pages/controls/{control['id']}.adoc",
            "related_controls": [],
        },
        "description": control["description"],
        "regulatory_mapping": [
            {"framework": fw, "controls": ctrls} for fw, ctrls in control["frameworks"]
        ],
        "checks": build_checks(control),
    }


def prefix_to_module(cid):
    mapping = {
        "SEC": "security",
        "COST": "cost",
        "PERF": "efficiancy",
        "REL": "reliability",
        "OPS": "excellence",
        "SUS": "sustainability",
        "SOV": "sovereign",
        "AGN": "agentic",
    }
    return mapping[cid.split("-")[1]]


def build_checks(control):
    """Build a minimal set of provider-aware checks. For new controls we use a mix of
    terraform and config engines with tags/labels where full resource attributes are
    not available across all providers."""
    base = control["id"].lower()
    pillar = control["pillar"]
    category = control["category"]
    checks = []

    # Each control gets at least one config check plus provider-specific terraform checks
    tag_key = control["id"].lower().replace("-", "_")

    if category == "network-security" and "WAF" in control["title"]:
        checks.extend([
            {
                "id": f"{base}.tf.aws.waf-associated",
                "engine": "terraform",
                "automated": True,
                "title": "AWS ALB/CloudFront distributions must have an associated WAFv2 WebACL",
                "provider": "aws",
                "description": "Public-facing AWS ALBs, CloudFront distributions, and API Gateways must reference an aws_wafv2_web_acl_association or origin with an active WAFv2 WebACL.",
                "expected": "true",
                "remediation": "Create an aws_wafv2_web_acl resource with managed rule sets and associate it with public-facing resources via aws_wafv2_web_acl_association.",
                "example": {
                    "compliant": 'resource "aws_wafv2_web_acl_association" "public_alb" {\n  resource_arn = aws_lb.public.arn\n  web_acl_arn  = aws_wafv2_web_acl.main.arn\n}\n',
                    "non_compliant": 'resource "aws_lb" "public" {\n  # Missing WAFv2 WebACL association\n}\n',
                },
                "scope": {"block_type": "resource", "resource_types": ["aws_wafv2_web_acl_association", "aws_cloudfront_distribution"]},
                "assertions": [{"attribute": "web_acl_arn", "op": "attribute_exists", "message": "Public resource must be associated with a WAFv2 WebACL."}],
                "on_fail": "violation",
            },
            {
                "id": f"{base}.tf.aws.shield-advanced",
                "engine": "terraform",
                "automated": True,
                "title": "AWS Shield Advanced should be enabled for critical public endpoints",
                "provider": "aws",
                "description": "Critical public endpoints should subscribe to AWS Shield Advanced for enhanced DDoS protection and cost protection.",
                "expected": "true",
                "remediation": "Enable AWS Shield Advanced on protected resources or at the account/organization level, and configure DDoS response team access.",
                "example": {
                    "compliant": 'resource "aws_shield_protection" "public_alb" {\n  name         = "public-alb-protection"\n  resource_arn = aws_lb.public.arn\n}\n',
                    "non_compliant": 'resource "aws_lb" "public" {\n  # No Shield Advanced protection configured\n}\n',
                },
                "scope": {"block_type": "resource", "resource_types": ["aws_shield_protection", "aws_shield_subscription"]},
                "assertions": [{"attribute": "resource_arn", "op": "attribute_exists", "message": "Shield Advanced protection must reference a public resource."}],
                "on_fail": "finding",
            },
            {
                "id": f"{base}.tf.azurerm.front-door-waf",
                "engine": "terraform",
                "automated": True,
                "title": "Azure Front Door/CDN must use WAF policy with managed rules",
                "provider": "azurerm",
                "description": "Azure Front Door and CDN endpoints must reference an azurerm_frontdoor_firewall_policy or azurerm_cdn_endpoint_security_policy with managed rule sets enabled.",
                "expected": "true",
                "remediation": "Create an azurerm_frontdoor_firewall_policy with managed_rules and associate it with the Front Door/CDN endpoint.",
                "example": {
                    "compliant": 'resource "azurerm_cdn_endpoint" "api" {\n  # ...\n}\n\nresource "azurerm_cdn_endpoint_security_policy" "waf" {\n  cdn_endpoint_id = azurerm_cdn_endpoint.api.id\n}\n',
                    "non_compliant": 'resource "azurerm_cdn_endpoint" "api" {\n  # Missing WAF security policy\n}\n',
                },
                "scope": {"block_type": "resource", "resource_types": ["azurerm_cdn_endpoint_security_policy", "azurerm_frontdoor_firewall_policy"]},
                "assertions": [{"attribute": "managed_rule", "op": "attribute_exists", "message": "WAF policy must include managed rule sets."}],
                "on_fail": "violation",
            },
            {
                "id": f"{base}.tf.google.cloud-armor",
                "engine": "terraform",
                "automated": True,
                "title": "GCP backend services must be protected by Cloud Armor security policy",
                "provider": "google",
                "description": "GCP backend services exposed to the internet must reference a google_compute_security_policy (Cloud Armor) with at least one rule.",
                "expected": "true",
                "remediation": "Create a google_compute_security_policy with OWASP rules or adaptive protection and attach it to the backend service via security_policy.",
                "example": {
                    "compliant": 'resource "google_compute_backend_service" "api" {\n  name            = "api-backend"\n  security_policy = google_compute_security_policy.waf.self_link\n}\n',
                    "non_compliant": 'resource "google_compute_backend_service" "api" {\n  name = "api-backend"\n  # Missing Cloud Armor security_policy\n}\n',
                },
                "scope": {"block_type": "resource", "resource_types": ["google_compute_backend_service", "google_compute_backend_bucket"]},
                "assertions": [{"attribute": "security_policy", "op": "attribute_exists", "message": "Backend service must reference a Cloud Armor security policy."}],
                "on_fail": "violation",
            },
            {
                "id": f"{base}.config.stackit-waf-documented",
                "engine": "config",
                "automated": False,
                "title": "STACKIT public endpoints must have WAF/DDoS configuration documented",
                "provider": "stackit",
                "description": "Because STACKIT does not expose WAF in Terraform, a configuration document or ADR must describe how public endpoints are protected.",
                "expected": "true",
                "remediation": "Create docs/security/waf-stackit.md describing the WAF/DDoS solution and add a reference in the repository README or control evidence.",
                "example": {"compliant": "# WAF/DDoS documented in docs/security/waf-stackit.md", "non_compliant": "# No WAF/DDoS documentation for STACKIT public endpoints"},
                "scope": {"block_type": "file", "path_pattern": "docs/security/waf-stackit.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "STACKIT WAF/DDoS documentation must exist."}],
                "on_fail": "finding",
            },
        ])
    elif category == "container-security" and "patch" in control["title"].lower():
        checks.extend([
            {
                "id": f"{base}.config.os-patch-policy",
                "engine": "config",
                "automated": False,
                "title": "OS patch policy and EDR coverage must be documented",
                "provider": "any",
                "description": "A repository file must document the patch SLA, automated patching mechanism, and EDR coverage for production compute instances.",
                "expected": "true",
                "remediation": "Create docs/security/patch-management.md with SLA table, tooling, and EDR coverage.",
                "example": {"compliant": "# Patch management policy exists and covers all OS types", "non_compliant": "# No patch management policy documented"},
                "scope": {"block_type": "file", "path_pattern": "docs/security/patch-management.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "Patch management policy must exist."}],
                "on_fail": "finding",
            },
            {
                "id": f"{base}.tf.aws.ssm-patch-manager",
                "engine": "terraform",
                "automated": True,
                "title": "AWS SSM Patch Manager must be configured for managed instances",
                "provider": "aws",
                "description": "AWS Systems Manager Patch Manager associations and patch baselines must exist for production instances.",
                "expected": "true",
                "remediation": "Create aws_ssm_patch_baseline and aws_ssm_association resources to schedule patching.",
                "example": {
                    "compliant": 'resource "aws_ssm_patch_baseline" "critical" {\n  name             = "critical-patch-baseline"\n  operating_system = "AMAZON_LINUX_2"\n}\n',
                    "non_compliant": 'resource "aws_instance" "app" {\n  # No SSM Patch Manager association\n}\n',
                },
                "scope": {"block_type": "resource", "resource_types": ["aws_ssm_patch_baseline", "aws_ssm_association"]},
                "assertions": [{"attribute": "name", "op": "attribute_exists", "message": "Patch baseline must be defined."}],
                "on_fail": "finding",
            },
        ])
    elif category == "logging-monitoring" and "log" in control["title"].lower():
        checks.extend([
            {
                "id": f"{base}.tf.aws.cloudwatch-logs-retention",
                "engine": "terraform",
                "automated": True,
                "title": "Security-relevant CloudWatch log groups must have explicit retention",
                "provider": "aws",
                "description": "CloudWatch log groups for security, audit, and authentication logs must define retention_in_days aligned with compliance requirements.",
                "expected": "true",
                "remediation": "Set retention_in_days >= 365 on aws_cloudwatch_log_group resources used for security logs.",
                "example": {
                    "compliant": 'resource "aws_cloudwatch_log_group" "auth" {\n  name              = "/aws/auth"\n  retention_in_days = 365\n}\n',
                    "non_compliant": 'resource "aws_cloudwatch_log_group" "auth" {\n  name = "/aws/auth"\n  # Missing retention_in_days\n}\n',
                },
                "scope": {"block_type": "resource", "resource_types": ["aws_cloudwatch_log_group"]},
                "assertions": [{"attribute": "retention_in_days", "op": "greater_than_or_equal", "expected": 365, "message": "Security log group retention must be at least 365 days."}],
                "on_fail": "violation",
            },
            {
                "id": f"{base}.tf.aws.s3-log-integrity",
                "engine": "terraform",
                "automated": True,
                "title": "Central log S3 buckets must have object lock or versioning enabled",
                "provider": "aws",
                "description": "S3 buckets storing central security logs must protect against deletion/modification via versioning or object lock.",
                "expected": "true",
                "remediation": "Enable versioning and object lock with governance/compliance retention on the central log bucket.",
                "example": {
                    "compliant": 'resource "aws_s3_bucket_versioning" "logs" {\n  bucket = aws_s3_bucket.logs.id\n  versioning_configuration { status = "Enabled" }\n}\n',
                    "non_compliant": 'resource "aws_s3_bucket" "logs" {\n  # No versioning or object lock\n}\n',
                },
                "scope": {"block_type": "resource", "resource_types": ["aws_s3_bucket", "aws_s3_bucket_versioning", "aws_s3_bucket_object_lock_configuration"]},
                "assertions": [{"attribute": "versioning.status", "op": "equals", "expected": "Enabled", "message": "Central log bucket must have versioning enabled."}],
                "on_fail": "finding",
            },
        ])
    else:
        # Generic tag/label checks for governance/configuration controls
        for provider, rt_map in [
            ("aws", ["aws_instance", "aws_autoscaling_group", "aws_db_instance"]),
            ("azurerm", ["azurerm_linux_virtual_machine", "azurerm_virtual_machine_scale_set"]),
            ("google", ["google_compute_instance", "google_container_node_pool"]),
            ("stackit", ["stackit_project", "stackit_server"]),
            ("ovh", ["ovh_cloud_project", "ovh_cloud_project_instance"]),
            ("hcloud", ["hcloud_server"]),
        ]:
            checks.append({
                "id": f"{base}.tf.{provider}.{tag_key}-tag",
                "engine": "terraform",
                "automated": True,
                "title": f"{provider.upper()} resources must document the control via '{tag_key}' tag/label",
                "provider": provider,
                "description": f"Resources relevant to this control must carry a '{tag_key}' tag or label to show the control is tracked in IaC.",
                "expected": "true",
                "remediation": f"Add a '{tag_key}' tag/label to the relevant resources with a documented value.",
                "example": {
                    "compliant": f'resource "{rt_map[0]}" "example" {{\n  tags = {{\n    {tag_key} = "true"\n  }}\n}}\n',
                    "non_compliant": f'resource "{rt_map[0]}" "example" {{\n  # Missing {tag_key} tag/label\n}}\n',
                },
                "scope": {"block_type": "resource", "resource_types": rt_map},
                "assertions": [{"attribute": "tags" if provider not in ("google", "hcloud", "stackit") else "labels", "op": "key_exists", "key": tag_key, "message": f"Resource is missing the '{tag_key}' tag/label."}],
                "on_fail": "finding",
            })
        # Config file check as fallback
        checks.append({
            "id": f"{base}.config.policy-document",
            "engine": "config",
            "automated": False,
            "title": f"Policy document for {control['id']} must exist",
            "provider": "any",
            "description": "A version-controlled policy or ADR must document the requirement and review cadence.",
            "expected": "true",
            "remediation": f"Create docs/controls/{control['id'].lower()}.md or add the requirement to an existing ADR.",
            "example": {"compliant": f"# {control['id']} documented in ADR", "non_compliant": f"# {control['id']} not documented"},
            "scope": {"block_type": "file", "path_pattern": f"docs/controls/{control['id'].lower()}.md"},
            "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "Policy document must exist."}],
            "on_fail": "advisory",
        })

    return checks


def write_yaml(repo_root, control):
    path = Path(repo_root) / "modules" / "controls" / "controls" / f"{control['id']}.yml"
    data = build_yaml(control)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=120)


def main():
    for lang, repo_root in REPOS.items():
        for control in NEW_CONTROLS:
            write_yaml(repo_root, control)
        print(f"Generated {len(NEW_CONTROLS)} new YAML controls in {repo_root} ({lang})")


if __name__ == "__main__":
    main()
