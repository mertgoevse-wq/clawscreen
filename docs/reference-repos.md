# Reference projects (E18)

Every row is a decision already taken in spec §22 — what we adopt and
what we refuse. This file exists so nobody re-runs the 50-repository
search. Rows marked *reference only*, *read only* or *do not copy* were
checked and rejected; do not retry them. A row marked **archived** must
never be used as a base.

Metadata (stars, licence, last push) is measured live via the GitHub API.

| | |
|---|---|
| Rows | 65 entries, 61 distinct repositories |
| Categories | 7 (A–G) |
| Last push seen among the listed repositories | 2026-10-04 |
| Regenerate | `python3 tools/build-reference-repos.py --live` |
| Verify without writing | `python3 tools/build-reference-repos.py --check` |

## Licence rule

Apache-2.0 and MIT may be used in our code with attribution. `NOASSERTION`
means GitHub could not identify a licence — treat it as *do not copy code
from it, read it only*. GPL-3.0 and LGPL-2.1 rows are read-only
references; nothing from them may end up in our source.

## Category A — Android control over ADB / MCP (feeds E1, E22, CS-010, CS-012)

| Repository | Stars | Licence | Last push | Archived | What we take from it |
|---|---:|---|---|---|---|
| [`Genymobile/scrcpy`](https://github.com/Genymobile/scrcpy) | 151,011 | Apache-2.0 | 2026-10-03 | no | Core dependency. The picture stream and fast taps (E22). Apache-2.0 allows using it inside our own code — keep it an external binary, do not fork it. |
| [`JuanCF/scrcpy-mcp`](https://github.com/JuanCF/scrcpy-mcp) | 110 | MIT | 2026-09-23 | no | Read first, do not adopt. Small MIT server showing the minimal scrcpy-over-MCP shape. Use it as the reference for our tool boundaries (Section 7), then write our own because it lacks blocklist, brakes and memory. |
| [`mobile-next/mobile-mcp`](https://github.com/mobile-next/mobile-mcp) | 8,648 | Apache-2.0 | 2026-10-04 | no | Reference for a cross-platform MCP tool surface. Copy the tool-naming discipline, not the code. |
| [`openatx/uiautomator2`](https://github.com/openatx/uiautomator2) | 8,406 | MIT | 2026-09-11 | no | The mature way to drive Android from Python. Use it inside Debian for `uiautomator dump` in apps where the inventory is empty — an escape hatch behind our own ADB path. |
| [`openatx/adbutils`](https://github.com/openatx/adbutils) | 1,082 | MIT | 2026-08-10 | no | Small, clean ADB wrapper in Python. Model for our thin ADB layer and for `tools/` scripts. |
| [`DeviceFarmer/stf`](https://github.com/DeviceFarmer/stf) | 4,586 | NOASSERTION | 2026-10-02 | no | Device farm. Reference for device-state handling and reconnect logic in `clawscreen connect` (Section 12). |
| [`DeviceFarmer/adbkit`](https://github.com/DeviceFarmer/adbkit) | 306 | NOASSERTION | 2026-10-02 | no | Node ADB library — the closest thing to our TypeScript transport. Use its connection/retry approach. |
| [`appium/appium`](https://github.com/appium/appium) | 22,043 | Apache-2.0 | 2026-10-04 | no | Reference for a stable action vocabulary (find / tap / wait) and its flaky-element handling. |
| [`appium/appium-uiautomator2-driver`](https://github.com/appium/appium-uiautomator2-driver) | 884 | Apache-2.0 | 2026-10-01 | no | Shows exactly which UiAutomator calls return nothing on canvas apps — the Cubasis problem in Section 5.1.5. |
| [`mobile-dev-inc/Maestro`](https://github.com/mobile-dev-inc/Maestro) | 15,932 | Apache-2.0 | 2026-10-02 | no | YAML test flows. Take the idea of readable, checkable UI scripts for our acceptance tests (Section 19). |
| [`cucumber/cucumber-js`](https://github.com/cucumber/cucumber-js) | 5,395 | MIT | 2026-10-04 | no | Gherkin step definitions. Take the *readable scenario* form for the memory-recipe tests (Section 8). |
| [`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers) | 91,003 | NOASSERTION | 2026-10-04 | no | Canonical MCP server examples. Use for tool schema and error-format correctness in CS-012. |
| [`modelcontextprotocol/typescript-sdk`](https://github.com/modelcontextprotocol/typescript-sdk) | 13,513 | NOASSERTION | 2026-10-02 | no | Our MCP SDK. Build the MCP server with this instead of hand-writing the protocol. |
| [`modelcontextprotocol/python-sdk`](https://github.com/modelcontextprotocol/python-sdk) | 24,479 | MIT | 2026-10-02 | no | Only if a Python helper is needed. |
| [`microsoft/mcp`](https://github.com/microsoft/mcp) | 3,730 | MIT | 2026-10-03 | no | Alternative MCP SDK; keep as a fallback if the TypeScript SDK misses a needed feature. |
| [`libimobiledevice/libusbmuxd`](https://github.com/libimobiledevice/libusbmuxd) | 691 | LGPL-2.1 | 2025-09-07 | no | Reference only. Out of scope (iOS). Listed so nobody re-suggests it. |

## Category B — Android testing, CI and build discipline (feeds E16, Section 14.3)

| Repository | Stars | Licence | Last push | Archived | What we take from it |
|---|---:|---|---|---|---|
| [`google/android-cuttlefish`](https://github.com/google/android-cuttlefish) | 726 | NOASSERTION | 2026-10-03 | no | Headless Android for CI device tests. Use when a real-device test must run on GitHub instead of the phone. |
| [`google/android-emulator-container-scripts`](https://github.com/google/android-emulator-container-scripts) | 2,094 | Apache-2.0 | 2026-10-04 | no | Run emulators inside containers — the practical recipe if cuttlefish is too heavy. |
| [`android/testing-samples`](https://github.com/android/testing-samples) | 9,289 | Apache-2.0 | 2025-07-18 | no | Official test samples. Patterns for the companion app's unit and UI tests (Section 19). |
| [`gradle/gradle-skills`](https://github.com/gradle/gradle-skills) | 14 | Apache-2.0 | 2026-09-30 | no | Official Gradle skills. Install via the skill flow in Section 14.2 — directly relevant to the companion app build. |
| [`facebook/buck2`](https://github.com/facebook/buck2) | 4,455 | Apache-2.0 | 2026-10-04 | no | Reference for hermetic, reproducible builds. Not adopted: too large a change for this project. |
| [`bazelbuild/bazel`](https://github.com/bazelbuild/bazel) | 25,919 | Apache-2.0 | 2026-10-02 | no | Reference only. Explicitly not adopted — Gradle stays (record the reason so nobody retries). |
| [`appium/appium`](https://github.com/appium/appium) | 22,043 | Apache-2.0 | 2026-10-04 | no | See category A. |

## Category C — Compose, architecture and design (feeds E21, Wave 4)

| Repository | Stars | Licence | Last push | Archived | What we take from it |
|---|---:|---|---|---|---|
| [`android/nowinandroid`](https://github.com/android/nowinandroid) | 21,878 | Apache-2.0 | 2026-10-04 | no | The design yardstick. Material 3, adaptive layouts, dark mode, clean layering. Copy its structure for the companion app, not its feature set. |
| [`android/compose-samples`](https://github.com/android/compose-samples) | 23,496 | Apache-2.0 | 2026-10-02 | no | Canonical snippets for the specific Compose problems the companion app hits. |
| [`android/architecture-samples`](https://github.com/android/architecture-samples) | 45,851 | Apache-2.0 | 2026-09-26 | no | MVVM / UDF structure for the companion app's state handling. |
| [`JetBrains/compose-multiplatform`](https://github.com/JetBrains/compose-multiplatform) | 19,401 | Apache-2.0 | 2026-10-03 | no | Only if a shared UI module ever makes sense. Not needed in v1.0. |
| [`android/architecture-components-samples`](https://github.com/android/architecture-components-samples) | 129 | Apache-2.0 | 2024-12-06 | **yes** | Archived — do not copy. Listed only to record that it was checked and rejected. |
| [`coil-kt/coil`](https://github.com/coil-kt/coil) | 11,913 | Apache-2.0 | 2026-10-04 | no | Image loading. Needed in the companion app for the session preview picture. |
| [`lysine-dev/okhttp`](https://github.com/lysine-dev/okhttp) | 47,083 | Apache-2.0 | 2026-10-04 | no | HTTP client for the companion app's local server calls (the repository was transferred, hence the new owner). |
| [`lysine-dev/retrofit`](https://github.com/lysine-dev/retrofit) | 43,938 | Apache-2.0 | 2026-10-02 | no | Typed local-server calls. Use only where it genuinely reduces boilerplate. |
| [`square/moshi`](https://github.com/square/moshi) | 10,165 | Apache-2.0 | 2026-10-01 | no | JSON for the companion app's local protocol. Compare against `kotlinx.serialization` and pick one — do not use both. |
| [`sqldelight/sqldelight`](https://github.com/sqldelight/sqldelight) | 6,887 | Apache-2.0 | 2026-10-03 | no | Local database for the operating memory (Section 8) — typed queries, compile-time checked. |
| [`bumptech/glide`](https://github.com/bumptech/glide) | 35,024 | NOASSERTION | 2026-10-02 | no | Mature image loading. Fallback if Coil does not fit. |
| [`ktlint/ktlint`](https://github.com/ktlint/ktlint) | 6,751 | MIT | 2026-10-02 | no | Formatter/linter gate in CI. No formatting argument survives a build. |

## Category D — Termux / Debian environment (feeds Section 4, CS-002)

| Repository | Stars | Licence | Last push | Archived | What we take from it |
|---|---:|---|---|---|---|
| [`termux/termux-app`](https://github.com/termux/termux-app) | 61,971 | NOASSERTION | 2026-09-26 | no | The terminal app itself. Check which of our tools need Termux-specific paths. |
| [`termux/proot-distro`](https://github.com/termux/proot-distro) | 3,526 | GPL-3.0 | 2026-09-23 | no | The Debian-in-Termux layer we build in. Understand its limits (no systemd, bind mounts) before debugging. |
| [`termux/termux-api`](https://github.com/termux/termux-api) | 4,414 | NOASSERTION | 2026-09-17 | no | Optional bridge for clipboard, sensors and notifications — candidate for the umlaut path (Section 7.4) if the companion app route fails. |
| [`termux/termux-tools`](https://github.com/termux/termux-tools) | 878 | GPL-3.0 | 2026-09-20 | no | The `termux-*` command set our scripts may call. |
| [`astral-sh/uv`](https://github.com/astral-sh/uv) | 90,406 | Apache-2.0 | 2026-10-04 | no | Fast Python package manager. Use it for all Python tooling in Debian instead of pip — far quicker on a phone CPU. |
| [`typst/typst`](https://github.com/typst/typst) | 56,407 | Apache-2.0 | 2026-10-02 | no | Typesetting tool. Only for optional PDF reports. |
| [`localsend/localsend`](https://github.com/localsend/localsend) | 93,353 | Apache-2.0 | 2026-10-04 | no | Reference for a local-network transfer service. Not needed; the project stays local (Section 5.1.7). |
| [`wireapp/wire-android`](https://github.com/wireapp/wire-android) | 253 | GPL-3.0 | 2026-10-04 | no | Reference for an Android app with serious security hygiene. Checklist source for the companion app. |
| [`Droid-ify/client`](https://github.com/Droid-ify/client) | 7,539 | GPL-3.0 | 2026-09-12 | no | Reference for a modern Compose app with a small surface area. |
| [`NeoApplications/Neo-Store`](https://github.com/NeoApplications/Neo-Store) | 5,336 | GPL-3.0 | 2026-10-01 | no | Reference for F-Droid-style distribution of the companion APK if sideloading gets annoying. |

## Category E — Quality yardstick and tooling (feeds E20, Section 14.5)

| Repository | Stars | Licence | Last push | Archived | What we take from it |
|---|---:|---|---|---|---|
| [`anthropics/claude-code`](https://github.com/anthropics/claude-code) | 149,414 | NOASSERTION | 2026-10-03 | no | We are running inside it. Its documented plugin/skill/hook mechanism is what Section 14.2 builds on. |
| [`anthropics/skills`](https://github.com/anthropics/skills) | 179,645 | NOASSERTION | 2026-10-03 | no | Official skill examples. Install several of these globally as the baseline skill set — this is the fastest quality win in the whole build. |
| [`eslint/eslint`](https://github.com/eslint/eslint) | 27,563 | MIT | 2026-10-04 | no | Lint gate in CI for the TypeScript MCP server. |
| [`prettier/prettier`](https://github.com/prettier/prettier) | 52,344 | MIT | 2026-10-04 | no | Format gate in CI. Formatting is not a style discussion. |
| [`bufbuild/buf`](https://github.com/bufbuild/buf) | 11,475 | Apache-2.0 | 2026-10-04 | no | Only if a protobuf schema is introduced. Record the 'no' so it is not revisited. |
| [`typst/typst`](https://github.com/typst/typst) | 56,407 | Apache-2.0 | 2026-10-02 | no | See category D. |
| [`astral-sh/uv`](https://github.com/astral-sh/uv) | 90,406 | Apache-2.0 | 2026-10-04 | no | See category D. |

## Category F — GPU / Vulkan on this exact phone (feeds E36, Section 21)

| Repository | Stars | Licence | Last push | Archived | What we take from it |
|---|---:|---|---|---|---|
| [`KhronosGroup/Vulkan-Tools`](https://github.com/KhronosGroup/Vulkan-Tools) | 497 | Apache-2.0 | 2026-10-04 | no | `vulkaninfo` for Android. How we prove on the phone that Vulkan really works before any GPU code is written (Section 21.2). |
| [`WearyConcern1165/xclipse-vulkan-decompiled`](https://github.com/WearyConcern1165/xclipse-vulkan-decompiled) | 11 | NOASSERTION | 2026-05-12 | no | Independent evidence of what the Xclipse driver really supports. Read-only reference — we do not link against a decompiled driver. |
| [`google-ai-edge/mediapipe`](https://github.com/google-ai-edge/mediapipe) | 37,162 | Apache-2.0 | 2026-10-04 | no | GPU-accelerated local vision. Candidate for the frame-difference / idle-detection helper (Section 21.3). |

## Category G — On-device inference, GPU-accelerated (feeds E36, Section 21.3)

| Repository | Stars | Licence | Last push | Archived | What we take from it |
|---|---:|---|---|---|---|
| [`ggml-org/llama.cpp`](https://github.com/ggml-org/llama.cpp) | 130,304 | MIT | 2026-10-04 | no | Vulkan backend (`GGML_VULKAN`). The strongest option for a local text/vision helper using the Xclipse GPU. Build from source in Termux; no NPU involved. |
| [`Tencent/ncnn`](https://github.com/Tencent/ncnn) | 23,907 | NOASSERTION | 2026-10-04 | no | Lightweight inference with a Vulkan backend. Alternative when the model is small. |
| [`google-ai-edge/LiteRT`](https://github.com/google-ai-edge/LiteRT) | 3,470 | Apache-2.0 | 2026-10-04 | no | Google's runtime (formerly TensorFlow Lite). Android-native, GPU delegate. Best fit if the helper ships inside the companion APK. |
| [`google-ai-edge/mediapipe`](https://github.com/google-ai-edge/mediapipe) | 37,162 | Apache-2.0 | 2026-10-04 | no | See category F. |
| [`microsoft/onnxruntime`](https://github.com/microsoft/onnxruntime) | 22,007 | MIT | 2026-10-04 | no | ONNX Runtime Mobile with the NNAPI/GPU providers. Cross-platform option. |
| [`pytorch/executorch`](https://github.com/pytorch/executorch) | 5,078 | NOASSERTION | 2026-10-04 | no | PyTorch's mobile runtime. Use only if we ever need a PyTorch model. |
| [`tensorflow/tensorflow`](https://github.com/tensorflow/tensorflow) | 200,702 | Apache-2.0 | 2026-10-04 | no | Reference for model formats. Do not vendor the full framework. |
| [`google/gemmlowp`](https://github.com/google/gemmlowp) | 1,845 | Apache-2.0 | 2024-01-29 | no | Low-precision kernels. Reference only. |
| [`qualcomm/ai-hub-models`](https://github.com/qualcomm/ai-hub-models) | 1,226 | BSD-3-Clause | 2026-10-03 | no | Read, do not run. Qualcomm Hexagon NPU models — wrong vendor for the Exynos 1580. Useful as the yardstick for what an NPU-optimised model set looks like. |
| [`qualcomm/ai-hub-apps`](https://github.com/qualcomm/ai-hub-apps) | 461 | BSD-3-Clause | 2026-10-01 | no | Same as above: reference for GPU/NPU delegate structure. |

## Take-over ledger

The take-over column above says what to adopt. This ledger is the honest counterpart: it only says *implemented* once the code or setup really contains the take-over and the task that needed it is done.

| Take-over | Task | What it looks like in this repository | State |
|---|---|---|---|
| scrcpy picture and control transport (Genymobile/scrcpy) | CS-010, CS-026 | Push `scrcpy-server` to the phone, start it, take a frame, send a tap. | planned |
| ADB reconnect and fallback logic (DeviceFarmer/adbkit, openatx/adbutils) | CS-010, CS-012, CS-014 | Thin ADB layer with timeouts, `get-state` check before every tool call. | planned |
| MCP tool schema and error format (modelcontextprotocol/typescript-sdk, anthropics/skills@mcp-builder) | CS-012, CS-090 | Server built with the official SDK; tool descriptions written the official way. | planned |
| Readable, checkable scenario format (mobile-dev-inc/Maestro, cucumber/cucumber-js) | CS-070, CS-071, CS-080 | Acceptance scenarios written as numbered, checkable steps. | planned |
| Material 3 and adaptive layout yardstick (android/nowinandroid, ehmo/platform-design-skills@android-design-guidelines) | CS-040, CS-042, CS-045 | Companion app screens: Material 3, dark mode, 48 dp targets, high contrast. | planned |
| Lint and format gates in CI (eslint, prettier, ktlint) | CS-003, CS-082 | Formatting is not a discussion; a finding fails the build. | planned |

0 of 6 take-overs are implemented so far. A row only leaves *planned* when the code exists and the task test has passed.

