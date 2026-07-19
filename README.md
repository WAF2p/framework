# WAF++ Framework Documentation

[![Build Status](https://github.com/WAF2p/waf2p.github.io/actions/workflows/jekyll-gh-pages.yml/badge.svg)](https://github.com/WAF2p/waf2p.github.io/actions/workflows/jekyll-gh-pages.yml)

This is the Antora documentation component for the **WAF++** (Well-Architected Framework++) project – a community-driven, cloud-agnostic framework for sovereign, secure, and sustainable cloud architectures.

The documentation is integrated into the main website at https://waf2p.dev/docs/wafpp/1.0.1-en/.

---

## 👥 For Content Contributors

### Where do I find the documentation files?

Content is organized by pillar module:

```
modules/
├── ROOT/pages/                 # Frame content: home, roadmap, resources
├── pillar-security/pages/      # Security pillar
├── pillar-cost/pages/          # Cost Optimization pillar
├── pillar-efficiancy/pages/    # Performance Efficiency pillar
├── pillar-reliability/pages/   # Reliability pillar
├── pillar-excellence/pages/    # Operational Excellence pillar
├── pillar-sustainability/pages/# Sustainability pillar
├── pillar-sovereign/pages/     # Sovereign pillar
├── pillar-agentic/pages/       # Agentic pillar
└── controls/pages/             # Machine-readable controls catalog
```

Each pillar has its own navigation (`nav.adoc`) and pages (`pages/`).

### How do I edit content?

1. **Open file**: Open the relevant `.adoc` file in the appropriate module under `modules/<module>/pages/`
2. **Edit**: Use AsciiDoc syntax (similar to Markdown)
3. **Save**: Save your changes
4. **Commit**: Create a commit with a meaningful description

### Important AsciiDoc Syntax

```asciidoc
= Page Title (H1)

== Section Heading (H2)

=== Subsection Heading (H3)

**Bold**, _italic_

* Bullet list
* Second item

xref:another-page.adoc[Link to another page]

image::images/diagram.png[Description]
```

### Previewing Changes

Preview happens via the website repository build. Alternatively you can use AsciiDoc editors:
- Online: https://asciidoclive.com/
- VS Code: Install the "AsciiDoc" extension

### Further Information

Detailed technical information is available in `AGENTS.md` in this repository.

---

## 🔧 For Repository Developers

### Antora Component Structure

This repository is structured as an **Antora documentation component**:

```
framework/
├── antora.yml                    # Component descriptor
├── modules/
│   ├── ROOT/
│   │   ├── nav.adoc              # Top-level navigation
│   │   └── pages/                # Frame content
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
│       └── controls/             # YAML controls
└── AGENTS.md                     # Developer guidelines
```

### Website Repository Integration

The documentation is **not built directly** in this repository. Instead:

1. The **website repository** (`waf2p.github.io`) uses Antora
2. Antora reads this repository as a **content source**
3. Antora generates HTML and integrates it into the Jekyll site
4. Output is published at: `https://waf2p.dev/docs/wafpp/1.0.1-en/`

### Antora Component Configuration

The `antora.yml` file defines this component:

```yaml
name: wafpp
version: '1.0.1-en'
display_version: '1.0.1 (English)'
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

**URL structure**: `/docs/<name>/<version>/<module>/<page-path>`  
**Example**: `/docs/wafpp/1.0.1-en/pillar-security/index.html`

### Build Process

The build runs in the **website repository**:

```bash
# In the website repository
npx antora antora-playbook-local.yml   # Local sources
task docs:build:local                  # Taskfile shortcut
task site:build                        # Complete site
```

The Antora playbooks in the website repository reference this repository as a content source.

### Cross-References and Links

Use `xref:` syntax for internal links. Within the same module without a module prefix; across modules with a module prefix:

```asciidoc
xref:index.adoc[Home page in current module]
xref:pillar-security:controls.adoc[Security Controls]
xref:pillar-agentic:index.adoc[Agentic Pillar]
xref:controls:catalog.adoc[Controls Catalog]
```

**Important**: Do not use relative paths like `../` – Antora resolves `xref:` automatically.

### Validation

Validate AsciiDoc syntax (requires asciidoctor):

```bash
# Install
gem install asciidoctor

# Single file
asciidoctor -o /dev/null modules/ROOT/pages/index.adoc

# All files
find modules -name "*.adoc" -exec asciidoctor -o /dev/null {} \;
```

### GitHub Actions Integration

The CI/CD pipeline in the website repository:

1. Clones this framework repository
2. Runs the Antora build
3. Combines Antora output with the Jekyll site
4. Deploys to GitHub Pages

Workflow file: `.github/workflows/jekyll-gh-pages.yml` in the website repository

### Deployment URLs

After successful deployment:

- **Home page**: https://waf2p.dev/docs/wafpp/1.0.1-en/
- **Example page**: https://waf2p.dev/docs/wafpp/1.0.1-en/pillar-security/index.html

### Developer Guidelines

Detailed technical standards and best practices can be found in:
- **`AGENTS.md`** in this repository – Antora-specific guidelines
- **`AGENTS.md`** in the website repository – overall architecture and build process

---

## 📁 Project Structure

```
framework/
├── antora.yml                              # Antora component descriptor
├── modules/
│   ├── ROOT/
│   │   ├── nav.adoc                        # Top-level navigation
│   │   └── pages/
│   │       ├── index.adoc                  # Home page
│   │       ├── pillars/
│   │       │   └── index.adoc              # 8-pillar landing page
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
│       └── controls/                       # YAML controls
├── AGENTS.md                               # Developer guidelines
└── README.md                               # This file
```

---

## 🔗 Resources

- **Antora Documentation**: https://docs.antora.org/
- **AsciiDoc Syntax**: https://docs.asciidoctor.org/asciidoc/latest/
- **Website Repository**: https://github.com/WAF2p/waf2p.github.io
- **Live Site**: https://waf2p.dev/

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Create a feature branch
2. Make your changes in the `.adoc` files
3. Test locally (via the website repository build)
4. Create a pull request with a meaningful description

For questions about structure or build process, see `AGENTS.md`.

---

**WAF++ Community** | https://waf2p.dev/
