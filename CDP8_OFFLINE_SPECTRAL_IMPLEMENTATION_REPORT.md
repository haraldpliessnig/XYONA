# CDP8 Offline And Spectral Implementation Report

Last updated: 2026-04-29

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
Project save/open/save-as orchestration and store-level staleness state.
The AudioEngineManager materialize path now also feeds store signatures with
current render-dependency fingerprints.
Project save now also cleans orphaned materialized audio assets and stale,
missing, or failed layers are not silently promoted back to valid RT-playable
audio during project asset reload.
Materialized WAV asset files now also carry content fingerprints so external
asset edits reload as `Stale` / `Re-render required` instead of valid resident
audio.
Lab now also persists `file` / `path` / `string` operator parameters through
Canvas project state, and `lab.audio_file_in` source WAV files feed content
fingerprints into materialized render-dependency signatures.
Lab now also exposes materialized clips that are `Rendering`, `Stale`,
`Missing`, `Failed`, or otherwise not RT-playable through a BottomBar status
surface backed by a separate `MaterializedAudioStatusSummary` model.
Realtime graphs can now consume valid resident materialized clips through the
registered `lab.layer_player` operator and `LayerPlayerHostAdapter`. Missing,
stale, or nonresident clips resolve to deterministic silence with a
`MaterializedClipUnavailable` graph diagnostic instead of performing disk or
pack work in the audio callback.
Gate G now has a synthetic length-changing audio reference slice:
`cdp.utility.length_change` runs through the production Offline Session ABI,
Lab accepts it as an offline whole-file node, and bus captures/materialized
clips retain the negotiated output length instead of being truncated to the
original render range. A realtime `lab.layer_player` graph consumes the
materialized result and reaches the synthetic tail samples. Gate G now also
includes the first real CDP8 length-changing operator:
`cdp.edit.cut` implements CDP8 `sfedit cut` mode 1 with param-dependent output
length and analytical golden coverage in the CDP pack, plus a Lab Offline
Session materialization smoke for the `ParamDependent` artifact contract. The
roadmap now closes the hard Gate H infrastructure contract before any further
production CDP8 operator families are ported. The first post-Gate-H production
slice is now also implemented: `cdp.edit.cutend` maps CDP8 `sfedit cutend`
mode 1 onto the same Offline Session path, keeps the requested end segment,
uses the CDP start-splice rule, and is covered by Pack conformance/metadata
tests plus Lab materialization and Canvas smoke tests.
Gate I has now moved past metadata preflight into the data-only artifact,
typed-data-input, and first real spectral analysis -> synthesis path: Core
Offline Session ABI v2 exposes data descriptor/read callbacks, ABI v3 adds
typed input delivery, the CDP pack provides the technical
`cdp.utility.pvoc_probe` fixture, Lab persists typed data assets, the CDP pack
has a PVOC golden harness, `cdp.pvoc.anal` implements a CDP8 `PVOC_ANAL`-style
magnitude/frequency analysis operator, and public `cdp.pvoc.synth` consumes the
same typed payload through the production Offline Session ABI. Lab can discover
both operators, reject them from RT/block-audio paths, materialize PVOC JSON as
a typed artifact, and feed that payload back into the pack to materialize
synthesized audio. The synth path now also has the first file-backed CDP8
`pvoc` reference coverage: 1024-frame impulse and 2048-frame 440 Hz sine cases
validate selected analysis bins, synthesized sample snapshots, and CDP8-style
synthesis length behavior. Lab now also has the first graph-native typed data edge:
the offline/HQ graph planner records `cdp.pvoc.anal -> cdp.pvoc.synth` as a
typed PVOC edge, keeps that edge out of audio wiring/PDC, and OfflineRenderEngine
materializes the analysis payload before invoking the synth and routing its
audio to `lab.mainbus_out`. Gate I now also has the first spectral-to-spectral
host-shape proof: `cdp.utility.pvoc_identity` is a technical typed PVOC
data-in/data-out transform, and Lab schedules
`cdp.pvoc.anal -> cdp.utility.pvoc_identity -> cdp.pvoc.synth -> lab.mainbus_out`
as a two-edge typed spectral chain. Gate I is still not fully closed: broader
CDP8-generated PVOC fixture matrices, generalized typed graph scheduling, and
persisted artifact-handle semantics remain open.
Gate J is now implemented locally as a technical host-shape fixture:
`cdp.utility.generator_probe` is a synthetic no-input pack generator with
`processShape="generator"` and direct block ABI metadata, and Lab proves that
Canvas discovery plus offline `generator -> MainBusOut` rendering work without
upstream audio.
Post-audit hygiene is now also handled locally: the workspace root has a
`.gitmodules` entry for the `xyona-cdp-pack` Gitlink, the Offline Session ABI
header documents per-call audio/data pointer lifetimes and single-handle
threading, Lab FNV-1a seeds use the canonical 64-bit offset basis, and the
existing `cdp.edit.cut` zero-length reject is covered by a regression test.

Latest implementation commits:

- `xyona-core`: `d4d437b feat(core): add offline pack ABI contract`
- `xyona-cdp-pack`: `57105fa feat(cdp-pack): add whole-file loudness normalise`
- `xyona-lab`: `16e662dc feat(lab): persist materialized audio assets`
- `xyona-lab`: `ad6a7d53 feat(lab): wire materialized assets into project lifecycle`
- `xyona-lab`: `6b71007b feat(lab): track materialized asset staleness`
- `xyona-lab`: `5adbcb97 feat(lab): fingerprint materialized render dependencies`
- `xyona-lab`: `f87b14aa feat(lab): clean orphaned materialized audio assets`
- `xyona-lab`: `1d24ef1a feat(lab): fingerprint materialized audio asset files`
- `xyona-lab`: `a9271660 feat(lab): fingerprint audio file source dependencies`
- `xyona-lab`: `48a79a0a feat(lab): surface materialized audio status`
- `xyona-lab`: `b4149bf0 feat(lab): add materialized layer player adapter`
- `xyona-lab`: `fbfa6e35 feat(lab): route materialized clips into realtime graph`
- `xyona-core`: `ed0982a5 feat(core): add offline session abi`
- `xyona-cdp-pack`: `5c39e098 feat(cdp-pack): implement offline session normalise`
- `xyona-lab`: `50abd15f feat(lab): render whole-file packs through sessions`
- `xyona-core`: `d9e2024d ci(core): add windows and macos baseline`
- `xyona-cdp-pack`: `31a6a176 ci(cdp-pack): add windows and macos baseline`
- `xyona-lab`: `75c116a4 ci(lab): add cdp smoke baseline`
- `xyona-cdp-pack`: `50563ad4 ci(cdp-pack): require token for private core checkout`
- `xyona-lab`: `5a65fbca ci(lab): require token for private sibling checkouts`
- `xyona-core`: `6cbd68b fix(core): create generated include dirs during configure`
- `xyona-lab`: `06865527 fix(lab): avoid atomic_ref in control output mirror`
- `xyona-lab`: `d30d3498 ci(lab): enable parallel msvc compilation`
- `xyona-lab`: `9cee3505 ci(lab): use ninja for windows baseline`
- `xyona-lab`: `fae01fec ci(lab): accept current vcpkg eigen package`
- `xyona-lab`: `2eec1b8f ci(lab): add minimal windows cdp smoke`
- `xyona-cdp-pack`: `49520b6 feat(cdp-pack): add length-changing offline reference`
- `xyona-lab`: `1e275d18 feat(lab): support length-changing offline audio`
- `xyona-cdp-pack`: `a982283 feat(cdp-pack): add edit cut offline session`
- `xyona-lab`: `3fd86fa4 test(lab): cover cdp edit cut offline session`
- `xyona-lab`: `af776c1e ci(lab): smoke test cdp edit cut`
- `xyona-cdp-pack`: `49c42cc test(cdp-pack): add gate h conformance coverage`
- `xyona-lab`: `0df30e03 test(lab): cover gate h artifact contracts`
- `xyona-cdp-pack`: `f6f5a1d feat(cdp-pack): add edit cutend offline session`
- `xyona-lab`: `d45fc1d1 test(lab): cover cdp edit cutend offline session`
- `xyona-cdp-pack`: `d613571 feat(cdp-pack): add spectral artifact contract`
- `xyona-lab`: `a8b02b97 feat(lab): parse spectral operator metadata`
- `xyona-core`: `a9ddb60 feat(core): add offline session data reads`
- `xyona-cdp-pack`: `8214aa4 feat(cdp-pack): add pvoc data artifact session`
- `xyona-lab`: `3fa12897 feat(lab): materialize offline data artifacts`
- `xyona-lab`: `8b6f8f22 feat(lab): persist materialized data artifacts`
- `xyona-cdp-pack`: `8d84014 test(cdp-pack): add pvoc golden harness`
- `xyona-cdp-pack`: `7db5698 feat(cdp-pack): add pvoc analysis operator`
- `xyona-lab`: `db8183d6 test(lab): cover cdp pvoc analysis artifacts`
- `xyona-core`: `4ec3915 feat(core): add offline session data input ABI`
- `xyona-cdp-pack`: `167542c feat(cdp-pack): add pvoc synth data input session`
- `xyona-lab`: `9e79e486 feat(lab): render offline audio from data artifacts`
- workspace root: this report update records the latest Lab render-dependency
  signature, orphan-cleanup, materialized asset file-fingerprint, and
  `lab.audio_file_in` source-fingerprint/status-surface and Gate D LayerPlayer
  slices.
- workspace root: this report/roadmap update records the Gate E Offline Session
  ABI close-out and advances the `xyona-cdp-pack` Gitlink to the Gate E pack
  commit.
- workspace root: this report/roadmap update records the Gate F CI close-out.
- workspace root: this report/roadmap update records the Gate H close-out and
  advances the `xyona-cdp-pack` Gitlink to the Gate H pack commit.
- workspace root: this report/roadmap update records the post-Gate-H
  `cdp.edit.cutend` slice and advances the `xyona-cdp-pack` Gitlink.
- workspace root: this report/roadmap update records the Gate I spectral
  metadata preflight and advances the `xyona-cdp-pack` Gitlink.
- workspace root: this report/roadmap update records the first Gate I data-only
  Offline Session artifact materialization path and advances the
  `xyona-cdp-pack` Gitlink.
- workspace root: this report/roadmap update records the Gate I typed data
  artifact persistence and PVOC golden harness slices and advances the
  `xyona-cdp-pack` Gitlink.
- workspace root: this report/roadmap update records the first real Gate I
  PVOC analysis producer and advances the `xyona-cdp-pack` Gitlink.
- workspace root: this report/roadmap update records the Gate I Offline Session
  typed-data-input ABI, public PVOC synthesis path, Lab data-artifact-to-audio
  render path, and advances the `xyona-cdp-pack` Gitlink.
- local working tree: Gate J adds the `cdp.utility.generator_probe` synthetic
  pack fixture and Lab null-upstream generator graph/render coverage.
- local working tree: Gate I adds the first graph-native PVOC typed-data edge,
  `cdp.pvoc.anal -> cdp.pvoc.synth -> lab.mainbus_out`, with Pack descriptor
  updates and Lab OfflineRenderEngine materialization coverage.
- local working tree: Gate I adds the technical spectral-to-spectral
  `cdp.utility.pvoc_identity` fixture and Lab scheduling for
  `cdp.pvoc.anal -> cdp.utility.pvoc_identity -> cdp.pvoc.synth`.
- local working tree: review hygiene closes the `.gitmodules` gap for the
  `xyona-cdp-pack` Gitlink, documents Offline Session pointer lifetime and
  handle-threading rules, corrects Lab FNV-1a offset-basis seeds, and adds
  `cdp.edit.cut` zero-length regression coverage.

Current proven capability:

- `cdp.modify.loudness_normalise` is the reference same-length whole-file
  operator.
- The pack advertises the operator as HQ-only and rejects block processing for
  it.
- Lab can call the pack's production Offline Session ABI directly, stream input
  blocks, materialize output audio blocks, validate the `OfflineSessionContract`,
  and mark the artifact as RT re-entry-capable.
- Lab can now also schedule same-length whole-file pack nodes inside the
  offline/HQ graph for the first supported graph shape:
  source/block region -> one whole-file node -> direct terminal audio targets.
- Lab can now also schedule the synthetic `cdp.utility.length_change`
  reference operator as a length-changing whole-file node, materialize the
  negotiated longer output, and keep fixed-tail artifact metadata on the
  resulting materialized clip.
- Lab now proves the synthetic length-changing materialized clip can re-enter a
  realtime `lab.layer_player` graph and expose its tail samples without hidden
  truncation or nonzero padding.
- The CDP pack now has the first real CDP8 length-changing operator slice:
  `cdp.edit.cut` maps CDP8 `sfedit cut` mode 1 onto the production Offline
  Session ABI, publishes `param_dependent` output length, and validates CDP-style
  time rounding, reversed-time swapping, and linear splice windows with an
  analytical golden buffer.
- Lab's Offline Pack Processor Client now proves `cdp.edit.cut` materializes
  the `end - start` output length through the production Offline Session ABI and
  records a `ParamDependent` RT-reentry-capable audio artifact.
- The CDP pack now also has `cdp.edit.cutend`, a second real CDP8
  length-changing `sfedit` slice. It maps CDP8 `sfedit cutend` mode 1 to the
  production Offline Session ABI, publishes `param_dependent` output length,
  keeps the requested final segment, applies the start splice only, and rejects
  invalid keep/splice windows according to CDP8 consistency rules.
- Lab's Offline Pack Processor Client and CDP Pack Canvas smoke tests now prove
  `cdp.edit.cutend` materializes the negotiated end-segment output length,
  preserves the `ParamDependent` artifact contract, is Canvas-discoverable as
  an offline whole-file length-changing node, and remains outside RT/HQ block
  processing.
- The CDP pack now has a concrete `CdpSpectralArtifactContract` for future
  PVOC/spectral analysis artifacts. The contract records sample rate, channel
  count, window size, hop size, FFT size, real-FFT bin count, frame-count model,
  bin encoding, and Offline Session artifact kind without representing PVOC as
  audio.
- Lab's operator process metadata parser now reads `engine.spectral` metadata,
  validates PVOC format/bin layout/window-hop-FFT shape, and fails closed if a
  descriptor advertises spectral data as direct audio output.
- Core Offline Session ABI v2 now extends the production session API with
  `get_output_data_desc` and `read_output_data` while preserving the v1 prefix
  for existing audio-session clients.
- The CDP pack now has `cdp.utility.pvoc_probe`, a technical data-only fixture
  that emits a deterministic file-backed `pvoc_analysis` JSON artifact over the
  production Offline Session path.
- Lab's Offline Pack Processor Client now materializes data-only artifacts via
  `renderWholeFileDataArtifacts`, preserving artifact contract metadata,
  media type, schema, extension, descriptor metadata, and raw bytes separately
  from audio.
- Lab now stores materialized data artifacts in `MaterializedDataArtifactStore`,
  persists resident bytes under `ProjectName.xyona-assets/materialized_data`,
  keeps a `ProjectState` manifest anchor, restores resident bytes on project
  open, removes orphaned data files on save, and marks stale/missing/failed
  data assets as nonvalid instead of treating them as audio or RT-playable
  material.
- The CDP pack now has `CdpPvocGoldenFixtureSpec` and
  `comparePvocGoldenData()` for CDP8-reference-generated PVOC/PVX fixture
  contracts, spectral shape validation, and in-memory magnitude/frequency or
  magnitude/phase comparisons with mismatch location reporting.
- The CDP pack now has the first real Gate I PVOC producer:
  `cdp.pvoc.anal` implements a CDP8 `PVOC_ANAL`-style mono
  magnitude/frequency analysis path with 1024-point FFT/window, 128-sample hop,
  513 real bins, explicit JSON serialization, file-backed/data-only artifact
  output, and no audio output.
- The PVOC runtime now deserializes that JSON and public `cdp.pvoc.synth`
  consumes the same typed analysis payload through Offline Session ABI v3 to
  render analysis-dependent mono audio.
- Lab's Offline Pack Processor Client and CDP Pack Canvas smoke tests now prove
  `cdp.pvoc.anal` and `cdp.pvoc.synth` are discoverable as spectral/typed-data
  descriptors, stay out of RT/block-audio execution, materialize real PVOC
  analysis bytes, and render that payload back to materialized audio.
- Lab's offline graph path now proves the first real graph-native typed data
  chain:
  `cdp.utility.generator_probe -> cdp.pvoc.anal -> cdp.pvoc.synth -> lab.mainbus_out`.
  The planner records one `offlineTypedDataEdges` entry for `pvoc -> pvoc`,
  emits only audio wires for the audio legs, and OfflineRenderEngine
  materializes the PVOC payload before rendering the synth audio to the main
  bus.
- Lab has a headless integration test that proves the real graph path:
  `lab.grid_source -> cdp.utility.db_gain -> cdp.modify.loudness_normalise -> lab.mainbus_out`.
- Lab has a headless integration test that proves the synthetic Gate G graph
  path:
  `lab.grid_source -> cdp.utility.length_change -> lab.mainbus_out`.
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
  leave playable stale layers in the active store.
- `MaterializedAudioStore` now persists per-layer dependency signatures plus
  `Valid`, `Rendering`, `Stale`, `Missing`, and `Failed` state. A dependency
  signature mismatch marks the layer `Stale`, records a `Re-render required`
  diagnostic, and clears resident audio so the layer cannot be consumed as
  RT-playable material.
- Missing assets now leave diagnostic metadata in the active store as `Missing`
  instead of being silently discarded; `isRealtimePlayable()` remains false for
  stale, missing, failed, or nonresident material.
- The AudioEngineManager materialize path now extends materialized dependency
  signatures with a current render fingerprint covering the RenderJob, render
  range, sample rate, graph plan, wires, whole-file node identity, operator
  descriptor versions, operator parameters, parameter sources, tempo points, and
  timeline grid context.
- A headless integration test now proves that changing an upstream operator
  parameter changes the materialized signature and that the older layer can be
  marked `Stale` / `Re-render required` / not RT-playable.
- Project save now treats `*.xyona-assets/materialized_audio` as the
  MaterializedAudioStore-owned directory: files not referenced by valid
  manifest layers are deleted, empty materialized-audio directories are removed
  when the store has no layers, and stale/missing/failed layers are not
  rehydrated as `Valid` from old WAV files.
- Materialized WAV asset files now persist a content fingerprint
  (size/mtime/FNV-64). If an external edit changes the stored asset, project
  reload marks the layer `Stale`, records `Re-render required`, and leaves it
  nonresident/non-RT-playable.
- `lab.audio_file_in` source file paths now persist as string parameters instead
  of being coerced through numeric parameter state, and source WAV content
  fingerprints now participate in materialized render-dependency signatures.
  Changing the source file changes the signature and makes older materialized
  layers fail the current-signature check as `Stale` / `Re-render required`.
- `MaterializedAudioStatusSummary` now turns store state into user-facing clip
  counts and diagnostics, and the BottomBar displays that summary whenever
  materialized clips need attention. This is intentionally a small replaceable
  status surface, not the final clip/render-queue UI.
- `LayerPlayerHostAdapter` can play a prepared immutable materialized audio
  source in the realtime graph, including clip offset, length, gain, cursor
  advance, bypass behavior, and mono fanout without allocating in the callback.
- `lab.layer_player` is a registered realtime custom operator. GraphBuilder
  resolves its `clip_id` against `MaterializedAudioStore` during graph build and
  prepares a playback source from valid resident layers before RT processing.
- Missing, stale, failed, or nonresident materialized clips stay deterministic:
  the realtime plan remains buildable, outputs silence, and records a
  `MaterializedClipUnavailable` diagnostic.
- A headless integration test now proves the Gate D path:
  offline `lab.grid_source` render -> materialized clip -> realtime
  `lab.layer_player` -> `lab.audio_out` playback.
- Gate F CI is green on GitHub Actions for Core, Pack, and Lab on Windows MSVC
  Debug and macOS Clang Debug. Lab's Windows leg uses the focused
  `xyona_lab_cdp_offline_smoke` executable for dynamic CDP pack discovery and
  Offline Session ABI coverage; macOS still builds `xyona_lab_tests` and runs
  the Gate E CDP smoke subset.
- Gate H is closed for the current shared infrastructure contract:
  - the CDP pack validates all current CDP descriptors for shape/capability
    consistency, CDP provenance, validation strategy, parameter metadata, and
    port metadata;
  - generic Offline Session conformance now covers create/feed/finish/output
    discovery/block reads/cancel/progress/error paths across the same-length,
    fixed-tail length-changing, and param-dependent length-changing
    representative operators;
  - the golden fixture harness now has an explicit metadata contract separating
    analytical goldens from CDP8-reference-generated goldens;
  - Lab tests now cover data-only artifacts, multi-artifact sessions,
    file-collection data artifacts, typed-data/multi-output descriptor shapes,
    and current unsupported mixed-shape graph planning diagnostics.
- The plan is now gated: the current whole-buffer offline ABI, currently named
  `offline_whole_buffer_prototype`, is a prototype/reference bridge. Length-changing,
  PVOC/spectral, multi-output, and production-scale long-file CDP work require
  the implemented and tested Offline Session ABI.
- The prototype whole-buffer ABI no longer uses release-like `v1` names in the
  live code path. Core installs `xyona/api/offline_whole_buffer_prototype.h`,
  the CDP pack exports `xyona_pack_get_offline_whole_buffer_prototype_api`, and
  Lab resolves that symbol explicitly.

Gate D handoff state for Gate E work:

- `xyona-lab` must include:
  - `b4149bf0 feat(lab): add materialized layer player adapter`
  - `fbfa6e35 feat(lab): route materialized clips into realtime graph`
  - `439ce5f2 docs(lab): mark layer player bridge implemented`
- Workspace root must include:
  - `40daf13 docs: close gate d layer player bridge`
- Gate D is closed for valid resident materialized audio clips. The remaining
  materialized-audio work is future artifact/source coverage and product UX,
  not a blocker for Gate E.
- Handoff revalidation on 2026-04-28:
  - `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
    passed; target was already up to date.
  - `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager" --summary-only --xyona-only`
    passed; 40 tests, 586 passes, 0 failures. The CDP whole-file subtest was
    skipped because `XYONA_OPERATOR_PACK_PATH` was unset.
  - `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="LayerPlayerHostAdapter" --summary-only --xyona-only`
    passed; 4 tests, 37 passes, 0 failures.
  - `xyona-lab`: `XYONA_RT_ALLOC_TRAP=2 build/macos-dev/tests/xyona_lab_tests --test="RT Safety Smoke" --summary-only --xyona-only`
    passed; 2 tests, 4 passes, 0 failures.
  - `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
    passed; 6 tests, 145 passes, 0 failures.

Resume commands on a fresh machine:

```powershell
git fetch --all --prune
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

Gate G close-out state:

- Gate G is closed on 2026-04-28.
- Pack CI coverage runs full `ctest`, including `cdp_edit_cut_tests`, so the
  real `sfedit cut` length-changing slice is in the Pack baseline.
- Lab macOS CI coverage runs the full `Offline Pack Processor Client` smoke,
  including `cdp.utility.length_change` and `cdp.edit.cut`.
- Lab Windows/minimal CI coverage now runs
  `xyona_lab_cdp_offline_smoke`, which covers:
  - `cdp.modify.loudness_normalise`
  - `cdp.utility.length_change`
  - `cdp.edit.cut`
- Remote close-out CI on 2026-04-28:
  - `xyona-cdp-pack`: GitHub Actions run `25071434999` passed for
    `a982283c0506697119cf4107a5a7656d6022e081`, with `macOS Clang Debug` and
    `Windows MSVC Debug` jobs both successful.
  - `xyona-lab`: GitHub Actions run `25071981136` passed for
    `af776c1e8afe8b77795574c234b3a038153a98fe`, with `macOS Clang Debug` and
    `Windows MSVC Debug` jobs both successful.
- Local close-out verification on 2026-04-28:
  - `xyona-cdp-pack`: `ctest --preset macos-clang-debug --output-on-failure`
    passed; 14/14 tests.
  - `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --xyona-test "Offline Pack Processor Client" --summary-only`
    passed; 5 tests, 64 passes, 0 failures.
  - `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_cdp_offline_smoke`
    passed.

Next implementation steps, in order:

1. Expand the existing CDP8 PVOC fixture assets beyond the current impulse/sine
   analysis -> synthesis identity cases into a broader length, sample-rate, and
   spectral-behavior matrix, then use them to harden the graph-native
   `cdp.pvoc.anal -> cdp.pvoc.synth` path.
2. Generalize the typed graph path beyond the current direct and one-intermediate
   PVOC slices: arbitrary multiple typed edges/chains, persisted artifact
   handles, and clearer graph diagnostics.
3. Decide whether Gate I closes after the fixture matrix and typed-handle work,
   or whether one real CDP8 spectral-to-spectral algorithm should be pulled
   forward in addition to the technical host-shape fixture.
4. Keep further non-spectral CDP8 families optional. If selected, likely next
   candidates are `extend`/`iterate` or a non-spectral waveset-style
   length-changing family, depending on fixture cost.

Additional production operators are not required to prove the current shared
infrastructure. If a missing host shape cannot be tested through the current
representative operators, add a test-only fixture operator or conformance stub
rather than starting another CDP8 production port prematurely.

Hard gate summary:

- The current whole-buffer offline ABI remains usable only as an internal
  prototype/reference path for existing same-length reference tests. It is not a
  release production path for length-changing, PVOC/spectral, multi-output, or
  long-running CDP operators.
- Current materialized-audio persistence/staleness is complete for Gate C:
  stale/missing assets produce visible status, and future materialized artifact
  dependencies are added as those artifact types appear.
- Realtime consumption of valid resident materialized audio clips is complete
  for Gate D through `lab.layer_player`; missing/stale/nonresident clips are
  diagnosable silence, not hidden RT work.
- Gate H is closed for the current non-spectral infrastructure contract:
  descriptor validation, Offline Session conformance, golden fixture metadata,
  materialized artifact contracts, Lab offline-graph planning rules, and
  baseline Pack/Lab CI coverage are in place.
- PVOC/spectral remains Gate I work, but the first real analysis producer,
  Offline Session typed data input, public synth operator, Lab
  data-artifact-to-audio path, first CDP8-backed PVOC synthesis-length
  fixtures, a graph-native one-chain `cdp.pvoc.anal -> cdp.pvoc.synth`
  render, and a technical spectral-to-spectral
  `cdp.pvoc.anal -> cdp.utility.pvoc_identity -> cdp.pvoc.synth` render are
  now in place. The remaining hard work is broader CDP8-generated PVOC fixture
  matrix coverage plus generalized typed graph/persisted-handle support for
  arbitrary multiple chains.
- Gate J is locally covered by a synthetic no-input pack generator fixture and
  Lab graph/render tests before any real CDP8 generator program is ported.
- The review hygiene items that were concrete local blockers are now covered:
  `.gitmodules` exists for the Pack Gitlink, ABI lifetime/threading comments are
  in the Core header, FNV-1a seed literals are canonicalized in Lab hash users,
  and `cdp.edit.cut` rejects zero-length cuts with a dedicated Pack test.

## Post-Audit Hygiene Close-Out

Date: 2026-04-29

Status: implemented locally; commit pending.

Files changed:

- `.gitmodules`
- `xyona-core/include/xyona/api/offline_session.h`
- `xyona-cdp-pack/tests/test_cdp_edit_cut.cpp`
- `xyona-lab/src/app/lab/audio/engine/AudioEngineManager.cpp`
- `xyona-lab/src/app/lab/audio/engine/MaterializedAudioStore.cpp`
- `xyona-lab/src/app/lab/audio/engine/MaterializedDataArtifactStore.cpp`
- `xyona-lab/src/app/lab/signal/runtime/PreparedSignalRuntime.cpp`
- `xyona-lab/src/app/lab/timeline/grid/runtime/PreparedGridRuntime.cpp`
- workspace root roadmap/report updates.

Technical change:

- Added the missing root `.gitmodules` entry for the existing `xyona-cdp-pack`
  Gitlink using the pack repository remote.
- Documented Offline Session handle threading as one thread per session handle,
  while separate independent handles may be driven in parallel.
- Documented that audio channel arrays, mutable output channel arrays, and typed
  data input byte spans are host-owned and valid only for the receiving ABI call.
- Corrected Lab FNV-1a seed literals from the truncated value to the canonical
  64-bit offset basis `14695981039346656037ull` in materialized asset/source
  fingerprints and local runtime revision hashes.
- Added a `cdp.edit.cut` regression test proving that `start_seconds == end_seconds`
  is rejected at session creation as `INVALID_PARAM`.

Verification:

- `xyona-core`: `cmake --build --preset windows-msvc-debug --target test_offline_session_abi --config Debug`
  passed.
- `xyona-core`: `ctest --preset windows-msvc-debug -R offline_session_abi_tests --output-on-failure`
  passed; 1/1 test.
- `xyona-cdp-pack`: `cmake --build --preset windows-msvc-debug --target test_cdp_edit_cut --config Debug`
  passed.
- `xyona-cdp-pack`: `ctest --preset windows-msvc-debug -R cdp_edit_cut_tests --output-on-failure`
  passed; 1/1 test.
- `xyona-lab`: `cmake --build --preset windows-dev --target xyona_lab_tests --config Debug`
  passed with existing warnings.
- `xyona-lab`: `xyona_lab_tests.exe --test="Materialized Audio Store" --xyona-only --summary-only`
  passed; 6 tests, 145 passes, 0 failures.
- `xyona-lab`: `xyona_lab_tests.exe --test="Materialized Data Artifact Store" --xyona-only --summary-only`
  passed; 3 tests, 69 passes, 0 failures.
- `xyona-lab`: `xyona_lab_tests.exe --test="PreparedSignalRuntime" --xyona-only --summary-only`
  passed; 2 tests, 42 passes, 0 failures.
- `xyona-lab`: `xyona_lab_tests.exe --test="PreparedGridRuntime" --xyona-only --summary-only`
  passed; 21 tests, 226 passes, 0 failures.
- `xyona-lab`: with
  `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug`,
  `xyona_lab_tests.exe --test="AudioEngineManager" --xyona-only --summary-only`
  passed; 45 tests, 2659 passes, 0 failures.

Follow-up:

- Commit the local Gate I/Gate J/review-hygiene working tree as a coherent
  checkpoint once the branch boundary is chosen.

## Gate I Slice - PVOC Spectral-To-Spectral Identity Chain

Date: 2026-04-29

Status: implemented locally; commit pending.

Files changed:

- `xyona-cdp-pack/CMakeLists.txt`
- `xyona-cdp-pack/specs/cdp8_inventory.yaml`
- `xyona-cdp-pack/src/offline_api.cpp`
- `xyona-cdp-pack/src/pack_registration.cpp`
- `xyona-cdp-pack/src/operators/cdp_utility_pvoc_identity.h`
- `xyona-cdp-pack/src/operators/cdp_utility_pvoc_identity.cpp`
- `xyona-cdp-pack/src/support/pack_descriptors.h`
- `xyona-cdp-pack/tests/test_cdp_descriptor_metadata.cpp`
- `xyona-cdp-pack/tests/test_cdp_offline_session_conformance.cpp`
- `xyona-cdp-pack/tests/test_cdp_spectral_contract.cpp`
- `xyona-lab/src/app/lab/adapters/OperatorProcessMetadata.cpp`
- `xyona-lab/src/app/lab/audio/adapter/AudioIOHostAdapters.h`
- `xyona-lab/src/app/lab/audio/adapter/AudioIOHostAdapters.cpp`
- `xyona-lab/src/app/lab/audio/engine/OfflinePackProcessorClient.h`
- `xyona-lab/src/app/lab/audio/engine/OfflinePackProcessorClient.cpp`
- `xyona-lab/src/app/lab/audio/engine/OfflineRenderEngine.cpp`
- `xyona-lab/tests/OperatorProcessMetadataTests.cpp`
- `xyona-lab/tests/OfflinePackProcessorClientTests.cpp`
- `xyona-lab/tests/CdpPackCanvasSmokeTests.cpp`
- `xyona-lab/tests/AudioEngineManagerTests.cpp`
- `xyona-lab/tests/OfflinePackProcessorClientSmoke.cpp`
- workspace root roadmap/report updates.

Technical change:

- Added `cdp.utility.pvoc_identity`, a technical PVOC typed-data input/output
  operator. It consumes one `pvoc_analysis` payload through Offline Session ABI
  v3, validates/deserializes it, reserializes the same analysis content as a
  new typed PVOC output payload, and marks the output as file-backed data-only
  spectral material.
- This operator is explicitly not a CDP8 algorithm port. It is the Gate I
  host-shape proof for spectral-to-spectral scheduling before broader spectral
  families are selected.
- Lab now accepts typed-data transforms that output typed spectral data, not
  only data-to-audio transforms.
- `OfflinePackProcessorClient` now has a data-input/data-output path, and
  `OfflineDataTransformPackHostAdapter` can materialize either data or final
  audio from a typed source artifact.
- `OfflineRenderEngine` now supports the first two-edge typed spectral chain:
  one data producer, one typed spectral data transform, and one final
  data-to-audio transform routed to direct terminal targets.
- The graph smoke now proves
  `cdp.utility.generator_probe -> cdp.pvoc.anal -> cdp.utility.pvoc_identity -> cdp.pvoc.synth -> lab.mainbus_out`.

Verification:

- `xyona-cdp-pack`: targeted build for `xyona_pack_cdp_ops`,
  `test_cdp_descriptor_metadata`, `test_cdp_spectral_contract`, and
  `test_cdp_offline_session_conformance` passed.
- `xyona-cdp-pack`: targeted CTest for descriptor metadata, spectral contract,
  and Offline Session conformance passed; 3/3 tests.
- `xyona-cdp-pack`: full `cmake --build --preset windows-msvc-debug --config Debug`
  passed.
- `xyona-cdp-pack`: full `ctest --preset windows-msvc-debug --output-on-failure`
  passed; 19/19 tests.
- `xyona-lab`: `cmake --build --preset windows-dev --target xyona_lab_tests --config Debug`
  passed with existing warnings.
- `xyona-lab`: with
  `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug`,
  `xyona_lab_tests.exe --test="Operator Process Metadata" --xyona-only --summary-only`
  passed; 12 tests, 112 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `xyona_lab_tests.exe --test="Offline Pack Processor Client" --xyona-only --summary-only`
  passed; 10 tests, 1054 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only`
  passed; 14 tests, 376 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `xyona_lab_tests.exe --test="AudioEngineManager" --xyona-only --summary-only`
  passed; 45 tests, 2659 passes, 0 failures.

Follow-up:

- Decide whether the technical spectral-to-spectral proof is sufficient for
  Gate I infrastructure closure, or whether one real CDP8 spectral transform
  should be pulled forward.
- Expand PVOC fixture coverage beyond the first impulse/sine cases.
- Generalize typed graph scheduling beyond the current one-intermediate typed
  chain and add persisted typed artifact-handle semantics.

## Gate I Slice - CDP8 PVOC Fixture-Backed Synthesis Length

Date: 2026-04-29

Status: implemented locally; commit pending.

Files changed:

- `xyona-cdp-pack/CMakeLists.txt`
- `xyona-cdp-pack/specs/cdp8_inventory.yaml`
- `xyona-cdp-pack/src/operators/cdp_pvoc_synth.cpp`
- `xyona-cdp-pack/src/runtime/cdp_pvoc_analysis.h`
- `xyona-cdp-pack/src/runtime/cdp_pvoc_analysis.cpp`
- `xyona-cdp-pack/tests/golden/README.md`
- `xyona-cdp-pack/tests/golden/cdp.pvoc.anal/impulse-1024-mono-48000/manifest.yaml`
- `xyona-cdp-pack/tests/golden/cdp.pvoc.anal/impulse-1024-mono-48000/expected/selected_bins.csv`
- `xyona-cdp-pack/tests/golden/cdp.pvoc.anal/impulse-1024-mono-48000/expected/synth_samples.csv`
- `xyona-cdp-pack/tests/golden/cdp.pvoc.anal/sine440-2048-mono-48000/manifest.yaml`
- `xyona-cdp-pack/tests/golden/cdp.pvoc.anal/sine440-2048-mono-48000/expected/selected_bins.csv`
- `xyona-cdp-pack/tests/golden/cdp.pvoc.anal/sine440-2048-mono-48000/expected/synth_samples.csv`
- `xyona-cdp-pack/tests/test_cdp_pvoc_analysis.cpp`
- `xyona-cdp-pack/tests/test_cdp_offline_session_conformance.cpp`
- `xyona-lab/tests/OfflinePackProcessorClientTests.cpp`
- `xyona-lab/tests/AudioEngineManagerTests.cpp`
- workspace root roadmap/report updates.

Technical change:

- Built the local CDP8 reference `pvoc` target and generated two small reference
  cases from CDP8 itself: 1024-frame impulse mono at 48 kHz and 2048-frame
  440 Hz sine mono at 48 kHz, both using `-c1024 -o3`.
- Added file-backed PVOC golden fixture coverage for selected analysis bins and
  synthesized sample snapshots.
- `cdp.pvoc.synth` no longer emits `analysis.inputFrames` by default. The
  production synthesis path now derives a CDP8-style maximum reconstruction
  length, keeps the tail when the terminal block is non-silent, and trims silent
  trailing blocks.
- The locked reference behavior is now: impulse 1024 input frames synthesizes
  to 896 output frames, sine 2048 input frames synthesizes to 2944 output
  frames, and the non-silent 1024-frame generator graph keeps its reconstruction
  tail and materializes 1920 output frames.
- Lab test expectations were updated so Offline Pack Processor and
  AudioEngineManager validate the negotiated materialized audio length instead
  of assuming the original analysis frame count.

Verification:

- `CDP8`: `cmake -S . -B build\windows-msvc-debug -G "Visual Studio 17 2022" -A x64`
  passed.
- `CDP8`: `cmake --build build\windows-msvc-debug --target pvoc --config Debug`
  passed with existing warnings and produced `NewRelease\Debug\pvoc.exe`.
- `xyona-cdp-pack`: `cmake --build --preset windows-msvc-debug --target test_cdp_pvoc_analysis test_cdp_offline_session_conformance xyona_pack_cdp_ops`
  passed.
- `xyona-cdp-pack`: `ctest --preset windows-msvc-debug -R "cdp_pvoc_analysis_tests|cdp_offline_session_conformance_tests" --output-on-failure`
  passed.
- `xyona-cdp-pack`: full `cmake --build --preset windows-msvc-debug` passed.
- `xyona-cdp-pack`: full `ctest --preset windows-msvc-debug --output-on-failure`
  passed; 19/19 tests.
- `xyona-lab`: `cmake --build --preset windows-dev --target xyona_lab_tests --config Debug`
  passed with existing warnings.
- `xyona-lab`: with
  `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug`,
  `xyona_lab_tests.exe --test="Offline Pack Processor Client" --xyona-only --summary-only`
  passed; 9 tests, 1042 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `xyona_lab_tests.exe --test="AudioEngineManager" --xyona-only --summary-only`
  passed; 45 tests, 2657 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only`
  passed; 13 tests, 354 passes, 0 failures.

Follow-up:

- Expand the PVOC fixture matrix beyond the first impulse/sine cases.
- Generalize typed graph handling beyond one direct PVOC producer -> transform
  chain.
- Spectral-to-spectral host-shape proof is now covered by the later
  `cdp.utility.pvoc_identity` slice; decide separately whether a real CDP8
  spectral transform should be pulled forward before Gate I closes.

## Gate I Slice - Graph-Native PVOC Typed Data Chain

Date: 2026-04-29

Status: implemented locally; commit pending.

Files changed:

- `xyona-cdp-pack/src/operators/cdp_pvoc_anal.cpp`
- `xyona-cdp-pack/src/operators/cdp_pvoc_synth.cpp`
- `xyona-cdp-pack/src/support/pack_descriptors.h`
- `xyona-cdp-pack/tests/test_cdp_descriptor_metadata.cpp`
- `xyona-cdp-pack/tests/test_cdp_spectral_contract.cpp`
- `xyona-lab/src/app/lab/adapters/OperatorProcessMetadata.h`
- `xyona-lab/src/app/lab/adapters/OperatorProcessMetadata.cpp`
- `xyona-lab/src/app/lab/audio/adapter/AudioIOHostAdapters.h`
- `xyona-lab/src/app/lab/audio/adapter/AudioIOHostAdapters.cpp`
- `xyona-lab/src/app/lab/audio/builder/AudioGraphBuilder.h`
- `xyona-lab/src/app/lab/audio/builder/AudioGraphBuilder.cpp`
- `xyona-lab/src/app/lab/audio/builder/AudioTypes.h`
- `xyona-lab/src/app/lab/audio/builder/GraphPlanUtils.cpp`
- `xyona-lab/src/app/lab/audio/engine/AudioGraphProcessor.h`
- `xyona-lab/src/app/lab/audio/engine/AudioGraphProcessor.cpp`
- `xyona-lab/src/app/lab/audio/engine/AudioEngineManager.cpp`
- `xyona-lab/src/app/lab/audio/engine/OfflineRenderEngine.cpp`
- `xyona-lab/tests/OperatorProcessMetadataTests.cpp`
- `xyona-lab/tests/CdpPackCanvasSmokeTests.cpp`
- `xyona-lab/tests/AudioEngineManagerTests.cpp`
- workspace root roadmap/report updates.

Technical change:

- `cdp.pvoc.anal` now exposes a typed `pvoc` output and `cdp.pvoc.synth`
  exposes a typed `pvoc` input, both tagged `typed_data` / `pvoc_analysis` and
  advertised with `abiV2Support="requires_typed_data_host_contract"`.
- Lab metadata now distinguishes `RequiresTypedDataHostContract` from the older
  future-contract marker and exposes producer/transform eligibility helpers for
  offline typed-data graph nodes.
- Graph planning now has `EdgeKind::Data`, records typed data links in
  `GraphPlan::offlineTypedDataEdges`, excludes them from audio `Wire`s and PDC,
  and fingerprints them in materialized render dependencies.
- Added offline host adapters for typed data producer and typed data transform
  nodes. They capture the block-pass context, then call the existing
  `OfflinePackProcessorClient` data-artifact and data-to-audio session paths.
- OfflineRenderEngine now supports the first narrow chain shape:
  one typed data edge from an analysis producer to a transform, with transform
  audio routed directly to terminal targets such as `lab.mainbus_out`.
- Lab tests now build and render
  `cdp.utility.generator_probe -> cdp.pvoc.anal -> cdp.pvoc.synth -> lab.mainbus_out`
  and verify typed edge planning, audio output, progress, bus capture, and
  session metadata.

Verification:

- `xyona-cdp-pack`: `cmake --build --preset windows-msvc-debug` passed.
- `xyona-cdp-pack`: `ctest --preset windows-msvc-debug --output-on-failure`
  passed; 19/19 tests.
- `xyona-lab`: `cmake --build --preset windows-dev --target xyona_lab_tests --config Debug`
  passed with existing warnings.
- `xyona-lab`: with
  `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug`,
  `xyona_lab_tests.exe --test="Operator Process Metadata" --xyona-only --summary-only`
  passed; 11 tests, 102 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only`
  passed; 13 tests, 354 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `xyona_lab_tests.exe --test="AudioEngineManager" --xyona-only --summary-only`
  passed; 45 tests, 1761 passes, 0 failures.

Follow-up:

- Add broader CDP8-generated PVOC fixtures for analysis -> synthesis identity
  and larger spectral behavior.
- Superseded by the later PVOC spectral-to-spectral identity slice for the
  first technical data -> data -> audio host shape.
- Generalize typed graph handling beyond the current direct and one-intermediate
  PVOC chains before exposing arbitrary real spectral workflows.
- Add persisted artifact-handle semantics if typed data must survive as a graph
  value across sessions or non-direct render shapes.

## Gate J Slice - Pack Generator Null-Upstream Graph

Date: 2026-04-29

Status: implemented locally; commit pending.

Files changed:

- `xyona-cdp-pack/CMakeLists.txt`
- `xyona-cdp-pack/specs/cdp8_inventory.yaml`
- `xyona-cdp-pack/src/operators/cdp_utility_generator_probe.h`
- `xyona-cdp-pack/src/operators/cdp_utility_generator_probe.cpp`
- `xyona-cdp-pack/src/pack_registration.cpp`
- `xyona-cdp-pack/src/runtime/cdp_process_contract.h`
- `xyona-cdp-pack/src/support/pack_descriptors.h`
- `xyona-cdp-pack/tests/test_cdp_descriptor_metadata.cpp`
- `xyona-cdp-pack/tests/test_cdp_pack.cpp`
- `xyona-cdp-pack/tests/test_cdp_process_contract.cpp`
- `xyona-lab/tests/CdpPackCanvasSmokeTests.cpp`
- `xyona-lab/tests/AudioEngineManagerTests.cpp`

Technical change:

- Added synthetic `cdp.utility.generator_probe` as a technical CDP-pack fixture,
  not a CDP8 algorithm port. Its descriptor publishes
  `processShape="generator"`, `outputLength="same_as_input"`,
  `abiV2Support="direct"`, zero inputs, and one expandable audio output.
- The generator emits deterministic finite audio without upstream input in RT
  and HQ modes, validating the pack ABI and Lab host assumptions for future CDP
  generator operators.
- Lab Canvas smoke now proves the descriptor is discoverable, instantiable, and
  marked `RealtimeAndOffline`.
- Lab AudioEngineManager now builds and renders
  `cdp.utility.generator_probe -> lab.mainbus_out` without any upstream audio
  node and verifies the rendered stereo output samples.

Verification:

- `xyona-cdp-pack`: `cmake --build --preset windows-msvc-debug` passed after
  closing the local Debug `XYONA Lab.exe` process that had the old pack DLL
  loaded.
- `xyona-cdp-pack`: `ctest --preset windows-msvc-debug --output-on-failure`
  passed; 19/19 tests.
- `xyona-lab`: `cmake --build --preset windows-dev --target xyona_lab_tests --config Debug`
  passed with existing warnings.
- `xyona-lab`: with
  `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug`,
  `xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only`
  passed; 13 tests, 346 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `xyona_lab_tests.exe --test="AudioEngineManager" --xyona-only --summary-only`
  passed; 44 tests, 711 passes, 0 failures.

Follow-up:

- Superseded by the later Gate I graph-native PVOC typed data chain slice for
  direct Canvas/HQ `cdp.pvoc.anal -> cdp.pvoc.synth` chaining.
- Remaining generator-specific work should wait for a real CDP8 generator
  family or a host shape that the synthetic fixture does not already cover.

## Gate I Slice - PVOC Synth Data Input Path

Date: 2026-04-29

Commits:

- `xyona-core`: `4ec3915 feat(core): add offline session data input ABI`
- `xyona-cdp-pack`: `167542c feat(cdp-pack): add pvoc synth data input session`
- `xyona-lab`: `9e79e486 feat(lab): render offline audio from data artifacts`
- workspace root: this report/roadmap update records the Gate I typed data
  input and PVOC synthesis path and advances the `xyona-cdp-pack` Gitlink.

Files changed:

- `xyona-core/include/xyona/api/offline_session.h`
- `xyona-core/tests/test_offline_session_abi.cpp`
- `xyona-cdp-pack/src/offline_api.cpp`
- `xyona-cdp-pack/src/runtime/cdp_pvoc_analysis.h`
- `xyona-cdp-pack/src/runtime/cdp_pvoc_analysis.cpp`
- `xyona-cdp-pack/src/operators/cdp_pvoc_synth.h`
- `xyona-cdp-pack/src/operators/cdp_pvoc_synth.cpp`
- `xyona-cdp-pack/src/pack_registration.cpp`
- `xyona-cdp-pack/src/support/pack_descriptors.h`
- `xyona-cdp-pack/specs/cdp8_inventory.yaml`
- `xyona-cdp-pack/tests/test_cdp_offline_session_conformance.cpp`
- `xyona-cdp-pack/tests/test_cdp_pvoc_analysis.cpp`
- `xyona-cdp-pack/tests/test_cdp_spectral_contract.cpp`
- `xyona-cdp-pack/tests/test_cdp_descriptor_metadata.cpp`
- `xyona-lab/src/app/lab/audio/engine/OfflinePackProcessorClient.h`
- `xyona-lab/src/app/lab/audio/engine/OfflinePackProcessorClient.cpp`
- `xyona-lab/tests/OfflinePackProcessorClientTests.cpp`
- `xyona-lab/tests/OfflinePackProcessorClientSmoke.cpp`
- `xyona-lab/tests/CdpPackCanvasSmokeTests.cpp`

Technical change:

- Extended the Core Offline Session ABI to v3. The v1/v2 prefix remains stable,
  while v3 adds `input_data_count` to session creation and `feed_input_data` for
  typed payload delivery into pack sessions.
- Added PVOC analysis JSON deserialization in the CDP pack runtime, with schema,
  shape, sample-rate, bin-count, and finite-value validation for
  `xyona.cdp.pvoc.analysis.v1`.
- Registered public `cdp.pvoc.synth` as a CDP8 `PVOC_SYNTH`-style typed data
  transform. It requires exactly one `pvoc_analysis` payload with media type
  `application/vnd.xyona.cdp.pvoc+json`, accepts chunked input blocks through
  Offline Session ABI v3, rejects audio input, and emits analysis-dependent mono
  materialized audio.
- Added Lab `OfflinePackProcessorClient::renderWholeFileAudioFromDataArtifact`
  so the host can run a typed data artifact through an Offline Session and read
  the resulting audio artifact. The implementation validates ABI v3 support,
  output artifact shape, materialized-audio RT re-entry mode, and negotiated
  output frame count.
- Added Pack and Lab coverage for the analysis -> synthesis path:
  `cdp.pvoc.anal` produces a real PVOC JSON artifact, Lab feeds it into
  `cdp.pvoc.synth`, and the result is finite, nonzero mono audio.

Verification:

- `xyona-core`: `cmake --build build/macos-clang-debug --target test_offline_session_abi -j 6`
  passed.
- `xyona-core`: `ctest --test-dir build/macos-clang-debug -R offline_session_abi_tests --output-on-failure`
  passed; 1/1 test.
- `xyona-core`: `cmake --build build/macos-clang-debug -j 6` passed.
- `xyona-core`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed; 8/8 tests.
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug --target test_cdp_pvoc_analysis test_cdp_spectral_contract test_cdp_offline_session_conformance test_cdp_descriptor_metadata xyona_pack_cdp_ops -j 6`
  passed.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug -R "cdp_pvoc_analysis_tests|cdp_pvoc_golden_tests|cdp_spectral_contract_tests|cdp_offline_session_conformance_tests|cdp_descriptor_metadata_tests" --output-on-failure`
  passed; 5/5 tests.
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug -j 6` passed.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed; 19/19 tests.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests xyona_lab_cdp_offline_smoke -j 6`
  passed.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="Offline Pack Processor Client" --summary-only --xyona-only`
  passed; 9 tests, 1170 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  passed; 12 tests, 325 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_cdp_offline_smoke`
  passed.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --summary-only --xyona-only`
  passed; 1197 tests, 945272 passes, 0 failures.
- Remote CI on 2026-04-29 still could not run code. Core run `25094646197`,
  Pack run `25094646072`, and Lab run `25094646144` failed before job steps
  started; the Windows and macOS jobs all reported empty `steps` arrays,
  matching the existing GitHub Actions billing/spending-limit blocker.
- `xyona-core`, `xyona-cdp-pack`, and `xyona-lab`: `git diff --check` passed
  before commit.

Follow-up:

- Superseded by the later Gate I graph-native PVOC typed data chain slice:
  Canvas/HQ can now connect `cdp.pvoc.anal` directly to `cdp.pvoc.synth` for
  the first narrow chain.
- Superseded again by the later PVOC spectral-to-spectral identity slice for
  the first technical typed data -> typed data -> audio chain.
- Remaining work is broader CDP8 PVOC fixtures plus generalized typed graph /
  persisted-handle support for arbitrary multiple chains.

## Gate I Slice - PVOC Analysis Operator

Date: 2026-04-29

Commits:

- `xyona-cdp-pack`: `7db5698 feat(cdp-pack): add pvoc analysis operator`
- `xyona-lab`: `db8183d6 test(lab): cover cdp pvoc analysis artifacts`
- workspace root: this report/roadmap update records the first real Gate I
  PVOC analysis producer and advances the `xyona-cdp-pack` Gitlink.

Files changed:

- `xyona-cdp-pack/CMakeLists.txt`
- `xyona-cdp-pack/specs/cdp8_inventory.yaml`
- `xyona-cdp-pack/src/runtime/cdp_pvoc_analysis.h`
- `xyona-cdp-pack/src/runtime/cdp_pvoc_analysis.cpp`
- `xyona-cdp-pack/src/operators/cdp_pvoc_anal.h`
- `xyona-cdp-pack/src/operators/cdp_pvoc_anal.cpp`
- `xyona-cdp-pack/src/offline_api.cpp`
- `xyona-cdp-pack/src/pack_registration.cpp`
- `xyona-cdp-pack/src/support/pack_descriptors.h`
- `xyona-cdp-pack/tests/test_cdp_pvoc_analysis.cpp`
- `xyona-cdp-pack/tests/test_cdp_descriptor_metadata.cpp`
- `xyona-cdp-pack/tests/test_cdp_offline_session_conformance.cpp`
- `xyona-cdp-pack/tests/test_cdp_spectral_contract.cpp`
- `xyona-lab/tests/OfflinePackProcessorClientTests.cpp`
- `xyona-lab/tests/CdpPackCanvasSmokeTests.cpp`

Technical change:

- Added `cdp.pvoc.anal` as the first real Gate I PVOC producer. It implements a
  CDP8 `PVOC_ANAL`-style mono magnitude/frequency analysis path with 1024-point
  FFT/window, 128-sample hop, 513 real bins, explicit frame/bin metadata, JSON
  serialization, and file-backed/data-only Offline Session output.
- Added pack-local PVOC runtime support for analysis data, frame/bin objects,
  Hamming window normalization, phase-unwrapped magnitude/frequency bins, JSON
  payload generation, and an internal synthesis helper used by tests.
- At this slice, public `PVOC_SYNTH` was intentionally kept unregistered. The
  later PVOC synth data input slice supersedes that blocker with Offline
  Session ABI v3 typed payload delivery.
- Wired the operator through pack registration, descriptor metadata, inventory,
  Offline Session create/feed/finish/read callbacks, descriptor validation,
  spectral-contract tests, and Offline Session conformance.
- Added Lab coverage proving `cdp.pvoc.anal` is discoverable as a data-only
  spectral descriptor, rejected from RT/block-audio paths, executable through
  `renderWholeFileDataArtifacts`, and materialized with real PVOC payload bytes
  plus descriptor metadata.

Verification:

- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug --target test_cdp_pvoc_analysis test_cdp_spectral_contract test_cdp_offline_session_conformance test_cdp_descriptor_metadata xyona_pack_cdp_ops -j 6`
  passed.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug -R "cdp_pvoc_analysis_tests|cdp_pvoc_golden_tests|cdp_spectral_contract_tests|cdp_offline_session_conformance_tests|cdp_descriptor_metadata_tests" --output-on-failure`
  passed; 5/5 tests.
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug -j 6` passed.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed; 19/19 tests.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests -j 6`
  passed.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="Offline Pack Processor Client" --summary-only --xyona-only`
  passed; 8 tests, 134 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  passed; 11 tests, 305 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_cdp_offline_smoke`
  passed.
- `xyona-lab`: full `build/macos-dev/tests/xyona_lab_tests --summary-only --xyona-only`
  had one unrelated `TransportContracts / Double-buffer snapshot preserves
  invariants` failure with `XYONA_OPERATOR_PACK_PATH` unset; the targeted
  `TransportContracts` rerun passed with 7 tests, 18 passes, 0 failures.
- Remote CI on 2026-04-29 could not run code. Pack run `25092257976` and Lab
  run `25092266656` failed before job steps started; both Windows and macOS jobs
  reported empty `steps` arrays, matching the existing GitHub Actions
  billing/spending-limit blocker.
- `xyona-cdp-pack` and `xyona-lab`: `git diff --check` passed before commit.

Follow-up:

- Superseded by the later Gate I PVOC synth data input slice: Offline Session
  ABI v3 and public `cdp.pvoc.synth` now exist.
- Superseded again by the later Gate I graph-native PVOC typed data chain
  slice for the first direct Canvas/HQ analysis -> synthesis graph.
- Superseded again by the later PVOC spectral-to-spectral identity slice for
  the first technical typed data -> typed data -> audio graph.
- Remaining work is broader CDP8-generated PVOC fixtures plus generalized typed
  graph / persisted-handle support for arbitrary multiple chains.

## Gate I Slice - PVOC Golden Harness

Date: 2026-04-28

Commit:

- `xyona-cdp-pack`: `8d84014 test(cdp-pack): add pvoc golden harness`
- workspace root: this report/roadmap update records the PVOC golden harness
  slice and advances the `xyona-cdp-pack` Gitlink.

Files changed:

- `xyona-cdp-pack/CMakeLists.txt`
- `xyona-cdp-pack/src/validation/cdp_pvoc_golden.h`
- `xyona-cdp-pack/src/validation/cdp_pvoc_golden.cpp`
- `xyona-cdp-pack/tests/test_cdp_pvoc_golden.cpp`
- `xyona-cdp-pack/tests/golden/README.md`

Technical result:

- Added `CdpPvocGoldenFixtureSpec` for CDP8-reference-generated PVOC/PVX-style
  fixtures. The contract records operator/case identity, reference kind,
  validation strategy, source reference, sample rate, channel count, input
  frames, analysis frames, window size, hop size, FFT size, bin count, bin
  encoding, and tolerance.
- Added validation for PVOC-specific strategies, required CDP8 source
  references, positive audio/analysis shape, valid spectral shape, supported
  magnitude/frequency or magnitude/phase encodings, and nonnegative tolerance.
- Added `comparePvocGoldenData()` for in-memory PVOC frame/bin comparisons. It
  compares both bin components, rejects nonfinite values, honors the existing
  golden tolerance model, and reports the exact frame/bin/component with the
  maximum error.
- Documented PVOC/data golden manifest fields in `tests/golden/README.md`.

Verification:

- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug --target test_cdp_pvoc_golden -j 6`
  passed.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug -R "cdp_pvoc_golden_tests|cdp_golden_compare_tests|cdp_spectral_contract_tests" --output-on-failure`
  passed; 3/3 tests.
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug -j 6`
  passed; target graph was already up to date.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed; 18/18 tests.
- `xyona-cdp-pack`: `git diff --check`
  passed before commit.
- Remote CI run `25081343127` could not run code on 2026-04-28 because GitHub
  Actions rejected the Windows and macOS jobs before job startup with the
  account billing/spending-limit annotation.

Remaining risk:

- The harness is intentionally test-side infrastructure. Later slices added
  the first real `cdp.pvoc.anal` producer and public `cdp.pvoc.synth`, but
  larger operator-specific CDP8-generated fixture assets still need algorithm
  comparison coverage.
- The current tiny PVOC comparison tests are in-memory contract tests; they do
  not claim full-family CDP8 algorithm parity by themselves.

## Gate I Slice - Persistent Data Artifact Assets

Date: 2026-04-28

Commit:

- `xyona-lab`: `8b6f8f22 feat(lab): persist materialized data artifacts`
- workspace root: this report/roadmap update records the persistent data
  artifact slice.

Files changed:

- `xyona-lab/src/app/CMakeLists.txt`
- `xyona-lab/src/app/MainWindow.cpp`
- `xyona-lab/src/app/lab/audio/engine/AudioEngineManager.h`
- `xyona-lab/src/app/lab/audio/engine/MaterializedDataArtifactStore.h`
- `xyona-lab/src/app/lab/audio/engine/MaterializedDataArtifactStore.cpp`
- `xyona-lab/src/app/lab/audio/engine/MaterializedDataArtifactProjectPersistence.h`
- `xyona-lab/src/app/lab/audio/engine/MaterializedDataArtifactProjectPersistence.cpp`
- `xyona-lab/src/app/state/ProjectState.h`
- `xyona-lab/src/app/state/projectstate/ProjectStateCoreMethods.inc`
- `xyona-lab/src/app/state/projectstate/ProjectStatePreamble.inc`
- `xyona-lab/tests/CMakeLists.txt`
- `xyona-lab/tests/MaterializedDataArtifactStoreTests.cpp`
- `xyona-lab/tests/OfflinePackProcessorClientTests.cpp`

Technical result:

- Added `MaterializedDataArtifactStore` for non-audio
  `OfflineDataArtifactPayload` objects. It stores artifact identity, producer
  metadata, media type, schema, file extension, descriptor metadata, raw bytes,
  file path, byte count, content fingerprint, dependency signature, and
  `Valid` / `Rendering` / `Stale` / `Missing` / `Failed` state.
- The store accepts data-only Offline Session outputs, rejects audio artifacts,
  requires `OfflineRealtimeReentryPolicy::DataOnly`, persists resident bytes as
  project-owned assets, and detects external file edits or dependency signature
  mismatches as `Stale`.
- Added `MaterializedDataArtifactProjectPersistence`: project assets live under
  `ProjectName.xyona-assets/materialized_data`, manifest metadata is stored in
  `ProjectState`, resident bytes are restored on open, orphaned data files are
  cleaned on save, and missing directories/files reload as `Missing`.
- `AudioEngineManager` now owns the data artifact store. `MainWindow` save,
  save-as, and open integrate data artifact persistence with warning dialogs on
  persistence/load errors.
- The real `cdp.utility.pvoc_probe` client test now also feeds the returned
  PVOC payload into the store and validates the data dependency signature path.

Verification:

- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests xyona_lab_cdp_offline_smoke -j 6`
  passed.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Data Artifact Store" --summary-only --xyona-only`
  passed; 3 tests, 69 passes, 0 failures.
- `xyona-lab`: with `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug`,
  `build/macos-dev/tests/xyona_lab_tests --test="Offline Pack Processor Client" --summary-only --xyona-only`
  passed; 7 tests, 107 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  passed; 10 tests, 279 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `build/macos-dev/tests/xyona_lab_cdp_offline_smoke`
  passed.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --summary-only --xyona-only`
  passed; 1176 tests, 943668 passes, 0 failures. The run emitted existing JUCE
  assertion text in older tests but the final Catch summary was green.
- `xyona-lab`: `git diff --cached --check`
  passed before commit.
- Remote CI run `25081107777` could not run code on 2026-04-28 because GitHub
  Actions rejected the Lab job before job startup with the account
  billing/spending-limit annotation.

Remaining risk:

- The persistent store proves data/PVOC asset lifecycle, staleness, and project
  save/open behavior, but there is still no real CDP8 PVOC algorithm feeding it.
- Future real spectral operators must include their own spectral settings and
  any additional source asset fingerprints in the dependency signature.

## Gate I Slice - Data-Only Offline Artifacts

Date: 2026-04-28

Commits:

- `xyona-core`: `a9ddb60 feat(core): add offline session data reads`
- `xyona-cdp-pack`: `8214aa4 feat(cdp-pack): add pvoc data artifact session`
- `xyona-lab`: `3fa12897 feat(lab): materialize offline data artifacts`
- workspace root: this report/roadmap update records the Gate I data artifact
  slice and advances the `xyona-cdp-pack` Gitlink.

Technical result:

- Core Offline Session ABI v2 adds `xyona_pack_offline_session_data_desc`,
  `xyona_pack_offline_session_read_data_request`,
  `get_output_data_desc`, and `read_output_data` while preserving the v1
  prefix layout through `XYONA_PACK_OFFLINE_SESSION_API_SIZE_V1`.
- The CDP pack registers `cdp.utility.pvoc_probe` as a technical, data-only
  PVOC fixture. It requires whole-file input, emits no block audio output, and
  returns a deterministic file-backed `pvoc_analysis` artifact with
  `application/vnd.xyona.cdp.pvoc+json`, schema
  `xyona.cdp.pvoc.analysis.v1`, and `xyopvoc` extension.
- Lab's Offline Pack Processor Client now has
  `renderWholeFileDataArtifacts`, which feeds/finishes the production Offline
  Session, validates the data-only artifact contract, reads descriptor metadata
  and bytes, and keeps this path separate from audio materialization and RT
  re-entry.

Verification:

- `xyona-core`: `cmake --build build/macos-clang-debug --target test_offline_session_abi -j 6`
  passed.
- `xyona-core`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed; 8/8 tests.
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug --target xyona_pack_cdp_ops test_cdp_offline_session_conformance test_cdp_descriptor_metadata -j 6`
  passed.
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug -j 6`
  passed after rebuilding stale test binaries against ABI v2.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed; 17/17 tests.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests xyona_lab_cdp_offline_smoke -j 6`
  passed.
- `xyona-lab`: with `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug`,
  `build/macos-dev/tests/xyona_lab_tests --test="Offline Pack Processor Client" --summary-only --xyona-only`
  passed; 7 tests, 102 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  passed; 10 tests, 279 passes, 0 failures.
- `xyona-lab`: with the same pack path,
  `build/macos-dev/tests/xyona_lab_cdp_offline_smoke` passed.
- `git diff --check` passed for touched Core, Pack, and Lab files.
- Remote CI could not run code on 2026-04-28 because GitHub Actions rejected
  Core run `25077292280`, Pack run `25077304074`, and Lab run `25077315551`
  before job startup with the account billing/spending-limit annotation.

Remaining risk:

- `cdp.utility.pvoc_probe` is deliberately a technical fixture, not a real CDP8
  PVOC algorithm.
- The persistent typed data asset store and PVOC golden harness were completed
  in later Gate I slices on 2026-04-28.
- Real PVOC analysis/synthesis ports and their operator-specific
  CDP8-generated fixture assets remain required before Gate I can close.

## Gate I Preflight - Spectral Metadata Contract

Date: 2026-04-28

Commits:

- `xyona-cdp-pack`: `d613571 feat(cdp-pack): add spectral artifact contract`
- `xyona-lab`: `a8b02b97 feat(lab): parse spectral operator metadata`
- workspace root: this report/roadmap update records the Gate I preflight and
  advances the `xyona-cdp-pack` Gitlink.

Technical result:

- The CDP pack now has `runtime/cdp_spectral_contract.h`, defining the first
  concrete PVOC/spectral artifact contract for future data-only Offline Session
  outputs.
- The contract validates sample rate, channel count, power-of-two window/FFT
  sizes, hop size, real-FFT bin count, frame-count model, PVOC artifact type,
  and magnitude/frequency bin encoding.
- The CDP pack descriptor helper now includes a canonical
  `XYONA_CDP_ENGINE_PVOC_ANALYSIS_DATA_JSON` metadata shape for future
  file-backed, data-only `pvoc_analysis` outputs.
- The pack process contract now allows `analysis_data_output` and
  `multi_file_output` shapes to require whole-file host execution without
  becoming block-processable or audio-producing.
- Lab's `OperatorProcessMetadata` now parses `engine.spectral`, records PVOC
  format/bin/frame metadata, validates real-FFT layout, and rejects descriptors
  that advertise spectral data as direct audio output.

Verification:

- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug --target test_cdp_process_contract test_cdp_spectral_contract -j 6`
  passed.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug -R "cdp_process_contract_tests|cdp_spectral_contract_tests" --output-on-failure`
  passed; 2/2 tests.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed; 17/17 tests.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests -j 6`
  passed.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Operator Process Metadata" --summary-only --xyona-only`
  passed; 10 tests, 94 passes, 0 failures.
- `git diff --check` passed for the Pack and Lab touched files.
- Remote CI could not run code on 2026-04-28 because GitHub Actions rejected
  both Pack run `25076365951` and Lab run `25076388018` before job startup with
  the account billing/spending-limit annotation.

Remaining risk:

- This preflight only defined the descriptor/metadata contract. Follow-on
  slices later proved the data-read transport, persistent typed asset lifecycle,
  PVOC golden harness, first real `cdp.pvoc.anal` producer, Offline Session
  typed data input, public `cdp.pvoc.synth`, and the first graph-native
  one-chain analysis -> synthesis render. Spectral-to-spectral and generalized
  multi-chain typed graph work still need persisted-handle semantics plus
  broader generated fixtures.

## Post-Gate-H Slice - CDP Edit Cutend

Date: 2026-04-28

Commits:

- `xyona-cdp-pack`: `f6f5a1d feat(cdp-pack): add edit cutend offline session`
- `xyona-lab`: `d45fc1d1 test(lab): cover cdp edit cutend offline session`
- workspace root: this report/roadmap update records the `cutend` slice and
  advances the `xyona-cdp-pack` Gitlink.

Technical result:

- `cdp.edit.cutend` implements CDP8 `sfedit cutend` mode 1 as a
  param-dependent length-changing Offline Session operator.
- The pack descriptor records CDP provenance, command shape, process number
  `207`, length-changing metadata, validation strategy, and the Offline Session
  engine contract.
- The session keeps the final `length_seconds` of input, applies the CDP
  start-splice rule only, rejects invalid keep/splice windows, reports
  `ParamDependent` output length, and exposes one RT-reentry-capable in-memory
  audio artifact.
- Lab coverage proves the operator loads from the dynamic pack, materializes
  the negotiated shorter end segment, sanitizes audio consistently, and is
  Canvas-classified as offline whole-file length-changing rather than RT/HQ
  block-processable.

Verification:

- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug --target xyona_pack_cdp_ops test_cdp_edit_cut test_cdp_descriptor_metadata test_cdp_offline_session_conformance -j 6`
  passed.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug -R "cdp_edit_cut_tests|cdp_descriptor_metadata_tests|cdp_offline_session_conformance_tests" --output-on-failure`
  passed; 3/3 tests.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed; 16/16 tests.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests xyona_lab_cdp_offline_smoke -j 6`
  passed.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="Offline Pack Processor Client" --summary-only --xyona-only`
  passed; 6 tests, 80 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  passed; 9 tests, 259 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_cdp_offline_smoke`
  passed.
- Remote: CDP pack GitHub Actions run `25075159320` passed for `f6f5a1d`,
  with `macOS Clang Debug` and `Windows MSVC Debug` successful.
- Remote: Lab GitHub Actions run `25075158292` passed for `d45fc1d1`, with
  `macOS Clang Debug` and `Windows MSVC Debug` successful.

Remaining risk:

- This confirms another real param-dependent audio editor on the existing host
  contract. It does not change the Gate I constraint: PVOC/spectral still needs
  concrete typed data or asset handles and CDP8 spectral goldens before real
  spectral ports start.

## Gate H Close-Out - Infrastructure Contract

Date: 2026-04-28

Commits:

- `xyona-cdp-pack`: `49c42cc test(cdp-pack): add gate h conformance coverage`
- `xyona-lab`: `0df30e03 test(lab): cover gate h artifact contracts`
- workspace root: this report/roadmap update records the Gate H close-out and
  advances the `xyona-cdp-pack` Gitlink.

Technical result:

- CDP pack descriptor/metadata validation now covers the exact current CDP
  operator set, shape/capability consistency, provenance, validation strategy,
  parameter metadata, port metadata, and technical-role exceptions.
- Offline Session conformance now exercises lifecycle and error contracts across
  `cdp.modify.loudness_normalise`, `cdp.utility.length_change`, and
  `cdp.edit.cut`.
- Golden fixture metadata now distinguishes analytical fixtures from
  CDP8-reference-generated fixtures.
- Lab artifact-contract tests now cover data-only, multi-artifact,
  file-collection, typed-data, multi-output, and unsupported mixed-shape
  contracts.

Verification:

- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed; 16/16 tests.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests -j 6`
  passed.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Offline Artifact Contract" --summary-only --xyona-only`
  passed; 8 tests, 27 passes, 0 failures.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Operator Process Metadata" --summary-only --xyona-only`
  passed; 7 tests, 65 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="Offline Pack Processor Client" --summary-only --xyona-only`
  passed; 5 tests, 64 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  passed; 8 tests, 240 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager" --summary-only --xyona-only`
  passed; 42 tests, 695 passes, 0 failures.
- Remote: CDP pack GitHub Actions run `25073486854` passed for
  `49c42cc`, with `macOS Clang Debug` and `Windows MSVC Debug` successful.
- Remote: Lab GitHub Actions run `25073495548` passed for `0df30e03`, with
  `macOS Clang Debug` and `Windows MSVC Debug` successful.

Remaining risk:

- Gate H does not implement real PVOC/spectral operators. It defines and tests
  the contract that typed data/spectral artifacts must obey in Gate I.
- Additional CDP8 families should add family-specific golden fixtures as they
  are ported.

## Gate E Close-Out - Offline Session ABI

Date: 2026-04-28

Commits:

- `xyona-core`: `ed0982a5 feat(core): add offline session abi`
- `xyona-cdp-pack`: `5c39e098 feat(cdp-pack): implement offline session normalise`
- `xyona-lab`: `50abd15f feat(lab): render whole-file packs through sessions`
- workspace root: this report/roadmap close-out commit

Repositories changed:

- `xyona-core`
- `xyona-cdp-pack`
- `xyona-lab`

Technical change:

- Core now has the first production `xyona/api/offline_session.h` C ABI surface:
  session create/feed/finish/output-count/output-desc/read-audio/cancel/destroy,
  progress and cancellation callbacks, and host scratch policy fields.
- The CDP pack exports `xyona_pack_get_offline_session_api`. The normal build no
  longer exports `xyona_pack_get_offline_whole_buffer_prototype_api`; that getter
  is gated behind the explicit `XYONA_CDP_PACK_ENABLE_OFFLINE_PROTOTYPE_EXPORT`
  option for legacy/debug builds.
- `cdp.modify.loudness_normalise` now has a session-backed implementation that
  accepts streaming input blocks, finalizes whole-file peak normalization,
  reports progress, supports cancellation, discovers one same-length audio
  output, and reads output audio blocks.
- Lab's `OfflinePackProcessorClient` now requires the production Offline Session
  ABI for whole-file pack processing and no longer falls back to
  `offline_whole_buffer_prototype`.
- Lab now forwards whole-file graph render progress and cancellation into the
  Offline Session ABI. A cancelled CDP session render fails deterministically and
  does not publish a partial `MaterializedAudioStore` clip.
- `cdp.modify.loudness_normalise` validates session scratch-policy shape. Pack
  tests keep the prototype query/process logic only as an internal reference
  path, while the exported DLL surface is session-only by default.

Verification:

- `xyona-core`: `ctest --test-dir build\windows-msvc-debug -C Debug --output-on-failure`
  passed; 8 tests, 0 failures.
- `xyona-cdp-pack`: `ctest --preset windows-msvc-debug --output-on-failure`
  passed; 12 tests, 0 failures.
- `xyona-cdp-pack`: `objdump -p build\windows-msvc-debug\Debug\xyona_pack_cdp_ops.dll | Select-String -Pattern "xyona_pack_get_offline"`
  showed only `xyona_pack_get_offline_session_api` in the normal Debug export
  table.
- `xyona-lab`: `xyona_lab_tests.exe --test="Offline Pack Processor Client" --xyona-only --summary-only`
  passed with `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug`;
  3 tests, 30 passes, 0 failures.
- `xyona-lab`: `xyona_lab_tests.exe --test="AudioEngineManager" --xyona-only --summary-only`
  passed with `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug`;
  40 tests, 644 passes, 0 failures.
- `xyona-lab`: `xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only`
  passed with `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug`;
  7 tests, 220 passes, 0 failures.

Gate E exit status:

- Gate E exit criteria are met in the working tree: Core exposes the Offline
  Session ABI, the CDP pack exercises the full lifecycle with the normalise
  reference operator, Lab routes the supported whole-file graph shape through
  sessions, progress/cancellation are covered, and cancelled renders do not
  publish partial materialized RT artifacts.
- Remaining work moves to later gates: CI baseline is Gate F; length-changing
  output negotiation is Gate G; typed data/asset handles for PVOC/spectral work
  remain blocked until the later typed-data/asset phase.

## Gate F Close-Out - CI Baseline

Date: 2026-04-28

Commits:

- `xyona-core`: `d9e2024d ci(core): add windows and macos baseline`
- `xyona-core`: `6cbd68b fix(core): create generated include dirs during configure`
- `xyona-cdp-pack`: `31a6a176 ci(cdp-pack): add windows and macos baseline`
- `xyona-cdp-pack`: `50563ad4 ci(cdp-pack): require token for private core checkout`
- `xyona-lab`: `75c116a4 ci(lab): add cdp smoke baseline`
- `xyona-lab`: `5a65fbca ci(lab): require token for private sibling checkouts`
- `xyona-lab`: `06865527 fix(lab): avoid atomic_ref in control output mirror`
- `xyona-lab`: `d30d3498 ci(lab): enable parallel msvc compilation`
- `xyona-lab`: `9cee3505 ci(lab): use ninja for windows baseline`
- `xyona-lab`: `fae01fec ci(lab): accept current vcpkg eigen package`
- `xyona-lab`: `2eec1b8f ci(lab): add minimal windows cdp smoke`
- workspace root: this report/roadmap update

Technical change:

- Core now has a GitHub Actions workflow for Windows MSVC Debug and macOS Clang
  Debug configure/build/test using existing CMake presets.
- Core's Windows CTest preset now carries `configuration: Debug`, so
  `ctest --preset windows-msvc-debug` works for Visual Studio multi-config
  builds.
- The CDP pack now has a GitHub Actions workflow that checks out `xyona-core`
  as a sibling repo, builds Core first, then configures/builds/tests the pack on
  Windows MSVC Debug and macOS Clang Debug.
- Lab now has a GitHub Actions workflow that checks out sibling Core and CDP
  Pack repos, builds the pack, and runs Gate E CDP smoke coverage with
  `XYONA_OPERATOR_PACK_PATH` pointing at the built pack.
- Lab's Windows leg uses a Ninja/MSVC `windows-ci` preset and builds
  `xyona_lab_cdp_offline_smoke`, a small executable that links only the offline
  pack client/contract code plus Core/JUCE. It loads the dynamic CDP pack, runs
  `cdp.modify.loudness_normalise` through the Offline Session ABI, verifies the
  normalized samples, progress span, session/artifact contract, RT re-entry
  policy, and cancellation behavior. This keeps the hosted Windows baseline
  focused and avoids the full `xyona_lab_lib` test-bundle compile bottleneck.
- Lab's macOS leg still builds `xyona_lab_tests` and runs the three Gate E CDP
  smoke subsets: `Offline Pack Processor Client`, `AudioEngineManager`, and
  `CDP Pack Canvas Smoke`.
- Gate F scope is intentionally asymmetric:
  - Windows: Core CTest, Pack CTest, and Lab `OfflinePackProcessorClientSmoke`
    through dynamic pack discovery and the Offline Session ABI.
  - macOS: Core CTest, Pack CTest, and Lab's full CDP smoke suite
    (`Offline Pack Processor Client`, `AudioEngineManager`, and
    `CDP Pack Canvas Smoke`) from `xyona_lab_tests`.
  The asymmetry is deliberate because hosted Windows runner build time for the
  full JUCE/Lab test bundle is too high for the first CI baseline, while the
  focused Windows smoke still proves the CDP pack loading and offline-session
  contract that Gate F needs.
- Pack and Lab workflows require a private sibling-repo token named
  `XYONA_CI_REPO_TOKEN`; without it, GitHub Actions cannot clone private sibling
  repositories from another repo's workflow token.

Verification:

- Local: `xyona-core` `ctest --preset windows-msvc-debug --output-on-failure`
  passed; 8 tests, 0 failures.
- Local: `xyona-cdp-pack` `ctest --preset windows-msvc-debug --output-on-failure`
  passed; 12 tests, 0 failures.
- Local: `xyona-lab` `cmake --preset windows-dev` passed after adding the
  minimal smoke target.
- Local: `xyona-lab`
  `cmake --build --preset windows-dev --target xyona_lab_cdp_offline_smoke`
  passed.
- Local: `xyona-lab`
  `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug .\build\windows-dev\tests\Debug\xyona_lab_cdp_offline_smoke.exe`
  passed with `xyona_lab_cdp_offline_smoke passed`.
- Local: `git diff --check` passed for Core, Pack, and Lab CI edits.
- Remote: Core CI run `25048402759` completed successfully for commit
  `6cbd68b`.
- Remote: CDP pack CI run `25046455344` completed successfully for commit
  `50563ad4`.
- Remote: Lab CI run `25057837762` completed successfully for commit
  `2eec1b8f`; Windows MSVC Debug and macOS Clang Debug both passed.

Gate F exit status:

- Gate F exit criteria are met: Core, Pack, and Lab are covered by GitHub
  Actions on Windows MSVC Debug and macOS Clang Debug, and CDP pack runtime
  discovery/offline-session execution is covered in Lab CI.
- Non-blocking follow-up: improve hosted Windows coverage throughput with
  `sccache` or split the CDP-focused Lab tests into a dedicated
  `xyona_lab_cdp_tests` target.
- Linux CI expansion remains planned later and does not block the Gate F
  baseline.
- The next major block is Gate G: length-changing audio through the Offline
  Session ABI.

## Commit Log

### Realtime Materialized Clip Graph Routing

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `fbfa6e35`

Subject: `feat(lab): route materialized clips into realtime graph`

Files changed:

- `src/app/lab/operators/io/MaterializedAudioClipOperator.h`
- `src/app/lab/operators/io/MaterializedAudioClipOperator.cpp`
- `src/app/lab/operators/io/IOOperatorRegistration.cpp`
- `src/app/lab/audio/builder/AudioGraphBuilder.h`
- `src/app/lab/audio/builder/AudioGraphBuilder.cpp`
- `src/app/lab/audio/builder/GraphPlanDiagnostics.h`
- `src/app/lab/audio/builder/GraphPlanDiagnostics.cpp`
- `src/app/lab/audio/engine/AudioEngineManager.cpp`
- `tests/AudioEngineManagerTests.cpp`

Technical change:

- Added the registered realtime custom operator `lab.layer_player`.
- `AudioEngineManager` now passes its active `MaterializedAudioStore` into the
  realtime `GraphBuilder`.
- GraphBuilder resolves `clip_id` against the store during graph build and
  creates a prepared `LayerPlayerHostAdapter` source for valid resident clips.
- Missing, stale, failed, or nonresident materialized clips keep the realtime
  graph deterministic: the node outputs silence and emits a
  `MaterializedClipUnavailable` diagnostic.
- Added headless coverage for offline render -> materialized clip -> realtime
  `LayerPlayer` playback, and for stale clips producing diagnosed silence.

Verification:

- `xyona-lab`: `git diff --check`
  - Result: passed.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager" --summary-only --xyona-only`
  - Result: passed; 40 tests, 586 passes, 0 failures. The CDP whole-file
    subtest was skipped because `XYONA_OPERATOR_PACK_PATH` was unset.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="LayerPlayerHostAdapter" --summary-only --xyona-only`
  - Result: passed; 4 tests, 37 passes, 0 failures.
- `xyona-lab`: `XYONA_RT_ALLOC_TRAP=2 build/macos-dev/tests/xyona_lab_tests --test="RT Safety Smoke" --summary-only --xyona-only`
  - Result: passed; 2 tests, 4 passes, 0 failures.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  - Result: passed; 6 tests, 145 passes, 0 failures.
- Full Lab CTest was intentionally not run; the focused Gate D coverage includes
  the graph path, adapter behavior, store behavior, and RT allocation smoke.

Follow-up:

- Keep future materialized source/asset types on the same graph-build
  resolution rule: prepare outside RT, diagnose invalid material, and output
  deterministic silence in RT.
- Product UI for clip placement/render queues remains a separate UX decision.

### Materialized Layer Player Adapter

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `b4149bf0`

Subject: `feat(lab): add materialized layer player adapter`

Files changed:

- `src/app/lab/audio/adapter/LayerPlayerHostAdapter.h`
- `src/app/lab/audio/adapter/LayerPlayerHostAdapter.cpp`
- `tests/AudioHostAdapterTests.cpp`
- `tests/RTSafetySmokeTests.cpp`

Technical change:

- Added `LayerPlayerHostAdapter`, an RT-safe playback adapter for prebuilt
  materialized audio sources.
- The adapter copies resident materialized audio into an immutable shared buffer
  before RT processing and only reads that prepared source in `processWired`.
- Playback supports clip source offset, clip length, gain, cursor advance,
  bypass timeline advance, and mono fanout to multiple outputs.
- Added RT safety smoke coverage for the graph path under the allocation trap.

Verification:

- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="LayerPlayerHostAdapter" --summary-only --xyona-only`
  - Result: passed; 4 tests, 37 passes, 0 failures.
- `xyona-lab`: `XYONA_RT_ALLOC_TRAP=2 build/macos-dev/tests/xyona_lab_tests --test="RT Safety Smoke" --summary-only --xyona-only`
  - Result: passed; 2 tests, 4 passes, 0 failures.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  - Result: passed; 6 tests, 145 passes, 0 failures.

Follow-up:

- Wire the adapter into realtime graph construction through a registered
  operator and `MaterializedAudioStore` clip lookup.

### Materialized Audio Status Surface

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `48a79a0a`

Subject: `feat(lab): surface materialized audio status`

Files changed:

- `src/app/lab/audio/engine/MaterializedAudioStatusSummary.h`
- `src/app/lab/audio/engine/MaterializedAudioStatusSummary.cpp`
- `src/app/lab/bottombar/BottomBar.h`
- `src/app/lab/bottombar/BottomBar.cpp`
- `src/app/MainComponent.cpp`
- `src/app/CMakeLists.txt`
- `tests/MaterializedAudioStoreTests.cpp`
- `docs/architecture/HQ_RT.md`

Technical change:

- Added a separate `MaterializedAudioStatusSummary` model that scans
  `MaterializedAudioStore` clips and reports user-visible issues for
  non-RT-playable materialized audio.
- The summary counts `Rendering`, `Stale`, `Missing`, `Failed`, and blocked
  clips and formats compact status text plus detail tooltip diagnostics.
- `BottomBar` now consumes the summary and shows a small status chip only when
  materialized clips need attention. This keeps Gate C user-visible without
  locking the product into this as the final materialized-clip UI.
- `MainComponent` wires the active `AudioEngineManager` store into the
  BottomBar, so project load/save/render state is surfaced from the live store.
- `HQ_RT.md` now marks the first `Re-render required` / `Missing` status UI as
  implemented and leaves the later product Clip/Render Queue UI as a UX choice.

Verification:

- `xyona-lab`: `git diff --check`
  - Result: passed.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  - Result: passed; 6 tests, 145 passes, 0 failures.
- Full Lab CTest was intentionally not run for this focused Gate C UI/status
  slice.

Follow-up:

- Move the summary into a richer materialized clip/render-queue UI once that UX
  is intentionally designed.
- Start Gate D by making realtime LayerPlayer consume valid resident
  `MaterializedAudioStore` clips without disk I/O or pack calls on the audio
  thread.

### Audio File Source Dependency Fingerprints

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `a9271660`

Subject: `feat(lab): fingerprint audio file source dependencies`

Files changed:

- `src/app/lab/adapters/CorePayload.h`
- `src/app/lab/adapters/NodeBinder.h`
- `src/app/lab/adapters/NodeBinder.cpp`
- `src/app/lab/canvas/Canvas.Persistence.cpp`
- `src/app/lab/audio/builder/AudioGraphBuilder.cpp`
- `src/app/lab/audio/engine/AudioEngineManager.cpp`
- `tests/AudioEngineManagerTests.cpp`
- `tests/CanvasParamPersistenceTests.cpp`
- `docs/architecture/HQ_RT.md`

Technical change:

- Added `CorePayload::stringParamValues` for non-RT setup parameters such as
  file/path/string values while keeping numeric `paramValues` as the primary RT
  path.
- `NodeBinder` now initializes, restores, and applies descriptor parameters of
  type `file`, `path`, or `string` as string values, and Canvas persistence
  round-trips them through a `stringParams` array.
- `AudioGraphBuilder` and `OfflineGraphBuilder` now read `lab.audio_file_in`
  and file-out `file_path` values from string parameter state, with numeric
  fallback for older payloads.
- `AudioEngineManager` now includes sorted string parameter values in
  materialized render-dependency fingerprints and adds a source-file content
  fingerprint for `lab.audio_file_in` paths.
- A focused integration test proves that changing the source WAV for
  `lab.audio_file_in` changes the materialized dependency signature and makes
  the older layer verify as `Stale` / `Re-render required` / not RT-playable.
- `HQ_RT.md` now marks `lab.audio_file_in` source dependency fingerprints as
  implemented for the current materialized audio path.

Verification:

- `xyona-lab`: `git diff --check`
  - Result: passed.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --summary-only --xyona-only`
  - Result: passed; 36 tests, 537 passes, 0 failures. The CDP pack subtest was
    skipped because `XYONA_OPERATOR_PACK_PATH` was unset.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Canvas Param Persistence" --summary-only --xyona-only`
  - Result: passed; 14 tests, 88 passes, 0 failures.
- Full Lab CTest was intentionally not run for this focused Gate C slice.

Follow-up:

- Add future spectral settings and any additional external source/asset types
  to dependency signatures as those materialized artifact paths are introduced.
- First status surface was completed later in `48a79a0a`; richer
  materialized-clip UI remains a product UX decision.

### Store-Level Materialized Asset Staleness

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `6b71007b`

Subject: `feat(lab): track materialized asset staleness`

Files changed:

- `src/app/lab/audio/engine/MaterializedAudioStore.h`
- `src/app/lab/audio/engine/MaterializedAudioStore.cpp`
- `src/app/lab/audio/engine/MaterializedAudioProjectPersistence.cpp`
- `tests/MaterializedAudioStoreTests.cpp`
- `docs/architecture/HQ_RT.md`

Technical change:

- Added `MaterializedAudioLayerState` with `Valid`, `Rendering`, `Stale`,
  `Missing`, and `Failed`.
- Added persisted `dependencySignature`, `state`, and `statusMessage` fields to
  materialized layers.
- Exposed `makeMaterializedAudioDependencySignature(...)` and
  `verifyLayerDependencySignature(...)` as the store-level dependency comparison
  API.
- A signature mismatch now marks the layer `Stale`, records `Re-render
  required`, and clears resident audio so stale material is not RT-playable.
- Missing asset directories/files now restore layer metadata as `Missing` with a
  diagnostic message instead of clearing the active store entirely.

Verification:

- `xyona-lab`: `git diff --check`
  - Result: passed.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  - Result: passed; 4 tests, 88 passes, 0 failures.
- Full Lab CTest was intentionally not rerun for this slice.

Follow-up:

- Feed the store API with future spectral settings and any additional
  source/asset dependency fingerprints once those materialized artifact types
  exist.
- First status surface was completed later in `48a79a0a`; richer
  materialized-clip UI remains a product UX decision.

### Graph-Side Materialized Render Dependency Signatures

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `5adbcb97`

Subject: `feat(lab): fingerprint materialized render dependencies`

Files changed:

- `src/app/lab/audio/engine/AudioEngineManager.cpp`
- `src/app/lab/audio/engine/MaterializedAudioStore.h`
- `src/app/lab/audio/engine/MaterializedAudioStore.cpp`
- `tests/AudioEngineManagerTests.cpp`
- `docs/architecture/HQ_RT.md`

Technical change:

- Added an optional render-dependency fingerprint input to
  `makeMaterializedAudioDependencySignature(...)` and to the store
  materialization APIs.
- `AudioEngineManager::renderOfflineToMaterializedClip(...)` now builds a
  deterministic `offline-render-deps-v1` fingerprint from RenderJob fields,
  render range, sample rate, graph plan, wires, whole-file nodes, operator
  descriptor versions, operator parameters, parameter sources, tempo points, and
  timeline grid context.
- The CDP whole-file normalise integration test now renders once, changes an
  upstream `cdp.utility.db_gain` parameter, renders again, verifies that the
  signature changes, and proves the old layer transitions to `Stale` with
  `Re-render required` and `isRealtimePlayable() == false`.
- `HQ_RT.md` now marks the graph/job/parameter side of current signatures as
  implemented. At this point, external source file fingerprints, spectral
  settings, UI, and LayerPlayer RT consumption remained open.

Verification:

- `xyona-lab`: `git diff --check`
  - Result: passed.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  - Result: passed; 4 tests, 88 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --summary-only --xyona-only`
  - Result: passed; 35 tests, 566 passes, 0 failures.
- Full Lab CTest was intentionally not rerun for this slice.

Follow-up:

- Add future spectral settings and any additional source/asset dependency
  fingerprints once those materialized artifact paths exist.
- First status surface was completed later in `48a79a0a`; richer
  materialized-clip UI remains a product UX decision.

### Materialized Asset Orphan Cleanup

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `f87b14aa`

Subject: `feat(lab): clean orphaned materialized audio assets`

Files changed:

- `src/app/lab/audio/engine/MaterializedAudioProjectPersistence.cpp`
- `src/app/lab/audio/engine/MaterializedAudioStore.cpp`
- `tests/MaterializedAudioStoreTests.cpp`
- `docs/architecture/HQ_RT.md`

Technical change:

- Project save now removes unreferenced files from the store-owned
  `*.xyona-assets/materialized_audio` directory.
- Saving an empty materialized store removes an empty materialized-audio asset
  directory.
- Cleanup keeps only files referenced by currently `Valid` manifest layers, so
  old WAV files from stale/missing/failed layers cannot remain active assets.
- Project asset reload no longer loads resident audio for persisted
  stale/missing/failed layers, preventing stale metadata from becoming
  RT-playable just because an old file still exists.
- `HQ_RT.md` now marks materialized asset cleanup/orphan policy as implemented.

Verification:

- `xyona-lab`: `git diff --check`
  - Result: passed.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  - Result: passed; 5 tests, 112 passes, 0 failures.
- Full Lab CTest was intentionally not run for this focused persistence slice.

Follow-up:

- Add future spectral settings and any additional source/asset dependency
  fingerprints once those materialized artifact paths exist.
- First status surface was completed later in `48a79a0a`; richer
  materialized-clip UI remains a product UX decision.

### Materialized WAV Asset File Fingerprints

Repository: `xyona-lab`

Branch: `feature/cdp8-offline-foundation`

Commit: `1d24ef1a`

Subject: `feat(lab): fingerprint materialized audio asset files`

Files changed:

- `src/app/lab/audio/engine/MaterializedAudioStore.h`
- `src/app/lab/audio/engine/MaterializedAudioStore.cpp`
- `tests/MaterializedAudioStoreTests.cpp`
- `docs/architecture/HQ_RT.md`

Technical change:

- Added a persisted `fileFingerprint` field to `MaterializedAudioLayer`
  manifests.
- After saving a resident materialized layer as WAV, Lab now fingerprints the
  closed file using size, mtime, and FNV-64 content hashing.
- Project asset reload compares the persisted fingerprint with the current WAV
  file before decoding it. A mismatch marks the layer `Stale`, records
  `Re-render required`, clears resident audio, and keeps
  `isRealtimePlayable() == false`.
- Existing manifests without `fileFingerprint` remain load-compatible.
- `HQ_RT.md` now distinguishes implemented materialized WAV dependent-asset
  fingerprints from source-file fingerprints, which were added in the later
  `a9271660` slice.

Verification:

- `xyona-lab`: `git diff --check`
  - Result: passed.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  - Result: passed. Build succeeded with existing warning classes only.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  - Result: passed; 5 tests, 123 passes, 0 failures.
- Full Lab CTest was intentionally not run for this focused persistence slice.

Follow-up:

- Add future spectral settings and any additional source/asset dependency
  fingerprints once those materialized artifact paths exist.
- First status surface was completed later in `48a79a0a`; richer
  materialized-clip UI remains a product UX decision.

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

- Materialized asset dependency signatures, stale detection, and first visible
  `Re-render required` state were completed later in the Gate C slices through
  `48a79a0a`.
- Realtime LayerPlayer consumption was completed later in Gate D through
  `b4149bf0` and `fbfa6e35`.

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
- File-backed artifact persistence was completed later in Gate C; realtime
  LayerPlayer consumption was completed later in Gate D through `b4149bf0` and
  `fbfa6e35`.
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
  LayerPlayer playback remained open at that point. Those follow-ups were later
  completed through Gate C and Gate D slices.

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
- Clarified that current materialization was in-memory audio plus metadata
  manifest at that point, not yet file-backed ProjectState persistence or
  realtime LayerPlayer playback. Those follow-ups were later completed through
  Gate C and Gate D slices.
- Updated the next implementation step at that time to focus on file-backed
  artifact assets and RT LayerPlayer consumption.

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

- `xyona-cdp-pack`: targeted Windows Debug build for the PVOC identity slice
  passed: `xyona_pack_cdp_ops`, `test_cdp_descriptor_metadata`,
  `test_cdp_spectral_contract`, and `test_cdp_offline_session_conformance`.
- `xyona-cdp-pack`: targeted CTest for descriptor metadata, spectral contract,
  and Offline Session conformance passed after adding the PVOC identity slice;
  3/3 tests.
- `xyona-cdp-pack`: full `cmake --build --preset windows-msvc-debug --config Debug`
  passed after adding the PVOC identity slice.
- `xyona-cdp-pack`: full `ctest --preset windows-msvc-debug --output-on-failure`
  passed after adding the PVOC identity slice; 19/19 tests.
- `xyona-lab`: `cmake --build --preset windows-dev --target xyona_lab_tests --config Debug`
  passed after adding data-in/data-out spectral transform scheduling.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Operator Process Metadata" --xyona-only --summary-only`
  passed after accepting data-output typed transforms; 12 tests, 112 passes,
  0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Offline Pack Processor Client" --xyona-only --summary-only`
  passed after adding data-input/data-output materialization; 10 tests, 1054
  passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only`
  passed after adding the PVOC identity descriptor/Canvas coverage; 14 tests,
  376 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="AudioEngineManager" --xyona-only --summary-only`
  passed after adding the graph-native spectral-to-spectral PVOC chain; 45
  tests, 2659 passes, 0 failures.
- `CDP8`: Windows Debug configure and `pvoc` target build passed before
  generating the PVOC fixture assets.
- `xyona-cdp-pack`: full `cmake --build --preset windows-msvc-debug` passed
  after adding fixture-backed PVOC synthesis-length coverage.
- `xyona-cdp-pack`: full `ctest --preset windows-msvc-debug --output-on-failure`
  passed after adding fixture-backed PVOC synthesis-length coverage; 19/19
  tests.
- `xyona-lab`: `cmake --build --preset windows-dev --target xyona_lab_tests --config Debug`
  passed after updating PVOC materialized-length expectations.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Offline Pack Processor Client" --xyona-only --summary-only`
  passed after updating PVOC synth length expectations; 9 tests, 1042 passes,
  0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="AudioEngineManager" --xyona-only --summary-only`
  passed after updating graph-native PVOC render length expectations; 45 tests,
  2657 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only`
  passed after fixture-backed PVOC synthesis-length coverage; 13 tests, 354
  passes, 0 failures.
- `xyona-cdp-pack`: `cmake --build --preset windows-msvc-debug` passed after
  adding the graph-native PVOC typed data chain.
- `xyona-cdp-pack`: `ctest --preset windows-msvc-debug --output-on-failure`
  passed after adding the graph-native PVOC typed data chain; 19/19 tests.
- `xyona-lab`: `cmake --build --preset windows-dev --target xyona_lab_tests --config Debug`
  passed after adding the graph-native PVOC typed data chain.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Operator Process Metadata" --xyona-only --summary-only`
  passed after adding typed-data host-contract metadata; 11 tests, 102 passes,
  0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only`
  passed after adding typed PVOC descriptor coverage; 13 tests, 354 passes,
  0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug .\build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="AudioEngineManager" --xyona-only --summary-only`
  passed after adding graph-native PVOC render coverage; 45 tests, 1761 passes,
  0 failures.
- `xyona-core`: `cmake --build build/macos-clang-debug --target test_offline_session_abi -j 6`
  passed after adding Offline Session ABI v3 typed data input.
- `xyona-core`: `ctest --test-dir build/macos-clang-debug -R offline_session_abi_tests --output-on-failure`
  passed after adding Offline Session ABI v3 typed data input; 1/1 test.
- `xyona-core`: `cmake --build build/macos-clang-debug -j 6` passed after
  adding Offline Session ABI v3 typed data input.
- `xyona-core`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed after adding Offline Session ABI v3 typed data input; 8/8 tests.
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug --target test_cdp_pvoc_analysis test_cdp_spectral_contract test_cdp_offline_session_conformance test_cdp_descriptor_metadata xyona_pack_cdp_ops -j 6`
  passed after adding `cdp.pvoc.synth`.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug -R "cdp_pvoc_analysis_tests|cdp_pvoc_golden_tests|cdp_spectral_contract_tests|cdp_offline_session_conformance_tests|cdp_descriptor_metadata_tests" --output-on-failure`
  passed after adding `cdp.pvoc.synth`; 5/5 tests.
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug -j 6` passed after
  adding `cdp.pvoc.synth`.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed after adding `cdp.pvoc.synth`; 19/19 tests.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests xyona_lab_cdp_offline_smoke -j 6`
  passed after adding data-artifact-to-audio rendering.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="Offline Pack Processor Client" --summary-only --xyona-only`
  passed after adding `cdp.pvoc.synth` host coverage; 9 tests, 1170 passes,
  0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  passed after adding `cdp.pvoc.synth` descriptor coverage; 12 tests, 325
  passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_cdp_offline_smoke`
  passed after adding the PVOC analysis -> synthesis smoke.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --summary-only --xyona-only`
  passed after adding data-artifact-to-audio rendering; 1197 tests, 945272
  passes, 0 failures.
- Remote CI on 2026-04-29 could not run code. Core run `25094646197`, Pack run
  `25094646072`, and Lab run `25094646144` failed before job steps started;
  the Windows and macOS jobs all reported empty `steps` arrays, matching the
  existing GitHub Actions billing/spending-limit blocker.
- `xyona-core`, `xyona-cdp-pack`, and `xyona-lab`: `git diff --check` passed
  before the PVOC synth data input commits.
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug --target test_cdp_pvoc_analysis test_cdp_spectral_contract test_cdp_offline_session_conformance test_cdp_descriptor_metadata xyona_pack_cdp_ops -j 6`
  passed after adding `cdp.pvoc.anal`.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug -R "cdp_pvoc_analysis_tests|cdp_pvoc_golden_tests|cdp_spectral_contract_tests|cdp_offline_session_conformance_tests|cdp_descriptor_metadata_tests" --output-on-failure`
  passed after adding `cdp.pvoc.anal`; 5/5 tests.
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug -j 6` passed after
  adding `cdp.pvoc.anal`.
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug --output-on-failure`
  passed after adding `cdp.pvoc.anal`; 19/19 tests.
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests -j 6`
  passed after adding `cdp.pvoc.anal` host coverage.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="Offline Pack Processor Client" --summary-only --xyona-only`
  passed after adding `cdp.pvoc.anal`; 8 tests, 134 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_tests --test="CDP Pack Canvas Smoke" --summary-only --xyona-only`
  passed after adding `cdp.pvoc.anal`; 11 tests, 305 passes, 0 failures.
- `xyona-lab`: `XYONA_OPERATOR_PACK_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-cdp-pack/build/macos-clang-debug build/macos-dev/tests/xyona_lab_cdp_offline_smoke`
  passed after adding `cdp.pvoc.anal`.
- `xyona-lab`: full `build/macos-dev/tests/xyona_lab_tests --summary-only --xyona-only`
  had one unrelated `TransportContracts / Double-buffer snapshot preserves
  invariants` failure with the CDP pack path unset; the targeted
  `TransportContracts` rerun passed with 7 tests, 18 passes, 0 failures.
- Remote CI on 2026-04-29 could not run code. Pack run `25092257976` and Lab
  run `25092266656` failed before job steps started; both Windows and macOS jobs
  reported empty `steps` arrays, matching the existing GitHub Actions
  billing/spending-limit blocker.
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
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  passed after adding store-level staleness/status tracking.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  passed after adding store-level staleness/status tracking; 4 tests, 88
  passes, 0 failures.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  passed after adding materialized asset orphan cleanup.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  passed after materialized asset orphan cleanup; 5 tests, 112 passes, 0
  failures.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  passed after adding materialized WAV asset file fingerprints.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  passed after materialized WAV asset file fingerprints; 5 tests, 123 passes,
  0 failures.
- `xyona-lab`: `git diff --check` passed before committing
  `lab.audio_file_in` source dependency fingerprints.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  passed after adding `lab.audio_file_in` source dependency fingerprints.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --summary-only --xyona-only`
  passed after adding `lab.audio_file_in` source dependency fingerprints; 36
  tests, 537 passes, 0 failures. The CDP pack subtest was skipped because
  `XYONA_OPERATOR_PACK_PATH` was unset.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Canvas Param Persistence" --summary-only --xyona-only`
  passed after adding string parameter persistence; 14 tests, 88 passes, 0
  failures.
- Full Lab CTest was intentionally not run for the focused
  `lab.audio_file_in` source dependency fingerprint slice.
- `xyona-lab`: `git diff --check` passed before committing the materialized
  audio status surface.
- `xyona-lab`: `XYONA_CORE_PATH=/Users/haraldpliessnig/Github/XYONA/xyona-core cmake --build build/macos-dev --target xyona_lab_tests`
  passed after adding the materialized audio status surface.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  passed after adding the status summary coverage; 6 tests, 145 passes, 0
  failures.
- Full Lab CTest was intentionally not run for the focused Gate C status-surface
  slice.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="LayerPlayerHostAdapter" --summary-only --xyona-only`
  passed after adding the materialized layer player adapter; 4 tests, 37
  passes, 0 failures.
- `xyona-lab`: `XYONA_RT_ALLOC_TRAP=2 build/macos-dev/tests/xyona_lab_tests --test="RT Safety Smoke" --summary-only --xyona-only`
  passed after adding the materialized layer player adapter and graph path; 2
  tests, 4 passes, 0 failures.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager" --summary-only --xyona-only`
  passed after routing materialized clips into the realtime graph; 40 tests,
  586 passes, 0 failures. The CDP whole-file subtest was skipped because
  `XYONA_OPERATOR_PACK_PATH` was unset.
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="Materialized Audio Store" --summary-only --xyona-only`
  passed after Gate D graph routing; 6 tests, 145 passes, 0 failures.
- Full Lab CTest was intentionally not run for the Gate D LayerPlayer slices;
  the focused test set covered adapter behavior, store behavior, graph
  integration, stale-clip diagnostics, and RT allocation smoke.

## Open Risks

- `MaterializedAudioStore` now participates in normal Project save/open/save-as,
  and Project save now removes orphaned materialized audio assets from the
  store-owned asset directory.
- Materialized layers now carry store-level dependency signatures, the
  AudioEngineManager materialize path computes current graph/job/parameter
  signatures, and `lab.audio_file_in` source files plus materialized WAV assets
  are fingerprinted. Future spectral settings, additional source/asset types,
  and pack binary identity beyond descriptor/artifact versions are still open as
  future artifact paths appear.
- `Missing` and `Stale` states are persisted, diagnosable, and visible through
  the BottomBar status surface. A richer materialized clip/render-queue UI is
  still a later product UX decision.
- Materialized clips are consumed by the realtime LayerPlayer path for valid
  resident audio. Later UX work still needs to decide how users place, inspect,
  and re-render those clips in a richer product surface.
- Same-length whole-file CDP operators now execute and materialize through the
  production Offline Session ABI. The whole-buffer prototype remains a
  reference/test helper and is not exported by the normal pack build.
  Length-changing, PVOC/spectral, multi-output, and long-running CDP operators
  must use the implemented/tested Offline Session ABI.
- Typed spectral/PVOC artifacts must not be routed through audio buffers.
  `cdp.pvoc.anal` now produces real PVOC analysis artifacts and public
  `cdp.pvoc.synth` consumes them through Offline Session ABI v3. The first two
  file-backed CDP8 PVOC analysis/synthesis fixtures now lock selected bins,
  synthesized samples, and synthesis length for impulse/sine cases. The first
  graph-native Canvas/HQ PVOC analysis -> synthesis chain and the first
  technical spectral-to-spectral PVOC identity chain are implemented locally;
  generalized typed graph / persisted-handle support and broader CDP8 golden
  fixture matrices are still required before wider spectral workflows.
