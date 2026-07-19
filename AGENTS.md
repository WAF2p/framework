# Agent-Guidelines für das WAF++ Framework Repository

Dieses Repository enthält die **WAF++** (Well-Architected Framework++) Dokumentation – ein community-getriebenes Framework für souveränes, cloud-agnostisches Cloud-Engineering. Die Dokumentation wird mit **Antora**, einem Multi-Repository-Dokumentationsgenerator, aus AsciiDoc-Dateien erzeugt.

## Projektübersicht

**Repository**: https://github.com/WAF2p/framework.git  
**Sprache**: Deutsch  
**Typ**: Antora-Dokumentationskomponente  
**Build-System**: Antora 3.1.x  
**Inhaltsschwerpunkte**: Cloud-Architektur, Governance, Security, Cost Optimization, Reliability, Sustainability, Sovereign, Agentic  
**Ausgabeformat**: Statisches HTML durch Antora

### Verzeichnisstruktur (Antora-Standard)

```
.
├── antora.yml                    # Komponentendeskriptor
└── modules/
    ├── ROOT/                     # Rahmeninhalt
    │   ├── nav.adoc              # Top-Level-Navigation
    │   ├── pages/                # Dokumentationsseiten (AsciiDoc)
    │   │   ├── index.adoc        # Komponenten-Startseite
    │   │   ├── pillars/
    │   │   ├── architecture/
    │   │   ├── governance-community/
    │   │   ├── roadmap/
    │   │   └── resources/
    │   └── images/               # Bilder und Assets
    ├── pillar-security/          # Security-Säule
    │   ├── nav.adoc
    │   └── pages/
    ├── pillar-cost/              # Cost-Optimization-Säule
    │   ├── nav.adoc
    │   └── pages/
    ├── pillar-efficiancy/        # Performance-Efficiency-Säule
    │   ├── nav.adoc
    │   └── pages/
    ├── pillar-reliability/       # Reliability-Säule
    │   ├── nav.adoc
    │   └── pages/
    ├── pillar-excellence/        # Operational-Excellence-Säule
    │   ├── nav.adoc
    │   └── pages/
    ├── pillar-sustainability/    # Sustainability-Säule
    │   ├── nav.adoc
    │   └── pages/
    ├── pillar-sovereign/         # Sovereign-Säule
    │   ├── nav.adoc
    │   └── pages/
    ├── pillar-agentic/           # Agentic-Säule
    │   ├── nav.adoc
    │   └── pages/
    └── controls/                 # Controls-Katalog
        ├── nav.adoc
        ├── pages/
        └── controls/             # YAML-Controls
```

## Build-/Test-Kommandos

Dieses Repository wird von Antora als Dokumentationskomponente konsumiert. Der Build findet im Website-Repository (`waf2p.github.io`) statt, nicht hier direkt.

### Lokale Entwicklung

**Hinweis**: Dieses Repository baut nicht standalone. Es wird von Antora aus dem Website-Repository bezogen. Inhalte lassen sich aber lokal prüfen.

**AsciiDoc-Dateien anzeigen**:
```bash
# Mit asciidoctor (falls installiert)
asciidoctor modules/ROOT/pages/index.adoc -o /tmp/preview.html
open /tmp/preview.html

# Oder online: https://asciidoclive.com/
```

**Validierung**:
```bash
# Alle AsciiDoc-Dateien finden
find modules -name "*.adoc" -type f

# Navigation prüfen
cat modules/ROOT/nav.adoc
cat modules/pillar-security/nav.adoc

# Verwaiste oder unvollständige xrefs finden
grep -R "xref:\.\." modules --include="*.adoc"
```

### Antora-Build

Die komplette Dokumentation inklusive dieser Komponente baut im Website-Repository:

```bash
# Website-Repository verwenden
cd /path/to/waf2p.github.io

# Build mit lokalem Dateisystem-Quellverzeichnis
npx antora antora-playbook-local.yml

# Oder Taskfile
task docs:build:local
```

### Einzelne Dateien prüfen

```bash
# Datei lesen
cat modules/pillar-security/pages/index.adoc

# Dokumentstruktur prüfen
head -20 modules/pillar-security/pages/index.adoc
```

## Inhaltsstil-Guidelines

### Sprache & Ton

- **Hauptsprache**: Deutsch – alle Dokumentationsinhalte müssen auf Deutsch sein
- **Ton**: Professionell, zugänglich, community-orientiert
- **Zielgruppe**: Architekten, Plattform-Teams, Security-/Compliance-Verantwortliche
- **Stil**: Klar, strukturiert, handlungsorientiert

### AsciiDoc-Struktur

**Seitenattribute** (oben in jeder `.adoc`-Datei):
```asciidoc
= Seitentitel
:description: Kurze Seitenbeschreibung

Inhalt beginnt hier...
```

**Abschnittsstruktur**:
- `= Titel` für den Seitentitel (H1, nur einmal pro Seite)
- `== Abschnitt` für Hauptabschnitte (H2)
- `=== Unterabschnitt` für Unterabschnitte (H3)
- `*fett*` für Hervorhebungen von Schlüsselbegriffen
- `* ` für ungeordnete Listen
- `NOTE:`, `TIP:`, `IMPORTANT:`, `WARNING:`, `CAUTION:` für Callouts

**Link-Stil**:
```asciidoc
# Interne Cross-References innerhalb desselben Moduls
xref:controls.adoc[Controls]

# Cross-References zwischen Modulen
xref:pillar-security:controls.adoc[Security-Controls]
xref:pillar-agentic:index.adoc[Agentic-Säule]
xref:controls:catalog.adoc[Controls-Katalog]

# Externe Links
https://example.com[Linktext^]

# Links mit Attributen
link:https://example.com[Linktext,window=_blank]
```

**Beispiel-AsciiDoc-Seite**:
```asciidoc
= Security-Säule
:description: Sicherheit und Compliance im Cloud-Umfeld

== Worum geht es?

Die Security-Säule adressiert...

=== Was wird gemacht?

* Punkt 1
* Punkt 2

NOTE: Wichtiger Hinweis für Leser

== Weitere Informationen

Siehe auch xref:controls.adoc[Controls].
```

### Inhaltsrichtlinien für Säulen

Jede Säule sollte folgende Struktur verwenden:

1. **Definition & Scope** – Was wird abgedeckt?
2. **Prinzipien** – 5-7 Leitprinzipien
3. **Controls** – Messbare Controls mit ID, Severity, Automatisierbarkeit
4. **Best Practices** – Umsetzungshilfen
5. **Maturity Model** – Reifegradstufen und Selbstbewertung
6. **Evidence & Audit** – Nachweistypen und Audit-Hinweise

### Naming Conventions

**Verzeichnisse**:
- Kleinbuchstaben mit Bindestrichen: `best-practices/`, `governance-community/`
- Deutsche Begriffe bevorzugt, wo sinnvoll: `architektur/` statt `architecture/`
- Säulen-Module folgen dem Schema `pillar-<name>`

**Dateien**:
- Hauptdateien: `index.adoc`
- Alle Seiten müssen `.adoc` verwenden (kein Markdown)
- YAML-Controls im Controls-Modul: `WAF-<PILLAR>-<NNN>.yml`

**Titel**:
- Säulen: "<Name> (Säule: <Name>)" oder "Säule <Nummer> – <Name>"
- Controls: "WAF-<PILLAR>-<NNN> – <Titel>"

### Navigationsstruktur

Jedes Modul hat eine eigene `nav.adoc`. Die Top-Level-Navigation in `modules/ROOT/nav.adoc` verlinkt auf die Säulen-Startseiten:

```asciidoc
* xref:index.adoc[Startseite]
* xref:pillars/index.adoc[Die 8 Säulen]
** xref:pillar-security:index.adoc[Security]
** xref:pillar-cost:index.adoc[Cost Optimization]
** xref:pillar-efficiancy:index.adoc[Performance Efficiency]
** xref:pillar-reliability:index.adoc[Reliability]
** xref:pillar-excellence:index.adoc[Operational Excellence]
** xref:pillar-sustainability:index.adoc[Sustainability]
** xref:pillar-sovereign:index.adoc[Sovereign]
** xref:pillar-agentic:index.adoc[Agentic]
* xref:controls:index.adoc[Controls]
```

Innerhalb einer Säule werden Links ohne Modul-Präfix geschrieben:
```asciidoc
** xref:controls.adoc[Controls (WAF-SEC)]
*** xref:controls/WAF-SEC-010.adoc[WAF-SEC-010]
```

### Terminologie

**Wichtige Begriffe** (konsistent verwenden):
- **Säule** = Pillar
- **Control** = Control (fachlicher Begriff beibehalten)
- **Reifegrad/Reifegradmodell** = Maturity/Maturity Model
- **Governance** = Governance (englisch beibehalten)
- **Cloud-agnostisch** = Cloud-agnostic
- **Souverän/Souveränität** = Sovereign/Sovereignty
- **Agentic** = Agentic (fachlicher Begriff)

## Git Workflow

### Commit-Message-Format

Conventional-Commits-Stil auf Deutsch:

```
<type>: <beschreibung>

[optionaler body]

[optionaler footer]
```

**Typen**:
- `feat`: Neue Inhalte oder Features
- `fix`: Korrekturen bestehender Inhalte
- `docs`: Dokumentationsstruktur-Änderungen
- `style`: Formatierung, Tippfehler (kein Inhaltswechsel)
- `refactor`: Inhaltliche Neuorganisation
- `chore`: Wartungstasks

**Beispiele**:
```
feat: Agentic-Säule mit Maturity-Modell ergänzen

fix: Tippfehler in Security-Controls korrigieren

docs: Navigation auf 8 Säulen aktualisieren
```

### Branch-Strategie

- `main` – stabil, produktionsbereit
- `feature/*` – neue Inhalte oder Abschnitte
- `fix/*` – Korrekturen und Verbesserungen

## Content-Quality-Checkliste

Vor dem Commit neuer Inhalte:

- [ ] Inhalt im AsciiDoc-Format (`.adoc`-Endung)
- [ ] Inhalt auf Deutsch
- [ ] Seitentitel mit `= Titel` gesetzt
- [ ] Struktur folgt dem Säulen-Template (falls zutreffend)
- [ ] Cross-References verwenden `xref:`-Syntax mit korrekten Pfaden
- [ ] Keine relativen Pfade (`../`) in xrefs
- [ ] Keine verwaisten Dateien oder defekten internen Verweise
- [ ] Navigation in `modules/<pillar>/nav.adoc` aktualisiert
- [ ] Terminologie ist mit dem Projektsglossar konsistent
- [ ] AsciiDoc-Syntax ist gültig

## Antora-spezifische Hinweise

### Komponentendeskriptor

Die `antora.yml` definiert diese Dokumentationskomponente:

```yaml
name: wafpp
title: WAF++
version: '1.0.1-de'
display_version: '1.0.1 (Deutsch)'
prerelease: false
start_page: ROOT:index.adoc
asciidoc:
  attributes:
    page-lang: de
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

**Nur in Absprache mit den Website-Repository-Maintainern ändern**.

### Cross-References

Für interne Links immer Antora-`xref`-Syntax verwenden:

```asciidoc
# Innerhalb desselben Moduls
xref:controls.adoc[Linktext]

# Mit Anker
xref:controls.adoc#WAF-SEC-010[Linktext]

# In ein anderes Modul
xref:pillar-security:controls.adoc[Security-Controls]
xref:pillar-agentic:index.adoc[Agentic-Säule]

# Mit Anker in anderem Modul
xref:pillar-cost:controls.adoc#WAF-COST-010[Linktext]
```

### Bilder und Assets

Bilder pro Modul im jeweiligen `images/`-Verzeichnis ablegen:

```asciidoc
image::diagram.png[Alternativer Text]
```

Antora löst die Pfade beim Build automatisch auf.

## Community-Guidelines

Dieses Projekt folgt einem **CNCF-inspirierten Governance-Modell**:

- **Technical Steering Committee (TSC)**: Technische Ausrichtung
- **Maintainer**: Repository-Qualität und Konsistenz
- **Contributors**: Issues, PRs, Vorschläge
- **User Advisory Group**: Praktisches Feedback

**Beitragen**:
1. Bestehende Issues auf GitHub prüfen
2. Vor großen Änderungen ein Issue zur Diskussion öffnen
3. Stilrichtlinien in diesem Dokument befolgen
4. PRs mit klaren Beschreibungen einreichen
5. An Community-Diskussionen teilnehmen

## Besondere Hinweise

### Antora-Integration

Dieses Repository wird als **Dokumentationskomponente** von Antora konsumiert:

- **Website-Repo**: https://github.com/WAF2p/waf2p.github.io
- **Build-System**: Antora generiert statisches HTML aus diesem Inhalt
- **URL-Struktur**: `https://waf2p.dev/docs/wafpp/1.0.1-de/<module>/<page-path>`
- **Version**: Aktuell `1.0.1-de` (in `antora.yml` definiert)

### AsciiDoc vs Markdown

- **AsciiDoc** (`.adoc`) verwenden, kein Markdown
- AsciiDoc bietet bessere semantische Auszeichnung für technische Dokumentation
- Antora erfordert AsciiDoc
- Referenz: https://docs.asciidoctor.org/asciidoc/latest/

### Kein Standalone-Build

Dieses Repository **baut nicht eigenständig**:
- Keine Jekyll-Konfiguration
- Kein Build-System in diesem Repo
- Build findet im Website-Repository statt
- Inhalte werden von Antora remote oder über das Dateisystem bezogen

### Barrierefreiheit

Beim Erstellen von AsciiDoc-Inhalten:
- Semantische Überschriftenhierarchie verwenden (`=`, `==`, `===`)
- Alternativtexte für Bilder: `image::file.png[Aussagekräftiger Alt-Text]`
- Korrekte Dokumentstruktur sicherstellen
- Antora-Navigation und Cross-References nutzen

---

**Zuletzt aktualisiert**: Juli 2026  
**Maintainer-Referenz**: Siehe `governance-community/index.adoc` für Governance-Struktur  
**Verwandt**: Siehe `waf2p.github.io`-Repository für Website-Build-Konfiguration
