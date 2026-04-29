# XYONA Operator Module Contract

**Status:** Workspace standard  
**Version:** 1.2-draft
**Date:** 2026-04-29
**Applies to:** `xyona-core`, `xyona-cdp-pack`, future operator packs, Lab help consumption

## Intent

All public XYONA operators must be authored, documented, indexed, and exposed
through the same structure, independent of whether the operator ships in
`xyona-core` or in a dynamic pack.

This contract exists because the current workspace has several partially
overlapping conventions:

- Core operators use process folders, `meta.yaml`, generated JSON, C++ runtime
  descriptors, and operator help files.
- CDP pack operators use flat C++ files with C ABI descriptors and JSON metadata
  embedded in code.
- Lab has its own filesystem help layout and a generated help index.
- CDP8 has useful original process documentation, but its user text is CLI- and
  CDP-specific, not a Lab-ready help format.

The standard below is the canonical shape.

## Breaking Migration Policy

This contract does not preserve legacy operator naming or metadata behavior.
During the operator-module migration, old descriptor layouts, missing module
identity fields, provider-prefixed labels, provider-prefixed source folders,
aggregate operator spec files, and ID-derived Canvas node-name fallbacks may be
removed without alias layers.

Rules:

- Do not add compatibility aliases for old operator IDs or old module paths.
- Do not accept pack descriptors that omit required module identity metadata.
- Do not derive pack `provider`, `family`, `moduleName`, `ui.nodeNameStem`,
  `engine.domain`, or `engine.materialization` from IDs, labels, categories, or
  private file paths.
- Do not use provider-prefixed visible labels such as `CDP: Loudness Gain`.
- Do not create new `src/processes` or `src/operators/cdp.modify` modules.

Any current code that still relies on legacy Core `meta.yaml`, `src/processes`,
or discovery defaults is migration debt, not a compatibility guarantee.

## Required Module Shape

Every public operator must have one module root:

```text
src/operators/<family>/<module>/
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

`<family>` is provider-local. It must not repeat the provider namespace. For
example, the CDP operator `cdp.modify.loudness_gain` lives in a `modify`
family module, not in a canonical `cdp.modify` family. Provider-prefixed paths
such as `src/operators/cdp.modify/loudness_gain/` are invalid module roots.

Current Core code may still be found under the old implementation path:

```text
src/processes/<family>/<module>/
```

The target path is `src/operators`. `src/processes` is not a compatibility
location; it is an unmigrated implementation location that should disappear as
Core operator modules move.

## Required Files

`op.yaml` is required for every public operator.

`docs/en.md` is required for every public operator.

`docs/de.md` is required for all release-ready operators. During development it
may lag behind, but release validation must fail if the German file is missing.

`README.md` is required for non-trivial operators and recommended for all
operators. It is developer-facing. The HelpCenter uses `docs/<locale>.md`, not
the module README.

Tests are required for every implemented operator. Operators that cannot have a
stable audio golden reference must still have descriptor and behavioral tests.

## Offline ABI Guardrail

The current whole-buffer offline ABI, currently named
`offline_whole_buffer_prototype`, is a prototype/reference surface only. If
represented in an operator module, use an explicit prototype name such as
`adapter/offline_whole_buffer_prototype.cpp`, not a name that implies a released
production ABI. The prototype may describe bounded, same-length, whole-buffer
operators such as the current CDP loudness-normalise slice while the production
Offline Session ABI is being built.

Production-scale offline operators must target the session/streaming offline
contract once the Offline Session ABI exists. This includes length-changing,
PVOC/spectral, multi-output, multi-file, long-running, or large-source CDP
operators.

The module contract must therefore be able to describe both:

- a prototype whole-buffer adapter for bounded same-length work
- a production offline-session adapter for streamed execution, progress,
  cancellation, output-length discovery, and host asset/scratch policy

Before release, public operators that still use the prototype whole-buffer ABI
must be ported to the Offline Session ABI, or the prototype surface must be
explicitly scoped as an internal test helper instead of a pack contract.

## `op.yaml` Ownership

`op.yaml` is the source of truth for:

- public operator ID
- provider namespace
- provider display label
- family and module name
- label, summary, description, category, icon, version
- short UI labels and default Canvas instance naming
- operator type
- RT/HQ capabilities
- engine/process shape
- execution/domain classification and materialization contract
- input/output port descriptors
- parameter descriptors
- parameter availability and scope
- help ID, locale list, tags, and related articles
- provenance
- validation strategy
- host boundary and ownership

C++ code is the source of truth only for behavior.

## Identity, Provider, Family, And Module Rules

Operator identity is split into separate public fields. Do not encode UI,
provider, family, and persistence concerns into one string.

| Field | Meaning | Example |
|---|---|---|
| `id` | Immutable machine identity used for persistence, lookup, help, and tests. | `cdp.modify.loudness_gain` |
| `provider` | Stable lowercase namespace of the shipping source. | `cdp` |
| `providerLabel` | Human display label for the provider. | `CDP` |
| `family` | Provider-local operator family or type. It must not include `provider`. | `modify` |
| `moduleName` | Provider-local module name. | `loudness_gain` |
| `label` | Human operator name without forced provider/family prefix. | `Loudness Gain` |
| `category` | Browser grouping path. It may include provider context. | `CDP/Modify` |

Rules:

- `provider` is required for every public operator. Core uses `core`; Lab uses
  `lab`; the CDP dynamic pack uses `cdp`; future packs use their pack ID.
- `providerLabel` is required for packs and Lab-authored public operators. Core
  may use `Core` or leave provider display to the host.
- `family` is provider-local. Use `modify`, `pvoc`, `edit`, `utility`,
  `system.audio`, or `timeline.grid`, not `cdp.modify` or `lab.system.audio`.
- `moduleName` is lowercase ASCII snake_case.
- Pack and Lab operator IDs must start with `<provider>.`.
- New pack IDs should normally use `<provider>.<family>.<moduleName>`.
- Core operator IDs may remain plain stable IDs such as `gain` and
  `signal_lfo`, but their `op.yaml` must still declare `provider: core`,
  `family`, and `moduleName`.
- Lab-authored public IDs must still expose clean `provider`, `family`, and
  `moduleName` metadata even when an existing short ID is kept by explicit
  product decision.
- Do not use hyphens in machine IDs, family segments, module names, parameter
  IDs, or node-name stems. Use underscores.

## Operator Execution And Domain Taxonomy

Operator classification is intentionally multi-axis. Do not collapse execution
mode, process shape, signal domain, and host materialization into one enum or
into provider-specific categories such as "CDP audio" vs. "CDP spectral".

### Axis 1: Execution Capability

Execution capability is represented by `capabilities.canRealtime` and
`capabilities.canHQ`.

| Label | Meaning |
|---|---|
| `RT` | The operator can run in the realtime graph, block by block, under realtime-safety constraints. |
| `HQ` | The operator can run in an offline/HQ graph or offline session. |
| `RT+HQ` | The normal case for deterministic block audio DSP that can preview live and render offline. |
| `RT-only` | Host/live/device-bound operation that has no deterministic or useful HQ render path. |
| `HQ-only` | Offline-only operation, usually because it is heavy, whole-file, length-changing, analysis-producing, or requires a host artifact contract. |

`RT-only` does not mean "currently used in a realtime patch"; it means
`canRealtime=true` and `canHQ=false`. For example, Audio In and Audio Out are
typically realtime-only host I/O nodes. A gain, pan, filter, or block-safe CDP
effect used between them is usually `RT+HQ`, even when the current signal path is
pure realtime.

### Axis 2: Process Shape

Process shape describes scheduling and I/O behavior, not audio domain.

| Shape | Meaning | Typical capability |
|---|---|---|
| `block_length_preserving` | Processes bounded blocks and emits the same number of samples. | Usually `RT+HQ` |
| `block_stateful_length_preserving` | Processes bounded blocks with state, latency, tails, or history. | `RT+HQ` if realtime-safe; otherwise `HQ-only` |
| `whole_file_length_preserving` | Requires the full input/render range but emits same-length audio. | `HQ-only` until an explicit realtime contract exists |
| `whole_file_length_changing` | Requires whole-file scheduling and can change output length. | `HQ-only` |
| `generator` | Produces output from parameters, time, data, or host context. | `RT+HQ`, `RT-only`, or `HQ-only` depending on determinism and host requirements |
| `analysis_data_output` | Produces analysis data or reports rather than ordinary audio. | Usually `HQ-only` |
| `typed_data_transform` | Transforms non-audio artifacts such as breakpoint, text, or spectral data. | Usually `HQ-only` until typed realtime contracts exist |
| `multi_output_or_multi_file_output` | Produces multiple artifacts or files. | `HQ-only` until a host contract exists |

Whole-file and length-changing operators must not claim realtime support unless
there is an explicit realtime/preview contract. A dual-mode operator may expose
a bounded realtime preview plus an authoritative HQ whole-file path, but that is
a hybrid contract and must be documented as such.

### Axis 3: Signal Or Artifact Domain

Domain describes what the algorithm consumes, transforms, or emits.

| Domain | Meaning |
|---|---|
| `time_audio` | Ordinary sample-domain audio. |
| `spectral_pvoc` | Spectral, FFT, PVOC/PVX, or related analysis/resynthesis data. |
| `control_data` | Breakpoint tables, text tables, envelopes, reports, control streams, or other typed data. |
| `generator` | Generates audio or data from parameters, models, randomness, or host time. |
| `hybrid` | Crosses domains, for example audio -> spectral analysis -> transformed data -> resynthesized audio. |

Domain is independent from `RT` and `HQ`:

- `HQ / time_audio` is valid, for example whole-file normalise, cut, or length
  change.
- `HQ / spectral_pvoc` is valid, for example PVOC analysis, spectral transform,
  and resynthesis.
- `RT+HQ / spectral_pvoc` is possible only for streaming spectral algorithms
  with bounded latency and realtime-safe resource use.
- `RT+HQ / time_audio` is the common case for block-safe audio DSP.

Do not infer domain from provider alone. CDP can contain time-domain audio,
spectral/PVOC, analysis, text/data, generator, and hybrid processes. Non-CDP
packs and Core operators can have the same domains.

`engine.domain` is required in `op.yaml` and must use one of the domain tokens
above.

### Axis 4: Materialization

Materialization describes whether an offline result is turned into a host-owned
artifact that can be cached, persisted, reused, or re-enter the realtime graph.

| Label | Meaning |
|---|---|
| `WF` | Whole-file: the operator needs the complete input/render range before the correct output can be known. |
| `MAT` | Materialized: the host stores the result as an artifact such as audio buffer/file, layer clip, analysis table, PVOC data, report, or file collection. |
| `LC` | Length-changing: output duration can differ from input duration. |
| `ANL` | Analysis/data output: output is not ordinary audio. |

`WF` and `MAT` are related but not identical. `WF` is an execution requirement.
`MAT` is a host artifact/result state. A block HQ render may stream directly
without creating a materialized artifact, and a future freeze/generator workflow
may materialize an artifact without requiring whole-file input.

`engine.materialization` is required in `op.yaml`. Use `none` when the operator
does not require a host-owned artifact. Use a concrete artifact token such as
`audio_buffer`, `audio_file`, `spectral_data`, `control_data`, `report`, or
`file_collection` when the host must store or expose an offline result. The
visible `MAT` badge is derived from any value other than `none`.

### Canonical Combination Examples

| Example | Capability | Shape | Domain | Materialization |
|---|---|---|---|---|
| Audio In | `RT-only` | host source | `time_audio` | none |
| Gain, pan, EQ, block-safe CDP gain | `RT+HQ` | `block_length_preserving` | `time_audio` | none |
| Realtime FFT analyzer with bounded latency | `RT+HQ` | `block_stateful_length_preserving` | `spectral_pvoc` or `hybrid` | optional data |
| CDP normalise | `HQ-only` | `whole_file_length_preserving` | `time_audio` | audio `MAT` |
| CDP cut or length change | `HQ-only` | `whole_file_length_changing` | `time_audio` | audio `MAT`, `LC` |
| PVOC analysis / spectral transform | `HQ-only` unless streaming contract exists | whole-file or typed-data transform | `spectral_pvoc` | spectral/audio/data `MAT` |
| Analysis report | `HQ-only` | `analysis_data_output` | `control_data` or `hybrid` | data/report `MAT` |
| Audio Out / MainBus device output | `RT-only` | host sink | `time_audio` | none |

### UI Labels

Hosts should present execution and domain as separate UI signals. For example,
use execution badges such as `RT`, `HQ`, `WF`, `MAT`, `LC`, `ANL`, and separate
domain badges such as `AUDIO`, `SPEC`, `DATA`, `GEN`, or `HYB`.

Do not use a different node header style to mean both "CDP" and "offline" or
both "spectral" and "whole-file". Header status, domain, and provider are
separate concepts.

## Required `op.yaml` Fields

Minimum schema:

```yaml
schema: xyona-operator-v1

id: cdp.modify.loudness_gain
provider: cdp
providerLabel: CDP
family: modify
moduleName: loudness_gain
label: Loudness Gain
summary: Adjusts loudness by a linear CDP gain factor.
description: |
  CDP8 rewrite of modify loudness mode 1.
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
  outputLength: same_as_input
  wholeFileRequired: false
  lengthChanging: false
  materialization: none
  audioOutput: true
  multiOutput: false
  abiV2Support: direct

ports:
  inputs: []
  outputs: []

params: []

help:
  id: help.node.cdp.modify.loudness_gain
  locales: [en, de]
  tags: [node, cdp, modify, loudness, gain]
  related: []

validation:
  strategy: analytic_golden_buffer
```

CDP-derived operators must also include:

```yaml
provenance:
  source: cdp8
  cdp:
    library: modify
    program: modify
    process: loudness
    mode: LOUDNESS_GAIN
    processNumber: 195
    modeNumber: 0
    commandMode: 1
    sourceFile: dev/modify/gain.c
```

## Operator ID Rules

Core operator IDs use plain stable IDs:

```text
gain
hq_gain
slot_gain
signal_lfo
```

Pack and Lab operator IDs must start with their provider namespace:

```text
cdp.utility.identity
cdp.modify.loudness_gain
cdp.modify.space_mirror
lab.audio_in
lab.timeline.grid_source
```

The filesystem path is not authoritative. `op.yaml:id` is authoritative.

## Display And Instance Naming Rules

Operator IDs are machine identity, not Canvas display names.

This distinction is mandatory for packs. A namespaced pack ID such as
`cdp.modify.loudness_gain` is correct for persistence, lookup, help IDs, tests,
and provenance, but it is not acceptable as the default visible node instance
name. Core currently hides this problem only because Core IDs such as `gain`
are already short.

Every public operator must therefore expose separate naming surfaces:

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

Meanings:

- `id`: immutable machine ID. It may be long and namespaced.
- `provider` and `providerLabel`: provider identity and display label.
- `family`: provider-local family/type. It must not include the provider.
- `moduleName`: provider-local module identifier.
- `label`: human operator name for browsers, descriptors, help titles, and
  search results. It should not mechanically repeat provider and family if the
  UI already shows those separately.
- `category`: browser/grouping path such as `CDP/Modify`.
- `ui.shortLabel`: compact label for constrained UI surfaces.
- `ui.nodeNameStem`: default Canvas instance-name prefix.

Canvas default names must be generated from `ui.nodeNameStem`, not from `id`.

Examples:

| Operator ID | Label | Category | Node Name Stem | Default Instances |
|---|---|---|---|---|
| `gain` | `Gain` | `Amplitude` | `gain` | `gain1`, `gain2` |
| `cdp.modify.loudness_gain` | `Loudness Gain` | `CDP/Modify` | `loud_gain` | `loud_gain1` |
| `cdp.modify.space_mirror` | `Space Mirror` | `CDP/Modify` | `mirror` | `mirror1` |
| `cdp.distort.waveset_density` | `Waveset Density` | `CDP/Distort` | `density` | `density1` |
| `lab.audio_in` | `Audio Input` | `Lab/System/Audio` | `audio_in` | `audio_in1` |
| `lab.timeline.grid_source` | `Grid Signal` | `Lab/Timeline/Grid` | `grid` | `grid1` |

Rules:

- `ui.nodeNameStem` must be short, lowercase, ASCII, and stable.
- `ui.nodeNameStem` must not contain dots or provider namespace fragments such
  as `cdp.modify`.
- `ui.nodeNameStem` should be unique across the discovered operator set. If a
  collision is unavoidable, add the smallest useful qualifier, for example
  `cdp_gain` rather than `cdp.modify.loudness_gain`.
- Persisted projects must keep both the immutable operator `id` and the editable
  node instance name. Renaming a node must not change the operator ID.
- Hosts may show provider/family context in menus, breadcrumbs, tooltips, and
  search filters. They should not force that context into the Canvas node name.
- Hosts must not mutate `label` to add provider prefixes such as `CDP: `. Use
  `providerLabel`, menu grouping, badges, breadcrumbs, or search facets instead.
- Browser rows may display provider and category context, for example
  `Loudness Gain` with `CDP / Modify`, but the stored descriptor label remains
  `Loudness Gain`.

Runtime requirement:

1. Use `ui.nodeNameStem` for default Canvas node names.
2. Reject or mark invalid any discovered pack operator that lacks
   `ui.nodeNameStem`.
3. Do not derive new pack node names from dotted provider-qualified IDs.
4. Do not sanitize an invalid pack stem into a different accepted stem; fix the
   operator metadata instead.

## Descriptor And ABI Transport Requirements

The naming contract is only useful if it reaches the host through public
discovery. Private source paths, C++ filenames, or pack-local conventions are
not valid transport surfaces.

The public descriptor/discovery surface consumed by Lab must expose, either as
typed descriptor fields or as structured operator metadata:

- `provider`
- `providerLabel`
- `family`
- `moduleName`
- `label`
- `ui.shortLabel`
- `ui.nodeNameStem`
- `engine.processShape`
- `engine.domain`
- `engine.materialization`

Required transport behavior:

- `xyona::OpDesc` contains first-class UI naming fields or a typed nested
  metadata object.
- Pack ABI descriptors are generated from `op.yaml`; until first-class ABI
  fields exist, pack `meta_json` must carry the same stable `provider`,
  `providerLabel`, `family`, `moduleName`, `ui`, and `engine` fields.
- Pack descriptors missing these required fields are invalid.
- Lab reads these fields from Core's public discovery surface after pack loading.
  Lab must not parse pack-private source folders to recover naming metadata.
- `NodeBinder` and any other default node creation path use `ui.nodeNameStem`
  for new node instance names while preserving the immutable `id` in node
  metadata/project state.
- Existing persisted node names are user data and are not rewritten by schema
  migration.

Badge derivation is also public metadata:

- Execution badges are derived from `capabilities.canRealtime`,
  `capabilities.canHQ`, and whole-file/materialization flags.
- Domain badges are derived from `engine.domain`.
- Materialization badges such as `WF`, `MAT`, `LC`, and `ANL` are derived from
  `engine.wholeFileRequired`, `engine.materialization`, `engine.lengthChanging`,
  and analysis/data output state.
- Hosts may style badges differently per provider, but the meaning must not be
  provider-specific.

## Help ID Rules

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
```

The HelpCenter must treat Core, pack, and Lab-authored public operators
identically after discovery.

## Help File Front Matter

All operator help files must start with YAML front matter:

```yaml
---
id: help.node.<operator_id>
title: <Display Name>
tags: [node, <provider-or-domain>, <feature>]
related: []
---
```

Rules:

- `id` must match `op.yaml:help.id`.
- `title` should use the natural user-facing operator name. Standalone help
  articles may include provider or family context when needed for
  disambiguation, but descriptor `label` should not be provider-prefixed only
  because the operator came from a pack.
- `tags` must include `node`.
- Pack docs must include the provider tag, for example `cdp`.
- CDP-derived docs should include family/process tags such as `modify`,
  `loudness`, or `space`.
- `related` may be empty but must be present in release-ready docs.

## Help File Content Order

Use the same structure across all operators:

```text
# Title

Brief behavior description.

## Parameters

## Usage

## Processing Modes

## Requirements

## Provenance

## Tips

## See Also
```

`## Provenance` is required for CDP-derived operators. For non-CDP operators it
may be omitted.

`## Parameters` must state "No user parameters" for parameterless operators.

`## Processing Modes` must match `op.yaml:capabilities`.

`## Requirements` must document channel count, whole-file requirements, and any
host contract that matters to the user.

## CDP Documentation Policy

CDP8 documentation and CDP8 CLI usage text are reference material, not direct
HelpCenter content.

Use CDP docs to extract:

- original command name
- original mode number/name
- parameter meaning and ranges
- file shape requirements
- behavior notes and edge cases

Then rewrite the help into XYONA structure:

- Lab/node language instead of CLI-only language
- RT/HQ behavior stated explicitly
- parameter names matching XYONA descriptors
- channel and whole-file requirements stated as host requirements
- CDP provenance preserved in `## Provenance`

Do not paste large CDP manual sections directly into XYONA help. The help files
must be authored as XYONA operator documentation.

## Generated Artifacts

From `op.yaml`, generation or validation should cover:

- runtime descriptor helpers
- generated JSON metadata
- public provider/family/UI naming metadata
- pack ABI descriptor arrays
- registration lists
- help metadata
- docs install manifests
- CMake source lists
- descriptor smoke tests

Hand-written descriptor data is allowed only during migration and must be
validated against `op.yaml`.

## Validation Requirements

A repository-level validator should fail if:

- a public operator lacks `op.yaml`
- `docs/en.md` is missing
- release mode lacks `docs/de.md`
- help front matter ID does not match `op.yaml:help.id`
- a parameter in `op.yaml` is missing from help
- RT/HQ capability docs disagree with metadata
- `provider`, `family`, or `moduleName` is missing
- `family` repeats the provider namespace, for example `cdp.modify`
- a pack or Lab operator ID does not start with `<provider>.`
- `engine.domain` or `engine.materialization` is missing
- a CDP operator lacks provenance
- `label` mechanically repeats provider/family context without an explicit
  exception, for example `CDP Modify Loudness Gain` when provider and category
  already expose `CDP/Modify`
- `ui.nodeNameStem` is missing, contains dots, duplicates another public
  operator without an explicit exception, or is derived from the full namespaced
  ID
- public descriptor/discovery metadata does not expose `ui.nodeNameStem`
- Lab default node creation derives a new node name from a dotted operator ID
  when a node-name stem is available
- Lab mutates descriptor labels to add provider prefixes such as `CDP: `
- a whole-file or length-changing operator claims realtime without an explicit
  realtime contract
- a prototype whole-buffer adapter is used for length-changing, PVOC/spectral,
  multi-output, multi-file, long-running, or large-source production work
- a production offline operator lacks a declared Offline Session ABI contract
  once that ABI is available
- generated JSON is stale or missing
- registration omits an implemented operator

## Lab Consumption Contract

Lab owns HelpCenter UI and Lab-only docs. Lab does not own operator help for
Core or packs.

Lab-authored public operators are still operators under this contract. This
includes host endpoints and host/runtime helpers such as Audio In, Audio Out,
MainBus, Grid Signal, Grid Value, Grid Action Filter, Layer Player, and future
Lab-only adapters.

Lab-authored operator requirements:

- `provider: lab`
- `providerLabel: Lab`
- `ownership.repository: xyona-lab`
- `ownership.algorithmOwner: lab` for host/runtime behavior
- `ownership.hostBoundary: host_owned` or another explicit host-owned value
- `id` starts with `lab.`
- `family` is provider-local, for example `system.audio`, `system.bus`, or
  `timeline.grid`
- `ui.nodeNameStem` is present and does not contain the `lab` provider segment

Examples:

| Operator ID | Family | Label | Node Name Stem | Typical Capability |
|---|---|---|---|---|
| `lab.audio_in` | `system.audio` | `Audio Input` | `audio_in` | `RT-only` |
| `lab.audio_out` | `system.audio` | `Audio Output` | `audio_out` | `RT-only` |
| `lab.mainbus_out` | `system.bus` | `Main Bus Out` | `mainbus_out` | `RT-only` |
| `lab.timeline.grid_source` | `timeline.grid` | `Grid Signal` | `grid` | `RT+HQ` |

Lab help namespaces:

```text
help.node.*      Core, pack, and Lab-authored public operators
help.panel.*     Lab panels/windows
help.topic.*     Lab concepts and technical topics
help.workflow.*  Lab workflows/how-tos
```

Lab-only source files:

```text
docs/help/lab/<locale>/nodes/
docs/help/lab/<locale>/panels/
docs/help/lab/<locale>/topics/
docs/help/lab/<locale>/workflows/
```

Pack/Core operator source files:

```text
src/operators/<family>/<module>/docs/<locale>.md
```

Until Core modules are migrated, Core may still expose old source files under:

```text
src/processes/<family>/<module>/docs/<locale>.md
```

This is a temporary implementation detail. Lab should consume operator help
through Core's public discovery/help surface whenever possible, not by
hardcoding private pack source paths.

## References

- `ROADMAP_OPERATOR_MODULE_STRUCTURE.md` - migration plan and rationale.
- `xyona-core/src/processes/HELP_STANDARDS.md` - Core compatibility standard.
- `xyona-cdp-pack/docs/HELP_STANDARDS.md` - CDP pack authoring standard.
- `xyona-lab/docs/help/lab/README.md` - Lab-only help layout.
