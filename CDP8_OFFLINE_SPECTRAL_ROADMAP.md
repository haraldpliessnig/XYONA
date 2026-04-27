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
- The CDP pack has the first dynamic pack, descriptor, buffer, validation, and
  block-safe operator infrastructure.
- The CDP pack already classifies future process shapes such as whole-file,
  length-changing, analysis-output, multi-output, and generator operators.

Missing state:

- A host/pack execution contract for whole-file operators.
- Output length negotiation for length-changing CDP programs.
- A typed analysis/spectral data model instead of pretending PVOC/PVX is audio.
- Lab graph planning rules for offline-only and non-audio-producing nodes.
- Golden reference tooling at CDP8 family scale.
- Robust Windows pack test execution and CI coverage.

Conclusion:

This is cleanly achievable by extending the current HQ renderer and pack ABI. It
should not be solved by special-case hacks inside individual CDP operators.

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
- Add tests with a synthetic whole-file operator.

Exit criteria:

- A synthetic pack operator can consume a full input, finalize, and return a
  same-length output through the offline session path.
- The same operator is not allowed in realtime processing.
- Cancellation and progress are observable in tests.

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
  - `AudioLayer` / `LayeredClip`
  - `LayerPool` / `ClipStore`
  - `LayerPlayerNode` or equivalent RT-safe playback node
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

- Define memory budgets and disk-backed scratch before broad whole-file rollout.

## Recommended Immediate Next Steps

1. Fix `xyona-cdp-pack` Windows test script behavior.
2. Draft Core pack offline/session ABI structs.
3. Promote process-shape metadata into host-visible descriptors.
4. Reconcile the first CDP RT re-entry slice with `HQ_RT.md` Phase 5-7:
   renderer metadata, layer/clip storage, and RT-safe playback.
5. Add a synthetic whole-file same-length operator test.
6. Integrate that synthetic operator through Lab HQ render.
7. Materialize the result into a Lab layer/clip/asset that RT can consume.
8. Port one real whole-file length-preserving CDP operator.
9. Only then start length-changing and PVOC work.

## Definition Of Done For CDP8 Rewrite Readiness

XYONA is ready for broad CDP8 rewrite work when:

- Pack tests are green on all target platforms.
- Lab can distinguish realtime, HQ, whole-file, length-changing, and typed-data
  operators before execution.
- Whole-file same-length operators execute through Lab HQ render.
- Length-changing operators negotiate output length without truncation.
- Completed offline results can re-enter RT atomically as ordinary Lab
  source/value artifacts.
- Typed spectral data exists as a first-class graph or asset value.
- PVOC analysis/synthesis identity roundtrip is deterministic.
- CDP8 golden reference tooling is repeatable.
- The LGPL pack remains dynamically loadable and replaceable.

At that point, CDP8 porting can proceed family by family without repeatedly
reworking the foundation.
