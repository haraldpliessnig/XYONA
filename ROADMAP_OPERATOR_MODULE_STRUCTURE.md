# Roadmap: Unified Operator Module Structure

**Status:** Draft architecture and migration roadmap  
**Date:** 2026-04-27  
**Scope:** `xyona-core`, `xyona-cdp-pack`, `xyona-lab`, `CDP8` reference workflow  
**Owner:** Workspace-level architecture; implementation remains repo-local

**Normative contract:** `OPERATOR_MODULE_CONTRACT.md`. This roadmap explains
why the contract exists and how to migrate current repositories toward it.

## Purpose

This document defines how XYONA should store and author DSP, processes, and
operators across Core and runtime packs with one consistent module system.

The immediate reason for this roadmap is a structural mismatch:

- `xyona-core` has process folders, `meta.yaml`, generated JSON, C++ runtime
  descriptors, help files, and manual registration.
- `xyona-cdp-pack` has an excellent planning inventory, but implemented
  operators are flat C++ files with descriptor structs and JSON string literals
  embedded in code.
- `xyona-lab` consumes descriptors and help, but does not own DSP algorithms.
- `CDP8` is old C code, but its process/family/mode organization is very
  explicit and therefore easier to reason about than the current mixed XYONA
  structure.

The goal is not to copy CDP8's C architecture. The goal is to keep CDP8's
clarity: a predictable place for process identity, process family, modes,
parameters, documentation, implementation, tests, and registration.

## Executive Summary

XYONA needs one canonical **Operator Module Contract**. Every operator,
regardless of whether it ships in `xyona-core` or a dynamic pack such as
`xyona-cdp-pack`, should be represented by one self-contained module:

```text
src/operators/<family>/<operator_id>/
  op.yaml
  README.md
  docs/en.md
  docs/de.md
  dsp/
  adapter/
  tests/
  golden/
```

`op.yaml` should become the source of truth for identity, ports, parameters,
capabilities, engine shape, help metadata, provenance, and pack/core adapter
requirements. C++ descriptor code, generated JSON, registration lists, help
indexes, and pack ABI descriptor structs should be generated or validated from
that file.

The current system is close in concept but not strict enough. The same operator
facts are duplicated across YAML, generated JSON, C++ descriptors, CMake,
manual registration, help files, Lab indexes, and pack JSON string literals.
That duplication has already produced drift.

## Repository Responsibilities

This roadmap follows the workspace ownership rules.

`xyona-core` owns:

- host-agnostic operator contracts and descriptor types
- `xyona::Operator` and processing contexts
- generic metadata schema and code generation
- generic pack ABI and pack loading
- pure DSP families that are not CDP-pack-specific
- core operator help API and generated/help metadata surfaces

`xyona-cdp-pack` owns:

- CDP algorithm rewrites
- CDP program and mode semantics
- CDP provenance and validation metadata
- pack-local adapters to Core's pack ABI
- CDP golden references and CDP-specific helper layers

`xyona-lab` owns:

- graph topology, nodes, Canvas UI, project state, render jobs, device routing
- HelpCenter UI and Lab-only documentation
- consumption of Core and pack descriptors
- operator discovery caches and host-side rendering workflow

`CDP8` remains:

- reference-only source code
- source for original program/mode behavior, CLI usage, and validation
- not a place for XYONA implementation changes unless explicitly requested

## Current Structure Analysis

### Core: Current Operator Storage

Current `xyona-core` operators live below `src/processes`, grouped by family:

```text
xyona-core/src/processes/
  dynamics/gain/
  dynamics/hq_gain/
  generators/test_tone/
  signal/
  sources/audio_clip/
  spatial/stereo_width/
  utility/slot_gain/
```

A mostly canonical operator folder contains:

```text
meta.yaml
<operator>.cpp
CMakeLists.txt
README.md
docs/en.md
docs/de.md
```

Examples:

- `xyona-core/src/processes/dynamics/gain/`
- `xyona-core/src/processes/spatial/stereo_width/`
- `xyona-core/src/processes/utility/slot_gain/`

Runtime registration is not driven by `meta.yaml`. Runtime descriptors are built
inside each C++ operator class through `buildDescriptor(OpDesc&)`, and operators
are registered with `detail::registerOperator(...)`. The central registry stores
`OpDesc` plus a factory in a process registry map.

This means Core has multiple data surfaces:

| Surface | Current role | Problem |
|---|---|---|
| `meta.yaml` | codegen input for JSON and generated parameter headers | not runtime source of truth |
| C++ `buildDescriptor()` | runtime descriptor source | duplicates YAML |
| `gen/json/*.json` | Lab/help metadata and generated discovery surface | can go stale |
| `include/xyona/processes.hpp` | manual registration list | can drift |
| `src/processes/CMakeLists.txt` | manual object library aggregation | can drift |
| `docs/*.md` | help source | only partly installed by Core CMake |

Concrete drift observed on 2026-04-27:

- Core has 16 `meta.yaml` files and 16 help file pairs.
- `gen/json/slot_gain.json` is missing.
- `gen/json/lane_gain.json` exists but no matching current `meta.yaml` exists.
- Core install rules only install help for `gain`, `hq_gain`, `stereo_width`,
  and `audio_clip`, not all current operators.
- `src/processes/PROCESS_TEMPLATE.md` still contains older names such as
  `Processor`, `ProcDesc`, and `registerProcess`, while actual operators now use
  `Operator`, `OpDesc`, and `registerOperator`.
- Signal operators are metadata-separated (`signal_lfo`, `signal_noise`, etc.)
  but implementation-grouped in two C++ files (`signal_generators.cpp`,
  `signal_processors.cpp`). That is acceptable as an implementation detail, but
  it makes module ownership less obvious.

### Core: Current Documentation

Core already has meaningful documentation:

- `xyona-core/src/processes/PROCESS_TEMPLATE.md`
- `xyona-core/src/processes/HELP_STANDARDS.md`
- `xyona-core/src/processes/HELP_TEMPLATE.md`
- `xyona-core/docs/METADATA_SPECIFICATION.md`
- `xyona-core/docs/OPERATOR_PACKS.md`
- `xyona-core/docs/OPERATOR_PACKS_ABI_V2.md`

The weakness is not absence of documentation. The weakness is enforcement and
unification. Core has the right ideas, but several documents describe different
generations of the system.

### CDP Pack: Current Operator Storage

`xyona-cdp-pack` currently stores implemented operators flat:

```text
xyona-cdp-pack/src/operators/
  cdp_modify_loudness_gain.cpp
  cdp_modify_loudness_gain.h
  cdp_modify_loudness_dbgain.cpp
  cdp_modify_loudness_dbgain.h
  cdp_modify_loudness_normalise.cpp
  cdp_modify_loudness_normalise.h
  cdp_modify_loudness_phase_invert.cpp
  cdp_modify_loudness_phase_invert.h
  cdp_modify_space_mirror.cpp
  cdp_modify_space_mirror.h
  cdp_modify_space_narrow.cpp
  cdp_modify_space_narrow.h
  cdp_utility_db_gain.cpp
  cdp_utility_db_gain.h
  cdp_utility_identity.cpp
  cdp_utility_identity.h
```

Each `.cpp` typically contains:

- C ABI lifecycle callbacks
- DSP process code or direct sample loop
- parameter parsing
- static `xyona_pack_v2_param_desc`
- static `xyona_pack_v2_port_desc`
- static `xyona_pack_v2_op_desc`
- static `xyona_pack_v2_operator_vtable`
- `register...V2(host)` function
- JSON metadata string literals for CDP provenance and engine contract

Pack registration is manual:

- CMake manually lists every operator `.cpp`.
- `src/pack_registration.cpp` includes every operator header.
- `registerAllOperatorsV2()` calls every operator registration function.
- `src/offline_api.cpp` manually dispatches whole-file/offline-capable
  operators such as `cdp.modify.loudness_normalise`.

The pack has a strong planning source:

- `xyona-cdp-pack/specs/cdp8_inventory.yaml`
- `xyona-cdp-pack/specs/cdp8_target_index.yaml`

`specs/README.md` explicitly says the inventory is the source of planning truth.
That is good. The problem is that implementation code is not generated or
validated from that inventory, and there is no equivalent to Core's per-operator
metadata and help structure.

### CDP Pack: Current Documentation State

`xyona-cdp-pack` has:

- good README-level build and boundary rules
- good inventory rules
- good test coverage for current operators
- good engine-shape language
- pack-level help standards in `xyona-cdp-pack/docs/HELP_STANDARDS.md`
- per-operator HelpCenter files for the currently implemented public operators
  under `xyona-cdp-pack/src/operators/<cdp.family>/<operator>/docs/`

It still does not currently have:

- per-operator `op.yaml`
- a pack operator template
- generated descriptor code
- generated registration
- generated Lab help metadata
- a full implementation-folder migration from flat `.cpp` files to complete
  operator module roots

### Lab: Current Consumption Model

Lab's HelpCenter uses a hybrid model:

- Core operators: `help.node.*` via Core Host API
- Lab docs: filesystem under `docs/help/lab/<locale>/...`
- Lab build: `sync_docs` copies `docs/help` and Core `src/processes` into
  `build/docs`
- Lab build: `tools/i18n/build_docs_index.py` creates `build/docs/index/*.json`

This is architecturally reasonable. Lab should not own DSP or CDP algorithms.
Lab's help documentation previously had drift: README documented `panels/`,
some files lived under a generic UI folder, and older docs used a concept
namespace. The current rule is `nodes/`, `panels/`, `topics/`, and `workflows/`
with the namespaces defined in `OPERATOR_MODULE_CONTRACT.md`.

This confirms the need for a single shared help namespace and file layout
contract.

### CDP8: Why It Feels Cleaner

CDP8 is old C code, but it has a very consistent mental model:

- process families are directories under `CDP8/dev/`
- build includes each family explicitly
- process numbers are central in `dev/include/processno.h`
- mode numbers are central in `dev/include/modeno.h`
- each CLI family maps command names to process IDs and modes
- usage text lives close to the command parser
- process logic defines file shape requirements in a central switch

For example, `modify` owns `loudness`, `space`, `speed`, `revecho`, etc. The
command parser maps names to process numbers, mode logic maps mode numbers to
file/shape requirements, and processing dispatch routes to the implementation.

This is not a modern architecture, but it has a strong property XYONA should
copy: **there is always an obvious place to find the source of truth**.

## Root Cause

The structural problem is not a missing class or missing folder. The root cause
is that "operator identity" is not represented by one canonical artifact.

Today an operator's identity is spread across:

- file path
- CMake target list
- registration function name
- runtime `OpDesc`
- `meta.yaml`
- generated JSON
- help front matter
- help file path
- pack ABI descriptor
- pack metadata JSON string literal
- CDP inventory entry
- Lab help index
- tests that look up hardcoded operator IDs

As long as all of those are hand-maintained, the project will remain vulnerable
to drift.

## Target Architecture

### Operator Module Contract

Every operator module should be self-contained and follow one shape:

```text
src/operators/<family>/<operator_id>/
  op.yaml
  README.md
  docs/
    en.md
    de.md
  dsp/
    <operator_id>_dsp.hpp
    <operator_id>_dsp.cpp
  adapter/
    core_operator.cpp
    pack_v2_operator.cpp
    offline_whole_buffer_prototype.cpp
    offline_session.cpp
  tests/
    test_<operator_id>.cpp
  golden/
    manifest.yaml
```

Not every file is required for every operator:

- Core-native operator: `adapter/core_operator.cpp` required.
- Pack operator: `adapter/pack_v2_operator.cpp` required.
- Bounded same-length reference whole-file pack operator:
  `adapter/offline_whole_buffer_prototype.cpp` allowed while the production
  session contract is being built.
- Production offline pack operator: `adapter/offline_session.cpp` required once
  the Offline Session ABI exists.
- Length-changing, PVOC/spectral, multi-output, multi-file, long-running, and
  large-source CDP operators must not target the prototype adapter.
- Header-only tiny DSP: `dsp/*.cpp` optional.
- Operators with no golden audio may omit `golden/`, but must explain their
  validation strategy in `op.yaml`.

### Canonical Naming

Use the public operator ID as the canonical module identity.

Examples:

```text
gain
hq_gain
slot_gain
signal_lfo
cdp.modify.loudness_gain
cdp.modify.loudness_normalise
cdp.modify.space_mirror
```

Filesystem options:

```text
src/operators/dynamics/gain/
src/operators/cdp/modify/loudness_gain/
```

The preferred filesystem path should avoid extremely long single directory names
while preserving the exact public ID in `op.yaml`:

```yaml
id: cdp.modify.loudness_gain
family: cdp.modify
moduleName: loudness_gain
```

The path is organizational. `op.yaml:id` is authoritative.

### UI And Canvas Instance Naming

Canonical IDs must not be reused as default Canvas instance names.

Current Lab behavior generates TouchDesigner-style node names from the operator
ID. That works for short Core IDs such as `gain`, because the visible instance
becomes `gain1`. It breaks for namespaced pack IDs such as
`cdp.modify.loudness_gain`, because the UI leaks the internal namespace into
the node header.

This is a structure issue, not a reason to shorten pack IDs. Pack IDs need the
provider namespace for persistence, discovery, help IDs, and collision
avoidance. The missing layer is a separate short node-name stem.

The target contract is:

```yaml
id: cdp.modify.loudness_gain       # stable machine ID
label: Modify Loudness Gain        # browser/help label
category: CDP/Modify               # grouping context

ui:
  shortLabel: Loudness Gain
  nodeNameStem: loud_gain           # Canvas instance prefix
```

Default instances should be:

```text
gain1
loud_gain1
mirror1
density1
```

not:

```text
cdp.modify.loudness_gain1
cdp.modify.cdp.loudness.density1
```

Migration rule:

1. Add `ui.nodeNameStem` to `op.yaml`.
2. Generate or validate descriptor/UI metadata from it.
3. Lab should generate new node instance names from `nodeNameStem`.
4. Existing persisted node names remain user data and must not be rewritten
   automatically.
5. Menus and search can show provider/family context, but Canvas node headers
   should stay short.

### Required `op.yaml`

`op.yaml` should become the canonical operator contract.

Minimum schema:

```yaml
schema: xyona-operator-v1

id: cdp.modify.loudness_gain
provider: cdp
family: cdp.modify
moduleName: loudness_gain
label: CDP Modify Loudness Gain
summary: Adjusts loudness by a linear CDP gain factor.
description: |
  CDP8 rewrite of modify loudness mode 1. Applies a fixed linear gain
  factor to all audio samples.
operatorType: processor
category: CDP/Modify
icon: volume-2
version: 0.1.0

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
  outputLength: same_as_input
  wholeFileRequired: false
  lengthChanging: false
  audioOutput: true
  multiOutput: false
  abiV2Support: direct

ports:
  inputs:
    - id: in
      label: Input
      kind: audio
      minChannels: 1
      maxChannels: 16
      defaultChannels: 2
  outputs:
    - id: out
      label: Output
      kind: audio
      minChannels: 1
      maxChannels: 16
      defaultChannels: 2

params:
  - id: gain
    label: Gain
    type: float
    min: 0.000002
    max: 32767.0
    default: 1.0
    unit: x
    description: Linear gain factor for CDP modify loudness mode 1.
    group: Gain
    display: slider
    precision: 3
    availableIn: [realtime, hq]
    scopeSupport: [global]
    ui:
      step: 0.01
      scale: linear

help:
  id: help.node.cdp.modify.loudness_gain
  locales: [en, de]
  tags: [node, cdp, modify, loudness, gain]

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

validation:
  strategy: analytic_golden_buffer
  tests:
    - descriptor_matches_cdp_mode
    - parameter_range_validation
    - renders_expected_gain
```

Core-native example:

```yaml
schema: xyona-operator-v1

id: gain
provider: core
family: dynamics
moduleName: gain
label: Gain
summary: Simple gain/amplification.
operatorType: processor
category: Amplitude
icon: volume_up
version: 1.0.0

ownership:
  repository: xyona-core
  license: MIT
  algorithmOwner: core
  hostBoundary: no_lab_dependencies

capabilities:
  canRealtime: true
  canHQ: false

engine:
  processShape: block_length_preserving
  outputLength: same_as_input
  wholeFileRequired: false
  lengthChanging: false
  audioOutput: true
  multiOutput: false

ports:
  inputs:
    - id: in
      label: Input
      kind: audio
      minChannels: 1
      maxChannels: 16
      defaultChannels: 2
  outputs:
    - id: out
      label: Output
      kind: audio
      minChannels: 1
      maxChannels: 16
      defaultChannels: 2

params:
  - id: factor
    label: Gain Factor
    type: float
    min: 0.0
    max: 10.0
    default: 1.0
    unit: x
    description: Gain factor. 1.0 is unity gain.
    group: Basic
    display: slider
    precision: 2
    availableIn: [realtime]

help:
  id: help.node.gain
  locales: [en, de]
  tags: [node, level, amplitude]

validation:
  strategy: deterministic_unit_test
```

### Source of Truth Rules

`op.yaml` must own:

- public operator ID
- provider namespace
- label, summary, description, category, icon, version
- operator type
- RT/HQ capabilities
- processing/engine shape
- input/output ports
- parameter descriptors
- parameter availability and scope
- help ID, locales, tags
- provenance
- validation strategy
- host-boundary requirements

C++ adapter code must own:

- runtime state
- prepare/reset/process implementation
- conversion from host buffers to DSP views
- algorithm invocation
- error handling at the ABI or `Operator` boundary

DSP code must own:

- math
- deterministic state machines
- sample/block/whole-file processing
- CDP algorithm behavior when in pack

Tests must own:

- behavioral verification
- descriptor verification where generator output is expected
- golden comparison or analytic expected output

CMake must not own:

- operator identity
- parameter facts
- help facts
- provenance facts

CMake should only include generated target/source lists or call helper functions
that consume module manifests.

## Generated Artifacts

From each `op.yaml`, generate or validate:

```text
gen/operators/<safe_id>/descriptor.hpp
gen/operators/<safe_id>/params.hpp
gen/operators/<safe_id>/pack_v2_descriptor.inc
gen/json/<id>.json
gen/registration/register_core_operators.cpp
gen/registration/register_pack_operators.cpp
build/help_html/...
build/docs/index/*.json
```

Core-specific generated output:

- `OpDesc` construction helper
- parameter descriptor helper
- registration table for `registerAllProcesses()`
- JSON metadata for Lab/help
- recursive install manifest for docs and metadata

Pack-specific generated output:

- `xyona_pack_v2_op_desc`
- `xyona_pack_v2_param_desc[]`
- `xyona_pack_v2_port_desc[]`
- metadata JSON blobs without hand-written raw string duplication
- registration list for `registerAllOperatorsV2()`
- optional prototype whole-buffer dispatch table for bounded same-length
  reference
  operators
- offline-session dispatch/registration for production offline operators

Lab-specific generated/consumed output:

- help index
- operator library cache
- search tags
- category/group metadata

Lab should consume the same public surfaces, not parse pack-private files.

## Documentation Contract

Every operator with a public node should have:

```text
docs/en.md
docs/de.md
```

`en.md` is required. `de.md` is strongly recommended and should be treated as
required for release builds once the authoring flow is stable.

Front matter:

```yaml
---
id: help.node.<operator_id>
title: <Display Name>
tags: [node, <category>, <feature>]
related: []
---
```

For pack operators with dots:

```yaml
---
id: help.node.cdp.modify.loudness_gain
title: CDP Modify Loudness Gain
tags: [node, cdp, modify, loudness]
related: []
---
```

Required content sections:

1. title
2. brief behavior description
3. parameters
4. usage
5. processing modes
6. requirements
7. CDP provenance, if CDP-derived
8. validation notes, if useful
9. see also

The existing Core `HELP_STANDARDS.md` is a good base, but it must be updated to
cover pack operators and dotted operator IDs.

## Help ID and File Path Rules

The help ID should be derived from `op.yaml:id`:

```text
help.node.<operator_id>
```

Examples:

```text
help.node.gain
help.node.slot_gain
help.node.cdp.modify.loudness_gain
```

File paths should not be guessed from help ID alone. The generated metadata
should include the actual relative help file path:

```json
{
  "help": {
    "en": {
      "id": "help.node.cdp.modify.loudness_gain",
      "path": "operators/cdp/modify/loudness_gain/docs/en.md",
      "title": "CDP Modify Loudness Gain",
      "tags": ["node", "cdp", "modify", "loudness"]
    }
  }
}
```

This avoids fragile path logic when operator IDs contain dots.

## Proposed Physical Layouts

### Core Target Layout

```text
xyona-core/
  src/operators/
    dynamics/
      gain/
        op.yaml
        README.md
        docs/en.md
        docs/de.md
        dsp/gain_dsp.hpp
        adapter/core_operator.cpp
        tests/test_gain.cpp
    spatial/
      stereo_width/
        op.yaml
        docs/en.md
        docs/de.md
        dsp/stereo_width_dsp.hpp
        adapter/core_operator.cpp
    signal/
      lfo/
      noise/
      dust/
```

Existing `src/processes` can remain during migration. New code should prefer
`src/operators`. If immediate folder movement is too disruptive, Core can first
adopt the module contract inside `src/processes/<family>/<operator>/` and later
rename the root folder.

### CDP Pack Target Layout

```text
xyona-cdp-pack/
  src/operators/
    utility/
      identity/
        op.yaml
        README.md
        docs/en.md
        docs/de.md
        dsp/identity_dsp.hpp
        adapter/pack_v2_operator.cpp
        tests/test_identity.cpp
      db_gain/
        op.yaml
        docs/en.md
        docs/de.md
        dsp/db_gain_dsp.hpp
        adapter/pack_v2_operator.cpp
    modify/
      loudness_gain/
        op.yaml
        docs/en.md
        docs/de.md
        dsp/loudness_gain_dsp.hpp
        adapter/pack_v2_operator.cpp
        tests/test_loudness_gain.cpp
      loudness_normalise/
        op.yaml
        docs/en.md
        docs/de.md
        dsp/loudness_normalise_dsp.hpp
        adapter/pack_v2_operator.cpp
        adapter/offline_whole_buffer_prototype.cpp
        tests/test_loudness_normalise.cpp
      space_mirror/
      space_narrow/
```

`adapter/offline_whole_buffer_prototype.cpp` in this layout is a
prototype/reference path for bounded same-length whole-buffer operators.
Production offline operators should use a session/streaming adapter such as
`adapter/offline_session.cpp` once the Offline Session ABI is implemented.
Before release, public operators still using the prototype path should be ported
to the session adapter, or the prototype surface should be explicitly
internal-only.

### Shared Generated Layout

```text
gen/
  json/
  include/xyona/gen/
  operators/
    gain/
    cdp_modify_loudness_gain/
  registration/
```

Generated files should be either fully build-tree artifacts or intentionally
checked in. Mixing generated source-tree files and stale manual updates is the
current failure mode. Prefer build-tree generation for new artifacts unless
there is a strong packaging reason to check them in.

## Adapter Boundaries

### DSP Layer

The DSP layer must be independent of:

- JUCE
- Lab
- Canvas
- project files
- device routing
- parameter UI
- render jobs
- pack ABI structs

It should expose small C++ functions/classes with explicit inputs:

```cpp
struct LoudnessGainParams {
    float gain = 1.0f;
};

void processLoudnessGain(CdpAudioView input,
                         CdpMutableAudioView output,
                         const LoudnessGainParams& params) noexcept;
```

### Core Adapter

Core adapter responsibilities:

- subclass `xyona::Operator`
- register parameters
- implement `inputPorts()` and `outputPorts()`
- implement `prepare`, `reset`, `processRT`, `processHQ`
- call DSP layer
- build descriptor using generated helper

The adapter should not duplicate parameter ranges already in `op.yaml`.

### Pack ABI Adapter

Pack adapter responsibilities:

- expose C ABI v2 lifecycle callbacks
- convert C ABI process context to pack-local views
- parse incoming `xyona_pack_v2_param_value`
- call DSP layer
- return pack ABI error codes
- use generated descriptor arrays

The adapter should not hand-write large descriptor structs when those can be
generated from `op.yaml`.

### Offline Adapter

Offline pack operators need an offline adapter. The adapter class depends on
the operator contract:

- `adapter/offline_whole_buffer_prototype.cpp` is allowed only for bounded
  same-length, whole-buffer prototype/reference operators.
- `adapter/offline_session.cpp` is the intended production path for
  length-changing, PVOC/spectral, multi-output, multi-file, long-running, or
  large-source work once the Offline Session ABI exists.

Offline adapters must:

- query output shape
- validate full-file input
- process whole-file input to materialized output
- keep realtime path disabled unless a specific RT contract exists
- report progress and observe cancellation when using the session/streaming
  Offline Session ABI contract

This should be generated/registered from `engine.wholeFileRequired` and
`engine.abiV2Support`.

## What Should Be Generated vs Hand-Written

Generated:

- descriptor identity fields
- port descriptors
- parameter descriptors
- C ABI descriptor arrays
- help metadata JSON
- registration tables
- CMake operator source lists
- docs install manifests
- basic descriptor tests

Hand-written:

- DSP logic
- adapter state and processing callbacks
- special validation behavior
- golden expected values
- user-facing prose docs

Generated but reviewable:

- `register_all` source
- `operator_manifest.json`
- docs index

## Validation Rules

Add a validator that can run in each repo:

```sh
python tools/operator_modules/validate_operator_modules.py --root .
```

It should enforce:

- every module has `op.yaml`
- `op.yaml:schema` is known
- `id` is unique
- pack IDs start with provider namespace, e.g. `cdp.`
- help front matter ID matches `help.node.<id>`
- `docs/en.md` exists
- every param in `op.yaml` is documented in `docs/en.md`
- `capabilities` match engine shape
- whole-file and length-changing operators are not realtime unless explicitly
  allowed by a named contract
- the prototype whole-buffer adapter is not used for length-changing,
  PVOC/spectral, multi-output, multi-file, long-running, or large-source
  production work
- production offline operators declare the Offline Session ABI contract once
  that ABI exists
- CDP operators include `provenance.cdp.sourceFile`
- CMake/generated registration contains all implemented operators
- stale generated JSON is detected
- generated descriptor matches checked-in descriptor code where generation is
  not yet fully adopted

CI should fail on validation errors.

## Migration Roadmap

### Phase 0: Freeze the Contract

Create a small shared spec before moving files:

- `docs/OPERATOR_MODULE_CONTRACT.md` in root or Core
- `tools/operator_modules/validate_operator_modules.py`
- `tools/operator_modules/schema/xyona-operator-v1.schema.json`
- update Core `PROCESS_TEMPLATE.md` to current `Operator` API
- add Pack `OPERATOR_TEMPLATE.md`

Exit criteria:

- The schema can describe all current Core operators.
- The schema can describe all current CDP pack operators.
- The validator can report current drift without requiring immediate migration.

### Phase 1: Fix Current Drift Without Moving Code

Core:

- regenerate `gen/json` and remove stale `lane_gain`
- ensure `slot_gain` generates JSON
- make codegen part of normal build or a required pre-build target
- make docs install recursive for all operator docs
- update `PROCESS_TEMPLATE.md` to current W6 `Operator` API
- add a test that checks `meta.yaml` IDs against `gen/json`

Pack:

- add `op.yaml` next to each current flat `.cpp` or in temporary
  `specs/operators/<id>.yaml`
- validate descriptor JSON string literals against `op.yaml`
- add generated help metadata for Lab consumption
- keep newly added per-operator help docs in sync with descriptor metadata

Lab:

- keep Lab help folders normalized (`nodes`, `panels`, `topics`, `workflows`)
- keep help docs on one namespace policy: `help.topic.*`, `help.panel.*`,
  `help.workflow.*`, `help.node.*`

Exit criteria:

- No stale generated operator metadata.
- All current public operators have help metadata.
- Pack implemented operators are represented by machine-readable operator specs.

### Phase 2: Generate Descriptors

Core:

- generate descriptor helper from `op.yaml`
- operators call generated descriptor helper from `buildDescriptor()`
- handwritten descriptor facts are removed from operator code where possible

Pack:

- generate `xyona_pack_v2_op_desc`, param arrays, port arrays, and metadata JSON
- pack adapters keep lifecycle/process code only
- generate `registerAllOperatorsV2()`

Exit criteria:

- Adding a new parameter requires editing one YAML field and DSP/adapter code,
  not four descriptor surfaces.
- Descriptor tests compare generated descriptor output to runtime discovery.

### Phase 3: Move Pack Operators Into Modules

Move:

```text
src/operators/cdp_modify_loudness_gain.cpp
```

to:

```text
src/operators/modify/loudness_gain/
  op.yaml
  docs/
  dsp/
  adapter/
  tests/
```

Do this family by family:

1. `utility`
2. `modify/loudness`
3. `modify/space`
4. next CDP8 priority groups

Exit criteria:

- Flat `src/operators/*.cpp` no longer contains public operator modules.
- `src/operators/<family>/<operator>/` is the normal authoring path.

### Phase 4: Migrate Core to Same Module Shape

Options:

1. Low-risk: keep `src/processes/<family>/<operator>` but require the same
   internal module shape.
2. Full alignment: rename `src/processes` to `src/operators`.

Recommended path:

- first enforce the module contract inside `src/processes`
- then migrate to `src/operators` when generated registration and generated
  CMake source lists are stable

Exit criteria:

- Core and Pack use the same `op.yaml` schema.
- Core and Pack use the same help/docs rules.
- Core and Pack use generated/validated registration.

### Phase 5: Lab Integration

Lab should consume:

- Core operators via Core API
- Pack operators via Core API after pack loading
- operator metadata JSON/help metadata from Core's discovery surface
- Lab-only docs from `docs/help/lab`

Lab should not parse pack-private implementation folders.

Needed Core/Pack API work:

- expose help metadata for pack operators through pack metadata registration
- allow pack help paths to be loaded by Core or handed to Lab through a stable
  metadata surface
- define installed pack help location:

```text
<bundle>/operator_packs/
<bundle>/operator_pack_docs/<pack_id>/...
```

or:

```text
<share>/xyona-core/packs/<pack_id>/help/...
```

Exit criteria:

- `help.node.cdp.modify.loudness_gain` opens in Lab HelpCenter.
- pack docs are searchable by tags.
- locale fallback works for pack docs.

### Phase 6: CI Enforcement

Each repo should run:

- operator module validation
- descriptor generation check
- stale generated file check
- markdown/front-matter validation
- CTest
- pack load smoke test where applicable

Exit criteria:

- A PR adding an operator cannot pass if docs, metadata, registration, or tests
  are incomplete.

## Recommended Add-Operator Workflow

For a Core operator:

1. Create `src/operators/<family>/<operator>/op.yaml`.
2. Add `docs/en.md` and `docs/de.md`.
3. Implement DSP in `dsp/`.
4. Implement `adapter/core_operator.cpp`.
5. Add tests.
6. Run operator validator.
7. Run codegen.
8. Run CTest.

For a CDP pack operator:

1. Update `specs/cdp8_inventory.yaml`.
2. Create `src/operators/<family>/<operator>/op.yaml`.
3. Include CDP provenance and engine shape.
4. Add docs with CDP provenance section.
5. Implement pack-local DSP.
6. Implement `adapter/pack_v2_operator.cpp`.
7. Add `adapter/offline_whole_buffer_prototype.cpp` only for bounded
   same-length prototype/reference whole-file work; add
   `adapter/offline_session.cpp` for production offline/session work once the
   Offline Session ABI exists.
8. Add analytic or golden tests.
9. Run validator.
10. Run pack build and CTest.

## Immediate High-Value Fixes

These should happen before large code movement:

1. Update `xyona-core/src/processes/PROCESS_TEMPLATE.md` to current API.
2. Add a root `OPERATOR_MODULE_CONTRACT.md` or promote this roadmap into that
   contract once decisions are accepted.
3. Add a validator that reports:
   - missing generated JSON
   - stale generated JSON
   - missing docs install rules
   - mismatch between `meta.yaml` and help front matter
4. Make Core CMake install docs recursively instead of listing four operators.
5. Add `op.yaml` for current CDP pack operators without moving code.
6. Replace pack descriptor raw JSON strings with generated metadata once the
   schema is accepted.

## Design Decisions

### Decision: `op.yaml` Instead of C++ Descriptor as Source of Truth

Reason:

- descriptors feed UI, docs, tests, pack ABI, and discovery
- those facts are structured data
- structured data is easier to validate than C++ string literals
- it avoids repeating parameter ranges and help IDs

C++ remains source of truth only for behavior.

### Decision: One Schema for Core and Packs

Reason:

- Lab consumes both through the same operator discovery model
- RT/HQ, ports, params, help, tags, and categories are not pack-specific
- pack-specific details fit into `provider`, `provenance`, and `engine`

This keeps CDP pack replaceable while making its operators first-class XYONA
operators.

### Decision: Keep CDP Algorithms in Pack

Reason:

- license boundary
- dynamic replaceability
- workspace ownership contract
- Lab must never compile CDP algorithm files directly

Core owns the generic ABI and descriptor system, not CDP implementation.

### Decision: Generate Registration

Reason:

- manual registration lists are a repeated drift source
- CMake source lists and registration lists currently duplicate identity
- CDP8 felt clean because process membership was centralized

Generated registration restores that centrality without adopting CDP8's old C
style.

### Decision: Help Belongs With Operator Module

Reason:

- users need help per node/operator
- parameter docs must match metadata
- docs must travel with packs
- Lab should not invent help for Core/Pack DSP operators

Lab owns only Lab-specific panels, topics, workflows, and UI help.

## Open Questions

1. Should Core physically rename `src/processes` to `src/operators`, or keep
   the old path for compatibility and enforce the new module contract inside it?
2. Should generated JSON be checked into source control or only generated in the
   build tree?
3. Where exactly should installed pack help live?
4. Should `de.md` be mandatory for all shipped operators?
5. Should `cdp8_inventory.yaml` generate initial `op.yaml` stubs for CDP pack
   operators?
6. Should Core's metadata loader support dotted operator IDs with explicit paths
   only, avoiding path derivation from ID?
7. Should descriptor tests be generated for every operator by default?

## Success Criteria

The roadmap is successful when all of these are true:

- A developer can add an operator by following one documented folder contract.
- Core and packs use the same metadata schema.
- Public operator descriptors are generated or validated from `op.yaml`.
- Runtime registration cannot forget an implemented operator.
- CMake cannot forget an implemented operator.
- Help docs cannot silently miss installed operators.
- Stale generated metadata is caught by CI.
- Pack operators expose help and tags in Lab just like Core operators.
- CDP provenance is visible and searchable for CDP-derived operators.
- Lab remains free of DSP and CDP implementation code.

## Summary

The current project is not unstructured because it lacks ideas. It is
unstructured because the same operator facts are maintained in too many places.

The optimal structure is a strict operator module:

```text
operator folder + op.yaml + docs + DSP + adapter + tests
```

Everything else should be generated or validated from that module. This keeps
Core, packs, and Lab aligned while preserving the correct ownership boundaries:
DSP below the host boundary, CDP algorithms inside the dynamic pack, and Lab as
the UI/orchestration consumer.
