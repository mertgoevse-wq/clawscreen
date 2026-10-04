# Skill matrix (E15)

Every task loads at least two skills before it is implemented: the main skill
that shapes the work and a checking or side skill. The build loop in
`CLAUDE.md` reads this table, loads the listed skills, then implements.

Sources: `P` = project skill in this repository, `C` = community skill in
`.agents/skills/` (see `.agents/skills/README.md`), `R` = runtime-provided
Android/Compose skill.

| Task | Wave | Skills | Why these |
|---|---:|---|---|
| CS-001 | 0 | R `testing-setup`, C `tdd` | Repository and first CI gate. Nothing ships yet, so the two skills set the gate discipline from task one. |
| CS-002 | 0 | R `testing-setup`, R `android-permissions-security` | Rules and permissions documentation. |
| CS-003 | 0 | R `testing-setup`, C `tdd` | CI gates are tests; the green-on-empty-state check is the first one that must pass. |
| CS-004 | 0 | C `tdd`, R `testing-setup` | The two checker scripts are exactly "tests that assert on the repository". |
| CS-005 | 0 | C `skill-creator`, C `tdd` | Writes this file and `.agents/skills/README.md`; the review of each find is judged against what a skill must prove to be useful. |
| CS-006 | 0 | C `skill-creator`, R `testing-setup` | Structured per-entry documentation plus the link check that must really pass. |
| CS-010 | 1 | C `tdd`, R `android-permissions-security` | Transport first as a test: fake adb, then the real phone. Permissions rules decide which adb calls are allowed at all. |
| CS-011 | 1 | C `tdd`, R `android-permissions-security` | Four tools, each with a runnable test. |
| CS-012 | 1 | C `mcp-builder`, C `tdd` | Official MCP server shape (schema, error format) and tests for the stdio protocol. |
| CS-013 | 1 | C `skill-creator`, C `mcp-builder` | A skill file for `/screen`, and the tool names it may call. |
| CS-014 | 1 | C `tdd`, C `mcp-builder` | Status report built from the same modules the MCP server exposes. |
| CS-015 | 1 | C `tdd`, C `mcp-builder` | A blocklist that fails open is a safety bug; tests first. |
| CS-016 | 1 | C `tdd`, R `testing-setup` | The report must match measured output, so the measuring side is reviewed. |
| CS-021 | 2 | C `tdd`, C `mcp-builder` | Coordinate scaling is arithmetic with edge cases; it needs real assertions. |
| CS-022 | 2 | C `tdd`, R `android-permissions-security` | Acting tools must stay inside the E28 limits while they act. |
| CS-023 | 2 | C `tdd`, C `mcp-builder` | Frame difference and surprise detection are pure functions worth testing hard. |
| CS-024 | 2 | C `tdd`, C `skill-creator` | Session, log and task list are state machines that the `/screen` skill drives. |
| CS-025 | 2 | C `skill-creator`, C `mcp-builder` | The complete skill plus the language switch it reads. |
| CS-026 | 2 | C `tdd`, C `mcp-builder` | E23 stream discipline is a lifecycle rule that must be provable. |
| CS-031 | 2+3 | C `tdd`, R `android-permissions-security` | Money-app blocklist and purchase-dialog text abort. |
| CS-032 | 3 | C `tdd`, R `android-permissions-security` | Emergency brake plus the E28 permission module: the two things that must never be wrong. |
| CS-033 | 3 | C `tdd`, C `mcp-builder` | Log rotation and the pause rule are timer logic; simulated limits are the test. |
| CS-040 | 4 | C `gradle-best-practices`, C `android-design-guidelines` | Build skeleton plus the design baseline E21 requires. |
| CS-041 | 4 | C `android-native-dev`, C `android-design-guidelines` | Accessibility service and the JSON reading path. |
| CS-042 | 4 | C `android-design-guidelines`, C `android-native-dev` | Floating stop button (always on top, 64 dp, high contrast) plus the local server. |
| CS-043 | 4 | C `android-native-dev`, C `tdd` | Volume-key capture with the 600 ms double-press window. |
| CS-044 | 4 | C `android-native-dev`, C `android-design-guidelines` | Foreground service, notification, clean reset. |
| CS-045 | 4 | C `android-native-dev`, C `android-design-guidelines` | Clipboard/paste through the accessibility service and the setup assistant screens. |
| CS-050 | 5 | C `android-native-dev`, R `android-permissions-security` | `WRITE_SECURE_SETTINGS` is a privileged grant; the rule set must be exact. |
| CS-051 | 5 | C `android-native-dev`, C `tdd` | Port discovery and reporting to the MCP server. |
| CS-060 | 6 | C `tdd`, C `mcp-builder` | Memory read/write and the confidence rule; the "fewer looks" claim needs numbers. |
| CS-061 | 6 | C `tdd`, C `mcp-builder` | Anchor re-discovery after a deliberate miss. |
| CS-062 | 6 | C `tdd`, C `skill-creator` | Recipe format plus the recorder that saves and replays them. |
| CS-070 | 7 | C `tdd`, C `mcp-builder` | Cubasis cookbook: the acceptance scenario is checked step by step. |
| CS-071 | 7 | C `tdd`, C `mcp-builder` | FL Studio Mobile cookbook, same acceptance form. |
| CS-072 | 7 | C `tdd`, R `android-permissions-security` | Ten everyday apps; permission dialogs are only answered for the allow list. |
| CS-080 | 8 | C `tdd`, C `mcp-builder` | Settings recipes: flight mode on and off, end to end. |
| CS-081 | 8 | C `tdd`, C `mcp-builder` | Speed measurement; the number must come from a command that exists. |
| CS-082 | 8 | C `tdd`, R `testing-setup` | Final documentation plus the CI and lint that must be green. |
| CS-090 | 9 | C `mcp-builder`, C `tdd` | MCP manifest and a guide that has to work for a foreign client. |
| CS-091 | 9 | C `tdd`, C `mcp-builder` | Safety review: brakes, blocklist, localhost binding, E28 limits. |
| CS-092 | 10 | C `tdd`, C `mcp-builder` | Fallback chain and the `max_tokens >= 2048` rule, both unit-tested with a fake router. |
| CS-093 | 10 | R `android-profiler`, C `tdd` | GPU proof on the real device; the measurement decides the rest of the wave. |
| CS-094 | 10 | R `android-profiler`, C `tdd` | Frame-change check on the GPU, 20 measurements. |
| CS-095 | 10 | R `android-profiler`, C `tdd` | Element hints and OCR locally; Claude still has to verify. |
| CS-096 | 10 | R `android-profiler`, C `tdd` | Benchmark candidates, keep exactly one, delete the rest. |
| CS-097 | 10 | C `tdd`, C `mcp-builder` | Re-measure the model chain and record what really happened. |

## How this file is checked

`python3 tools/sync_frontmatter.py --check-matrix` verifies that every task in
`tasks/` appears above and that every row lists at least two skills. A missing
task or a single-skill row fails the check, and CI runs the same command.