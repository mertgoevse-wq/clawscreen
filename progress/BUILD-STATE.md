# ClawScreen — build state

This file is the truth about what is finished. After every task it records what
was built, how it was tested, and which git state was last pushed. The resume
skill compares this file against the file system and `git log` **without
guessing** — only what can be verified counts.

## Run log

### CS-001 — repository (2026-10-04)

**What:** private repository `mertgoevse-wq/clawscreen`, spec v2.1 and the v1.1
backup committed verbatim.

**Test:** `gh repo view mertgoevse-wq/clawscreen --json isPrivate`

```
{"isPrivate":true,"name":"clawscreen","url":"https://github.com/mertgoevse-wq/clawscreen"}
```

**Result:** passed. Push verified with `git ls-remote origin main` → `dbc5e8d`.

### CS-002 — CLAUDE.md, README, task templates (2026-10-04)

**What:** `CLAUDE.md` (compact build rules: loop, blocker rule, E28 limits, one-adb
rule, credential rule, git discipline, anti-slop, resume, skills), German
`README.md` skeleton with the NPU limitation stated honestly, and all 47 task
files.

**Test:** structure against Section 11 — every path exists.

```
CLAUDE.md 4472 bytes | README.md 5852 bytes | tasks 47 files
mcp cli companion skill/screen .claude/skills/clawscreen-resume .agents/skills
memory docs tools .github/workflows — all present
```

**Extra check:** the generator cross-checked the dependency table (Section 15.1)
against the wave list (Section 15): `mismatch … none`.

**Result:** passed.

## Decisions taken when the spec was unclear

- **The task-file generator derives short titles** from the first sentence of each
  task description rather than keeping a second hand-written title list. One
  source, no drift between title and description.
- **Task files are generated from the spec**, not transcribed by hand, so the
  dependency table and the wave list cannot disagree (§15.1 is authoritative).

## Environment facts measured on this phone (2026-10-04)

These are findings, not assumptions. They shape what is possible and they are
re-checked by the tasks that depend on them.

| Fact | Measured value |
|---|---|
| adb | `/usr/bin/adb` 1.0.41 (Debian). The adb **server** runs on port 5037 and is shared with Termux (§5.1.1). |
| Termux adb binary | **not present** at `/data/data/com.termux/files/usr/bin/adb`. Debian's own adb is the client. |
| Network namespace | Debian (proot) and Termux share one namespace `net:[4026531840]`, so loopback is shared in both directions. |
| Model router | omniroute v16.3.5 is running and **reachable** at `http://localhost:20128`; it answers `/v1/models` with `invalid_api_key`, i.e. it is alive and wants a bearer key from the environment. Never store that key in this repo (E35, §20.4). |
| adb devices | **no device connected at the start of the build.** |
| Phone self-wireless port | `45907` open on loopback **and** on `10.153.65.213` — the phone's own wireless-debugging daemon. `adb connect` reaches the transport but it stays `offline` until a one-time pairing code is accepted. |
| Pairing port | `44508` open on the LAN IP only. |
| mDNS discovery | `adb mdns services` returns **nothing** on this network, so automatic discovery cannot be relied on. |
| USB | `/dev/bus/usb` is not readable from proot, so a USB cable cannot replace the wireless route. |
| Device LAN IP | `10.153.65.213` |

### Incident: the shared adb daemon was stopped once

During the first environment probe, `adb devices` was run without
`ADB_SERVER_SOCKET`, which started a **second** adb daemon inside proot. Removing
it with `adb kill-server` stopped the **shared** daemon, so Termux's adb went down
too. The daemon was restarted immediately and both sides use it again.

**Rule for the rest of the build:** always set `ADB_SERVER_SOCKET=tcp:127.0.0.1:5037`
when talking to the phone, and never use `adb kill-server`. This is now written
into `CLAUDE.md`.

## Blockers

*(none yet)*

### CS-003 — CI workflows (2026-10-04)

**What:** `.github/workflows/repo-health.yml` (task consistency, skill matrix,
spec shape, anti-slop self-test + lint, then MCP build/test once `mcp/` exists)
and `.github/workflows/build-apk.yml` (companion APK as an artifact).

**Test:** both files parse as YAML and expose the expected steps.

```
OK   build-apk.yml: jobs=['apk'] steps=5
OK   repo-health.yml: jobs=['health'] steps=9
```

**Result:** passed. The MCP steps carry `if: hashFiles('mcp/package.json') != ''`
because the MCP server only arrives with CS-012 — they skip honestly instead of
failing or pretending to run.

### CS-004 — the two tools (2026-10-04)

**What:** `tools/sync_frontmatter.py` (five modes: `--check`, `--fix`,
`--check-matrix`, `--check-spec`, `--list`) and `tools/anti-slop.py` (six rules
plus a broken-link check, with `--self-test`).

**Test:**

```
python3 tools/anti-slop.py --self-test   -> OK: self-test passed — 4 rules and the link check each catch their case
python3 tools/anti-slop.py               -> OK: 6 rules clean over 2 file(s)
python3 tools/sync_frontmatter.py --check      -> OK: 47 task headers consistent (2 done, 45 open)
python3 tools/sync_frontmatter.py --check-spec -> OK: spec present (93349 bytes, all 7 sections found)
python3 tools/sync_frontmatter.py --check-matrix -> FAIL: tasks/skill-matrix.md is missing (E15)
```

**Result:** passed. The last line is the correct, honest state: the matrix is
CS-005's job, so the checker reports it as missing rather than passing silently.

**Bug found and fixed while testing:** `main()` dispatched on `vars(args)` keys,
which are `check` / `check_spec`, not `--check` / `--check-spec`, so every mode
raised `KeyError`. Fixed by keying the dispatch table on the bare names.

**Side effect worth keeping:** the lint caught a real broken link in README.md on
its first real run (`docs/fortschritt.md` did not exist). That file now exists,
which is why the second run is clean. A linter that has never found anything is
not a proven linter.

### CS-005 — skill hunt (2026-10-04)

**What:** baseline skills installed from `anthropics/skills` and
`gradle/gradle-skills` (spec §22 category E) before any hunting, then a search
over the §14.2 terms. Six skills installed and documented in
`.agents/skills/README.md`, `tasks/skill-matrix.md` written with at least two
skills per task for all 47 tasks, `tasks/DEPENDENCIES.md` added (§11 lists it).

**Test:**

```
python3 tools/sync_frontmatter.py --check-matrix
OK: every one of 47 tasks has a test and at least 2 skills
```

**Negative test of the checker** (a check that never fails is not a check):
removing one skill from the CS-011 row gives `CS-011: only 1 skill(s)` and exit 1.

**Installed:** `mcp-builder`, `skill-creator` (anthropics/skills),
`gradle-best-practices` (gradle/gradle-skills), `android-design-guidelines`,
`android-native-dev`, `tdd`.

**Result:** passed, with one deviation recorded below.

**Deviation:** the spec asks for a *global* install. This build's agent runner
rejects it (`PromptScript does not support global skill installation`), so the
skills live in `.agents/skills/` and are loaded by name exactly as before. The
rejected candidates (web skills, document skills, Slack) are listed with the
reason in `.agents/skills/README.md` so nobody re-hunts them (E20).

**Bug found and fixed while testing:** `sync_frontmatter.py --check-matrix`
counted commas across *all* table columns, so a row with one real skill plus a
comma in its explanation column counted as two. It now parses the table by
header name and counts only the `Skills` column.

#### CS-006 — reference projects (2026-10-04): document written, task still open

**What:** `tools/build-reference-repos.py` turns spec §22 into
`docs/reference-repos.md`, merging metadata read live from the GitHub API. A
take-over ledger records which take-overs are actually implemented.

**Test:**

```
python3 tools/build-reference-repos.py --live
OK: wrote docs/reference-repos.md — 65 rows, 7 categories
python3 tools/build-reference-repos.py --check
OK: docs/reference-repos.md matches the spec (65 rows, 7 categories)
```

**Link check:** all 61 distinct repositories were queried through
`gh api repos/<name>`; **61 answered, 0 failed**, so every link still resolves.
Stars and last-push dates come from that response, not from the spec text.

**Negative test of `--check`:** changing one star count in the document makes it
fail with `out of date` and exit 1.

**Why CS-006 is not marked done:** its test also demands "at least one scrcpy
take-over that CS-010 actually uses". CS-010 has not been built, so that clause
cannot be honestly claimed. The ledger therefore reads `0 of 6 take-overs are
implemented`, and the task stays `pending` until CS-010 exists.

## Open blocker: no phone is connected (blocks most of wave 1 and later)

Measured on 2026-10-04, 21:40, with the shared adb daemon restarted first
(it was down; `adb.5037` pointed at Debian's own adb binary).

| Probe | Result |
|---|---|
| adb server on `tcp:127.0.0.1:5037` | was **down**, restarted as `adb nodaemon server`; Termux has no own adb binary, so this is the one and only server (§5.1.1) |
| `adb connect 127.0.0.1:45907` | transport created, then **`offline`** |
| `adb devices` after `adb reconnect` | list empty again |
| wireless-debugging **pairing** port (was 44508) | **closed** — no pairing code can be obtained |
| `adb mdns services` | empty (already known: no mDNS on this network) |

So the phone's own wireless-debugging daemon answers on 45907, but this adb key
is not authorized for the current session, and the pairing dialog that would
issue a fresh 6-digit code is not open. Nothing in the build can fix that from
outside — it needs the one-time pairing (spec §12.1), which the user performs
once in the phone's Settings.

**Consequence, stated plainly:** every task whose test says *on the real phone*
cannot pass in this state and must stay open or become a blocker. Everything
that can be proved without the device — the MCP server, the tool layer against a
scripted fake adb, safety, session, memory, the companion app build in CI, the
documentation, the linters — can be built and tested, and that is the order the
next run should use.

## Second environment blocker: the local model router stopped answering

Measured 2026-10-04, 21:52. Same URL, two different states within minutes:

```
21:39  curl http://localhost:20128/v1/models  -> 401 {"error":{"type":"invalid_api_key"}}
21:52  curl http://localhost:20128/v1/models  -> 000 (connection refused in 3 ms), 3 tries
```

`401` means the router is alive and wants a bearer key. `000` means it is not
listening at all. It stopped during this build. `OMNI_API_KEY` is also not set
in this session's environment.

**Consequence:** CS-092's test ("a real call proves one working model") cannot
pass right now. Its unit-test half — the fallback chain, the `max_tokens >= 2048`
rule, a 402 moving down the chain — can be built and tested against a fake router.
The real call is recorded as an open blocker, not worked around.
