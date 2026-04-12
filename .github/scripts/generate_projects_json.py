"""Parse README.md and sub-READMEs into projects.json for GitHub Pages."""

import json
import re
import sys


def parse_readme(filepath, category="main"):
    """Parse a README file and extract project entries."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    projects = []
    current_date = ""
    current_author = ""
    current_author_github = ""

    for line in lines:
        # Match date header
        date_match = re.match(
            r"^###\s+(\d{4}\s+年\s+\d{1,2}\s+月\s+\d{1,2}\s+号添加)", line
        )
        if date_match:
            current_date = date_match.group(1)
            current_author = ""
            current_author_github = ""
            continue

        # Match author line with Github link
        author_match = re.match(
            r"^####\s+(.+?)\s*-\s*\[Github\]\((.+?)\)", line
        )
        if author_match:
            current_author = author_match.group(1)
            current_author_github = author_match.group(2)
            continue

        # Match author line without Github link
        author_match2 = re.match(r"^####\s+(.+)", line)
        if author_match2 and not re.match(
            r"^####\s+(.+?)\s*-\s*\[Github\]", line
        ):
            current_author = author_match2.group(1)
            current_author_github = ""
            continue

        # Match project entries
        proj_match = re.match(
            r"^\*\s+:(white_check_mark|clock8|x):\s+\[(.+?)\]\((.+?)\)[：:]\s*(.*)",
            line,
        )
        if proj_match:
            status = proj_match.group(1)
            name = proj_match.group(2)
            url = proj_match.group(3)
            desc = proj_match.group(4).strip()

            status_map = {
                "white_check_mark": "online",
                "clock8": "developing",
                "x": "offline",
            }

            projects.append(
                {
                    "name": name,
                    "url": url,
                    "status": status_map[status],
                    "description": desc,
                    "author": current_author,
                    "authorGithub": current_author_github,
                    "date": current_date,
                    "category": category,
                }
            )

    return projects


def main():
    all_projects = []

    # Parse main README
    all_projects.extend(parse_readme("README.md", "main"))

    # Parse sub-READMEs
    try:
        all_projects.extend(parse_readme("README-Game.md", "game"))
    except FileNotFoundError:
        print("README-Game.md not found, skipping.", file=sys.stderr)

    try:
        all_projects.extend(
            parse_readme("README-Programmer-Edition.md", "programmer")
        )
    except FileNotFoundError:
        print(
            "README-Programmer-Edition.md not found, skipping.",
            file=sys.stderr,
        )

    # Sort by date descending (newest first)
    def date_sort_key(p):
        match = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*号", p.get("date", ""))
        if match:
            return (
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
            )
        return (0, 0, 0)

    all_projects.sort(key=date_sort_key, reverse=True)

    with open("projects.json", "w", encoding="utf-8") as f:
        json.dump(all_projects, f, ensure_ascii=False, indent=2)

    print(f"Generated projects.json with {len(all_projects)} projects")


if __name__ == "__main__":
    main()
