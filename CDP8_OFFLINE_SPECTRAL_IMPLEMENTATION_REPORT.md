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
| `xyona-core` | `feature/cdp8-offline-foundation` | `main` |
| `xyona-lab` | `feature/cdp8-offline-foundation` | `docs/cdp8-offline-crossrefs` |
| `xyona-cdp-pack` | `feature/cdp8-offline-foundation` | `cdp8-rewrite-infra` |

## Continuation Note

This is the handoff state after the first graph-scheduled whole-file CDP/HQ
vertical slice, the first Canvas/runtime eligibility state for HQ-only CDP
nodes, and the first in-memory materialized layer/clip bridge for RT-ready
offline audio artifacts. The materialized store now also has the first
file-backed asset/ProjectState manifest persistence API plus normal Lab
Project save/open/save-as orchestration.

Latest implementation commits:

- `xyona-core`: `d4d437b feat(core): add offline pack ABI contract`
- `xyona-cdp-pack`: `57105fa feat(cdp-pack): add whole-file loudness normalise`
- `xyona-lab`: `16e662dc feat(lab): persist materialized audio assets`
- `xyona-lab`: `ad6a7d53 feat(lab): wire materialized assets into project lifecycle`
- workspace root: this report update records the latest Lab lifecycle slice.

Current proven capability:

- `cdp.modify.loudness_normalise` is the reference same-length whole-file
  operator.
- The pack advertises the operator as HQ-only and rejects block processing for
  it.
- Lab can call the pack's optional offline API directly, materialize the output
  audio buffer, validate the `OfflineSessionContract`, and mark the artifact as
  RT re-entry-capable.
- Lab can now also schedule same-length whole-file pack nodes inside the
  offline/HQ graph for the first supported graph shape:
  source/block region -> one whole-file node -> direct terminal audio targets.
- Lab has a headless integration test that proves the real graph path:
  `lab.grid_source -> cdp.utility.db_gain -> cdp.modify.loudness_normalise -> lab.mainbus_out`.
- Canvas nodes now derive a runtime eligibility state from descriptor
  capabilities and engine metadata, so `cdp.modify.loudness_normalise` is
  marked as valid offline whole-file work instead of an invalid RT node.
- Realtime graph diagnostics now distinguish offline-materializable HQ-only
  nodes from genuinely unsupported capability/process-shape failures.
- Lab can materialize the first RT-ready audio artifact from an offline render
  into `MaterializedAudioStore` as a layer-backed clip.
- The materialized clip bridge preserves producer/session/artifact metadata and
  resident in-memory audio for the current Lab session; its manifest round-trip
  stores metadata only and deliberately does not inline raw audio frames.
- `MaterializedAudioStore` can now write resident materialized layers as WAV
  assets, mark the artifact as file-backed audio, and restore resident buffers
  from those assets.
- `ProjectState` now has a manifest anchor for materialized audio metadata, so
  the store manifest can survive a project save/load round-trip without embedding
  raw audio in the `.xyona` XML.
- MainWindow project save and save-as now persist the active
  `MaterializedAudioStore` before writing the `.xyona` file. Assets are stored
  beside the project in `ProjectName.xyona-assets/materialized_audio`, while the
  manifest keeps relative WAV filenames.
- MainWindow project open now rehydrates materialized assets automatically. A
  missing asset directory or file produces a user-visible warning and does not
  leave stale layers in the active store.
- The plan is now gated: the current whole-buffer offline ABI, currently named
  `offline_whole_buffer_prototype`, is a prototype/reference bridge. Length-changing,
  PVOC/spectral, multi-output, and production-scale long-file CDP work require
  the implemented and tested Offline Session ABI.
- The prototype whole-buffer ABI no longer uses release-like `v1` names in the
  live code path. Core installs `xyona/api/offline_whole_buffer_prototype.h`,
  the CDP pack exports `xyona_pack_get_offline_whole_buffer_prototype_api`, and
  Lab resolves that symbol explicitly.

Resume commands on a fresh machine:

```powershell
git -C xyona-core switch feature/cdp8-offline-foundation
git -C xyona-core pull
git -C xyona-cdp-pack switch feature/cdp8-offline-foundation
git -C xyona-cdp-pack pull
git -C xyona-lab switch feature/cdp8-offline-foundation
git -C xyona-lab pull
git switch docs/cdp8-offline-spectral-roadmap
git pull
```

Verification baseline to rerun before the next implementation step:

```powershell
cd D:\GITHUB\XYONA\xyona-core
cmake --build --preset windows-msvc-debug
ctest --test-dir build\windows-msvc-debug -C Debug --output-on-failure

cd D:\GITHUB\XYONA\xyona-cdp-pack
$env:XYONA_CORE_ROOT='D:\GITHUB\XYONA\xyona-core'
cmake --build --preset windows-msvc-debug
ctest --preset windows-msvc-debug --output-on-failure

cd D:\GITHUB\XYONA\xyona-lab
$env:XYONA_CORE_PATH='D:\GITHUB\XYONA\xyona-core'
cmake --build --preset windows-dev --target xyona_lab_tests
$env:XYONA_OPERATOR_PACK_PATH='D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug'
.\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test='Offline Pack Processor Client' --xyona-only --summary-only
.\build\windows-dev\tests\Debug\xyona_lab_tests.exe --xyona-only --summary-only
```

Next implementation steps, in order:

1. Finalize the gate documentation:
   - the current whole-buffer offline ABI is prototype/reference only.
   - `MaterializedAudioStore` is the concrete `HQ_RT.md` Phase 7 store line.
   - length-changing and PVOC/spectral require implemented/tested
     Offline Session ABI.
2. Finish materialized asset production persistence:
   - cleanup/orphan policy
   - dependency signatures and stale detection
   - user-visible `Re-render required` state
3. Make the realtime LayerPlayer consume the materialized layer/clip store with
   no disk I/O or pack calls in the audio callback.
4. Add CI baseline for Core, Pack, and Lab on macOS Clang and Windows MSVC.
5. Implement the Offline Session ABI with a reference operator
   and tests for normal completion, progress, and cancellation.
6. Port `cdp.modify.loudness_normalise` onto the session lifecycle and remove
   or internalize the prototype whole-buffer ABI surface before release.
7. Only after the Offline Session ABI is implemented and tested, start
   length-changing audio.
8. Only after the Offline Session ABI plus typed data/asset handles and CDP8
   golden fixtures, start PVOC/spectral work.
9. Before the first CDP generator, add the explicit null-upstream generator
   graph/render test.

Hard gate summary:

- The current whole-buffer offline ABI remains usable only as a temporary
  prototype/reference path for existing same-length work. It is not a release
  production path for length-changing, PVOC/spectral, multi-output, or
  long-running CDP operators.
- Persistence is not production-complete until materialized asset dependencies
  are fingerprinted and stale/missing assets produce a visible re-render state.
- PVOC/spectral has an explicit hard dependency on implemented/tested
  Offline Session ABI, typed data or asset handles, and CDP8 golden fixtures.

## Commit Log

### Project-Lifecycle Materialized Asset Persistence

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `ad6a7d53`

Subject: `feat(lab): wire materialized assets into project lifecycle`

Files changed:

- `src/app/lab/audio/engine/MaterializedAudioProjectPersistence.h`
- `src/app/lab/audio/engine/MaterializedAudioProjectPersistence.cpp`
- `src/app/lab/audio/engine/MaterializedAudioStore.cpp`
- `src/app/MainWindow.cpp`
- `src/app/CMakeLists.txt`
- `tests/MaterializedAudioStoreTests.cpp`
- `docs/architecture/HQ_RT.md`

Technical change:

- Added a Lab-side project persistence bridge for materialized audio assets.
- Project save and save-as now persist resident materialized audio to
  `ProjectName.xyona-assets/materialized_audio` and store relative WAV filenames
  in the `ProjectState` materialized audio manifest before the `.xyona` file is
  written.
- Project open now loads the manifest plus asset directory back into the active
  `AudioEngineManager` store. Missing assets are reported with a warning and do
  not leave stale layers in the active store.
- Fixed a JUCE debug assertion in repeated persistence/save-as by deriving a
  filename from stored relative paths without constructing `juce::File` from a
  relative path string.
- Updated `HQ_RT.md` to mark the Project save/open/save-as lifecycle as done and
  keep staleness, cleanup, and RT LayerPlayer consumption as the remaining Phase
  7 work.

Verification:

- `xyona-lab`: `git diff --check`
  - Result: passed.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  - Result: passed; 3 tests, 59 passes, 0 failures.
- Full Lab CTest was intentionally not rerun for this slice; the targeted
  lifecycle suite covers the changed path and avoids the long blanket test run.

Follow-up:

- Add materialized asset dependency signatures, stale detection, and a visible
  `Re-render required` state.
- Define cleanup/orphan policy for project asset directories.
- Add realtime LayerPlayer consumption of materialized clips without disk I/O in
  the audio callback.

### Prototype Whole-Buffer ABI Rename

Repositories:

- `xyona-core`: `1b0468e refactor(core): rename offline prototype ABI`
- `xyona-cdp-pack`: `142ca88 refactor(cdp-pack): use offline prototype ABI name`
- `xyona-lab`: `9d8badad refactor(lab): load offline prototype ABI`

Technical change:

- Renamed the live prototype header from a release-looking offline-pack-v1 name
  to `xyona/api/offline_whole_buffer_prototype.h`.
- Renamed the exported CDP pack symbol to
  `xyona_pack_get_offline_whole_buffer_prototype_api`.
- Renamed prototype C ABI types and constants to the
  `xyona_pack_offline_whole_buffer_prototype_*` /
  `XYONA_PACK_OFFLINE_WHOLE_BUFFER_PROTOTYPE_*` namespace.
- Updated Lab's `OfflinePackProcessorClient` dynamic lookup to require the new
  prototype symbol.

Verification:

- `xyona-core`: `cmake --build --preset macos-clang-debug` passed.
- `xyona-core`: `ctest --preset macos-clang-debug --output-on-failure` passed;
  7/7 tests.
- `xyona-cdp-pack`: `XYONA_CORE_ROOT=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build --preset macos-clang-debug` passed.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug --output-on-failure -R '^cdp_modify_loudness_normalise_tests$'` passed; 1/1 targeted test.
- `xyona-cdp-pack`: `nm -gU build/macos-clang-debug/xyona_pack_cdp_ops.dylib | rg "offline.*api"` showed only `_xyona_pack_get_offline_whole_buffer_prototype_api`.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests` passed with existing warning classes.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="Offline Pack Processor Client" --summary-only --xyona-only` passed; 1 test, 22 passes.
- `git diff --check` passed for Root, Core, Pack, and Lab.

### `xyona-core`

Repository: `xyona-core`

Branch: `feature/cdp8-offline-foundation`

Commit: `d4d437b`

Subject: `feat(core): add offline pack ABI contract`

Files changed:

- `include/xyona/api/offline_whole_buffer_prototype.h`
- `CMakeLists.txt`
- `tests/CMakeLists.txt`
- `tests/test_operator_packs.cpp`

Technical change:

- Added a small optional C ABI for whole-file/offline pack execution:
  query, process, parameter values, immutable/mutable audio views, output
  artifact classification, length model, materialization, and RT re-entry
  policy.
- Installed the new public API header with the existing Core package headers.
- Fixed the Core Windows test harness so CTest copies runtime DLLs for
  Core-linked tests and passes the generated pack output directory into
  `test_operator_packs`.

Verification:

- `cmake --build --preset windows-msvc-debug`
  - Result: passed. Build succeeded with existing warning classes only.
- `ctest --test-dir build\windows-msvc-debug -C Debug --output-on-failure`
  - Result: passed; 7/7 CTest tests passed.
- `git diff --check`
  - Result: passed. Git reported only line-ending normalization warnings.

Follow-up:

- Future offline ABI revisions should remain optional and additive so existing
  block-only packs keep working unchanged.

### `xyona-cdp-pack`

Repository: `xyona-cdp-pack`

Branch: `feature/cdp8-offline-foundation`

Commit: `57105fa`

Subject: `feat(cdp-pack): add whole-file loudness normalise`

Files changed:

- `src/operators/cdp_modify_loudness_normalise.h`
- `src/operators/cdp_modify_loudness_normalise.cpp`
- `src/offline_api.cpp`
- `src/pack_registration.cpp`
- `src/support/pack_descriptors.h`
- `CMakeLists.txt`
- `tests/test_cdp_modify_loudness_normalise.cpp`
- `specs/cdp8_inventory.yaml`
- `ROADMAP_CDP8_REWRITE.md`
- `REPORT_CDP8_REWRITE_STATUS.md`

Technical change:

- Added `cdp.modify.loudness_normalise` as the first whole-file,
  length-preserving, HQ-only CDP8 operator.
- The descriptor advertises `canRealtime=false`, `canHQ=true`, CDP8 provenance
  for `modify loudness 3` / `LOUDNESS_NORM`, and
  `whole_file_length_preserving` engine metadata.
- The block v2 process path deliberately returns unsupported for this operator;
  actual execution goes through `xyona_pack_get_offline_whole_buffer_prototype_api`.
- The offline process scans the full input for peak level, sanitizes non-finite
  boundary samples, materializes same-length audio, and rejects invalid target
  peak parameters.
- Updated pack inventory, roadmap, and status report so normalise is no longer
  incorrectly listed as infrastructure-blocked.

Verification:

- `$env:XYONA_CORE_ROOT='D:\GITHUB\XYONA\xyona-core'; cmake --build --preset windows-msvc-debug --target test_cdp_modify_loudness_normalise`
  - Result: passed.
- `ctest --preset windows-msvc-debug -R cdp_modify_loudness_normalise_tests --output-on-failure`
  - Result: passed; 1/1 targeted test passed.
- `ctest --preset windows-msvc-debug --output-on-failure`
  - Result: passed; 12/12 CTest tests passed.
- `git diff --check`
  - Result: passed. Git reported only line-ending normalization warnings.

Follow-up:

- Use this operator as the reference implementation for additional same-length
  whole-file CDP tools.
- Do not move length-changing or spectral tools onto this path until output
  length negotiation and typed data artifacts are implemented.

### `xyona-lab`

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `a83cf769`

Subject: `feat(lab): render whole-file offline pack artifacts`

Files changed:

- `src/app/lab/audio/engine/OfflinePackProcessorClient.h`
- `src/app/lab/audio/engine/OfflinePackProcessorClient.cpp`
- `src/app/lab/audio/engine/OfflineRenderEngine.h`
- `src/app/lab/audio/engine/OfflineRenderEngine.cpp`
- `src/app/CMakeLists.txt`
- `tests/OfflinePackProcessorClientTests.cpp`
- `tests/CMakeLists.txt`

Technical change:

- Added a Lab-side offline pack client that resolves a loaded pack by operator
  namespace, opens its dynamic library, obtains `xyona_pack_get_offline_whole_buffer_prototype_api`,
  queries the output contract, materializes an audio buffer, validates the
  `OfflineSessionContract`, and returns an RT re-entry-capable audio artifact.
- Added `OfflineRenderEngine::renderWholeFileOperatorToBuffer` as the first
  explicit host entry point for whole-file pack work.
- Added an optional Lab unit test that runs
  `cdp.modify.loudness_normalise` against the local CDP pack build and verifies
  descriptor capabilities, rendered samples, session flags, artifact length
  model, and RT re-entry eligibility.

Verification:

- `$env:XYONA_CORE_PATH='D:\GITHUB\XYONA\xyona-core'; cmake --build --preset windows-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `$env:XYONA_OPERATOR_PACK_PATH='D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug'; .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test='Offline Pack Processor Client' --xyona-only --summary-only`
  - Result: passed; 1 test, 22 passes, 0 failures.
- Same pack path, `--test='CDP Pack Canvas Smoke' --xyona-only --summary-only`
  - Result: passed; 6 tests, 194 passes, 0 failures.
- Same pack path, `.\build\windows-dev\tests\Debug\xyona_lab_tests.exe --xyona-only --summary-only`
  - Result: passed; 1155 tests, 943516 passes, 0 failures.
- `git diff --check`
  - Result: passed. Git reported only line-ending normalization warnings.

Follow-up:

- Completed by `ffdeb47f feat(lab): schedule whole-file offline pack nodes`.
- Persist materialized artifacts through the HQ/RT layer/clip bridge described
  in `xyona-lab/docs/architecture/HQ_RT.md`.

### `xyona-lab`

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `ffdeb47f`

Subject: `feat(lab): schedule whole-file offline pack nodes`

Files changed:

- `src/app/lab/adapters/OperatorProcessMetadata.h`
- `src/app/lab/adapters/OperatorProcessMetadata.cpp`
- `src/app/lab/audio/adapter/AudioIOHostAdapters.h`
- `src/app/lab/audio/adapter/AudioIOHostAdapters.cpp`
- `src/app/lab/audio/builder/AudioGraphBuilder.cpp`
- `src/app/lab/audio/engine/AudioGraphProcessor.h`
- `src/app/lab/audio/engine/OfflineRenderEngine.cpp`
- `tests/OperatorProcessMetadataTests.cpp`

Technical change:

- Added `supportsOfflineWholeFileHostContract(...)` so Lab can recognize
  HQ-only, same-length, whole-file pack operators from descriptor metadata.
- Added `OfflineWholeFilePackHostAdapter`, an offline-only graph adapter that
  captures full input audio during block graph execution, captures the first
  parameter snapshot, and invokes `OfflinePackProcessorClient` after the block
  region has rendered.
- Extended `GraphPlan` with scheduled whole-file node sidecar metadata.
- Taught `OfflineGraphBuilder` to keep supported same-length whole-file nodes
  in the HQ graph and construct `OfflineWholeFilePackHostAdapter` for them.
- Taught `OfflineRenderEngine` to materialize exactly one active whole-file
  node in the first supported scheduling slice:
  - direct terminal audio targets only
  - whole-file node must feed every render terminal
  - terminal targets cannot have additional direct inputs
  - channel mappings must be complete
  - output length must match the internal render range
- Replaces device/file-out/signal-capture material with the materialized
  whole-file result when the supported terminal shape is detected.
- Added a metadata unit test proving that
  `whole_file_length_preserving` / `same_as_input` / `requires_whole_file_host_contract`
  is rejected by current block builders but accepted by the offline whole-file
  scheduler helper.

Verification:

- `xyona-core`: `./build-dev.sh`
  - Result: passed.
- `xyona-cdp-pack`: `./build-dev.sh`
  - Result: passed.
- `xyona-cdp-pack`: `ctest --preset macos-clang-debug --output-on-failure`
  - Result: passed; 12/12 CTest tests passed.
- `xyona-lab`: `./build-dev.sh`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed after adding the metadata test.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Operator Process Metadata" --summary-only --xyona-only`
  - Result: passed; 6 tests, 49 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug ctest --test-dir build/macos-dev --output-on-failure -R '^(xyona_lab_tests|operator_packs_tests)$'`
  - Result: passed; 2/2 CTest tests passed.
- `xyona-lab`: `git diff --check`
  - Result: passed.

Follow-up:

- Completed by `6dee2ec5 test(lab): cover whole-file CDP graph render`.
- Keep length-changing, multi-output, and typed data operators closed until
  output-length negotiation and typed artifact flow exist.

### `xyona-lab`

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `6dee2ec5`

Subject: `test(lab): cover whole-file CDP graph render`

Files changed:

- `tests/AudioEngineManagerTests.cpp`

Technical change:

- Added a headless Lab integration test for the real whole-file CDP graph path:
  `lab.grid_source -> cdp.utility.db_gain -> cdp.modify.loudness_normalise -> lab.mainbus_out`.
- The test loads the CDP pack through `XYONA_OPERATOR_PACK_PATH`, builds an
  `OfflineGraphBuilder` plan, and asserts that exactly one whole-file CDP node
  is scheduled.
- The render path goes through `AudioEngineManager::renderOffline`, not the
  direct offline pack client.
- The source grid pulses are first attenuated by `cdp.utility.db_gain`; the
  whole-file normalise node must then materialize stereo pulses back to target
  peak while preserving the render length and silent non-pulse samples.
- The pack-load helper now tolerates the full test suite order where the CDP
  pack may already be loaded and `loadOperatorPacksDefault()` reports a
  duplicate path.

Verification:

- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --summary-only --xyona-only`
  - Result: passed; 35 tests, 542 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug ctest --test-dir build/macos-dev --output-on-failure -R '^(xyona_lab_tests|operator_packs_tests)$'`
  - Result: passed; 2/2 CTest tests passed.
- `xyona-lab`: `git diff --check`
  - Result: passed.

Follow-up:

- Move from render-path proof to Canvas/UI validity state for HQ-only CDP nodes.
- Keep artifact persistence and output-length negotiation as the next
  infrastructure milestones before length-changing CDP operators are enabled.

### `xyona-lab`

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `6131bce2`

Subject: `feat(lab): mark offline-only CDP nodes`

Files changed:

- `src/app/lab/audio/builder/AudioGraphBuilder.cpp`
- `src/app/lab/audio/builder/GraphPlanDiagnostics.cpp`
- `src/app/lab/audio/builder/GraphPlanDiagnostics.h`
- `src/app/lab/canvas/Canvas.CoreNodes.cpp`
- `src/app/lab/canvas/nodes/common/NodeData.h`
- `src/app/lab/canvas/nodes/generic/renderers/GenericNodeRenderer.cpp`
- `tests/AudioEngineManagerTests.cpp`
- `tests/CdpPackCanvasSmokeTests.cpp`

Technical change:

- Added non-persisted Canvas node runtime eligibility state derived from
  descriptor capabilities plus engine metadata.
- `cdp.modify.loudness_normalise` now binds as `OfflineWholeFile` in Canvas,
  while block CDP pack nodes continue to bind as realtime+offline capable.
- Generic node rendering now draws a subtle accent for offline-only or
  currently unsupported runtime states without adding visible explanatory text
  to the node.
- Realtime `AudioGraphBuilder` diagnostics now emit
  `NodeOfflineOnlyMaterializable` for HQ/offline-only nodes that are valid for
  offline materialization, rather than treating them as generic missing
  `canRealtime` capability.
- Process-shape diagnostics now mention whole-file input before the generic
  unsupported host-contract message when both apply.
- The CDP Canvas smoke test now covers `cdp.modify.loudness_normalise` metadata,
  NodeBinder instantiation, parameter mini-readout, and offline-whole-file
  runtime state.

Verification:

- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  - Result: passed; 7 tests, 220 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --summary-only --xyona-only`
  - Result: passed; 35 tests, 542 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug ctest --test-dir build/macos-dev --output-on-failure -R '^(xyona_lab_tests|operator_packs_tests)$'`
  - Result: passed; 2/2 CTest tests passed.
- `xyona-lab`: `git diff --check`
  - Result: passed.

Follow-up:

- Completed in part by `e44c0d7f feat(lab): materialize offline renders as
  clips`.
- Finish file-backed artifact persistence and realtime LayerPlayer consumption
  through the existing `HQ_RT.md` layer/clip architecture.
- Keep length-changing and typed spectral CDP operators gated until output
  length negotiation and typed artifact semantics exist.

### `xyona-lab`

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `e44c0d7f`

Subject: `feat(lab): materialize offline renders as clips`

Files changed:

- `src/app/lab/audio/engine/MaterializedAudioStore.h`
- `src/app/lab/audio/engine/MaterializedAudioStore.cpp`
- `src/app/lab/audio/engine/AudioEngineManager.h`
- `src/app/lab/audio/engine/AudioEngineManager.cpp`
- `src/app/CMakeLists.txt`
- `tests/MaterializedAudioStoreTests.cpp`
- `tests/AudioEngineManagerTests.cpp`
- `tests/CMakeLists.txt`

Technical change:

- Added `MaterializedAudioStore`, a Lab-owned layer/clip store for RT-ready
  offline audio artifacts.
- The store validates `OfflineSessionContract` / `OfflineArtifactContract`,
  rejects data-only or non-RT-reentry artifacts, copies resident audio into a
  materialized layer, and creates timeline clips that reference that layer.
- Added a `juce::ValueTree` manifest round-trip for layer/clip metadata. The
  manifest preserves artifact metadata and IDs, but deliberately does not
  serialize raw audio buffers.
- Added `AudioEngineManager::renderOfflineToMaterializedClip(...)`, which
  renders the HQ/offline graph, picks the first RT-ready audio artifact,
  normalizes its sample/channel/range metadata to the rendered buffer, and
  inserts it into the materialized store.
- Extended the CDP whole-file normalise integration test so the graph render is
  also materialized as a reusable layer-backed clip.

Verification:

- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  - Result: passed; 2 tests, 23 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  - Result: passed; 7 tests, 220 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --summary-only --xyona-only`
  - Result: passed; 35 tests, 555 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug ctest --test-dir build/macos-dev --output-on-failure -R '^(xyona_lab_tests|operator_packs_tests)$'`
  - Result: passed; 2/2 CTest tests passed.
- `xyona-lab`: `git diff --check`
  - Result: passed.

Follow-up:

- Completed in part by `16e662dc feat(lab): persist materialized audio assets`.
- Wire the materialized store into the actual project save/load lifecycle so
  rendered assets and manifests are persisted automatically for normal projects.
- Add the realtime LayerPlayer adapter/path that consumes materialized clips
  instead of re-running the HQ graph.
- Keep length-changing and typed spectral CDP operators gated until the bridge
  can handle persisted artifacts, output-length negotiation, and typed data.

### `xyona-lab`

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `16e662dc`

Subject: `feat(lab): persist materialized audio assets`

Files changed:

- `src/app/lab/audio/engine/MaterializedAudioStore.h`
- `src/app/lab/audio/engine/MaterializedAudioStore.cpp`
- `src/app/state/ProjectState.h`
- `src/app/state/projectstate/ProjectStateCoreMethods.inc`
- `src/app/state/projectstate/ProjectStatePreamble.inc`
- `tests/MaterializedAudioStoreTests.cpp`

Technical change:

- Added `MaterializedAudioStore::persistResidentAudioToDirectory(...)` to write
  resident materialized layers as WAV assets and update their artifact metadata
  to file-backed audio.
- Added `loadResidentAudioFromDirectory(...)` and
  `restoreFromValueTreeAndLoadAudio(...)` so a metadata manifest plus an asset
  directory can rehydrate resident layer buffers.
- Added a `ProjectState` root subtree for materialized audio and public
  `getMaterializedAudioManifest()` / `setMaterializedAudioManifest(...)`
  methods. The project file stores only the manifest subtree; raw audio stays in
  the asset directory.
- Extended `MaterializedAudioStoreTests` to prove metadata-only restore,
  WAV-backed restore, and ProjectState save/load of the manifest.

Verification:

- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  - Result: passed; 2 tests, 39 passes, 0 failures.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="ProjectState Round-Trip" --summary-only --xyona-only`
  - Result: passed; 8 tests, 138 passes, 0 failures.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="ProjectState Schema Validation" --summary-only --xyona-only`
  - Result: passed; 4 tests, 8 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --summary-only --xyona-only`
  - Result: passed; 35 tests, 555 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug ctest --test-dir build/macos-dev --output-on-failure -R '^(xyona_lab_tests|operator_packs_tests)$'`
  - Result: passed; 2/2 CTest tests passed.
- `xyona-lab`: `git diff --check`
  - Result: passed.

Follow-up:

- Completed by `ad6a7d53 feat(lab): wire materialized assets into project
  lifecycle`.
- Add the realtime LayerPlayer adapter/path that consumes materialized clips
  instead of re-running the HQ graph.

### Workspace Root

Repository: workspace root

Branch: `docs/cdp8-offline-spectral-roadmap`

Commit: pending report commit

Subject: `docs: record materialized asset persistence slice`

Files changed:

- `CDP8_OFFLINE_SPECTRAL_IMPLEMENTATION_REPORT.md`

Technical change:

- Updated the implementation report to record Lab's first file-backed
  materialized audio asset persistence API.
- Clarified that the current slice persists store assets/manifests through
  explicit APIs, while normal project save/open orchestration and realtime
  LayerPlayer playback remain open.

Verification:

- `git diff --check`
  - Result: passed.

Follow-up:

- Backfill this root commit hash in a later report update if exact root-report
  self-reference becomes necessary.

### Workspace Root

Repository: workspace root

Branch: `docs/cdp8-offline-spectral-roadmap`

Commit: `1c77da1`

Subject: `docs: record materialized clip bridge slice`

Files changed:

- `CDP8_OFFLINE_SPECTRAL_IMPLEMENTATION_REPORT.md`

Technical change:

- Updated the implementation report to record the first materialized layer/clip
  bridge slice in `xyona-lab`.
- Clarified that current materialization is in-memory audio plus metadata
  manifest, not yet file-backed ProjectState persistence or realtime
  LayerPlayer playback.
- Updated the next implementation step to focus on file-backed artifact assets
  and RT LayerPlayer consumption.

Verification:

- `git diff --check`
  - Result: passed.

Follow-up:

- Backfill this root commit hash in a later report update if exact root-report
  self-reference becomes necessary.

### Workspace Root

Repository: workspace root

Branch: `docs/cdp8-offline-spectral-roadmap`

Commit: pending report commit

Subject: `docs: record whole-file normalise slice`

Files changed:

- `CDP8_OFFLINE_SPECTRAL_ROADMAP.md`
- `CDP8_OFFLINE_SPECTRAL_IMPLEMENTATION_REPORT.md`
- `xyona-cdp-pack` gitlink

Technical change:

- Updated the cross-repo roadmap to record that the first same-length
  whole-file CDP/HQ slice now exists.
- Recorded the Core, Pack, and Lab implementation commits and verification.
- Updated the workspace gitlink for `xyona-cdp-pack` to the commit that contains
  `cdp.modify.loudness_normalise`.

Verification:

- `git diff --check`
  - Result: passed before commit; only line-ending normalization warnings.

Follow-up:

- Backfill this root commit hash in a later report update if exact root-report
  self-reference becomes necessary.

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

Commit: `6e232d87`

Subject: `feat(lab): add graph diagnostics and offline artifact contract`

Files changed:

- `src/app/lab/audio/builder/GraphPlanDiagnostics.h`
- `src/app/lab/audio/builder/GraphPlanDiagnostics.cpp`
- `src/app/lab/audio/builder/AudioGraphBuilder.h`
- `src/app/lab/audio/builder/AudioGraphBuilder.cpp`
- `src/app/lab/audio/engine/AudioEngineManager.h`
- `src/app/lab/audio/engine/AudioEngineManager.cpp`
- `src/app/lab/audio/engine/OfflineArtifactContract.h`
- `src/app/lab/audio/engine/OfflineArtifactContract.cpp`
- `src/app/lab/audio/engine/OfflineRenderEngine.h`
- `src/app/lab/audio/engine/OfflineRenderEngine.cpp`
- `src/app/lab/debugbar/DebugBar.cpp`
- `src/app/CMakeLists.txt`
- `tests/AudioEngineManagerTests.cpp`
- `tests/OfflineArtifactContractTests.cpp`
- `tests/CMakeLists.txt`

Technical change:

- Added structured graph-plan diagnostics for RT and HQ/offline graph builds.
- Builder diagnostics now record skipped nodes for missing capabilities,
  unsupported process shapes, invalid process metadata, empty live graphs after
  pruning, and bus-dependency cycles.
- `AudioEngineManager` stores the latest RT and offline diagnostics and exposes
  them through `getGraphPlanDiagnostics()`.
- Offline render failures now include the most relevant graph diagnostic instead
  of only a generic "failed to build HQ graph plan" message.
- DebugBar's Audio view now shows graph diagnostics, including formatted
  per-domain diagnostic entries.
- Added a typed offline session/artifact contract for:
  - audio buffers
  - audio files
  - breakpoint/text tables
  - spectral/PVOC analysis artifacts
  - analysis reports
  - file collections
- The contract records output length model, materialization policy, RT re-entry
  policy, producer identity, sample rate, channel count, expected sample count,
  whole-file requirement, length-changing status, and spectral status.
- Current block-based offline renders now declare and validate a block-audio
  session artifact before rendering.
- Contract validation rejects invalid future states such as a length-changing
  artifact claiming `same_as_render_range`, or PVOC/spectral data trying to
  re-enter RT as an audio layer.

Verification:

- `cmake --build --preset windows-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `.\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Offline Artifact Contract" --xyona-only --summary-only`
  - Result: passed; 5 tests, 18 passes, 0 failures.
- `.\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="AudioEngineManager Minimal Plan" --xyona-only --summary-only`
  - Result: passed; 34 tests, 514 passes, 0 failures.
- `.\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Operator Process Metadata" --xyona-only --summary-only`
  - Result: passed; 5 tests, 36 passes, 0 failures.
- `$env:XYONA_OPERATOR_PACK_PATH='D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug'; .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only`
  - Result: passed; 6 tests, 194 passes, 0 failures.
- `ctest --test-dir build\windows-dev -C Debug -R "^xyona_lab_tests$" --output-on-failure`
  - Result: passed; 1/1 CTest tests passed.
- `git diff --check`
  - Result: passed. Git reported only line-ending normalization warnings.

Follow-up:

- Use the offline artifact contract as the input to the first real whole-file
  CDP execution path.
- Add materialized layer/clip persistence once the first length-changing CDP
  render produces an audio artifact.

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

- Completed by `6e232d87 feat(lab): add graph diagnostics and offline artifact
  contract`.

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
- `xyona-lab`: `.\build\windows-dev\tests\Debug\xyona_lab_tests.exe
  --test="Offline Artifact Contract" --xyona-only --summary-only` passed; 5
  tests, 18 passes, 0 failures.
- `xyona-lab`: `.\build\windows-dev\tests\Debug\xyona_lab_tests.exe
  --test="AudioEngineManager Minimal Plan" --xyona-only --summary-only` passed;
  34 tests, 514 passes, 0 failures.
- `xyona-lab`: `ctest --test-dir build\windows-dev -C Debug -R
  "^xyona_lab_tests$" --output-on-failure` passed after graph diagnostics and
  offline artifact contract; 1/1 CTest tests passed.
- `xyona-core`: `cmake --build --preset windows-msvc-debug` passed after adding
  the optional offline pack ABI.
- `xyona-core`: `ctest --test-dir build\windows-msvc-debug -C Debug
  --output-on-failure` passed after fixing the Windows test runtime path and
  pack-test directory; 7/7 CTest tests passed.
- `xyona-cdp-pack`: `ctest --preset windows-msvc-debug --output-on-failure`
  passed after `cdp.modify.loudness_normalise`; 12/12 CTest tests passed.
- `xyona-lab`: `.\build\windows-dev\tests\Debug\xyona_lab_tests.exe
  --test="Offline Pack Processor Client" --xyona-only --summary-only` passed
  with `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug`;
  1 test, 22 passes, 0 failures.
- `xyona-lab`: `.\build\windows-dev\tests\Debug\xyona_lab_tests.exe
  --xyona-only --summary-only` passed with the same pack path; 1155 tests,
  943516 passes, 0 failures.
- `xyona-core`: `./build-dev.sh` passed on macOS before graph-level whole-file
  Lab scheduling.
- `xyona-cdp-pack`: `./build-dev.sh` passed on macOS before graph-level
  whole-file Lab scheduling.
- `xyona-cdp-pack`: `ctest --preset macos-clang-debug --output-on-failure`
  passed on macOS; 12/12 CTest tests passed.
- `xyona-lab`: `./build-dev.sh` passed on macOS after graph-level whole-file
  Lab scheduling.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Operator Process Metadata" --summary-only --xyona-only`
  passed after the offline whole-file scheduler metadata test was added; 6
  tests, 49 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug ctest --test-dir build/macos-dev --output-on-failure -R '^(xyona_lab_tests|operator_packs_tests)$'`
  passed; 2/2 CTest tests passed.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --summary-only --xyona-only`
  passed after the graph-path CDP normalise integration test was added; 35
  tests, 542 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug ctest --test-dir build/macos-dev --output-on-failure -R '^(xyona_lab_tests|operator_packs_tests)$'`
  passed after the graph-path CDP normalise integration test was added; 2/2
  CTest tests passed.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests`
  passed after Canvas/runtime eligibility state was added.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  passed after `cdp.modify.loudness_normalise` Canvas status coverage was
  added; 7 tests, 220 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --summary-only --xyona-only`
  passed after offline-only graph diagnostics were added; 35 tests, 542 passes,
  0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug ctest --test-dir build/macos-dev --output-on-failure -R '^(xyona_lab_tests|operator_packs_tests)$'`
  passed after Canvas/runtime eligibility state was added; 2/2 CTest tests
  passed.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests`
  passed after adding the materialized audio store and bridge API.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  passed after materialized layer/clip store coverage was added; 2 tests, 23
  passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  passed after the materialized bridge slice; 7 tests, 220 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --summary-only --xyona-only`
  passed after the normalise render was also materialized as a clip; 35 tests,
  555 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug ctest --test-dir build/macos-dev --output-on-failure -R '^(xyona_lab_tests|operator_packs_tests)$'`
  passed after the materialized bridge slice; 2/2 CTest tests passed.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests`
  passed after adding file-backed materialized audio asset persistence.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  passed after WAV asset persistence and ProjectState manifest coverage was
  added; 2 tests, 39 passes, 0 failures.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="ProjectState Round-Trip" --summary-only --xyona-only`
  passed after the materialized audio manifest subtree was added; 8 tests, 138
  passes, 0 failures.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="ProjectState Schema Validation" --summary-only --xyona-only`
  passed after the materialized audio manifest subtree was added; 4 tests, 8
  passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --summary-only --xyona-only`
  passed after the materialized asset persistence slice; 35 tests, 555 passes,
  0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug ctest --test-dir build/macos-dev --output-on-failure -R '^(xyona_lab_tests|operator_packs_tests)$'`
  passed after the materialized asset persistence slice; 2/2 CTest tests
  passed.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  passed after wiring materialized assets into Project save/open/save-as.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  passed after the project lifecycle wiring; 3 tests, 59 passes, 0 failures.

## Open Risks

- `MaterializedAudioStore` now participates in normal Project save/open/save-as,
  but cleanup/orphan policy and dependency-staleness state are not implemented
  yet.
- Materialized layers/clips do not yet carry dependency signatures, so stale
  source audio, parameter, render-range, sample-rate, algorithm-version, or
  spectral-setting changes are not yet surfaced as `Re-render required`.
- Materialized clips are not yet consumed by the realtime LayerPlayer path, so
  the bridge proves storage, metadata, and file-backed reload but not RT
  playback.
- Same-length whole-file CDP operators now have a first execution and
  materialization path through the prototype whole-buffer offline ABI. Before
  release, that reference slice should move onto the Offline Session ABI or the
  prototype path should become an internal-only helper. Length-changing,
  PVOC/spectral, multi-output, and long-running CDP operators must use the
  implemented/tested Offline Session ABI.
- Typed spectral/PVOC artifacts remain data-only until typed artifact ports and
  host semantics exist; they must not be routed through audio buffers. PVOC also
  has an explicit hard dependency on the Offline Session ABI and CDP8 golden
  fixtures.
