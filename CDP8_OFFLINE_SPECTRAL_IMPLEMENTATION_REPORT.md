# CDP8 Offline And Spectral Implementation Report

Last updated: 2026-04-27

Companion roadmap:

- [`CDP8_OFFLINE_SPECTRAL_ROADMAP.md`](CDP8_OFFLINE_SPECTRAL_ROADMAP.md)

## Purpose

This report tracks the implementation work for the CDP8 offline, RT re-entry,
length-changing, and spectral/PVOC foundation.

The workspace contains multiple independent repositories. Every commit entry
must therefore state the repository, branch, changed files, verification, and
remaining risk.

## Tracking Rules

For every implementation commit, record:

- repository
- branch
- commit hash, once available
- commit subject
- files changed
- exact technical change
- verification command and result
- follow-up work created by the commit

Report-only commits may describe themselves by subject because a commit cannot
record its own final hash without changing that hash. When needed, the next
report update can backfill prior report commit hashes.

## Active Branches

| Repository | Branch | Base |
|---|---|---|
| workspace root | `docs/cdp8-offline-spectral-roadmap` | `master` |
| `xyona-lab` | `feature/cdp8-offline-foundation` | `docs/cdp8-offline-crossrefs` |
| `xyona-cdp-pack` | `feature/cdp8-offline-foundation` | `cdp8-rewrite-infra` |

## Commit Log

### Workspace Root

Repository: workspace root

Branch: `docs/cdp8-offline-spectral-roadmap`

Commit: `6daa5c9`

Subject: `chore: track CDP pack foundation pointer`

Files changed:

- `xyona-cdp-pack` gitlink
- `CDP8_OFFLINE_SPECTRAL_IMPLEMENTATION_REPORT.md`

Technical change:

- Updates the workspace root's `xyona-cdp-pack` gitlink to the CDP pack
  foundation branch state that contains:
  - `e06a193 fix(cdp-pack): stabilize Windows test preset`
  - `4708197 feat(cdp-pack): expose process shape metadata`
- Records this pointer update in the implementation report.

Verification:

- `xyona-cdp-pack` branch state was verified before the gitlink update:
  `.\build-and-test-dev.bat` passed with 11/11 CTest tests.

Follow-up:

- If publishing these branches, push `xyona-cdp-pack` before or alongside this
  workspace root branch so the gitlink target exists remotely.

### Workspace Root

Repository: workspace root

Branch: `docs/cdp8-offline-spectral-roadmap`

Commit: `9153919`

Subject: `docs: add CDP8 offline spectral roadmap`

Files changed:

- `CDP8_OFFLINE_SPECTRAL_ROADMAP.md`
- `CDP8_OFFLINE_SPECTRAL_IMPLEMENTATION_REPORT.md`

Technical change:

- Added a cross-repo roadmap for CDP8 offline execution, RT re-entry,
  length-changing output, typed spectral data, and PVOC/PVX readiness.
- Added this implementation report.
- Aligned the roadmap with `xyona-lab/docs/architecture/HQ_RT.md` Phase 5-7 so
  CDP RT re-entry uses the existing HQ/RT layer/clip architecture rather than a
  CDP-specific cache path.
- Documented the architecture documents considered by the roadmap:
  `HQ_RT.md`, `PDC.md`, `PURE_DATA_NODES.md`,
  `HIGH_END_ANALYZER_ARCHITECTURE_v2_2.md`, and related Lab ADRs.

Verification:

- `git diff --check`
- Result: passed before commit.

Follow-up:

- This report update backfills the root commit hash. This report-update commit
  can be backfilled by a later report update if needed.

### `xyona-lab`

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `2733f133`

Subject: `feat(lab): validate operator process metadata`

Files changed:

- `src/app/lab/adapters/OperatorProcessMetadata.h`
- `src/app/lab/adapters/OperatorProcessMetadata.cpp`
- `src/app/lab/audio/builder/AudioGraphBuilder.cpp`
- `src/app/CMakeLists.txt`
- `tests/OperatorProcessMetadataTests.cpp`
- `tests/CdpPackCanvasSmokeTests.cpp`
- `tests/CMakeLists.txt`

Technical change:

- Added Lab-side parsing for optional Core/pack operator `engine` metadata.
- Added explicit process-shape, output-length, and ABI-support enums for:
  block length-preserving, block stateful, whole-file, generator, analysis data,
  typed-data, and multi-output/multi-file operators.
- Kept operators with no `engine` metadata on the existing capability-driven
  path so current Core/Lab functionality remains compatible.
- Made invalid `engine` metadata fail closed instead of silently entering the
  RT/HQ block graph.
- Taught the current RT builder to reject whole-file, length-changing,
  no-audio/analysis, multi-output, and non-direct ABI operators before adapter
  construction.
- Taught the current HQ block builder the same guardrail. Whole-file and
  length-changing CDP operators remain blocked until the future offline session
  contract exists.
- Extended the CDP Canvas smoke test to verify that current CDP operators expose
  direct `block_length_preserving` / `same_as_input` metadata and remain eligible
  for the current RT and HQ block graphs.
- Added synthetic metadata unit tests for legacy descriptors, direct block
  operators, future whole-file length-changing operators, analysis-only output,
  and invalid metadata.

Verification:

- `cmake --build --preset windows-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `.\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Operator Process Metadata" --xyona-only --summary-only`
  - Result: passed; 5 tests, 36 passes, 0 failures.
- `$env:XYONA_OPERATOR_PACK_PATH='D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug'; .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only`
  - Result: passed; 6 tests, 194 passes, 0 failures.
- `ctest --test-dir build\windows-dev -C Debug -R "^xyona_lab_tests$" --output-on-failure`
  - Result: passed; 1/1 CTest tests passed.
- `git diff --check`
  - Result: passed. Git reported only line-ending normalization warnings.

Follow-up:

- Add user-facing graph-plan diagnostics for unsupported process shapes. The
  current builder keeps RT/HQ safety by skipping unsupported nodes, matching the
  existing capability-filter behavior, but users should eventually see a precise
  reason in the UI.
- Implement the offline session/artifact contract before enabling whole-file or
  length-changing CDP operators in HQ plans.

### `xyona-lab`

Repository: `xyona-lab`

Branch: `docs/cdp8-offline-crossrefs`

Commit: `595f51fe`

Subject: `docs(lab): reference CDP offline roadmap`

Files changed:

- `docs/architecture/HQ_RT.md`

Technical change:

- Added a cross-reference from the Lab HQ/RT architecture contract to the
  workspace-level CDP8 offline/spectral roadmap.
- Kept `HQ_RT.md` as the Lab-specific architecture source and framed the root
  roadmap as the cross-repo CDP/HQ extension.

Verification:

- `git diff --check`
- Result: passed. Git reported only existing line-ending normalization warnings.

Follow-up:

- CDP RT re-entry implementation must use the `HQ_RT.md` Phase 5-7 layer/clip
  bridge path instead of a CDP-specific playback cache.

### `xyona-cdp-pack`

Repository: `xyona-cdp-pack`

Branch: `feature/cdp8-offline-foundation`

Commit: `4708197`

Subject: `feat(cdp-pack): expose process shape metadata`

Files changed:

- `src/support/pack_descriptors.h`
- `src/operators/cdp_utility_identity.cpp`
- `src/operators/cdp_utility_db_gain.cpp`
- `src/operators/cdp_modify_loudness_gain.cpp`
- `src/operators/cdp_modify_loudness_dbgain.cpp`
- `src/operators/cdp_modify_loudness_phase_invert.cpp`
- `src/operators/cdp_modify_space_mirror.cpp`
- `src/operators/cdp_modify_space_narrow.cpp`
- `tests/test_cdp_pack.cpp`

Technical change:

- Added a shared block-length-preserving engine metadata fragment for CDP pack
  operator descriptors.
- Exposed host-visible process-shape metadata for all currently registered CDP
  operators:
  - `processShape: block_length_preserving`
  - `outputLength: same_as_input`
  - `wholeFileRequired: false`
  - `lengthChanging: false`
  - `audioOutput: true`
  - `multiOutput: false`
  - `abiV2Support: direct`
- Updated the pack-loader test to assert that every currently registered CDP
  operator publishes the block-length-preserving engine metadata through Core's
  metadata registry.

Verification:

- `.\build-and-test-dev.bat`
- Result: passed. Build succeeded and CTest reported `100% tests passed, 0 tests
  failed out of 11`.
- `git diff --check`
- Result: passed before commit. Git reported only line-ending normalization
  warnings.

Follow-up:

- The next metadata step is Lab-side interpretation/validation of these fields,
  not just pack publication.

### `xyona-cdp-pack`

Repository: `xyona-cdp-pack`

Branch: `feature/cdp8-offline-foundation`

Commit: `e06a193`

Subject: `fix(cdp-pack): stabilize Windows test preset`

Files changed:

- `ROADMAP_CDP8_REWRITE.md`
- `CMakeLists.txt`
- `CMakePresets.json`
- `build-and-test-dev.bat`
- `run-tests-dev.bat`

Technical change:

- Added a cross-reference from the CDP pack roadmap to the workspace-level CDP8
  offline/spectral roadmap.
- Changed the common CTest preset policy from `noTestsAction: ignore` to
  `noTestsAction: error`, so a broken or empty test discovery cannot be reported
  as success.
- Added `configuration: Debug` to the Windows test preset, fixing the
  multi-config CTest "Not Run" behavior.
- Added a CMake helper that copies Windows runtime DLLs for Core-linked test
  executables into the test output directory.
- Applied that helper to the CDP tests that link against `xyona-core`.
- Simplified `build-and-test-dev.bat` so it delegates to `build-dev.bat` and
  `run-tests-dev.bat`, avoiding duplicated configuration/build/test logic.
- Updated `run-tests-dev.bat` to invoke CTest with the Debug configuration
  explicitly.

Verification:

- `.\build-and-test-dev.bat`
- Result: passed. Build succeeded and CTest reported `100% tests passed, 0 tests
  failed out of 11`.
- `ctest --preset windows-msvc-debug --output-on-failure`
- Result: passed without manual `PATH` edits. CTest reported `100% tests passed,
  0 tests failed out of 11`.

Development note:

- An initial attempt to copy `$<TARGET_RUNTIME_DLLS:xyona_pack_cdp_ops>` from
  the pack library failed because that target does not link the Core DLL
  directly. The committed fix copies runtime DLLs only for the Core-linked test
  executables.

Follow-up:

- Add CI once the same script behavior is confirmed on a clean checkout/runner.
- Keep the next implementation slice focused on host-visible process-shape
  metadata.

## Verification Log

- workspace root: `git diff --check` passed before commit.
- `xyona-lab`: `git diff --check` passed before commit.
- `xyona-cdp-pack`: `git diff --check` passed before commit.
- `xyona-cdp-pack`: `.\build-and-test-dev.bat` passed; 11/11 CTest tests passed.
- `xyona-cdp-pack`: `ctest --preset windows-msvc-debug --output-on-failure`
  passed without manual runtime DLL `PATH`; 11/11 CTest tests passed.
- `xyona-cdp-pack`: `.\build-and-test-dev.bat` passed after process-shape
  metadata publication; 11/11 CTest tests passed.
- `xyona-lab`: `cmake --build --preset windows-dev --target xyona_lab_tests`
  passed after Lab-side metadata validation was added.
- `xyona-lab`: `.\build\windows-dev\tests\Debug\xyona_lab_tests.exe
  --test="Operator Process Metadata" --xyona-only --summary-only` passed; 5
  tests, 36 passes, 0 failures.
- `xyona-lab`: CDP Pack Canvas Smoke passed with
  `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug`;
  6 tests, 194 passes, 0 failures.
- `xyona-lab`: `ctest --test-dir build\windows-dev -C Debug -R
  "^xyona_lab_tests$" --output-on-failure` passed; 1/1 CTest tests passed.

## Open Risks

- The first implementation slice must not fork a CDP-only RT re-entry path. It
  must align with `xyona-lab/docs/architecture/HQ_RT.md` Phase 5-7.
- Unsupported process shapes are currently kept out of RT/HQ block plans by
  builder guardrails and debug logs. Before exposing whole-file CDP operators to
  normal users, Lab needs user-facing graph-plan diagnostics.
- Whole-file and length-changing CDP operators must remain HQ/offline-session
  work until the artifact/result contract exists. They must not be forced
  through the current block adapter path.
