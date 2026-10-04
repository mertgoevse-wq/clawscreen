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
