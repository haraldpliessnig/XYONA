# XYONA Parameter Automation System Review and Highend Roadmap

Date: 2026-05-01

Scope: Standalone XYONA only: `xyona-lab` plus `xyona-core` plus runtime packs such
as `xyona-cdp-pack`. This report deliberately does not design a DAW plugin runtime.
The plugin-runtime idea document is used only as an architectural stress test.

Status: technical review and implementation roadmap. No source change has been
made by this report.

## Executive Verdict

XYONA already has strong foundations: host-free Core descriptors, Lab-side
`ParamAddress`, a `ParameterControlHub`, lock-free realtime parameter updates,
block-stable audio snapshots, timeline lanes, macro/modulation concepts, and
topology parameter recognition.

The system is not yet highend because the value semantics of a parameter are not
one canonical contract. In practice, UI, automation, MIDI, modulation, snapshots,
and pack metadata can interpret the same parameter differently. The most urgent
issue is not cosmetic: parameter automation currently mixes normalized 0..1 and
plain/native parameter values.

The roadmap should therefore start with value domains and parameter semantics,
then migrate Lab's existing paths onto that contract. This is a staged hardening,
not a rewrite.

## Target Definition

A highend XYONA parameter system should provide these guarantees:

1. Every public parameter has one canonical semantic contract.
2. Every value crossing a subsystem boundary states its domain:
   `Plain`, `Normalized01`, `DisplayText`, `AutomationPoint`, or `ModulationDelta`.
3. UI, timeline automation, MIDI, macros, modulation, offline render, realtime
   playback, patch persistence, and packs use the same codec.
4. Realtime and offline rendering produce the same parameter values at the same
   musical/sample positions.
5. Block-stable parameter automation remains block-stable by contract. Sample
   accuracy belongs to signal/CV paths unless a future parameter explicitly opts
   into sub-block application.
6. Topology parameters cannot silently enter normal automation, modulation, or
   MIDI-learn paths.
7. Slot-scoped parameters are addressable end-to-end, not only in persistence.
8. Parameter state is debuggable: for any final value, Lab can explain source,
   base, automation, macro/bind, modulation, clamp, quantize, and smoothing.
9. Packs can expose rich parameter semantics without Lab depending on pack
   implementation code.
10. Future projects can reuse the semantic/runtime core without inheriting Lab UI
    or project-state implementation.

Non-goals for the current standalone roadmap:

- Do not turn Lab into a plugin host abstraction layer.
- Do not make generic parameters sample-accurate by default.
- Do not move Lab orchestration, timeline, UI, or project state into Core.
- Do not solve arbitrary expression/binding languages until the parameter value
  contract is hard.

## Current Architecture Map

### Core and Pack Descriptors

- `xyona-core/include/xyona/types.hpp` defines `ParamDesc`.
- `ParamDesc` includes id, label, type, min/max/default, enum values, unit,
  display, precision, scope support, and topology flag.
- It does not encode a full value semantic contract: scale/mapping, step,
  quantization, smoothing, formatter/parser, automation policy, modulation
  policy, or MIDI policy.
- `xyona-cdp-pack` operator YAML files already contain useful `ui.scale` and
  `ui.step` hints. These are not yet treated as first-class Lab parameter
  semantics.

### Lab Parameter Model and Hub

- `ParamAddress` supports node id, parameter id, and optional slot index.
- `ParameterControlHub` arbitrates manual, MIDI, automation, and modulation
  contributions.
- The hub accepts and emits raw/plain values. Its public names say `rawValue`;
  e.g. `setAutomationBase(const ParamAddress&, double rawValue)`.
- Bounds are seeded from descriptor min/max. There is no codec or scale policy
  in the hub.

### Realtime Bridge and Snapshots

- `ParamUpdateBridge` sends realtime updates as node id, hashed storage key, raw
  value, and sample offset.
- Audio snapshots are block-stable arrays of parameter hashes and values.
- Some hot paths still resolve by hash and linear scan. This is acceptable for
  current scale but not the final highend shape.

### Timeline Parameter Automation

- `TimelineAutomationPoint.value` is an untyped `double`.
- `TimelineParameterAutomationLane` sets its visual/edit range to `0.0..1.0`.
- `AutomationRecorder` records manual/MIDI base values from the hub directly
  into timeline points. Those base values are plain/native values.
- `AutomationPlaybackEngine` evaluates timeline lanes through the signal source
  system and sends the result to `ParameterControlHub::setAutomationBase`.
- `TimelineLaneSignalSource` normalizes parameter automation lanes to unipolar
  0..1. If no per-lane normalization range is supplied, the default range is
  0..1.

This means the current automation path is value-domain ambiguous.

## Strict Findings

### F0 Critical: Parameter Automation Has a Value-Domain Mismatch

Evidence:

- `TimelineParameterAutomationLane` initializes `setValueRange(0.0, 1.0)`.
- `AutomationRecorder` stores `event.baseValue` into `TimelineAutomationPoint.value`.
- `ParameterControlHub::setAutomationBase` expects a raw/plain value.
- `AutomationPlaybackEngine` currently builds timeline signal sources without
  parameter semantics and emits the evaluated value into the hub.
- `TimelineLaneSignalSource` treats parameter automation sources as
  `SignalDomain::Unipolar01` and normalizes them.

Impact:

- For a parameter whose native range is not 0..1, timeline automation can send
  wrong values.
- Recorded native values above 1.0 can be clamped/normalized to 1.0 on playback.
- Manually edited automation points are visually and interactively constrained
  to 0..1 regardless of the target parameter.
- dB, log, frequency, integer, enum, and bool parameters do not have correct
  automation authoring semantics.
- This also explains the observed symptom that automated parameters appear to be
  mapped only to 0 and 1 or generally to 0..1.

Target:

- Make timeline parameter automation value domain explicit.
- Preferred target: store parameter automation points as `Normalized01` using
  the canonical parameter codec.
- Recorder path: plain value -> codec -> normalized automation point.
- Playback path: normalized automation point -> codec -> plain value -> hub.
- UI path: normalized point <-> display/native editor through the same codec.
- Legacy migration must tag old lanes and convert them deterministically.

### F1 High: `ParamDesc` Is Not a Complete Parameter Semantic Contract

Current descriptor fields are enough to clamp simple numeric values but not
enough to drive highend automation.

Missing first-class semantics:

- value scale: linear, log, exponential, dB, frequency, power, enum, bool
- step and quantization
- display parser/formatter policy
- automation domain and interpolation domain
- smoothing/dezipper policy
- flags: automatable, modulatable, MIDI-learnable, recordable
- default modulation mode: additive plain delta, normalized offset, bipolar
  normalized, multiplicative, or custom
- topology behavior

Target:

- Introduce a host-neutral `ParamSemantics`/`ParamValueCodec` layer.
- Keep Core JUCE-free.
- Lab consumes resolved semantics; it does not invent conversions.

### F2 High: Multiple Linear Conversion Implementations Exist

Lab currently has several local conversions that assume linear min/max:

- `ParamFormatter`
- text-field parameter views
- canvas parameter model normalization
- MIDI mapping
- automation lane drawing/editing
- modulation contribution mapping

Impact:

- A parameter can display, automate, and modulate with different behavior.
- Fixing only one surface does not fix the product.

Target:

- All value conversion must go through one codec.
- Local linear helper functions should either disappear or become private
  helpers inside the codec implementation.

### F3 High: CDP Pack UI Metadata Is Not First-Class in Lab

CDP operator YAML already exposes information such as `ui.scale` and `ui.step`.
This is valuable semantic data, not cosmetic UI metadata.

Impact:

- CDP parameters with dB/log-like ranges are authored as plain linear ranges.
- Automation curves are not perceptually correct.
- MIDI and modulation ranges are likely musically wrong.

Target:

- Resolve CDP pack metadata into `ParamSemantics`.
- In the short term, parse existing pack param meta JSON into Lab's semantic
  resolver.
- In the longer term, extend the pack ABI in a backward-compatible way.

### F4 High: Automation Playback Ownership Is Split

There is a message/control-thread playback engine and a separate audio-side
automation event buffer concept. The current standalone product needs one
authoritative playback/offline path.

Impact:

- Realtime playback and offline render can diverge.
- UI tick timing can influence parameter values.
- The sample offset field exists but ordinary parameter automation is still
  effectively block-boundary oriented.

Target:

- Timeline automation should compile into a prepared parameter automation
  runtime used by both realtime and offline engines.
- UI/message ticks can remain for visual preview and editing, not as the source
  of render truth.
- Continue using block-stable parameter automation unless a parameter explicitly
  opts into a different policy.

### F5 High: Slot-Scoped Addressing Is Not End-to-End

`ParamAddress` and snapshot storage support slot keys such as `param@slot=N`.
However, prepared modulation and some selection/binding paths appear to keep
only node id plus parameter id.

Impact:

- Slot-specific parameter edits can persist, but automation/modulation may not
  target them reliably.
- UI source indicators can become misleading for slot-scoped values.

Target:

- Every target path uses full `ParamAddress`.
- Hashes are derived from `ParamAddress::storageKey()` only after the address is
  resolved.
- Modulation routes, macro targets, automation lanes, MIDI mappings, source
  masks, and snapshots all preserve slot index.

### F6 Medium/High: Smoothing Is Not a Contract

The current policy deliberately makes normal parameter updates block-stable. That
is acceptable. What is missing is a descriptor-level smoothing decision.

Impact:

- Gain, mix, filter frequency, pitch, and delay-time parameters can zipper unless
  each operator handles smoothing internally.
- It is unclear whether smoothing belongs to host, operator, or neither.

Target:

- Add `ParamSmoothingPolicy`.
- Values:
  - `None`
  - `BlockStable`
  - `HostRamp`
  - `OperatorOwned`
  - optional time constants for host-ramped parameters
- Make the application point explicit.

### F7 Medium/High: Topology Parameters Need Hard Policy Enforcement

Topology parameters are recognized and often skipped in runtime update paths.
That is good, but the policy should be enforced earlier.

Impact:

- A topology parameter can still appear as an ordinary target unless every caller
  remembers to filter it.
- Automation or MIDI of topology values can cause rebuild semantics to leak into
  value automation.

Target:

- `isTopology` implies not automatable, not modulatable, not MIDI-learnable,
  unless a future explicit rebuild automation mode exists.
- Target resolvers, lane creation, MIDI learn, modulation assignment, and hub
  APIs should reject topology parameters with diagnostics.

### F8 Medium: Value Sources Are Partially Implemented

`Const`, `Param`, `Expr`, and `Bind` exist in the value-source model. `Expr` and
`Bind` are not yet a deterministic runtime system.

Impact:

- Persisted intent can look like a feature but not behave like one.
- Future patch compatibility becomes harder if semantics are vague.

Target:

- Either implement deterministic value-source evaluation with dependency order,
  cycle detection, missing-target policy, and offline parity, or hide/quarantine
  incomplete source kinds from the product UI.

### F9 Medium: Runtime Parameter Application Still Uses Lookup-Heavy Paths

The current runtime uses stable hashes and block snapshots, which is a good
intermediate design. But some hot paths still linearly scan parameter arrays or
binding vectors.

Impact:

- Large patches pay unnecessary lookup cost.
- Runtime behavior depends on hash lookup patterns instead of compiled handles.

Target:

- During graph compile, resolve `ParamAddress` to `CompiledParamTarget`.
- Runtime updates should target stable indices where possible.
- Keep hashes for persistence/debug/compatibility, not as the primary hot-path
  addressing mechanism.

### F10 Medium: Product UI Does Not Yet Expose Highend Parameter State

Numeric parameter controls are still too text-field-heavy. Automation lanes do
not consistently show target units, target scale, source masks, or slot-specific
state.

Impact:

- The system may be technically capable but not operable at a high level.
- Users cannot easily inspect why a parameter has its final value.

Target:

- Descriptor-driven controls: slider, knob, stepper, enum, bool, channel picker,
  text editor where appropriate.
- Per-parameter source indicators: Manual, MIDI, Automation, Macro, Modulation,
  Bind.
- Automation lanes render in target-aware display units while storing canonical
  automation values.

## Target Architecture

### Core/Shared: Parameter Semantics and Codec

Add a JUCE-free semantic layer. It can live in `xyona-core` if it remains
host-free, or in a small shared runtime package if that better preserves ABI
boundaries.

Sketch:

```cpp
enum class ParamValueDomain
{
    Plain,
    Normalized01,
    DisplayText
};

enum class ParamScale
{
    Linear,
    Log,
    Exponential,
    Decibel,
    Frequency,
    EnumIndex,
    Boolean
};

enum class ParamSmoothingKind
{
    None,
    BlockStable,
    HostRamp,
    OperatorOwned
};

struct ParamStepPolicy
{
    double step { 0.0 };
    bool snap { false };
};

struct ParamAutomationPolicy
{
    bool automatable { true };
    bool recordable { true };
    bool midiLearnable { true };
    bool modulatable { true };
    bool topology { false };
};

struct ParamSemantics
{
    std::string id;
    ParamType type;
    double minPlain { 0.0 };
    double maxPlain { 1.0 };
    double defaultPlain { 0.0 };
    ParamScale scale { ParamScale::Linear };
    ParamStepPolicy step;
    ParamSmoothingKind smoothing { ParamSmoothingKind::BlockStable };
    ParamAutomationPolicy automation;
    std::string unit;
    std::vector<std::string> enumValues;
};

class ParamValueCodec
{
public:
    double plainToNormalized(double plain) const noexcept;
    double normalizedToPlain(double normalized) const noexcept;
    double sanitizePlain(double plain) const noexcept;
    double sanitizeNormalized(double normalized) const noexcept;
    std::string formatPlain(double plain) const;
    ParseResult parseDisplayText(std::string_view text) const;
};
```

Rules:

- Bool and enum decode must quantize.
- Integer parameters snap to integer or descriptor step.
- dB/frequency/log curves must define interpolation behavior.
- Parser and formatter must be deterministic and locale-independent for project
  state.
- UI localization can be layered above canonical persistence formatting.

### Lab: Resolved Parameter Semantics Cache

Lab should not ask every control to interpret raw descriptors independently.
Build a resolver:

```cpp
struct ResolvedParamSemantics
{
    ParamAddress address;
    xyona::ParamDesc desc;
    ParamSemantics semantics;
    ParamValueCodec codec;
    std::uint64_t semanticRevision;
};
```

Inputs:

- Core `ParamDesc`
- pack param meta JSON
- Lab-specific policy defaults
- slot scope
- topology rules

Consumers:

- `ParamFormatter`
- parameter views
- canvas parameter model
- timeline automation lanes
- automation recorder/playback
- MIDI learn/mapping
- modulation runtime
- `ParameterControlHub`
- project persistence/migration

### Timeline Automation Value Model

Target model:

```cpp
enum class AutomationPointValueDomain
{
    LegacyUnknown,
    Normalized01
};

struct TimelineAutomationLane
{
    ParamAddress target;
    AutomationPointValueDomain valueDomain { AutomationPointValueDomain::Normalized01 };
    std::uint64_t paramSemanticRevision { 0 };
    // points store normalized values in TimelineAutomationPoint::value
};
```

Semantics:

- New parameter automation lanes store normalized 0..1 values.
- The UI may display dB/Hz/percent/native values, but persisted point values are
  normalized.
- Curve interpolation occurs in normalized automation space by default.
- The codec defines how normalized automation becomes plain parameter values.
- Step/bool/enum parameters quantize at decode and/or force step interpolation.
- Legacy lanes are migrated on load or first target resolution.

Legacy migration:

1. If lane has explicit value-domain metadata, obey it.
2. If metadata is missing and all points are inside 0..1, treat as
   `LegacyNormalized01`.
3. If metadata is missing and any point is outside 0..1, treat as
   `LegacyPlain` and convert plain -> normalized with the target codec.
4. If the target is missing, preserve raw values and mark the lane unresolved.
5. Once resolved, write explicit domain metadata on next save.

### Runtime Parameter Target

Compile parameter targets during graph planning:

```cpp
struct CompiledParamTarget
{
    NodeId nodeId;
    ParamAddress address;
    audio::ParamKey storageKeyHash;
    std::uint32_t nodeIndex;
    std::uint32_t snapshotValueIndex;
    std::uint32_t slotIndex;
    ParamSemantics semantics;
};
```

Runtime rule:

- UI and timeline resolve addresses at control/compile time.
- Audio runtime applies values by compiled target index.
- Hash fallback remains for compatibility and diagnostics.

### Source Arbitration

Keep the current source model but make value domains explicit:

1. Manual/MIDI base: plain value
2. Automation base: plain value decoded from normalized timeline value
3. Macro/Bind: either normalized or plain, declared per binding
4. Modulation: declared contribution mode
5. Clamp/quantize through codec
6. Smooth according to policy
7. Emit final plain value

The hub should eventually expose names that encode domain, e.g.
`setAutomationBasePlain`, `setManualBasePlain`, and
`setModulationContributionPlainDelta`.

## Roadmap by Batches and Commits

The sequence below is written as implementation batches. Each commit should be
small enough to review independently and large enough to leave the tree in a
coherent state.

### Batch 0: Baseline Guards and This Report

Commit 0.1: `docs(parameters): add highend automation review roadmap`

- Add this report.
- No code changes.

Commit 0.2: `test(parameters): capture current automation value-domain behavior`

- Add failing or characterization tests around parameter automation values.
- Cover a parameter with range `0..1`.
- Cover a parameter with range `-60..12` dB or equivalent.
- Cover a parameter with range `20..20000` frequency or a large CDP gain range.
- Expected current behavior should document the mismatch before fixing it.

Acceptance:

- Tests prove the 0..1/native ambiguity.
- No production behavior changes yet.

### Batch 1: Core Parameter Semantics Skeleton

Commit 1.1: `core(parameters): introduce ParamValueDomain and ParamScale`

- Add JUCE-free enums and simple structs.
- No pack ABI break.
- Keep existing `ParamDesc` intact.

Commit 1.2: `core(parameters): add ParamValueCodec for linear numeric parameters`

- Implement plain <-> normalized for bool, enum, int, float.
- Clamp and quantize through codec.
- Add unit tests.

Commit 1.3: `core(parameters): add step and display parse/format policy`

- Support integer snapping and descriptor step.
- Add deterministic text formatting/parsing for plain values.
- Keep UI localization out of this layer.

Commit 1.4: `core(parameters): add non-linear scales to ParamValueCodec`

- Add log, exponential, dB, and frequency mappings.
- Define invalid-range fallback behavior.
- Add roundtrip tests and edge-case tests.

Acceptance:

- Codec roundtrip tests pass.
- Codec behavior is deterministic and host-free.
- No Lab feature depends on old linear helper behavior yet.

### Batch 2: Pack Semantics Resolution

Commit 2.1: `core(packs): expose param meta access through resolved descriptor helper`

- Provide a helper that combines `ParamDesc` plus optional pack param meta.
- Do not force Lab to parse arbitrary JSON in multiple places.

Commit 2.2: `cdp-pack(parameters): map op.yaml ui scale and step into param meta consistently`

- Ensure generated metadata contains scale/step for every relevant CDP parameter.
- Add descriptor generation tests where practical.

Commit 2.3: `lab(parameters): add ResolvedParamSemantics service`

- Build a Lab-side resolver from Core desc + pack meta.
- Cache by `ParamAddress` and descriptor revision.
- Apply Lab defaults when pack metadata is absent.

Acceptance:

- A CDP parameter with `ui.scale: linear_db` resolves to a non-default semantic
  scale.
- A CDP parameter with `ui.step` resolves to a step policy.
- Missing metadata still produces safe linear semantics.

### Batch 3: Migrate Lab Formatting and Controls to the Codec

Commit 3.1: `lab(parameters): route ParamFormatter through ParamValueCodec`

- Replace direct min/max linear mapping in `ParamFormatter`.
- Keep public API stable where possible.

Commit 3.2: `lab(parameters): remove duplicate text-field conversion logic`

- `ParamTextFieldView` uses `ParamFormatter`/codec.
- Text parsing supports units through the codec.

Commit 3.3: `lab(parameters): make numeric controls descriptor-driven`

- Use slider/knob/stepper/text according to resolved semantics/display hints.
- Preserve current text fallback for unsupported displays.

Commit 3.4: `lab(canvas): normalize CanvasParamModel through resolved semantics`

- Any UI normalized value must roundtrip through the codec.
- Remove local linear helper behavior.

Acceptance:

- Numeric UI, text entry, and parameter model agree for linear, dB/log, int,
  enum, and bool.
- CDP step values snap consistently.

### Batch 4: Fix Parameter Automation Value Domains

Commit 4.1: `lab(timeline): add explicit automation point value domain metadata`

- Add lane domain metadata with legacy default.
- Persist the metadata.
- Keep load backward-compatible.

Commit 4.2: `lab(timeline): resolve parameter automation lanes with target semantics`

- Lane stack receives `ResolvedParamSemantics` for target lanes.
- Lane rendering gets display labels/units from codec.

Commit 4.3: `lab(timeline): record parameter automation as normalized values`

- Recorder receives plain base value.
- Resolver converts plain -> normalized before appending point.
- Existing point append API either becomes domain-aware or wraps conversion.

Commit 4.4: `lab(timeline): edit parameter automation in normalized domain with display conversion`

- Mouse Y coordinate maps to normalized point value.
- Display/edit overlays show native/display values.
- Step/bool/enum targets quantize.

Commit 4.5: `lab(timeline): playback parameter automation through codec decode`

- Playback evaluates normalized lane value.
- Decode normalized -> plain through codec.
- Send plain value to `ParameterControlHub`.
- Stop relying on generic unipolar signal-source normalization for parameter
  automation unless it is explicitly a normalized source.

Commit 4.6: `lab(timeline): migrate legacy automation lanes`

- Implement migration rules:
  - values inside 0..1 -> normalized legacy
  - values outside 0..1 -> plain legacy -> convert
  - unresolved target -> preserve and mark unresolved
- Add project-state tests.

Acceptance:

- Automating a `0..1` parameter still works.
- Automating a dB parameter writes/display/plays correct dB values.
- Recording manual changes into automation plays back the same values.
- Existing patches load deterministically.

### Batch 5: Hard Automation/Topology Policy

Commit 5.1: `lab(parameters): add automatable/modulatable/midi policy flags`

- Derived from `ParamSemantics`.
- `isTopology` defaults all ordinary control policies to false.

Commit 5.2: `lab(timeline): filter non-automatable parameters from target selectors`

- Header/dropdown/target resolver rejects topology and unsupported params.
- Existing lanes for now remain loadable but unresolved/disabled with diagnostic.

Commit 5.3: `lab(midi): reject non-midi-learnable parameters`

- MIDI learn/mapping creation uses semantics.

Commit 5.4: `lab(modulation): reject non-modulatable parameters`

- Modulation assignment and prepared runtime use semantics policy.

Acceptance:

- Topology parameters cannot be newly automated, modulated, or MIDI learned.
- Existing invalid targets do not silently apply.

### Batch 6: Compile Runtime Parameter Targets

Commit 6.1: `lab(audio): build per-node parameter index maps in graph runtime cache`

- Map storage key hash -> snapshot index.
- Preserve hash fallback and debug diagnostics.

Commit 6.2: `lab(parameters): introduce CompiledParamTarget`

- Resolve `ParamAddress` to node index, snapshot index, storage key, and
  semantics.

Commit 6.3: `lab(audio): apply queued parameter updates through compiled target indices`

- Reduce hot-path linear scans.
- Keep old hash path as fallback during transition.

Commit 6.4: `lab(audio): update CoreOperatorHostAdapter bindings to use prepared indices`

- Avoid repeated binding scans where practical.

Acceptance:

- Existing realtime updates still work.
- Large parameter-count stress tests show reduced lookup cost.
- Hash collision diagnostics remain.

### Batch 7: Authoritative Realtime/Offline Automation Runtime

Commit 7.1: `lab(automation): add prepared parameter automation runtime`

- Compile timeline parameter lanes into target + evaluated segment data.
- Include codec/semantics per lane.

Commit 7.2: `lab(audio): apply prepared automation in AudioGraphProcessor`

- Apply block-stable automation at block boundary.
- Preserve ordering: manual base, automation base, modulation, process.

Commit 7.3: `lab(offline): use the same prepared automation runtime for offline render`

- Remove divergence between UI tick playback and render.

Commit 7.4: `lab(timeline): downgrade message-thread automation playback to preview/control`

- UI still reflects transport.
- Render truth comes from prepared runtime.

Acceptance:

- Realtime and offline render produce matching parameter traces.
- Timeline automation does not depend on message-thread tick cadence.

### Batch 8: Slot-Aware Automation, Modulation, and MIDI

Commit 8.1: `lab(timeline): persist and resolve slot-scoped automation targets`

- Ensure lane target includes optional slot index.
- Header/selector UI can expose slot targets where valid.

Commit 8.2: `lab(modulation): preserve ParamAddress slot index in routes`

- Replace target node/param-only route paths with full address.

Commit 8.3: `lab(modulation): prepare slot-scoped modulation targets`

- Prepared runtime hashes storage key from full address.

Commit 8.4: `lab(midi): make MIDI mappings full ParamAddress targets`

- Preserve slot index and semantics.

Acceptance:

- Slot-specific automation and modulation apply only to that slot.
- Global and slot override behavior remains deterministic.

### Batch 9: Modulation Semantics and Smoothing

Commit 9.1: `core(parameters): add modulation contribution modes`

- Plain additive delta, normalized bipolar offset, multiplicative, or disabled.

Commit 9.2: `lab(modulation): map modulation through target semantics`

- Replace min/max-only modulation math with codec-aware mapping.

Commit 9.3: `core(parameters): add ParamSmoothingPolicy`

- Descriptor-level smoothing policy and defaults.

Commit 9.4: `lab(audio): apply host smoothing only where policy allows it`

- Host ramps for appropriate params.
- Operator-owned smoothing remains operator-owned.

Acceptance:

- Modulation behaves correctly for dB/log/frequency parameters.
- Gain-like parameters do not zipper when host smoothing is selected.
- Operators can opt out or own smoothing.

### Batch 10: Value Sources, Macros, and Debuggability

Commit 10.1: `lab(parameters): mark Expr and Bind as unavailable until evaluated`

- Prevent UI from presenting incomplete source kinds as working features.

Commit 10.2: `lab(parameters): add deterministic value-source evaluation graph`

- Only if product scope wants Expr/Bind now.
- Include cycle detection and missing-target policy.

Commit 10.3: `lab(macros): define macro target binding semantics`

- Macro value domain, range, curve, target mapping, and missing target behavior.

Commit 10.4: `lab(ui): expose parameter source breakdown`

- Manual/MIDI, automation, macro/bind, modulation, clamp/quantize/smooth.

Acceptance:

- Users can inspect why a parameter has its current value.
- No incomplete source kind silently affects runtime.

### Batch 11: Persistence and Migration Hardening

Commit 11.1: `lab(project): version parameter automation lane schema`

- Persist value domain, target semantic revision, target identity, and migration
  status.

Commit 11.2: `lab(project): add parameter target migration records`

- Renamed parameters.
- Changed ranges.
- Removed targets.
- Pack unavailable.
- Slot count changes.

Commit 11.3: `lab(project): add migration diagnostics`

- Surface unresolved or migrated automation lanes in UI.

Acceptance:

- Old patches do not silently change sound.
- Missing targets are visible and non-destructive.

### Batch 12: Product UI Polish for Highend Operation

Commit 12.1: `lab(ui): target-aware automation lane scale and labels`

- Show units and display values.
- Support dB/log/frequency grid labels.

Commit 12.2: `lab(ui): add source indicators to parameter controls`

- Manual, MIDI, Automation, Macro, Modulation, Bind.

Commit 12.3: `lab(ui): add learn/assign workflows using semantics filters`

- MIDI learn, automation assignment, modulation assignment.

Commit 12.4: `lab(ui): add slot-aware parameter detail views`

- Global value vs slot override visibility.

Acceptance:

- The parameter system is visible, inspectable, and predictable in the product.

## Immediate Implementation Recommendation

Do not start with UI polish. Start with the automation value-domain bug.

Minimal safe first implementation slice:

1. Add explicit automation value-domain metadata.
2. Add a linear-only `ParamValueCodec` first.
3. Make recorder store normalized values.
4. Make playback decode normalized values to plain values before the hub.
5. Add legacy migration tests.
6. Then add non-linear scales and CDP metadata.

This avoids a risky all-at-once migration and immediately addresses the current
0..1 automation symptom.

## Test Plan

Required test categories:

- Codec roundtrip:
  - float linear
  - int with step
  - bool
  - enum
  - dB
  - log/frequency
- Automation value domain:
  - record plain -> stored normalized -> playback plain
  - manual edited normalized -> display native -> playback plain
  - legacy normalized lane migration
  - legacy plain lane migration
- Realtime/offline parity:
  - same patch, same automation lane, same rendered parameter trace
- Topology policy:
  - target selection rejects topology params
  - runtime rejects topology automation updates
- Slot targets:
  - global param unaffected by slot automation
  - slot param unaffected by global automation except documented inheritance
- Pack semantics:
  - CDP `ui.scale` and `ui.step` reach Lab resolved semantics
- Performance:
  - large patch parameter update stress test
  - no unexpected allocations on audio thread in new automation path

## Risk Register

Risk: Existing automation lanes are ambiguous.

- Mitigation: explicit legacy migration with unresolved-target preservation.

Risk: Non-linear mapping changes existing patch sound.

- Mitigation: use semantic versioning and migrate only when metadata is known.

Risk: Codec becomes a Lab-specific abstraction.

- Mitigation: keep codec JUCE-free and independent of UI/project state.

Risk: Too many changes land in one branch.

- Mitigation: follow the commit batches. Keep each batch buildable.

Risk: Smoothing policy moves DSP behavior into Lab.

- Mitigation: policy only states ownership. Operator-owned smoothing remains in
  Core/pack operators.

## Final Technical Position

The parameter system is structurally salvageable and already has the right
major parts. The highend gap is contract discipline: value domains, semantic
descriptors, codec reuse, authoritative automation runtime, and end-to-end
addressing.

The first non-negotiable fix is parameter automation value-domain correctness.
Once that is solved, the rest of the roadmap becomes a controlled migration
toward a reusable, product-grade parameter layer.
