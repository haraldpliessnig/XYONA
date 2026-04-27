# CDP8 Offline And Spectral Rewrite Roadmap

Last updated: 2026-04-27

## Purpose

This roadmap defines the technical work needed to make XYONA a clean host for
CDP8-style offline programs and spectral/PVOC workflows.

The goal is not to bolt CDP8 behavior onto the current block callback. The goal
is to extend the existing XYONA architecture so that CDP programs can be
rewritten as native, deterministic, testable XYONA operators while preserving the
repository boundaries:

- `xyona-core` owns host-agnostic runtime contracts and pack APIs.
- `xyona-lab` owns graph planning, render jobs, UI, project state, files, and
  offline/HQ execution.
- `xyona-cdp-pack` owns CDP algorithms, CDP descriptors, CDP data formats, and
  pack adapters.
- `CDP8` remains reference code and validation source.

## Executive Summary

The existing HQ renderer is the correct foundation, but it is not yet a complete
CDP program host.

Current state:

- Lab has an offline/HQ renderer that builds an HQ graph and renders it block by
  block into a known render range.
- Core pack ABI v2 supports block-based audio operators with fixed `num_samples`
  per process call.
- Core currently exposes a prototype whole-buffer offline C ABI, currently
  named `offline_whole_buffer_prototype`, for the first simple same-length
  whole-file query/process slice.
- The CDP pack has the first dynamic pack, descriptor, buffer, validation, and
  block-safe operator infrastructure.
- The CDP pack already classifies future process shapes such as whole-file,
  length-changing, analysis-output, multi-output, and generator operators.
- The first whole-file, length-preserving CDP slice exists:
  `cdp.modify.loudness_normalise` performs a full-file peak scan through the
  prototype whole-buffer offline ABI and Lab can materialize the result as an
  RT-reentry-safe audio artifact.
- Lab has a first `MaterializedAudioStore` for materialized layer/clip metadata,
  in-memory resident audio, WAV-backed asset persistence APIs, a ProjectState
  manifest anchor, and automatic Project save/open/save-as orchestration via a
  project-local `*.xyona-assets/materialized_audio` directory. The store also
  persists a per-layer dependency signature plus `Valid`, `Rendering`, `Stale`,
  `Missing`, and `Failed` states and clears resident audio when a layer becomes
  stale or missing. The AudioEngineManager materialize path now feeds those
  signatures with current render dependencies from the RenderJob, render range,
  sample rate, graph plan, wires, operator descriptor versions, parameters,
  tempo, and grid context. Project save now also removes orphaned materialized
  audio files and does not promote persisted stale/missing/failed material back
  to valid RT-playable audio just because an old WAV file still exists.
  Materialized WAV asset files now also carry content fingerprints, so an
  externally changed materialized asset reloads as `Stale` / `Re-render
  required` instead of becoming RT-playable. `lab.audio_file_in` source paths
  are now stored as string parameters and their source WAV content fingerprints
  feed the materialized render dependency signature.

Missing state:

- Offline Session ABI implemented and tested with streaming, progress, and
  cancellation. This is the first production offline pack contract.
- Remaining production persistence for materialized assets: future spectral
  settings and a dedicated UI surface for re-render state.
- Realtime LayerPlayer consumption of materialized clips.
- Output length negotiation for length-changing CDP programs through the Offline
  Session ABI.
- A typed analysis/spectral data model instead of pretending PVOC/PVX is audio.
- Lab graph planning rules for offline-only and non-audio-producing nodes.
- Golden reference tooling at CDP8 family scale.
- Robust Windows pack test execution and CI coverage.

Conclusion:

This is cleanly achievable by extending the current HQ renderer and pack ABI. It
should not be solved by special-case hacks inside individual CDP operators.
The current whole-buffer offline ABI is a prototype/reference bridge for the
existing same-length whole-file slice. It is not the release production offline
contract for length-changing, PVOC/spectral, multi-output, or long-running CDP
work.

## Why This Architecture Is Required

CDP8 was historically built around programs, files, and analysis artifacts.
XYONA is built around a realtime-safe graph plus an HQ/offline render path. Those
two models can fit together cleanly, but only if each layer keeps the right
responsibility.

### Why The Existing HQ Renderer Is The Right Base

The HQ renderer already provides the properties CDP needs from a host:

- it is separate from the realtime audio callback
- it can render deterministically outside device timing pressure
- it owns render jobs, progress, cancellation, file output, and graph snapshots
- it can use the Lab graph and project model instead of introducing a second
  hidden CDP host

Therefore the correct direction is to extend the HQ renderer with offline
program execution. Replacing it or bypassing it would duplicate scheduling,
render state, project integration, and asset handling.

### Why Realtime Must Only Consume Finalized Results

The realtime graph must remain predictable and callback-safe. It must not wait
for file-scale analysis, allocate large spectral buffers, finalize CDP programs,
or discover output length while audio is running.

The safe model is:

```text
HQ/CDP render computes the result
Lab materializes the result as an asset, clip, cache, or frozen segment
Realtime consumes that finalized result like ordinary source material
```

This keeps the RT engine simple and robust. CDP can still do complex work, but
the complexity finishes before the result crosses back into the realtime graph.

### Why Block Processing Is Not Enough

The current pack process callback receives a fixed number of samples and writes
the same block-sized output. That is enough for gain, mirror, narrow, filters,
and many ordinary audio effects.

Many CDP8 programs are different:

- some require the entire file before producing any correct output
- some produce a different length than their input
- some produce analysis data instead of audio
- some transform spectral data that is not time-domain audio
- some emit multiple artifacts

If those tools are forced into a normal block callback, XYONA would either
truncate results, hide latency/tail behavior, fake data types, or make operators
stateful in fragile ways.

### Why Output Length Must Be Negotiated

Lab's current HQ jobs can already render arbitrary user-selected durations. That
is different from an operator deciding its own output duration.

The missing contract is:

```text
given this input, these parameters, and this analysis state,
what output length will this operator produce?
```

Without that contract, length-changing CDP programs cannot be placed, cached,
rendered to file, or re-entered into RT reliably.

### Why Spectral Data Needs A Real Type

PVOC/PVX data is not audio. It has frames, bins, windows, hops, magnitudes,
phases/frequencies, and analysis metadata. Passing it through audio ports would
make the first demo easier but would corrupt graph validation, UI behavior,
storage, and future operators.

Spectral workflows need either typed graph ports, Lab asset handles, or both.
The pack should own the spectral data model and algorithms; Lab should own where
those artifacts live and how users manage them.

### Why The Pack Boundary Matters

The CDP pack is the separately licensed, dynamically loadable component. CDP
algorithms and CDP-specific file/data formats belong there. Lab should not link
CDP algorithms directly, and Core should not learn Lab project semantics.

The clean boundary is:

- Core defines generic host/pack contracts.
- Lab schedules work, stores assets, and presents UI.
- CDP pack implements CDP algorithms and maps them to the contracts.

## Existing Architecture Documents Considered

This roadmap must align with the existing Lab architecture documents, especially
the HQ/RT split.

Primary documents:

- `xyona-lab/docs/architecture/HQ_RT.md`
- `xyona-lab/docs/architecture/PDC.md`
- `xyona-lab/docs/architecture/PURE_DATA_NODES.md`
- `xyona-lab/docs/architecture/HIGH_END_ANALYZER_ARCHITECTURE_v2_2.md`
- grid and UI architecture ADRs in `xyona-lab/docs/architecture`

Important constraints from those documents:

- `HQ_RT.md` defines XYONA as HQ-first: HQ/offline rendering is the primary
  production path, while RT is preview, monitoring, and playback of baked
  material.
- `HQ_RT.md` already identifies the missing bridge work:
  - Phase 5: persistent renderer/render-target management
  - Phase 6: RT/HQ bridge nodes
  - Phase 7: `AudioLayer`, `LayeredClip`, `LayerPool`, and `ClipStore`
- Therefore CDP RT re-entry should reuse and complete that architecture instead
  of inventing a separate CDP-only cache model.
- `PDC.md` establishes the same design principle for latency: graph/build-time
  planning, not runtime hacks. CDP length and tail behavior should follow that
  pattern.
- `PURE_DATA_NODES.md` states that Canvas payloads are UI/metadata only and must
  not own DSP state. CDP execution state belongs in adapters, render jobs,
  assets, or pack sessions, not Canvas node payloads.
- `HIGH_END_ANALYZER_ARCHITECTURE_v2_2.md` reinforces the RT rule: RT must avoid
  locks, allocations, file I/O, FFT, LUFS, and unbounded work. CDP/PVOC work
  must stay outside RT and re-enter only as finalized data.
- Grid runtime ADRs reinforce the compiled-runtime pattern: expensive planning
  and semantic evaluation should happen before RT execution.

Architectural consequence:

The CDP roadmap is not a replacement for `HQ_RT.md`. It is an extension that
adds CDP-specific offline program execution and spectral data semantics to the
existing HQ-first architecture.

## Hard Gate System

These gates supersede the older informal phase ordering whenever there is a
conflict. A later CDP operator family may start only when every listed
dependency gate is complete.

### Gate A - Constrain Prototype Whole-Buffer Offline ABI

The current whole-buffer offline ABI, currently named
`offline_whole_buffer_prototype`, is a temporary prototype/reference bridge. It
remains valid only for bounded same-length, whole-buffer operators such as the
current `cdp.modify.loudness_normalise` reference slice while the production
Offline Session ABI is being built.

Allowed on the prototype:

- deterministic same-length whole-file operators
- bounded test/reference renders
- operators whose input and output can reasonably be held in memory

Forbidden on the prototype:

- length-changing operators
- PVOC/spectral analysis or synthesis
- multi-output or multi-file operators
- production-scale long-file CDP workflows

Exit criteria:

- Roadmap/report describe the current whole-buffer ABI as a temporary
  prototype/reference ABI.
- New CDP inventory entries for length-changing, PVOC/spectral, or multi-output
  work are blocked unless they target the production Offline Session ABI.
- Before release, the current `cdp.modify.loudness_normalise` slice is ported to
  the Offline Session ABI and the public prototype ABI surface is removed or
  explicitly downgraded to an internal test helper.

### Gate B - Converge `MaterializedAudioStore` With `HQ_RT.md` Phase 7

`MaterializedAudioStore` is the current concrete implementation line for the
`HQ_RT.md` Phase 7 layer/clip store. Do not build a parallel `AudioLayer`,
`LayerPool`, or `ClipStore` system beside it unless this decision is explicitly
reversed.

Exit criteria:

- `HQ_RT.md` states that `MaterializedAudioStore` is the active Phase 7 store
  implementation.
- Any future rename/refactor preserves one store lineage and one manifest/asset
  contract.

### Gate C - Production Persistence And Staleness

Normal project save/open orchestration, store-level staleness state, and the
AudioEngineManager render-dependency signatures now exist. Cleanup/orphan
policy, `lab.audio_file_in` source file fingerprints, and materialized WAV asset
file fingerprints exist. Materialized assets are not production-complete until
stale/missing UI states exist.

Required behavior:

- stable project asset directory convention
- save/open/save-as lifecycle wiring
- relative asset paths in project files
- missing asset diagnostics
- orphan cleanup policy
- dependency signature for each materialized layer/clip
- stale detection when source audio, producer operator, parameters, sample rate,
  render range, pack algorithm version, spectral settings, or dependent assets
  change
- user-visible state such as `Valid`, `Rendering`, `Stale`, `Missing`,
  `Failed`, or `Re-render required`
- RT playback must not silently treat stale or missing material as valid

Exit criteria:

- A saved project can reload materialized audio assets without manual API calls.
- A changed dependency marks the materialized clip stale and exposes a
  re-render-required state.
- Missing asset behavior is deterministic and diagnosable.
- External `lab.audio_file_in` source file changes and materialized WAV asset
  file changes are included in stale checks.

### Gate D - Realtime LayerPlayer Consumption

The RT graph must be able to consume a materialized clip as ordinary source
material.

Required behavior:

- no disk I/O on the audio thread
- no offline pack calls on the audio thread
- resident buffer or pre-opened asset handle prepared outside RT
- graph rebuild sees the clip as a normal RT-safe source
- clear behavior for missing or stale materialized clips

Exit criteria:

- A headless test proves: offline render -> materialized clip -> RT LayerPlayer
  playback.
- The RT playback path performs no blocking file or pack work in the callback.

### Gate E - Implemented Offline Session ABI

This gate is not satisfied by a design document. It requires implementation and
tests.

This is the first production offline pack contract. Its internal C ABI should be
versioned, for example as session API v1, but it should not be framed as a
second production generation replacing a released v1.

Required behavior:

- session lifecycle
- streaming input blocks
- finish/finalize step
- output length preflight or discovery
- read-output-block or host asset output
- progress reporting through a standardized ABI path
- cancellation through a standardized ABI path
- host scratch/asset policy hooks or equivalent memory-spooling contract

Exit criteria:

- Core exposes the Offline Session ABI.
- CDP pack implements one reference operator that exercises the full lifecycle.
- Lab/Core/Pack tests prove normal completion, progress reporting, and
  cancellation.
- The current `cdp.modify.loudness_normalise` reference slice is ported onto the
  session lifecycle or the remaining prototype path is explicitly internal-only.

### Gate F - CI Baseline

Local manual verification is not enough for this branch.

Exit criteria:

- GitHub Actions or equivalent CI runs at least Core, Pack, and Lab smoke tests
  on macOS Clang and Windows MSVC.
- Linux GCC/Clang is planned next but does not block the first baseline.
- CDP pack runtime discovery is covered by CI or a documented equivalent smoke
  command.

### Gate G - Length-Changing Audio

Hard dependencies:

- Gate C
- Gate D
- Gate E

Exit criteria:

- Synthetic length-changing reference operator passes through the Offline
  Session ABI.
- Lab allocates/materializes the actual negotiated output length.
- RT consumes the resulting materialized clip without truncation or hidden
  padding.

### Gate H - PVOC/Spectral

Hard dependencies:

- Gate E
- typed data ports or asset handles
- CDP8 golden fixture harness for PVOC/PVX behavior

PVOC/spectral work must not be started on the prototype whole-buffer offline
ABI.

Exit criteria:

- PVOC analysis data is represented as typed data or a host asset, not audio.
- Window, hop, magnitude/frequency, phase-unwrapping/reconstruction, and
  serialization policies are explicit.
- CDP8-compatible golden tests exist before real spectral families are ported.

### Gate I - Generator Edge Case

Before the first CDP generator operator is added, Lab must have an explicit test
for a `processShape=generator`, `abiV2Support=direct` pack operator with no
upstream audio input.

Exit criteria:

- RT and HQ graph building both handle the generator shape deliberately.
- Offline render behavior is covered for null-upstream generator nodes.

## Current Architecture Baseline

### Lab HQ Renderer

Relevant implementation:

- `xyona-lab/src/app/lab/audio/engine/OfflineRenderEngine.h`
- `xyona-lab/src/app/lab/audio/engine/OfflineRenderEngine.cpp`
- `xyona-lab/src/app/lab/audio/engine/AudioEngineManager.cpp`

Current behavior:

- `RenderJob` defines `startSeconds`, `endSeconds`, `sampleRate`, `blockSize`,
  `numChannels`, `destinationFile`, and `hqGraphId`.
- Lab builds an HQ graph through `OfflineGraphBuilder`.
- The offline renderer prepares a dedicated `AudioGraphProcessor`.
- It renders blocks until the known internal sample count is complete.
- It supports progress, cancellation, pre-block parameter ticks, file output
  finalization, offline bus capture, signal capture, and dedicated offline graph
  state.

This is the right foundation for CDP because it already separates HQ rendering
from the realtime audio device path.

Current limitation:

- The renderer assumes that the render range determines the primary output
  length.
- The graph is still executed as fixed-size audio blocks.
- A node cannot currently demand "give me the full input, then finalize, then
  produce an output whose length I determine".
- A node cannot currently emit typed non-audio analysis data as a first-class
  graph value.

### Core Pack ABI v2

Relevant implementation:

- `xyona-core/include/xyona/api/packs_v2.h`
- `xyona-core/src/core/packs_api.cpp`

Current behavior:

- Operator descriptors expose `can_realtime`, `can_hq`, latency, audio ports,
  params, and `meta_json`.
- Operators implement `prepare`, `reset`, `process`, and parameter updates.
- `process` receives:

```text
inputs
outputs
num_samples
params
mode
```

This is suitable for block-stable audio operators.

Current limitation:

- No offline session lifecycle.
- No output length query.
- No finalization callback for pack operators.
- No typed data ports.
- No asset handles.
- No multi-file/multi-output contract.
- No analysis-output contract.
- No way to represent PVOC/PVX as a graph-native value.

### CDP Pack

Relevant implementation:

- `xyona-cdp-pack/src/runtime/cdp_process_contract.h`
- `xyona-cdp-pack/src/runtime/cdp_whole_file_accumulator.h`
- `xyona-cdp-pack/src/runtime/cdp_audio_buffer.h`
- `xyona-cdp-pack/src/operators/*`
- `xyona-cdp-pack/specs/*`

Current behavior:

- Dynamic CDP pack builds and loads.
- First descriptors and registration helpers exist.
- Audio buffer conversion and sanitization exist.
- CDP process shape classification exists.
- Whole-file accumulation helper exists for future HQ-only operators.
- Golden comparison helpers exist.
- Breakpoint and dB/gain helpers exist.
- First block-safe CDP8-derived operators exist.

Current limitation:

- Whole-file helpers are pack-local utilities, not a host execution contract.
- Length-changing operators are intentionally not registerable through current
  ABI v2.
- Analysis-output and multi-output shapes are classified but not executable.
- PVOC/PVX data model is not implemented.

## Required Target Architecture

The target architecture should be layered like this:

```text
Lab Render Job / Project / UI
    |
    v
Lab HQ Graph Planner
    |
    +-- block audio execution path
    |
    +-- offline program execution path
            |
            v
Core pack offline/session ABI
            |
            v
CDP pack operator adapter
            |
            v
CDP algorithm / data model / validation
```

The existing Lab HQ renderer remains the execution host. It gains additional
planning and execution modes for offline-only program nodes.

## RT Re-Entry Contract

Offline CDP processing may be complex internally, but its result must re-enter
the realtime world as a normal, stable Lab runtime value.

This is the most important boundary:

```text
CDP/HQ/offline execution
    -> materialized render result
    -> normal RT-safe Lab source/value
    -> realtime graph consumes only the materialized result
```

The realtime engine must not call whole-file CDP operators, wait for spectral
analysis, allocate large analysis buffers, or depend on a length-changing
operator while the audio callback is running.

Allowed RT re-entry forms:

- rendered audio clip or buffer with a known sample length
- rendered file asset referenced by a Lab source node
- frozen/bounced graph segment
- generated analysis asset that is consumed only by RT-safe readers
- cached spectral result after it has been converted back to audio

Required guarantees:

- The materialized result has a stable sample rate, channel count, length, and
  timestamp/placement policy.
- RT graph rebuilds see the result as ordinary source material, not as an active
  offline computation.
- Stale offline results are invalidated when source audio, parameters, sample
  rate, spectral settings, or dependent assets change.
- If an offline result is missing or stale, Lab must show that state and avoid
  silently feeding invalid data into RT.
- Re-entry must be atomic from the RT graph perspective: the realtime graph
  observes either the old valid result or the new completed result.
- Re-entry should use the existing/planned `HQ_RT.md` layer model:
  `AudioLayer`, `LayeredClip`, `LayerPool`, `ClipStore`, and RT/HQ bridge nodes.
  See Gate B: the concrete implementation line is `MaterializedAudioStore`; the
  older names remain architecture terms, not parallel store systems.

This reduces implementation risk because CDP-specific complexity stays in the
HQ/offline layer. The RT engine only needs robust consumption of finalized
artifacts.

## Processing Shape Contract

XYONA should explicitly support these operator shapes:

1. Block length-preserving audio
2. Block stateful length-preserving audio
3. Whole-file length-preserving audio
4. Whole-file length-changing audio
5. Generator
6. Analysis data output
7. Typed data transform
8. Multi-output or multi-file output

Each shape must define:

- realtime eligibility
- HQ eligibility
- input acquisition model
- output length model
- output data type
- cancellation behavior
- progress behavior
- memory/spooling policy
- graph scheduling constraints
- UI availability and error behavior

## Output Length Model

The renderer and pack API need a formal output length model:

1. `same_as_input`
   - Output sample count equals selected input sample count.
2. `fixed_tail`
   - Output length is input length plus a known tail.
3. `param_dependent`
   - Output length can be computed from parameters before execution.
4. `analysis_dependent`
   - Output length is only known after an analysis/preflight/finalize step.
5. `no_audio_output`
   - Operator produces analysis/text/spectral data, not audio.
6. `multi_output`
   - Operator produces multiple outputs with possibly independent lengths.

Lab must never silently truncate a length-changing CDP operator to the original
render range.

## Typed Data Model

CDP spectral workflows require typed graph values beyond audio.

Minimum required data classes:

- `audio_buffer`
- `breakpoint_table`
- `text_table`
- `spectral_analysis`
- `pvoc_analysis`
- `analysis_report`
- `file_collection` or `multi_artifact`

For the first spectral slice, `pvoc_analysis` is the critical type.

PVOC/PVX data must include:

- sample rate
- source length
- channel count
- FFT size
- analysis window
- synthesis window policy
- hop size
- frame count
- bin count
- magnitude representation
- phase/frequency representation
- format version
- provenance metadata

Spectral operators must not fake analysis-file semantics through normal audio
ports.

## Asset And Storage Policy

Lab owns project assets and file decisions. The CDP pack owns pure data formats
and algorithms.

Required policies:

- Small analysis data can be kept in memory.
- Large analysis data needs a disk-backed scratch/cache option.
- Project persistence must decide whether analysis artifacts are embedded,
  referenced, regenerated, or stored beside the project.
- Pack operators should receive typed buffers or host asset handles, not raw UI
  file picker state.
- Temporary render artifacts must be cancellable and cleaned up.

## Roadmap

### Phase 0 - Verification Stabilization

Purpose:

Make the current pack infrastructure reliably testable before adding more
execution modes.

Tasks:

- Fix `xyona-cdp-pack` Windows test scripts:
  - pass the correct CTest configuration, for example `-C Debug`
  - ensure `xyona_core.dll` is available through `PATH` or copied beside tests
  - fail the script when CTest reports tests as "Not Run"
- Add a pack smoke command that validates:
  - build
  - unit tests
  - pack loading through Core
  - environment discovery through `XYONA_OPERATOR_PACK_PATH`
- Add CI matrix planning for:
  - Windows MSVC Debug
  - macOS Clang Debug
  - Linux Clang or GCC Debug

Exit criteria:

- Pack tests are green locally on Windows without manual `PATH` edits.
- CTest cannot show `0% tests passed` while the script prints success.
- Current block-safe CDP operators still load in Lab.

Primary repos:

- `xyona-cdp-pack`
- `xyona-core`

### Phase 1 - Formal Process Shape Metadata

Purpose:

Move process shape metadata from pack-local intent into a host-visible contract.

Tasks:

- Define a stable descriptor schema for process shape metadata.
- Decide whether the first transport is:
  - structured `meta_json` in ABI v2, or
  - a new ABI revision with typed fields.
- Include:
  - process shape
  - realtime/HQ eligibility
  - whole-file requirement
  - output length model
  - typed output kind
  - tail/latency semantics
  - multi-output flags
- Teach Core pack loading to preserve and expose this metadata.
- Teach Lab descriptor consumption to read and validate this metadata.
- Keep invalid combinations unrepresentable or rejected:
  - realtime plus whole-file-required
  - length-changing without output length model
  - analysis-output through audio-only ports

Exit criteria:

- Lab can inspect a pack operator and know whether it is block, whole-file,
  length-changing, analysis-output, or multi-output.
- Unsupported operators can be shown as unavailable with a clear reason instead
  of silently behaving like normal audio nodes.

Primary repos:

- `xyona-core`
- `xyona-lab`
- `xyona-cdp-pack`

### Phase 2 - Offline Session ABI

Purpose:

Add a pack execution mode for operators that need the full input or a finalizing
pass.

Candidate API shape:

```text
create
prepare
begin_offline_session(session_desc)
append_input_block(port, channels, num_samples, absolute_sample)
finish_input()
preflight_output_length()
finalize()
read_output_block(port, channels, offset, num_samples)
destroy_offline_session
```

Alternative:

```text
execute_offline(request, response)
```

The lifecycle API is more flexible for progress, cancellation, memory control,
and streaming.

Tasks:

- Define C ABI structs with explicit `struct_size` versioning.
- Add error/status codes for:
  - invalid shape
  - unsupported mode
  - cancelled
  - allocation failure
  - invalid port/data type
  - output length unavailable
- Add host callbacks for:
  - cancellation polling
  - progress reporting
  - scratch allocation or asset creation
  - logging
- Implement Core-side adapter from the C ABI to host runtime objects.
- Implement one reference operator in the CDP pack or a dedicated test pack that
  exercises the full lifecycle.
- Add tests for:
  - normal completion
  - progress reporting
  - cancellation before input finishes
  - cancellation during finalize/output
  - output length preflight/discovery

Exit criteria:

- The Offline Session ABI is implemented in Core and consumed by at least one
  pack.
- A reference operator can consume streamed input, finalize, and return output
  through the offline session path.
- The same operator is not allowed in realtime processing.
- The current `cdp.modify.loudness_normalise` reference slice is ported onto the
  session lifecycle, or the remaining prototype whole-buffer path is explicitly
  internal-only.
- Cancellation and progress are standardized and asserted in tests.
- Length-changing, PVOC/spectral, multi-output, and long-running CDP work remain
  blocked until this gate is complete.

Primary repos:

- `xyona-core`
- `xyona-cdp-pack`

### Phase 3 - Lab HQ Planner Integration

Purpose:

Teach Lab that some HQ graph nodes are offline programs, not ordinary block
processors, while staying aligned with the existing `HQ_RT.md` architecture.

Tasks:

- Extend `OfflineGraphBuilder` or adjacent planning code to classify nodes by
  process shape.
- Split the HQ render plan into execution regions:
  - ordinary block graph regions
  - whole-file program nodes
  - typed data transform nodes
  - final audio-producing regions
- Add validation:
  - reject offline-only nodes in realtime plans
  - reject unsupported data-type edges
  - reject unknown output length where the destination requires a fixed length
- Define materialization and RT re-entry for offline results:
  - rendered clip/buffer result
  - frozen/bounced graph segment
  - Lab asset handle
  - atomic swap into RT-visible source state
- Map CDP materialization onto the existing/planned `HQ_RT.md` Phase 5-7 model:
  - persistent renderer or render-target metadata
  - `MaterializedAudioStore` as the concrete Phase 7 layer/clip store line
  - `LayerPlayerNode` or equivalent RT-safe playback node
- Do not add a second parallel `AudioLayer` / `LayerPool` / `ClipStore`
  implementation beside `MaterializedAudioStore` without an explicit
  architecture reversal.
- Define scheduling for simple vertical slices:
  - source audio -> whole-file CDP node -> audio sink
  - source audio -> length-changing CDP node -> audio sink
- Preserve existing behavior for all current block-based graphs.

Exit criteria:

- Existing HQ renders remain bit-stable or within current tolerance.
- Lab can execute one whole-file length-preserving synthetic pack node.
- Lab can materialize that node's result as an RT-safe source/value.
- Lab can report unsupported whole-file/typed nodes clearly instead of trying to
  process them as block nodes.

Primary repos:

- `xyona-lab`
- `xyona-core`

### Phase 4 - First Real Whole-File CDP Operator

Purpose:

Prove that the offline session path can run an actual CDP-style algorithm.

Recommended first slice:

- Choose a whole-file length-preserving CDP8-derived process with limited data
  dependencies.
- Avoid spectral/PVOC at this phase.
- Avoid length-changing at this phase unless Phase 3 is already robust.

Tasks:

- Update CDP inventory entry before implementation.
- Implement algorithm in `xyona-cdp-pack`.
- Register descriptor as HQ-only and whole-file required.
- Add CDP8 golden fixture.
- Add pack unit tests.
- Add Core pack execution test.
- Add Lab headless smoke test through `XYONA_OPERATOR_PACK_PATH`.

Exit criteria:

- The operator is impossible to run in realtime.
- The operator executes through Lab HQ render.
- Output matches CDP8 reference within documented tolerance.
- Existing block-safe operators are unaffected.

Primary repos:

- `xyona-cdp-pack`
- `xyona-core`
- `xyona-lab`
- `CDP8` as read-only reference

### Phase 5 - Length-Changing Audio

Purpose:

Support CDP programs whose output length differs from input length and can still
re-enter RT as ordinary baked material.

Hard prerequisites:

- Gate C: production persistence and staleness
- Gate D: realtime LayerPlayer consumption
- Gate E: implemented and tested Offline Session ABI

Tasks:

- Implement `query_output_length` for:
  - fixed tail
  - parameter-dependent length
  - analysis-dependent length after preflight/finalize
- Update Lab render buffer/file allocation rules.
- Define where the resulting audio is placed when it re-enters RT:
  - replace selected region
  - create new rendered clip
  - create frozen graph segment
  - write explicit file asset
- Prefer the `HQ_RT.md` layer/clip path for RT playback instead of special CDP
  playback logic.
- Update progress calculation for output lengths that are not known at job
  creation.
- Define how downstream graph timing works after a length-changing node.
- Add file-render behavior for dynamic output length.
- Add tests for:
  - shorter output
  - longer output
  - zero-length invalid result
  - very large length guard
  - cancellation before and after length is known

Exit criteria:

- Lab does not truncate or pad length-changing CDP output accidentally.
- Length-changing output can be materialized and consumed by RT as a stable
  known-length source.
- One synthetic length-changing operator passes Core and Lab tests.
- One real CDP operator with length-changing behavior passes golden tests.

Primary repos:

- `xyona-lab`
- `xyona-core`
- `xyona-cdp-pack`

### Phase 6 - CDP Data Helper Completion

Purpose:

Build the non-spectral CDP data infrastructure required by many classic
programs.

Tasks:

- Expand breakpoint support:
  - validation diagnostics
  - units
  - extrapolation policy
  - tempo/sample mapping if needed by Lab
- Add CDP time/unit helpers:
  - seconds
  - samples
  - milliseconds
  - frequency
  - MIDI note where applicable
  - ratio and cents
- Add random/determinism helpers:
  - seed policy
  - repeatable random streams
  - golden-test stability
- Add text/table helpers:
  - parser
  - serializer
  - diagnostics
  - encoding policy

Exit criteria:

- Non-spectral CDP families can share data utilities instead of each operator
  defining local parsers or random behavior.
- Golden fixtures are repeatable across platforms.

Primary repo:

- `xyona-cdp-pack`

### Phase 7 - Typed Data Ports Or Asset Handles

Purpose:

Create the host-visible mechanism for non-audio data to flow through an HQ
graph.

Decision needed:

1. Typed graph ports
   - Strong graph semantics.
   - Better validation and visual patching.
   - Larger Core/Lab graph changes.

2. Lab-managed asset handles
   - Easier for file-like CDP workflows.
   - Good for large spectral data.
   - Requires asset lifecycle and dependency tracking.

Likely final design:

- Typed ports for logical graph compatibility.
- Asset handles for large backing storage.

Tasks:

- Define a `DataKind` model in Core descriptors.
- Add Lab connection validation for non-audio edges.
- Add project asset lifecycle for generated analysis artifacts.
- Add cache invalidation rules:
  - input audio changed
  - params changed
  - sample rate changed
  - spectral settings changed
- Surface stale analysis/materialized data as a user-visible state instead of
  silently treating old assets as valid.
- Add UI placeholders for unsupported or stale analysis data.

Exit criteria:

- Lab can represent a graph edge whose value is analysis data, not audio.
- The pack can produce and consume that data without seeing Lab UI concepts.
- Invalid audio-to-spectral or spectral-to-audio edges are caught at graph build
  time unless an explicit converter node exists.

Primary repos:

- `xyona-core`
- `xyona-lab`
- `xyona-cdp-pack`

### Phase 8 - PVOC/PVX Data Model

Purpose:

Implement spectral analysis data as a first-class CDP pack format.

Hard prerequisites:

- Gate E: implemented and tested Offline Session ABI
- Phase 7 typed data ports or asset handles
- CDP8 golden fixture harness for PVOC/PVX behavior

PVOC/PVX must not be implemented on the prototype whole-buffer offline ABI.

Tasks:

- Define internal PVOC/PVX structures:
  - header
  - channel layout
  - frames
  - bins
  - magnitudes
  - phases or frequencies
  - source metadata
  - transform metadata
- Define memory layout:
  - interleaved vs planar
  - channel-major vs frame-major
  - float vs double internal precision
- Define compatibility policy:
  - native XYONA spectral format first, or
  - CDP8-compatible PVX import/export first
- Add serialization if required:
  - binary format
  - versioned header
  - endian policy
  - validation diagnostics
- Add tests:
  - empty/invalid data
  - short files
  - mono/stereo
  - non-power-of-two rejection or support policy
  - deterministic roundtrip serialization

Exit criteria:

- A PVOC analysis object can be created, validated, stored, loaded if enabled,
  and compared in tests.
- The representation is not tied to Lab UI or file picker code.

Primary repo:

- `xyona-cdp-pack`

### Phase 9 - FFT, Windowing, And Reconstruction Policy

Purpose:

Make spectral analysis/synthesis deterministic and CDP-compatible enough for
real operator ports.

Tasks:

- Choose FFT backend:
  - existing Core utility if available and suitable
  - small embedded permissive FFT
  - platform-independent implementation in the CDP pack
- Define window functions:
  - Hann
  - Hamming
  - Blackman or CDP-specific windows if needed
- Define hop/overlap constraints.
- Define phase handling and frequency estimation.
- Define inverse transform overlap-add behavior.
- Add numerical tolerances for:
  - identity roundtrip
  - phase-sensitive tests
  - low-level noise floor
- Add platform reproducibility tests.

Exit criteria:

- `audio -> analysis -> synthesis -> audio` works as a controlled identity
  roundtrip.
- Tolerances are documented and stable.
- The same test passes on Windows/macOS/Linux within tolerance.

Primary repos:

- `xyona-cdp-pack`
- optionally `xyona-core` if a generic FFT abstraction is required

### Phase 10 - First Spectral Vertical Slice

Purpose:

Prove the complete time-domain to spectral-domain to time-domain workflow.

Hard prerequisites:

- Gate E: implemented and tested Offline Session ABI
- Phase 7 typed data ports or asset handles
- Phase 8 PVOC/PVX data model
- Phase 9 FFT/windowing/reconstruction policy

First slice:

```text
audio source
    -> cdp.pvoc.analysis
    -> cdp.pvoc.synthesis
    -> audio output
```

Tasks:

- Add inventory entries for analysis and synthesis.
- Add descriptors with typed ports:
  - audio input
  - pvoc output
  - pvoc input
  - audio output
- Add Lab graph validation for the typed connection.
- Add Lab HQ execution support for generated spectral assets.
- Add golden references from CDP8 where applicable.
- Add identity roundtrip tests independent of CDP8 if exact CDP8 parity is not
  yet the first target.

Exit criteria:

- Lab can render a graph that enters and leaves the spectral domain.
- Spectral data is not passed through audio ports.
- The output is deterministic and validated.

Primary repos:

- `xyona-lab`
- `xyona-core`
- `xyona-cdp-pack`
- `CDP8` as read-only reference

### Phase 11 - Spectral CDP Families

Purpose:

Port real CDP spectral families on top of the proven PVOC infrastructure.

Candidate families:

- `pvoc`
- `blur`
- `focus`
- `hilite`
- `spec`
- `formants`
- `specenv`
- `spectstr`
- `spectune`
- `suppress`
- `caltrain`

Tasks per family:

- Inventory entry.
- Mode classification.
- Parameter model.
- Data dependency model.
- Algorithm port.
- Golden fixture.
- Pack unit tests.
- Core loader/execution test if new shape is used.
- Lab smoke test if user-visible graph behavior changes.

Exit criteria:

- Operators share the same PVOC model.
- Operators do not duplicate spectral parsing, FFT, or asset lifecycle logic.
- CDP8 parity is measured, not guessed.

Primary repo:

- `xyona-cdp-pack`

### Phase 12 - Analysis, Text, And Multi-Output Programs

Purpose:

Support CDP programs that produce reports, text outputs, multiple files, or
analysis data rather than one audio stream.

Tasks:

- Define Lab destination policy:
  - project asset
  - user-selected file
  - report panel
  - hidden cache
- Add Core descriptor support for non-audio outputs.
- Add pack execution support for multi-artifact result sets.
- Add UI affordances only after the data contract is stable.

Exit criteria:

- Non-audio CDP tools do not pretend to be audio effects.
- Multi-output results are visible, stored, or exportable through Lab-owned
  project mechanisms.

Primary repos:

- `xyona-lab`
- `xyona-core`
- `xyona-cdp-pack`

## Golden Reference Strategy

CDP8 parity requires automated reference generation and comparison.

Required components:

- Fixture input audio:
  - silence
  - impulse
  - sine
  - sweep
  - noise with fixed seed
  - short clips
  - stereo decorrelated clips
- Reference output generated by CDP8.
- Metadata:
  - CDP8 command
  - exact args
  - sample rate
  - expected output length
  - tolerance
  - known deviations
- Comparison:
  - exact length checks where applicable
  - RMS error
  - peak error
  - optional spectral distance for spectral programs
  - explicit NaN/Inf rejection

Golden tests should live with the pack unless they test Lab graph behavior.

## Lab UI And UX Implications

Lab should expose CDP process constraints honestly:

- Realtime-incompatible operators should be marked HQ/offline-only.
- Unsupported operators should not be draggable into a graph as if they worked.
- Whole-file operators need clear render-time behavior.
- Length-changing operators need destination/region behavior that does not
  surprise users.
- Spectral analysis assets need stale/valid state.
- Long-running CDP renders need progress and cancellation.

The pack should not own UI wording beyond descriptor labels, parameter metadata,
and CDP provenance.

## Risks

### Risk: Treating PVOC as Audio

This would make the first spectral demo easier but would corrupt the long-term
graph model. Avoid.

Mitigation:

- Add typed data or asset handles before real spectral operators.

### Risk: Length-Changing Output Truncation

If Lab keeps assuming `endSeconds - startSeconds` as final output length,
length-changing CDP programs will be wrong.

Mitigation:

- Implement output length negotiation before porting length-changing families.

### Risk: Pack ABI Churn

Adding fields ad hoc for each CDP family would make packs fragile.

Mitigation:

- Use versioned structs and shape-level contracts.

### Risk: Lab Owning CDP Algorithms

This would break the LGPL dynamic-pack boundary.

Mitigation:

- Keep CDP algorithms and formats in `xyona-cdp-pack`.
- Keep Lab limited to host orchestration and project/asset policy.

### Risk: Whole-File Memory Blowup

CDP programs can operate on large files.

Mitigation:

- Keep the prototype whole-buffer offline ABI limited to bounded
  simple/reference operators.
- Implement the Offline Session ABI with memory/spooling policy
  before length-changing, PVOC/spectral, multi-output, or production-scale
  long-file operators.
- Port `cdp.modify.loudness_normalise` to the Offline Session ABI and remove the
  public prototype ABI surface before release unless an explicit internal-helper
  exception is made.

### Risk: Stale Materialized Assets

If source audio, parameters, sample rate, render range, algorithm version, or
spectral settings change after a clip is materialized, RT could otherwise play
an old render as if it were current.

Mitigation:

- Store dependency signatures with materialized layers/clips.
- Feed signatures with current AudioEngineManager render dependencies: render
  job, render range, sample rate, graph plan, wires, operator descriptor
  versions, parameters, tempo, and grid context.
- Include `lab.audio_file_in` source file fingerprints and materialized WAV
  asset fingerprints before declaring the persistence/staleness data path
  complete.
- Mark stale or missing assets with a user-visible `Re-render required` state.
- Do not silently treat stale material as valid RT source material.

## Recommended Immediate Next Steps

1. Document and enforce the gate system:
   - the current whole-buffer offline ABI is prototype/reference only.
   - `MaterializedAudioStore` is the concrete `HQ_RT.md` Phase 7 store line.
   - length-changing and PVOC/spectral require implemented/tested
     Offline Session ABI.
2. Finish materialized asset production persistence:
   - future spectral settings in dependency signatures once spectral
     materialized artifacts exist
   - dedicated UI surface for `Re-render required` / `Missing` materialized clips
3. Add realtime LayerPlayer consumption of `MaterializedAudioStore` clips with
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

## Definition Of Done For CDP8 Rewrite Readiness

XYONA is ready for broad CDP8 rewrite work when:

- Pack tests are green on all target platforms.
- Lab can distinguish realtime, HQ, whole-file, length-changing, and typed-data
  operators before execution.
- Whole-file same-length operators execute through Lab HQ render.
- The prototype whole-buffer offline ABI is not a release production contract.
- Offline Session ABI execution exists and is tested for normal completion,
  progress, and cancellation.
- Length-changing operators negotiate output length without truncation.
- Completed offline results can re-enter RT atomically as ordinary Lab
  source/value artifacts.
- Materialized assets persist through normal project save/open and stale results
  are detected before RT treats them as valid.
- Typed spectral data exists as a first-class graph or asset value.
- PVOC analysis/synthesis identity roundtrip is deterministic.
- CDP8 golden reference tooling is repeatable.
- The LGPL pack remains dynamically loadable and replaceable.

At that point, CDP8 porting can proceed family by family without repeatedly
reworking the foundation.
