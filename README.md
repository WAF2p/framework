# WAF++ Framework Dokumentation

[![Build Status](https://github.com/WAF2p/waf2p.github.io/actions/workflows/jekyll-gh-pages.yml/badge.svg)](https://github.com/WAF2p/waf2p.github.io/actions/workflows/jekyll-gh-pages.yml)

Dies ist die Antora-Dokumentationskomponente für das **WAF++** (Well-Architected Framework++) Projekt – ein community-geführtes, cloud-agnostisches Framework für souveräne, sichere und nachhaltige Cloud-Architekturen.

Die Dokumentation wird in die Haupt-Website unter https://waf2p.dev/docs/wafpp/1.0.1-de/ eingebunden.

---

## 👥 Für Inhalts-Beitragende

### Wo finde ich die Dokumentationsdateien?

Die Inhalte sind modular nach Säulen organisiert:

```
modules/
├── ROOT/pages/                 # Rahmeninhalt: Startseite, Roadmap, Ressourcen
├── pillar-security/pages/      # Security-Säule
├── pillar-cost/pages/          # Cost-Optimization-Säule
├── pillar-efficiancy/pages/    # Performance-Efficiency-Säule
├── pillar-reliability/pages/   # Reliability-Säule
├── pillar-excellence/pages/    # Operational-Excellence-Säule
├── pillar-sustainability/pages/# Sustainability-Säule
├── pillar-sovereign/pages/     # Sovereign-Säule
├── pillar-agentic/pages/       # Agentic-Säule
└── controls/pages/             # Maschinenlesbarer Controls-Katalog
```

Jede Säule hat ihre eigene Navigation (`nav.adoc`) und Seiten (`pages/`).

### Wie bearbeite ich Inhalte?

1. **Datei öffnen**: Öffne die entsprechende `.adoc`-Datei im passenden Modul unter `modules/<modul>/pages/`
2. **Bearbeiten**: Nutze AsciiDoc-Syntax (ähnlich wie Markdown)
3. **Speichern**: Speichere die Änderungen
4. **Commit**: Erstelle einen Commit mit aussagekräftiger Beschreibung

### Wichtige AsciiDoc-Syntax

```asciidoc
= Hauptüberschrift (Seitentitel)

== Überschrift Ebene 2

=== Überschrift Ebene 3

**Fettgedruckt**, _kursiv_

* Aufzählungsliste
* Zweiter Punkt

xref:andere-seite.adoc[Link zu anderer Seite]

image::bilder/diagramm.png[Beschreibung]
```

### Vorschau der Änderungen

Die Vorschau erfolgt über den Build des Website-Repositories. Alternativ kannst du AsciiDoc-Editoren nutzen:
- Online: https://asciidoclive.com/
- VS Code: Extension "AsciiDoc" installieren

### Weitere Informationen

Detaillierte technische Informationen findest du in der Datei `AGENTS.md` in diesem Repository.

---

## 🔧 Für Repository-Entwickler

### Antora-Komponentenstruktur

Dieses Repository ist als **Antora-Dokumentationskomponente** strukturiert:

```
framework/
├── antora.yml                    # Komponentendeskriptor
├── modules/
│   ├── ROOT/
│   │   ├── nav.adoc              # Top-Level-Navigation
│   │   └── pages/                # Rahmeninhalt
│   ├── pillar-security/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-cost/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-efficiancy/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-reliability/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-excellence/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-sustainability/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-sovereign/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-agentic/
│   │   ├── nav.adoc
│   │   └── pages/
│   └── controls/
│       ├── nav.adoc
│       ├── pages/
│       └── controls/             # YAML-Controls
└── AGENTS.md                     # Entwickler-Guidelines
```

### Integration mit Website-Repository

Die Dokumentation wird **nicht direkt** in diesem Repository gebaut, sondern:

1. Das **Website-Repository** (`waf2p.github.io`) nutzt Antora
2. Antora liest dieses Repository als **Content-Quelle**
3. Antora generiert HTML und integriert es in die Jekyll-Website
4. Ausgabe erfolgt unter: `https://waf2p.dev/docs/wafpp/1.0.1-de/`

### Antora-Komponentenkonfiguration

Die `antora.yml`-Datei definiert diese Komponente:

```yaml
name: wafpp
version: '1.0.1-de'
display_version: '1.0.1 (Deutsch)'
prerelease: false
title: WAF++
start_page: ROOT:index.adoc
nav:
  - modules/ROOT/nav.adoc
  - modules/pillar-security/nav.adoc
  - modules/pillar-cost/nav.adoc
  - modules/pillar-efficiancy/nav.adoc
  - modules/pillar-reliability/nav.adoc
  - modules/pillar-excellence/nav.adoc
  - modules/pillar-sustainability/nav.adoc
  - modules/pillar-sovereign/nav.adoc
  - modules/pillar-agentic/nav.adoc
  - modules/controls/nav.adoc
```

**URL-Struktur**: `/docs/<name>/<version>/<module>/<page-path>`  
**Beispiel**: `/docs/wafpp/1.0.1-de/pillar-security/index.html`

### Build-Prozess

Der Build erfolgt im **Website-Repository**:

```bash
# Im Website-Repository
npx antora antora-playbook-local.yml   # Lokale Quellen
task docs:build:local                  # Taskfile-Shortcut
task site:build                        # Komplette Site
```

Die Antora-Playbooks im Website-Repository referenzieren dieses Repository als Content-Quelle.

### Cross-References und Links

Interne Links zwischen Seiten nutzen die `xref:`-Syntax. Innerhalb desselben Moduls ohne Modul-Präfix, zwischen Modulen mit Modul-Präfix:

```asciidoc
xref:index.adoc[Startseite im aktuellen Modul]
xref:pillar-security:controls.adoc[Security-Controls]
xref:pillar-agentic:index.adoc[Agentic-Säule]
xref:controls:catalog.adoc[Controls-Katalog]
```

**Wichtig**: Keine relativen Pfade wie `../` verwenden – Antora löst `xref:` automatisch auf.

### Validierung

AsciiDoc-Syntax validieren (benötigt asciidoctor):

```bash
# Installation
gem install asciidoctor

# Validierung einzelner Datei
asciidoctor -o /dev/null modules/ROOT/pages/index.adoc

# Validierung aller Dateien
find modules -name "*.adoc" -exec asciidoctor -o /dev/null {} \;
```

### GitHub Actions Integration

Die CI/CD-Pipeline im Website-Repository:

1. Klont dieses Framework-Repository
2. Führt Antora-Build aus
3. Kombiniert Antora-Output mit Jekyll-Site
4. Deployed zu GitHub Pages

Workflow-Datei: `.github/workflows/jekyll-gh-pages.yml` im Website-Repository

### Deployment-URLs

Nach erfolgreichem Deployment:

- **Hauptseite**: https://waf2p.dev/docs/wafpp/1.0.1-de/
- **Beispiel-Seite**: https://waf2p.dev/docs/wafpp/1.0.1-de/pillar-security/index.html

### Entwickler-Guidelines

Detaillierte technische Standards und Best Practices findest du in:
- **`AGENTS.md`** in diesem Repository – Antora-spezifische Guidelines
- **`AGENTS.md`** im Website-Repository – Gesamtarchitektur und Build-Prozess

---

## 📁 Projektstruktur

```
framework/
├── antora.yml                              # Antora-Komponentendeskriptor
├── modules/
│   ├── ROOT/
│   │   ├── nav.adoc                        # Top-Level-Navigation
│   │   └── pages/
│   │       ├── index.adoc                  # Hauptseite
│   │       ├── pillars/
│   │       │   └── index.adoc              # Landingpage der 8 Säulen
│   │       ├── architecture/
│   │       ├── governance-community/
│   │       ├── roadmap/
│   │       └── resources/
│   ├── pillar-security/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-cost/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-efficiancy/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-reliability/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-excellence/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-sustainability/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-sovereign/
│   │   ├── nav.adoc
│   │   └── pages/
│   ├── pillar-agentic/
│   │   ├── nav.adoc
│   │   └── pages/
│   └── controls/
│       ├── nav.adoc
│       ├── pages/
│       └── controls/                       # YAML-Controls
├── AGENTS.md                               # Entwickler-Guidelines
└── README.md                               # Diese Datei
```

---

## 🔗 Ressourcen

- **Antora-Dokumentation**: https://docs.antora.org/
- **AsciiDoc-Syntax**: https://docs.asciidoctor.org/asciidoc/latest/
- **Website-Repository**: https://github.com/WAF2p/waf2p.github.io
- **Live-Site**: https://waf2p.dev/

---

## 🤝 Beitragen

Beiträge sind willkommen! Bitte:

1. Erstelle einen Feature-Branch
2. Mache deine Änderungen in den `.adoc`-Dateien
3. Teste lokal (via Website-Repository Build)
4. Erstelle einen Pull Request mit aussagekräftiger Beschreibung

Bei Fragen zur Struktur oder zum Build-Prozess siehe `AGENTS.md`.

---

**WAF++ Community** | https://waf2p.dev/
