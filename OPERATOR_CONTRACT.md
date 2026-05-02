# XYONA Operator Contract

**Status:** Workspace standard
**Version:** 2.0
**Date:** 2026-05-01
**Applies to:** `xyona-core`, `xyona-lab`, `xyona-cdp-pack`, future operator
packs, Lab-authored public host operators, and public descriptor consumers

## Purpose

This document is the single normative contract for public XYONA operators. It
defines:

- the required operator schema and descriptor fields
- the allowed technical classification axes
- the allowed combinations of capability, process shape, domain,
  materialization, and host contract
- the operator-wide slot model for mono and multichannel work
- the exact port metadata model, including audio ports
- patch compatibility rules
- operator availability rules for Lab UI and graph scheduling
- validation and extension requirements

The practical authoring instructions live in `OPERATOR_MODULE_AUTHORING_GUIDE.md`.
This document owns the contract. The authoring guide explains how to implement
it in a package.

## Foundational Model

XYONA operators are logical processing units. A visible operator node may map
to one DSP instance, multiple replicated DSP instances, a plugin host, a pack
adapter, or a Lab-owned host component. The public descriptor must describe the
operator's technical shape explicitly so Lab can build UI, project state,
patching, graph execution, and render behavior without guessing.

The foundational dimensions are:

| Dimension | Contract |
|---|---|
| Operator instance | The visible node and persisted operator identity. |
| Port | A stable logical connection surface declared by the operator descriptor. |
| Audio connection category | Either mono audio or multichannel audio. Stereo is the two-channel case, not its own type. |
| Channel | Ordered audio channel inside a mono or multichannel audio port/cable. |
| Slot | Optional operator-wide processing dimension. A slot is not a port, not a channel, not a cable type, and not a UI color. |
| Parameter scope | Parameters may be global only or may additionally support sparse per-slot overrides. |
| Endpoint address | `nodeId + descriptorPortId + optional channelIndex + optional slotIndex`. |

Slots are central but opt-in:

```text
non-slottable operator:
  slots.supported = false or missing
  no slot dimension

slottable operator, normal form:
  slots.supported = true
  slotCount = 1

slottable operator, expanded form:
  slots.supported = true
  slotCount = N
```

Do not use `slotCount=0` as the public meaning of normal operation. Zero slots
means no processing slots. Missing slot metadata resolves to
`slots.supported=false`.

For slottable operators, every public input and output must declare:

```text
slotMapping = per_slot | shared
```

`per_slot` means the port/cable is repeated for each slot and endpoint
addresses include `slotIndex`. `shared` means the port/cable exists once for
the operator instance and is available to all slots.

Mono and multichannel both support slots:

```text
mono audio cable         x slotCount N = N one-channel slot surfaces
multichannel audio cable x slotCount N = N ordered multichannel slot surfaces
```

This enables a single visible operator to manage many internal processors. For
example, a VST3 EQ host on a 5.1 bus may expose one visible node with
`slotCount=6`; internally it may run six EQ/plugin instances, while the UI shows
one global parameter set plus sparse per-slot overrides for L, R, C, LFE, Ls,
and Rs.

Slot parameter inheritance is:

```text
effective value for slot N =
  explicit value@slot=N if present
  otherwise global value
```

This model is part of the operator contract, not a renderer convention. Core
owns host-neutral descriptor fields and validation. Packs and Lab-authored
operators declare whether they are slottable. Lab owns Canvas presentation,
slot count editing, slot cables, endpoint persistence, graph expansion, and
runtime/render scheduling.

## Operator Schema

Every public operator is described by one stable schema. This is the conceptual
shape; package generators may store or emit equivalent structures as YAML,
metadata JSON, C++ descriptors, pack ABI descriptors, or Lab runtime tables, but
the public discovery surface must expose the resolved facts.

```yaml
schema: xyona-operator-v1
id: cdp.modify.loudness_gain
provider: cdp
providerLabel: CDP
family: modify
moduleName: loudness_gain

label: Loudness Gain
summary: "One-line technical summary."
description: "Longer operator description."
operatorType: processor
category: CDP/Modify
icon: volume-2
version: 0.1.0

ui:
  shortLabel: Loudness Gain
  nodeNameStem: loud_gain

ownership:
  repository: xyona-cdp-pack
  license: LGPL-2.1-or-later
  algorithmOwner: pack
  hostBoundary: no_lab_dependencies

capabilities:
  canRealtime: true
  canHQ: true

engine:
  processShape: block_length_preserving
  domain: time_audio
  materialization: none
  outputLength: same_as_input
  wholeFileRequired: false
  lengthChanging: false
  audioOutput: true
  multiOutput: false
  abiV2Support: direct

slots:
  supported: false

ports:
  inputs:
    - id: in
      type: xyona.audio
      kind: audio
      domain: time_audio
      rate: audio_rate
      channelPolicy: any
      mergePolicy: single_source
      executionContext: realtime_or_offline
      ui: { role: input }
  outputs:
    - id: out
      type: xyona.audio
      kind: audio
      domain: time_audio
      rate: audio_rate
      channelPolicy: match_input
      mergePolicy: sum
      executionContext: realtime_or_offline
      ui: { role: output }

params:
  - id: gain
    descriptor:
      label: Gain
      type: float
      min: 0.0
      max: 2.0
      default: 1.0
      unit: x
      description: "Linear gain factor."
      group: Gain
      display: slider
      precision: 3
      available: both
      isTopology: false
      scope: global

help:
  id: help.node.cdp.modify.loudness_gain
  tags: [node, cdp, modify, loudness]

provenance:
  source: cdp8
  cdp:
    sourceFile: dev/modify/gain.c

validation:
  strategy: analytic_golden_buffer
```

## Classification Model

An operator is not classified by one label. It is classified by orthogonal
facts:

```text
identity          = who owns it and what stable module it is
display           = how humans see it
capability        = whether RT and/or HQ are supported
process shape     = how it processes data
engine domain     = what problem domain it operates in
materialization   = what offline artifact, if any, it creates
slot model        = whether the operator has slots and how ports map to them
port types        = what can flow through each cable
host contract     = what Lab/runtime scheduler must provide
availability      = whether it is insertable and runnable in this build
```

Do not overload a single UI mark, color, category, source path, or operator ID
to represent these facts. Lab must be able to display an operator technical
summary just as it can already display port type facts.

## Required Operator Fields

Every public operator must expose these fields through `op.yaml` and the public
descriptor/discovery surface. Lab must not reconstruct them from source paths,
category strings, filenames, or dotted IDs.

| Group | Field | Required | Meaning |
|---|---:|---:|---|
| Identity | `schema` | yes | Operator spec schema. Current value: `xyona-operator-v1`. |
| Identity | `id` | yes | Immutable machine ID for lookup, persistence, help, tests. |
| Identity | `provider` | yes | Stable lowercase provider namespace. |
| Identity | `providerLabel` | yes | Human provider label. |
| Identity | `family` | yes | Provider-local family, without provider prefix. |
| Identity | `moduleName` | yes | Provider-local module identifier. |
| Display | `label` | yes | Human-facing operator name, without forced provider prefix. |
| Display | `summary` | yes | One-line technical summary. |
| Display | `description` | yes | Longer description. |
| Display | `operatorType` | yes | UI/behavior role from this contract. |
| Display | `category` | yes | Product grouping/filtering label; not identity. |
| Display | `icon` | yes | Stable icon identifier. |
| Display | `version` | yes | Operator version. |
| Display | `ui.shortLabel` | yes | Compact operator label. |
| Display | `ui.nodeNameStem` | yes | Default Canvas instance-name stem. |
| Ownership | `ownership.repository` | yes | Owning repository/package. |
| Ownership | `ownership.license` | package-dependent | Distribution license where relevant. |
| Ownership | `ownership.algorithmOwner` | yes | `core`, `lab`, `pack`, or equivalent owner. |
| Ownership | `ownership.hostBoundary` | yes | Whether implementation is host-free, host-owned, or pack-owned. |
| Capability | `capabilities.canRealtime` | yes | Whether RT preview/block processing is supported. |
| Capability | `capabilities.canHQ` | yes | Whether HQ/offline processing is supported. |
| Engine | `engine.processShape` | yes | Processing model from the allowed vocabulary. |
| Engine | `engine.domain` | yes | Operator domain from the allowed vocabulary. |
| Engine | `engine.materialization` | yes | Offline artifact/materialization class. |
| Engine | `engine.outputLength` | yes for pack/offline operators | Output length model. |
| Engine | `engine.wholeFileRequired` | yes | Whether complete source material is required. |
| Engine | `engine.lengthChanging` | yes | Whether output duration/sample count may change. |
| Engine | `engine.audioOutput` | yes for pack/offline operators | Whether the operator emits audio as an output artifact. |
| Engine | `engine.multiOutput` | yes for pack/offline operators | Whether it emits multiple artifacts/files. |
| Engine | `engine.abiV2Support` | yes for packs | Required pack ABI/host contract. |
| Slots | `slots.supported` | resolved descriptor fact | Whether the operator has a slot dimension. Missing legacy metadata resolves to `false`. |
| Slots | `slots.defaultCount` | slottable operators | Normal slot count. Must be `1` for a slottable operator unless a more specific operator contract says otherwise. |
| Slots | `slots.minCount` / `slots.maxCount` | slottable operators | Supported slot-count bounds. `minCount` must be at least `1`. |
| Slots | `slots.countParamId` | dynamic slottable operators | Topology parameter controlling slot count, when user-adjustable. |
| Ports | `ports.inputs[]` | yes | Stable input port descriptors. Empty list allowed. |
| Ports | `ports.outputs[]` | yes | Stable output port descriptors. Empty list allowed. |
| Params | `params[]` | yes | Stable parameter descriptors. Empty list allowed. |
| Help | `help.id` | yes | Help article ID, normally `help.node.<operator_id>`. |
| Help | `help.tags[]` | yes | Help/search tags. |
| Provenance | `provenance` | algorithmic operators | Source algorithm/provenance and validation reference. |
| Validation | `validation.strategy` | yes | How descriptor/DSP behavior is validated. |

CDP-derived operators include CDP8 provenance with `sourceFile` under `dev/`
unless the operator is an explicitly technical synthetic fixture.

## Descriptor Surface

The public descriptor/discovery surface consumed by Lab must expose at least:

- `id`
- `label`
- `summary`
- `description`
- `operatorType`
- `category`
- `icon`
- `version`
- `provider`
- `providerLabel`
- `family`
- `moduleName`
- `shortLabel`
- `nodeNameStem`
- `domain`
- `materialization`
- `inputs[]`
- `outputs[]`
- `params[]`
- `flags[]`
- `caps.canRealtime`
- `caps.canHQ`
- `latencySamples`
- `help`
- resolved `slots.supported`
- slot metadata and port `slotMapping` where `slots.supported=true`
- optional variable-port/control capability metadata where the operator uses
  those systems

Pack metadata must also transport `engine.processShape`, `engine.outputLength`,
`engine.wholeFileRequired`, `engine.lengthChanging`, `engine.audioOutput`,
`engine.multiOutput`, `engine.abiV2Support`, and any artifact/spectral details
needed by Lab scheduling and offline materialization.

## Runtime Descriptor Data Fields

The runtime descriptor surface is currently represented by `xyona::OpDesc`,
`xyona::ParamDesc`, `xyona::IODesc`, `xyona::PortDesc`,
`xyona::VariablePortTopologyDesc`, and related slot/control metadata. These
fields must remain consistent with the operator spec.

### `OpDesc`

| Field | Meaning |
|---|---|
| `id` | Stable operator ID. |
| `label` | Human display name. |
| `summary` | One-line summary. |
| `description` | Extended description. |
| `operatorType` | Operator role. |
| `category` | Product grouping/filtering category. |
| `icon` | Icon identifier. |
| `provider` | Stable provider namespace. |
| `providerLabel` | Human provider label. |
| `family` | Provider-local family. |
| `moduleName` | Provider-local module name. |
| `shortLabel` | Compact UI label. |
| `nodeNameStem` | Stable Canvas default-name stem. |
| `domain` | Descriptor-level engine domain. |
| `materialization` | Descriptor-level materialization class. |
| `inputs` | Input `IODesc` list. |
| `outputs` | Output `IODesc` list. |
| `params` | `ParamDesc` list. |
| `flags` | Extra capability/behavior flags such as `offline_only`, `per_channel`, `source`, `signal`, `control`, `generator`, `per_sample`. Flags are hints, not substitutes for contract fields. |
| `caps.canRealtime` | RT capability. |
| `caps.canHQ` | HQ/offline capability. |
| `version` | Operator version. |
| `latencySamples` | Processing latency for RT scheduling/PDC where applicable. |
| `help` | Help metadata. |
| `routingPolicy` | Optional slot routing policy. |
| `slotCount` | Optional explicit slot count. |
| `slotMap` | Optional custom slot-to-port mapping. |
| `slotGroups` | Optional UI semantics for grouped slots. |
| `variablePorts` | Optional variable input/output port families. |
| `supportsMidi` | Prepared control capability for MIDI 1.0. |
| `supportsMpe` | Prepared control capability for MPE. |
| `supportsMidi2` | Prepared control capability for MIDI 2.0. |
| `controlScopesSupported` | Bitmask for supported parameter/control scopes. |

### `ParamDesc`

| Field | Meaning |
|---|---|
| `id` | Stable parameter ID. |
| `label` | Human label. |
| `type` | Parameter type. |
| `min` / `max` | Numeric range. |
| `defaultValue` | Default raw value. |
| `enumValues` | Enum value labels for enum parameters. |
| `unit` | Unit string. |
| `description` | Parameter description. |
| `group` | UI grouping. |
| `display` | UI display hint. |
| `precision` | Display precision. |
| `visibleWhenParam` | Parameter ID controlling visibility. |
| `visibleWhenValues` | Values for which this parameter is visible. |
| `availableIn` | RT/HQ availability. |
| `isTopology` | True when changing this param rebuilds ports/topology. |
| `scopeSupport` | Global, per-slot, and/or per-voice scope support. |

### `IODesc`

`IODesc` is the descriptor transport used by current discovery and Canvas
consumption. It is retained for compatibility with generated descriptors.

| Field | Meaning |
|---|---|
| `id` | Stable port ID. |
| `channels` | Legacy channel declaration such as `any`, `1`, `2`, or `match_inputs`. |
| `tags` | Extra hints such as `sidechain`, `control`, `typed_data`, `pvoc_analysis`. |
| `type` | Stable namespaced port type. |
| `kind` | Broad runtime class. |
| `domain` | Signal/data domain. |
| `rate` | Data cadence. |
| `schema` | Typed-data schema. |
| `format` | Typed-data format/profile. |
| `channelPolicy` | Canonical channel policy. Defaults to `channels` when generated. |
| `mergePolicy` | Merge/source rule. |
| `executionContext` | Runtime context. |
| `slotMapping` | Slottable operators only: `per_slot` or `shared`. |

### `PortDesc`

`PortDesc` is the richer host-neutral port capability model.

| Field | Meaning |
|---|---|
| `id` | Stable port ID. |
| `type` | Stable namespaced port type. |
| `minChannels` | Minimum supported channel count. |
| `maxChannels` | Maximum supported channel count. |
| `defaultChannels` | Default/preferred channel count. |
| `kind` | `PortKind`: `Audio`, `Sidechain`, `Control`, `Trigger`. |
| `signalKind` | `SignalKind`: `AudioSignal`, `ControlSignal`, `GateSignal`, `EventSignal`, `MidiEvent`, `VisualStream`. |
| `rateHint` | `RateHint`: `AudioRate`, `ControlRate`, `EventRate`. |
| `rangeMin` / `rangeMax` | Optional CV/control value range. |
| `unit` | Optional CV/control unit. |
| `domain` | Signal/data domain. |
| `rate` | Data cadence. |
| `schema` | Typed-data schema. |
| `format` | Typed-data format/profile. |
| `channelPolicy` | Canonical channel policy. |
| `mergePolicy` | Merge/source rule. |
| `executionContext` | Runtime context. |
| `slotMapping` | Slottable operators only: `per_slot` or `shared`. |
| `label` | Optional port display label. |
| `group` | Optional UI grouping. |
| `optional` | Whether the port can remain unconnected. |

### Variable Ports And Slots

New public operator specs declare slot support through `slots.*` and declare
port slot behavior through per-port `slotMapping`. Current C++ descriptors and
pack ABI surfaces may still expose legacy transport fields from the earlier
slot rollout; those fields are compatibility carriers only and must resolve to
the canonical `slots.*` plus `slotMapping` model before Lab or another host
makes UX or patch-compatibility decisions.

| Field | Meaning |
|---|---|
| `VariablePortRangeDesc.countParamId` | Topology parameter controlling generated port count. |
| `portPrefix` | Generated port ID prefix. |
| `channels` | Channel declaration copied to generated ports. |
| `tags` | Tags copied to generated ports. |
| `type`, `kind`, `domain`, `rate`, `schema`, `format` | Port type facts copied to generated ports. |
| `channelPolicy`, `mergePolicy`, `executionContext` | Compatibility facts copied to generated ports. |
| `slotMapping` | Slot mapping copied to generated ports when the operator is slottable. |
| `minCount`, `maxCount`, `defaultCount` | Generated port count limits. |
| `familyId` | Optional stable variable-port family ID. |
| `order` | Optional ordering hint. |
| legacy `routingPolicy` | Transport-only legacy field. Do not author new public behavior with `Locked`/`Unlocked`; resolve to explicit port `slotMapping` and operator processing semantics. |
| legacy `slotMap` | Transport-only legacy field for older non-1:1 experiments. Do not use as a substitute for `slotMapping` on every public port. |
| `SlotGroupKind` | Optional UI/layout grouping: `Mono`, `StereoPair`, `Quad`, `Surround51`, `Surround71`, or `Custom`. It does not create a stereo or surround port type. |

## No Legacy Compatibility Mode

There are no legacy project or descriptor contracts to preserve for incomplete
public operator metadata. Do not add compatibility fallbacks that hide missing
facts.

Rules:

- Do not add compatibility aliases for old operator IDs or old module paths.
- Do not accept pack descriptors that omit required module identity metadata.
- Do not derive `provider`, `family`, `moduleName`, `ui.nodeNameStem`,
  `engine.domain`, `engine.materialization`, or port type facts from IDs,
  labels, categories, tags, channel counts, source paths, or private file
  layout.
- Do not use provider-prefixed visible labels such as `CDP: Loudness Gain`.
- Do not create public operator modules under `src/processes`.
- Do not create public operator `meta.yaml` files.
- Do not create provider-prefixed source folders such as
  `src/operators/cdp.modify`.
- Do not create flat public CDP adapter files such as
  `src/operators/cdp_modify_loudness_gain.cpp`.
- A missing public port type is a contract error, not a warning.
- Generic Canvas names such as `in_0` and `out_0` are never semantic
  substitutes for descriptor port IDs.
- Project state must persist stable descriptor port IDs.

## Providers

Current providers:

| Provider | Label | Ownership |
|---|---|---|
| `core` | `Core` | Host-agnostic built-in DSP/runtime foundation. |
| `lab` | `Lab` | Host-owned UI, routing, graph, device, project, timeline, and analyzer operators. |
| `cdp` | `CDP` | Dynamically loadable LGPL CDP operator pack. |

Rules:

- `provider` is required for every public operator.
- Pack and Lab operator IDs must start with `<provider>.`.
- New pack IDs should normally use `<provider>.<family>.<moduleName>`.
- Existing Core operator IDs may remain plain stable IDs such as `gain` or
  `signal_lfo`; metadata must still declare `provider: core`, `family`, and
  `moduleName`.
- Existing Lab public IDs may remain stable product IDs such as `lab.audio_in`;
  the structural family is still carried in `family`.
- Future providers are allowed only when they define a stable namespace,
  dynamic loading or build ownership, operator-module validation, descriptor
  transport, and port type facts.

## Current And Planned Provider Families

Families are provider-local taxonomy, not implementation paths invented by
Lab. They drive palette grouping, owner/family labels, validation, and future
pack planning. A family name must not repeat the provider namespace.

Current public provider families:

| Provider | Family | Current category label | Current role |
|---|---|---|---|
| `core` | descriptor-defined | `Core/<Family>` | Built-in host-neutral DSP/runtime operators. Current Core IDs may remain plain stable IDs, but descriptors still carry explicit family metadata. |
| `lab` | descriptor-defined | `Lab/<Family>` | Host-owned sources, sinks, analyzers, project/timeline/device operators, and UI-owned graph utilities. |
| `cdp` | `utility` | `CDP/Utility` | Technical pack fixtures and simple utility operators used to validate pack loading, parameters, block processing, whole-file ABI, and typed-data scheduling. |
| `cdp` | `modify` | `CDP/Modify` | CDP time-domain modification operators, including loudness and stereo-space transformations. |
| `cdp` | `edit` | `CDP/Edit` | CDP whole-file edit operators that cut or reshape source duration. |
| `cdp` | `pvoc` | `CDP/PVOC` | CDP PVOC analysis/synthesis and typed spectral data bridge operators. |

Current CDP public module families in `xyona-cdp-pack`:

| Family | Modules currently present | Normal classes represented |
|---|---|---|
| `utility` | `identity`, `db_gain`, `generator_probe`, `length_change`, `pvoc_identity`, `pvoc_probe` | Direct RT/HQ block utility, direct generator, HQ whole-file audio, HQ typed-data transform, and future-contract typed-data fixture. |
| `modify` | `loudness_gain`, `loudness_dbgain`, `loudness_phase_invert`, `loudness_normalise`, `space_mirror`, `space_narrow` | Direct RT/HQ block audio and HQ whole-file audio. |
| `edit` | `cut`, `cutend` | HQ whole-file length-changing audio. |
| `pvoc` | `anal`, `synth` | HQ typed-data producer and HQ typed-data-to-audio transform. |

CDP8 inventory/planning families currently tracked by the CDP pack:

| Family | Status in inventory | Expected operator shape |
|---|---|---|
| `technical` | in progress | Pack/host-contract fixtures, descriptor validation, and typed-data scheduling probes. Public modules should normally ship under the visible `utility` family unless a dedicated technical surface is created. |
| `utility` | planned/in use | Simple audio helpers and validation operators. |
| `classic_modify` | planned/in use | Classic CDP8 modify processes. Public module family is currently normalized to `modify`. |
| `classic_spectral` | in progress | PVOC/spectral analysis, synthesis, and spectral transforms. Public module family is currently normalized to `pvoc` for PVOC-specific operators. |
| `waveset` | infrastructure blocked | Waveset segmentation, distortion, partitioning, and waveset-derived multi-file/whole-file processes. |
| `granular_texture` | infrastructure blocked | Grain and texture processes requiring whole-file/random/splice contracts. |
| `multichannel` | infrastructure blocked/planned | Generic channel-count processing. Lab owns semantic speaker layout and physical routing. |
| `synthesis` | planned/infrastructure blocked | CDP8 generators and score/data-driven synthesis tools. |
| `speech` | infrastructure blocked | Speech/syllable/element-based whole-file processes. |
| `analysis_data` | infrastructure blocked | Non-audio analysis, text, table, and data-output operators. |

Inventory family names may differ from public module family names while the CDP
pack is normalizing CDP8 concepts into XYONA operator modules. Public descriptors
must always expose the normalized `family` used by their operator module.

## Identity And Naming

| Field | Meaning | Example |
|---|---|---|
| `id` | Immutable machine identity for lookup, persistence, help, tests. | `cdp.modify.loudness_gain` |
| `provider` | Stable lowercase namespace of the shipping source. | `cdp` |
| `providerLabel` | Human provider label. | `CDP` |
| `family` | Provider-local family/type, without provider prefix. | `modify` |
| `moduleName` | Provider-local module identifier. | `loudness_gain` |
| `label` | Human operator name without forced provider/family prefix. | `Loudness Gain` |
| `ui.shortLabel` | Compact UI label. | `Loudness Gain` |
| `ui.nodeNameStem` | Canvas default instance-name stem. | `loud_gain` |

Naming rules:

- `moduleName`, parameter IDs, port IDs, and `ui.nodeNameStem` use lowercase
  ASCII snake_case. Hyphens are not allowed.
- `ui.nodeNameStem` must not contain dots or provider namespace fragments.
- Default Canvas names must be generated from `ui.nodeNameStem`, not from `id`.
- Palette, sidebar, and context-menu secondary labels must use the canonical
  owner/family context derived from `providerLabel` and `family`, formatted as
  `<Provider>/<Family Display>`, for example `Core/Dynamics`, `Core/Signal`,
  `CDP/Modify`, or `Lab/System Audio`.
- UI secondary labels must not use `category`, `id`, source paths, or
  provider-prefixed labels as owner/family context. `category` may serve
  filtering or product grouping, but it is not the canonical owner context.

Example:

```yaml
id: cdp.modify.loudness_gain
provider: cdp
providerLabel: CDP
family: modify
moduleName: loudness_gain
label: Loudness Gain
category: CDP/Modify
ui:
  shortLabel: Loudness Gain
  nodeNameStem: loud_gain
```

The default node names are `loud_gain1`, `loud_gain2`, and so on. The persisted
operator ID remains `cdp.modify.loudness_gain`.

## Source Module Shape

Core operators, CDP pack operators, and future pack implementation modules use:

```text
src/operators/<family>/<module_name>/
  op.yaml
  README.md
  docs/
    en.md
    de.md
  dsp/
  adapter/
  tests/
  golden/
```

Not every optional subfolder is needed for every operator, but `op.yaml` is
required for every public implementation module.

Path rules:

- `<family>` is provider-local and must not include the provider namespace.
- `<family>` and `<module_name>` path parts must match `family` and
  `moduleName` in `op.yaml`.
- Shared implementation for multiple modules in the same family belongs in
  `src/operators/<family>/common/` and is not itself an operator module.
- Shared implementation must be declared explicitly where the generator needs
  it, for example with CDP pack `adapter.sharedSources`.

Lab-authored public host operators are currently declared in
`xyona-lab/specs/operators/lab-public.op.yaml` and must apply matching runtime
metadata through Lab's explicit descriptor metadata table. If Lab later moves
host operators into physical source modules, those modules must use the same
`src/operators/<family>/<module_name>/op.yaml` shape.

## Operator Types

`operatorType` describes the user-facing role. It does not decide patch
compatibility.

| Type | Meaning | Current usage |
|---|---|---|
| `processor` | Consumes and transforms incoming data/audio. | Core, CDP, Lab. |
| `generator` | Produces data/audio without a normal signal input. | Core, CDP fixture, Lab sources/grid. |
| `analyzer` | Observes or passes through data for analysis/visualization. | Lab analyzers. |
| `sink` | Consumes data without producing a patch output. | Lab CV/audio/output endpoints. |
| `modulator` | Reserved for explicit modulation operators if separated from `generator`. | Future. |

Unknown `operatorType` values are not allowed for public palette/discovery
unless this document is updated first.

## Capability Classes

Capabilities are descriptor facts. They are not UI status, render progress, or
current cache state.

| Class | `canRealtime` | `canHQ` | Meaning |
|---|---:|---:|---|
| `rt_only` | true | false | Runs only in realtime/preview graph. |
| `hq_only` | false | true | Runs only in HQ/offline graph. |
| `rt_hq` | true | true | Runs in both RT and HQ/offline graph. |
| `unavailable` | false | false | Not allowed for normal public operators. Use only quarantined/dev fixtures. |

Rules:

- Public palette operators must support at least one of RT or HQ.
- `canRealtime=false, canHQ=false` must be hidden, quarantined, or treated as a
  development/test descriptor.
- Whole-file and length-changing operators must not claim realtime support
  unless they have an explicit realtime preview contract.
- Capability does not imply port compatibility. Ports decide patchability.

## Process Shapes

`engine.processShape` describes the processing model.

| Shape | Meaning | Normal capability |
|---|---|---|
| `block_length_preserving` | Processes one block and preserves block length. | RT, HQ, or both. |
| `block_stateful_length_preserving` | Block processing with persistent state; length preserving. | RT, HQ, or both. |
| `generator` | Produces signal/audio/control without a normal signal input. | RT, HQ, or both. |
| `whole_file_length_preserving` | Requires complete source material and preserves length. | HQ only. |
| `whole_file_length_changing` | Requires complete source material and may change length. | HQ only. |
| `analysis_data_output` | Converts input material into typed analysis/data artifact. | HQ only. |
| `typed_data_transform` | Consumes typed data and produces typed data or materialized audio. | HQ only. |
| `multi_output_or_multi_file_output` | Produces multiple artifacts/files. | HQ only; explicit scheduler required. |
| `host_source` | Host-owned source such as device/file/project/timeline source. | Lab-owned. |
| `host_sink` | Host-owned sink such as output, file writer, CV sink. | Lab-owned. |
| `host_processor` | Host-owned router/adapter/bus processor. | Lab-owned. |

Unknown process shapes are descriptor errors for public operators.

## Engine Domains

`engine.domain` describes what the operator does. It does not decide cable
compatibility by itself.

| Domain | Meaning | Examples |
|---|---|---|
| `time_audio` | Time-domain audio processing or routing. | Gain, stereo width, file in/out. |
| `spectral_pvoc` | Spectral/PVOC analysis or synthesis domain. | CDP PVOC analysis/synth. |
| `control_data` | Control/CV/event/grid/signal data domain. | Grid signal, CV sink, signal selector. |
| `generator` | Source/generator whose output type is defined by ports. | Test tone, signal noise/LFO. |
| `hybrid` | Host/operator combines more than one domain. | Analyzer insert/tap. |

Future domains require an update to this document and a compatibility story for
their ports.

## Materialization Classes

`engine.materialization` describes what the operator creates outside ordinary
streaming cables.

| Materialization | Meaning | Normal pairing |
|---|---|---|
| `none` | No offline artifact beyond normal graph signal flow. | Block, generator, host route. |
| `audio_buffer` | Materialized audio buffer/layer/clip. | Whole-file audio or typed-data synth. |
| `audio_file` | File-backed rendered audio output. | File out/export. |
| `spectral_data` | File-backed or data-store spectral artifact. | PVOC analysis/data transforms. |
| `control_data` | Materialized control/event/envelope artifact. | Future control-data packs. |
| `report` | Analysis/report artifact, not directly patchable as audio. | Future analysis reports. |
| `file_collection` | Multiple output files/artifacts. | Future multi-output CDP/vendor tools. |

Nested artifact metadata may refine storage (`in_memory`, `file_backed`,
`file_collection`), but it must not replace descriptor-level
`engine.materialization`.

Lab offline artifacts currently classify materialized results as:

- `AudioBuffer`
- `AudioFile`
- `BreakpointTable`
- `TextTable`
- `SpectralAnalysis`
- `PvocAnalysis`
- `AnalysisReport`
- `FileCollection`

Their materialized state may be `Valid`, `Rendering`, `Stale`, `Missing`, or
`Failed`. Those are artifact/cache states, not static operator capabilities.

## Output Length Models

`engine.outputLength` describes the length relationship between input and
output.

| Model | Meaning |
|---|---|
| `same_as_input` | Output length matches input. |
| `fixed_tail` | Output has a fixed extension/tail. |
| `param_dependent` | Output length depends on parameters. |
| `analysis_dependent` | Output length depends on analysis/input data. |
| `no_audio_output` | Operator emits no audio output artifact. |
| `multi_output` | Multiple outputs/files; each output needs explicit metadata. |

`lengthChanging=true` is allowed only with `fixed_tail`,
`param_dependent`, `analysis_dependent`, or `multi_output`.

## ABI / Host Contract Classes

`engine.abiV2Support` states what the host must provide.

| ABI support | Meaning |
|---|---|
| `direct` | Existing block/direct operator path is sufficient. |
| `requires_whole_file_host_contract` | Needs whole-file offline materialization host API. |
| `requires_typed_data_host_contract` | Needs typed-data producer/transform host API. |
| `requires_future_host_contract` | Descriptor is valid but not runnable in the current public host contract. |
| `not_representable` | Cannot be represented by the current operator/pack ABI. |

`requires_future_host_contract` and `not_representable` operators must not
appear as normal runnable palette entries. They may be visible only in explicit
developer/experimental surfaces.

## Allowed Operator Combination Matrix

The following classes are the only allowed public operator combinations. A new
combination requires updating this document, validators, generated descriptors,
Lab scheduling, and tests.

| Class | `operatorType` | `processShape` | Capability | Domain | Materialization | Output length | ABI support | Runnable surface |
|---|---|---|---|---|---|---|---|---|
| `rt_block_audio_processor` | `processor` | `block_length_preserving` or `block_stateful_length_preserving` | `rt_only` or `rt_hq` | `time_audio`, `control_data`, `hybrid` | `none` | `same_as_input` | `direct` | Normal palette. |
| `hq_block_audio_processor` | `processor` | `block_length_preserving` or `block_stateful_length_preserving` | `hq_only` or `rt_hq` | `time_audio`, `control_data`, `hybrid` | `none` | `same_as_input` | `direct` | Normal palette; HQ-only must be clearly labeled. |
| `rt_hq_generator` | `generator` | `generator` | `rt_only`, `hq_only`, or `rt_hq` | `generator` or `control_data` | `none` | `same_as_input` | `direct` | Normal palette if at least one output port exists. |
| `host_source` | `generator` | `host_source` | `rt_only`, `hq_only`, or `rt_hq` | `time_audio`, `control_data`, `hybrid` | `none` | `same_as_input` | host-owned | Lab palette only. |
| `host_sink` | `processor` or `sink` | `host_sink` | `rt_only`, `hq_only`, or `rt_hq` | `time_audio`, `control_data`, `hybrid` | `none` or `audio_file` | `same_as_input` or `no_audio_output` | host-owned | Lab palette only. |
| `host_processor` | `processor`, `analyzer`, or `generator` | `host_processor` | `rt_only`, `hq_only`, or `rt_hq` | `time_audio`, `control_data`, `hybrid` | `none` | `same_as_input` | host-owned | Lab palette only. |
| `offline_whole_file_audio_processor` | `processor` | `whole_file_length_preserving` or `whole_file_length_changing` | `hq_only` | `time_audio` | `audio_buffer` or `audio_file` | `same_as_input`, `fixed_tail`, `param_dependent`, or `analysis_dependent` | `requires_whole_file_host_contract` | Normal palette only when HQ/offline workflow is available. |
| `offline_typed_data_producer` | `processor` or `analyzer` | `analysis_data_output` | `hq_only` | `spectral_pvoc` or `control_data` | `spectral_data`, `control_data`, `report`, or `file_collection` | `no_audio_output` or `multi_output` | `requires_typed_data_host_contract` | Normal palette only when typed-data scheduling is available. |
| `offline_typed_data_transform` | `processor` | `typed_data_transform` | `hq_only` | `spectral_pvoc` or `control_data` | `spectral_data`, `control_data`, `audio_buffer`, or `file_collection` | `no_audio_output`, `analysis_dependent`, or `multi_output` | `requires_typed_data_host_contract` | Normal palette only when typed-data scheduling is available. |
| `offline_multi_output` | `processor` | `multi_output_or_multi_file_output` | `hq_only` | any explicit domain | `file_collection`, `audio_buffer`, `spectral_data`, `control_data`, or `report` | `multi_output` | explicit contract required | Hidden until scheduler/import/materialization support exists. |
| `future_or_unavailable` | any | any | any | any | any | any | `requires_future_host_contract` or `not_representable` | Dev/experimental only; not normal palette. |

Additional constraints:

- `wholeFileRequired=true` is required for whole-file and typed-data offline
  operators.
- `wholeFileRequired=false` is required for direct block operators unless a
  realtime preview/materialization contract is explicitly documented.
- `audioOutput=false` requires `outputLength=no_audio_output` unless
  `multiOutput=true`.
- `multiOutput=true` requires `outputLength=multi_output` and explicit artifact
  metadata per output.
- `materialization=none` must not be used for operators whose only meaningful
  output is an offline artifact.
- Host-owned process shapes must be used only by Lab-owned operators.
- Pack operators must use `direct`,
  `requires_whole_file_host_contract`,
  `requires_typed_data_host_contract`,
  `requires_future_host_contract`, or `not_representable`; they must not rely
  on Lab-private process shapes.

## Operator Availability Classes

Lab should derive an availability class from descriptor facts and current host
support. This is the correct UI classification for palette entries, node
badges, inspector summaries, and diagnostics.

| Availability | Meaning | Normal UI behavior |
|---|---|---|
| `insertable_rt` | Runnable in current realtime graph. | Normal. |
| `insertable_hq` | Runnable in current HQ/offline graph only. | Normal but explicitly labeled `HQ only` or `Offline`. |
| `insertable_rt_hq` | Runnable in both RT and HQ/offline. | Normal. |
| `insertable_data_hq` | Runnable in HQ typed-data graph. | Normal only when typed-data scheduling is enabled; label as `Data/HQ`. |
| `host_owned` | Runnable through Lab host source/sink/processor path. | Normal for Lab operators. |
| `missing_dependency` | Descriptor references unavailable pack/runtime/dependency. | Disabled or missing-node placeholder. |
| `invalid_metadata` | Descriptor violates required metadata. | Hidden/quarantined; developer diagnostic. |
| `future_contract` | Valid descriptor but required host contract is not implemented. | Hidden or explicit experimental disabled entry. |
| `unsupported` | Cannot run in current host. | Disabled/hidden; not a normal node. |

`NodeData::RuntimeState` is a current Canvas implementation detail and is not a
complete classification model. Lab UI must not treat a single colored header
line as the sole expression of operator availability.

## Port Type Model

Every public descriptor port must resolve to a port type record with stable
facts. Project state and graph building must use descriptor port IDs plus
explicit channel/slot coordinates where applicable, not generated UI aliases.

| Field | Required | Meaning | Example |
|---|---:|---|---|
| `id` | yes | Stable descriptor port ID. | `in`, `out`, `pvoc`, `out_l` |
| `type` | yes | Stable namespaced port type ID. | `xyona.audio` |
| `kind` | resolved descriptor fact | Broad runtime class. | `audio`, `control`, `event`, `midi`, `typed_data`, `visual` |
| `domain` | resolved descriptor fact | Port signal/data domain. | `time_audio`, `spectral_pvoc`, `control_data` |
| `rate` | resolved descriptor fact | Execution/data cadence. | `audio_rate`, `control_rate`, `event_rate`, `offline_artifact` |
| `schema` | typed data only | Payload schema contract. | `xyona.cdp.pvoc.analysis.v1` |
| `format` | typed data only | Concrete typed-data format/profile. | `pvoc_analysis`, `breakpoint_curve` |
| `channelPolicy` | yes for audio/control | Channel behavior. | `1`, `2`, `any`, `match_input`, `fixed_n` |
| `mergePolicy` | yes or defaulted | Whether multiple incoming edges can merge. | `sum`, `merge`, `single_source` |
| `executionContext` | yes or defaulted | Runtime limits. | `realtime`, `offline`, `realtime_or_offline` |
| `slotMapping` | slottable operators | Whether the port is `per_slot` or `shared`. | `per_slot` |
| `tags[]` | optional | Extra non-authoritative hints. | `typed_data`, `pvoc_analysis` |
| `ui.role` | optional | UI placement/role hint. | `input`, `output`, `typed_data_output` |

If a field is defaulted by a generator, the generated descriptor must still
transport the resolved fact to Lab.

When generated JSON metadata uses `xyona.schema` as the metadata envelope
marker, the typed-data payload schema must be emitted under a non-conflicting
key such as `xyona.dataSchema` and mapped into descriptor `schema`.

Port domain vocabulary:

| Domain | Meaning |
|---|---|
| `time_audio` | Time-domain audio stream or materialized audio data. |
| `spectral_pvoc` | CDP/phase-vocoder spectral data. |
| `control_data` | Control, CV, event, MIDI, breakpoint, envelope, pitch, or text-like control data. |
| `visual_data` | Analyzer or visual stream data when made patchable. |

Port rate vocabulary:

| Rate | Meaning |
|---|---|
| `audio_rate` | Per-sample or block audio-rate stream. |
| `control_rate` | Control-rate stream or periodically sampled modulation. |
| `event_rate` | Sparse event/MIDI/trigger stream. |
| `offline_artifact` | Materialized offline data or file-backed artifact. |

## Ports, Channels, Cables, Slots, And Lab Endpoints

XYONA has mono audio ports/cables and multichannel audio ports/cables. It does
not have a separate stereo port or stereo cable category. Stereo is the
two-channel case of audio, represented by ordered channels/endpoints such as
`in_0` and `in_1`, optionally grouped by UI/layout metadata.

Use these terms precisely:

| Term | Meaning |
|---|---|
| Descriptor port | Stable logical operator port declared by Core or a pack, for example `in`, `out`, `pvoc`, or `sidechain`. |
| Audio channel | Channel inside an audio descriptor port buffer in the Core/pack DSP ABI. |
| Mono audio port/cable | A one-channel `xyona.audio` port or cable. |
| Multichannel audio port/cable | An ordered bundle of two or more `xyona.audio` channels/endpoints carried together as one logical port/cable. |
| Lab endpoint | Addressable Canvas/engine endpoint for a concrete descriptor port channel, for example `in`, `in_0`, or `out_3`. |
| Slot | Optional orthogonal processing dimension of a slottable operator. Slots are not channels and are not port types. |
| Slot group | UI/layout grouping for slots or endpoints, for example L/R, quad, 5.1, or custom labels. |

Endpoint expansion rule for channelized audio ports:

```text
descriptor port `in` with one audio channel  -> Lab endpoint `in`
descriptor port `in` with two audio channels -> Lab endpoints `in_0`, `in_1`
descriptor port `out` with N audio channels  -> Lab endpoints `out_0` ... `out_N-1`
```

For a stereo signal in Lab, the addressable channel endpoints are therefore
normally:

```text
in_0  = left mono endpoint
in_1  = right mono endpoint
out_0 = left mono endpoint
out_1 = right mono endpoint
```

Those two endpoints may be connected as two mono cables or as one multichannel
cable carrying the ordered pair. Both forms must still resolve to the same
underlying endpoint facts.

`StereoPair` may label or group those endpoints, but it must not create a
distinct `xyona.stereo` type. Project and GraphBuilder code should preserve
structured endpoint facts `descriptorPortId + channelIndex` when available;
textual names such as `in_0` are only the current expanded endpoint spelling.

Slot capability is orthogonal to mono vs. multichannel audio:

```text
mono port/cable         x slotCount N = N one-channel slot surfaces
multichannel port/cable x slotCount N = N ordered multichannel slot surfaces
```

A slottable mono operator normally has `slotCount = 1`; with four slots, its
one-channel port/cable is repeated over slots. A slottable multichannel
operator also normally has `slotCount = 1`; with four slots, each slot carries
the full ordered channel bundle.

## Slot Support And Port Slot Mapping

Slots are an operator-wide capability. Core, Lab, CDP, and future packs may all
ship slottable operators. The DSP/operator implementation declares whether it
is slottable; Lab owns UI, user-editable slot count, routing presentation,
project persistence, and graph endpoint expansion.

Slot support is explicit:

| Field | Meaning |
|---|---|
| `slots.supported=false` or missing | Operator has no slot dimension. It is a normal non-slotted operator. |
| `slots.supported=true` | Operator has a slot dimension. Its normal collapsed form is one slot. |
| `slots.defaultCount` | Default slot count. Must be `1` for ordinary slottable operators. |
| `slots.minCount` | Minimum slot count. Must be at least `1`. |
| `slots.maxCount` | Maximum supported slot count. |
| `slots.countParamId` | Optional topology parameter controlling slot count. |

Do not use `slotCount=0` to mean normal operation in the operator contract.
Zero slots means no processing slots. Normal slottable operation is one slot.
Current legacy descriptors may use missing slot metadata or `slotCount=0` as a
Lab implementation detail for non-slot-aware operators, but public contract
metadata must resolve that to `slots.supported=false`.

For a slottable operator, every input and output port must declare one of two
slot mappings:

| `slotMapping` | Meaning |
|---|---|
| `per_slot` | The port exists per slot. Endpoint addresses include `slotIndex`. |
| `shared` | The port exists once for the operator instance and is shared by all slots. Endpoint addresses do not include `slotIndex`. |

This is the first-level slot contract. Do not introduce broader mapping labels
such as `broadcast`, `split`, `reduce`, or `matrix` unless this contract is
updated first. Their behavior must be represented by `per_slot`/`shared` plus
explicit operator processing semantics.

Input rules:

- `input.slotMapping=per_slot` means each slot can receive its own mono or
  multichannel input cable.
- `input.slotMapping=shared` means one input cable/bundle feeds the operator
  instance and is available to every slot.

Output rules:

- `output.slotMapping=per_slot` means each slot produces its own mono or
  multichannel output cable/bundle.
- `output.slotMapping=shared` means the operator produces one instance-wide
  output. For processors, this is allowed only when the operator explicitly
  defines deterministic aggregation, selection, analysis, or sink semantics.
- A normal slottable processor should have at least one `per_slot` output.
  Otherwise users cannot address the slot results.

Validation rules:

- A slottable operator must declare `slotMapping` on every public input and
  output.
- A non-slottable operator must not expose slot-addressable endpoints.
- A slottable operator must have at least one slot-aware surface: a `per_slot`
  input, a `per_slot` output, or at least one `per_slot` parameter.
- Per-slot parameters use `scopeSupport: [global, per_slot]` and address values
  as `<paramId>@slot=<slotIndex>`.

Examples:

```yaml
slots:
  supported: true
  countParamId: slot_count
  defaultCount: 1
  minCount: 1
  maxCount: 16

ports:
  inputs:
    - id: in
      type: xyona.audio
      channelPolicy: any
      slotMapping: per_slot
  outputs:
    - id: out
      type: xyona.audio
      channelPolicy: match_input
      slotMapping: per_slot
```

```yaml
ports:
  inputs:
    - id: sidechain
      type: xyona.audio
      channelPolicy: any
      slotMapping: shared
  outputs:
    - id: out
      type: xyona.audio
      channelPolicy: match_input
      slotMapping: per_slot
```

## Audio Port Specification

An audio port is a port whose `type` is `xyona.audio`.

Required resolved facts:

```yaml
type: xyona.audio
kind: audio
domain: time_audio
rate: audio_rate
executionContext: realtime_or_offline # or the stricter actual context
```

Allowed `channelPolicy` values for audio ports:

| Policy | Meaning |
|---|---|
| `mono` or `1` | Exactly one channel. |
| `2` | Fixed two-channel DSP buffer contract. This is not a stereo port type; Lab resolves it as two ordered audio endpoints and may present it as a multichannel cable. |
| `any` | Any supported channel count; Core treats channel semantics as host-neutral. |
| `match_input` or `match_inputs` | Output channel count follows corresponding input. |
| `fixed_n` | Fixed N channels; descriptor must carry N explicitly or through generated `channels`. |

Allowed audio merge policies:

| Merge policy | Meaning |
|---|---|
| `sum` | Multiple sources may sum/mix into this input. |
| `single_source` | Only one incoming source is allowed. |
| empty/default | Lab must resolve to the operator/category default before graph validation. |

Audio port rules:

- `xyona.audio` connects only to compatible `xyona.audio` ports.
- `xyona.audio` is the only built-in streaming audio port type. There is no
  `xyona.stereo` or `xyona.audio.stereo` port type.
- `xyona.audio` must not connect directly to typed-data ports.
- Channel semantics such as mono, stereo, 5.1, 7.1, immersive, or physical
  output mapping are host/Lab concerns unless the operator explicitly requires
  a fixed channel count. Lab may expose those channels as mono cables or as a
  bundled multichannel cable, but the underlying endpoint facts remain ordered
  audio channels, not a separate stereo type.
- A spectral operator may still have audio ports. Example: PVOC analysis has an
  audio input and PVOC typed-data output.
- Audio file or materialized audio artifacts are not the same as `xyona.audio`
  streaming ports. Use `xyona.audio.buffer` or an explicit artifact contract
  when a materialized buffer is patched as data.

## Built-In Port Types

Core provides the small canonical vocabulary. It is not an exhaustive list of
all future formats; packs may add namespaced concrete types that map to these
broad kinds.

| Type ID | Kind | Domain | Rate | Notes |
|---|---|---|---|---|
| `xyona.audio` | `audio` | `time_audio` | `audio_rate` | Realtime/block audio stream. |
| `xyona.audio.buffer` | `typed_data` | `time_audio` | `offline_artifact` | Materialized audio buffer/whole-file artifact. |
| `xyona.signal` | `control` | `control_data` | `control_rate` | Generic non-audio signal stream. |
| `xyona.signal.cv` | `control` | `control_data` | `control_rate` | Continuous scalar/modulation value. |
| `xyona.signal.gate` | `event` | `control_data` | `event_rate` | Gate/trigger edge. |
| `xyona.signal.clock` | `event` | `control_data` | `event_rate` | Clock/transport pulse. |
| `xyona.midi.v1` | `midi` | `control_data` | `event_rate` | MIDI 1.0 event stream. |
| `xyona.midi.mpe.v1` | `midi` | `control_data` | `event_rate` | MPE profile. |
| `xyona.midi.v2` | `midi` | `control_data` | `event_rate` | Reserved MIDI 2.0 profile. |
| `xyona.visual.stream` | `visual` | `visual_data` | `event_rate` or `control_rate` | Analyzer/visual streams if made patchable. |

## CDP Port Types

Current CDP concrete typed-data type:

| Type ID | Kind | Domain | Rate | Schema | Format |
|---|---|---|---|---|---|
| `cdp.pvoc.analysis.v1` | `typed_data` | `spectral_pvoc` | `offline_artifact` | `xyona.cdp.pvoc.analysis.v1` | `pvoc_analysis` |

The canonical port type is `cdp.pvoc.analysis.v1`. The current Offline Session
payload schema remains `xyona.cdp.pvoc.analysis.v1`; descriptors must carry
both values explicitly rather than treating them as interchangeable.

Reserved future CDP candidates:

| Type ID | Kind | Domain | Expected format |
|---|---|---|---|
| `cdp.pitch.track.v1` | `typed_data` | `control_data` | `pitch_track` |
| `cdp.transposition.track.v1` | `typed_data` | `control_data` | `transposition_track` |
| `cdp.formant.envelope.v1` | `typed_data` | `spectral_pvoc` | `formant_envelope` |
| `cdp.envelope.curve.v1` | `typed_data` | `control_data` | `envelope_curve` |
| `cdp.breakpoint.curve.v1` | `typed_data` | `control_data` | `breakpoint_curve` |
| `cdp.number.list.v1` | `typed_data` | `control_data` | `number_list` |
| `cdp.soundfile.list.v1` | `typed_data` | `time_audio` | `soundfile_list` |

Reserved candidates must not appear in public descriptors until generator,
validator, Lab compatibility, scheduler, materialization, and tests support
them.

## Patch Compatibility Rules

Compatibility is decided by source and target port facts, not by operator facts.

Allowed by default:

| Source | Target | Rule |
|---|---|---|
| `xyona.audio` | `xyona.audio` | Allowed when channel policy and merge policy allow it. |
| `xyona.signal` | `xyona.signal` | Allowed. |
| `xyona.signal.cv` | `xyona.signal.cv` | Allowed. |
| `xyona.signal.gate` | `xyona.signal.gate` | Allowed. |
| `xyona.signal.clock` | `xyona.signal.clock` | Allowed. |
| MIDI | MIDI | Allowed only by explicit MIDI profile compatibility. |
| typed data | typed data | Allowed only when `type`, `schema`, and `format` are compatible. |

Blocked by default:

| Source | Target | Reason |
|---|---|---|
| typed data | `xyona.audio` | Requires explicit synthesis/conversion operator. |
| `xyona.audio` | typed data | Requires explicit analysis/conversion operator. |
| typed data | control/audio/MIDI | Cross-domain conversion must be explicit. |
| unknown type | any | Unknown types are not patch-compatible unless explicit facts/rules allow it. |

Valid PVOC bridge:

```text
xyona.audio -> cdp.pvoc.anal.in
cdp.pvoc.anal.pvoc -> cdp.pvoc.synth.pvoc
cdp.pvoc.synth.out -> xyona.audio
```

Invalid examples:

```text
cdp.pvoc.analysis.v1 -> xyona.audio
xyona.audio -> cdp.pvoc.analysis.v1
cdp.pvoc.analysis.v1 -> xyona.signal.cv
```

The rule is:

```text
operator domain = what the operator does
port type       = what flows through the connection
compatibility   = whether this exact connection may exist
```

## Parameter Metadata

Every parameter must expose stable descriptor facts.

| Field | Required | Meaning |
|---|---:|---|
| `id` | yes | Stable machine ID. |
| `descriptor.label` | yes | UI label. |
| `descriptor.type` | yes | `float`, `int`, `bool`, `enum`, `string`, `file`, or `path` where supported. |
| `descriptor.min` | numeric params | Minimum numeric value. |
| `descriptor.max` | numeric params | Maximum numeric value. |
| `descriptor.default` | yes | Default raw value. |
| `descriptor.unit` | optional | Unit label. |
| `descriptor.description` | yes | Technical/user description. |
| `descriptor.group` | yes | UI grouping. |
| `descriptor.display` | optional | UI control hint. |
| `descriptor.precision` | yes | Display precision or `-1` auto. |
| `descriptor.available` | yes | `realtime`, `hq`, or `both`. |
| `descriptor.isTopology` | optional | True if changes rebuild ports/topology. |
| `descriptor.scope` | optional | `global`, `slot`, `per_slot`, `voice`, or `per_voice`. |
| `visibleWhenParam` / `visibleWhenValues` | optional | Visibility dependency. |

Parameter availability must not reference a capability the operator does not
support.

## Adapter Rules

Module-owned adapters stay under the module root:

```yaml
adapter:
  header: operators/edit/cut/adapter/cdp_edit_cut.h
  source: src/operators/edit/cut/adapter/cdp_edit_cut.cpp
  registrationFunction: registerEditCutV2
```

Shared implementation stays under the family `common` folder and is declared
explicitly:

```yaml
adapter:
  header: operators/edit/cutend/adapter/cdp_edit_cutend.h
  source: src/operators/edit/cutend/adapter/cdp_edit_cutend.cpp
  sharedSources:
    - src/operators/edit/common/cdp_edit_cut_sessions.cpp
  registrationFunction: registerEditCutEndV2
```

Do not point one module's `adapter.header` or `adapter.source` into another
module's adapter directory.

## Help Contract

Every public operator help article uses:

```text
help.node.<operator_id>
```

Examples:

```text
help.node.gain
help.node.slot_gain
help.node.cdp.utility.identity
help.node.cdp.modify.loudness_gain
help.node.lab.audio_in
```

Core and pack operator help belongs with the owning package. Lab owns Lab-only
panels, topics, workflows, and host-operator help. Lab must not author CDP or
Core DSP help as a substitute for the owning package.

The normative help content and validation contract lives in
`OPERATOR_HELP_STANDARD.md`. The first implementation slice is archived in
`docs/done/ROADMAP_OPERATOR_HELP_STANDARD.md`; remaining operator-help product
work is tracked in `ROADMAP_OPERATOR_HELP_STANDARD_FOLLOWUP.md`. Backward
compatibility with legacy operator help structure is not required; every public
operator help file must use `standard: operator_help_v1`.

## Operator Technical Summary For Lab

Lab must be able to present operator facts, not only port tooltips. A complete
operator tooltip or inspector summary should include:

```text
Operator: <label>
ID: <id>
Provider/Family: <providerLabel>/<family>
Type: <operatorType>
Capability: RT, HQ, RT+HQ, HQ only, or unavailable
Availability: insertable_rt, insertable_hq, insertable_data_hq, ...
Process: <engine.processShape>
Domain: <engine.domain>
Materialization: <engine.materialization>
Output length: <engine.outputLength>
Host contract: <engine.abiV2Support or host-owned>
Ports: stable input/output IDs and types
Parameters: visible count plus topology-sensitive params
Reason if disabled: invalid metadata, missing dependency, future contract, unsupported
```

This summary is the correct place for operator-level metadata. A header accent
or color may be used as a secondary cue only after the summary and disabled
state are clear.

## Palette And Node UI Rules

- Normal palette entries must be insertable in at least one supported host
  workflow.
- Disabled palette entries must explain exactly which fact blocks insertion.
- Unsupported or future-contract operators must not look like ordinary runnable
  nodes.
- RT/HQ/Data/Offline should be represented as explicit text or badge metadata,
  not only as a color.
- Render/materialization progress is a transient runtime state and must not be
  conflated with static descriptor capability.
- Port tooltips describe port facts. Operator tooltips/inspectors must describe
  operator facts.

## Visual Token Ownership

Port colors, tooltip text, cable styling, hover states, and hit-target styling
are Lab concerns. They must be derived from port type facts through a Lab
registry, not hardcoded in individual node renderers.

Core and packs provide semantic facts. They must not provide JUCE colors or
Canvas layout rules.

Port icons/glyphs are out of scope for port visuals. Future multicore/bundled
cables must be represented by explicit connection facts and styled through the
same Lab registry rather than by overlay-local rules.

## Ownership Boundaries

- `xyona-core` owns host-neutral descriptor types, operator metadata
  validation, generated metadata, pack ABI surfaces, and compatibility facts
  that are independent of any UI.
- `xyona-cdp-pack` owns CDP-specific concrete port type declarations and schema
  facts, for example PVOC analysis data, pitch tracks, envelope files,
  breakpoint lists, provenance, and CDP validation fixtures.
- `xyona-lab` owns Canvas rendering, drag highlighting, connection blocking,
  project import validation, GraphBuilder revalidation, operator tooltips,
  inspector presentation, and visual tokens.
- `CDP8` is reference only. It can justify CDP type semantics, but modern
  descriptors and validation belong in Core and the CDP pack.

## Enforcement Points

This contract must be enforced at multiple layers:

- Operator module validators reject missing or incomplete identity, engine, and
  port metadata.
- Generated descriptors expose stable descriptor port IDs and type facts.
- Pack loaders reject invalid public descriptors for normal discovery.
- Lab-owned public operator registration rejects incomplete descriptors.
- Lab discovery does not repair incomplete descriptors.
- Canvas drag highlighting only marks compatible targets.
- Canvas connection creation rejects incompatible edges.
- Project import rejects or quarantines invalid edges.
- GraphBuilder validates compatibility again before execution.
- Tests cover valid and invalid audio, control, MIDI, and typed-data edges.

The shared validator must fail when:

- a public implementation module under `src/operators` lacks module-local
  `op.yaml`
- `src/processes` contains public operator sources/specs
- public operator `meta.yaml` is present
- provider-prefixed dotted source directories are present under `src/operators`
- flat public CDP adapter files are present under `src/operators`
- path family/module does not match `family` and `moduleName`
- adapter header/source paths leave the owning module root
- shared adapter sources leave `src/operators/<family>/common/`
- `provider`, `family`, `moduleName`, `ui.shortLabel`, `ui.nodeNameStem`,
  `engine.domain`, or `engine.materialization` is missing
- `family` repeats the provider namespace
- a pack or Lab operator ID does not start with `<provider>.`
- `ui.nodeNameStem` contains dots, provider fragments, or invalid characters
- labels are provider-prefixed with strings such as `CDP:`
- whole-file or length-changing operators claim realtime without an explicit
  contract
- generated descriptors, registration, or source lists are stale

Package-local runtime/spec tests then compare generated descriptors to runtime
discovery.

## Implementation Rollout Baseline

The detailed rollout status belongs in the roadmap and report documents. The
baseline implementation sequence retained from the previous port compatibility
contract is:

1. Add contract docs and AGENTS references in Root, Core, Lab, and CDP pack.
2. Extend Core descriptor/metadata surfaces with explicit port type facts.
3. Make Core and pack validators fail on untyped public ports.
4. Update CDP PVOC operators to declare `cdp.pvoc.analysis.v1` consistently.
5. Update Lab public operator specs and runtime metadata to carry port types.
6. Replace generic Canvas semantic wiring with descriptor port IDs.
7. Add a central Lab connection compatibility service.
8. Wire compatibility into drag highlighting, connection creation, import, and
   GraphBuilder validation.
9. Add focused tests before broad UI polish.

## Extension Rules For Future Packs

Future packs such as Faust, Maximilian, or vendor-specific XYONA packs may add
provider namespaces, families, process classes, and port types only when they
also provide:

- stable `provider`, `family`, `moduleName`, and `id` naming
- explicit `engine` classification
- explicit port type facts, including typed-data schema and format where needed
- compatibility rules for any new port type
- host scheduling/materialization support for any non-direct ABI contract
- descriptor/generator validation
- Lab UI/inspector text
- focused tests for valid and invalid patching

New concrete port types must:

- use a stable namespaced ID, for example `faust.audio` or
  `vendor.spectral.frame.v1`
- map to a known broad `kind`
- declare `domain`, `rate`, and `executionContext`
- declare `schema` and `format` for typed data
- declare compatibility with built-in or pack-local types explicitly
- avoid relying on Lab-specific colors, cable styling, or renderer behavior

Core should only grow a new broad `kind` when a new runtime class genuinely
cannot be modeled by the existing vocabulary.

Any future pack type not listed here is considered unknown and not
patch-compatible by default.

## Verification

Before committing operator-structure work:

- Run the affected repo's operator-module validator.
- Run generation staleness checks where the repo has generated artifacts.
- Run targeted build and CTest for the affected operator/discovery surface.
- Run Lab Canvas smoke tests when labels, node-name stems, descriptor metadata,
  or pack discovery change.
- Run `git diff --check`.

Use repo-local commands. The XYONA root is a workspace, not a monorepo build.

## Related Documents

- `OPERATOR_MODULE_AUTHORING_GUIDE.md` - practical authoring instructions.
- `docs/done/ROADMAP_OPERATOR_MODULE_STRUCTURE.md` - archived
  operator-module migration roadmap.
- `docs/done/REPORT_OPERATOR_MODULE_NAMING_STRUCTURE.md` - archived
  operator-module implementation report.
- `docs/done/ROADMAP_OPERATOR_PORT_TYPES_AND_PATCH_COMPATIBILITY.md` - archived
  port compatibility rollout roadmap.
- `docs/done/REPORT_OPERATOR_PORT_TYPES_AND_PATCH_COMPATIBILITY_2026-04-30.md` -
  archived port compatibility implementation report.
