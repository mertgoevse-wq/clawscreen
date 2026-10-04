# ClawScreen — Build Specification (version 2.1)

**Date:** 2026-10-04
**Status:** Ready to build (nothing built yet)
**Who wrote it:** an interview with the project owner. Everything here is a decision, not a suggestion.

**Previous version:** `clawscreen-spec-v1.1-backup.md` (kept for reference only — do not build from it).

**What version 2.1 adds** (all measured on the real phone on 2026-10-04, not researched on paper):

| Addition | Where | Why it exists |
|---|---|---|
| Decisions E34–E37 | Section 3 | Which model looks at the screen, where credentials come from, what the chip can really do, and the thinking-token trap. |
| **Section 20** | new | The model list **with measured vision results and latencies**, the measured list of what does *not* work, and the credential rule. |
| **Section 21** | new | GPU yes / **NPU no — verified on the device**, and what the hardware is honestly used for. |
| **Section 22** | new | 65 researched GitHub entries (59 distinct repositories) in 7 categories with live metadata, a binding take-over decision each, and the install commands. |
| Wave 10 (CS-092 … CS-097) | Section 15 | Tasks that make the phone use its own chip. They run **after** v1.0 and are never in the way. |
| A10–A13 | Section 18 | The measured facts, written as settled rather than as guesses. |

**How to read this file if you are Claude Code:**

**START HERE (Section 0) — read it before anything else.** It tells you how to begin and that you work alone.

1. **Section 3** = the decisions. They are settled. Do not re-ask.
2. **Section 2** = the word list. Every hard word is explained there. If you meet a word that is not in that list, explain it in plain words inside `CLAUDE.md` instead of guessing.
3. **Section 15** = the build plan (waves and tasks). `tasks/` plus `progress/BUILD-STATE.md` are the only truth about what is finished.
4. **Section 14** = how you work while building (loop, git, crash recovery).
5. **Sections 20–22** = measured facts, not plans: which model sees, what the chip can do, and which repositories to use. They were measured on the real phone on 2026-10-04. **Treat them as findings, not as opinions — but re-check them if reality disagrees (task CS-097).**
6. If two parts of this file disagree: decide in favour of Section 3 or Section 14, and write the decision into `progress/BUILD-STATE.md`.

---

## 0. How to start this build (read first)

When the user says **"Build everything to the final product"**, do exactly this:

1. Read **this whole file** from top to bottom before writing any code.
2. Create the repository as described in **Section 16** (private GitHub repository `mertgoevse-wq/clawscreen`).
3. Do **not** ask the user anything unless Section 18 lists it as an assumption that turned out to be false. Everything else you decide yourself and write the decision into `progress/BUILD-STATE.md`.
4. Work through **Section 15** task by task using the loop in **Section 14.1**: load skills → implement → test → update build state → commit and push → next. **The demo slice (CS-010 … CS-016) comes before everything else** (E26).
5. **Hard limits for the whole run (Section 9.5):** never delete an app, never delete a file of the user's data, never use superuser access. If a task seems to need one of these, mark it as a blocker and continue.
6. **After 2 failed attempts on a task** (E24): write it into `progress/BUILD-STATE.md` as a blocker, continue with the next task, and report it at the end.
7. End the run only when every task is `done` or listed as a blocker. Finish with the short report: **finished / open / blockers** (E32).

**If you are interrupted or the phone restarts**, the user says "resume" and you continue per Section 14.4.

---

## 1. What this project is

ClawScreen lets Claude Code **see and operate the whole screen of the user's own phone**, on its own, without asking for every step. It works like an assistant who looks over your shoulder and replaces your fingers.

Example: the user types `/screen` and says *"Build me a project in Cubasis with a drum track and a bass line, tempo 100."* Claude then sees the screen, plans, taps, swipes, types, checks every step against a fresh picture, and reports what it did. Not only music apps — anything on the screen: settings, apps, any operation.

---

## 2. Word list (plain explanations)

This file is written so a person with no technical background can read it, while still giving Claude Code every detail it needs.

| Word | Plain meaning |
|---|---|
| **ADB** | Android's built-in "service door". From outside it you can take pictures of the screen, tap, swipe, type text and start apps. It works on the same phone over "wireless debugging". No superuser access needed. |
| **Superuser (root)** | Full control over Android that manufacturers block. This project never uses it and never needs it. |
| **Wireless debugging** | A switch in the phone's developer settings that opens the ADB service door. You turn it on once with a 6-digit pairing code. The small "port number" it uses changes after restarts, so the project needs an automatic way to find it again (Section 12). |
| **Port** | A small number, 4–5 digits, that names a door into a program. The debugging door's number changes; that is why it must be looked up automatically. |
| **MCP** | A standard plug format. Claude Code can use extra "tools" through it as if they were built in. ClawScreen offers its tools (look, tap, swipe, type) as one MCP server. |
| **Tool** | One single ability that Claude can call, for example `screen_tap`. |
| **Accessibility service (German: Zugangshilfe)** | A special permission Android gives to some apps, for example screen-reader apps for blind people. Such an app may read the screen content in detail and perform system gestures (back, home, paste). |
| **Screen inventory (uiautomator dump)** | A list of all buttons and text fields on the screen with their positions, like an inventory list. It returns almost nothing in apps that draw their own graphics, such as Cubasis and FL Studio Mobile. |
| **Vision** | Claude can look at and understand pictures. Pictures of the screen are Claude's eyes when the inventory list gives nothing away. |
| **Skill** | A reusable instruction sheet Claude Code can load — either written by us or installed from the community. |
| **AI slop** | Dressed-up, interchangeable AI output: big claims without proof, emoji soup, buzzword paragraphs, placeholder functions, fake tests. Forbidden here and checked by a script (Section 14.5). |
| **Resume** | The command ("resume" / "weiter") that after a crash picks up the last **verified** build state (compare files, git log and the state log) and continues building by itself. |
| **Session** | A period in which ClawScreen is actively watching the screen. Started with `/screen`, ended with `/stop`. |
| **Blocklist (Sperrliste)** | A list of apps Claude may never operate (during the build phase: all money and shopping apps). |
| **APK** | The installation file of an Android app (like a .exe on Windows). |
| **Waves** | Build phases. Tasks that depend on each other run in order; independent tasks may run side by side. |
| **Build state (Checkpoint)** | The file `progress/BUILD-STATE.md`. After every finished task it records what is done, how it was tested, and which git state was last pushed. This is what makes resuming after a crash possible. |
| **Demo slice** | A small but genuinely working part built first, so the user can see something real early and confirm the approach. |
| **Blocker** | A task that failed twice. It is written into the build state and skipped; the build continues with other tasks and reports it at the end. |
| **Model** | The thinking program that answers. A "model with vision" can look at a picture; a text-only model cannot. |
| **Local router** | A small server on the phone (`http://localhost:20128`) that hands a request to whichever model provider is available. It speaks the usual OpenAI-style format, so our code talks to it like any other endpoint. |
| **Provider** | Where a model comes from. `agy` and `antigravity` are two Google accounts; `openrouter`, `gemini`, `nvidia` and many others are different services with their own credit and their own failures. |
| **Fallback chain** | The ordered list of models to try when the first one fails (Section 20.1). The next one is used **only** after an error, and the switch is logged. |
| **Reasoning / thinking tokens** | Part of the answer budget a model spends thinking before it replies. If the budget is too small, nothing is left for the actual answer (E37). |
| **GPU** | The graphics processor. On this phone: Samsung Xclipse 540, reachable through **Vulkan** (a modern graphics interface). Useful for local image work. |
| **NPU** | The neural processor — a chip part specialised for AI. This phone has one, but **apps cannot reach it** (Section 21.1). |
| **Vulkan** | The graphics interface used to talk to the GPU. Verified present on this phone. |
| **TOPS** | "Trillion operations per second" — a rough measure of how much a chip can compute. Only used to describe marketing numbers here, never as a promise. |
| **OAuth** | The standard way an app gets permission to use a service **without ever handling the password**. Both Google accounts are connected this way (E35). |

---

## 3. Decisions (settled — do not re-ask)

| # | Topic | Decision |
|---|---|---|
| E1 | Control path | **ADB as the base, plus a small extra app** ("ClawScreen Companion") that has the accessibility permission. Full coverage, no root. |
| E2 | Relation to ClauDroide | **Separate project with a bridge**: its own repository, but interfaces designed from day one so it can later be plugged into ClauDroide. |
| E3 | How autonomous | **Fully autonomous** — no step-by-step questions in normal operation. Limits see E10. |
| E4 | First real test | **Music first**: Cubasis 3 and FL Studio Mobile are the first two real tests. |
| E5 | Ways to use it | **Both**: short single commands **and** a running `/screen` session. |
| E6 | Emergency brakes | **All three**: terminal (`/stop` or Ctrl+C), floating stop button on the screen, volume keys (double-press "volume down"). |
| E7 | Music apps | Cubasis 3, FL Studio Mobile, **and general coverage** of all other apps. |
| E8 | Operating memory | **Yes, with notes**: per-app saved hints (positions, sequences) that get better with every use. |
| E9 | Keeping the screen awake | **Allowed**: during a session the display stays on, switched off again automatically at the end. |
| E10 | Money apps | **Stay completely blocked** for the whole project (bank, payment, shopping apps). The switch to loosen it exists in code from day one, set to `blocked`. |
| E11 | Language | **German and English**, freely choosable in the configuration. |
| E12 | Task lists | **Yes**: multi-part requests ("1. …, 2. …, 3. …") are worked through as a visible list that can be extended in between. |
| E13 | Repository creation | **Fully automatic**: folder, git, private GitHub repository `mertgoevse-wq/clawscreen`, first upload. |
| E14 | Future chapter | **Yes**, an outlook section so the foundation fits later (Section 17). |
| E15 | Skills | Claude Code **finds, installs and uses** community skills automatically. Every build task gets at least 2 assigned skills (skill matrix), loaded by the build loop. |
| E16 | Git discipline | **Commit and push after every single task.** Local commits that were never pushed may be squashed or dropped. GitHub is the only truth. |
| E17 | Crash recovery | Command **"resume"** (`/clawscreen-resume`, "resume", "weiter") picks up and continues by itself. |
| E18 | Reference projects | **50+ GitHub repositories researched and curated**, the best ones installed and actually used while building — documented in `docs/reference-repos.md`. |
| E19 | One-run build | Master command **"Build everything to the final product"**: one autonomous run that only ends when all tasks are done or a safety rule forbids going on. Crash-safe through E16 + E17. |
| E20 | No AI slop | README and code at a high standard, no AI filler, working quickstart, honest limitations — checked by a script in CI. |
| E21 | UI design skills | **Mandatory** for every screen of the companion app (adaptive layout, Material 3, touch target size, dark mode). |
| **E22** | **Picture transport** | **Use the finished scrcpy base** (a proven open-source tool) for the live picture stream and for fast taps. Own implementation is only a fallback if scrcpy turns out not to work. |
| **E23** | **When the stream runs** | **Only while Claude is actually looking.** No permanent stream. Protects battery, costs almost no extra delay. |
| **E24** | **When a task fails** | **After 2 failed attempts:** write it into the build state as a blocker, continue with the next task, report all blockers at the end. The build never ends silently. |
| **E25** | **Language of this file** | **English**, so Claude follows it strictly. Every hard word is explained in Section 2 and must be explained plainly in the README for the user. |
| **E26** | **Build order** | **First a working demo slice in a single session**, then everything else. The user sees something real early and can confirm the approach. |
| **E27** | **Scope** | **One cut: everything needed, no luxury items.** 41 tasks instead of the 60 of version 1.1 (version 2.1 adds 6 optional ones in Wave 10, so 47). E18 (50+ reference repos) is explicitly kept — it is not a luxury item. |
| **E28** | **Permissions for Claude** | Claude may do **everything it needs**, including granting permissions and starting services — but **deleting apps and deleting data is forbidden, always.** |
| **E29** | **Permissions for the user** | The user grants the companion app's permissions **once**; Claude only checks afterwards that everything is still in place. |
| **E30** | **Pairing** | Claude tries several connection ways automatically and **asks out loud** only when none of them work. |
| **E31** | **Speed** | **Under 2 minutes for a typical task.** The user gets a short report after each finished step. |
| **E32** | **Logging** | **Log everything.** Log files and pictures stay on the phone. Build progress goes to GitHub; a short final report closes the run. |
| **E33** | **Money apps, again** | Confirmed: blocklist stays on, completely. |
| **E34** | **Which model looks at the screen** | Measured on 2026-10-04, not guessed (Section 20). **`agy/gemini-3.7-flash-high` is the default "eyes"** (2.1 s measured, reads pictures correctly). `agy/gemini-pro-agent` for hard cases. **Never** `*/claude-*` on the agy/antigravity providers — they time out. |
| **E35** | **Where the models come from** | **Only the two Google AI Pro accounts work** (providers `agy` and `antigravity`, already connected via OAuth, no password anywhere). OpenRouter, direct Gemini API and Perplexity have **no credit or are disabled** (Section 20.2). Claude Code never stores a password or key in the repository — ever. |
| **E36** | **Use the phone's own chip** | **GPU via Vulkan is real and usable** (`vulkan.samsung.so` present, Xclipse 540). **The NPU is not reachable** — there is no NNAPI driver on the device (Section 21). So local helpers use the **GPU**, and no spec claim may promise NPU. |
| **E37** | **The thinking-token trap** | Reasoning models spend `max_tokens` on thinking. With `max_tokens: 150` the models returned only `"The"`. **Every vision call uses `max_tokens >= 2048`** (measured proof in Section 20.3). This is a bug that would otherwise look like "the model cannot see". |

### 3.1 What changed against version 1.1 (and why)

| Change | Reason |
|---|---|
| This file is in English | E25 — models follow English instructions more strictly. |
| Video stream added, scrcpy chosen as the base | E22, E23 — much faster and smoother than taking single pictures over ADB. |
| Task count cut from 60 to 41 | E27 — fewer moving parts means the autonomous run is less likely to stall. |
| **Version 2.1 adds Wave 10 (CS-092 … CS-097)** | The user asked for the phone's NPU and GPU to be used. Measured honestly: the **GPU is usable, the NPU is not reachable** (Section 21.1). Wave 10 therefore uses the GPU and CPU, runs **after** v1.0, and is optional — 6 tasks, not a rewrite of the plan. |
| "Demo slice first" | E26 — the user wants to see something real early. |
| Blocker rule now explicitly "2 attempts, then skip and report" | E24 |
| Section 17 (outlook) shortened | E27 |
| 50+ reference repos **kept** | Explicitly requested after the interview — not a luxury item. |

---

## 4. The device (fixed, not "any Android phone")

| Part | Value |
|---|---|
| Phone | Samsung Galaxy A56 5G (6.7 inch, 1080 × 2340 pixels, 120 Hz, 8 GB RAM) |
| Android version | Android 15 with Samsung "One UI" 7 |
| Terminal app | **Termux** (brings a Linux command line to the phone) |
| Linux inside Termux | **Debian**, installed via `proot-distro` (a "Linux inside Linux" that does not touch the phone system) |
| Assistant | **Claude Code runs inside Debian**, in `/home/mert/<project>` |
| Project location | `/home/mert/clawscreen` |
| GitHub account | `mertgoevse-wq` |
| Superuser access | **Not available and not needed** |
| Chip | **Samsung Exynos 1580** (verified: ARM CPU part `0xd80` = Cortex-X4, 1 × 2.9 GHz + 3 × Cortex-A720 + 4 × Cortex-A520) |
| Graphics (GPU) | **Samsung Xclipse 540** (AMD RDNA 3 based), **Vulkan driver present and usable** (verified: `/vendor/lib64/hw/vulkan.samsung.so`) |
| NPU | Exists in hardware (~14.7 TOPS) but **not reachable from apps** — verified: no NNAPI driver present (Section 21.1). Samsung only exposes it to selected partners. |

**The important consequence:** Claude Code runs on the very phone it controls. It may install anything it needs in Termux or Debian, and it may test on the real phone directly. "Tested on device" is the normal case, not the exception.

---

## 5. What the pieces are and how they work together

```
┌─────────────────────────── Samsung Galaxy A56 ────────────────────────────┐
│                                                                            │
│  ┌────────────────────── Termux ─────────────────────────┐                │
│  │  adb server (package android-tools, door number 5037)  │                │
│  │  connected to "itself": 127.0.0.1:<port>               │                │
│  │  scrcpy server (picture stream + fast taps, pushed in) │                │
│  └────────────▲───────────────────────────────────────────┘                │
│               │  ADB: start apps, key events, install, read inventories     │
│  ┌────────────┴────────────── Debian (proot) ─────────────┐                │
│  │  Claude Code                                              │                │
│  │   ├─ /screen skill          (how a session behaves)      │                │
│  │   ├─ /clawscreen-resume     (crash recovery)            │                │
│  │   ├─ MCP server "clawscreen" (TypeScript/Node)          │                │
│  │   │    ├─ tools: screen_* (Section 7)                   │                │
│  │   │    ├─ screen transport: scrcpy server, base layer    │                │
│  │   │    └─ blocklist, session log (Section 6), memory (Section 8) │          │
│  │   ├─ CLI "clawscreen" (pair/connect/status/stop/…)       │                │
│  │   └─ globally installed community skills                  │                │
│  └──────────────────────────────────────────────────────────┘                │
│                                                                            │
│  ┌────────────── ClawScreen Companion (APK) ───────────────┐                │
│  │  accessibility: read protected screens, system          │                │
│  │    gestures, catch volume keys                           │                │
│  │  floating stop button (always on top)                    │                │
│  │  keep-awake service during sessions                      │                │
│  │  tiny local server 127.0.0.1:8765 → state / brakes      │                │
│  │  typing umlauts and special characters via clipboard     │                │
│  └──────────────────────────────────────────────────────────┘                │
│                                                                            │
│  Whatever app is in front (Cubasis 3, FL Studio Mobile, Settings, …)       │
└────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Hard conditions Claude must respect while building

1. **Where adb lives.** In **Termux** (package `android-tools`). The Debian side reaches it by setting the environment variable `ADB_SERVER_SOCKET=tcp:127.0.0.1:5037`, so the adb client inside Debian talks to the one adb server inside Termux. **Only ONE adb server may exist** — never start a second one.
2. **Picture and tap transport = scrcpy (E22).** scrcpy is an existing open-source tool that streams the screen as a fast video and accepts injected taps, swipes and key presses. Claude pushes the scrcpy server onto the phone once (`adb push`), starts it, and then:
   - **looks** = start or continue the stream and take the current frame (E23: only while looking),
   - **taps** = send an input event through the scrcpy control channel,
   - **falls back** to plain ADB (`screencap`, `input tap`) if scrcpy cannot be used — the tools must work either way.
3. **Connecting to itself.** Android 11 and later offer wireless debugging also for `127.0.0.1` ("this device itself"). One-time: Settings → Developer options → Wireless debugging → "Pair device with pairing code" → `adb pair 127.0.0.1:<pairing port>` plus the 6-digit code → then `adb connect 127.0.0.1:<connect port>`. The pairing dialog must stay visible while pairing, so the user reads the code into the terminal. This is what `clawscreen pair` does (Section 12).
4. **Ports change.** After a restart the connect port changes. Therefore the `connect` routine tries several ways and, with the companion app, can find the current port automatically (Section 12).
5. **Inventories are not always available.** Screenshots and the scrcpy stream work everywhere; `uiautomator dump` returns almost nothing in apps that draw their own graphics (Cubasis, FL Studio Mobile). There, Claude relies on looking at pictures.
6. **Resolution and coordinates.** The device is 1080 × 2340. Pictures handed to Claude are scaled down (default width 840 px, JPEG quality 85) to save time and tokens, but **every tap coordinate must be given in real device pixels** — the tool converts and documents the factor. `wm size` gives the truth at run time.
7. **Everything stays local.** No data leaves the device, apart from Claude's own requests to Anthropic that the user already allows through Claude Code.

---

## 6. The two ways to use it

**A) Session mode — `/screen`**
1. **Prepare (automatic):** `clawscreen status` → is the connection up? is the companion app reachable? If not: try to repair automatically, and only then ask the user (E30).
2. **Start:** `session_start` → keep screen awake, show the stop button, open a log file `~/.clawscreen/logs/YYYY-MM-DD-HHMM.md`.
3. **First look:** Claude gets an overview and reports briefly what it sees.
4. **Take the request:** the user speaks freely (German or English). Claude breaks it into a task list (E12) and shows it numbered.
5. **Work cycle per task:**
   a. check memory (`memory_read`) → b. act (tools) → c. **verify** (fresh picture, compare with expectation) → d. report in one or two sentences → e. extend the memory if something new and reliable was learned.
   **Surprise rule:** if the screen differs strongly from expectation (unexpected dialog, wrong app, error message, network hint) → **stop immediately**, show the picture and the observation, and wait for a new instruction or "continue".
6. **In between:** new wishes extend the list; "stop" aborts the current task; every action is written into the log with time and picture path.
7. **End:** `/stop`, stop button, or double volume-down → abort, switch keep-awake off, hide stop button, final report (what is done, what is open, anything odd that was noticed).

**B) Single-command mode** — same tools, no session: `clawscreen run "Open Settings and turn Bluetooth off"` → Claude plans, acts, reports, ends. Blocklist and surprise rule apply here too.

**Speed target (E31):** a typical five-step task is finished in under 2 minutes, with a short report after each finished step.

**Logging (E32):** everything is logged — every action, every picture path, every report — in files on the phone. Build progress additionally goes to GitHub (Section 14). The run ends with one short final report: finished / open / blockers.

---

## 7. The tools (Claude's hands and eyes)

All tools start with `screen_` so they form one clear block in Claude Code's tool menu. Every answer contains `ok`, `screenshot_ref` (path to the fresh picture), `ui_inventar` (when available) and `notiz` (one short sentence in the session language).

### 7.1 Seeing

| Tool | What it does | How |
|---|---|---|
| `screen_look` | Current picture, plus inventory if possible | Preferred: current frame from the scrcpy stream. If the stream is not running, start it, take the frame, stop it again (E23). Fallback: `adb exec-out screencap -p`. Scale to analysis size. In parallel `uiautomator dump` with a 3-second time limit, tolerant of failure. **Optional GPU pre-check** (Section 21.3): skip the round trip when the screen has not changed since the last look. |
| `screen_describe` | Have a model read the picture and answer a question about it | Sends the picture to the local router (`http://localhost:20128`). **Default model `agy/gemini-3.7-flash-high`; fallback chain and measured numbers in Section 20.1. Always `max_tokens >= 2048` (E37).** Used by `/screen` and by tests; a normal `screen_look` does not need it because Claude itself sees the picture. |
| `screen_look_region` | Zoom into a part of the screen | Cut out a rectangle around a coordinate, full resolution |
| `screen_apps` | List of installed apps with their package names | `adb shell pm list packages -3` (option for system apps) |
| `screen_foreground` | Which app is in front right now | `adb shell dumpsys activity activities`, read `topResumedActivity`, safe on One UI |

### 7.2 Acting

| Tool | What it does | How |
|---|---|---|
| `screen_tap` | Tap at (x, y) in real device pixels | scrcpy input channel; fallback `adb shell input tap` |
| `screen_long_press` | Long press | swipe with same start and end point, 800 ms |
| `screen_swipe` | Swipe from start to end over a duration | scrcpy input channel; fallback `adb shell input swipe` |
| `screen_drag` | Drag with intermediate points (sliders, keyboards) | several `input swipe` steps |
| `screen_text` | Type text into the focused field | Plain letters: `adb shell input text`. Umlauts and special characters: clipboard route via the companion app (Section 7.4) |
| `screen_key` | System buttons: BACK, HOME, RECENTS, ENTER, DEL, VOLUME UP/DOWN … | `adb shell input keyevent KEYCODE_*` |
| `screen_open_app` | Start an app | `adb shell monkey -p <package> 1` (more reliable than resolving a launcher intent) |
| `screen_wait_change` | Wait until the screen changes, up to a time limit | Compare frames in a loop |
| `screen_scroll_to` | Keep swiping until a search term appears in the inventory or the picture | Combine swipe and look |

### 7.3 Thinking and organising

| Tool | What it does |
|---|---|
| `session_start` / `session_status` / `session_stop` | Start a session (keep awake on, show stop button, open log), read the state, end it cleanly (keep awake off) |
| `tasklist_set` / `tasklist_update` | Create and update the task list (E12); carried in the log and in every report |
| `memory_read` / `memory_write` | Read and write the operating memory (Section 8) |
| `safety_check` | Check the planned app and action against the blocklist (Section 9) — **runs automatically before every acting tool** |

### 7.4 The umlaut problem and its solution

`adb shell input text` cannot type umlauts (ä ö ü ß) and only some special characters. Solution via the companion app:

1. The MCP server puts the text into the Android clipboard through the companion app (`POST /clipboard` to `127.0.0.1:8765`).
2. The MCP server triggers paste (`POST /paste`); the companion app performs the paste action on the focused field using its accessibility permission.
3. Fallback without the companion app: type the text key by key using a key code table (slow), or ask the user to use plain spelling.

The tool decides automatically based on which characters occur in the text.

---

## 8. The operating memory (E8)

**Where:** `~/.clawscreen/memory/<package-name>.json` — and for the two music apps also in the repository under `memory/`, so the starting knowledge is versioned.

**Shape (example `cubasis3.json`):**
```json
{
  "app": "com.steinberg.cubasis",
  "zuletzt_geprueft": "2026-10-04",
  "aufloesung": [1080, 2340],
  "anker": {
    "projekt_neu": { "koordinaten": [980, 2200], "sicherheitspruefung": "Dialog 'Neues Projekt' sichtbar", "vertrauen": 0.9 },
    "spur_hinzufuegen": { "koordinaten": [540, 2290], "vertrauen": 0.8 }
  },
  "rezepte": {
    "projekt_anlegen": [
      "screen_open_app com.steinberg.cubasis",
      "wait for main view (title 'Cubasis' or project list)",
      "screen_tap anker.projekt_neu",
      "screen_tap confirm button",
      "verify: empty timeline visible"
    ]
  },
  "hinweise": [
    "The screen is drawn by the app itself: uiautomator returns almost nothing — use pictures",
    "Allow 2.5 seconds of loading time after starting the app"
  ]
}
```

**Rules:**
- Every stored coordinate gets a **safety check** ("how do I know I am in the right place") and a **confidence value**. Below 0.5, the tool insists on a zoomed look before tapping.
- Every confirmed success raises the confidence, every miss lowers it and triggers re-discovery.
- If resolution or layout changed (visible through systematic misses), ClawScreen discards that app's anchors and rebuilds them.

---

## 9. Safety

### 9.1 Autonomy (E3)
No step-by-step questions. Claude acts within this specification and **reports continuously**.

### 9.2 Money apps stay blocked (E10, E33) — for the whole project
- Default list, stored in `~/.clawscreen/config.json` under `deny_packages`:
  - `com.android.vending` (Google Play — this closes off all purchases),
  - packages matching common banking and payment patterns (name contains `bank`, `banking`, `paypal`, `klarna`, `payment`, `wallet`); the configurable list is what finally decides,
  - an extra rule: **never confirm a purchase dialog**, even in an allowed app. Detection: dialog text contains "kaufen", "Kauf", "€", "$", "Preis bestätigen" → abort and report.
- Blocked attempts are written into the log and reported to the user.
- A switch exists in the code from day one with three values: `blocked` (set as delivered), `announce` (say it out loud first, then act), `open`. **The default stays `blocked`.**

### 9.3 Three emergency brakes (E6) — at any time, in any situation
1. **Terminal:** `/stop` in the chat or Ctrl+C ends session and task immediately; `clawscreen stop` is the hard way (aborts running input transfers and switches keep-awake off).
2. **Stop button:** a red floating circle from the companion app, always on top, movable, 64 dp. Tapping it → the companion app reports STOPP to `127.0.0.1:8765`, the MCP server aborts the running action (every gesture is limited by a time limit, at most 1.5 seconds, so nothing "runs through"), the session pauses, the phone vibrates.
3. **Volume keys:** the companion app catches a **double press of "volume down"** (within 600 ms) through its accessibility permission → same STOPP behaviour. A single press passes through normally.

### 9.4 Further hard rules (enforced in `safety.ts`, not just intended)
- At most 1 action per 300 ms (protection against runaway loops).
- **Every answer of an acting tool must contain a fresh picture** — no action is ever done "blind from memory".
- A session without a reply from the user pauses automatically after 15 minutes (the display stays awake until the user reacts; it ends 5 minutes later).
- Log size is limited: the picture folder rotates at 200 MB, oldest first.

### 9.5 What Claude is allowed and forbidden to do on the phone (E28)
- **Allowed:** install packages in Termux and Debian, install the companion app, grant permissions, start and stop services, change settings the automation needs.
- **Forbidden, always:** deleting apps (`pm uninstall`), deleting files or folders of the user's data, wiping the device, and anything that removes user content.
- If a task appears to need one of the forbidden things: stop, write it into the build state as a blocker, continue.

### 9.6 How Claude gets permission from the user (E29)
The user grants the companion app's permissions **once**, during setup. Claude only checks whether they are still in place (`clawscreen status`) and tells the user in one sentence what is missing. It does not walk the user through the permission screens again.

---

## 10. The companion app (short version)

**Purpose:** everything ADB alone cannot do or does awkwardly — reading protected screens, system gestures, clipboard, catching volume keys, stop button, keeping the screen awake, automatic reconnection.

**Permissions, each with a reason:**

| Permission | For what |
|---|---|
| Accessibility | reading screen content (also where the inventory fails), system gestures (back/home/recents/paste), catching volume keys |
| Draw over other apps | the stop button |
| Foreground service + keep awake | keeping the screen awake during sessions (E9), stable local server |
| Vibrate | confirming emergency brakes |
| Internet | **only** for the `127.0.0.1` local server, no network traffic |

**Local server (HTTP on `127.0.0.1:8765`, reachable only locally):**
- `GET /health` → reachable and state
- `GET /state` → stop pressed? sleep state? last gesture?
- `POST /clipboard` {text} → sets the clipboard
- `POST /paste` → triggers paste on the focused field
- `POST /keepawake` {on|off}
- `POST /stopbutton` {show|hide}

No password needed (localhost only). The app additionally checks that the caller belongs to the Termux/Debian environment as far as that can be done reliably.

**Not in the Play Store:** the APK is built by GitHub Actions (workflow `build-apk.yml`) and installed from Termux with `adb install`. App name "ClawScreen Companion", its own brand, no Claude or Android marks in the logo.

**Screens (built with UI design skills, E21):** setup assistant as a step-by-step question sequence with a status display (permission granted? connection? ready), stop button permanently movable, slightly transparent when idle and fully covering when urgent, touch targets at least 48 dp, Material 3, dark mode, strong contrast.

---

## 11. What the repository contains

Private repository `mertgoevse-wq/clawscreen`, locally at `/home/mert/clawscreen`:

```
clawscreen/
├── clawscreen-spec.md          # this file, the single source of truth for building
├── CLAUDE.md                   # compact build rules for Claude Code (Section 14)
├── README.md                   # user's guide, German, high standard, lint-checked
├── mcp/                        # MCP server (TypeScript/Node, speaks over stdio)
│   ├── src/index.ts            #   server entry
│   ├── src/transport/          #   screen transport: scrcpy server + ADB fallback (E22)
│   ├── src/tools/*.ts          #   the screen_* tools (Section 7)
│   ├── src/adb.ts              #   ADB layer (ADB_SERVER_SOCKET, timeouts, errors)
│   ├── src/memory.ts           #   operating memory (Section 8)
│   ├── src/safety.ts           #   blocklist + surprise rule (Section 9)
│   ├── src/session.ts          #   session mode, task list, log
│   ├── src/permissions.ts      #   what Claude may and may not do on the phone (E28)
│   ├── src/vision.ts           #   model client: local router, fallback chain, max_tokens (Section 20)
│   └── package.json
├── cli/                        # the clawscreen command line tool
│   ├── clawscreen              #   pair | connect | status | stop | setup | memory | run …
│   └── lib/…
├── companion/                  # the companion app (Kotlin)
│   ├── app/src/main/…
│   │   ├── AccessibilityService      # read screen, system gestures, volume keys
│   │   ├── FloatingStopButton        # red floating STOPP circle
│   │   ├── KeepAwakeService          # foreground service with notification
│   │   ├── ClipboardBridge           # umlauts and special characters
│   │   └── LocalStateServer          # 127.0.0.1:8765 state and brakes
│   └── build.gradle.kts
├── skill/screen/SKILL.md       # how a /screen session behaves, in plain rules
├── .claude/skills/
│   └── clawscreen-resume/SKILL.md   # crash recovery
├── .agents/skills/             # documentation of the globally installed community skills
├── memory/                     # starting knowledge, versioned in the repository
│   ├── cubasis3.json
│   └── flstudio-mobile.json
├── docs/
│   ├── reference-repos.md      # the 65 entries from Section 22 and what we take from them (E18)
│   ├── model-matrix.md         # measured models, latencies, what failed (Section 20)
│   ├── vulkaninfo-a56.txt      # GPU proof from the real phone (Section 21.2, CS-093)
│   ├── local-helpers.md        # which local runtime won, with measured numbers (CS-096)
│   └── fortschritt.md          # plain-language progress notes for the user (no jargon)
├── tasks/                      # tasks with a YAML header
│   ├── DEPENDENCIES.md
│   ├── skill-matrix.md         # at least 2 skills per task (E15)
│   └── CS-001 … CS-0xx.md
├── progress/BUILD-STATE.md     # build log, the basis for resuming
├── tools/
│   ├── sync_frontmatter.py     # check and repair task state
│   ├── anti-slop.py            # check README and docs against AI filler patterns
│   └── e2e-check.sh            # end-to-end checks
└── .github/workflows/
    ├── repo-health.yml         # task consistency, spec check, anti-slop lint
    └── build-apk.yml           # build the companion APK
```

---

## 12. Connection — the trickiest everyday part

1. **One-time pairing (the user must do this once).** `clawscreen pair` guides step by step: says where the switch is (Settings → Developer options → Wireless debugging → "Pair device with pairing code"), asks for the pairing port and the 6-digit code, runs `adb pair`, then `adb connect`, and stores the last working port in `~/.clawscreen/state.json`.
2. **Everyday connection, automatic first.** `clawscreen connect` tries in this order: the stored port → the last five known ports → `adb mdns services` (automatic discovery) → **plus the ways it can figure out itself** (E30). Only when all of them fail does it stop and ask the user, with a clear picture of what to do.
3. **Full automation.** The companion app receives the permission `WRITE_SECURE_SETTINGS` (`adb shell pm grant … android.permission.WRITE_SECURE_SETTINGS`). With it, the app can switch wireless debugging on and off by itself and can find the current port using Android's network discovery. Result: after a phone restart, `clawscreen connect` works without the user doing anything.
4. **Connection watcher.** Before every tool call, the MCP server checks whether the connection is alive (`adb get-state`) and starts the connect routine before it fails.
5. **Nothing is ever deleted** while fixing connections (E28).

---

## 13. The bridge to ClauDroide (E2)

- **Interface from day one:** the MCP server is a separate process with clear versioning (`mcp/manifest.json`). ClauDroide, or any other assistant that speaks MCP, can use it later as a source of tools without needing anything from inside ClawScreen.
- **Name and brand kept separate:** own name and logo, no "Claude" lettering in the logo; the word only in the text with a note that there is no connection to Anthropic.
- **Conventions reused:** task YAML, build state, waves, skill matrix — so a later merge into a ClauDroide add-on stays simple.
- **Config bridge:** `~/.clawscreen/config.json` contains `claude_integration: { enabled: false, expose_mcp: true }`.

---

## 14. How Claude Code works while building

This section is the **operating manual for Claude Code itself**. It is binding and is summarised compactly in `CLAUDE.md`.

### 14.1 Master command and one-run building (E19)
- The master command is: **"Build everything to the final product."** Claude Code then starts the autonomous loop and only ends when all tasks are `done` or a safety rule forbids going on.
- **Loop per task:** pick the next task by this priority → load its assigned skills (skill matrix) → implement → run the tests → mark the task `done` and update the build state → **commit and push** → next task.
- **Priority rule (E26, binding):** the **demo slice (Wave 1, CS-010 … CS-016) comes before everything else.** As long as a demo task is open and its dependencies are met, build that one — even if a later wave is already buildable. Do not start Wave 2 or later before the demo slice is finished or marked as a blocker. After the demo slice, work through the remaining waves in order; within a wave, pick the earliest open task whose dependencies are met.
- **Task list:** Claude Code keeps a task list throughout (per wave and per working session) and updates it after every step, so the user always sees where the build stands.
- **Blocker rule (E24):** after **2 failed attempts** on a task → write it into `progress/BUILD-STATE.md` as a blocker, continue with the next independent task, report all blockers at the end. **A run never ends silently.**
- **Crash safety = one-run guarantee across crashes:** because every task is pushed immediately (E16), after a Termux crash the *same* run continues with `resume` — no progress is lost.

### 14.2 Skills: find, install, use (E15)
- **Search** (task CS-005, before wave 1): `npx skills find <term>` for at least: `android`, `adb`, `android-testing`, `compose`, `ui design`, `adaptive`, `accessibility`, `mcp`, `git`, `testing`, `performance`, `kotlin`, `release`, `scrcpy`.
- **Look, then install:** briefly review each find (description, source repository, activity, content), install the suitable ones **globally** with `npx skills add <owner/repo> --skill <name> --yes`. Never execute unknown things blindly. Document what was installed, from where and for what, under `.agents/skills/`.
- **Skill matrix** `tasks/skill-matrix.md`: every task gets **at least 2 skills** (main skill plus a checking or side skill). The loop loads them before each task.
- **Side by side work:** independent tasks may run in parallel (`/parallel-task`) as long as files and waves are separate; wave borders are the points where everything is synchronised.
- Own skills (`screen`, `clawscreen-resume`) are project skills; the global community skills add to them. In a conflict the project skill wins.

### 14.3 Git discipline: always commit and push, no local pile-up (E16)
- **After every finished task:** commit and push. The state on GitHub is the only truth.
- **Before starting a new task** the working folder must be clean. Experiment commits that were **never pushed** are squashed into the task commit or dropped. The user explicitly allows dropping local commits.
- **Forbidden:** local piles of uncommitted work; force-push over already pushed history. **Allowed:** rewriting or dropping local commits that were never pushed.
- **Commit format:** `CS-0xx: <one sentence about what was done and how it was tested>` plus the footer `Generated with Claude Code` / `Co-Authored-By: Claude <noreply@anthropic.com>`.
- **Even partial success is pushed** (tested state plus blocker note), so a crash never eats progress.

### 14.4 Crash recovery: `/clawscreen-resume` (E17)
- **Words that trigger it:** `/clawscreen-resume`, "resume", "weiter".
- **What the skill does** (`.claude/skills/clawscreen-resume/SKILL.md`):
  1. read `progress/BUILD-STATE.md`,
  2. compare with the file system, `git log` and the task headers — **without guessing**; only what can be verified counts as the state,
  3. **re-check the last claimed task** by running its tests again,
  4. repair deviations (fix status, `sync_frontmatter`),
  5. continue the loop at the earliest open task with met dependencies.
- **Worst case:** because every task is pushed, the remote repository always holds the complete state including the build state. A freshly set up Termux/Debian can continue fully with `git clone` plus `resume`.

### 14.5 No AI slop, README at a high standard (E20)
- **The yardstick:** READMEs of excellent open-source projects — concrete, calm, code first — collected as examples during the 50+ repo research (E18).
- **Forbidden:** emoji in headings, superlatives without proof ("revolutionary", "blazing fast"), empty buzzword paragraphs, generic filler ("contributions welcome!" without a process), placeholder functions, fake tests, unfinished TODO implementations, files that belong to nothing.
- **Required:** a working quickstart (copyable, tested on the target phone), an honest "Known limitations" section, real commands, tables instead of long prose, a table of contents, a CI badge, pictures only when they really exist, a troubleshooting chapter.
- **Tool:** `tools/anti-slop.py` checks README and docs against that forbidden list and runs in `repo-health.yml`. A finding means a red CI. (Documentation lint only, no content censorship.)
- **Same rules for the code:** every function on a real call path, every claim in the README backed by a command or test.

### 14.6 UI design skills for the companion app (E21)
- Before every screen task in wave 4, Claude Code loads its UI design skills (adaptive layout, Material 3 guidelines, touch targets at least 48 dp, dark mode, edge-to-edge), assigned through the skill matrix.
- **Design rules:** ClawScreen brand (signal red for STOPP, dark neutral surfaces, simple icons); stop button movable, slightly transparent when idle; setup assistant as a question sequence with a status display; high contrast, easy on the eyes, usable with one hand.
- The keep-awake notification shows the session state and a direct stop action.

---

## 15. The build plan (waves, tasks, tests)

> Task IDs `CS-0xx`, one file per task `tasks/CS-0xx.md` with a YAML header (`status: pending|done`, `depends_on: []`, `wave`, `skills: [ … ]`, `test:`). Commit and push after every task (Section 14.3). Skill assignment per task in `tasks/skill-matrix.md` (at least 2 per task, E15).

**Rules for all tasks:**
- Dependencies first: no task starts before its `depends_on` are `done`.
- Independent tasks may run side by side; wave borders are the sync points.
- **Blocker rule (E24):** 2 failed attempts → note in `progress/BUILD-STATE.md`, continue, report at the end.
- **Hard limits (E28):** never delete apps, never delete user files, no root.
- **E23:** the screen stream only runs while Claude is actually looking.

### 15.1 Dependencies (authoritative — write these into the task files)

| Task | depends_on |
|---|---|
| CS-001 | — |
| CS-002 | CS-001 |
| CS-003 | CS-002 |
| CS-004 | CS-002 |
| CS-005 | CS-002 |
| CS-006 | CS-002 |
| CS-010 | CS-001, CS-004, CS-005, CS-006 |
| CS-011 | CS-010 |
| CS-012 | CS-011 |
| CS-013 | CS-012 |
| CS-014 | CS-010 |
| CS-015 | CS-011 |
| CS-016 | CS-013, CS-014, CS-015 |
| CS-021 | CS-011 |
| CS-022 | CS-011 |
| CS-023 | CS-021 |
| CS-024 | CS-012 |
| CS-025 | CS-013 |
| CS-026 | CS-010 |
| CS-031 | CS-015 |
| CS-032 | CS-015 |
| CS-033 | CS-024 |
| CS-040 | CS-003 |
| CS-041 | CS-040 |
| CS-042 | CS-040, CS-012 |
| CS-043 | CS-041 |
| CS-044 | CS-040 |
| CS-045 | CS-041, CS-042 |
| CS-050 | CS-044 |
| CS-051 | CS-050 |
| CS-060 | CS-024 |
| CS-061 | CS-060 |
| CS-062 | CS-060 |
| CS-070 | CS-022, CS-026, CS-060 |
| CS-071 | CS-070 |
| CS-072 | CS-041 |
| CS-080 | CS-024 |
| CS-081 | CS-026, CS-060 |
| CS-082 | CS-071, CS-072, CS-080, CS-081 |
| CS-090 | CS-012, CS-024 |
| CS-091 | CS-031, CS-032, CS-033, CS-082, CS-090 |
| CS-092 | CS-002 |
| CS-093 | CS-092 |
| CS-094 | CS-093, CS-011 |
| CS-095 | CS-093, CS-011 |
| CS-096 | CS-093 |
| CS-097 | CS-090 |

**A task is `done` only when its test (given in its own file) actually passed.** "Wrote the code" is not done. If the test cannot be run, the task stays open and the reason goes into the build state.

---

### Wave 0 — Setting up (CS-001 … CS-006)
- **CS-001:** Create the repository as described in Section 16 (private!), put this spec in. **Test:** `gh repo view mertgoevse-wq/clawscreen --json isPrivate` → true.
- **CS-002:** `CLAUDE.md` (build loop, skill use, git discipline, resume pointer, anti-slop rules, blocker rule, E28 limits — compact) + README skeleton + task templates. **Test:** files present, structure matches Section 11.
- **CS-003:** Workflows `repo-health.yml` (with anti-slop lint) and `build-apk.yml` (skeleton). **Test:** CI runs green on an empty state.
- **CS-004:** `tools/sync_frontmatter.py` + `tools/anti-slop.py` + `progress/BUILD-STATE.md`. **Test:** both scripts report consistency.
- **CS-005:** **Skill hunt (E15):** `npx skills find` over the terms in Section 14.2 (plus `scrcpy`), review, install the best globally, write `.agents/skills/` documentation and `tasks/skill-matrix.md` (at least 2 skills per task, every task listed). **Start with [`anthropics/skills`](https://github.com/anthropics/skills) and [`gradle/gradle-skills`](https://github.com/gradle/gradle-skills) (Section 22, category E) — these are the known-good baseline, do not go hunting before installing them.** **Test:** matrix complete; installed skills load and are actually used from CS-010 on.
- **CS-006:** **Reference projects (E18):** **Section 22 already contains 65 researched entries in 7 categories with live GitHub metadata and a binding take-over decision per row.** CS-006 turns that section into `docs/reference-repos.md`, verifies each link still resolves, installs the ones marked for installation (skills first, then the Vulkan proof), and links every take-over in the affected task file. **Do not start a fresh 50-repo search** — that research is done; extending it is allowed only for something Section 22 genuinely lacks. Result per entry: stars, last activity, licence, "what we take from it". **Test:** `docs/reference-repos.md` has all 65 rows, at least 5 categories, at least 5 concrete take-overs visible in the code or setup — **including at least one scrcpy take-over that CS-010 actually uses.**

---

### Wave 1 — Demo slice (CS-010 … CS-016) — **the part you see working first (E26)**
*This wave is the priority. It produces a genuinely working demo before anything else is built.*

- **CS-010:** **Connection + scrcpy transport on the real phone.** Guided pairing (`clawscreen pair`), connect with automatic fallbacks (Section 12), push and start the scrcpy server, capture one frame, send one tap, close the stream. **Test:** on the Galaxy A56: `adb devices` shows `127.0.0.1:* device`; a frame arrives; a tap on Settings visibly opens a row.
- **CS-011:** The three core tools as a minimum: `screen_look`, `screen_tap`, `screen_key`, plus `screen_open_app`. **Test:** on the real phone — open Settings, tap Bluetooth, verify the state changed by looking at the picture.
- **CS-012:** MCP server skeleton (speaks over stdio, registers tools, error format) + register it in Claude Code. **Test:** `claude mcp add` works in Debian, the `screen_*` tools appear in Claude Code.
- **CS-013:** `/screen` skill with the work cycle from Section 6 (look → act → verify → report), in short form. **Test:** hands-on run — "open the clock app and stop an alarm" runs autonomously.
- **CS-014:** `clawscreen status` (connection, companion app, storage, config). **Test:** clear plain-text report.
- **CS-015:** Blocklist `safety.ts` minimum (money apps, purchase dialogs). **Test:** trying to open the Play Store is blocked and reported.
- **CS-016:** **Demo slice report:** run the real acceptance scenario for the demo level on the device, write the result into `progress/BUILD-STATE.md` and `docs/fortschritt.md` in plain words, tag it as the demo milestone. **Test:** a written, honest demo result exists, including anything that does not work yet.

---

### Wave 2 — The full tool set (CS-021 … CS-026)
- **CS-021:** Seeing tools complete (Section 7.1), including scaling and the coordinate factor. **Test:** `screen_look` delivers picture plus inventory; the zoom path works.
- **CS-022:** Acting tools complete (Section 7.2, without the umlaut extra). **Test:** end-to-end — open Settings, tap the Bluetooth row, switch it, verify by picture.
- **CS-023:** `screen_wait_change` + surprise detection (frame difference). **Test:** an unexpected dialog pauses the run.
- **CS-024:** Session mode, log, task list (Section 6, E12). **Test:** a three-item list is worked through, the log is complete.
- **CS-025:** `/screen` skill complete + language setting (E11, German/English). **Test:** both language modes tested.
- **CS-026:** Stream control according to E23 (only while looking), plus the ADB fallback path proven. **Test:** no stream running between looks; both paths produce a working tap.

---

### Wave 3 — Safety and brakes (CS-031 … CS-033)
- **CS-031:** Blocklist and hard rules complete (Sections 9.2, 9.4) with the config file. **Test:** Play Store blocked and reported; purchase dialog text aborts.
- **CS-032:** Emergency brake from the terminal (`/stop`, `clawscreen stop`) + permissions module for E28. **Test:** a running action aborts, keep-awake is reset; the permissions module blocks uninstall attempts in a test.
- **CS-033:** Log rotation + the 15-minute pause rule. **Test:** limits simulated.

---

### Wave 4 — Companion app core (CS-040 … CS-045) — **UI design skills mandatory (E21, Section 14.6)**
- **CS-040:** App skeleton (Kotlin, minimal, brand "ClawScreen Companion"). **Test:** builds in CI.
- **CS-041:** Accessibility service: read the screen as JSON, system gestures. **Test:** on a protected screen the reading path gives more than the inventory.
- **CS-042:** Stop button + local server `/state` (Section 10). **Test:** pressing the button → MCP notices STOPP in under 500 ms.
- **CS-043:** Double volume-down detection. **Test:** double press → STOPP, single press passes through.
- **CS-044:** Keep-awake service with a clean reset + state notification. **Test:** session on/off → state correct.
- **CS-045:** Clipboard and paste (Section 7.4) + `adb install` routine and the first-time setup assistant (`clawscreen setup`, guided, screen per Section 14.6). **Test:** "Write 'Grüße aus Köln' in Messages" — umlauts correct; a fresh state reaches "ready".

---

### Wave 5 — Full connection automation (CS-050 … CS-051)
- **CS-050:** Grant `WRITE_SECURE_SETTINGS` + switch wireless debugging on and off programmatically. **Test:** switch off → `clawscreen connect` switches it on and connects without the user.
- **CS-051:** Port discovery via Android network discovery + report to the MCP server. **Test:** after a phone restart, reconnection works without the user.

---

### Wave 6 — Operating memory (CS-060 … CS-062)
- **CS-060:** Read and write the memory + confidence logic (Section 8). **Test:** a second run of the same task visibly needs fewer looks.
- **CS-061:** Re-discovery of anchors (self-healing). **Test:** deliberately move a coordinate → the way back works and the value is updated.
- **CS-062:** Recipe format + recorder (learns while working). **Test:** the sequence "create project" is saved and reused.

---

### Wave 7 — Music apps (CS-070 … CS-072) — the showcase (E4)
- **CS-070:** Cubasis 3 cookbook + starting memory (`memory/cubasis3.json`): create project, add track and instrument, play, tempo, save, export. **Acceptance scenario:** "In Cubasis build a project: drum track in 4/4 at 100 BPM and a bass track, play it, name it 'ClawTest'." — fully autonomous, checking pictures in the log.
- **CS-071:** FL Studio Mobile cookbook, same kind of scenario.
- **CS-072:** General robustness: loading screens, popups, advertising dialogs ignored and closed; permission dialogs of target apps (the companion app presses "Allow" only for apps on the user's allow list). **Test:** open ten everyday apps and do basic navigation in each.

---

### Wave 8 — Everyday use, speed, final documentation (CS-080 … CS-082)
- **CS-080:** Settings recipes (WLAN, Bluetooth, sound, display, apps). **Test:** "turn flight mode on and off again" runs autonomously.
- **CS-081:** Speed: measure the picture pipeline (start stream, frame, scale) and memory hits. **Target (E31):** a typical five-step task under 2 minutes. **Test:** a measured number exists, with the measurement command.
- **CS-082:** Final documentation: README at a high standard (Section 14.5) — quickstart typed out fresh on the phone, "Known limitations", troubleshooting (pairing lost, companion app stopped, storage full); anti-slop lint green; comparison with the examples from `docs/reference-repos.md`. **Test:** CI green including the lint; quickstart typed fresh and successful; `docs/fortschritt.md` complete in plain words.

---

### Wave 9 — Bridge and finish (CS-090 … CS-091)
- **CS-090:** MCP manifest + guide for plugging into ClauDroide (Section 13). **Test:** the guide is followable from the view of a foreign MCP client.
- **CS-091:** Safety review: blocklist tests, all three brakes checked, local-only binding of the small server, E28 limits honoured. Then version stamp 1.0, tag `v1.0.0`, **final report: finished / open / blockers** (E32). **Test:** checklist worked through, results in the build state.

---

### Wave 10 — Local acceleration on the phone's own chip (CS-092 … CS-097) — optional, never in the way (E36)

*This wave makes the phone use its own hardware instead of only the network. It runs **after** version 1.0 is stamped, because none of it is required for the product to work. Every task here must degrade silently to the CPU; a slow helper is bypassed, never waited for.*

- **CS-092:** **Model and provider client** (`src/vision.ts`): the local router endpoint, the model names from Section 20.1, the fallback chain, `max_tokens >= 2048` (E37), a 60 s timeout, and a clear error when no provider is reachable. **No credential is ever read from or written to a file (E35).** **Test:** a unit test with a fake router proves the fallback order and that a 402 moves down the chain; a real call proves one working model.
- **CS-093:** **Prove the GPU on the real phone.** Build `vulkaninfo` (Section 22, category F) for arm64 Android, run it on the A56, save the output to `docs/vulkaninfo-a56.txt`. **Test:** the file exists and states whether a Vulkan device was found. **If no device is found, this is a valid result** — record it, and CS-094/095/096 switch to CPU-only and say so.
- **CS-094:** **Frame-change check** on the GPU (Section 21.3): decide whether the screen changed since the last look, so Claude only spends a round trip when something moved (serves E23 and E31). **Test:** on the phone, 20 measurements — a static screen is reported "unchanged", a tap is reported "changed", each under 100 ms on average.
- **CS-095:** **Local element hints and OCR** on the GPU: propose likely tappable regions and extract text without a network call. **Test:** on a real Settings screenshot, hints are produced and the measured time is written to `docs/local-helpers.md`. **Hints are never trusted without a look** — the test proves Claude still verifies.
- **CS-096:** **Local text-only thinking** (no vision, no network) plus the runtime decision from Section 21.3: build the GPU candidates, **benchmark them on the A56, keep exactly one**, and delete the others. **Test:** `docs/local-helpers.md` contains the measured numbers and the sentence naming the winner and why; the losing builds are gone.
- **CS-097:** **Re-measure the models.** Section 20 was measured on 2026-10-04; quotas and latency move. Repeat the vision test over the fallback chain and update Section 20 and this task's results. **Test:** a table of model, latency and pass/fail exists and matches a run that really happened. **A model that stopped working is updated here, not silently worked around.**

---

## 16. Creating the GitHub repository automatically (E13) — task CS-001

Claude Code does this at project start (commands run later, when building):

1. Check `gh auth status`. If not logged in: **stop** and ask the user to run `gh auth login` once, interactively.
2. `mkdir -p /home/mert/clawscreen && cd /home/mert/clawscreen && git init -b main`
3. Put this spec in as `clawscreen-spec.md`; write `CLAUDE.md`, `README.md` (German), the wave 0 tasks; first commit.
4. `gh repo create mertgoevse-wq/clawscreen --private --source . --remote origin --push` — **private**, description: "ClawScreen — Claude steuert den Android-Bildschirm autonom (Termux/Debian, Samsung Galaxy A56)".
5. Write the workflows `repo-health.yml` (task consistency, spec check, anti-slop lint) and `build-apk.yml` (companion APK, upload as artifact).
6. After every finished task: **commit and push** (Section 14.3). Commit format `CS-0xx: <one sentence>`. No force-push over pushed history.
7. Right after that: the skill hunt (CS-005) and the 50+ reference project hunt (CS-006) — before wave 1 begins, the skills and examples are ready.

---

## 17. Outlook (E14) — planned in, not built now

1. **Voice control:** the user speaks the request (microphone in Termux or in the companion app), it becomes text, then the identical session flow runs.
2. **Headphone buttons as remote control:** play/pause as "continue/stop" — the companion app catches media keys, same technique as the volume keys.
3. **Unlocking money apps:** switch to `announce` mode with a loud announcement before every money action, or a separate "money session" where the user confirms only the money steps. (E33 keeps it blocked until the user decides otherwise.)
4. **All languages:** the language setting is free text, report templates are localisable.
5. **Preview mode:** before long tasks Claude shows the planned way step by step from the memory recipe, the user nods.
6. **Other devices:** controlling a second Android device (e.g. a tablet) over the same tools — the tools get a `device` argument.
7. **Deeper ClauDroide integration:** a "screen tasks" category that calls the ClawScreen MCP directly.

---

## 18. Assumptions and open points

| # | Assumption | If not |
|---|---|---|
| A1 | `gh` (the GitHub tool) is set up in Debian. | Wave 0 stops with the instruction `gh auth login`. |
| A2 | Cubasis 3 is installed (package `com.steinberg.cubasis`; verified in wave 7). | `screen_apps` gives the real name, the cookbook adapts. |
| A3 | FL Studio Mobile is installed. | same. |
| A4 | The user grants the companion app's permissions once (E29). | Wave 4 falls back to ADB-only (no umlauts, no stop button, no volume brake). |
| A5 | Developer options are switched on. | The setup guide explains the way to unlock them. |
| A6 | This spec file is moved to `/home/mert/clawscreen` before wave 0. | CS-001 copies it from the existing path. |
| A7 | `npx skills` is available in Debian (Node present — Claude Code needs it anyway). | CS-005 installs Node first. |
| A8 | Network access for GitHub search and clones is available. | CS-006 works with a shortened list and notes it. |
| A9 | The scrcpy server runs on the Galaxy A56 under Android 15 (E22). | If it does not: the ADB fallback stays primary; the tools work either way. CS-010 tests this first, so the answer comes early. |
| **A10** | The local model router on `http://localhost:20128` keeps working with the two Google AI Pro accounts (E35). | **Verified working on 2026-10-04.** If it stops: no screen reading and no `screen_describe`. Fall back to Claude looking at pictures directly (the normal path anyway) and report the exact error to the user. Never log in with a password. |
| **A11** | The GPU (Vulkan) is usable on the phone (E36). | The driver file exists; whether a Vulkan device is actually reported is **measured in CS-093**. If not: all local helpers run on the CPU. Nothing else changes. |
| **A12** | The NPU can be reached from an app. | **False, verified on 2026-10-04** — no NNAPI driver on the device (Section 21.1). This is a settled fact, not an open point. Do not attempt it again; do not promise it anywhere. |
| **A13** | OpenRouter / Perplexity / free aggregators could serve as a fallback (E35). | **False, verified on 2026-10-04** — 402 no credits, or disabled (Section 20.2). The only free fallback that works is `nvidia/meta/llama-3.2-11b-vision-instruct`. |

---

## 19. Acceptance criteria for version 1.0 (the project is done when …)

**Demo level (wave 1, the early milestone):**
1. On the real Galaxy A56: pairing works, a picture arrives, a tap works, `/screen` runs "open the clock app and stop an alarm" autonomously, and the Play Store is blocked.
2. A written, honest demo result exists (what works, what does not).

**Full version:**
3. `clawscreen setup` takes a fresh state (after a phone restart) all the way to a ready connection.
4. `/screen` session: "Open Cubasis, create a project 'ClawTest' with drums and bass (100 BPM), play it" — **fully autonomous**, with log and checking pictures.
5. The same kind of task in FL Studio Mobile.
6. "Turn WLAN off and on again" autonomously in a single instruction.
7. All three emergency brakes measurably work within a running action (reaction under 1 second).
8. Blocklist: opening the Play Store and purchase dialogs are reliably blocked and reported (E33).
9. A second run of the same Cubasis task visibly uses the memory (fewer looks, faster).
10. **Speed:** a typical five-step task is measured under 2 minutes (E31), with the measurement command recorded.
11. **Stream discipline:** no stream is running while Claude is not looking (E23), and the ADB fallback is proven.
12. **Limits honoured:** no app was deleted, no user file was deleted during the whole build (E28).
13. Repository `mertgoevse-wq/clawscreen` is **private**, CI green (including the anti-slop lint), APK artifact exists, build state complete, **every task pushed**.
14. **Resume proven:** the build state is deliberately rolled back one step → `/clawscreen-resume` notices the deviation, repairs it and continues (E17).
15. **Skills proven:** `tasks/skill-matrix.md` assigns at least 2 skills per task; at least 4 community skills are installed globally, documented and were actually loaded during the build (E15).
16. **Reference hunt proven:** `docs/reference-repos.md` lists at least 50 repositories with take-over decisions, at least 5 take-overs visible in the code or setup, including at least one scrcpy take-over used in CS-010 (E18).
17. **README standard:** lint green, quickstart typed fresh and successful, no forbidden patterns, plain explanations of every hard word (E20, E25).
18. **Final report:** finished / open / blockers, in plain words (E32).

**Local acceleration (Wave 10 — only checked if the run got that far):**
19. **Model path proven (E34, E37):** `screen_describe` reads a real screenshot correctly through `agy/gemini-3.7-flash-high` with `max_tokens >= 2048`, the fallback chain is unit-tested, and **no credential appears anywhere in the repository** (E35).
20. **GPU truth recorded (E36):** `docs/vulkaninfo-a56.txt` exists and states the real outcome; `docs/local-helpers.md` names exactly one retained runtime with measured numbers, and the rejected builds are gone.
21. **Honest limitation stated:** the README says plainly that the NPU is not accessible to apps and that the GPU/CPU helpers are optional (Section 21.4) — and **no document claims NPU use**.
22. **Helpers never block:** every local helper is bypassed when slow; the five-step time target (E31) still holds with helpers enabled.

---

## 20. Which model looks at the screen (measured, E34, E35, E37)

> Everything in this section was **measured on the actual phone on 2026-10-04**, not assumed. The test image was a white square with a red circle and a blue bar at the bottom; the model was asked to describe it. "Vision works" means it named both correctly. Re-measuring is a task (CS-097 below), because quotas and latency change.

### 20.1 The models that actually work

Reached through the local router at `http://localhost:20128` (the "Omniroute" server running in Termux). All of them speak the normal OpenAI-style API, so the MCP server talks to it like any other endpoint.

| Model | Provider | Vision | Measured latency | Role in ClawScreen |
|---|---|---|---|---|
| **`agy/gemini-3.7-flash-high`** | Google AI Pro (account 1) | **works** | **2.1 s / 2.7 s** | **Default model.** Fastest reliable result, measured twice. Used by `screen_describe`, by the `/screen` skill for hard-to-read screens, and by the automated tests. |
| `nvidia/meta/llama-3.2-11b-vision-instruct` | NVIDIA | **works** | **1.3 s** | **Free fallback.** Small model, but it read the test image correctly and needs no credit. Use it when the Pro quota is exhausted. |
| `antigravity/gemini-3.8-flash-tiered` | Google AI Pro (account 2) | **works** | 2.9 s | Second Google account, same quality. Spread the load so one account's quota carries everything. |
| `antigravity/gemini-3.1-pro-high` | Google AI Pro (account 2) | **works** | 4.1 s | Higher-quality reading when a screen is hard to interpret. |
| `agy/gemini-3.1-pro-high` | Google AI Pro (account 1) | **works** (with E37) | 4.5 s | Same, on account 1. |
| `agy/gemini-3.8-flash-medium` / `-low` | Google AI Pro (account 1) | **works** | 19.3 s / 19.9 s | Keep as a reserve; too slow for the interactive loop. |
| `agy/gemini-pro-agent` | Google AI Pro (account 1) | **works** (with E37) | 7.3 s | **Hard cases.** Uses ~560 reasoning tokens, so it reasons before answering. Worth it when a look needs real thought, not for every frame. |

**Fallback order in code** (`mcp/src/vision.ts`, built in **CS-092**): `agy/gemini-3.7-flash-high` → `antigravity/gemini-3.8-flash-tiered` → `nvidia/meta/llama-3.2-11b-vision-instruct`. On quota or timeout errors only, move down. Never silently: a fallback must be logged, because a weaker model may read a screen differently.

**Note on `screen_look`:** the normal path does **not** call a model at all — Claude looks at the picture itself. A model is only asked when a screen needs describing in words (`screen_describe`), when a test needs a machine-readable answer, or when the `/screen` skill wants a second opinion. That is why the 2-minute target (E31) survives a slow or broken provider.

### 20.2 What does **not** work — do not build on it

| Tried | Result | Consequence for the build |
|---|---|---|
| `agy/claude-sonnet-5-5-high`, `agy/claude-opus-5-5-high`, `antigravity/claude-sonnet-5-5-high` | **Timeout after 150 s** | **Never route vision through `*/claude-*` on agy/antigravity.** Unusable in a 2-minute budget (E31). |
| `openrouter/google/gemini-2.5-pro`, `openrouter/perplexity/sonar-pro` | `402 Insufficient credits. This account never purchased credits` | **OpenRouter is connected but empty.** It is not a usable provider today. |
| `gemini/gemini-3.1-pro-preview`, `gemini/gemini-2.5-computer-use-preview-10-2025` | `402 Your prepayment credits are depleted` | The direct Gemini API key is used up. (Note: the computer-use model would have been ideal for this project — worth re-testing if credits are topped up.) |
| `perplexity-web` | Disabled by the operator | Not available. The Pro subscription is with **Google**, not Perplexity. |
| `kc/openrouter/auto-beta`, `agentrouter/claude-opus-5` | `402` quota exhausted | No working free fallback beyond the two above. |
| `free-ai/x-ai/grok-4.20` | `429` all credentials cooling down | Free aggregators are unreliable. Not a foundation. |

**Consequence:** the project depends on **two Google AI Pro accounts**. Both are already connected with OAuth and both must keep working. This is a single point of failure the user must know about — written into the README's "Known limitations" (E20).

### 20.3 The thinking-token trap (E37) — a real bug found by measuring

Reasoning models spend their `max_tokens` budget on thinking before they answer. Measured on `agy/gemini-3.1-pro-high` with the same image:

| `max_tokens` | Reasoning tokens used | What came back |
|---:|---:|---|
| 150 | 140 | `"The"` — **vision looks broken** |
| 2048 | 224 | `"The image shows a large red circle."` — correct |

**Rule:** every vision request sets `max_tokens >= 2048`, and thinking models additionally get a timeout of 60 s. Without this rule the models look blind, and the obvious "fix" of switching models wastes hours.

### 20.4 Credentials — a hard rule

Both Google accounts are connected to the local router via **OAuth**; the tokens refresh automatically. **No password, no API key, no token ever goes into the repository, into `CLAUDE.md`, into a task file, or into any file that is pushed to GitHub** (E16 pushes everything). The only thing the build is allowed to read is the *model name list* and the local endpoint address.

If a provider stops working: check `omniroute` status first, report the exact error to the user, and fall back per 20.1. **Never** try to log in with a password, and never ask the user to paste one into a chat or a file.

---

## 21. Using the phone's own chip — GPU yes, NPU no (E36)

The user asked for the Galaxy A56's NPU and GPU to be actively used. The GPU is real and usable. **The NPU is not reachable from an app, and no part of this specification may claim otherwise.** That was verified on the device, not guessed.

### 21.1 The NPU finding — verified, honest

The Exynos 1580 contains an NPU (~14.7 TOPS). It is **not available to third-party apps**:

- **Verified:** no NNAPI driver anywhere on the device — `find /vendor /system/lib64 -iname "*nnapi*"` returns **nothing**, and `/vendor/lib64/hw/` contains no NPU or neural-networks module (it holds camera, audio, gralloc, input and `vulkan.samsung.so`).
- Samsung's NPU SDK is only given to selected partners. There is no public, supported way to reach it without Samsung approval.
- Qualcomm's Hexagon NPU is a **different vendor** and does not exist in this phone.

**Therefore:** no NPU code, no NPU promise, no "NPU-accelerated" in the README. Anyone who adds such a claim has invented it. If Samsung ever opens the NPU, that is a later chapter (Section 17).

### 21.2 The GPU finding — verified, usable

- **Verified:** `/vendor/lib64/hw/vulkan.samsung.so` exists, and `libvulkan.so` is in `/system/lib64`. The Xclipse 540 GPU is reachable through **Vulkan**.
- **Task CS-093** must prove it on the real phone before anything depends on it: build [`KhronosGroup/Vulkan-Tools`](https://github.com/KhronosGroup/Vulkan-Tools) (`vulkaninfo`) for arm64 Android, run it on the A56, and save the output to `docs/vulkaninfo-a56.txt`. If it shows no device, the GPU path is marked unavailable and every helper below falls back to the CPU. Record whichever outcome happens — the point is the measurement, not the result.

### 21.3 What the phone's hardware is genuinely used for

Every helper below is **optional** and must degrade silently to the CPU. None of them may ever sit between Claude and a screenshot — if a helper is slow, it is bypassed.

| Helper | Hardware used | What it does for ClawScreen | Task |
|---|---|---|---|
| **Frame-change check** | GPU (Vulkan/OpenGL) | Decides whether a screen actually changed since the last look. Claude only sends a picture when something moved — directly serves E23 (no stream while not looking) and cuts latency. | CS-094 |
| **Local element hints** | GPU | A small local model proposes likely tappable regions. Claude still verifies by looking; the hints only make the first guess cheaper. Never trusted blindly. | CS-095 |
| **Local OCR** | GPU | Fast text extraction for logs and app labels, so routine text never needs a network round trip. | CS-095 |
| **Text-only thinking** | CPU (Cortex-X4 @ 2.9 GHz) | Long planning text runs locally, no vision, no network. The big core is genuinely useful here. | CS-096 |

**Runtime choice (CS-096):** [`ggml-org/llama.cpp`](https://github.com/ggml-org/llama.cpp) with the **Vulkan backend** (`GGML_VULKAN`) is the primary candidate — it has a real, maintained Vulkan path and builds from source in Termux. [`Tencent/ncnn`](https://github.com/Tencent/ncnn) is the lightweight alternative. For a helper that must live inside the companion APK, [`google-ai-edge/LiteRT`](https://github.com/google-ai-edge/LiteRT) with its GPU delegate is the Android-native choice. **Benchmark on the phone before committing** — pick the one that actually runs fastest on the A56, and write the measured numbers into `docs/local-helpers.md`. Do not install all three "to have options"; that is exactly the kind of unused dependency E20 forbids.

### 21.4 Honest limitation for the README

> The Galaxy A56's neural processor (NPU) is not accessible to apps, so ClawScreen uses the **graphics processor (GPU)** and the CPU for local helpers. Everything still works without them — they only make it faster.

---

## 22. Reference repositories, ready to install (E18)

65 entries across 7 categories (59 distinct repositories), **metadata pulled live from the GitHub API on 2026-10-04** (stars, licence, last push). Claude Code turns this section into `docs/reference-repos.md` during **CS-006**, then follows the take-over column.

**How to use this section:**
1. Every row is a decision already made. Do not re-research; verify the link still resolves when installing.
2. The "What we take from it" column is binding — it says what to adopt and what to refuse.
3. Rows marked *reference only* or *do not copy* were checked and rejected. **Do not retry them.**
4. A repo marked **archived** must never be used as a base.
5. The install commands are in the block below. They are the only ones that install something; everything else is read as a reference.

**Install commands:**

```bash
# Official Anthropic skills — the fastest quality win in the whole build (E15)
npx skills add anthropics/skills --list
npx skills add anthropics/skills --skill <name> --yes      # repeat per chosen skill

# Gradle skills for the companion app (Wave 4)
npx skills add gradle/gradle-skills --list

# Any further skill of the Section 14.2 search list
npx skills find <term>
npx skills add <owner/repo> --skill <name> --yes

# GPU proof on the phone (CS-093)
git clone --depth 1 https://github.com/KhronosGroup/Vulkan-Tools.git
# build vulkaninfo for arm64-android, run it, save output to docs/vulkaninfo-a56.txt

# Local GPU helper (CS-096) — benchmark, then pick ONE
git clone --depth 1 https://github.com/ggml-org/llama.cpp      # build with -DGGML_VULKAN=ON
```

**Licence rule:** Apache-2.0 and MIT may be used in our code with attribution. `NOASSERTION` means GitHub could not identify a licence — **treat as "do not copy code from it, read it only"**. GPL-3.0 and LGPL-2.1 rows are read-only references; nothing from them may end up in our source.

#### A — Android control over ADB / MCP (feeds E1, E22, CS-010, CS-012)

| Repository | Stars | Licence | Last push | What we take from it |
|---|---:|---|---|---|
| [`Genymobile/scrcpy`](https://github.com/Genymobile/scrcpy) | 151,009 | Apache-2.0 | 2026-10-03 | **Core dependency.** The picture stream and fast taps (E22). Apache-2.0 allows using it inside our own code — keep it an external binary, do not fork it. |
| [`JuanCF/scrcpy-mcp`](https://github.com/JuanCF/scrcpy-mcp) | 110 | MIT | 2026-09-23 | **Read first, do not adopt.** Small MIT server showing the minimal scrcpy-over-MCP shape. Use it as the reference for our tool boundaries (Section 7), then write our own because it lacks blocklist, brakes and memory. |
| [`mobile-next/mobile-mcp`](https://github.com/mobile-next/mobile-mcp) | 8,644 | Apache-2.0 | 2026-10-04 | Reference for a cross-platform MCP tool surface. Copy the tool-naming discipline, not the code. |
| [`openatx/uiautomator2`](https://github.com/openatx/uiautomator2) | 8,406 | MIT | 2026-09-11 | The mature way to drive Android from Python. Use it **inside Debian** for `uiautomator dump` in apps where the inventory is empty — an escape hatch behind our own ADB path. |
| [`openatx/adbutils`](https://github.com/openatx/adbutils) | 1,082 | MIT | 2026-08-10 | Small, clean ADB wrapper in Python. Model for our thin ADB layer and for `tools/` scripts. |
| [`DeviceFarmer/stf`](https://github.com/DeviceFarmer/stf) | 4,586 | NOASSERTION | 2026-10-02 | Device farm. Reference for device-state handling and reconnect logic in `clawscreen connect` (Section 12). |
| [`DeviceFarmer/adbkit`](https://github.com/DeviceFarmer/adbkit) | 306 | NOASSERTION | 2026-10-02 | Node ADB library — the closest thing to our TypeScript transport. Use its connection/retry approach. |
| [`appium/appium`](https://github.com/appium/appium) | 22,043 | Apache-2.0 | 2026-10-04 | Reference for a stable action vocabulary (find / tap / wait) and its flaky-element handling. |
| [`appium/appium-uiautomator2-driver`](https://github.com/appium/appium-uiautomator2-driver) | 884 | Apache-2.0 | 2026-10-01 | Shows exactly which UiAutomator calls return nothing on canvas apps — the Cubasis problem in Section 5.1.5. |
| [`mobile-dev-inc/Maestro`](https://github.com/mobile-dev-inc/Maestro) | 15,932 | Apache-2.0 | 2026-10-02 | YAML test flows. Take the idea of readable, checkable UI scripts for our acceptance tests (Section 19). |
| [`cucumber/cucumber-js`](https://github.com/cucumber/cucumber-js) | 5,395 | MIT | 2026-10-04 | Gherkin step definitions. Take the *readable scenario* form for the memory-recipe tests (Section 8). |
| [`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers) | 91,002 | NOASSERTION | 2026-10-04 | Canonical MCP server examples. Use for tool schema and error-format correctness in CS-012. |
| [`modelcontextprotocol/typescript-sdk`](https://github.com/modelcontextprotocol/typescript-sdk) | 13,513 | NOASSERTION | 2026-10-02 | **Our MCP SDK.** Build the MCP server with this instead of hand-writing the protocol. |
| [`modelcontextprotocol/python-sdk`](https://github.com/modelcontextprotocol/python-sdk) | 24,479 | MIT | 2026-10-02 | Only if a Python helper is needed. |
| [`microsoft/mcp`](https://github.com/microsoft/mcp) | 3,730 | MIT | 2026-10-03 | Alternative MCP SDK; keep as a fallback if the TypeScript SDK misses a needed feature. |
| [`libimobiledevice/libusbmuxd`](https://github.com/libimobiledevice/libusbmuxd) | 691 | LGPL-2.1 | 2025-09-07 | Reference only. Out of scope (iOS). Listed so nobody re-suggests it. |


#### B — Android testing, CI and build discipline (feeds E16, Section 14.3)

| Repository | Stars | Licence | Last push | What we take from it |
|---|---:|---|---|---|
| [`google/android-cuttlefish`](https://github.com/google/android-cuttlefish) | 726 | NOASSERTION | 2026-10-03 | Headless Android for CI device tests. Use when a real-device test must run on GitHub instead of the phone. |
| [`google/android-emulator-container-scripts`](https://github.com/google/android-emulator-container-scripts) | 2,094 | Apache-2.0 | 2026-10-04 | Run emulators inside containers — the practical recipe if cuttlefish is too heavy. |
| [`android/testing-samples`](https://github.com/android/testing-samples) | 9,289 | Apache-2.0 | 2025-07-18 | Official test samples. Patterns for the companion app's unit and UI tests (Section 19). |
| [`gradle/gradle-skills`](https://github.com/gradle/gradle-skills) | 14 | Apache-2.0 | 2026-09-30 | Official Gradle skills. Install via the skill flow in Section 14.2 — directly relevant to the companion app build. |
| [`facebook/buck2`](https://github.com/facebook/buck2) | 4,455 | Apache-2.0 | 2026-10-04 | Reference for hermetic, reproducible builds. Not adopted: too large a change for this project. |
| [`bazelbuild/bazel`](https://github.com/bazelbuild/bazel) | 25,919 | Apache-2.0 | 2026-10-02 | Reference only. Explicitly **not** adopted — Gradle stays (record the reason so nobody retries). |
| [`appium/appium`](https://github.com/appium/appium) | 22,043 | Apache-2.0 | 2026-10-04 | See category A. |


#### C — Compose, architecture and design (feeds E21, Wave 4)

| Repository | Stars | Licence | Last push | What we take from it |
|---|---:|---|---|---|
| [`android/nowinandroid`](https://github.com/android/nowinandroid) | 21,878 | Apache-2.0 | 2026-10-04 | **The design yardstick.** Material 3, adaptive layouts, dark mode, clean layering. Copy its structure for the companion app, not its feature set. |
| [`android/compose-samples`](https://github.com/android/compose-samples) | 23,496 | Apache-2.0 | 2026-10-02 | Canonical snippets for the specific Compose problems the companion app hits. |
| [`android/architecture-samples`](https://github.com/android/architecture-samples) | 45,851 | Apache-2.0 | 2026-09-26 | MVVM / UDF structure for the companion app's state handling. |
| [`JetBrains/compose-multiplatform`](https://github.com/JetBrains/compose-multiplatform) | 19,401 | Apache-2.0 | 2026-10-03 | Only if a shared UI module ever makes sense. Not needed in v1.0. |
| [`android/architecture-components-samples`](https://github.com/android/architecture-components-samples) | 129 | Apache-2.0 | 2024-12-06 **(archived)** | **Archived — do not copy.** Listed only to record that it was checked and rejected. |
| [`coil-kt/coil`](https://github.com/coil-kt/coil) | 11,913 | Apache-2.0 | 2026-10-04 | Image loading. Needed in the companion app for the session preview picture. |
| [`lysine-dev/okhttp`](https://github.com/lysine-dev/okhttp) | 47,083 | Apache-2.0 | 2026-10-03 | HTTP client for the companion app's local server calls (the repository was transferred, hence the new owner). |
| [`lysine-dev/retrofit`](https://github.com/lysine-dev/retrofit) | 43,938 | Apache-2.0 | 2026-10-02 | Typed local-server calls. Use only where it genuinely reduces boilerplate. |
| [`square/moshi`](https://github.com/square/moshi) | 10,165 | Apache-2.0 | 2026-10-01 | JSON for the companion app's local protocol. Compare against `kotlinx.serialization` and pick one — do not use both. |
| [`sqldelight/sqldelight`](https://github.com/sqldelight/sqldelight) | 6,887 | Apache-2.0 | 2026-10-03 | Local database for the operating memory (Section 8) — typed queries, compile-time checked. |
| [`bumptech/glide`](https://github.com/bumptech/glide) | 35,024 | NOASSERTION | 2026-10-02 | Mature image loading. Fallback if Coil does not fit. |
| [`ktlint/ktlint`](https://github.com/ktlint/ktlint) | 6,751 | MIT | 2026-10-02 | **Formatter/linter gate in CI.** No formatting argument survives a build. |


#### D — Termux / Debian environment (feeds Section 4, CS-002)

| Repository | Stars | Licence | Last push | What we take from it |
|---|---:|---|---|---|
| [`termux/termux-app`](https://github.com/termux/termux-app) | 61,970 | NOASSERTION | 2026-09-26 | The terminal app itself. Check which of our tools need Termux-specific paths. |
| [`termux/proot-distro`](https://github.com/termux/proot-distro) | 3,526 | GPL-3.0 | 2026-09-23 | The Debian-in-Termux layer we build in. Understand its limits (no systemd, bind mounts) before debugging. |
| [`termux/termux-api`](https://github.com/termux/termux-api) | 4,414 | none | 2026-09-17 | Optional bridge for clipboard, sensors and notifications — candidate for the umlaut path (Section 7.4) if the companion app route fails. |
| [`termux/termux-tools`](https://github.com/termux/termux-tools) | 878 | GPL-3.0 | 2026-09-20 | The `termux-*` command set our scripts may call. |
| [`astral-sh/uv`](https://github.com/astral-sh/uv) | 90,407 | Apache-2.0 | 2026-10-04 | **Fast Python package manager.** Use it for all Python tooling in Debian instead of pip — far quicker on a phone CPU. |
| [`typst/typst`](https://github.com/typst/typst) | 56,406 | Apache-2.0 | 2026-10-02 | Typesetting tool. Only for optional PDF reports. |
| [`localsend/localsend`](https://github.com/localsend/localsend) | 93,352 | Apache-2.0 | 2026-10-04 | Reference for a local-network transfer service. Not needed; the project stays local (Section 5.1.7). |
| [`wireapp/wire-android`](https://github.com/wireapp/wire-android) | 253 | GPL-3.0 | 2026-10-04 | Reference for an Android app with serious security hygiene. Checklist source for the companion app. |
| [`Droid-ify/client`](https://github.com/Droid-ify/client) | 7,539 | GPL-3.0 | 2026-09-12 | Reference for a modern Compose app with a small surface area. |
| [`NeoApplications/Neo-Store`](https://github.com/NeoApplications/Neo-Store) | 5,335 | GPL-3.0 | 2026-10-01 | Reference for F-Droid-style distribution of the companion APK if sideloading gets annoying. |


#### E — Quality yardstick and tooling (feeds E20, Section 14.5)

| Repository | Stars | Licence | Last push | What we take from it |
|---|---:|---|---|---|
| [`anthropics/claude-code`](https://github.com/anthropics/claude-code) | 149,407 | none | 2026-10-03 | **We are running inside it.** Its documented plugin/skill/hook mechanism is what Section 14.2 builds on. |
| [`anthropics/skills`](https://github.com/anthropics/skills) | 179,634 | none | 2026-10-03 | Official skill examples. **Install several of these globally as the baseline skill set** — this is the fastest quality win in the whole build. |
| [`eslint/eslint`](https://github.com/eslint/eslint) | 27,564 | MIT | 2026-10-04 | Lint gate in CI for the TypeScript MCP server. |
| [`prettier/prettier`](https://github.com/prettier/prettier) | 52,343 | MIT | 2026-10-04 | Format gate in CI. Formatting is not a style discussion. |
| [`bufbuild/buf`](https://github.com/bufbuild/buf) | 11,475 | Apache-2.0 | 2026-10-04 | Only if a protobuf schema is introduced. Record the 'no' so it is not revisited. |
| [`typst/typst`](https://github.com/typst/typst) | 56,406 | Apache-2.0 | 2026-10-02 | See category D. |
| [`astral-sh/uv`](https://github.com/astral-sh/uv) | 90,407 | Apache-2.0 | 2026-10-04 | See category D. |


#### F — GPU / Vulkan on this exact phone (feeds E36, Section 21)

| Repository | Stars | Licence | Last push | What we take from it |
|---|---:|---|---|---|
| [`KhronosGroup/Vulkan-Tools`](https://github.com/KhronosGroup/Vulkan-Tools) | 497 | Apache-2.0 | 2026-10-04 | **`vulkaninfo` for Android.** How we prove on the phone that Vulkan really works before any GPU code is written (Section 21.2). |
| [`WearyConcern1165/xclipse-vulkan-decompiled`](https://github.com/WearyConcern1165/xclipse-vulkan-decompiled) | 11 | none | 2026-05-12 | Independent evidence of what the Xclipse driver really supports. Read-only reference — we do **not** link against a decompiled driver. |
| [`google-ai-edge/mediapipe`](https://github.com/google-ai-edge/mediapipe) | 37,162 | Apache-2.0 | 2026-10-04 | **GPU-accelerated local vision.** Candidate for the frame-difference / idle-detection helper (Section 21.3). |


#### G — On-device inference, GPU-accelerated (feeds E36, Section 21.3)

| Repository | Stars | Licence | Last push | What we take from it |
|---|---:|---|---|---|
| [`ggml-org/llama.cpp`](https://github.com/ggml-org/llama.cpp) | 130,298 | MIT | 2026-10-04 | **Vulkan backend (`GGML_VULKAN`).** The strongest option for a local text/vision helper using the Xclipse GPU. Build from source in Termux; no NPU involved. |
| [`Tencent/ncnn`](https://github.com/Tencent/ncnn) | 23,906 | NOASSERTION | 2026-10-04 | Lightweight inference with a Vulkan backend. Alternative when the model is small. |
| [`google-ai-edge/LiteRT`](https://github.com/google-ai-edge/LiteRT) | 3,470 | Apache-2.0 | 2026-10-04 | Google's runtime (formerly TensorFlow Lite). Android-native, GPU delegate. Best fit if the helper ships inside the companion APK. |
| [`google-ai-edge/mediapipe`](https://github.com/google-ai-edge/mediapipe) | 37,162 | Apache-2.0 | 2026-10-04 | See category F. |
| [`microsoft/onnxruntime`](https://github.com/microsoft/onnxruntime) | 22,007 | MIT | 2026-10-04 | ONNX Runtime Mobile with the NNAPI/GPU providers. Cross-platform option. |
| [`pytorch/executorch`](https://github.com/pytorch/executorch) | 5,078 | NOASSERTION | 2026-10-04 | PyTorch's mobile runtime. Use only if we ever need a PyTorch model. |
| [`tensorflow/tensorflow`](https://github.com/tensorflow/tensorflow) | 200,700 | Apache-2.0 | 2026-10-04 | Reference for model formats. Do not vendor the full framework. |
| [`google/gemmlowp`](https://github.com/google/gemmlowp) | 1,845 | Apache-2.0 | 2024-01-29 | Low-precision kernels. Reference only. |
| [`qualcomm/ai-hub-models`](https://github.com/qualcomm/ai-hub-models) | – | – | – | **Read, do not run.** Qualcomm Hexagon NPU models — wrong vendor for the Exynos 1580. Useful as the yardstick for what an NPU-optimised model set looks like. |
| [`qualcomm/ai-hub-apps`](https://github.com/qualcomm/ai-hub-apps) | – | – | – | Same as above: reference for GPU/NPU delegate structure. |

---

*End of the specification. This file is the only foundation for building. Changes only with a version bump and an entry in the change history at the top. The previous version 1.1 is kept as `clawscreen-spec-v1.1-backup.md` for reference only.*
