# Installed community skills (E15)

These skills were found with `npx skills find`, reviewed, and installed for this
project. The build loop loads the skills listed per task in
[`tasks/skill-matrix.md`](../../tasks/skill-matrix.md) before implementing it.

## Why project-local and not global

The spec asks for a global install (`npx skills add … --global`). The agent
runner used for this build refuses global installs and prints the reason:

```
✗ mcp-builder → PromptScript: PromptScript does not support global skill installation
```

So the skills are installed into this repository under `.agents/skills/` and
symlinked for the agent runtime. They are loaded by name exactly as a global
install would be; only the storage location differs. This is recorded here
rather than silently worked around.

## What is installed

| Skill | Source | Licence | Used by | Why this one |
|---|---|---|---|---|
| `mcp-builder` | `anthropics/skills` | see `LICENSE.txt` | CS-012, CS-090 | Official guidance for building MCP servers: tool schema, error format, description writing. Our server is the deliverable, so the official shape matters. |
| `skill-creator` | `anthropics/skills` | see `LICENSE.txt` | CS-013, CS-025, CS-091 | Writes and checks the `/screen` and `/clawscreen-resume` skills, including the frontmatter rules the runtime needs. |
| `gradle-best-practices` | `gradle/gradle-skills` | Apache-2.0 | CS-040, CS-041, CS-042, CS-043, CS-044, CS-045 | Official Gradle skills, named in spec §22 category E. The companion app is a Gradle build; this keeps the build configuration correct. |
| `android-design-guidelines` | `ehmo/platform-design-skills` | see skill | CS-040, CS-042, CS-044, CS-045 | Material 3, touch target sizes, dark mode, contrast — the rules E21 makes mandatory for every companion-app screen. |
| `android-native-dev` | `minimax-ai/skills` | see skill | CS-041, CS-043 | Accessibility services, foreground services and Kotlin/Android specifics that the accessibility and volume-key work depends on. |
| `tdd` | `mattpocock/skills` | see skill | CS-015, CS-031, CS-032, CS-092 | Small-test-first discipline. The safety and fallback-chain modules are the places where a green test matters most, because a false "allowed" is dangerous. |

Not installed, and why (E20 forbids unused dependencies):

- `webapp-testing`, `frontend-design`, `theme-factory`, `web-artifacts-builder` —
  web skills. ClawScreen has no web frontend; the companion app is Jetpack Compose.
- `docx`, `pdf`, `pptx`, `xlsx` — document formats this project does not produce.
- `internal-comms`, `slack-gif-creator`, `academy-guide` — not related to the build.
- Everything the search returned under `scrcpy`, `adb` — the top hits were
  marketing, scraping or iOS tooling. None of them controls an Android phone
  over adb. The real take-over is source code, not a skill, and it is recorded
  in [`docs/reference-repos.md`](../../docs/reference-repos.md) category A.

## Runtime-provided skills

The agent runtime also offers Android/Compose skills that are not stored in
this repository (`android-profiler`, `compose-kotlin-agent-skills`, `adaptive`,
`testing-setup`, `android-permissions-security`). They were loadable by name in
this build session and the matrix assigns them where they fit. They are listed
separately here because they are not part of this repository's content.