#!/usr/bin/env python3
"""Anti-slop lint for the ClawScreen README and docs.

Section 14.5 of the specification forbids dressed-up, interchangeable output:
emoji in headings, superlatives without proof, buzzword paragraphs, filler
without a process, placeholder code and broken internal links.

This tool checks documentation only. It does not censor content and it never
rewrites a file on its own.

Usage:
  anti-slop.py                 lint README.md and docs/*.md
  anti-slop.py --self-test     prove the checker works (runs in CI)
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

# (rule id, what it forbids, how it is detected, why it matters)
RULES: list[tuple[str, str, re.Pattern, str]] = [
    (
        "emoji-in-heading",
        "emoji in a Markdown heading",
        re.compile(r"^#{1,6} .*[\U0001F300-\U0001FAFF☀-➿]", re.M),
        "Section 14.5: headings stay calm and copyable.",
    ),
    (
        "unproven-superlative",
        "superlative without proof",
        re.compile(
            r"\b(revolutionary|game[- ]changer|blazingly fast|blazing fast"
            r"|best[- ]in[- ]class|world[- ]class|cutting[- ]edge"
            r"|next[- ]generation|seamlessly|effortlessly|magical)\b",
            re.I,
        ),
        "Section 14.5: no superlatives without proof.",
    ),
    (
        "filler-without-process",
        "filler invitation with no process behind it",
        re.compile(r"contributions welcome", re.I),
        "Section 14.5: say what the process is, or say nothing.",
    ),
    (
        "unfinished-marker",
        "placeholder or unfinished marker",
        re.compile(r"\b(TODO|FIXME|XXX|TBD|coming soon|lorem ipsum)\b", re.I),
        "Section 20: no placeholder functions or unfinished TODOs.",
    ),
    (
        "ai-filler-phrase",
        "AI filler phrase",
        re.compile(
            r"\b(as an AI language model|I cannot fulfill|delve into the realm"
            r"|in today's (fast[- ]paced|digital) world|it'?s important to note that)\b",
            re.I,
        ),
        "Section 14.5: no buzzword paragraphs.",
    ),
    (
        "fake-test-claim",
        "claim of a passing test with no command",
        re.compile(r"^.*\ball tests pass\b.*$", re.M),
        "Section 20: every claim in the README is backed by a command or a test.",
    ),
]

# Markdown links to a repository-relative path: [text](path)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def check_text(text: str, label: str) -> list[str]:
    findings: list[str] = []
    for rule_id, message, pattern, why in RULES:
        for m in pattern.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            snippet = m.group(0).strip()[:60]
            findings.append(f"{label}:{line}: [{rule_id}] {message}: {snippet!r}\n      {why}")
    return findings


def check_links(text: str, label: str, base: pathlib.Path) -> list[str]:
    """A relative Markdown link must resolve inside the repository."""
    findings: list[str] = []
    for m in LINK_RE.finditer(text):
        target = m.group(1).strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = target.split("#", 1)[0]
        if not path:
            continue
        if not (base / path).exists():
            line = text.count("\n", 0, m.start()) + 1
            findings.append(f"{label}:{line}: [broken-link] {target!r} does not exist in the repo")
    return findings


def lint_file(path: pathlib.Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    label = str(path.relative_to(REPO))
    return check_text(text, label) + check_links(text, label, path.parent)


def lint_repo() -> tuple[int, list[str]]:
    targets: list[pathlib.Path] = []
    readme = REPO / "README.md"
    if readme.exists():
        targets.append(readme)
    docs = REPO / "docs"
    if docs.is_dir():
        targets.extend(sorted(docs.rglob("*.md")))

    if not targets:
        print("FAIL: no README.md and no docs/*.md found — nothing was linted")
        return 1, []

    findings: list[str] = []
    for path in targets:
        findings.extend(lint_file(path))

    if findings:
        print(f"FAIL: {len(findings)} finding(s) in {len(targets)} file(s)")
        for line in findings:
            print(f"  - {line}")
        return 1, findings

    names = ", ".join(str(p.relative_to(REPO)) for p in targets)
    print(f"OK: {len(RULES)} rules clean over {len(targets)} file(s): {names}")
    return 0, []


# --- self-test: the checker must actually catch what it claims to catch ---
SLOP_SAMPLE = """# Build \U0001F680 ClawScreen

This is a revolutionary, game-changing tool with blazing fast performance.

TODO: write the real text.

Contributions welcome!

See [the missing file](docs/does-not-exist.md).
"""

CLEAN_SAMPLE = """# ClawScreen

ClawScreen steuert den Bildschirm eines Android-Smartphones.

Die gemessene Verbindungszeit liegt bei 2,1 Sekunden, gemessen am 2026-10-04.

Siehe [BUILD-STATE.md](progress/BUILD-STATE.md).
"""


def self_test() -> int:
    failures: list[str] = []

    slop_findings = check_text(SLOP_SAMPLE, "sample")
    caught = {f.split("[")[1].split("]")[0] for f in slop_findings}
    expected = {
        "emoji-in-heading",
        "unproven-superlative",
        "unfinished-marker",
        "filler-without-process",
    }
    for rule in sorted(expected):
        if rule not in caught:
            failures.append(f"self-test: the slop sample should trip {rule!r}, it did not")

    link_findings = check_links(SLOP_SAMPLE, "sample", REPO)
    if not any("[broken-link]" in f for f in link_findings):
        failures.append("self-test: a link to a missing file should be reported")

    clean_findings = check_text(CLEAN_SAMPLE, "clean") + check_links(CLEAN_SAMPLE, "clean", REPO)
    if clean_findings:
        failures.append(
            "self-test: the clean sample must produce no findings, got:\n      "
            + "\n      ".join(clean_findings)
        )

    if failures:
        print(f"FAIL: {len(failures)} self-test failure(s)")
        for line in failures:
            print(f"  - {line}")
        return 1
    print(
        f"OK: self-test passed — {len(expected)} rules and the link check "
        "each catch their case, and the clean sample is silent"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--self-test", action="store_true", help="prove the checker catches slop")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    code, _ = lint_repo()
    return code


if __name__ == "__main__":
    sys.exit(main())