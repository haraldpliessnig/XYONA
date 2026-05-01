# Roadmap: Parameter Automation System

**Status:** Active planning
**Started:** 2026-05-01
**Branch:** `operator-slot-system`
**Applies to:** `xyona-core`, `xyona-lab`, `xyona-cdp-pack`, future runtime packs
**Reference:** `IDEA_XYONA_PLUGIN_RUNTIME.md`

Scope: Standalone XYONA only: `xyona-lab`, `xyona-core`, and runtime packs such
as `xyona-cdp-pack`. This roadmap deliberately does not design the future DAW
plugin runtime. It uses the plugin-runtime idea only as an architectural stress
test.

Document convention:

- Active root work is tracked as `ROADMAP_...`.
- Completed or superseded root roadmaps/reports move to `docs/done/`.
- `REPORT_...` files are reserved for implementation tracking and completed
  implementation evidence. This file must not be used as a completion report.
- When implementation work for a milestone completes, create or update a
  separate `REPORT_PARAMETER_AUTOMATION_SYSTEM_YYYY-MM-DD.md` and archive it
  under `docs/done/` only when the work is closed or superseded.

## Executive Decision

The current parameter system is structurally good enough to harden. It should
not be rewritten. The correct path is a staged contract hardening:

1. Fix parameter automation value domains.
2. Introduce one canonical parameter semantics and value codec.
3. Migrate Lab surfaces onto that codec.
4. Make automation playback/offline execution authoritative and deterministic.
5. Finish slot-aware addressing, topology policy, smoothing, and diagnostics.

The first blocking bug is value-domain correctness. Parameter automation
currently mixes plain/native parameter values with normalized `0..1` values.
This explains the observed symptom that automated parameters can collapse to
`0..1` behavior, and in some cases look like only `0` and `1` are available.

## Verified Critical Facts

These facts were verified against the current source tree.

### F0: Automation value-domain mismatch

Evidence:

- `TimelineParameterAutomationLane` initializes its edit range with
  `setValueRange(0.0, 1.0)`.
- `TimelineAutomationPoint.value` is an untyped `double`.
- `AutomationRecorder` writes `event.baseValue` directly into point values.
  `event.baseValue` comes from `ParameterControlHub` and is plain/native.
- `TimelineLaneSignalSource` exposes parameter automation as
  `SignalDomain::Unipolar01` and can normalize/clamp to `0..1`.
- `AutomationPlaybackEngine` sends evaluated values to
  `ParameterControlHub::setAutomationBase`, whose API names the value
  `rawValue`.

Conclusion:

Automation points have no explicit domain. Some paths treat them as normalized
`0..1`; some paths treat them as plain/native parameter values. This is the
first issue to fix.

### F1: `ParamDesc` is not a full semantics contract

`ParamDesc` has id, label, type, min/max/default, enum values, unit, display,
precision, availability, topology flag, and scope support. It does not define:

- scale/mapping: linear, log, dB, frequency, exponential
- step/quantization
- parse/format policy
- automation policy
- modulation policy
- smoothing/dezipper ownership
- MIDI-learn policy

### F2: Lab has multiple conversion truths

Conversion or interpretation currently exists in multiple places:

- `ParamFormatter`
- text field views
- canvas interaction/model code
- timeline automation lane drawing/editing
- MIDI mapping
- modulation mapping
- hub bounds/clamping

This must collapse to one codec.

### F3: CDP pack parameter metadata is richer than Lab consumption

`xyona-cdp-pack` operator YAML/generated metadata contains `ui.step` and
`ui.scale`, including `linear_db`. Lab does not currently consume this as
first-class parameter semantics.

### F4: Topology policy is not enforced early enough

Topology parameters exist and are marked, but Timeline/MIDI/Modulation target
paths do not consistently filter them before they become ordinary control
targets.

### F5: Slot addressing is not end-to-end

`ParamAddress` can store `slotIndex`, and `storageKey()` supports
`param@slot=N`. But `ModulationRoute` currently stores target node + param name
only, so slot-specific target identity is lost in that path.

### F6: Runtime parameter targeting is still lookup-heavy

The realtime path has stable hashes and block snapshots, but direct compiled
target indices do not exist yet. Some hot paths still scan by hash/binding
vector.

### F7: Value sources are partly modeled but not complete

`Const` and `Param` can be evaluated. `Expr` and `Bind` currently resolve to no
runtime value. They should not be treated as finished product features until
they have deterministic evaluation, dependency handling, and migration rules.

## Target Architecture

### Value domains

Every boundary-crossing value must declare its domain.

```cpp
enum class ParamValueDomain
{
    Plain,          // native parameter units, e.g. dB, Hz, enum index
    Normalized01,   // canonical automation/control position
    DisplayText,    // text representation parsed/formatted through codec
    PlainDelta,     // native-unit modulation delta
    NormalizedDelta // normalized modulation delta
};
```

Target rule:

- `ParameterControlHub` stores and emits final plain values.
- Timeline parameter automation stores normalized `0..1` point values.
- Recorder converts plain -> normalized before writing points.
- Playback converts normalized -> plain before writing automation base into the
  hub.
- UI can display native values, but persisted automation points remain
  normalized.

### Parameter semantics

Add a JUCE-free semantic contract, preferably in `xyona-core` if it remains
host-free.

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

### Parameter codec

All conversions go through one codec.

```cpp
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

Codec requirements:

- Deterministic and JUCE-free.
- Bool and enum values quantize.
- Integer and stepped floats snap according to policy.
- Nonlinear mapping is explicit.
- Parse/format is stable for project persistence.
- UI localization is layered above persistence formatting.

### Lab semantic resolver

Lab should resolve all parameter metadata once and provide it to consumers.

Inputs:

- Core `ParamDesc`
- pack param meta JSON
- Lab defaults
- topology policy
- slot scope

Output:

```cpp
struct ResolvedParamSemantics
{
    ParamAddress address;
    xyona::ParamDesc desc;
    ParamSemantics semantics;
    ParamValueCodec codec;
    std::uint64_t semanticRevision { 0 };
};
```

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

### Runtime compiled targets

Parameter runtime should move from hash lookup as primary addressing to compiled
targets.

```cpp
struct CompiledParamTarget
{
    NodeId nodeId;
    ParamAddress address;
    audio::ParamKey storageKeyHash;
    std::uint32_t nodeIndex;
    std::uint32_t snapshotValueIndex;
    ParamSemantics semantics;
};
```

Hashes remain useful for persistence, fallback, diagnostics, and compatibility.
Hot application paths should prefer compiled indices.

## Roadmap Overview

The roadmap is ordered by dependency and product risk.

1. **M0: Characterize and protect current behavior**
2. **M1: Fix automation value-domain correctness**
3. **M2: Add canonical semantics and codec**
4. **M3: Migrate Lab surfaces to the codec**
5. **M4: Consume pack semantics and harden policies**
6. **M5: Make playback/offline automation authoritative**
7. **M6: Compile runtime parameter targets**
8. **M7: Finish slot-aware modulation/MIDI/automation**
9. **M8: Add smoothing, value-source, and macro contracts**
10. **M9: Add persistence migration and highend UI diagnostics**

M0-M1 are the urgent correctness block. M2-M4 make the system clean. M5-M9 make
it highend and expandable.

## M0: Baseline and Characterization

Goal: prove current behavior and create safety tests before changing semantics.

### Commit M0.1

`docs(parameters): add parameter automation roadmap`

Changes:

- Keep this document as the implementation guide.
- No production code changes.

Acceptance:

- The plan is clear enough to drive follow-up implementation batches.

### Commit M0.2

`test(parameters): characterize automation value domains`

Tests:

- Record/playback for a `0..1` float parameter.
- Record/playback for a non-`0..1` float parameter, e.g. `-96..24 dB`.
- Manual automation point editing for the same non-`0..1` parameter.
- Playback path into `ParameterControlHub`.

Acceptance:

- Tests demonstrate the existing domain ambiguity.
- The failing/characterization behavior is explicitly documented.

### Commit M0.3

`test(parameters): characterize topology and slot target gaps`

Tests:

- Topology parameter can currently be selected or routed where it should not.
- Slot target identity is lost in modulation route path.

Acceptance:

- Current gaps are covered before policy changes.

## M1: Critical Automation Value-Domain Fix

Goal: make parameter automation correct before broader refactoring.

Design decision:

- New parameter automation lanes store normalized `0..1` values.
- `ParameterControlHub` continues to receive plain/native values.
- Recorder and playback perform conversion at the edge.

### Commit M1.1

`lab(timeline): add automation point value-domain metadata`

Changes:

- Add value-domain metadata to parameter automation lanes.
- Supported values initially:
  - `LegacyUnknown`
  - `Normalized01`
  - `LegacyPlain`
- Persist the field in project state.
- Default newly created lanes to `Normalized01`.

Acceptance:

- Existing projects load without data loss.
- New lanes write explicit domain metadata.

### Commit M1.2

`lab(parameters): add minimal linear ParamValueCodec adapter`

Changes:

- Add a minimal codec adapter using current `ParamDesc` min/max/type.
- Support float, int, bool, and enum.
- Do not solve CDP nonlinear scales yet.

Acceptance:

- Plain <-> normalized roundtrips for current descriptor data.
- Bool/enum/int values sanitize deterministically.

### Commit M1.3

`lab(timeline): record automation points as normalized values`

Changes:

- Recorder resolves the lane target descriptor.
- Recorder converts hub plain base values to normalized point values.
- Last-value dedupe compares normalized values or compares plain values through
  codec consistently.

Acceptance:

- Recording a `-96..24 dB` parameter does not store raw dB into a `0..1` point.
- Recording a `0..1` parameter remains unchanged.

### Commit M1.4

`lab(timeline): decode parameter automation playback to plain values`

Changes:

- Playback evaluates normalized lane values.
- Playback converts normalized -> plain before calling
  `ParameterControlHub::setAutomationBase`.
- Parameter automation playback no longer relies on generic unipolar signal
  source normalization as the semantic conversion step.

Acceptance:

- A point at normalized `0.5` maps to the target parameter's plain midpoint.
- Hub receives plain/native values.

### Commit M1.5

`lab(timeline): migrate legacy automation lane value domains`

Migration:

- If lane has explicit domain, use it.
- If missing and target is unresolved, preserve raw points and mark unresolved.
- If missing and any value is outside `0..1`, treat as `LegacyPlain` and convert
  plain -> normalized.
- If missing and all values are inside `0..1`, treat as
  `LegacyAssumedNormalized`; preserve values but record a migration diagnostic
  because old data is inherently ambiguous.

Acceptance:

- Migration is deterministic.
- Ambiguous old lanes are not silently reinterpreted without a marker.

### Commit M1.6

`test(timeline): verify automation record playback parity`

Tests:

- Manual plain value -> recorded normalized point -> playback plain value.
- Float range not equal to `0..1`.
- Bool/int/enum target.
- Legacy outside-`0..1` migration.
- Legacy inside-`0..1` assumed-normalized migration.

Acceptance:

- F0 is fixed.

## M2: Canonical Core Parameter Semantics

Goal: create the host-free contract used by Core, packs, and Lab.

### Commit M2.1

`core(parameters): introduce ParamValueDomain and ParamScale`

Changes:

- Add JUCE-free enums and data structs.
- Do not break existing `ParamDesc` users.

### Commit M2.2

`core(parameters): add ParamSemantics and ParamValueCodec`

Changes:

- Add codec implementation for current linear descriptor behavior.
- Include bool, enum, int, float.
- Add tests in `xyona-core`.

### Commit M2.3

`core(parameters): add step and quantization policy`

Changes:

- Add step snapping.
- Define enum/bool/int quantization.
- Add edge-case tests.

### Commit M2.4

`core(parameters): add nonlinear scale support`

Changes:

- Add dB, log, frequency, exponential mappings.
- Define invalid range fallback.
- Add roundtrip tests.

### Commit M2.5

`core(parameters): add control and smoothing policies`

Changes:

- Add `automatable`, `recordable`, `modulatable`, `midiLearnable`.
- Add smoothing ownership policy.
- `isTopology` resolves to ordinary control policies disabled by default.

Acceptance for M2:

- A host-free codec exists and is tested.
- Existing simple parameter behavior remains compatible.

## M3: Lab Resolver and Surface Migration

Goal: remove duplicate interpretation from Lab.

### Commit M3.1

`lab(parameters): add ResolvedParamSemantics service`

Changes:

- Resolve `ParamDesc` into `ParamSemantics`.
- Include descriptor revision/cache invalidation.
- Expose lookup by full `ParamAddress`.

### Commit M3.2

`lab(parameters): route ParamFormatter through ParamValueCodec`

Changes:

- `rawToNormalized`, `normalizedToRaw`, `rawToText`, and `textToRaw` delegate to
  codec.
- Keep existing call sites compiling.

### Commit M3.3

`lab(parameters): remove duplicate text-field conversions`

Changes:

- Text field views use formatter/codec.
- Units and steps roundtrip through the same logic.

### Commit M3.4

`lab(canvas): use resolved semantics for canvas parameter editing`

Changes:

- Canvas interaction/model code stops doing ad hoc min/max conversion.
- Canvas default/readout text uses the codec.

### Commit M3.5

`lab(midi): map MIDI through target semantics`

Changes:

- MIDI normalized input maps through codec.
- Mapping min/max becomes explicit override policy, not the default semantics.

### Commit M3.6

`lab(timeline): make automation lane UI target-aware`

Changes:

- Persisted point values remain normalized.
- Lane display and editing can show plain/display values through codec.
- Step/bool/enum targets quantize correctly.

Acceptance for M3:

- There is no user-facing parameter conversion path that bypasses the codec.
- Existing linear behavior remains stable.

## M4: Pack Semantics and Policy Enforcement

Goal: make packs first-class semantic providers and block invalid targets early.

### Commit M4.1

`cdp-pack(parameters): ensure ui scale and step metadata is generated`

Changes:

- Verify `ui.scale` and `ui.step` in generated param metadata.
- Add generation tests where possible.

### Commit M4.2

`core(packs): expose resolved param meta for pack descriptors`

Changes:

- Provide a stable helper for param meta access.
- Avoid scattered JSON parsing in Lab.

### Commit M4.3

`lab(parameters): consume pack ui scale and step semantics`

Changes:

- Map `linear_db` to dB semantics.
- Map `step` to step policy.
- Preserve safe defaults when metadata is missing.

### Commit M4.4

`lab(parameters): enforce topology control policy`

Changes:

- Topology params are not automatable/modulatable/MIDI-learnable by default.
- Hub/target resolver rejects invalid ordinary control writes with diagnostics.

### Commit M4.5

`lab(timeline): filter automation targets by semantics policy`

Changes:

- Timeline target selectors hide/reject non-automatable params.
- Existing invalid lanes load as unresolved/disabled, not silently active.

### Commit M4.6

`lab(midi modulation): filter targets by semantics policy`

Changes:

- MIDI learn rejects non-MIDI-learnable targets.
- Modulation assignment rejects non-modulatable targets.

Acceptance for M4:

- CDP dB/step parameters behave semantically in Lab.
- Topology parameters cannot become ordinary automation/modulation/MIDI targets.

## M5: Authoritative Automation Runtime

Goal: realtime playback and offline render use the same automation truth.

### Commit M5.1

`lab(automation): introduce prepared parameter automation runtime`

Changes:

- Compile lanes into target address + prepared scalar evaluation + codec.
- Keep ordinary parameter automation block-stable.

### Commit M5.2

`lab(audio): apply prepared automation in AudioGraphProcessor`

Changes:

- Apply automation at block boundary through prepared targets.
- Preserve ordering:
  1. restore manual/base snapshot
  2. drain live parameter queue
  3. apply prepared automation
  4. apply modulation
  5. process nodes

### Commit M5.3

`lab(offline): use prepared automation runtime for offline render`

Changes:

- Offline render consumes the same prepared automation data.
- Message-thread playback is not render truth.

### Commit M5.4

`lab(timeline): demote message-thread automation playback to preview`

Changes:

- UI tick path can update visual state.
- Audio/offline runtime owns audible/rendered automation.

Acceptance for M5:

- Realtime and offline parameter traces match.
- Automation does not depend on message-thread cadence.

## M6: Compiled Runtime Parameter Targets

Goal: reduce hot-path lookup work and make runtime application explicit.

### Commit M6.1

`lab(audio): build parameter index maps in graph runtime cache`

Changes:

- Per-node hash -> snapshot index map.
- Collision diagnostics remain.

### Commit M6.2

`lab(parameters): introduce CompiledParamTarget`

Changes:

- Resolve full `ParamAddress` to node index, snapshot index, storage hash, and
  semantics.

### Commit M6.3

`lab(audio): apply parameter queue updates through compiled targets`

Changes:

- Prefer direct index application.
- Keep hash fallback during transition.

### Commit M6.4

`lab(audio): update host adapter parameter bindings to prepared indices`

Changes:

- Reduce repeated binding scans in adapter application.

Acceptance for M6:

- Existing realtime parameter updates still work.
- Large graph parameter stress tests show no regression and lower lookup cost.

## M7: Slot-Aware End-to-End Targeting

Goal: full `ParamAddress` identity everywhere.

### Commit M7.1

`lab(timeline): persist and resolve slot-scoped automation targets`

Changes:

- Automation lanes can carry optional `slotIndex`.
- Selectors expose slot targets where semantically valid.

### Commit M7.2

`lab(modulation): store full ParamAddress in ModulationRoute`

Changes:

- Replace target node + param-only representation with full address.
- Add migration from old route schema.

### Commit M7.3

`lab(modulation): prepare slot-scoped modulation targets`

Changes:

- Prepared runtime hashes `ParamAddress::storageKey()`.
- Slot modulation applies only to the intended slot.

### Commit M7.4

`lab(midi): store full ParamAddress in MIDI mappings`

Changes:

- MIDI mappings preserve slot index.
- Mapping migration preserves old global targets.

Acceptance for M7:

- Slot automation, modulation, and MIDI target only the intended slot.
- Global and slot override inheritance is documented and tested.

## M8: Smoothing, Modulation Semantics, Value Sources, Macros

Goal: finish higher-level parameter behavior after the core contract is stable.

### Commit M8.1

`core(parameters): add modulation contribution modes`

Modes:

- plain additive delta
- normalized bipolar offset
- multiplicative
- disabled

### Commit M8.2

`lab(modulation): map modulation through target semantics`

Changes:

- Replace min/max-only modulation math with codec-aware mapping.

### Commit M8.3

`lab(audio): apply host smoothing where policy allows`

Changes:

- Host ramp only when policy says host-owned.
- Operator-owned smoothing remains inside operators/packs.

### Commit M8.4

`lab(parameters): quarantine incomplete Expr and Bind sources`

Changes:

- Hide or mark incomplete source kinds until evaluated deterministically.

### Commit M8.5

`lab(parameters): implement deterministic value-source evaluation`

Only do this if product scope requires `Expr`/`Bind` now.

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

- Modulation is semantically correct for non-linear parameters.
- Smoothing ownership is explicit.
- Incomplete value sources are not silently product-visible.

## M9: Persistence, Migration, and Highend UI

Goal: make the system inspectable and patch-compatible.

### Commit M9.1

`lab(project): version parameter automation schema`

Persist:

- value domain
- target address
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

`lab(ui): add target-aware automation lane labels`

Show:

- units
- dB/Hz/native labels
- step/grid hints
- unresolved target status

Acceptance for M9:

- Old patches do not silently change sound.
- Users can inspect why a parameter has its final value.
- Missing/migrated targets are visible and non-destructive.

## Suggested Branch and Review Strategy

Use one branch per milestone until M4:

- `parameter-domain-m0-baseline`
- `parameter-domain-m1-automation-domain`
- `parameter-semantics-m2-core-codec`
- `parameter-semantics-m3-lab-migration`
- `parameter-semantics-m4-pack-policy`

After M4, runtime work can split:

- `parameter-runtime-m5-automation`
- `parameter-runtime-m6-targets`
- `parameter-slots-m7`
- `parameter-sources-m8`
- `parameter-ui-m9`

Review rule:

- No milestone is complete without tests.
- No new conversion helper may bypass `ParamValueCodec`.
- No new target path may store node + param without full `ParamAddress`, unless
  it is explicitly a compatibility adapter.
- No topology parameter may be added to ordinary automation, MIDI, or modulation
  paths.

## Minimal First Slice

If implementation needs to start immediately, do this exact slice:

1. M0.2 characterization tests.
2. M1.1 domain metadata.
3. M1.2 minimal linear codec adapter.
4. M1.3 recorder conversion.
5. M1.4 playback conversion.
6. M1.6 parity tests.

This fixes the current 0..1/native automation bug without waiting for the full
semantic contract.

## Final Definition of Done

The parameter system is considered highend-ready when:

- Automation point storage has explicit value domains.
- Timeline automation records and plays back non-`0..1` parameters correctly.
- All Lab parameter conversion flows through one codec.
- CDP `ui.scale` and `ui.step` affect Lab controls, automation, MIDI, and
  modulation.
- Realtime and offline automation produce matching parameter traces.
- Topology parameters are rejected by ordinary automation, MIDI, and modulation.
- Slot-scoped targets work end-to-end.
- Runtime parameter application uses compiled targets where practical.
- Smoothing ownership is explicit.
- Incomplete value sources are either complete or product-hidden.
- Patch migration is deterministic and visible.
