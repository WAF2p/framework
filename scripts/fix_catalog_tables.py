#!/usr/bin/env python3
"""Fix malformed AsciiDoc tables in catalog.adoc.

Issues addressed:
- Rows with too many cells (extra trailing |— spanning a separate line) get trimmed.
- Duplicate table delimiters on the same line are split.
- Missing blank line after a table closer (|===) before the next heading is inserted.
- Stray leading | in table row continuation lines is removed.
"""
import re
from pathlib import Path

REPOS = {
    "de": ".",
    "en": "../framework-en",
}


def count_cols(line):
    m = re.search(r'\[cols="([^"]+)"\]', line)
    if m:
        return len([c for c in m.group(1).split(",") if c.strip()])
    return None


def fix_file(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out = []
    cols = None
    in_table = False
    pending_row = []  # collects multi-line row cells
    for i, line in enumerate(lines):
        # Detect column spec before table opener
        cols_spec = count_cols(line)
        if cols_spec is not None and i + 1 < len(lines) and lines[i + 1].strip() == "|===":
            cols = cols_spec
            in_table = True

        # Split duplicated opener/closer like "[cols=...]|==="
        if re.match(r'\[cols="[^"]+"\]\|===', line.strip()):
            out.append(line.replace("|===", "").rstrip())
            out.append("|===")
            in_table = True
            continue

        # Table closer
        if line.strip() == "|===":
            in_table = False
            cols = None
            out.append(line)
            continue

        # Collect cells that span lines while inside a table
        if in_table and cols and line.startswith("|"):
            cell_text = line[1:]  # strip leading pipe
            pending_row.append(cell_text)
            # Check if we reached expected column count or next line is blank/new row/closer
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            is_row_break = (
                pending_row and next_line.startswith("|") and not next_line.startswith("|===")
            ) or next_line.strip() == "|===" or next_line.strip() == ""
            if len(pending_row) >= cols or (is_row_break and len(pending_row) >= 1):
                # Trim trailing empty/placeholder cells
                while len(pending_row) > cols and pending_row[-1].strip() in ("", "—", "-"):
                    pending_row.pop()
                # If still too many, hard trim
                if len(pending_row) > cols:
                    pending_row = pending_row[:cols]
                # Reconstruct row, ensuring each cell starts on its own line
                out.extend(["|" + c for c in pending_row])
                pending_row = []
            continue

        out.append(line)

    # Ensure blank line between |=== and following == heading
    text2 = "\n".join(out)
    text2 = re.sub(r"\|===\n(== )", r"|===\n\n\1", text2)
    text2 = re.sub(r"\n{3,}", "\n\n", text2)

    if text2 != text:
        path.write_text(text2 + "\n", encoding="utf-8")
        return True
    return False


def main():
    for lang, root in REPOS.items():
        path = Path(root) / "modules" / "controls" / "pages" / "catalog.adoc"
        if fix_file(path):
            print(f"Fixed {path}")
        else:
            print(f"No changes needed in {path}")


if __name__ == "__main__":
    main()
