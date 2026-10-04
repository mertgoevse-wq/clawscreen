---
name: clawscreen-resume
description: Continue the ClawScreen build after a crash, a restart or an interruption. Use when the user says "resume", "weiter", "/clawscreen-resume", or after any interruption of a build run. Reads progress/BUILD-STATE.md, verifies it against the file system, git log and the task headers without guessing, repairs deviations, and continues at the earliest open task whose dependencies are met.
---

# Resume the ClawScreen build

Spec §14.4 (E17). The rule is simple: **only what can be verified counts.** If
this file and `progress/BUILD-STATE.md` disagree with the repository, the
repository wins and the disagreement gets repaired before anything new is built.

## 1. Read the claimed state

```bash
python3 tools/sync_frontmatter.py --list      # id, status, wave, deps
```

Read `progress/BUILD-STATE.md` end to end. Note the last `### CS-0xx` entry and
every open blocker. Do not skip the blockers section — a blocker explains why a
task is still open and must not be rediscovered by failing again.

## 2. Check the environment before the tasks

```bash
export ADB_SERVER_SOCKET=tcp:127.0.0.1:5037
adb devices -l                                  # is a phone connected?
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:20128/v1/models
```

One adb server only (spec §5.1.1). **Never `adb kill-server`** — the daemon is
shared with Termux. If the socket is refused, the daemon is down; start it once
with `adb nodaemon server &` and never start a second one.

If `adb devices` is empty, every task whose test says *on the real phone*
cannot pass. Do not build it anyway and do not mark it done: build the parts
that can be proved without the device, and record the device tests as open.

The model router on `localhost:20128` answers `401 invalid_api_key` when it is
alive and needs a bearer key, and nothing at all (curl `000`) when it is down.
Both states were seen on 2026-10-04. `401` means reachable, `000` means not —
`screen_describe` (CS-092) needs the reachable state, and a real model call
additionally needs `OMNI_API_KEY` in the environment. Never write that key into
a file (E35).

## 3. Verify the claimed work — re-run the tests

For the **last task that claims to be done**, re-run its own test command from
its task file. A claim in the build state is not evidence.

Then run the repository-wide checks:

```bash
python3 tools/sync_frontmatter.py --check
python3 tools/sync_frontmatter.py --check-matrix
python3 tools/sync_frontmatter.py --check-spec
python3 tools/anti-slop.py
python3 tools/build-reference-repos.py --check   # only if docs/reference-repos.md exists
cd mcp && npm test && npx tsc --noEmit            # only if mcp/ exists
```

## 4. Repair deviations

| Deviation | Repair |
|---|---|
| task header says `done`, build state has no `### CS-0xx` entry | the header is wrong → `sync_frontmatter.py --fix` sets it back to `pending` |
| build state has a `### CS-0xx` entry, header says something else | somebody wrote the entry before the test passed → `--fix`; re-run the task's test |
| a task is `#### CS-0xx — blocker: …` in the build state | header must say `blocked`; `--fix` aligns it |
| build state has an entry, test does not pass now | it was never really done → set `status: pending`, write the reason |
| `tools/sync_frontmatter.py --check` reports a mismatch | `python3 tools/sync_frontmatter.py --fix`, then re-run the check |
| a checker fails | fix the cause. Never weaken an assertion, skip a test or add a suppression to make a check pass |
| working tree is dirty | finish or drop the change; a task may not start on top of an unfinished one |

Heading levels in `progress/BUILD-STATE.md` carry meaning:

| Heading | Meaning | Effect on the task header |
|---|---|---|
| `### CS-0xx` | the task's own test passed | `--fix` sets `done` |
| `#### CS-0xx — blocker: …` | gave up after 2 attempts (E24) | `--fix` sets `blocked` |
| `#### CS-0xx` (no *blocker*) | progress note for a task that is **still open** | `--fix` leaves it alone |

```bash
python3 tools/sync_frontmatter.py --fix
git status --short
```

## 5. Pick the next task

Earliest `pending` task whose `depends_on` are all `done`. **Wave 1 (CS-010 …
CS-016) has priority over every later wave** (E26) while it is still open.

```bash
python3 tools/sync_frontmatter.py --list
```

Read `tasks/DEPENDENCIES.md` if the dependency looks wrong; spec §15.1 is
authoritative.

## 6. Load the assigned skills, then build

Read the task's row in `tasks/skill-matrix.md` and load at least those two
skills before implementing (E15).

## 7. Close honestly

- Only `done` when the task's own test passed, with its real output.
- After **2 failed attempts**: write it into `progress/BUILD-STATE.md` as a
  blocker and move on (E24).
- Commit and push after every task (E16). Commit message
  `CS-0xx: <what was done and how it was tested>`, footer
  `Co-Authored-By: Claude <noreply@anthropic.com>`.
- End the run with **finished / open / blockers** in plain words (E32).

## Never

- Never write a credential, token or password into any file in this repository
  (E35, spec §20.4). Read keys from the environment at run time.
- Never run `adb uninstall`, delete a user file, or use superuser (E28). If a
  task appears to need that, it becomes a blocker.
- Never `adb kill-server`.
- Never mark a task `done` because the code was written.