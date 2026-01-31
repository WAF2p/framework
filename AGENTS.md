# Agent Guidelines for WAF++ Framework Repository

This repository contains the **WAF++** (Well-Architected Framework Plus Plus) documentation - a community-driven framework for sovereign, cloud-agnostic cloud usage. This is a documentation-only project written in German, consisting of markdown files and HTML for static site generation.

## Project Overview

**Repository**: https://github.com/WAF2p/framework.git  
**Language**: German (Deutsch)  
**Type**: Documentation/Static Website  
**Content Focus**: Cloud architecture, governance, security, cost optimization, reliability, and sustainability

### Directory Structure

```
.
├── index.html                    # Main landing page
├── architektur/                  # Architecture & maturity models
├── best-practises/               # Getting started & motivation
├── governance-community/         # CNCF-inspired governance
├── pillars/                      # Seven framework pillars
│   ├── security/                 # Security (Säule 1)
│   ├── costs/                    # Cost Optimization (Säule 2)
│   ├── reliability/              # Reliability (Säule 4)
│   ├── excellence/               # Operational Excellence
│   ├── efficiancy/               # Performance Efficiency
│   ├── governance/               # Governance
│   └── sustainability/           # Sustainability
├── resources/                    # Additional resources
│   └── wording/                  # Terminology definitions
└── roadmap/                      # Project roadmap
    └── 2026/                     # Annual roadmap
```

## Build/Test Commands

### Local Development

**Preview HTML**:
```bash
# Open the main page in browser
open index.html

# For local development with live reload (if using a static server)
python3 -m http.server 8000
# Then visit: http://localhost:8000
```

**Validation**:
```bash
# Check markdown syntax (if markdownlint is installed)
markdownlint '**/*.md' --ignore node_modules

# Validate frontmatter in markdown files
grep -r "^---$" --include="*.md" .
```

**Git Operations**:
```bash
# Check status
git status

# View recent changes
git log --oneline -10

# Create feature branch
git checkout -b feature/your-feature-name
```

### Testing Individual Files

**Validate a single markdown file**:
```bash
# Read file content
cat pillars/security/index.md

# Check frontmatter structure
head -10 pillars/security/index.md | grep -E "^(---|title:|subtitle:)"
```

## Content Style Guidelines

### Language & Tone

- **Primary language**: German (Deutsch) - all documentation must be in German
- **Tone**: Professional, accessible, community-focused
- **Audience**: Architects, platform teams, security/compliance professionals
- **Style**: Clear, structured, action-oriented

### Markdown Structure

**Frontmatter** (required for all index.md files):
```yaml
---
title: "Page Title"
subtitle: "Optional subtitle"
---
```

**Section Structure**:
- Use `##` for main sections
- Use `###` for subsections
- Use `**bold**` for emphasis on key terms
- Use `- ` for unordered lists (bullet points)
- Use `> ` for tips and callouts

**Link Style**:
- Internal links: `[text](#anchor)`
- External links: `[text](https://url)`
- Always use German text for link descriptions

### Content Guidelines for Pillars

Each pillar (Säule) should follow this structure:

1. **Worum geht es?** - What is it about? (2-3 sentences)
2. **Was wird gemacht?** - What is being done? (bullet points)
3. **Was ist zu beachten?** - What should be considered? (bullet points)
4. **Wo soll es hingehen?** - Where should it go? (long-term vision, 3-4 points)

### Naming Conventions

**Directories**:
- Use lowercase with hyphens: `best-practises/`, `governance-community/`
- German words preferred: `architektur/` not `architecture/`

**Files**:
- Main content files: `index.md`
- Root landing page: `index.html`

**Titles**:
- Pillars: "Säule [Number] - [Name]"
- Use title case for major sections

### Terminology

**Key German Terms** (use consistently):
- **Säule** = Pillar
- **Reifegrad/Reifegradmodell** = Maturity/Maturity Model
- **Governance** = Governance (keep English)
- **Cloud-agnostisch** = Cloud-agnostic
- **Souverän/Souveränität** = Sovereign/Sovereignty

Refer to `resources/wording/index.md` for project-specific terminology.

## Git Workflow

### Commit Message Format

Follow conventional commits style in German:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New content or feature
- `fix`: Corrections to existing content
- `docs`: Documentation structure changes
- `style`: Formatting, typos (no content change)
- `refactor`: Content reorganization
- `chore`: Maintenance tasks

**Examples**:
```
feat: add sustainability pillar description

fix: correct typo in security pillar

docs: restructure roadmap for 2026
```

### Branch Strategy

- `main` - stable, production-ready content
- `feature/*` - new content or sections
- `fix/*` - corrections and improvements

## Content Quality Checklist

Before committing new content:

- [ ] Frontmatter is present and valid
- [ ] Content is in German
- [ ] Structure follows pillar template (if applicable)
- [ ] No orphaned files or broken internal references
- [ ] Terminology is consistent with project glossary
- [ ] Markdown syntax is valid
- [ ] HTML entities are escaped in HTML context (`&amp;` not `&`)

## Community Guidelines

This project follows a **CNCF-inspired governance model**:

- **Technical Steering Committee (TSC)**: Technical direction
- **Maintainers**: Repository quality and consistency
- **Contributors**: Issues, PRs, proposals
- **User Advisory Group**: Practical feedback

**Contributing**:
1. Check existing issues on GitHub
2. Open an issue for discussion before major changes
3. Follow the style guidelines in this document
4. Submit PRs with clear descriptions
5. Participate in community discussions

## Special Considerations

### HTML Files

The `index.html` file uses:
- UTF-8 encoding
- German language content
- Simple static structure
- HTML entity encoding for special characters

### No Code Files

This repository contains **no executable code**:
- No build system (npm, make, etc.)
- No dependencies to install
- No tests to run
- Pure documentation repository

### Accessibility

When editing HTML or adding new formats:
- Use semantic HTML tags
- Provide alt text for images (when added)
- Ensure proper heading hierarchy
- Maintain readable contrast

---

**Last Updated**: January 2026  
**Maintainer Reference**: See `governance-community/index.md` for governance structure
