# Roadmap: Parameter Automation System

**Status:** Implementation active; M0-M7 completed; M8.1-M8.3 completed; M8.4 pending
**Started:** 2026-05-01
**Planning branch:** `parameter-automation-review`
**Implementation branch:** `parameter-automation-system`
**Applies to:** `xyona-core`, `xyona-lab`, `xyona-cdp-pack`, future runtime packs
**Primary review:** `docs/done/REPORT_PARAMETER_AUTOMATION_SYSTEM_TECHNICAL_REVIEW_2026-05-01.md`
**Implementation report:** `docs/done/REPORT_PARAMETER_AUTOMATION_SYSTEM_IMPLEMENTATION_2026-05-01.md`
**Reference:** `IDEA_XYONA_PLUGIN_RUNTIME.md`

Scope: Standalone XYONA only: `xyona-lab`, `xyona-core`, and runtime packs such
as `xyona-cdp-pack`. This roadmap deliberately does not design the future DAW
plugin runtime. The plugin-runtime idea is used only as an architectural stress
test.

Document convention:

- Active root work is tracked as `ROADMAP_...`.
- `REPORT_...` files are implementation or review evidence.
- Completed or superseded root roadmaps and reports can be archived under
  `docs/done/`.
- This file is not a completion report.

## Executive Decision

The current parameter system has the right broad architecture, but the previous
roadmap was not directly implementable. The implementation order must change.

The correct sequence is:

1. Characterize the current automation/domain bugs.
2. Add target identity and resolver interfaces before value migration.
3. Fix new automation record/playback for resolved targets.
4. Reconcile legacy automation in a descriptor-aware Lab pass, not in
   `ProjectState`.
5. Define the Core semantics contract and pack ABI/metadata transport.
6. Migrate Lab surfaces in narrow stages with an explicit temporary bypass list.
7. Replace or formalize the existing audio automation event path.
8. Optimize runtime targets and finish modulation, smoothing, macros, value
   sources, and UI diagnostics.

The first product bug remains the same: parameter automation mixes plain/native
parameter values with normalized `0..1` values. But that bug cannot be fixed
reliably until automation code can resolve target semantics and preserve full
target identity.

## Verified Baseline

### F0: Automation value-domain mismatch

Verified facts:

- `TimelineParameterAutomationLane` initializes its edit range with
  `setValueRange(0.0, 1.0)`.
- `TimelineAutomationPoint.value` is an untyped `double`.
- `AutomationRecorder` writes `event.baseValue` directly into point values.
  That value comes from `ParameterControlHub` and is plain/native.
- `TimelineLaneSignalSource` exposes parameter automation as
  `SignalDomain::Unipolar01` and can normalize/clamp to `0..1`.
- `AutomationPlaybackEngine` sends evaluated values to
  `ParameterControlHub::setAutomationBase`, whose API expects raw/plain values.

Conclusion: stored automation point values are not self-describing. Some paths
treat them as normalized `0..1`; other paths treat them as plain/native values.

### F1: `ParamDesc` is not a complete parameter semantics contract

`ParamDesc` currently carries basic metadata: id, label, type, min/max/default,
enum values, unit, display, precision, availability, topology, and scope.

It does not carry first-class:

- scale/mapping: linear, log, dB, frequency, exponential
- step/quantization
- parse/format policy
- automation policy
- modulation policy
- MIDI-learn policy
- smoothing/dezipper ownership

### F2: Lab has multiple conversion paths

Conversion currently exists outside a single codec, including:

- `ParamFormatter`
- text field views
- canvas interaction/model code
- timeline automation lane drawing/editing
- MIDI mapping
- modulation math
- hub bounds/clamping
- legacy parameter model helpers

### F3: CDP metadata is richer than Lab consumption

`xyona-cdp-pack` YAML/generated metadata contains `ui.step` and `ui.scale`,
including `linear_db`. Lab does not currently consume these as first-class
parameter semantics.

### F4: Full target identity is incomplete

`ParamAddress` supports optional `slotIndex`, and `storageKey()` supports
`param@slot=N`. However, some routes/mappings persist target node + parameter
name only, so slot identity can be lost before runtime.

### F5: Topology policy is not enforced early enough

Topology parameters are marked, but Timeline/MIDI/Modulation target paths do
not consistently reject them before they become ordinary control targets.

### F6: `ProjectState` cannot do descriptor-aware migration

The project state layer can read and write persisted lane data, but it does not
have reliable descriptor, pack discovery, operator revision, or slot-topology
context. Any migration that needs target semantics must run in a Lab
post-load/reconciliation layer above raw state reading.

### F7: Recorder/playback do not have a semantic resolver

`AutomationRecorder` currently receives a lane resolver and point appender.
`AutomationPlaybackEngine` receives lanes and a `ParameterControlHub`. Neither
has a descriptor/semantic resolver dependency. Value-domain fixes must add this
explicit dependency before converting stored values.

## Target Architecture

### Value domains

Every subsystem boundary must say which value domain it carries.

```cpp
enum class ParamValueDomain
{
    Plain,          // native units: dB, Hz, enum index, bool 0/1
    Normalized01,   // canonical 0..1 automation/control position
    DisplayText,    // text parsed/formatted by the codec
    PlainDelta,     // native-unit modulation delta
    NormalizedDelta // normalized modulation delta
};
```

Rules:

- `ParameterControlHub` stores and emits final plain values.
- New parameter automation points store normalized `0..1` values.
- Recorder converts plain -> normalized.
- Playback converts normalized -> plain.
- UI may display native values, but persisted point values remain normalized.
- Legacy lanes carry explicit migration status until reconciled.

### Target identity

All persisted parameter targets must converge on full `ParamAddress`:

```text
nodeId + paramId + optional slotIndex
```

Compatibility rule:

- Old node+param fields remain migration input only.
- New schema must preserve optional `slotIndex`.
- Runtime hashes derive from `ParamAddress::storageKey()` after address
  resolution.

### Resolver interface

Automation cannot own descriptor discovery. It needs an injected resolver.

```cpp
enum class ParamResolveStatus
{
    Resolved,
    MissingNode,
    MissingParameter,
    MissingDescriptor,
    PackUnavailable,
    TopologyNotControllable,
    UnsupportedScope
};

struct ResolvedParamTarget
{
    ParamAddress address;
    xyona::ParamDesc desc;
    ParamResolveStatus status { ParamResolveStatus::MissingDescriptor };
    std::uint64_t descriptorRevision { 0 };
};

class IParamTargetResolver
{
public:
    virtual ~IParamTargetResolver() = default;
    virtual ResolvedParamTarget resolve(const ParamAddress& address) const = 0;
};
```

Initial resolver can use current `ParamDesc` min/max/type. Later milestones
replace that with full `ParamSemantics`.

### Core semantics and codec

The final codec should be host-free and deterministic. It belongs in
`xyona-core` or a host-free shared layer, not in Lab UI code.

```cpp
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

struct ParamControlPolicy
{
    bool automatable { true };
    bool recordable { true };
    bool modulatable { true };
    bool midiLearnable { true };
    bool topology { false };
};

struct ParamSemantics
{
    std::string id;
    std::string type;
    double minPlain { 0.0 };
    double maxPlain { 1.0 };
    double defaultPlain { 0.0 };
    ParamScale scale { ParamScale::Linear };
    ParamStepPolicy step {};
    ParamSmoothingKind smoothing { ParamSmoothingKind::BlockStable };
    ParamControlPolicy control {};
    std::string unit;
    std::vector<std::string> enumValues;
};
```

Pack transport must be decided before Lab treats pack semantics as
authoritative:

- Option A: add semantic fields to `ParamDesc`.
- Option B: keep `ParamDesc` stable and add versioned semantic sidecar metadata.
- Option C: extend the pack ABI with semantic fields and require the new
  semantics contract for parameterized runtime packs.

The roadmap does not assume which option wins. M3 explicitly decides it.

## Roadmap Overview

Implementation order:

1. **M0: Baseline characterization and roadmap correction**
2. **M1: Target identity and resolver foundation**
3. **M2: Automation value-domain fix for resolved targets**
4. **M3: Core semantics contract and pack transport decision**
5. **M4: Lab semantic resolver and staged conversion migration**
6. **M5: Pack semantics and target policy enforcement**
7. **M6: Authoritative realtime/offline automation runtime**
8. **M7: Compiled runtime parameter targets**
9. **M8: Modulation, smoothing, value sources, and macros**
10. **M9: Persistence migration UX and highend diagnostics**

M0-M2 fix correctness. M3-M5 make the contract clean. M6-M9 make the system
highend and scalable.

## M0: Baseline Characterization And Roadmap Correction

Goal: make the roadmap implementable and lock down the current bug behavior.

### Commit M0.1

`docs(parameters): make automation roadmap implementable`

Changes:

- Correct branch metadata.
- Incorporate the technical review blockers.
- Define resolver and migration boundaries.

Acceptance:

- Roadmap no longer requires descriptor-aware migration inside `ProjectState`.
- Roadmap no longer claims a global "no conversion bypass" gate before all
  conversion paths are scheduled.

### Commit M0.2

`test(parameters): characterize automation value-domain mismatch`

Tests:

- Record/playback for a `0..1` float parameter.
- Record/playback for a non-`0..1` float parameter, e.g. `-96..24 dB`.
- Manual point editing for the non-`0..1` target.
- Playback path into `ParameterControlHub`.

Acceptance:

- Tests prove current point values are domain-ambiguous.

### Commit M0.3

`test(parameters): characterize target identity and topology gaps`

Tests:

- Topology target selection/routing where it currently leaks.
- Slot target identity loss in modulation/MIDI route data.

Acceptance:

- Gaps are covered before schema/policy changes.

## M1: Target Identity And Resolver Foundation

Goal: add the prerequisites needed by the value-domain fix.

### Commit M1.1

`lab(parameters): introduce parameter target resolver interface`

Changes:

- Add `IParamTargetResolver` or equivalent Lab-local interface.
- Return status for missing descriptor, missing param, pack unavailable,
  topology-ineligible, and unsupported scope.
- Provide an initial adapter backed by current Canvas/operator descriptors.

Acceptance:

- Resolver can answer for current global `ParamAddress` targets.
- Resolver failure paths are testable.

### Commit M1.2

`lab(timeline): inject target resolver into automation recorder and playback`

Changes:

- `AutomationRecorder` can resolve the focused lane target before writing.
- `AutomationPlaybackEngine` can resolve each lane target before emitting.
- Missing/unresolved targets are skipped non-destructively.

Acceptance:

- Recorder/playback no longer need to guess descriptor context.
- No stored values are converted yet.

### Commit M1.3

`lab(timeline): persist full ParamAddress for automation lanes`

Changes:

- Persist optional `slotIndex` for parameter automation lane targets.
- Keep old node+param fields as compatibility input.
- Do not require descriptor lookup in raw `ProjectState` read methods.

Acceptance:

- Existing lanes load.
- New lanes preserve full target address.

### Commit M1.4

`lab(modulation): migrate route target storage to full ParamAddress`

Changes:

- Store full target address in `ModulationRoute`.
- Old node+param fields migrate to global address.
- Prepared route/runtime paths use full address.

Acceptance:

- Slot identity is not lost in modulation route data.

### Commit M1.5

`lab(midi): migrate MIDI mappings to full ParamAddress`

Changes:

- Store full target address in `MidiMapping`.
- Old target node+param fields migrate to global address.

Acceptance:

- Slot identity is not lost in MIDI mapping data.

## M2: Automation Value-Domain Fix For Resolved Targets

Goal: fix new recording/playback without unsafe legacy conversion.

### Commit M2.1

`lab(timeline): add automation value-domain schema`

Changes:

- Add lane value-domain metadata:
  - `LegacyUnknown`
  - `Normalized01`
  - `LegacyPlain`
  - `Unresolved`
- New lanes default to `Normalized01`.
- Raw state load preserves existing values and marks missing metadata as
  `LegacyUnknown`.

Acceptance:

- `ProjectState` only reads/writes markers. It does not perform descriptor-aware
  conversion.

### Commit M2.2

`lab(parameters): add descriptor-backed linear automation codec adapter`

Changes:

- Add minimal plain <-> normalized conversion from current `ParamDesc`.
- Support float, int, bool, enum.
- This is a temporary Lab adapter until Core codec lands.

Acceptance:

- Resolved targets can convert plain/native to normalized `0..1`.
- Edge behavior is tested.

### Commit M2.3

`lab(timeline): record resolved automation as normalized values`

Changes:

- Recorder resolves lane target.
- If resolved and controllable, convert plain hub base value -> normalized point.
- If unresolved, skip recording or record disabled according to explicit status.

Acceptance:

- Recording a non-`0..1` target no longer stores native values into point data.

### Commit M2.4

`lab(timeline): play normalized automation as plain values`

Changes:

- Playback resolves lane target.
- `Normalized01` lanes decode normalized -> plain before hub emission.
- Legacy/unresolved lanes do not silently emit guessed values.

Acceptance:

- `ParameterControlHub` receives plain/native values.
- Existing unresolved legacy lanes are preserved but not guessed.

### Commit M2.5

`lab(timeline): add descriptor-aware post-load automation reconciliation`

Changes:

- Run after Canvas/operator descriptors are available.
- For `LegacyUnknown` lanes:
  - target unresolved: preserve raw values, mark unresolved
  - any value outside `0..1`: treat as `LegacyPlain`, convert plain -> normalized
  - all values inside `0..1`: preserve as assumed normalized and mark ambiguous
- Store migration status separately from raw state read.

Acceptance:

- Legacy conversion never happens in low-level `ProjectState`.
- Ambiguous legacy lanes are visible and deterministic.

### Commit M2.6

`test(timeline): verify automation domain reconciliation`

Tests:

- New record/playback for non-`0..1` float.
- Bool/int/enum resolved target.
- Unresolved target preservation.
- `LegacyPlain` conversion.
- `LegacyUnknown` assumed-normalized diagnostic.

Acceptance:

- F0 is fixed for resolved targets.
- Legacy behavior is deterministic and non-destructive.

## M3: Core Semantics Contract And Pack Transport

Goal: define the long-term host-free semantics and how packs transport them.

### Commit M3.1

`core(parameters): decide parameter semantic transport contract`

Changes:

- Choose and document one transport:
  - `ParamDesc` fields
  - versioned sidecar metadata
  - strict pack ABI extension
- Define strict pack import behavior.
- Define Core-native missing-metadata defaults.

Acceptance:

- Lab can consume pack semantics without parsing ad hoc metadata in multiple
  places.

### Commit M3.2

`core(parameters): introduce ParamValueDomain and ParamScale`

Changes:

- Add host-free enums/structs.
- Preserve existing `ParamDesc` compatibility.

### Commit M3.3

`core(parameters): add ParamSemantics and ParamValueCodec`

Changes:

- Implement linear float/int/bool/enum conversion.
- Add roundtrip and edge tests.

### Commit M3.4

`core(parameters): add step, nonlinear scale, and control policy`

Changes:

- Add step/quantization.
- Add dB/log/frequency/exponential mappings.
- Add automatable/recordable/modulatable/MIDI policy.
- Add topology-derived defaults.

### Commit M3.5

`core(packs): expose parameter semantics through chosen transport`

Changes:

- Implement the M3.1 transport decision.
- Add ABI/version/strict-rejection tests.

Acceptance for M3:

- Core owns deterministic value conversion.
- Pack semantics have a defined strict transport path.

## M4: Lab Resolver And Staged Conversion Migration

Goal: migrate Lab consumers without claiming every path is done too early.

### Transitional bypass list

Until the listed milestones land, these paths may still contain compatibility
conversion logic:

- MIDI range override behavior until M5/M8.
- Existing audio runtime hash/update path until M6/M7.
- Legacy parameter model helpers until all UI surfaces are migrated.

No new conversion path may be added outside the codec/resolver unless it is on
this list and has a removal milestone.

### Commit M4.1

`lab(parameters): add resolved parameter semantics service`

Changes:

- Resolve Core semantics plus Lab target address.
- Include descriptor revision/cache invalidation.
- Preserve resolver failure status.

### Commit M4.2

`lab(parameters): route ParamFormatter through ParamValueCodec`

Changes:

- `rawToNormalized`, `normalizedToRaw`, `rawToText`, and `textToRaw` delegate to
  the codec.
- Existing call sites keep compiling.

### Commit M4.3

`lab(parameters): migrate text field and numeric controls to codec`

Changes:

- Text field views stop doing their own conversion.
- Step/enum/bool formatting uses the codec.

### Commit M4.4

`lab(canvas): migrate canvas parameter editing to semantics service`

Changes:

- Canvas mini parameter gestures and readouts use resolved semantics.
- Canvas code stops inventing scale behavior for migrated paths.

### Commit M4.5

`lab(timeline): make automation lane UI target-aware`

Changes:

- Stored point values remain normalized.
- Lane display/edit overlays show target-native values through codec.
- Step/bool/enum targets quantize through codec.

Acceptance for M4:

- Formatter, text controls, Canvas editing, and timeline automation UI use the
  same semantics.
- Transitional bypass list is still explicit and shrinking.

## M5: Pack Semantics And Target Policy Enforcement

Goal: consume pack semantics and reject invalid targets at selection/compile
time, not by teaching the hub to be a descriptor registry.

### Commit M5.1

`cdp-pack(parameters): verify generated ui scale and step metadata`

Changes:

- Ensure `ui.scale` and `ui.step` are generated consistently.
- Add generator/golden tests where practical.

### Commit M5.2

`lab(parameters): consume pack scale and step semantics`

Changes:

- Map `linear_db` and other known scales to Core semantics.
- Map step to step policy.
- Preserve safe defaults for missing metadata.

### Commit M5.3

`lab(parameters): add target eligibility service`

Changes:

- Check automatable/recordable/modulatable/MIDI-learnable/topology policy.
- Use resolver status and semantics.
- Keep `ParameterControlHub` focused on value arbitration.

### Commit M5.4

`lab(timeline midi modulation): reject ineligible targets`

Changes:

- Timeline target selectors reject non-automatable targets.
- MIDI learn rejects non-MIDI-learnable targets.
- Modulation assignment rejects non-modulatable targets.
- Existing invalid persisted targets load disabled/unresolved with diagnostics.

Acceptance for M5:

- Topology parameters cannot become ordinary automation/MIDI/modulation targets.
- CDP dB/step params are semantically visible to Lab.

## M6: Authoritative Realtime/Offline Automation Runtime

Goal: define one render-truth automation path.

### Commit M6.1

`lab(audio): inventory automation event producers`

Changes:

- Document current producers of `AutomationEventBuffer`.
- Decide whether existing event path is:
  - replaced
  - kept as compatibility adapter
  - removed

Acceptance:

- The roadmap no longer introduces a second active render-truth path.

### Commit M6.2

`lab(automation): add prepared parameter automation runtime`

Changes:

- Compile lanes into resolved target + prepared scalar evaluation + codec.
- Ordinary parameter automation remains block-stable.

### Commit M6.3

`lab(audio): apply prepared automation in AudioGraphProcessor`

Ordering:

1. restore base snapshot
2. drain live parameter queue
3. apply prepared automation
4. apply modulation
5. process nodes

Acceptance:

- Ordering is expressed in terms of existing processor APIs.

### Commit M6.4

`lab(offline): use prepared automation runtime for offline render`

Changes:

- Offline render uses the same prepared automation data.
- Message-thread playback is preview/control only.

Acceptance for M6:

- Realtime and offline parameter traces match.
- Automation does not depend on message-thread cadence.

## M7: Compiled Runtime Parameter Targets

Goal: reduce hot-path lookup work after semantics and runtime ownership are
settled.

### Commit M7.1

`lab(audio): build parameter index maps in graph runtime cache`

Status: completed in `xyona-lab` commit `f6152bd8`.

Changes:

- Per-node hash -> snapshot index maps.
- Collision diagnostics remain.

### Commit M7.2

`lab(parameters): introduce CompiledParamTarget`

Status: completed in `xyona-lab` commit `2bdd3883`.

Changes:

- Resolve full `ParamAddress` to node index, snapshot index, storage hash, and
  semantics.

### Commit M7.3

`lab(audio): apply queued updates through compiled targets`

Status: completed in `xyona-lab` commit `d8adbac4`.

Changes:

- Prefer direct index application.
- Keep hash fallback during transition.

### Commit M7.4

`lab(audio): update host adapter parameter bindings to prepared indices`

Status: completed in `xyona-lab` commit `566dcd07`.

Changes:

- Reduce repeated binding scans where practical.

Acceptance for M7:

- Existing realtime updates still work.
- Large graph parameter stress tests show no regression and lower lookup cost.

## M8: Modulation, Smoothing, Value Sources, Macros

Goal: finish advanced parameter behavior once value domains and target identity
are stable.

### Commit M8.1

`core(parameters): add modulation contribution modes`

Status: completed in `xyona-core` commit `e37bbd2`.

Modes:

- plain additive delta
- normalized bipolar offset
- multiplicative
- disabled

### Commit M8.2

`lab(modulation): map modulation through target semantics`

Status: completed in `xyona-lab` commit `1073dc6a`.

Changes:

- Replace min/max-only modulation math with codec-aware mapping.
- Remove modulation from the transitional bypass list.

### Commit M8.3

`lab(audio): apply host smoothing where policy allows`

Status: completed across `xyona-core` commit `aa66e4d`,
`xyona-cdp-pack` commit `72cc621`, and `xyona-lab` commit `c7d7fdfd`.

Changes:

- Core exposes `ParamSmoothingKind` through descriptors, semantics, and pack
  ABI v2.3.
- Pack parameter descriptors below v2.3 are rejected; no v2.2 fallback is
  accepted.
- CDP pack generated metadata emits explicit smoothing ownership.
- Host ramp only when policy says host-owned.
- Operator-owned smoothing remains in Core/pack operators.

### Commit M8.4

`lab(parameters): quarantine incomplete Expr and Bind sources`

Changes:

- Hide or mark incomplete source kinds until evaluated deterministically.

### Commit M8.5

`lab(parameters): implement deterministic value-source evaluation`

Only if product scope requires `Expr`/`Bind` now.

Requirements:

- dependency graph
- cycle detection
- missing-target policy
- offline/realtime parity
- migration behavior

### Commit M8.6

`lab(macros): define macro target binding contract`

Changes:

- Macro value domain.
- Target mapping.
- Missing target handling.
- Patch persistence.

Acceptance for M8:

- Modulation is semantically correct for nonlinear parameters.
- Smoothing ownership is explicit.
- Incomplete value sources are not silently product-visible.

## M9: Persistence Migration UX And Diagnostics

Goal: make the system inspectable and patch-compatible.

### Commit M9.1

`lab(project): version parameter automation schema`

Persist:

- value domain
- full target address
- semantic revision
- migration status
- unresolved target status

### Commit M9.2

`lab(project): add parameter target migration records`

Handle:

- renamed params
- removed params
- changed ranges
- pack unavailable
- slot count changes
- macro target changes

### Commit M9.3

`lab(ui): add parameter source breakdown`

Show:

- manual
- MIDI
- automation
- macro/bind
- modulation
- clamp/quantize
- smoothing

### Commit M9.4

`lab(ui): add target-aware automation diagnostics`

Show:

- units
- dB/Hz/native labels
- step/grid hints
- unresolved target status
- ambiguous legacy migration status

Acceptance for M9:

- Old patches do not silently change sound.
- Users can inspect why a parameter has its final value.
- Missing/migrated targets are visible and non-destructive.

## Branch Strategy

Planning/review branch:

- `parameter-automation-review`

Implementation branch:

- `parameter-automation-system`

Historical baseline branch:

- `parameter-automation-m0-baseline`

Cross-repo rule:

- Use `parameter-automation-system` in each repository touched by the roadmap.
- Do not create branches for untouched repositories until their milestone
  actually edits that repository.
- Keep milestone boundaries as clean commit groups and track every commit in the
  implementation report.

## Minimal First Implementation Slice

Start here, not with Core codec or UI polish:

1. M0.2 characterization tests.
2. M1.1 target resolver interface.
3. M1.2 inject resolver into recorder/playback.
4. M1.3 full automation target address persistence.
5. M2.1 value-domain metadata.
6. M2.2 temporary descriptor-backed linear codec adapter.
7. M2.3 recorder conversion for resolved targets.
8. M2.4 playback conversion for resolved targets.
9. M2.6 parity tests.

This fixes new automation correctness while preserving unresolved legacy data.

## Review Gates

No milestone is complete unless:

- It has tests or a documented reason tests are not possible yet.
- It does not require descriptor-aware logic inside `ProjectState`.
- It preserves unresolved targets non-destructively.
- It does not add new node+param-only target storage except as a migration
  adapter.
- It does not teach `ParameterControlHub` to become a descriptor registry.
- It updates the transitional bypass list when conversion paths move to the
  codec.

## Final Definition Of Done

The parameter system is highend-ready when:

- Automation point storage has explicit value domains.
- New automation records and plays back non-`0..1` parameters correctly.
- Legacy lanes reconcile through a descriptor-aware post-load pass.
- Full `ParamAddress` identity is preserved across automation, modulation, and
  MIDI.
- Core owns deterministic parameter conversion.
- Pack semantic transport is versioned and tested.
- Lab conversion paths flow through the semantics service, with no remaining
  unplanned bypasses.
- Realtime and offline automation produce matching parameter traces.
- Topology parameters are rejected by ordinary automation, MIDI, and modulation.
- Runtime parameter application uses compiled targets where practical.
- Smoothing ownership is explicit.
- Incomplete value sources are complete or product-hidden.
- Patch migration is deterministic and visible.
