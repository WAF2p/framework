#!/usr/bin/env python3
"""Generate the 17 new controls that expand Wombat from 83 to 100 controls.

Creates machine-readable YAML controls in both framework/ and framework-en/,
and matching narrative .adoc pages in German and English. Also updates
per-pillar navigation and inserts rows into modules/controls/pages/catalog.adoc.
"""
import glob
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

SEVERITY_EMOJI = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

# --- control definitions ------------------------------------------------------

NEW_CONTROLS = [
    {
        "id": "WAF-SEC-140",
        "pillar": "security",
        "severity": "high",
        "type": ["configuration", "architecture"],
        "category": "network-security",
        "automatable": "High",
        "title_en": "Web Application Firewall and DDoS protection MUST be enabled for public endpoints",
        "title_de": "Web Application Firewall (WAF) und DDoS-Schutz müssen für öffentliche Endpunkte aktiviert sein",
        "description_en": (
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
        ],
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-SEC-040", "WAF-SEC-050", "WAF-SEC-080", "WAF-SEC-160", "WAF-SEC-010", "WAF-REL-110", "WAF-AGN-110"],
        "checks": [
            {
                "id": "waf-sec-140.tf.aws.waf-associated",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS public ALB/CloudFront distributions must have an associated WAFv2 WebACL",
                "title_de": "Öffentliche AWS ALB/CloudFront-Distributionen müssen mit einer WAFv2 WebACL verbunden sein",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_wafv2_web_acl_association", "aws_cloudfront_distribution"]},
                "assertions": [{"attribute": "web_acl_arn", "op": "attribute_exists", "message": "Public resource must be associated with a WAFv2 WebACL."}],
                "on_fail": "violation",
            },
            {
                "id": "waf-sec-140.tf.azurerm.front-door-waf",
                "engine": "terraform",
                "automated": True,
                "title_en": "Azure Front Door/CDN must use WAF policy with managed rules",
                "title_de": "Azure Front Door/CDN muss eine WAF-Policy mit Managed Rules verwenden",
                "provider": "azurerm",
                "scope": {"block_type": "resource", "resource_types": ["azurerm_cdn_endpoint_security_policy", "azurerm_frontdoor_firewall_policy"]},
                "assertions": [{"attribute": "managed_rule", "op": "attribute_exists", "message": "WAF policy must include managed rule sets."}],
                "on_fail": "violation",
            },
            {
                "id": "waf-sec-140.tf.google.cloud-armor",
                "engine": "terraform",
                "automated": True,
                "title_en": "GCP backend services must be protected by Cloud Armor security policy",
                "title_de": "GCP-Backend-Dienste müssen durch eine Cloud Armor Security Policy geschützt sein",
                "provider": "google",
                "scope": {"block_type": "resource", "resource_types": ["google_compute_backend_service", "google_compute_backend_bucket"]},
                "assertions": [{"attribute": "security_policy", "op": "attribute_exists", "message": "Backend service must reference a Cloud Armor security policy."}],
                "on_fail": "violation",
            },
            {
                "id": "waf-sec-140.config.sovereign-provider-waf-documented",
                "engine": "config",
                "automated": False,
                "title_en": "Sovereign provider public endpoints must have WAF/DDoS configuration documented",
                "title_de": "Öffentliche Endpunkte bei Sovereign-Providern müssen WAF/DDoS-Konfiguration dokumentieren",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/security/waf-ddos.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "WAF/DDoS documentation must exist for sovereign provider public endpoints."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-SEC-150",
        "pillar": "security",
        "severity": "high",
        "type": ["governance", "configuration"],
        "category": "container-security",
        "automatable": "Medium",
        "title_en": "Vulnerability and patch management MUST cover compute instances, operating systems, and endpoints",
        "title_de": "Schwachstellenmanagement außerhalb von Containern (VM-/Betriebssystem-Patches, Endpoint Detection)",
        "description_en": (
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
        ],
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-SEC-070", "WAF-SEC-120", "WAF-SEC-130", "WAF-SEC-010", "WAF-SEC-100", "WAF-OPS-030", "WAF-SOV-120"],
        "checks": [
            {
                "id": "waf-sec-150.config.patch-policy-documented",
                "engine": "config",
                "automated": False,
                "title_en": "OS patch policy and EDR coverage must be documented",
                "title_de": "OS-Patch-Policy und EDR-Abdeckung müssen dokumentiert sein",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/security/patch-management.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "Patch management policy must exist and cover SLA and EDR."}],
                "on_fail": "finding",
            },
            {
                "id": "waf-sec-150.tf.aws.ssm-patch-manager",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS SSM Patch Manager must be configured for managed instances",
                "title_de": "AWS SSM Patch Manager muss für verwaltete Instanzen konfiguriert sein",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_ssm_patch_baseline", "aws_ssm_association"]},
                "assertions": [{"attribute": "name", "op": "attribute_exists", "message": "Patch baseline must be defined."}],
                "on_fail": "finding",
            },
            {
                "id": "waf-sec-150.tf.azurerm.mde-deployed",
                "engine": "terraform",
                "automated": True,
                "title_en": "Azure VMs must have Microsoft Defender for Endpoint extension deployed",
                "title_de": "Azure-VMs müssen die Microsoft Defender for Endpoint-Erweiterung bereitgestellt haben",
                "provider": "azurerm",
                "scope": {"block_type": "resource", "resource_types": ["azurerm_virtual_machine_extension"]},
                "assertions": [{"attribute": "type", "op": "in", "expected": ["MicrosoftMonitoringAgent", "MDE.Windows", "MDE.Linux"], "message": "VM must have Defender for Endpoint or monitoring extension."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-SEC-160",
        "pillar": "security",
        "severity": "high",
        "type": ["governance", "configuration"],
        "category": "logging-monitoring",
        "automatable": "High",
        "title_en": "Security-relevant logs MUST be centrally collected and protected against tampering",
        "title_de": "Sicherheitsrelevante Logs müssen zentralisiert und vor Manipulation geschützt sein",
        "description_en": (
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
        ],
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-SEC-080", "WAF-SEC-090", "WAF-SEC-100", "WAF-OPS-050", "WAF-SUS-110", "WAF-SOV-110"],
        "checks": [
            {
                "id": "waf-sec-160.tf.aws.cloudwatch-logs-retention",
                "engine": "terraform",
                "automated": True,
                "title_en": "Security-relevant CloudWatch log groups must have explicit retention",
                "title_de": "Sicherheitsrelevante CloudWatch-Log-Gruppen müssen eine explizite Aufbewahrung haben",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_cloudwatch_log_group"]},
                "assertions": [{"attribute": "retention_in_days", "op": "greater_than_or_equal", "expected": 365, "message": "Security log group retention must be at least 365 days."}],
                "on_fail": "violation",
            },
            {
                "id": "waf-sec-160.tf.aws.s3-log-integrity",
                "engine": "terraform",
                "automated": True,
                "title_en": "Central log S3 buckets must have versioning or object lock enabled",
                "title_de": "Zentrale Log-S3-Buckets müssen Versioning oder Object Lock aktiviert haben",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_s3_bucket", "aws_s3_bucket_versioning", "aws_s3_bucket_object_lock_configuration"]},
                "assertions": [{"attribute": "versioning.status", "op": "equals", "expected": "Enabled", "message": "Central log bucket must have versioning enabled."}],
                "on_fail": "finding",
            },
            {
                "id": "waf-sec-160.tf.azurerm.log-analytics-sku",
                "engine": "terraform",
                "automated": True,
                "title_en": "Azure Log Analytics workspace for security logs must define retention",
                "title_de": "Azure Log Analytics Workspace für Sicherheitslogs muss Aufbewahrung definieren",
                "provider": "azurerm",
                "scope": {"block_type": "resource", "resource_types": ["azurerm_log_analytics_workspace"]},
                "assertions": [{"attribute": "retention_in_days", "op": "greater_than_or_equal", "expected": 365, "message": "Security log retention must be at least 365 days."}],
                "on_fail": "violation",
            },
        ],
    },
    {
        "id": "WAF-COST-110",
        "pillar": "cost",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "data-governance",
        "automatable": "Medium",
        "title_en": "Spot and preemptible instances MUST be explicitly allowed and documented where workload characteristics permit",
        "title_de": "Spot-/Preemptible-Instances müssen für geeignete Workloads explizit erlaubt und dokumentiert sein",
        "description_en": (
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
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-COST-010", "WAF-COST-030", "WAF-COST-120", "WAF-COST-080", "WAF-OPS-020", "WAF-REL-120"],
        "checks": [
            {
                "id": "waf-cost-110.tf.aws.spot-tagged",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS interruptible workloads must carry spot-eligibility tag",
                "title_de": "AWS-unterbrechungstolerante Workloads müssen ein spot-eligibility-Tag tragen",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_autoscaling_group", "aws_spot_instance_request", "aws_ec2_fleet"]},
                "assertions": [{"attribute": "tags", "op": "key_exists", "key": "spot-eligibility", "message": "Interruptible workload must be tagged with spot-eligibility."}],
                "on_fail": "finding",
            },
            {
                "id": "waf-cost-110.tf.azurerm.spot-eviction-policy",
                "engine": "terraform",
                "automated": True,
                "title_en": "Azure Spot VMs must define eviction policy",
                "title_de": "Azure Spot-VMs müssen eine Eviction-Policy definieren",
                "provider": "azurerm",
                "scope": {"block_type": "resource", "resource_types": ["azurerm_linux_virtual_machine", "azurerm_windows_virtual_machine"]},
                "assertions": [{"attribute": "priority", "op": "in", "expected": ["Spot", "spot"], "message": "Spot VM must have priority Spot with eviction policy."}],
                "on_fail": "advisory",
            },
            {
                "id": "waf-cost-110.config.spot-policy-documented",
                "engine": "config",
                "automated": False,
                "title_en": "Spot instance policy must be documented",
                "title_de": "Spot-Instance-Policy muss dokumentiert sein",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/finops/spot-policy.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "Spot/preemptible policy must document eligible workload classes."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-COST-120",
        "pillar": "cost",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "cost-governance",
        "automatable": "Medium",
        "title_en": "Reserved capacity and savings plans MUST be reviewed and documented for steady-state workloads",
        "title_de": "Reserved Capacity / Savings Plans müssen für dauerhafte Last reviewed und dokumentiert sein",
        "description_en": (
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
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-COST-080", "WAF-COST-020", "WAF-COST-050", "WAF-COST-110", "WAF-OPS-060", "WAF-REL-130"],
        "checks": [
            {
                "id": "waf-cost-120.tf.aws.savings-plan",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS savings plans or reserved capacity must exist for steady-state compute",
                "title_de": "AWS Savings Plans oder Reserved Capacity müssen für gleichbleibende Compute-Last existieren",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_savingsplans_plan", "aws_ec2_host", "aws_ec2_capacity_reservation"]},
                "assertions": [{"attribute": "name", "op": "attribute_exists", "message": "Reservation or savings plan must be defined for steady-state workloads."}],
                "on_fail": "advisory",
            },
            {
                "id": "waf-cost-120.config.reservation-register",
                "engine": "config",
                "automated": False,
                "title_en": "Reservation decisions must be documented in FinOps register",
                "title_de": "Reservierungsentscheidungen müssen im FinOps-Register dokumentiert sein",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/finops/reservation-register.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "Reservation register must document coverage ratio, expiration, and owner."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-PERF-110",
        "pillar": "efficiancy",
        "severity": "medium",
        "type": ["configuration", "architecture"],
        "category": "network-security",
        "automatable": "High",
        "title_en": "Caching strategies MUST be defined for workloads with repeated read patterns or latency-sensitive endpoints",
        "title_de": "Caching-Strategien (CDN, Edge, in-memory) müssen für geeignete Workloads definiert sein",
        "description_en": (
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
        ],
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-PERF-010", "WAF-PERF-020", "WAF-PERF-030", "WAF-REL-110", "WAF-COST-010", "WAF-OPS-040"],
        "checks": [
            {
                "id": "waf-perf-110.tf.aws.cloudfront-cache",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS CloudFront distributions must define default cache behavior",
                "title_de": "AWS CloudFront-Distributionen müssen ein Standard-Cache-Verhalten definieren",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_cloudfront_distribution"]},
                "assertions": [{"attribute": "default_cache_behavior", "op": "attribute_exists", "message": "CloudFront must define default cache behavior."}],
                "on_fail": "finding",
            },
            {
                "id": "waf-perf-110.tf.azurerm.cdn-endpoint",
                "engine": "terraform",
                "automated": True,
                "title_en": "Azure CDN endpoints must have origin host header and compression configured",
                "title_de": "Azure CDN Endpoints müssen Origin Host Header und Komprimierung konfiguriert haben",
                "provider": "azurerm",
                "scope": {"block_type": "resource", "resource_types": ["azurerm_cdn_endpoint"]},
                "assertions": [{"attribute": "origin_host_header", "op": "attribute_exists", "message": "CDN endpoint must have origin host header configured."}],
                "on_fail": "finding",
            },
            {
                "id": "waf-perf-110.config.cache-adr",
                "engine": "config",
                "automated": False,
                "title_en": "Caching strategy must be documented in architecture decision record",
                "title_de": "Caching-Strategie muss im Architektur-Entscheidungsrecord dokumentiert sein",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/adr/*.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "At least one ADR must document caching strategy."}],
                "on_fail": "advisory",
            },
        ],
    },
    {
        "id": "WAF-PERF-120",
        "pillar": "efficiancy",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "logging-monitoring",
        "automatable": "Medium",
        "title_en": "Database workloads MUST undergo regular index and query performance reviews",
        "title_de": "Datenbank-Workloads müssen Index- und Query-Performance regelmäßig reviewen",
        "description_en": (
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
        ],
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-PERF-010", "WAF-PERF-020", "WAF-PERF-030", "WAF-COST-030", "WAF-OPS-050", "WAF-REL-110"],
        "checks": [
            {
                "id": "waf-perf-120.tf.aws.rds-performance-insights",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS RDS instances must enable Performance Insights",
                "title_de": "AWS RDS-Instanzen müssen Performance Insights aktiviert haben",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_db_instance", "aws_rds_cluster_instance"]},
                "assertions": [{"attribute": "performance_insights_enabled", "op": "is_true", "message": "RDS must have Performance Insights enabled for query review."}],
                "on_fail": "finding",
            },
            {
                "id": "waf-perf-120.config.query-review-register",
                "engine": "config",
                "automated": False,
                "title_en": "Database query review register must exist",
                "title_de": "Datenbank-Query-Review-Register muss existieren",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/performance/db-query-review.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "Database query review register must document review cadence and owners."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-REL-110",
        "pillar": "reliability",
        "severity": "high",
        "type": ["configuration", "architecture"],
        "category": "reliability-design",
        "automatable": "High",
        "title_en": "Circuit breaker, backpressure, and rate limiting MUST be defined for downstream dependencies",
        "title_de": "Circuit Breaker, Backpressure und Rate Limiting müssen für Downstream-Abhängigkeiten definiert sein",
        "description_en": (
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
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-REL-050", "WAF-REL-120", "WAF-REL-130", "WAF-OPS-020", "WAF-OPS-040", "WAF-AGN-040", "WAF-AGN-110"],
        "checks": [
            {
                "id": "waf-rel-110.tf.aws.alb-timeout",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS ALB idle timeout must be explicitly configured",
                "title_de": "AWS ALB Idle Timeout muss explizit konfiguriert sein",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_lb"]},
                "assertions": [{"attribute": "idle_timeout", "op": "attribute_exists", "message": "ALB idle_timeout must be explicitly set."}],
                "on_fail": "violation",
            },
            {
                "id": "waf-rel-110.tf.aws.api-gateway-throttle",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS API Gateway must define throttling settings",
                "title_de": "AWS API Gateway muss Throttling-Einstellungen definieren",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_api_gateway_stage", "aws_apigatewayv2_stage"]},
                "assertions": [
                    {"attribute": "throttle_settings", "op": "attribute_exists", "message": "API Gateway stage must define throttling."},
                ],
                "on_fail": "finding",
            },
            {
                "id": "waf-rel-110.tf.azurerm.app-gateway-timeout",
                "engine": "terraform",
                "automated": True,
                "title_en": "Azure Application Gateway backend settings must define explicit request timeout",
                "title_de": "Azure Application Gateway Backend-Einstellungen müssen explizite Request Timeouts definieren",
                "provider": "azurerm",
                "scope": {"block_type": "resource", "resource_types": ["azurerm_application_gateway"]},
                "assertions": [{"attribute": "backend_http_settings.request_timeout_in_seconds", "op": "attribute_exists", "message": "Backend HTTP settings must define request timeout."}],
                "on_fail": "violation",
            },
            {
                "id": "waf-rel-110.config.resilience-policy",
                "engine": "config",
                "automated": False,
                "title_en": "Circuit breaker policy must be documented",
                "title_de": "Circuit-Breaker-Policy muss dokumentiert sein",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/reliability/circuit-breaker-policy.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "Circuit breaker/backpressure policy must exist."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-REL-120",
        "pillar": "reliability",
        "severity": "high",
        "type": ["governance", "architecture"],
        "category": "reliability-design",
        "automatable": "Low",
        "title_en": "Graceful degradation and fallback strategies MUST be documented and tested",
        "title_de": "Graceful Degradation und Fallback-Strategien müssen dokumentiert und getestet sein",
        "description_en": (
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
        "providers": "Any",
        "related_controls": ["WAF-REL-050", "WAF-REL-110", "WAF-REL-130", "WAF-OPS-020", "WAF-OPS-040", "WAF-AGN-040"],
        "checks": [
            {
                "id": "waf-rel-120.config.degradation-adr",
                "engine": "config",
                "automated": False,
                "title_en": "Graceful degradation must be documented in ADR",
                "title_de": "Graceful Degradation muss im ADR dokumentiert sein",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/adr/*degradation*.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "At least one ADR must document graceful degradation strategy."}],
                "on_fail": "finding",
            },
            {
                "id": "waf-rel-120.config.chaos-test-evidence",
                "engine": "config",
                "automated": False,
                "title_en": "Chaos test evidence for fallback paths must exist",
                "title_de": "Chaos-Test-Evidenz für Fallback-Pfade muss existieren",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/reliability/chaos-tests.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "Chaos tests must demonstrate fallback behavior."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-REL-130",
        "pillar": "reliability",
        "severity": "high",
        "type": ["governance", "process"],
        "category": "backup-recovery",
        "automatable": "Low",
        "title_en": "Disaster recovery plans MUST be tested at least annually and updated based on test results",
        "title_de": "Disaster-Recovery-Pläne müssen jährlich getestet und dokumentiert sein",
        "description_en": (
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
        "providers": "Any",
        "related_controls": ["WAF-REL-010", "WAF-REL-040", "WAF-REL-070", "WAF-OPS-030", "WAF-OPS-060", "WAF-SOV-120"],
        "checks": [
            {
                "id": "waf-rel-130.config.dr-plan-documented",
                "engine": "config",
                "automated": False,
                "title_en": "DR plan with RTO/RPO must be documented",
                "title_de": "DR-Plan mit RTO/RPO muss dokumentiert sein",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/reliability/disaster-recovery-plan.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "DR plan must define RTO, RPO, and test schedule."}],
                "on_fail": "violation",
            },
            {
                "id": "waf-rel-130.config.dr-test-evidence",
                "engine": "config",
                "automated": False,
                "title_en": "Annual DR test evidence must exist",
                "title_de": "Jährliche DR-Test-Evidenz muss existieren",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/reliability/dr-test-evidence.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "DR test evidence within last 12 months must exist."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-OPS-110",
        "pillar": "excellence",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "deployment-automation",
        "automatable": "Medium",
        "title_en": "GitOps-based deployments SHOULD be preferred for Kubernetes and container workloads",
        "title_de": "GitOps-basierte Deployments müssen für Kubernetes-/Container-Workloads bevorzugt werden",
        "description_en": (
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
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-OPS-020", "WAF-OPS-030", "WAF-OPS-050", "WAF-OPS-120", "WAF-SEC-090", "WAF-REL-110"],
        "checks": [
            {
                "id": "waf-ops-110.tf.aws.eks-gitops-addon",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS EKS should deploy GitOps agent via EKS add-on or Helm",
                "title_de": "AWS EKS sollte GitOps-Agent über EKS Add-on oder Helm bereitstellen",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_eks_addon", "helm_release"]},
                "assertions": [{"attribute": "addon_name", "op": "in", "expected": ["fluxcd", "argo-cd"], "message": "EKS should have a GitOps add-on installed."}],
                "on_fail": "advisory",
            },
            {
                "id": "waf-ops-110.tf.azurerm.gitops-extension",
                "engine": "terraform",
                "automated": True,
                "title_en": "Azure AKS should use Flux extension for GitOps",
                "title_de": "Azure AKS sollte Flux-Erweiterung für GitOps verwenden",
                "provider": "azurerm",
                "scope": {"block_type": "resource", "resource_types": ["azurerm_kubernetes_cluster_extension"]},
                "assertions": [{"attribute": "extension_type", "op": "in", "expected": ["microsoft.flux"], "message": "AKS should use microsoft.flux GitOps extension."}],
                "on_fail": "advisory",
            },
            {
                "id": "waf-ops-110.config.gitops-policy",
                "engine": "config",
                "automated": False,
                "title_en": "GitOps policy must be documented",
                "title_de": "GitOps-Policy muss dokumentiert sein",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/devops/gitops-policy.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "GitOps policy must describe repository structure and reconciliation."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-OPS-120",
        "pillar": "excellence",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "deployment-automation",
        "automatable": "Medium",
        "title_en": "Feature flags MUST be available and documented for high-risk changes",
        "title_de": "Feature Flags müssen für risikoreiche Änderungen verfügbar und dokumentiert sein",
        "description_en": (
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
        "providers": "Any",
        "related_controls": ["WAF-OPS-020", "WAF-OPS-030", "WAF-OPS-050", "WAF-OPS-110", "WAF-REL-110", "WAF-REL-120"],
        "checks": [
            {
                "id": "waf-ops-120.config.feature-flag-policy",
                "engine": "config",
                "automated": False,
                "title_en": "Feature flag policy must exist",
                "title_de": "Feature-Flag-Policy muss existieren",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/devops/feature-flag-policy.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "Feature flag policy must define kill-switch and lifecycle."}],
                "on_fail": "finding",
            },
            {
                "id": "waf-ops-120.tf.aws.appconfig-flags",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS AppConfig feature flags should be used",
                "title_de": "AWS AppConfig Feature Flags sollten verwendet werden",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_appconfig_extension_association", "aws_appconfig_configuration_profile"]},
                "assertions": [{"attribute": "name", "op": "attribute_exists", "message": "AppConfig resources must exist for feature flags."}],
                "on_fail": "advisory",
            },
        ],
    },
    {
        "id": "WAF-SUS-110",
        "pillar": "sustainability",
        "severity": "medium",
        "type": ["governance", "configuration"],
        "category": "data-governance",
        "automatable": "Medium",
        "title_en": "Regional carbon intensity MUST be considered and documented in location decisions",
        "title_de": "Regionale Kohlenstoffintensität muss bei Standortentscheidungen berücksichtigt und dokumentiert werden",
        "description_en": (
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
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-SUS-010", "WAF-SUS-020", "WAF-SUS-030", "WAF-SUS-120", "WAF-COST-010", "WAF-SOV-120"],
        "checks": [
            {
                "id": "waf-sus-110.tf.aws.green-region",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS provider region should be a low-carbon region",
                "title_de": "AWS-Provider-Region sollte eine kohlenstoffarme Region sein",
                "provider": "aws",
                "scope": {"block_type": "provider", "provider_name": "aws"},
                "assertions": [{"attribute": "region", "op": "in", "expected": ["us-west-2", "eu-north-1", "eu-west-1"], "message": "AWS region has a high carbon intensity. Document justification or migrate."}],
                "on_fail": "advisory",
            },
            {
                "id": "waf-sus-110.config.carbon-adr",
                "engine": "config",
                "automated": False,
                "title_en": "Carbon intensity region decision must be documented in ADR",
                "title_de": "Kohlenstoffintensität der Regionsentscheidung muss im ADR dokumentiert sein",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/adr/*carbon*.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "ADR must document carbon intensity consideration."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-SUS-120",
        "pillar": "sustainability",
        "severity": "low",
        "type": ["governance", "configuration"],
        "category": "sustainability-efficiency",
        "automatable": "Medium",
        "title_en": "Batch and HPC workloads SHOULD run off-peak where SLA constraints allow",
        "title_de": "Batch- und HPC-Workloads müssen zeitverschoben (off-peak) aufsetzen, soweit SLA das zulässt",
        "description_en": (
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
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-SUS-010", "WAF-SUS-020", "WAF-SUS-030", "WAF-SUS-110", "WAF-COST-110", "WAF-OPS-040"],
        "checks": [
            {
                "id": "waf-sus-120.tf.aws.batch-schedule",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS Batch compute environments should prefer Spot and off-peak scheduling",
                "title_de": "AWS Batch Compute Environments sollten Spot und Off-Peak-Scheduling bevorzugen",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_batch_compute_environment", "aws_batch_job_queue"]},
                "assertions": [{"attribute": "compute_resources.spot_iam_fleet_role", "op": "attribute_exists", "message": "Batch compute environment should use Spot capacity."}],
                "on_fail": "advisory",
            },
            {
                "id": "waf-sus-120.config.off-peak-schedule",
                "engine": "config",
                "automated": False,
                "title_en": "Off-peak scheduling policy must be documented",
                "title_de": "Off-Peak-Scheduling-Policy muss dokumentiert sein",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/sustainability/off-peak-scheduling.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "Off-peak scheduling policy must define SLA windows."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-SOV-110",
        "pillar": "sovereign",
        "severity": "critical",
        "type": ["governance", "configuration"],
        "category": "encryption-key-management",
        "automatable": "High",
        "title_en": "Cryptographic keys for sensitive data MUST be managed in HSM or sovereign key management services",
        "title_de": "Kryptographische Schlüssel für sensitive Daten müssen in HSM oder sovereignem KMS verwaltet werden",
        "description_en": (
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
            ("EUCS (ENISA)", ["CRY-03 – Key management", "SOV-03 – Customer key control"]),
            ("ISO 27001:2022", ["A.8.24 – Use of cryptography"]),
        ],
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-SOV-010", "WAF-SOV-020", "WAF-SOV-050", "WAF-SEC-030", "WAF-SEC-060", "WAF-SOV-120", "WAF-AGN-110"],
        "checks": [
            {
                "id": "waf-sov-110.tf.aws.kms-hsm",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS KMS keys for sensitive data must use HSM-backed CUSTOMER-managed keys",
                "title_de": "AWS KMS-Schlüssel für sensitive Daten müssen HSM-gestützte, kundeneigene Schlüssel verwenden",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_kms_key"]},
                "assertions": [
                    {"attribute": "customer_master_key_spec", "op": "attribute_exists", "message": "KMS key must define key spec."},
                ],
                "on_fail": "finding",
            },
            {
                "id": "waf-sov-110.tf.azurerm.hsm-keyvault",
                "engine": "terraform",
                "automated": True,
                "title_en": "Azure Key Vault must use Premium SKU with HSM-backed keys",
                "title_de": "Azure Key Vault muss Premium-SKU mit HSM-gestützten Schlüsseln verwenden",
                "provider": "azurerm",
                "scope": {"block_type": "resource", "resource_types": ["azurerm_key_vault"]},
                "assertions": [{"attribute": "sku_name", "op": "in", "expected": ["premium", "Premium"], "message": "Key Vault must use Premium SKU for HSM-backed keys."}],
                "on_fail": "finding",
            },
            {
                "id": "waf-sov-110.tf.google.hsm-kms",
                "engine": "terraform",
                "automated": True,
                "title_en": "GCP KMS keys for sensitive data must use Cloud HSM",
                "title_de": "GCP KMS-Schlüssel für sensitive Daten müssen Cloud HSM verwenden",
                "provider": "google",
                "scope": {"block_type": "resource", "resource_types": ["google_kms_crypto_key"]},
                "assertions": [{"attribute": "key_ring", "op": "attribute_exists", "message": "Crypto key must be in a defined key ring."}],
                "on_fail": "finding",
            },
        ],
    },
    {
        "id": "WAF-SOV-120",
        "pillar": "sovereign",
        "severity": "high",
        "type": ["governance"],
        "category": "data-governance",
        "automatable": "Low",
        "title_en": "Data processing agreements MUST be documented for every sub-processor",
        "title_de": "Auftragsverarbeitungsvereinbarungen (AVV/DPA) müssen für jeden Subprozessor dokumentiert vorliegen",
        "description_en": (
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
            ("DORA", ["Art. 28 – Subcontracting of ICT services"]),
            ("ISO 27001:2022", ["A.5.19 – Information security in supplier relationships"]),
        ],
        "providers": "Any",
        "related_controls": ["WAF-SOV-010", "WAF-SOV-030", "WAF-SOV-050", "WAF-SOV-060", "WAF-SOV-090", "WAF-SEC-010", "WAF-SEC-130"],
        "checks": [
            {
                "id": "waf-sov-120.config.dpa-register",
                "engine": "config",
                "automated": False,
                "title_en": "DPA register must list all sub-processors",
                "title_de": "DPA-Register muss alle Subprozessoren auflisten",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/governance/dpa-register.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "DPA/AVV register must list each sub-processor and agreement status."}],
                "on_fail": "violation",
            },
        ],
    },
    {
        "id": "WAF-AGN-110",
        "pillar": "agentic",
        "severity": "high",
        "type": ["governance", "configuration"],
        "category": "agentic-governance",
        "automatable": "Medium",
        "title_en": "Agent outputs and actions MUST be validated, sandboxed, and restricted to allowlists",
        "title_de": "Agent-Ausgaben und -Aktionen müssen validiert, sandboxed und auf Allowlists beschränkt sein",
        "description_en": (
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
            ("SOC 2 Type II", ["CC6.1 – Logical access controls"]),
        ],
        "providers": "AWS, Azure, GCP, **StackIT**, **OVHcloud**, **Hetzner**",
        "related_controls": ["WAF-AGN-010", "WAF-AGN-020", "WAF-AGN-030", "WAF-AGN-040", "WAF-AGN-050", "WAF-AGN-060", "WAF-AGN-070", "WAF-SEC-010", "WAF-SEC-060", "WAF-REL-110"],
        "checks": [
            {
                "id": "waf-agn-110.tf.aws.bedrock-guardrail",
                "engine": "terraform",
                "automated": True,
                "title_en": "AWS Bedrock agent must use guardrails with blocked outputs",
                "title_de": "AWS Bedrock-Agent muss Guardrails mit blockierten Ausgaben verwenden",
                "provider": "aws",
                "scope": {"block_type": "resource", "resource_types": ["aws_bedrock_guardrail"]},
                "assertions": [{"attribute": "name", "op": "attribute_exists", "message": "Bedrock guardrail must be configured."}],
                "on_fail": "finding",
            },
            {
                "id": "waf-agn-110.config.agent-validation-policy",
                "engine": "config",
                "automated": False,
                "title_en": "Agent output validation and tool allowlist policy must exist",
                "title_de": "Agent-Output-Validierungs- und Tool-Allowlist-Policy muss existieren",
                "provider": "any",
                "scope": {"block_type": "file", "path_pattern": "docs/agentic/agent-validation-policy.md"},
                "assertions": [{"attribute": "exists", "op": "attribute_exists", "message": "Agent validation and tool allowlist policy must exist."}],
                "on_fail": "finding",
            },
        ],
    },
]


# --- YAML generation ----------------------------------------------------------

def category_risk_de(category):
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
    }.get(category, f"Fehlende Umsetzung dieser Kontrolle erhöht das Risiko von Sicherheitsvorfällen, Compliance-Verstößen und Betriebsunterbrechungen.")


def build_yaml(control):
    risk_de = category_risk_de(control["category"])
    rationale = f"{risk_de} Dieses Control adressiert die Anforderungen des Bereichs '{control['category'].replace('-', ' ').title()}' und stellt sicher, dass {control['description_en'][:100].rstrip('. ')}..."
    checks_out = []
    for ch in control["checks"]:
        checks_out.append({
            "id": ch["id"],
            "engine": ch["engine"],
            "provider": ch["provider"],
            "automated": ch["automated"],
            "title": ch["title_en"],
            "description": ch["title_en"],
            "expected": "true",
            "remediation": ch["title_en"],
            "scope": ch["scope"],
            "assertions": ch["assertions"],
            "on_fail": ch["on_fail"],
        })
    return {
        "id": control["id"],
        "title": control["title_en"],
        "status": "active",
        "tags": sorted(set([control["pillar"]] + control["type"] + [control["severity"]])),
        "pillar": control["pillar"],
        "severity": control["severity"],
        "type": control["type"],
        "category": control["category"],
        "rationale": rationale,
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
            "narrative": f"modules/{PILLAR_MODULE[control['pillar']]}/pages/controls/{control['id']}.adoc",
            "related_controls": control["related_controls"],
        },
        "description": control["description_en"],
        "regulatory_mapping": [{"framework": fw, "controls": ctrls} for fw, ctrls in control["frameworks"]],
        "checks": checks_out,
    }


def write_yaml_files():
    for lang, repo_root in REPOS.items():
        for c in NEW_CONTROLS:
            path = Path(repo_root) / "modules" / "controls" / "controls" / f"{c['id']}.yml"
            data = build_yaml(c)
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=120)
        print(f"Wrote {len(NEW_CONTROLS)} YAML controls to {repo_root}")


# --- narrative generation -----------------------------------------------------

def check_lines_de(check):
    lines = []
    lines.append(f"=== {check['id']}")
    lines.append("")
    auto = "Ja" if check["automated"] else "Nein"
    lines.append(f"*Engine:* `{check['engine']}` | *Provider:* {check['provider']} | *Automated:* {auto}")
    lines.append("")
    lines.append(f"*{check['title_de']}*")
    lines.append("")
    lines.append(check["title_de"])
    lines.append("")
    scope = check["scope"]
    if scope.get("block_type") == "resource":
        lines.append(f"*Scope:* `resource` — {', '.join(scope['resource_types'])}")
    elif scope.get("block_type") == "provider":
        lines.append(f"*Scope:* `provider` — `{scope['provider_name']}`")
    elif scope.get("block_type") == "file":
        lines.append(f"*Scope:* `file` — `{scope['path_pattern']}`")
    else:
        lines.append(f"*Scope:* `{scope.get('block_type')}`")
    lines.append("")
    lines.append("*Assertions:*")
    for a in check["assertions"]:
        attr = a.get("attribute", "")
        op = a.get("op", "")
        expected = a.get("expected")
        key = a.get("key")
        msg = a.get("message", "")
        if key:
            lines.append(f"* `{attr}` {op} `{key}` — {msg}")
        elif expected is not None:
            lines.append(f"* `{attr}` {op} `{expected}` — {msg}")
        else:
            lines.append(f"* `{attr}` {op} — {msg}")
    lines.append("")
    lines.append(f"*Remediation:* {check['title_de']}")
    lines.append("")
    lines.append(".Compliant")
    lines.append("[source,terraform]")
    lines.append("----")
    lines.append(f"# Beispiel konform zu {check['id']}")
    lines.append("----")
    lines.append("")
    lines.append(".Non-Compliant")
    lines.append("[source,terraform]")
    lines.append("----")
    lines.append(f"# Beispiel nicht konform zu {check['id']}")
    lines.append("----")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def check_lines_en(check):
    lines = []
    lines.append(f"=== {check['id']}")
    lines.append("")
    auto = "Yes" if check["automated"] else "No"
    lines.append(f"*Engine:* `{check['engine']}` | *Provider:* {check['provider']} | *Automated:* {auto}")
    lines.append("")
    lines.append(f"*{check['title_en']}*")
    lines.append("")
    lines.append(check["title_en"])
    lines.append("")
    scope = check["scope"]
    if scope.get("block_type") == "resource":
        lines.append(f"*Scope:* `resource` — {', '.join(scope['resource_types'])}")
    elif scope.get("block_type") == "provider":
        lines.append(f"*Scope:* `provider` — `{scope['provider_name']}`")
    elif scope.get("block_type") == "file":
        lines.append(f"*Scope:* `file` — `{scope['path_pattern']}`")
    else:
        lines.append(f"*Scope:* `{scope.get('block_type')}`")
    lines.append("")
    lines.append("*Assertions:*")
    for a in check["assertions"]:
        attr = a.get("attribute", "")
        op = a.get("op", "")
        expected = a.get("expected")
        key = a.get("key")
        msg = a.get("message", "")
        if key:
            lines.append(f"* `{attr}` {op} `{key}` — {msg}")
        elif expected is not None:
            lines.append(f"* `{attr}` {op} `{expected}` — {msg}")
        else:
            lines.append(f"* `{attr}` {op} — {msg}")
    lines.append("")
    lines.append(f"*Remediation:* {check['title_en']}")
    lines.append("")
    lines.append(".Compliant")
    lines.append("[source,terraform]")
    lines.append("----")
    lines.append(f"# Example compliant with {check['id']}")
    lines.append("----")
    lines.append("")
    lines.append(".Non-Compliant")
    lines.append("[source,terraform]")
    lines.append("----")
    lines.append(f"# Example non-compliant with {check['id']}")
    lines.append("----")
    lines.append("")
    lines.append("---")
    lines.append("")
    return lines


def generate_adoc(control, lang):
    module = PILLAR_MODULE[control["pillar"]]
    sev_emoji = SEVERITY_EMOJI[control["severity"]]
    sev_de = {"critical": "Kritisch", "high": "Hoch", "medium": "Mittel", "low": "Niedrig"}[control["severity"]]
    if lang == "de":
        lines = [
            f"= {control['id']} – {control['title_de']}",
            ":page-toc: right",
            f":control-id: {control['id']}",
            f":pillar: {control['pillar']}",
            f":severity: {control['severity']}",
            f":category: {control['category']}",
            f":automatable: {control['automatable']}",
            f":description: {control['description_en']}",
            "",
            f"[.metadata]",
            f"*Säule:* {control['pillar'].title()} | *Schweregrad:* {sev_emoji} {sev_de} | *Kategorie:* {control['category'].replace('-',' ').title()} | *Automatisierbar:* {control['automatable']}",
            "",
            "== Beschreibung",
            "",
            control["description_en"],
            "",
            "== Begründung",
            "",
            '[cols="1,3"]',
            "|===",
            "|Risiko |Beschreibung",
            "",
        ]
        for t in control["threat"]:
            lines.append(f"|*Risk* |{t}")
            lines.append("")
        lines.append("|===")
        lines.append("")
        lines.append("== Anforderungen")
        lines.append("")
        for sentence in control["description_en"].split(". "):
            sentence = sentence.strip()
            if sentence:
                if not sentence.endswith("."):
                    sentence += "."
                lines.append(f"* {sentence}")
        lines.append("")
        lines.append("== Implementierungsleitfaden")
        lines.append("")
        lines.append(". Document the requirement in a version-controlled policy, ADR, or standard.")
        lines.append(". Assign ownership and establish a review cadence (e.g., quarterly).")
        lines.append(". Implement the required configuration as code in Terraform or equivalent IaC.")
        lines.append("")
        lines.append("== Reifegrade")
        lines.append("")
        lines.append('[cols="1,2,4"]')
        lines.append("|===")
        lines.append("|Level |Name |Kriterien")
        lines.append("")
        for lvl, label in [("level_1", "L1"), ("level_2", "L2"), ("level_3", "L3"), ("level_4", "L4"), ("level_5", "L5")]:
            ml = build_yaml(control)["maturity_levels"][lvl]
            crit = ml["criteria"][0]
            lines.append(f"|{label} |{ml['description']} |* {crit}")
            lines.append("")
        lines.append("|===")
        lines.append("")
        lines.append("== Checks")
        lines.append("")
        for ch in control["checks"]:
            lines.extend(check_lines_de(ch))
        lines.append("")
        lines.append("== Evidenz")
        lines.append("")
        lines.append("* Terraform-Konfiguration, die die Anforderung umsetzt.")
        lines.append("* Policy, ADR oder Standard, der die Anforderung dokumentiert.")
        lines.append("* Optionale Cloud-Konsolen- oder API-Ausgaben, die den Laufzeit-Zustand bestätigen.")
        lines.append("")
        lines.append("== Verwandte Controls")
        lines.append("")
        for rc in control["related_controls"]:
            rc_pillar = "-".join(rc.lower().split("-")[1:2])
            rc_pillar = {
                "sec": "pillar-security", "cost": "pillar-cost", "perf": "pillar-efficiancy",
                "rel": "pillar-reliability", "ops": "pillar-excellence", "sus": "pillar-sustainability",
                "sov": "pillar-sovereign", "agn": "pillar-agentic",
            }[rc_pillar]
            lines.append(f"* xref:{rc_pillar}:controls/{rc}.adoc[{rc}]")
        lines.append("")
        lines.append("== Regulatorisches Mapping")
        lines.append("")
        for fw, ctrls in control["frameworks"]:
            lines.append(f"* *{fw}*: {', '.join(ctrls)}")
        lines.append("")
    else:
        sev_en = control["severity"].title()
        lines = [
            f"= {control['id']} – {control['title_en']}",
            ":page-toc: right",
            f":control-id: {control['id']}",
            f":pillar: {control['pillar']}",
            f":severity: {control['severity']}",
            f":category: {control['category']}",
            f":automatable: {control['automatable']}",
            f":description: {control['description_en']}",
            "",
            f"[.metadata]",
            f"*Pillar:* {control['pillar'].title()} | *Severity:* {sev_emoji} {sev_en} | *Category:* {control['category'].replace('-',' ').title()} | *Automatable:* {control['automatable']}",
            "",
            "== Description",
            "",
            control["description_en"],
            "",
            "== Rationale",
            "",
            '[cols="1,3"]',
            "|===",
            "|Risk |Description",
            "",
        ]
        for t in control["threat"]:
            lines.append(f"|*Risk* |{t}")
            lines.append("")
        lines.append("|===")
        lines.append("")
        lines.append("== Requirements")
        lines.append("")
        for sentence in control["description_en"].split(". "):
            sentence = sentence.strip()
            if sentence:
                if not sentence.endswith("."):
                    sentence += "."
                lines.append(f"* {sentence}")
        lines.append("")
        lines.append("== Implementation Guidance")
        lines.append("")
        lines.append(". Document the requirement in a version-controlled policy, ADR, or standard.")
        lines.append(". Assign ownership and establish a review cadence (e.g., quarterly).")
        lines.append(". Implement the required configuration as code in Terraform or equivalent IaC.")
        lines.append("")
        lines.append("== Maturity Levels")
        lines.append("")
        lines.append('[cols="1,2,4"]')
        lines.append("|===")
        lines.append("|Level |Name |Criteria")
        lines.append("")
        for lvl, label in [("level_1", "L1"), ("level_2", "L2"), ("level_3", "L3"), ("level_4", "L4"), ("level_5", "L5")]:
            ml = build_yaml(control)["maturity_levels"][lvl]
            crit = ml["criteria"][0]
            lines.append(f"|{label} |{ml['description']} |* {crit}")
            lines.append("")
        lines.append("|===")
        lines.append("")
        lines.append("== Checks")
        lines.append("")
        for ch in control["checks"]:
            lines.extend(check_lines_en(ch))
        lines.append("")
        lines.append("== Evidence")
        lines.append("")
        lines.append("* Terraform configuration implementing the requirement.")
        lines.append("* Policy, ADR, or standard documenting the requirement.")
        lines.append("* Optional cloud console or API output confirming runtime state.")
        lines.append("")
        lines.append("== Related Controls")
        lines.append("")
        for rc in control["related_controls"]:
            rc_pillar = "-".join(rc.lower().split("-")[1:2])
            rc_pillar = {
                "sec": "pillar-security", "cost": "pillar-cost", "perf": "pillar-efficiancy",
                "rel": "pillar-reliability", "ops": "pillar-excellence", "sus": "pillar-sustainability",
                "sov": "pillar-sovereign", "agn": "pillar-agentic",
            }[rc_pillar]
            lines.append(f"* xref:{rc_pillar}:controls/{rc}.adoc[{rc}]")
        lines.append("")
        lines.append("== Regulatory Mapping")
        lines.append("")
        for fw, ctrls in control["frameworks"]:
            lines.append(f"* *{fw}*: {', '.join(ctrls)}")
        lines.append("")
    return "\n".join(lines) + "\n"


def write_narratives():
    for lang, repo_root in REPOS.items():
        for c in NEW_CONTROLS:
            module = PILLAR_MODULE[c["pillar"]]
            path = Path(repo_root) / "modules" / module / "pages" / "controls" / f"{c['id']}.adoc"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(generate_adoc(c, lang), encoding="utf-8")
        print(f"Wrote {len(NEW_CONTROLS)} narrative pages to {repo_root}")


# --- nav and catalog ----------------------------------------------------------

def update_navigation():
    for lang, repo_root in REPOS.items():
        for c in NEW_CONTROLS:
            module = PILLAR_MODULE[c["pillar"]]
            nav_path = Path(repo_root) / "modules" / module / "nav.adoc"
            text = nav_path.read_text(encoding="utf-8")
            # find controls section block
            pattern = re.compile(r"(\.\.\. Controls\n|\*\*\* Controls & Audit\n|\*\*\* Controls\n|\*\*\* xref:controls\.adoc[^\n]*\n|\*\*\* xref:controls:index\.adoc[^\n]*\n)(.*?)(\n(?:\*\* |\*\*\* )|\Z)", re.S)
            def repl(m):
                header = m.group(1)
                body = m.group(2)
                tail = m.group(3)
                existing = re.findall(r"WAF-" + c["id"].split("-")[1] + r"-\d{3}", body)
                if c["id"] in existing:
                    return m.group(0)
                # append control entry before tail; match depth by first control line
                lines = body.rstrip().split("\n")
                prefix = "****"
                for line in lines:
                    if re.match(r"\*+ xref:controls/WAF-", line):
                        prefix = line.split("xref")[0]
                        break
                lines.append(f"{prefix} xref:controls/{c['id']}.adoc[{c['id']} {c['title_de' if lang=='de' else 'title_en'][:40]}...]")
                return header + "\n".join(lines) + tail
            text = pattern.sub(repl, text, count=1)
            nav_path.write_text(text, encoding="utf-8")
        print(f"Updated navigation in {repo_root}")


def update_catalog():
    for lang, repo_root in REPOS.items():
        path = Path(repo_root) / "modules" / "controls" / "pages" / "catalog.adoc"
        text = path.read_text(encoding="utf-8")
        for c in NEW_CONTROLS:
            pillar = PILLAR_MODULE[c["pillar"]]
            # Find table for this pillar
            marker = f"== Pillar {list(PILLAR_MODULE.values()).index(pillar)+1}"
            # Better: find by module name
            marker = f"== Pillar"
            # insert before the |=== that ends the table containing this pillar's controls
            # Use regex to find section header and table end
            sev_emoji = SEVERITY_EMOJI[c["severity"]]
            sev_word = c["severity"].title()
            title = c["title_en"]
            row = (
                f"|xref:#{c['id']}[{c['id']}]\n"
                f"|{title}\n"
                f"|{sev_emoji} {sev_word}\n"
                f"|{c['providers']}\n"
                f"|{c['category']}\n"
            )
            # Insert row before the first "|===" that follows this pillar's section header
            section_title = None
            for header in re.finditer(r"^== Pillar \d+ · (.+) – WAF-[A-Z]+\n", text, re.M):
                if PILLAR_MODULE[c["pillar"]].replace("pillar-", "").replace("excellence", "operational excellence") in header.group(1).lower() or PILLAR_MODULE[c["pillar"]].replace("pillar-", "") in header.group(1).lower():
                    section_title = header.start()
                    break
            if section_title is None:
                print(f"WARNING: could not find catalog section for {c['id']}")
                continue
            # find table end after section
            table_end = text.find("\n|===", section_title)
            # insert before table_end
            text = text[:table_end] + "\n" + row + text[table_end:]
        path.write_text(text, encoding="utf-8")
        print(f"Updated catalog in {repo_root}")


# --- main ---------------------------------------------------------------------

def main():
    write_yaml_files()
    write_narratives()
    update_navigation()
    update_catalog()
    print("Done. Run validation and regenerate framework pages/compliance dashboard.")


if __name__ == "__main__":
    main()
