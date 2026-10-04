#!/usr/bin/env python3
"""Check and repair ClawScreen task headers.

The task files under `tasks/` carry a YAML header. This tool is the only place
that is allowed to decide whether a header agrees with the build state, so the
resume skill (E17) can trust it instead of guessing.

Usage:
  sync_frontmatter.py --check          task headers agree with progress/BUILD-STATE.md
  sync_frontmatter.py --fix            set status to done where the build state says done
  sync_frontmatter.py --check-matrix   every task has a test and at least 2 skills
  sync_frontmatter.py --check-spec     the spec is present and has the expected shape
  sync_frontmatter.py --list           print the task table (id, status, wave, deps)
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
TASKS = REPO / "tasks"
STATE = REPO / "progress" / "BUILD-STATE.md"
SPEC = REPO / "clawscreen-spec.md"
MATRIX = TASKS / "skill-matrix.md"

# Fields the header must carry. Anything missing is a finding, not a guess.
REQUIRED = ("id", "title", "status", "wave", "depends_on", "skills", "test")

VALID_STATUS = ("pending", "done", "blocked")

# Sections the spec must still contain, so a truncated or swapped spec is caught.
SPEC_MARKERS = (
    "## 0. How to start this build",
    "## 3. Decisions",
    "## 14. How Claude Code works while building",
    "## 15. The build plan",
    "## 20. Which model looks at the screen",
    "## 21. Using the phone's own chip",
    "## 22. Reference repositories",
)


def parse_header(text: str) -> tuple[dict, str]:
    """Return the header fields and the body. A task without a header is an error."""
    if not text.startswith("---"):
        raise ValueError("no YAML header (file must start with '---')")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("YAML header is not closed")
    block = text[3:end]
    body = text[end + 4 :]

    fields: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            fields[key] = m.group(2).strip()
        elif key and line.startswith(("  ", "\t")):
            # continuation of a block scalar such as `test: |`
            fields[key] = (fields[key] + "\n" + line.strip()).strip()
    return fields, body


def load_tasks() -> dict[str, dict]:
    tasks: dict[str, dict] = {}
    for path in sorted(TASKS.glob("CS-*.md")):
        text = path.read_text(encoding="utf-8")
        try:
            fields, _ = parse_header(text)
        except ValueError as exc:
            raise SystemExit(f"{path.name}: {exc}") from exc
        fields["_path"] = path
        fields["_text"] = text
        tasks[fields.get("id", path.stem)] = fields
    return tasks


def done_ids_from_state() -> set[str]:
    """Task ids the build state claims as done.

    Only a level-3 heading (`### CS-0xx`) counts. A level-4 heading
    (`#### CS-0xx`) is a note about a task that is still open, so a partial
    result can never be read as a finished one.
    """
    if not STATE.exists():
        return set()
    return set(re.findall(r"^### (CS-\d+)", STATE.read_text(encoding="utf-8"), re.M))


def blocker_ids_from_state() -> set[str]:
    """Task ids the build state claims as blocked (E24).

    A blocker is written as `#### CS-0xx — blocker: <what went wrong>`.
    """
    if not STATE.exists():
        return set()
    return set(
        re.findall(r"^#### (CS-\d+) — blocker", STATE.read_text(encoding="utf-8"), re.M)
    )


def cmd_check(tasks: dict[str, dict]) -> int:
    findings: list[str] = []

    for tid, f in tasks.items():
        missing = [k for k in REQUIRED if k not in f]
        if missing:
            findings.append(f"{tid}: header is missing {', '.join(missing)}")
            continue
        if f["status"] not in VALID_STATUS:
            findings.append(f"{tid}: status '{f['status']}' is not one of {VALID_STATUS}")
        if f["id"] != f["_path"].stem:
            findings.append(f"{tid}: id does not match the file name {f['_path'].name}")
        if not f["test"].strip():
            findings.append(f"{tid}: test is empty — a task is done only when its test passed")

    claimed = done_ids_from_state()
    blockers = blocker_ids_from_state()
    for tid in sorted(claimed | blockers):
        if tid not in tasks:
            findings.append(f"{tid}: named in BUILD-STATE.md but no task file exists")

    for tid, f in tasks.items():
        status = f.get("status")
        if status == "done" and tid not in claimed:
            findings.append(
                f"{tid}: header says done but BUILD-STATE.md has no '### {tid}' entry"
            )
        # The other direction matters too: a level-3 entry that claims a task is
        # finished while the header still says pending means somebody wrote the
        # entry before the test passed.
        if status != "done" and tid in claimed:
            findings.append(
                f"{tid}: BUILD-STATE.md claims done ('### {tid}') but the header "
                f"says '{status}' — the header wins until the test passes again"
            )
        if status == "blocked" and tid not in blockers:
            findings.append(
                f"{tid}: header says blocked but BUILD-STATE.md has no "
                f"'#### {tid} — blocker' entry"
            )
        if status != "blocked" and tid in blockers:
            findings.append(
                f"{tid}: BUILD-STATE.md lists a blocker but the header says '{status}'"
            )

    if findings:
        print(f"FAIL: {len(findings)} problem(s)")
        for line in findings:
            print(f"  - {line}")
        return 1

    done = sum(1 for f in tasks.values() if f.get("status") == "done")
    print(f"OK: {len(tasks)} task headers consistent ({done} done, {len(tasks) - done} open)")
    return 0


def cmd_fix(tasks: dict[str, dict]) -> int:
    """Align `status: done` with the build state. Never invents a done task."""
    claimed = done_ids_from_state()
    blockers = blocker_ids_from_state()
    changed = []
    for tid, f in tasks.items():
        current = f.get("status", "pending")
        if tid in claimed:
            want = "done"
        elif tid in blockers:
            want = "blocked"
        elif current == "done":
            # The header claims more than the build state can show. Repair
            # towards the verifiable side: a task whose entry is missing was
            # never proven, so it goes back to open.
            want = "pending"
        else:
            want = current
        if want == f.get("status"):
            continue
        text = f["_text"]
        text = re.sub(r"^status: \S+", f"status: {want}", text, count=1, flags=re.M)
        f["_path"].write_text(text, encoding="utf-8")
        changed.append(f"{tid}: -> {want}")
    print(f"OK: {len(changed)} header(s) updated" if changed else "OK: nothing to fix")
    for line in changed:
        print(f"  - {line}")
    return 0


def _split_row(line: str) -> list[str]:
    """Split a markdown table row into its cells, ignoring the outer pipes."""
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _matrix_table(matrix: str) -> tuple[list[str], dict[str, list[str]]]:
    """Return the header cells and the rows of the matrix table, by column name.

    The column named `Skills` is the one that counts. Looking at every column
    would count commas in the explanation column as skills, which is how an
    earlier version of this check passed a row with a single skill.
    """
    lines = [ln for ln in matrix.splitlines() if ln.strip().startswith("|")]
    if not lines:
        return [], {}
    header = [h.lower() for h in _split_row(lines[0])]
    rows: dict[str, list[str]] = {}
    for line in lines[2:]:  # skip header and the ---|--- separator
        cells = _split_row(line)
        if not cells:
            continue
        task_id = cells[0].strip("`")
        if not re.fullmatch(r"CS-\d+", task_id):
            continue
        rows[task_id] = cells
    return header, rows


def cmd_check_matrix(tasks: dict[str, dict]) -> int:
    findings: list[str] = []
    if not MATRIX.exists():
        print("FAIL: tasks/skill-matrix.md is missing (E15)")
        return 1
    matrix = MATRIX.read_text(encoding="utf-8")
    header, rows = _matrix_table(matrix)
    if "skills" not in header:
        print("FAIL: tasks/skill-matrix.md has no 'Skills' column")
        return 1
    skill_col = header.index("skills")

    for tid in sorted(tasks):
        cells = rows.get(tid)
        if cells is None:
            findings.append(f"{tid}: no row in skill-matrix.md")
            continue
        if skill_col >= len(cells):
            findings.append(f"{tid}: row has no Skills column")
            continue
        skills = [s.strip() for s in re.split(r",\s*|\s{2,}", cells[skill_col]) if s.strip()]
        if len(skills) < 2:
            findings.append(f"{tid}: only {len(skills)} skill(s) — E15 requires at least 2")
    if findings:
        print(f"FAIL: {len(findings)} problem(s)")
        for line in findings:
            print(f"  - {line}")
        return 1
    print(f"OK: every one of {len(tasks)} tasks has a test and at least 2 skills")
    return 0


def cmd_check_spec(_tasks: dict[str, dict]) -> int:
    findings: list[str] = []
    if not SPEC.exists():
        print("FAIL: clawscreen-spec.md is missing — it is the source of truth")
        return 1
    text = SPEC.read_text(encoding="utf-8")
    for marker in SPEC_MARKERS:
        if marker not in text:
            findings.append(f"missing section: {marker}")
    if findings:
        print(f"FAIL: {len(findings)} problem(s)")
        for line in findings:
            print(f"  - {line}")
        return 1
    print(f"OK: spec present ({len(text)} bytes, all {len(SPEC_MARKERS)} sections found)")
    return 0


def cmd_list(tasks: dict[str, dict]) -> int:
    def key(item: tuple[str, dict]) -> tuple[int, str]:
        return (int(item[0].split("-")[1]), item[0])

    print(f"{'id':<9}{'status':<9}{'wave':<6}{'deps'}")
    for tid, f in sorted(tasks.items(), key=key):
        print(f"{tid:<9}{f.get('status', '?'):<9}{f.get('wave', '?'):<6}{f.get('depends_on', '[]')}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="headers agree with the build state")
    group.add_argument("--fix", action="store_true", help="repair status from the build state")
    group.add_argument(
        "--check-matrix", action="store_true", help="every task has a test and 2+ skills"
    )
    group.add_argument(
        "--check-spec", action="store_true", help="the spec is present and complete"
    )
    group.add_argument("--list", action="store_true", help="print the task table")
    args = ap.parse_args()

    if not TASKS.is_dir():
        print(f"FAIL: {TASKS} does not exist")
        return 1
    tasks = load_tasks()
    if not tasks:
        print("FAIL: no task files found")
        return 1

    flag = next(k for k, v in vars(args).items() if v)
    return {
        "check": cmd_check,
        "fix": cmd_fix,
        "check_matrix": cmd_check_matrix,
        "check_spec": cmd_check_spec,
        "list": cmd_list,
    }[flag](tasks)


if __name__ == "__main__":
    sys.exit(main())