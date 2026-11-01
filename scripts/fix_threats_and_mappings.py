#!/usr/bin/env python3
"""Replace placeholder threats with control-specific risks and tighten framework mappings.

Applies to all 83 YAML controls in both language repositories.
"""
import glob
import yaml
from pathlib import Path

REPOS = {
    "de": ".",
    "en": "../framework-en",
}

PLACEHOLDERS = [
    "Autonomous agents take unreviewed actions when identity, logging, or boundaries are missing.",
    "Sensitive data leaks through agent prompts, tool calls, or memory stores.",
    "Non-compliance with this control creates exploitable weaknesses in the workload.",
    "Audit and certification evidence is harder to produce when the control is missing.",
    "Overly permissive or shared credentials allow unauthorized access and privilege escalation.",
    "Weak authentication policies increase the risk of account takeover.",
]

# Control-specific threat pairs (lang -> cid -> [threat1, threat2])
SPECIFIC_THREATS = {
    "de": {
        # Agentic
        "WAF-AGN-010": [
            "Nicht identifizierbare Agenten können weder zurückverfolgt noch für ihre Aktionen zur Verantwortung gezogen werden.",
            "Fehlende Authentifizierung für Agenten ermöglicht Identitätssprengung und nicht nachvollziehbare Änderungen.",
        ],
        "WAF-AGN-020": [
            "Zu weitreichende Tool-Berechtigungen erlauben Agenten destruktive oder unautorisierte Operationen.",
            "Fehlende Berechtigungsgrenzen auf Tool-Ebene ermöglichen Rechteausweitung in automatisierten Workflows.",
        ],
        "WAF-AGN-030": [
            "Undurchsichtige Agenten-Entscheidungen verhindern Root-Cause-Analysen und regulatorische Audits.",
            "Fehlende Begründungsketten machen es unmöglich, die Einhaltung von Geschäftsregeln nachzuweisen.",
        ],
        "WAF-AGN-040": [
            "Inkonsistentes Memory-Management führt zu widersprüchlichen Entscheidungen und Dateninkonsistenzen.",
            "Unkontrollierte Zustandsspeicherung kann sensible Kontexte zwischen Sitzungen oder Mandanten leaken.",
        ],
        "WAF-AGN-050": [
            "Fehljustierte Agenten können für falsche Ziele optimieren und Geschäfts- oder Sicherheitsschäden verursachen.",
            "Fehlende Verifikationsschleifen lassen fehlerhafte Agenten-Ausgaben in Produktionssysteme gelangen.",
        ],
        "WAF-AGN-060": [
            "Unkoordinierte Agenten erzeugen Race Conditions, Deadlocks oder doppelte kritische Operationen.",
            "Fehlende Orchestrierungs-Governance ermöglicht es Agenten-Schwärmen, Freigabegrenzen zu umgehen.",
        ],
        "WAF-AGN-070": [
            "Unsichtbare Agenten-Aktivitäten verzögern die Erkennung von Missbrauch, Drift oder Angriffen.",
            "Ohne Metriken lässt sich Agenten-Verhalten weder kontrollieren noch kontinuierlich verbessern.",
        ],
        "WAF-AGN-080": [
            "Agenten, die sensible Entscheidungen ohne menschliche Freigabe treffen, können irreversible Schäden verursachen.",
            "Fehlende Freigabegatter für hochimpactige Aktionen verletzen Verantwortlichkeits- und Compliance-Anforderungen.",
        ],
        "WAF-AGN-090": [
            "Unbegrenzter Agenten-Rechenverbrauch führt zu explodierenden Kosten und erhöhtem CO₂-Fußabdruck.",
            "Ineffiziente Agenten-Architekturen verfehlen Latenzanforderungen und verschwenden Ressourcen.",
        ],
        "WAF-AGN-100": [
            "Undokumentierte Agenten-Limitierungen akkumulieren technische und regulatorische Schulden.",
            "Unbekannte Schwächen in Agentensystemen exponieren die Organisation gegenüber neuen Fehlermustern.",
        ],
        # Security
        "WAF-SEC-010": [
            "Konten ohne MFA können durch gestohlene Passwörter oder Phishing kompromittiert werden.",
            "Dauerhafte Root- oder Benutzer-Zugangsschlüssel ermöglichen unentdeckte Persistenz und Datenexfiltration.",
        ],
        "WAF-SEC-020": [
            "Wildcard-Berechtigungen erlauben prinzipiell alle Aktionen auf allen Ressourcen und erleichtern Lateral Movement.",
            "Administrator-Rollen an Workload-Prinzipalen bergen das Risiko unbeabsichtigter oder böswilliger Zerstörung.",
        ],
        "WAF-SEC-070": [
            "Ungeprüfte Container-Images enthalten häufig bekannte Schwachstellen, die in Produktion ausgenutzt werden.",
            "Fehlende SBOMs und Scan-Ergebnisse erschweren Supply-Chain-Audits und Incident Response.",
        ],
        "WAF-SEC-090": [
            "Compliance-Regeln, die nur dokumentiert und nicht als Code gepflegt werden, veralten und werden ignoriert.",
            "Manuelle Kontrollen lassen sich nicht skalierend prüfen und liefern keine wiederholbaren Audit-Nachweise.",
        ],
        "WAF-SEC-100": [
            "Fehlende Incident-Response-Pläne verlängern Reaktionszeiten und verschärfen den Schaden von Sicherheitsvorfällen.",
            "Ungetestete IR-Prozesse führen im Ernstfall zu Fehlentscheidungen und regulatorischen Meldepflichtverletzungen.",
        ],
        "WAF-SEC-110": [
            "Mutable Tags erlauben das Überschreiben produktiver Images und erschweren Rollbacks nach Incidents.",
            "Fehlende Binärautorisierung lässt kompromittierte Images unbemerkt in Produktion deployen.",
        ],
        # Cost
        "WAF-COST-030": [
            "Unreviewte Compute-Ressourcen führen dauerhaft zu Überdimensionierung und Cloud-Waste.",
            "Fehlende Rechtsizing-Nachweise erschweren FinOps-Reviews und Budgetverantwortlichkeit.",
        ],
        "WAF-COST-040": [
            "Unbegrenzte Speicherlebensdauer lässt Daten unnötig wachsen und erhöht Kosten sowie Löschrisiken.",
            "Fehlende Lifecycle-Regeln verhindern die automatische Archivierung oder Löschung abgestufter Datenklassen.",
        ],
        "WAF-COST-050": [
            "Architekturentscheidungen ohne Kostenbetrachtung führen zu lock-in und nicht nachvollziehbaren Ausgaben.",
            "Fehlende Lock-in-Bewertung erschwert spätere Vertragsverhandlungen und Cloud-Wechsel.",
        ],
        "WAF-COST-080": [
            "Hohe Dauerlast ohne Kapazitätsplanung führt zu teuren On-Demand-Ressourcen und Budgetabweichungen.",
            "Fehlende Reserved-Instance- oder Savings-Plan-Dokumentation verhindert Optimierungspotenziale.",
        ],
        # Ops
        "WAF-OPS-010": [
            "Fehlende CI/CD-Pipelines erzwingen manuelle Deployments und erhöhen das Risiko menschlicher Fehler.",
            "Undokumentierte Deployment-Prozesse führen zu nicht reproduzierbaren Umgebungen und längeren Ausfällen.",
        ],
        "WAF-OPS-020": [
            "Manuell verwaltete Infrastruktur driftet von der Dokumentation ab und ist schwer wiederherzustellen.",
            "Fehlende IaC-Praktiken verhindern Versionierung, Peer-Review und Disaster Recovery.",
        ],
        "WAF-OPS-030": [
            "Unstrukturierte Logs und fehlende Metriken verzögern die Fehlerdiagnose und Incident-Erkennung.",
            "Ohne zentrale Observability-Daten lassen sich SLO-Verletzungen und Sicherheitsvorfälle nicht korrelieren.",
        ],
        "WAF-OPS-040": [
            "Alerting auf Infrastruktur- statt Symptom-Metriken erzeugt Alarmflut und verpasst kundenrelevante Ausfälle.",
            "Fehlende Aktionszuordnung bei Alerts verlängert die Zeit bis zur Problembehebung.",
        ],
        "WAF-OPS-050": [
            "Undokumentierte Änderungen an Produktionssystemen erschweren Rollbacks und Audits.",
            "Fehlende Freigabegatter ermöglichen nicht autorisierte oder ungetestete Deployments.",
        ],
        "WAF-OPS-060": [
            "Runbooks, die nicht mit Alerts verknüpft sind, verlangsamen die Reaktion auf wiederkehrende Störungen.",
            "Fehlende Eskalationsanweisungen führen zu unkoordinierten Ad-hoc-Reaktionen.",
        ],
        "WAF-OPS-070": [
            "Nicht dokumentierte Incidents verhindern organisatorisches Lernen und Wiedervorfall-Prävention.",
            "Fehlende Post-Mortems lassen systemische Schwächen unerkannt und unkorrigiert.",
        ],
        "WAF-OPS-080": [
            "Big-Bang-Deployments können alle Benutzer gleichzeitig von Fehlern betreffen und Rollbacks erschweren.",
            "Fehlende Canary- oder Feature-Flag-Mechanismen verlangsamen die Erkennung regressiver Änderungen.",
        ],
        "WAF-OPS-090": [
            "Drift zwischen IaC und tatsächlicher Infrastruktur führt zu Shadow-IT und unerwarteten Konfigurationen.",
            "Unentdeckete manuelle Änderungen untergraben Compliance- und Sicherheitskontrollen.",
        ],
        "WAF-OPS-100": [
            "Undokumentierte manuelle Prozesse akkumulieren Betriebsschulden und Know-how-Risiken.",
            "Nicht priorisierte operationelle Schulden verhindern geplante Automatisierung und Skalierung.",
        ],
        # Performance
        "WAF-PERF-010": [
            "Veraltete oder falsch dimensionierte Compute-Instanzen verschwenden Kosten und verfehlen Performance-Ziele.",
            "Fehlende SKU-Reviews führen zu Ressourcen, die weder effizient noch ausfallsicher sind.",
        ],
        "WAF-PERF-020": [
            "Stateless Workloads ohne Autoscaling versagen bei Lastspitzen oder verschwenden Ressourcen im Tief.",
            "Fehlende Skalierungsrichtlinien erzwingen manuelle Eingriffe und verlängern Ausfallzeiten.",
        ],
        "WAF-PERF-040": [
            "Datenbanken ohne Performance-Insights lassen langsame Queries und Kapazitätsengpässe unerkannt.",
            "Fehlende Monitoring-Daten erschweren gezielte Optimierungen und Kapazitätsplanung.",
        ],
        "WAF-PERF-050": [
            "Dienste ohne SLOs haben keine messbare Zuverlässigkeitsvereinbarung und verschleiern Auswirkungen auf Benutzer.",
            "Fehlende Fehlerbudgets erlauben es, wiederkehrende Instabilität zu akzeptieren, ohne Konsequenzen zu ziehen.",
        ],
        "WAF-PERF-060": [
            "Workloads ohne Lastverteilung werden bei Knotenausfall oder Spitzenlast unverhältnismäßig beeinträchtigt.",
            "Fehlende Load-Balancer-Konfigurationen führen zu Single Points of Failure.",
        ],
        "WAF-PERF-080": [
            "Spiky Workloads auf langsam startenden Ressourcen erleiden Kaltstart-Latenzen und schlechte Benutzererfahrung.",
            "Fehlende serverlose oder auto-skalierende Optionen führen zu Over-Provisioning in Ruhephasen.",
        ],
        "WAF-PERF-090": [
            "Langsame oder überdimensionierte Speicher verlängern Antwortzeiten und erhöhen Kosten.",
            "Fehlende Speicher-Tiering-Strategien verhindern kostengünstige Langzeitarchivierung.",
        ],
        # Reliability
        "WAF-REL-010": [
            "Workloads ohne dokumentierte SLOs können Auswirkungen auf Benutzer nicht messen oder kommunizieren.",
            "Fehlende Verfügbarkeitsziele führen zu uneinheitlichen Erwartungen zwischen Teams und Stakeholdern.",
        ],
        "WAF-REL-020": [
            "Dienste ohne Health-Checks werden von Load-Balancern nicht als ausgefallen erkannt und erhalten weiter Traffic.",
            "Fehlende Endpoints zur Zustandsprüfung verzögern die Erkennung von Teilausfällen.",
        ],
        "WAF-REL-030": [
            "Single-AZ-Deployments werden bei Zonen-Ausfällen vollständig unerreichbar.",
            "Fehlende Multi-AZ-Strategien verletzen Verfügbarkeitsanforderungen kritischer Workloads.",
        ],
        "WAF-REL-040": [
            "Datenbanken ohne Backups oder mit zu kurzer Aufbewahrung können bei Korruption nicht wiederhergestellt werden.",
            "Fehlende Point-in-Time-Recovery verlängert die Recovery Time bei logischen Fehlern erheblich.",
        ],
        "WAF-REL-050": [
            "Unbegrenzte Timeouts und Retries kaskadieren Fehler in Downstream-Systeme und verlängern Ausfälle.",
            "Fehlende Circuit-Breaker lassen Workloads bei Downstream-Problemen in Dauerfehlerzustände verfallen.",
        ],
        "WAF-REL-060": [
            "Fehlende Incident-Response-Pläne führen zu panischen Ad-hoc-Reaktionen und längeren MTTR.",
            "Unklare Eskalationswege verzögern die Einbindung der richtigen Experten.",
        ],
        "WAF-REL-070": [
            "Kritische Workloads ohne Disaster-Recovery-Plan können bei Regionenausfall lange unerreichbar bleiben.",
            "Fehlende Failover-Mechanismen verhindern die Wiederherstellung im sekundären Standort.",
        ],
        "WAF-REL-080": [
            "Unvollständige Abhängigkeitsinventare erschweren Impact-Analysen und Notfallplanung.",
            "Externe Abhängigkeiten ohne Dokumentation werden im Incident unterschätzt oder übersehen.",
        ],
        "WAF-REL-090": [
            "Ungetestete Workloads überraschen im echten Ausfall, da bekannte Schwachstellen nicht geprobt wurden.",
            "Fehlende Chaos-Experimente verhindern das gezielte Erkennen von Resilienzlücken.",
        ],
        "WAF-REL-100": [
            "Nicht erfasste Zuverlässigkeitsrisiken werden systematisch ignoriert und verschärfen sich im Betrieb.",
            "Fehlende Debt-Register verhindern die geplante Ablösung bekannter Schwachstellen.",
        ],
        # Sovereign
        "WAF-SOV-040": [
            "Observability-Daten außerhalb genehmigter Regionen können Datenschutz- und Souveränitätsanforderungen verletzen.",
            "Fehlende Datenstandortkontrolle für Logs und Metriken erschwert Audit und regulatorische Nachweise.",
        ],
        "WAF-SOV-060": [
            "Dauerhafte oder weitreichende privilegierte Rollen erhöhen das Insider-Risiko und den Schaden bei Kompromittierung.",
            "Fehlende Zeitbegrenzung für Admin-Zugriffe verhindert effektive Least-Privilege-Prüfungen.",
        ],
        "WAF-SOV-070": [
            "Notfallzugriffsverfahren ohne Dokumentation führen zu unautorisierten Break-Glass-Aktionen im Ernstfall.",
            "Fehlende Break-Glass-Prozesse verlängern die Wiederherstellungszeit bei schwerwiegenden Incidents.",
        ],
        "WAF-SOV-080": [
            "Unvollständige Subprozessor-Inventare verletzen Auftragsverarbeiter-Transparenzpflichten.",
            "Fehlende Abhängigkeitsbewertungen erschweren Exit-Management und Notfallplanung.",
        ],
        "WAF-SOV-090": [
            "Offenes Outbound-Traffic ermöglicht Datenexfiltration und Command-and-Control-Kommunikation.",
            "Fehlende Default-Deny-Netzwerkregeln lassen Angreifer ungehindert externe Dienste erreichen.",
        ],
        "WAF-SOV-100": [
            "Fehlende Exit-Pläne führen zu Daten-Lock-in und verhinderten Cloud-Wechseln.",
            "Undokumentierte Exportverfahren verlängern die Migration und erhöhen regulatorische Risiken.",
        ],
        # Sustainability
        "WAF-SUS-020": [
            "Energieineffiziente Prozessoren erhöhen CO₂-Fußabdruck und Betriebskosten ohne Mehrwert.",
            "Veraltete Instanzfamilien nutzen Hardware nicht optimal aus und verschwenden Strom.",
        ],
        "WAF-SUS-050": [
            "Unstrukturierte Speicherlebenszyklen lassen Daten auf teuren, energieintensiven Tiers verbleiben.",
            "Fehlende Tiering-Strategien verhindern die automatische Migration weniger genutzter Daten.",
        ],
        "WAF-SUS-060": [
            "Batch-Jobs ohne flexible Zeitfenster verbrauchen Spitzenlastkapazitäten und erneuerbare Energiepotenziale.",
            "Fehlende Spot- oder Scheduler-Optimierung führt zu teurer und klimaintensiver Verarbeitung.",
        ],
        "WAF-SUS-070": [
            "Software, die Energieeffizienz nicht berücksichtigt, verbraucht überproportional Ressourcen.",
            "Ineffiziente Algorithmen oder Polling-Muster verschwenden CPU-Zyklen und erhöhen den CO₂-Ausstoß.",
        ],
        "WAF-SUS-080": [
            "Unnötige Datenübertragungen über Regionen hinweg erhöhen Netzwerkkosten und Emissionen.",
            "Fehlende Datenlokalitätsstrategien verschwenden Bandbreite und verlangsamen Workloads.",
        ],
        "WAF-SUS-090": [
            "Fehlende Nachhaltigkeitsberichterstattung verhindert ESG-Transparenz und regulatorische Compliance.",
            "Unvollständige CO₂-Daten erschweren die Definition und Überwachung von Reduktionszielen.",
        ],
        "WAF-SUS-100": [
            "Undokumentierte Nachhaltigkeitsschulden verhindern gezielte Optimierungen und Budgetfreigaben.",
            "Fehlende Priorisierung von Green-Debt-Items lässt ineffiziente Workloads unverändert laufen.",
        ],
    },
    "en": {
        # Agentic
        "WAF-AGN-010": [
            "Non-identifiable agents cannot be traced or held accountable for their actions.",
            "Missing agent authentication enables identity spoofing and non-attributable changes.",
        ],
        "WAF-AGN-020": [
            "Overly broad tool permissions allow agents to perform destructive or unauthorized operations.",
            "Missing permission boundaries at the tool level enable privilege escalation in automated workflows.",
        ],
        "WAF-AGN-030": [
            "Opaque agent decisions prevent root-cause analysis and regulatory audits.",
            "Missing reasoning chains make it impossible to demonstrate compliance with business rules.",
        ],
        "WAF-AGN-040": [
            "Inconsistent memory management leads to conflicting decisions and data inconsistencies.",
            "Uncontrolled state persistence may leak sensitive contexts across sessions or tenants.",
        ],
        "WAF-AGN-050": [
            "Misaligned agents can optimize for the wrong objectives and cause business or safety harm.",
            "Missing verification loops let erroneous agent outputs reach production systems.",
        ],
        "WAF-AGN-060": [
            "Uncoordinated agents create race conditions, deadlocks, or duplicate critical operations.",
            "Missing orchestration governance allows agent swarms to bypass approval boundaries.",
        ],
        "WAF-AGN-070": [
            "Invisible agent activity delays detection of misuse, drift, or attacks.",
            "Without metrics, agent behavior cannot be governed or continuously improved.",
        ],
        "WAF-AGN-080": [
            "Agents making sensitive decisions without human approval can cause irreversible damage.",
            "Missing approval gates for high-impact actions violate accountability and compliance requirements.",
        ],
        "WAF-AGN-090": [
            "Unbounded agent compute consumption leads to exploding costs and increased carbon footprint.",
            "Inefficient agent architectures miss latency requirements and waste resources.",
        ],
        "WAF-AGN-100": [
            "Undocumented agent limitations accumulate technical and regulatory debt.",
            "Unknown weaknesses in agent systems expose the organization to emergent failure modes.",
        ],
        # Security
        "WAF-SEC-010": [
            "Accounts without MFA can be compromised through stolen passwords or phishing.",
            "Permanent root or user access keys enable undetected persistence and data exfiltration.",
        ],
        "WAF-SEC-020": [
            "Wildcard permissions allow all actions on all resources in principle and facilitate lateral movement.",
            "Administrator roles attached to workload principals risk unintended or malicious destruction.",
        ],
        "WAF-SEC-070": [
            "Unscanned container images frequently contain known vulnerabilities exploitable in production.",
            "Missing SBOMs and scan results complicate supply-chain audits and incident response.",
        ],
        "WAF-SEC-090": [
            "Compliance rules that are only documented and not maintained as code become outdated and ignored.",
            "Manual controls cannot be checked at scale and provide no repeatable audit evidence.",
        ],
        "WAF-SEC-100": [
            "Missing incident-response plans extend reaction times and worsen the impact of security incidents.",
            "Untested IR processes lead to wrong decisions and missed regulatory reporting obligations in a real event.",
        ],
        "WAF-SEC-110": [
            "Mutable tags allow production images to be overwritten and complicate rollbacks after incidents.",
            "Missing binary authorization lets compromised images deploy into production unnoticed.",
        ],
        # Cost
        "WAF-COST-030": [
            "Unreviewed compute resources permanently lead to over-provisioning and cloud waste.",
            "Missing rightsizing evidence complicates FinOps reviews and budget accountability.",
        ],
        "WAF-COST-040": [
            "Unlimited storage retention lets data grow unnecessarily and increases cost and deletion risk.",
            "Missing lifecycle rules prevent automatic archiving or deletion by data classification.",
        ],
        "WAF-COST-050": [
            "Architecture decisions without cost consideration lead to lock-in and unaccountable spending.",
            "Missing lock-in assessment complicates future contract negotiations and cloud migration.",
        ],
        "WAF-COST-080": [
            "High sustained load without capacity planning leads to expensive on-demand resources and budget variance.",
            "Missing reserved-instance or savings-plan documentation prevents optimization opportunities.",
        ],
        # Ops
        "WAF-OPS-010": [
            "Missing CI/CD pipelines force manual deployments and increase the risk of human error.",
            "Undocumented deployment processes lead to non-reproducible environments and longer outages.",
        ],
        "WAF-OPS-020": [
            "Manually managed infrastructure drifts from documentation and is hard to restore.",
            "Missing IaC practices prevent versioning, peer review, and disaster recovery.",
        ],
        "WAF-OPS-030": [
            "Unstructured logs and missing metrics delay troubleshooting and incident detection.",
            "Without centralized observability data, SLO breaches and security incidents cannot be correlated.",
        ],
        "WAF-OPS-040": [
            "Alerting on infrastructure instead of symptom metrics creates alert fatigue and misses customer-impacting outages.",
            "Missing action assignment on alerts prolongs time to resolution.",
        ],
        "WAF-OPS-050": [
            "Undocumented changes to production systems complicate rollbacks and audits.",
            "Missing approval gates enable unauthorized or untested deployments.",
        ],
        "WAF-OPS-060": [
            "Runbooks not linked to alerts slow response to recurring disturbances.",
            "Missing escalation instructions lead to uncoordinated ad-hoc reactions.",
        ],
        "WAF-OPS-070": [
            "Undocumented incidents prevent organizational learning and recurrence prevention.",
            "Missing post-mortems leave systemic weaknesses unrecognized and uncorrected.",
        ],
        "WAF-OPS-080": [
            "Big-bang deployments can hit all users with failures at once and complicate rollbacks.",
            "Missing canary or feature-flag mechanisms slow detection of regressive changes.",
        ],
        "WAF-OPS-090": [
            "Drift between IaC and actual infrastructure leads to shadow IT and unexpected configurations.",
            "Undetected manual changes undermine compliance and security controls.",
        ],
        "WAF-OPS-100": [
            "Undocumented manual processes accumulate operational debt and knowledge-risk.",
            "Unprioritized operational debt blocks planned automation and scaling.",
        ],
        # Performance
        "WAF-PERF-010": [
            "Outdated or wrongly sized compute instances waste cost and miss performance targets.",
            "Missing SKU reviews lead to resources that are neither efficient nor resilient.",
        ],
        "WAF-PERF-020": [
            "Stateless workloads without autoscaling fail under load spikes or waste resources in troughs.",
            "Missing scaling policies force manual intervention and extend downtime.",
        ],
        "WAF-PERF-040": [
            "Databases without performance insights let slow queries and capacity bottlenecks go unnoticed.",
            "Missing monitoring data complicates targeted optimization and capacity planning.",
        ],
        "WAF-PERF-050": [
            "Services without SLOs have no measurable reliability commitment and hide user impact.",
            "Missing error budgets allow recurring instability to be accepted without consequence.",
        ],
        "WAF-PERF-060": [
            "Workloads without load balancing are disproportionately impacted by node failure or traffic spikes.",
            "Missing load-balancer configurations create single points of failure.",
        ],
        "WAF-PERF-080": [
            "Spiky workloads on slow-starting resources suffer cold-start latency and poor user experience.",
            "Missing serverless or auto-scaling options lead to over-provisioning during idle periods.",
        ],
        "WAF-PERF-090": [
            "Slow or over-provisioned storage extends response times and increases cost.",
            "Missing storage-tiering strategies prevent cost-efficient long-term archiving.",
        ],
        # Reliability
        "WAF-REL-010": [
            "Workloads without documented SLOs cannot measure or communicate user impact.",
            "Missing availability targets lead to inconsistent expectations between teams and stakeholders.",
        ],
        "WAF-REL-020": [
            "Services without health checks are not recognized as failed by load balancers and keep receiving traffic.",
            "Missing state-check endpoints delay detection of partial outages.",
        ],
        "WAF-REL-030": [
            "Single-AZ deployments become completely unreachable during zone failures.",
            "Missing multi-AZ strategies violate availability requirements for critical workloads.",
        ],
        "WAF-REL-040": [
            "Databases without backups or with too short retention cannot be recovered from corruption.",
            "Missing point-in-time recovery significantly extends recovery time from logical errors.",
        ],
        "WAF-REL-050": [
            "Unbounded timeouts and retries cascade failures into downstream systems and extend outages.",
            "Missing circuit breakers let workloads remain in perpetual failure states when downstream breaks.",
        ],
        "WAF-REL-060": [
            "Missing incident-response plans lead to panicked ad-hoc reactions and longer MTTR.",
            "Unclear escalation paths delay involving the right experts.",
        ],
        "WAF-REL-070": [
            "Critical workloads without disaster-recovery plans may remain unreachable for a long time during regional outages.",
            "Missing failover mechanisms prevent recovery in the secondary location.",
        ],
        "WAF-REL-080": [
            "Incomplete dependency inventories complicate impact analysis and emergency planning.",
            "External dependencies without documentation are underestimated or overlooked during incidents.",
        ],
        "WAF-REL-090": [
            "Untested workloads surprise teams during real outages because known weaknesses were never exercised.",
            "Missing chaos experiments prevent targeted discovery of resilience gaps.",
        ],
        "WAF-REL-100": [
            "Unrecorded reliability risks are systematically ignored and worsen in operation.",
            "Missing debt registers prevent planned retirement of known weaknesses.",
        ],
        # Sovereign
        "WAF-SOV-040": [
            "Observability data outside approved regions can violate data-protection and sovereignty requirements.",
            "Missing data-location control for logs and metrics complicates audits and regulatory evidence.",
        ],
        "WAF-SOV-060": [
            "Permanent or far-reaching privileged roles increase insider risk and damage if compromised.",
            "Missing time-boxing for admin access prevents effective least-privilege reviews.",
        ],
        "WAF-SOV-070": [
            "Emergency access procedures without documentation lead to unauthorized break-glass actions in a crisis.",
            "Missing break-glass processes extend recovery time during severe incidents.",
        ],
        "WAF-SOV-080": [
            "Incomplete sub-processor inventories violate processor transparency obligations.",
            "Missing dependency assessments complicate exit management and emergency planning.",
        ],
        "WAF-SOV-090": [
            "Open outbound traffic enables data exfiltration and command-and-control communication.",
            "Missing default-deny network rules let attackers reach external services unhindered.",
        ],
        "WAF-SOV-100": [
            "Missing exit plans lead to data lock-in and blocked cloud migrations.",
            "Undocumented export procedures extend migration time and increase regulatory risk.",
        ],
        # Sustainability
        "WAF-SUS-020": [
            "Energy-inefficient processors increase carbon footprint and operating cost without added value.",
            "Outdated instance families do not use hardware optimally and waste power.",
        ],
        "WAF-SUS-050": [
            "Unstructured storage lifecycles leave data on expensive, energy-intensive tiers.",
            "Missing tiering strategies prevent automatic migration of less-used data.",
        ],
        "WAF-SUS-060": [
            "Batch jobs without flexible time windows consume peak-load capacity and miss renewable-energy potential.",
            "Missing spot or scheduler optimization leads to expensive and carbon-intensive processing.",
        ],
        "WAF-SUS-070": [
            "Software that ignores energy efficiency consumes resources disproportionately.",
            "Inefficient algorithms or polling patterns waste CPU cycles and increase carbon emissions.",
        ],
        "WAF-SUS-080": [
            "Unnecessary data transfers across regions increase network cost and emissions.",
            "Missing data-locality strategies waste bandwidth and slow down workloads.",
        ],
        "WAF-SUS-090": [
            "Missing sustainability reporting prevents ESG transparency and regulatory compliance.",
            "Incomplete carbon data complicates defining and monitoring reduction targets.",
        ],
        "WAF-SUS-100": [
            "Undocumented sustainability debt prevents targeted optimization and budget approvals.",
            "Missing prioritization of green-debt items lets inefficient workloads run unchanged.",
        ],
    },
}

FRAMEWORKS_TO_REMOVE = [
    "Internal Governance",
    "AWS Well-Architected Framework",
    "Azure Well-Architected Framework",
    "Google Cloud Architecture Framework",
]


def has_placeholder(threats):
    return any(t in PLACEHOLDERS for t in threats)


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    cid = data["id"]
    original = data.copy()

    # Fix threats (YAML controls are always English)
    threats = data.get("threat") or []
    if has_placeholder(threats):
        if cid in SPECIFIC_THREATS["en"]:
            data["threat"] = SPECIFIC_THREATS["en"][cid]
        else:
            cleaned = [t for t in threats if t not in PLACEHOLDERS]
            data["threat"] = cleaned if cleaned else threats

    # Tighten framework mappings
    if "regulatory_mapping" in data and data["regulatory_mapping"]:
        data["regulatory_mapping"] = [
            m for m in data["regulatory_mapping"]
            if m.get("framework") not in FRAMEWORKS_TO_REMOVE
        ]

    if data != original:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True, width=120)
        return True
    return False


def main():
    for lang, repo_root in REPOS.items():
        updated = 0
        for path in sorted(Path(repo_root).glob("modules/controls/controls/WAF-*.yml")):
            if process_file(path):
                updated += 1
        print(f"Updated {updated} controls in {repo_root} ({lang})")


if __name__ == "__main__":
    main()
