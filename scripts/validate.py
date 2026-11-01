#!/usr/bin/env python3
"""
Validate the Wombat documentation repository for:
  1. YAML control schema compliance
  2. Narrative page existence for each control
  3. Navigation coverage of all controls
  4. Cross-reference sanity (no ../, targets exist)

Run: python3 scripts/validate.py
"""
import re
import sys
import glob
from pathlib import Path
from collections import defaultdict

try:
    import yaml
except ImportError as e:  # pragma: no cover
    print(f"ERROR: PyYAML is required: {e}")
    sys.exit(1)

REPO = Path.cwd()
MODULES_DIR = REPO / "modules"
CONTROLS_DIR = MODULES_DIR / "controls" / "controls"

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

ALLOWED_SEVERITY = {"critical", "high", "medium", "low"}
ALLOWED_TYPES = {"governance", "configuration", "automation", "process", "architecture"}
ALLOWED_ENGINES = {"terraform", "config", "manual", "api"}
ALLOWED_ON_FAIL = {"violation", "finding", "advisory"}
ALLOWED_BLOCK_TYPES = {
    "resource",
    "provider",
    "variable",
    "terraform",
    "module",
    "file",
    "any",
}
ALLOWED_OPERATORS = {
    "attribute_exists",
    "attribute_exists_or_fallback",
    "not_empty",
    "equals",
    "not_equals",
    "in",
    "not_in",
    "is_true",
    "is_false",
    "greater_than",
    "greater_than_or_equal",
    "less_than",
    "less_than_or_equal",
    "matches",
    "not_matches",
    "key_exists",
    "block_exists",
    "has_associated_resource",
    "not_contains",
    "json_not_contains_pattern",
}
OPERATORS_NEED_EXPECT = {"equals", "not_equals", "in", "not_in", "greater_than",
                         "greater_than_or_equal", "less_than", "less_than_or_equal"}
OPERATORS_NEED_PATTERN = {"matches", "not_matches"}
OPERATORS_NEED_KEY = {"key_exists"}
OPERATORS_NEED_FALLBACK = {"attribute_exists_or_fallback"}

errors = []
warnings = []


def err(path: Path, msg: str):
    errors.append(f"{path.relative_to(REPO)}: {msg}")


def warn(path: Path, msg: str):
    warnings.append(f"{path.relative_to(REPO)}: {msg}")


def validate_control_schema(path: Path):
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        err(path, f"invalid YAML: {e}")
        return

    if not isinstance(data, dict):
        err(path, "control must be a YAML mapping")
        return

    expected_id = path.stem
    if data.get("id") != expected_id:
        err(path, f"id must be '{expected_id}', got {data.get('id')!r}")

    pillar = data.get("pillar")
    if pillar not in PILLAR_MODULE:
        err(path, f"unknown pillar {pillar!r}")

    if data.get("severity") not in ALLOWED_SEVERITY:
        err(path, f"severity must be one of {ALLOWED_SEVERITY}, got {data.get('severity')!r}")

    control_types = data.get("type")
    if isinstance(control_types, str):
        control_types = [control_types]
    if not isinstance(control_types, list) or not control_types:
        err(path, "type must be a non-empty list of strings")
    else:
        for t in control_types:
            if t not in ALLOWED_TYPES:
                err(path, f"type value {t!r} not in {ALLOWED_TYPES}")

    if not isinstance(data.get("description"), str) or not data.get("description", "").strip():
        err(path, "description must be a non-empty string")

    checks = data.get("checks", [])
    if not isinstance(checks, list):
        err(path, "checks must be a list")
        return

    for idx, check in enumerate(checks):
        prefix = f"check[{idx}]"
        if not isinstance(check, dict):
            err(path, f"{prefix} must be a mapping")
            continue

        cid = check.get("id")
        if not isinstance(cid, str) or not cid:
            err(path, f"{prefix}.id missing")
        elif not cid.startswith(expected_id.lower()):
            err(path, f"{prefix}.id '{cid}' must start with '{expected_id.lower()}'")

        if check.get("engine") not in ALLOWED_ENGINES:
            err(path, f"{prefix}.engine must be one of {ALLOWED_ENGINES}, got {check.get('engine')!r}")

        provider = check.get("provider")
        if not isinstance(provider, str) or not provider:
            err(path, f"{prefix}.provider must be a non-empty string")

        automated = check.get("automated")
        if not isinstance(automated, bool):
            err(path, f"{prefix}.automated must be a boolean, got {automated!r}")

        if check.get("on_fail") not in ALLOWED_ON_FAIL:
            err(path, f"{prefix}.on_fail must be one of {ALLOWED_ON_FAIL}, got {check.get('on_fail')!r}")

        scope = check.get("scope")
        if not isinstance(scope, dict):
            err(path, f"{prefix}.scope must be a mapping")
        else:
            block_type = scope.get("block_type")
            if block_type not in ALLOWED_BLOCK_TYPES:
                err(path, f"{prefix}.scope.block_type {block_type!r} not in {ALLOWED_BLOCK_TYPES}")
            if block_type == "resource" and not scope.get("resource_types"):
                err(path, f"{prefix}.scope.block_type=resource requires resource_types list")
            if block_type == "provider" and not scope.get("provider_name"):
                err(path, f"{prefix}.scope.block_type=provider requires provider_name")
            if block_type == "file" and not scope.get("path_pattern"):
                err(path, f"{prefix}.scope.block_type=file requires path_pattern")

        assertions = check.get("assertions", [])
        if not isinstance(assertions, list):
            err(path, f"{prefix}.assertions must be a list")
            continue
        for aidx, assertion in enumerate(assertions):
            aprefix = f"{prefix}.assertion[{aidx}]"
            if not isinstance(assertion, dict):
                err(path, f"{aprefix} must be a mapping")
                continue
            op = assertion.get("op")
            if op not in ALLOWED_OPERATORS:
                err(path, f"{aprefix}.op {op!r} not in {ALLOWED_OPERATORS}")
                continue
            if op in OPERATORS_NEED_EXPECT and "expected" not in assertion:
                err(path, f"{aprefix}.op={op} requires 'expected'")
            if op in OPERATORS_NEED_PATTERN and "pattern" not in assertion:
                err(path, f"{aprefix}.op={op} requires 'pattern'")
            if op in OPERATORS_NEED_KEY and "key" not in assertion:
                err(path, f"{aprefix}.op={op} requires 'key'")
            if op in OPERATORS_NEED_FALLBACK and "fallback_attribute" not in assertion:
                err(path, f"{aprefix}.op={op} requires 'fallback_attribute'")


def validate_narrative_pages():
    yaml_controls = set()
    for yml in sorted(CONTROLS_DIR.glob("WAF-*.yml")):
        yaml_controls.add(yml.stem)

    narrative_controls = set()
    for adoc in sorted(MODULES_DIR.glob("pillar-*/pages/controls/WAF-*.adoc")):
        narrative_controls.add(adoc.stem)

    missing = yaml_controls - narrative_controls
    extra = narrative_controls - yaml_controls
    if missing:
        for m in sorted(missing):
            err(Path("modules/controls/controls") / f"{m}.yml",
                f"missing narrative page for {m}")
    if extra:
        for e in sorted(extra):
            p = next(MODULES_DIR.glob(f"pillar-*/pages/controls/{e}.adoc"))
            warn(p, f"narrative page {e} has no YAML control")


def validate_navigation():
    nav_controls = defaultdict(set)
    for nav in MODULES_DIR.glob("*/nav.adoc"):
        text = nav.read_text(encoding="utf-8")
        for m in re.finditer(r"xref:((?:[^:\[]+):)?([^\[]+)\[", text):
            target = m.group(2)
            if "controls/WAF-" in target:
                ctrl = re.search(r"WAF-[A-Z]{3,4}-\d{3}", target)
                if ctrl:
                    nav_controls[nav.parent.name].add(ctrl.group(0))

    for pillar_mod, expected_pillar in PILLAR_MODULE.items():
        expected_controls = {p.stem for p in (MODULES_DIR / expected_pillar / "pages" / "controls").glob("WAF-*.adoc")}
        found = nav_controls.get(expected_pillar, set())
        missing = expected_controls - found
        extra = found - expected_controls
        for m in sorted(missing):
            err(MODULES_DIR / expected_pillar / "nav.adoc", f"control {m} not linked in navigation")
        for e in sorted(extra):
            err(MODULES_DIR / expected_pillar / "nav.adoc", f"navigation links unknown control {e}")


def validate_xrefs():
    def resolve(current_module, raw):
        if raw.startswith("#"):
            return None, None
        if ":" in raw:
            mod, page = raw.split(":", 1)
        else:
            mod = current_module
            page = raw
        page = page.split("#")[0]
        if not page.endswith(".adoc"):
            page += ".adoc"
        return mod, page

    for adoc in MODULES_DIR.glob("*/pages/**/*.adoc"):
        current_module = adoc.relative_to(MODULES_DIR).parts[0]
        text = adoc.read_text(encoding="utf-8")
        for m in re.finditer(r"xref:([^\[\]]+)\[", text):
            raw = m.group(1)
            # Skip literal examples inside inline code (preceded by ` or ')
            if m.start() > 0 and text[m.start() - 1] in ("`", "'", "+"):
                continue
            if raw.startswith("http") or raw.startswith("//") or "../" in raw:
                if "../" in raw:
                    err(adoc, f"xref uses relative path: xref:{raw}[]")
                continue
            mod, page = resolve(current_module, raw)
            if mod is None:
                continue
            target = MODULES_DIR / mod / "pages" / page
            if not target.exists():
                err(adoc, f"xref target not found: xref:{raw}[] -> {mod}:{page}")


def main():
    print(f"Validating repository: {REPO}")
    for yml in sorted(CONTROLS_DIR.glob("WAF-*.yml")):
        validate_control_schema(yml)
    validate_narrative_pages()
    validate_navigation()
    validate_xrefs()

    print()
    print(f"YAML controls validated: {len(list(CONTROLS_DIR.glob('WAF-*.yml')))}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    if warnings:
        for w in warnings:
            print(f"  WARN: {w}")
    if errors:
        for e in errors[:50]:
            print(f"  ERROR: {e}")
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more errors")
        sys.exit(1)
    print("OK – all validation checks passed")


if __name__ == "__main__":
    main()
