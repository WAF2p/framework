#!/usr/bin/env python3
"""Remove extra blank lines between table rows in catalog.adoc."""
from pathlib import Path

REPOS = {
    "de": ".",
    "en": "../framework-en",
}


def clean(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out = []
    in_table = False
    prev_blank = False
    for line in lines:
        if line.strip() == "|===":
            in_table = not in_table
            out.append(line)
            prev_blank = False
            continue
        if in_table:
            if line.strip() == "":
                if not prev_blank:
                    out.append(line)
                prev_blank = True
                continue
        out.append(line)
        prev_blank = False
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    for lang, repo_root in REPOS.items():
        path = Path(repo_root) / "modules" / "controls" / "pages" / "catalog.adoc"
        clean(path)
        print(f"Cleaned whitespace in {repo_root}/catalog.adoc")


if __name__ == "__main__":
    main()
