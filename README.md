# WAF++ Framework Dokumentation

[![Build Status](https://github.com/WAF2p/waf2p.github.io/actions/workflows/jekyll-gh-pages.yml/badge.svg)](https://github.com/WAF2p/waf2p.github.io/actions/workflows/jekyll-gh-pages.yml)

Dies ist die Antora-Dokumentationskomponente für das **WAF++** (Well-Architected Framework++) Projekt - ein community-geführtes, cloud-agnostisches Framework für sichere und nachhaltige Cloud-Architekturen.

Die Dokumentation wird in die Haupt-Website unter https://waf2p.dev/docs/wafpp/1.0/ eingebunden.

---

## 👥 Für Inhalts-Beitragende

### Wo finde ich die Dokumentationsdateien?

Alle Dokumentationsinhalte befinden sich im Verzeichnis:
```
modules/ROOT/pages/
```

### Wie bearbeite ich Inhalte?

1. **Datei öffnen**: Öffne die entsprechende `.adoc`-Datei in `modules/ROOT/pages/`
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

Die Vorschau erfolgt über die Website-Repository-Build. Alternativ kannst du AsciiDoc-Editoren nutzen:
- Online: https://asciidoclive.com/
- VS Code: Extension "AsciiDoc" installieren

### Weitere Informationen

Detaillierte technische Informationen findest du in der Datei `AGENTS.md` in diesem Repository.

---

## 🔧 Für Repository-Entwickler

### Antora-Komponentenstruktur

Dieses Repository ist als **Antora-Komponente** strukturiert:

```
framework/
├── antora.yml                    # Komponentendeskriptor (name: wafpp, version: 1.0)
├── modules/
│   └── ROOT/
│       ├── nav.adoc              # Navigationsstruktur
│       └── pages/                # Alle Dokumentationsseiten (.adoc)
│           ├── index.adoc        # Hauptseite
│           ├── architektur/      # Architektur-Seiten
│           ├── best-practises/   # Best Practices
│           ├── governance-community/
│           ├── pillars/          # 7 Säulen (Security, Costs, etc.)
│           ├── roadmap/
│           └── resources/
└── AGENTS.md                     # Entwickler-Guidelines
```

### Integration mit Website-Repository

Die Dokumentation wird **nicht direkt** in diesem Repository gebaut, sondern:

1. Das **Website-Repository** (`waf2p.github.io`) nutzt Antora
2. Antora liest dieses Repository als **Content-Quelle**
3. Antora generiert HTML und integriert es in die Jekyll-Website
4. Ausgabe erfolgt unter: `https://waf2p.dev/docs/wafpp/1.0/`

### Antora-Komponentenkonfiguration

Die `antora.yml`-Datei definiert diese Komponente:

```yaml
name: wafpp                # Komponenten-Name (wird Teil der URL)
version: '1.0'             # Version (wird Teil der URL)
title: WAF++ Framework     # Anzeigename
start_page: ROOT:index.adoc  # Startseite
nav:
  - modules/ROOT/nav.adoc  # Navigationsdatei
```

**URL-Struktur**: `/docs/<name>/<version>/<page-path>`  
**Beispiel**: `/docs/wafpp/1.0/pillars/security.html`

### Build-Prozess

Der Build erfolgt im **Website-Repository**:

```bash
# Im Website-Repository
task docs:build:local   # Baut Dokumentation aus lokalem Framework-Repo
task docs:build         # Baut Dokumentation aus GitHub
task site:build         # Baut komplette Site (Jekyll + Antora)
```

Die Antora-Playbooks im Website-Repository (`antora-playbook.yml`, `antora-playbook-local.yml`) referenzieren dieses Repository als Content-Quelle.

### Cross-References und Links

Interne Links zwischen Seiten nutzen die `xref:`-Syntax:

```asciidoc
xref:pillars/security.adoc[Security-Säule]
xref:index.adoc[Zurück zur Hauptseite]
xref:architektur/index.adoc#abschnitt[Spezifischer Abschnitt]
```

**Wichtig**: Keine relativen Pfade wie `../` verwenden - Antora löst xrefs automatisch auf.

### Validierung

AsciiDoc-Syntax validieren (benötigt asciidoctor):

```bash
# Installation
gem install asciidoctor

# Validierung einzelner Datei
asciidoctor -o /dev/null modules/ROOT/pages/index.adoc

# Validierung aller Dateien
find modules/ROOT/pages -name "*.adoc" -exec asciidoctor -o /dev/null {} \;
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

- **Hauptseite**: https://waf2p.dev/docs/wafpp/1.0/
- **Beispiel-Seite**: https://waf2p.dev/docs/wafpp/1.0/pillars/security.html

### Entwickler-Guidelines

Detaillierte technische Standards und Best Practices findest du in:
- **`AGENTS.md`** in diesem Repository - Antora-spezifische Guidelines
- **`AGENTS.md`** im Website-Repository - Gesamtarchitektur und Build-Prozess

---

## 📁 Projektstruktur

```
framework/
├── antora.yml                              # Antora-Komponentendeskriptor
├── modules/
│   └── ROOT/
│       ├── nav.adoc                        # Hauptnavigation
│       └── pages/
│           ├── index.adoc                  # Hauptseite
│           ├── architektur/
│           │   └── index.adoc
│           ├── best-practises/
│           │   └── index.adoc
│           ├── governance-community/
│           │   └── index.adoc
│           ├── pillars/
│           │   ├── costs.adoc
│           │   ├── efficiency.adoc
│           │   ├── excellence.adoc
│           │   ├── governance.adoc
│           │   ├── index.adoc
│           │   ├── reliability.adoc
│           │   ├── security.adoc
│           │   └── sustainability.adoc
│           ├── roadmap/
│           │   ├── 2026.adoc
│           │   └── index.adoc
│           └── resources/
│               ├── index.adoc
│               └── wording.adoc
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
