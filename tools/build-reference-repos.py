#!/usr/bin/env python3
"""Build docs/reference-repos.md from spec section 22 (task CS-006).

The specification already contains the curated list with a binding take-over
decision per row. This script turns that section into a document and merges
metadata that is read live from the GitHub API, so the document never claims
stars or activity that were never measured.

Usage:
  tools/build-reference-repos.py --live        query the GitHub API for every row
  tools/build-reference-repos.py              use only the metadata in the spec
  tools/build-reference-repos.py --check      fail if the document is out of date

The live path needs `gh auth status` to be logged in. Without credentials the
script falls back to the spec numbers and says so in the document, rather than
inventing values.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
SPEC = REPO / "clawscreen-spec.md"
OUT = REPO / "docs" / "reference-repos.md"
CACHE = REPO / "docs" / ".reference-repos-cache.json"

ROW = re.compile(
    r"^\|\s*\[`(?P<repo>[^`]+)`\]\((?P<url>https://github\.com/[^)]+)\)\s*\|"
    r"\s*(?P<stars>[^|]*)\|\s*(?P<licence>[^|]*)\|\s*(?P<pushed>[^|]*)\|\s*(?P<take>.+?)\s*\|"
)
HEADING = re.compile(r"^####\s+([A-G])\s+—\s+(.+)$")


def parse_spec() -> tuple[list[dict], list[tuple[str, str]]]:
    """Return the rows and the category headings, in document order."""
    rows: list[dict] = []
    categories: list[tuple[str, str]] = []
    category = "?"
    for line in SPEC.read_text(encoding="utf-8").splitlines():
        h = HEADING.match(line)
        if h:
            category = h.group(1)
            categories.append((category, h.group(2).strip()))
            continue
        if not line.startswith("|"):
            continue
        m = ROW.match(line)
        if not m:
            continue
        pushed = m.group("pushed").replace("**", "").strip()
        rows.append(
            {
                "category": category,
                "repo": m.group("repo").strip(),
                "url": m.group("url").strip(),
                "stars_spec": m.group("stars").replace(",", "").replace("**", "").strip(),
                "licence_spec": m.group("licence").replace("**", "").strip(),
                "pushed_spec": pushed,
                "take": m.group("take").replace("**", "").strip(),
            }
        )
    return rows, categories


def load_cache() -> dict[str, dict]:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def fetch_live(repos: list[str]) -> dict[str, dict]:
    """Read stars, licence, last push and archive state from the GitHub API."""
    live = load_cache()
    changed = False
    for repo in sorted(set(repos)):
        if repo in live:
            continue
        proc = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{repo}",
                "--jq",
                "{stars: .stargazers_count, licence: (.license.spdx_id // \"NOASSERTION\"),"
                " pushed: (.pushed_at|.[0:10]), archived}",
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            print(f"  ! {repo}: {proc.stderr.strip().splitlines()[:1]}", file=sys.stderr)
            continue
        live[repo] = json.loads(proc.stdout)
        changed = True
        time.sleep(0.4)  # stay well inside the unauthenticated rate limit
    if changed:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(live, indent=1, sort_keys=True), encoding="utf-8")
    return live


TAKE_OVERS = [
    (
        "scrcpy picture and control transport (Genymobile/scrcpy)",
        "CS-010, CS-026",
        "Push `scrcpy-server` to the phone, start it, take a frame, send a tap.",
        "planned",
    ),
    (
        "ADB reconnect and fallback logic (DeviceFarmer/adbkit, openatx/adbutils)",
        "CS-010, CS-012, CS-014",
        "Thin ADB layer with timeouts, `get-state` check before every tool call.",
        "planned",
    ),
    (
        "MCP tool schema and error format (modelcontextprotocol/typescript-sdk, anthropics/skills@mcp-builder)",
        "CS-012, CS-090",
        "Server built with the official SDK; tool descriptions written the official way.",
        "planned",
    ),
    (
        "Readable, checkable scenario format (mobile-dev-inc/Maestro, cucumber/cucumber-js)",
        "CS-070, CS-071, CS-080",
        "Acceptance scenarios written as numbered, checkable steps.",
        "planned",
    ),
    (
        "Material 3 and adaptive layout yardstick (android/nowinandroid, ehmo/platform-design-skills@android-design-guidelines)",
        "CS-040, CS-042, CS-045",
        "Companion app screens: Material 3, dark mode, 48 dp targets, high contrast.",
        "planned",
    ),
    (
        "Lint and format gates in CI (eslint, prettier, ktlint)",
        "CS-003, CS-082",
        "Formatting is not a discussion; a finding fails the build.",
        "planned",
    ),
]


def render(rows: list[dict], categories: list[tuple[str, str]], live: dict[str, dict]) -> str:
    stamp = max((v["pushed"] for v in live.values()), default="")
    measured = "measured live via the GitHub API" if live else "taken from the specification"
    out = [
        "# Reference projects (E18)",
        "",
        "Every row is a decision already taken in spec §22 — what we adopt and",
        "what we refuse. This file exists so nobody re-runs the 50-repository",
        "search. Rows marked *reference only*, *read only* or *do not copy* were",
        "checked and rejected; do not retry them. A row marked **archived** must",
        "never be used as a base.",
        "",
        f"Metadata (stars, licence, last push) is {measured}.",
        "",
        "| | |",
        "|---|---|",
        f"| Rows | {len(rows)} entries, {len(set(r['repo'] for r in rows))} distinct repositories |",
        f"| Categories | {len(categories)} (A–G) |",
        f"| Last push seen among the listed repositories | {stamp or 'n/a'} |",
        "| Regenerate | `python3 tools/build-reference-repos.py --live` |",
        "| Verify without writing | `python3 tools/build-reference-repos.py --check` |",
        "",
        "## Licence rule",
        "",
        "Apache-2.0 and MIT may be used in our code with attribution. `NOASSERTION`",
        "means GitHub could not identify a licence — treat it as *do not copy code",
        "from it, read it only*. GPL-3.0 and LGPL-2.1 rows are read-only",
        "references; nothing from them may end up in our source.",
        "",
    ]
    for letter, title in categories:
        out.append(f"## Category {letter} — {title}")
        out.append("")
        out.append("| Repository | Stars | Licence | Last push | Archived | What we take from it |")
        out.append("|---|---:|---|---|---|---|")
        for row in rows:
            if row["category"] != letter:
                continue
            meta = live.get(row["repo"], {})
            stars = meta.get("stars")
            licence = meta.get("licence", row["licence_spec"])
            pushed = meta.get("pushed", row["pushed_spec"])
            archived = "**yes**" if meta.get("archived") else "no"
            stars_cell = f"{stars:,}" if isinstance(stars, int) else row["stars_spec"]
            out.append(
                f"| [`{row['repo']}`]({row['url']}) | {stars_cell} | {licence} | {pushed} | "
                f"{archived} | {row['take']} |"
            )
        out.append("")

    out.append("## Take-over ledger")
    out.append("")
    out.append(
        "The take-over column above says what to adopt. This ledger is the honest "
        "counterpart: it only says *implemented* once the code or setup really "
        "contains the take-over and the task that needed it is done."
    )
    out.append("")
    out.append("| Take-over | Task | What it looks like in this repository | State |")
    out.append("|---|---|---|---|")
    for name, task, shape, state in TAKE_OVERS:
        out.append(f"| {name} | {task} | {shape} | {state} |")
    out.append("")
    done = sum(1 for t in TAKE_OVERS if t[3] != "planned")
    out.append(
        f"{done} of {len(TAKE_OVERS)} take-overs are implemented so far. A row only "
        "leaves *planned* when the code exists and the task test has passed."
    )
    out.append("")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true", help="query the GitHub API")
    ap.add_argument("--check", action="store_true", help="fail if the file is out of date")
    args = ap.parse_args()

    rows, categories = parse_spec()
    if not rows:
        print("FAIL: no rows parsed from spec section 22")
        return 1
    if len(categories) < 5:
        print(f"FAIL: only {len(categories)} categories found, at least 5 required")
        return 1

    # --check must not call the API: CI compares against the cached measurement,
    # and --live refreshes that cache first.
    if args.check:
        live = load_cache()
    elif args.live:
        live = fetch_live([r["repo"] for r in rows])
    else:
        live = {}
    text = render(rows, categories, live)

    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("FAIL: docs/reference-repos.md is out of date — rerun with --live")
            return 1
        print(f"OK: {OUT.relative_to(REPO)} matches the spec ({len(rows)} rows, {len(categories)} categories)")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"OK: wrote {OUT.relative_to(REPO)} — {len(rows)} rows, {len(categories)} categories")
    return 0


if __name__ == "__main__":
    sys.exit(main())