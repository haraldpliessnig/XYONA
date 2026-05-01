# Roadmap: Operator Slot System

Status: Implemented roadmap; see `REPORT_OPERATOR_SLOT_SYSTEM_IMPLEMENTATION_2026-05-01.md`
Date: 2026-05-01
Contract: `OPERATOR_CONTRACT.md`
Scope: `xyona-core`, `xyona-lab`, `xyona-cdp-pack`, future operator packs

## Executive Decision

The system is ready to start the slot-system overhaul because the central
operator contract now defines the model. The implementation is not yet aligned
with that model. Current code still carries the earlier `routingPolicy`,
`slotMap`, string-only connection lane, and `slotCount` transport model.

The implementation must therefore proceed in contract-first slices. Do not add
new product-facing slot UX on top of the old `Locked`/`Unlocked` model.

## Target Function

Slots are an optional operator-wide processing dimension.

```text
non-slottable:
  slots.supported = false or missing

slottable normal form:
  slots.supported = true
  slotCount = 1

slottable expanded form:
  slots.supported = true
  slotCount = N
```

Each public port of a slottable operator resolves to exactly one mapping:

| Mapping | Meaning |
|---|---|
| `per_slot` | The port exists per slot. Endpoint addresses include `slotIndex`. |
| `shared` | The port exists once for the operator instance. Endpoint addresses do not include `slotIndex`. |

Mono and multichannel audio are both slot-capable:

```text
mono audio cable         x slotCount N = N one-channel slot surfaces
multichannel audio cable x slotCount N = N ordered multichannel slot surfaces
```

Stereo is not a slot model and not a port type. Stereo is the two-channel case
of `xyona.audio`.

The canonical endpoint address is:

```text
nodeId + descriptorPortId + optional channelIndex + optional slotIndex
```

Slot parameters use sparse overrides:

```text
global value: gain
slot override: gain@slot=3

effective value for slot 3 =
  gain@slot=3 if present
  otherwise gain
```

## User-Facing Product Behavior

The user sees one operator node, not N duplicated nodes. A slottable operator
can process several independent slot surfaces internally while keeping one
global parameter set and optional per-slot overrides.

Expected high-value cases:

- one gain/EQ/processor node on 5.1 with six independent slot overrides
- one VST3 host node internally running one plugin instance per slot
- one multichannel processor with shared sidechain input and per-slot outputs
- one analyzer/sink with shared output only when explicitly documented

The UI must never imply that a slot marker is render progress or operator
availability. Slot UI is topology and addressability.

## Non-Goals

- Do not introduce a `xyona.stereo` port type.
- Do not use `slotCount=0` as normal operation.
- Do not use `Locked`/`Unlocked` as product UX.
- Do not infer slot behavior from operator IDs, port names, provider, family,
  channel count, or header stripe color.
- Do not make CDP or Lab depend on pack-private slot conventions.

## Baseline State Before Implementation

The following inventory was the verified implementation baseline before this
roadmap was executed. It is retained to explain the migration sequence and the
legacy terms still mentioned below.

Implemented or partially implemented at baseline:

- Core has legacy slot transport fields:
  `OpDesc::routingPolicy`, `slotCount`, `slotMap`, `slotGroups`.
- Core has `ParamScope::PerSlot` and `param@slot=N` convention.
- Core has `slot_gain` as a reference operator, but it still uses
  `routingPolicy: locked`, generated `in_N/out_N`, and default slot count 2.
- Core variable-port metadata exists and can generate `in_N/out_N`.
- Lab has `ParamAddress::slotIndex`, `ParamAddress::storageKey()`, and
  per-slot parameter persistence through `@slot=`.
- Lab has string-based bundled connection `lanes`, useful for multichannel
  bundles but not yet the structured endpoint model.
- Lab expands channelized descriptor ports into visible `in_0/out_0` style
  endpoints.
- CDP pack has no public slottable operators; existing CDP audio ports are
  mono or fixed/matching channel-count `xyona.audio` descriptors.

Missing or incompatible with the target:

- No canonical `slots.*` descriptor struct in Core.
- No `slotMapping` field on `IODesc`, `PortDesc`, `VariablePortRangeDesc`, or
  pack ABI transport.
- Core codegen and validators still understand `routingPolicy`, not the new
  port-mapping contract.
- Lab connections still store endpoint strings instead of structured
  `descriptorPortId/channelIndex/slotIndex`.
- Lab "connection lanes" conflate bundled channel pairs with the old lane term.
- Lab GraphBuilder does not yet expand `per_slot` and `shared` slot mappings
  from structured endpoint facts.
- Slot count UI, slot affordances, and per-slot override UX are not yet a
  complete product surface.
- CDP generator/validator does not yet transport slot metadata, even if all
  current operators remain non-slottable.
- CDP still carries legacy `routingPolicy` values, including some locked
  technical/PVOC operators. This is not slot support; it is legacy routing
  transport until resolved through the new descriptor contract.

## Implementation Sequence

Each step is intended to be one reviewable commit or a very small commit group.
Do not skip the tests named in each step.

### Commit 01 - Root Planning Baseline

Create/maintain:

- `ROADMAP_OPERATOR_SLOT_SYSTEM.md`
- `REPORT_OPERATOR_SLOT_SYSTEM_2026-05-01.md`

Acceptance:

- Roadmap and report reference `OPERATOR_CONTRACT.md`.
- Current gaps are explicit and repo-scoped.

### Commit 02 - Core Slot Descriptor Types

Add host-neutral descriptor types:

- `SlotSupportDesc`
- `SlotMapping` enum: `PerSlot`, `Shared`
- optional `slotMapping` on `IODesc`
- optional `slotMapping` on `PortDesc`
- optional `slotMapping` on `VariablePortRangeDesc`

Keep legacy `routingPolicy`, `slotMap`, and `slotGroups` as migration fields.

Acceptance:

- Public headers compile.
- Existing operators still build without metadata changes.
- Tests prove missing slot metadata resolves to non-slottable.

### Commit 03 - Core Schema And Codegen

Extend Core `op.yaml` handling:

- parse `slots.supported/defaultCount/minCount/maxCount/countParamId`
- parse per-port `slotMapping`
- generate C++ descriptor facts
- keep reading legacy `routingPolicy` only as compatibility input

Acceptance:

- Validator rejects ports without `slotMapping` only when
  `slots.supported=true`.
- Validator rejects slot minimum below 1.
- Validator rejects non-slottable slot-addressable metadata.

### Commit 04 - Core Slot Compatibility Helpers

Add pure helper APIs:

- `isSlotSupported(desc)`
- `effectiveSlotCount(desc)`
- `resolveSlotMapping(port)`
- `validateSlotDescriptor(desc)`

Relationship to existing `OpDesc` helpers must be explicit. Current
`OpDesc::isSlotAware()`, `OpDesc::getEffectiveSlotCount()`, and
`OpDesc::isRoutingLocked()` are legacy-helper surfaces. This commit either
replaces them, deprecates them with wrappers around the new helpers, or keeps
them only as clearly named legacy migration helpers. Do not leave two
independent slot semantics in Core.

Acceptance:

- Helpers have unit coverage independent of Lab.
- Helpers do not use JUCE or project/canvas types.
- Existing descriptor callers use one canonical helper path for slot support
  and effective count decisions.

### Commit 05 - Migrate Core Slot Gain

Migrate `slot_gain` from legacy route metadata to:

```yaml
slots:
  supported: true
  countParamId: slot_count
  defaultCount: 1
  minCount: 1
  maxCount: 16
```

Generated inputs and outputs declare `slotMapping: per_slot`.

This migration changes the public topology from the current generated
`in_N/out_N` legacy shape to one descriptor input and one descriptor output
with per-slot addresses. The commit that changes `slot_gain` must therefore
either include Lab project migration for legacy `slot_gain` instances or mark
the `slot_gain` fixture/project surface as intentionally breaking and clean the
affected fixtures in the same change.

`slotGroups` are UI/layout labels only. If `slot_gain` defaults to one slot,
no default `stereo_pair` group may be emitted for that one-slot topology;
stereo-pair grouping is valid only when the effective slot count is at least 2.

Acceptance:

- `slot_gain` still works as a multi-slot reference.
- Default normal form is one slot unless the test intentionally sets more.
- Old `routingPolicy: locked` is removed from its public spec.
- Existing `slot_gain` tests and fixtures are migrated to the new port shape,
  or the break is explicitly documented and accepted in that commit.

### Commit 06 - Pack ABI Slot Transport

Extend pack ABI v2 compatibly:

- slot support flags/count limits
- per-port slot mapping
- generated metadata JSON fields

Acceptance:

- Existing CDP packs load unchanged.
- New fields are gated by `struct_size`.
- Pack tests cover absence and presence of slot metadata.

### Commit 07 - CDP Generator And Validator

Teach `xyona-cdp-pack` generator/validator the slot fields.

Acceptance:

- All current CDP operators validate as non-slottable.
- A fixture slottable pack operator can transport `slotMapping`.
- CDP rejects `slotMapping` on non-slottable operators and rejects slottable
  operators whose public ports omit `slotMapping`.
- CDP stereo processes remain fixed two-channel `xyona.audio`, not stereo
  ports.

### Commit 08 - Lab Structured Endpoint Model

Introduce a Lab endpoint value object:

```cpp
struct EndpointAddress {
    NodeId nodeId;
    std::string descriptorPortId;
    std::optional<int> channelIndex;
    std::optional<int> slotIndex;
};
```

Acceptance:

- Existing string port IDs can round-trip through this object.
- `in_0` can be represented as `descriptorPortId=in, channelIndex=0` when
  descriptor facts prove that expansion.
- No renderer decides endpoint semantics from text alone.

### Commit 09 - Lab Project Persistence Migration

Persist structured endpoints while reading legacy string connections.

Acceptance:

- Old projects load.
- New projects save structured endpoint facts.
- Import rejects missing ports, invalid channel indices, and invalid slot
  indices with diagnostics.
- Migration fixtures cover:
  - legacy string connection `in_0 -> out_0`
  - legacy `lanes[]` multichannel bundle
  - persisted `param@slot=N` value
  - pre-migration `slot_gain` project/operator shape
  - invalid slot-index reference rejected with diagnostics

### Commit 10 - Lab Connection Model Split

Separate concepts:

- one visible cable
- channel endpoint bundle
- slot endpoint coordinate

Legacy `ConnectionLane` may remain as a compatibility type, but new code should
use endpoint pairs rather than lane terminology.

Acceptance:

- Existing bundled multichannel visual tests still pass.
- New tests cover one mono cable, one multichannel cable, and one slotted cable.

### Commit 11 - Lab Port Resolver And Compatibility Service

Centralize endpoint resolution:

- descriptor port lookup
- channel expansion
- slot expansion
- compatibility explainers

Acceptance:

- Mouse hover, connection creation, project import, and GraphBuilder use the
  same service.
- Incompatible slot mappings cannot be patched accidentally.

### Commit 12 - Lab Slot UI Model

Build a slot UI model from descriptor facts:

- slot count
- slot labels/groups
- per-port `per_slot/shared`
- valid parameter override surfaces

Acceptance:

- No header stripe is used as slot meaning.
- Slot affordances are shown only for slottable descriptors.
- Non-slottable operators remain visually unchanged.

### Commit 13 - Lab Slot Count Editing

Add slot-count editing for descriptors with `slots.countParamId`.

Acceptance:

- Changing slot count is a topology change.
- Invalid wires are removed or blocked.
- Undo/redo restores slot count and valid endpoint state.

### Commit 14 - Lab Per-Slot Parameter UX

Complete per-slot override authoring:

- global value
- sparse override value
- clear override -> inherit global
- per-slot display in ParameterBar/operator mini UI

Acceptance:

- `ParamAddress::slotIndex` is used end to end.
- `Canvas::setCoreParamAddressValue()` rejects `slotIndex` values outside
  `0 <= slotIndex < effectiveSlotCount` before writing `CorePayload` state.
- Persistence round-trips sparse overrides.

### Commit 15 - GraphBuilder Slot Expansion

Teach GraphBuilder to expand:

- `per_slot` input/output endpoints
- `shared` inputs
- `shared` outputs only for operators with explicit aggregate/sink semantics
- mono and multichannel cables with optional `slotIndex`

Acceptance:

- Runtime plan has deterministic wires.
- Builder revalidates all structured endpoint coordinates.
- Tests cover per-slot input/output, shared input, and invalid shared output.

### Commit 16 - Runtime Parameter Snapshot Slot Resolution

Keep `param@slot=N` as the bridge format until a structured runtime snapshot
exists. Ensure the runtime sees global and override keys consistently.

Acceptance:

- Slot Gain resolves global fallback and sparse override correctly.
- Parameter update bridge hashes the same keys GraphBuilder/runtime expects.

### Commit 17 - Multichannel Slot Cables

Add true bundled multichannel + slot address coverage.

Acceptance:

- A two-channel cable can be patched as one bundle and still address slot N.
- A six-channel cable can feed six slots when the operator declares that shape.
- Tests cover the full matrix:
  `mono non-slottable`, `mono slottable`, `multichannel non-slottable`, and
  `multichannel slottable`.
- Tests include a connection that is both bundled multichannel and slotted.
- Stereo remains a two-channel audio case.

### Commit 18 - Product Reference Operator

Harden one reference processor beyond `slot_gain` if needed:

- a slottable multichannel gain/EQ-style operator, or
- a Lab-hosted VST/plugin-host prototype with one internal processor per slot.

Acceptance:

- One visible node controls multiple internal slot processors.
- Global parameters and sparse overrides are visible and testable.

### Commit 19 - End-To-End Tests

Add cross-repo coverage:

- Core descriptor validator tests
- Core runtime `slot_gain` tests
- Lab Canvas connection tests
- Lab persistence migration tests
- Lab GraphBuilder slot expansion tests
- CDP pack metadata absence/presence tests

Acceptance:

- No product-facing path depends on `routingPolicy`.
- No product-facing path depends on `in_N/out_N` text guessing.

### Commit 20 - Documentation And Cleanup

Update:

- `OPERATOR_CONTRACT.md`
- package-local authoring guides
- Canvas and UI docs
- Core slot transport notes
- CDP port type docs
- implementation report

Acceptance:

- `rg` finds old `Locked/Unlocked` language only in explicitly marked legacy
  transport notes or historical roadmap sections.
- `git diff --check` passes in root, Core, Lab, and CDP pack.

## Validation Matrix

| Area | Required tests |
|---|---|
| Core descriptors | slot schema, slotMapping validation, default non-slottable behavior |
| Core runtime | `slot_gain`, per-slot override fallback, topology change |
| Pack ABI | old pack compatibility, new slot fields, generated metadata |
| CDP pack | all current ops non-slottable, fixed two-channel audio remains `xyona.audio` |
| Lab model | structured endpoint parsing, legacy project migration |
| Lab UI | slottable vs non-slottable visuals, slot count editing, override clearing |
| Lab GraphBuilder | per-slot ports, shared inputs, multichannel bundles, invalid endpoints |
| Migration fixtures | legacy `in_N/out_N`, `lanes[]`, `param@slot=N`, pre-migration `slot_gain`, invalid slot index |

## Stop Conditions

Stop the implementation and update the contract if any phase requires:

- a third slot mapping besides `per_slot` and `shared`
- a separate stereo port type
- slot behavior inferred from names instead of metadata
- a host-specific requirement in Core or CDP pack descriptors
- a normal palette operator with `canRealtime=false` and `canHQ=false`

## Definition Of Done

The slot system is done when a user can create one visible slottable operator,
set `slotCount=N`, patch mono or multichannel slot endpoints, set global and
sparse per-slot parameters, save/reload the project, and run RT/HQ/offline
graphs without Lab guessing port or slot semantics from string names.
