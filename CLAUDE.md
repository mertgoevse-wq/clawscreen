# ClawScreen — build rules for Claude Code

Compact operating manual. The full specification lives in `clawscreen-spec.md`;
this file is the short version you work from. Sections refer to that file.

## The one-run build loop (E19)

Per task, in this order, without asking:

1. Pick the next task: earliest `pending` task whose `depends_on` are all `done`.
   **Wave 1 (CS-010 … CS-016) has absolute priority (E26).** While a demo task is
   open and buildable, build it — even if a later wave is buildable.
2. Load its skills from `tasks/skill-matrix.md` (at least 2 per task, E15).
3. Implement.
4. Run the test written in the task file. **A task is `done` only when its own
   test passed.** "Wrote the code" is never done.
5. Set `status: done` in the task header, run `tools/sync_frontmatter.py --fix`.
6. Append the result to `progress/BUILD-STATE.md` — what was built, how it was
   tested with the real command and its real output, what is still open.
7. Commit and push (E16). Then continue with the next task.

End the run only when every task is `done` or listed as a blocker, and close
with the short report: **finished / open / blockers** (E32).

## Blocker rule (E24)

After **2 failed attempts** on a task: write it into `progress/BUILD-STATE.md` as a
blocker, continue with the next independent task, report all blockers at the end.
A run never ends silently.

## Hard limits on the phone (E28)

- **Allowed:** install packages in Termux and Debian, install the companion app,
  grant permissions, start and stop services, change settings automation needs.
- **Forbidden, always:** `pm uninstall`, deleting user files or folders, wiping
  the device, anything that removes user content, superuser/root.
- If a task seems to need one of the forbidden things: stop, write it into
  `progress/BUILD-STATE.md` as a blocker, continue.

## One adb server only (§5.1.1)

The adb server lives in **Termux**. Reach it from Debian with
`ADB_SERVER_SOCKET=tcp:127.0.0.1:5037`. Never start a second adb daemon, and
never run `adb kill-server` to "reset" it — the daemon is shared, so that also
kills Termux's. Restart with `adb nodaemon server` only if you intend to serve
both sides.

## Credentials (E35, §20.4)

The local model router key lives in the Termux environment (`OMNI_API_KEY`).
**Never write a key, token or password into this repository, into any task file,
into `CLAUDE.md`, or into any file that gets pushed.** Read it from the
environment at runtime. Never ask the user to paste a secret into a chat or file.

## Git discipline (E16)

- Commit and push after **every** task. GitHub is the only truth.
- Working tree must be clean before a task starts. Unpushed local commits may be
  squashed or dropped; the user allows this explicitly.
- **Forbidden:** local piles of uncommitted work; force-push over pushed history.
  (Exception agreed by the user on 2026-10-04: rewriting the trailer of commits
  that carried a wrong co-author line. Done with `--force-with-lease`, once,
  after a backup ref.)
- Commit message: `CS-0xx: <what was done and how it was tested>`, then a
  single line `Generated with <the agent that actually did the work>.`
- **No `Co-Authored-By` trailer.** It attributed the work to Claude while the
  work was done by a different agent. State what actually ran; do not copy a
  trailer that names someone who did not do it. Spec §14.3 still prescribes the
  Claude trailer — that line is superseded by this one, and the deviation is
  recorded in `progress/BUILD-STATE.md`.
- Push partial success too (tested state + blocker note) so a crash eats nothing.

## No AI slop (E20, §14.5)

Forbidden in README, docs and code: emoji in headings, superlatives without
proof, buzzword paragraphs, "contributions welcome!" without a process, placeholder
functions, fake tests, unfinished TODOs, files that belong to nothing.

Required in the README: working quickstart (copyable, tested on the phone), a
table of contents, a CI badge, an honest "Known limitations" section, a
troubleshooting chapter, real commands and tables instead of long prose.

`tools/anti-slop.py` checks this and runs in CI. A finding means red CI.

## Crash recovery (E17)

"resume", "weiter" or `/clawscreen-resume` runs
`.claude/skills/clawscreen-resume/SKILL.md`: read `progress/BUILD-STATE.md`,
compare against the file system, `git log` and the task headers **without
guessing**, re-run the last claimed task's test, repair deviations, continue at the
earliest open task.

## Skills (E15)

Community skills are installed globally (`npx skills add <owner/repo> --skill
<name> --yes`). Every build task has at least 2 assigned in
`tasks/skill-matrix.md`; load them before the task. In a conflict the project
skill wins over the community skill.

## When two parts of the spec disagree

Decide in favour of **Section 3 (decisions)** or **Section 14 (working rules)**,
and write the decision into `progress/BUILD-STATE.md`. Do not re-ask the user
unless a Section 18 assumption turned out to be false.