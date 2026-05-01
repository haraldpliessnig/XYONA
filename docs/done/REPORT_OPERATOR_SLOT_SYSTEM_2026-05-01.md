# Report: Operator Slot System Planning

Date: 2026-05-01
Status: Planning baseline
Roadmap: `ROADMAP_OPERATOR_SLOT_SYSTEM.md`
Contract: `OPERATOR_CONTRACT.md`
Repositories audited: `xyona-core`, `xyona-lab`, `xyona-cdp-pack`

## Executive Summary

The slot-system overhaul can start now, but the implementation is not yet on
the new slot basis. The central operator contract defines the intended model:
operator-wide slots, `slotMapping = per_slot | shared`, structured endpoint
coordinates, mono and multichannel slot support, and sparse per-slot parameter
overrides.

The codebase currently contains useful foundations but they are still mixed
with the older slot/lane model. The first implementation work must therefore
be schema and transport migration, not UI polish.

## Current Foundations

### Workspace Contract

`OPERATOR_CONTRACT.md` now defines:

- slot as an operator-wide processing dimension
- normal slottable form as `slotCount=1`
- `slotCount=0` as invalid for normal public operation
- per-port `slotMapping` with only `per_slot` and `shared`
- mono and multichannel audio as slot-capable
- stereo as a two-channel audio case, not a port type
- structured endpoint model:
  `nodeId + descriptorPortId + optional channelIndex + optional slotIndex`
- operator availability classes separate from UI stripes/progress/status

### Core

Observed current state:

- `include/xyona/types.hpp` still exposes legacy:
  - `RoutingPolicy`
  - `SlotMapEntry`
  - `OpDesc::routingPolicy`
  - `OpDesc::slotCount`
  - `OpDesc::slotMap`
  - `OpDesc::slotGroups`
- `ParamScope::PerSlot` exists.
- `ParamDesc::scopeSupport` exists.
- `VariablePortRangeDesc` exists.
- `IODesc` and `VariablePortRangeDesc` do not yet expose `slotMapping`.
- `slot_gain` exists as the current reference operator.
- `slot_gain/op.yaml` still uses:
  - `routingPolicy: locked`
  - `slotCount: 2`
  - generated `in_0/in_1/out_0/out_1`
  - `scopeSupport: [global, per_slot]`
- Core codegen and runtime tests still compare `routingPolicy`.

Conclusion: Core has enough primitives to migrate, but the public descriptor
schema must be extended before Lab can implement the new model safely.

### Lab

Observed current state:

- `ParamAddress` has `std::optional<int> slotIndex`.
- `ParamAddress::storageKey()` already emits `param@slot=N`.
- Canvas stores arbitrary parameter keys, including `@slot=`.
- `setCoreParamAddressValue()` validates `ParamScope::PerSlot`.
- Parameter update bridge hashes `address.storageKey()`.
- `Connection` has string-based `sourceOutput`/`targetInput`.
- `Connection` also has `std::vector<ConnectionLane> lanes` for bundled
  connection pairs.
- Port visuals expand channelized descriptor ports into visible `in_N/out_N`
  strings.
- `Canvas::onOperatorPortsChanged()` rebuilds descriptors for topology changes.

Conclusion: Lab already has parameter-slot foundations and some bundled cable
infrastructure, but it lacks a structured slot endpoint model and GraphBuilder
slot expansion.

### CDP Pack

Observed current state:

- No public CDP operator currently declares slot support.
- Existing CDP audio operators use `xyona.audio` channel contracts.
- Space operators require exactly two channels, but this is a fixed
  two-channel audio contract, not a stereo port type.
- CDP `op.yaml` files still carry legacy `routingPolicy` metadata. Most are
  unlocked, and some technical/PVOC operators are locked; none of those fields
  currently declare the new slot contract.
- The CDP generator does not yet transport `slots.*` or per-port
  `slotMapping`.

Conclusion: CDP can remain non-slottable during early migration. Its generator
and ABI transport still need to learn slot metadata so future packs use the
same contract.

## Readiness Answer

We are ready to begin the overhaul because:

- the central contract is explicit
- old conflicting docs are no longer the source of truth
- Core already owns descriptor types and validators
- Lab already has parameter address support for slot overrides
- bundled/multichannel cable work has a partial model to build on

We are not ready to ship the feature because:

- `slotMapping` is not yet in public descriptor transport
- Lab endpoint persistence is still string-first
- GraphBuilder does not yet expand slots by metadata
- the reference operator still publishes legacy routing metadata
- pack ABI and CDP generator do not yet carry slot mapping facts

## Technical Risks

| Risk | Mitigation |
|---|---|
| Old `Locked/Unlocked` logic leaks into UX. | Treat it as legacy transport only and migrate `slot_gain` early. |
| `in_N/out_N` strings become semantic truth. | Introduce structured `EndpointAddress` before GraphBuilder slot expansion. |
| Slot and multichannel concepts blur. | Keep `channelIndex` and `slotIndex` separate in every model. |
| Slot UI ships before runtime semantics. | Gate UI behind descriptor validation and GraphBuilder tests. |
| CDP fixed two-channel processes get called stereo ports. | Keep `xyona.audio` with fixed channel policy and document signal semantics only. |
| Per-slot params update UI but not audio runtime. | Keep `param@slot=N` bridge until structured snapshots are implemented, and test bridge hashing. |

## Recommended First Implementation Batch

Batch 1 should be contract transport only:

1. Core slot descriptor types and helper functions.
2. Core parser/codegen/validator support for `slots.*` and `slotMapping`.
3. Migrate `slot_gain` public spec to the new contract.
4. Add pack ABI slot metadata fields.
5. Teach CDP generator/validator to pass through non-slottable defaults.

Do not start Lab visual slot UX until Batch 1 is green. Lab UI without
structured descriptor facts would recreate the ambiguity that the new contract
was designed to remove.

## Reviewer Hardening Applied

A follow-up code inspection on 2026-05-01 confirmed that the roadmap sequence is
technically viable, but it also identified implementation details that must be
handled before the first code slice:

- Core validation must require `slotMapping` only when `slots.supported=true`;
  existing non-slottable operators must remain valid.
- New Core slot helpers must not duplicate the existing legacy
  `OpDesc::isSlotAware()`, `OpDesc::getEffectiveSlotCount()`, and
  `OpDesc::isRoutingLocked()` semantics. The implementation must replace,
  wrap, or clearly deprecate those helpers.
- Migrating `slot_gain` is a public topology change from generated
  `in_N/out_N` legacy endpoints to descriptor ports with per-slot addresses.
  The same commit must either migrate affected fixtures/projects or document
  the break explicitly.
- `slot_gain` must not emit a default `stereo_pair` slot group for a one-slot
  topology. Stereo-pair grouping is valid only when the effective slot count is
  at least 2.
- Lab per-slot parameter writes must validate `slotIndex` against the effective
  slot count before persisting `param@slot=N`.
- Lab project migration needs concrete fixtures for legacy `in_N/out_N`
  strings, `lanes[]` bundles, `param@slot=N`, pre-migration `slot_gain`, and
  invalid slot-index rejection.
- Multichannel slot cable tests must cover mono/multichannel crossed with
  slottable/non-slottable, including one bundled multichannel connection that
  also addresses a slot.

One correction to the review language: CDP does use some `routingPolicy:
locked` metadata today. That metadata is legacy transport, not slot support,
so it does not block the slot-system migration.

## Recommended Second Implementation Batch

Batch 2 should be Lab model and persistence:

1. Add `EndpointAddress`.
2. Migrate project connection persistence.
3. Centralize endpoint resolution and compatibility.
4. Split bundled channel endpoint pairs from slot endpoint coordinates.

This must happen before GraphBuilder/runtime work.

## Recommended Third Implementation Batch

Batch 3 should be Lab behavior:

1. Slot UI model from descriptors.
2. Slot count editing through topology parameters.
3. Per-slot parameter override UX.
4. GraphBuilder slot expansion.
5. RT/HQ/offline runtime tests.

## Decision

Proceed with the slot-system overhaul only as a commit-by-commit roadmap. The
first commit after this planning baseline should not touch UI. It should add
the canonical slot descriptor transport in Core and keep legacy fields as
migration-only data.
