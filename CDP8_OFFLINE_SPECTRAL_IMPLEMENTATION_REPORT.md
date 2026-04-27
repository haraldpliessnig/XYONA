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
| `xyona-lab` | `docs/cdp8-offline-crossrefs` | `master` |
| `xyona-cdp-pack` | `feature/cdp8-offline-foundation` | `cdp8-rewrite-infra` |

## Commit Log

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

## Workspace Root Documentation Work

Commit hash: to be backfilled by a later report update if needed.

Subject planned for this report commit: `docs: add CDP8 offline spectral roadmap`

### Workspace Root

Files:

- `CDP8_OFFLINE_SPECTRAL_ROADMAP.md`
- `CDP8_OFFLINE_SPECTRAL_IMPLEMENTATION_REPORT.md`

Work:

- Added a cross-repo roadmap for CDP8 offline execution, RT re-entry,
  length-changing output, typed spectral data, and PVOC/PVX readiness.
- Added this implementation report.
- Updated the roadmap to explicitly align CDP RT re-entry with
  `xyona-lab/docs/architecture/HQ_RT.md` Phase 5-7.

### `xyona-lab`

No uncommitted work.

### `xyona-cdp-pack`

No uncommitted work.

## Verification Log

- `xyona-lab`: `git diff --check` passed before commit.
- `xyona-cdp-pack`: `git diff --check` passed before commit.
- `xyona-cdp-pack`: `.\build-and-test-dev.bat` passed; 11/11 CTest tests passed.
- `xyona-cdp-pack`: `ctest --preset windows-msvc-debug --output-on-failure`
  passed without manual runtime DLL `PATH`; 11/11 CTest tests passed.

## Open Risks

- The first implementation slice must not fork a CDP-only RT re-entry path. It
  must align with `xyona-lab/docs/architecture/HQ_RT.md` Phase 5-7.
- Windows CDP pack tests currently require explicit configuration/runtime DLL
  handling and are the first implementation target.
