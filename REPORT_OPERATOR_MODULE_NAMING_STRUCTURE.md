# Report: Operator Module Naming Structure

Status: Implementation slices 1-17 landed
Scope: workspace, xyona-core, xyona-cdp-pack, xyona-lab  
Date: 2026-04-29  
Roadmap: `ROADMAP_OPERATOR_MODULE_STRUCTURE.md`  
Contract: `OPERATOR_MODULE_CONTRACT.md`

This report tracks the implementation slices for structured operator identity,
provider-aware UI metadata, deterministic Canvas node naming, and operator
module validation. The initial goal was to remove Lab-side label mutation such
as `CDP: ...` and stop deriving default node names from dotted operator IDs such
as `cdp.modify.loudness_gain`. Later slices hardened the same surface by making
engine domain/materialization explicit, by adding a schema-backed metadata
gate for current Core, CDP-pack, and Lab operator surfaces, by comparing
those declared surfaces against runtime discovery descriptors, and by starting
the physical operator-module folder migration in the CDP pack.

## Executive Status

The first seventeen cross-repository naming/metadata slices are implemented and
verified.

`xyona-core` now exposes transitional operator module identity fields directly
on `xyona::OpDesc`. The dynamic pack loader fills those fields for loaded
packs using pack identity, operator ID structure, and optional operator
metadata JSON. This gives hosts a stable descriptor surface before the final
schema/codegen path is introduced.

`xyona-cdp-pack` now publishes explicit `ui.shortLabel` and
`ui.nodeNameStem` metadata for every currently registered CDP operator. The
first visible target case is covered: `cdp.modify.loudness_gain` now carries
the intended node-name stem `loud_gain`, allowing Lab to create `loud_gain1`
instead of a provider-prefixed or dotted name.

`xyona-lab` now consumes structured descriptor metadata. Discovery no longer
rewrites labels with provider prefixes such as `CDP: `. Canvas node creation
and restore now generate default names from `nodeNameStem` while preserving
the stable operator ID on the node payload for graph execution and project
persistence.

Slice 2 adds the first validation gate around these fields. Core now exposes a
shared node-name-stem validity helper and only reads pack `domain` and
`materialization` from the `engine` metadata object. CDP pack engine macros now
publish explicit domain/materialization values for every current process shape.
Lab discovery coverage now proves that Lab-authored and Core-authored operators
receive the same naming defaults as pack operators.

Slice 3 adds the first real operator module validator. Core now owns the shared
`xyona-operator-v1` schema and validation script. CDP pack publishes
transitional `specs/operators/*.op.yaml` data for all 16 currently registered
CDP operators. Lab publishes equivalent specs for 17 current public host
operators. Core, CDP pack, and Lab now expose CTest metadata gates for these
surfaces.

Slice 4 closes the first spec/runtime drift loop. Core now compares legacy
`src/processes/**/meta.yaml` records against actual registered runtime
descriptors. CDP pack compares `specs/operators/cdp-current.op.yaml` against
the loaded dynamic-pack descriptors and operator metadata JSON. Lab compares
`specs/operators/lab-public.op.yaml` against `DiscoveryService` descriptors
and palette UI metadata. This gate found and fixed real drift: Core
`audio_clip` was not registered through `registerAllProcesses()` and had a
descriptor category mismatch, CDP descriptor labels still repeated provider
and family names, and Lab discovery needed full provider-local family defaults,
explicit domain/materialization defaults, analyzer test registration, and a
stable `grid` node-name stem for `lab.grid_source`.

Slice 5 starts Roadmap Phase 3 with the lowest-risk CDP family: `utility`.
The six current utility operators now live in provider-local module roots under
`src/operators/utility/<operator>/`. Their C++ pack adapters live below
`adapter/`, existing `identity` and `db_gain` HelpCenter docs moved to the
same provider-local module roots, and their operator specs moved out of the
temporary aggregate file into per-module `op.yaml` files. The descriptor
runtime test now scans the repository for both remaining aggregate
`*.op.yaml` files and migrated module `op.yaml` files, so split specs remain
covered by the same runtime gate.

Slice 6 continues Roadmap Phase 3 with the CDP `modify/loudness` group. The
four current loudness operators now use provider-local module roots under
`src/operators/modify/<operator>/`, with adapters, existing HelpCenter docs,
and per-module `op.yaml` records co-located. The temporary aggregate spec now
only keeps the not-yet-migrated CDP groups, while the same validator and
runtime descriptor gate continue to cover the full 16-operator pack surface.

Slice 7 completes the current CDP `modify` structure migration by moving the
`modify/space` operators. `cdp.modify.space_mirror` and
`cdp.modify.space_narrow` now have provider-local module roots with co-located
adapter code, HelpCenter docs, and per-module `op.yaml`. The old
provider-prefixed `cdp.modify` documentation-only folder is gone from the
working tree after this slice.

Slice 8 moves the current CDP `edit` operators into module roots. `cut` and
`cutend` now each own a provider-local `op.yaml`; their current shared
Cut/CutEnd adapter is no longer a flat `src/operators/*.cpp` file and now
lives below `src/operators/edit/cut/adapter/`. Splitting that shared adapter
can happen later with descriptor/code generation, but the public operator specs
are now module-local.

Slice 9 moves the current CDP `pvoc` operators into module roots and removes
the transitional aggregate `specs/operators/cdp-current.op.yaml`. All 16
currently registered CDP pack operators are now represented by module-local
`op.yaml` files under `src/operators/<family>/<operator>/`, while the runtime
descriptor gate still validates the full discovered pack surface.

Slice 10 applies the explicit no-backward-compatibility policy to pack
discovery. Core no longer accepts pack operators that rely on ID/category
fallbacks for module identity. A loaded pack operator must publish `provider`,
`providerLabel`, `family`, `moduleName`, `ui.shortLabel`,
`ui.nodeNameStem`, `engine.domain`, and `engine.materialization` in operator
metadata. CDP pack runtime metadata now carries those fields for all 16 current
operators, and the CDP descriptor gate verifies metadata, descriptors, and
module-local `op.yaml` agree.

Slice 11 starts Roadmap Phase 2 for the CDP pack by generating the first
runtime metadata fragments from module-local `op.yaml`. The generated header
now supplies operator identity/UI and `engine` metadata fragments for all 16
current CDP operators. The old handwritten shared `XYONA_CDP_ENGINE_*` macros
are gone from `pack_descriptors.h`; PVOC artifact and spectral contract facts
now live in the relevant module-local `op.yaml` files. Adapter code still owns
CDP provenance, validation, port, parameter, descriptor, and registration
surfaces until the next generation slices replace them.

Slice 12 moves the remaining operator-level CDP provenance and validation JSON
out of handwritten adapter fragments and into module-local `op.yaml`.
`scripts/generate_operator_metadata.py` now emits complete operator metadata
JSON for all current CDP operators, including `xyona`, provider/family/module,
UI naming, `cdp`, `engine`, and `validation` objects. The adapters now only
reference generated `XYONA_CDP_OP_META_*` macros for operator metadata; port,
parameter, descriptor, CMake, and registration generation remain the next
Phase-2 work.

Slice 13 moves CDP port and parameter metadata JSON into the same generated
metadata path. Module-local `op.yaml` files now declare current public ports,
typed PVOC port data metadata, CDP stereo/channel-policy metadata, and UI
metadata for exposed parameters. The generator emits `XYONA_CDP_PARAM_META_*`,
`XYONA_CDP_INPUT_META_*`, and `XYONA_CDP_OUTPUT_META_*` macros, and adapters no
longer carry hand-authored `param_meta` or `port_meta` JSON strings.

Slice 14 moves top-level CDP pack operator descriptor initializers onto the
generated path. Module-local `op.yaml` now carries descriptor summary,
description, icon, version, and routing policy. The generator emits
`XYONA_CDP_OP_DESC_*` initializer macros for `xyona_pack_v2_op_desc`; adapters
still own behavior callbacks plus local port/parameter descriptor arrays, but
no longer hand-write the top-level operator descriptor body.

Slice 15 removes the manual CDP pack registration list. Module-local `op.yaml`
now declares each adapter header and registration function, and the generator
emits `src/generated/cdp_operator_registration.h`. `pack_registration.cpp`
validates the host ABI and delegates to the generated registration helper, so
adding/removing an operator no longer requires hand-editing the central
registration source.

Slice 16 removes the manual CMake operator source list for current CDP
operators. Module-local `op.yaml` now also declares each adapter source file,
the generator emits `src/generated/cdp_operator_sources.cmake`, and the pack
target includes `${XYONA_CDP_OPERATOR_SOURCES}` instead of listing every
operator adapter in `CMakeLists.txt`.

Slice 17 moves current CDP port descriptor facts onto the generated path.
The generator now emits `XYONA_CDP_INPUT_PORT_DESC_*` and
`XYONA_CDP_OUTPUT_PORT_DESC_*` macros from module-local `op.yaml` port
semantics, including variable audio ports, fixed stereo ports, mono PVOC
analysis/synthesis ports, and typed PVOC data ports. Current adapters no
longer hand-write the port descriptor calls; they keep only the local C arrays
that bind generated port descriptors into each operator descriptor. The slice
also fixes the shared Cut/CutEnd adapter so CutEnd's `splice_ms` descriptor
uses CutEnd's generated parameter metadata instead of Cut's metadata.

## Current Baseline Before This Slice

Existing behavior:

- Pack operator IDs were stable and namespaced, for example
  `cdp.modify.loudness_gain`.
- Lab displayed pack origin by mutating descriptor labels to include a
  provider prefix, for example `CDP: ...`.
- `NodeBinder` generated new node names from `desc.id`.
- `NodeStore` lowercased the provided type string and appended a counter.
- This produced default Canvas names that could include dotted provider/family
  fragments and did not respect provider-local naming conventions.
- `xyona::OpDesc` did not expose provider, family, module, short label, node
  name stem, domain, or materialization metadata.
- Pack ABI v2.1 already transported opaque operator metadata JSON, but hosts
  did not have a normalized descriptor-level surface for the new contract.

Known product problem:

- Names such as `CDP:cdp.modify.loudness-gain1` or similar dotted/cryptic
  default names are not acceptable as public operator-node names.
- Provider identity, family/type, and module identity must be structural
  metadata, not baked into labels or default node names.

## Implementation Summary

### xyona-core

Added transitional descriptor fields to `xyona::OpDesc`:

- `provider`
- `providerLabel`
- `family`
- `moduleName`
- `shortLabel`
- `nodeNameStem`
- `domain`
- `materialization`

Updated the dynamic pack loader to populate those fields for ABI v2 pack
operators:

- `provider` defaults to the pack ID.
- `providerLabel` defaults to the pack display name.
- `family` is derived from the second dotted ID segment, for example
  `modify` in `cdp.modify.loudness_gain`.
- `moduleName` is derived from the remaining provider-local ID tail.
- `shortLabel` is read from operator metadata when present, otherwise derived
  from the descriptor label with provider/family prefixes stripped.
- `nodeNameStem` is read from operator metadata when present, otherwise
  derived from the module name and sanitized.
- `domain` is read from metadata when present, otherwise derived
  conservatively from PVOC/spectral metadata, generator shape, or audio ports.
- `materialization` is read from metadata when present.

Slice 2 additions:

- added `xyona::isValidOperatorNodeNameStem()` and
  `OpDesc::hasValidNodeNameStem()`
- limited explicit `domain` and `materialization` reads to the top-level
  `engine` object instead of any nested object in `op_meta_json`
- added category-based family fallback for IDs that do not include a provider
  and family segment, for example Core/test fixture IDs
- extended pack-loader tests so `ui.nodeNameStem`, invalid stems,
  `engine.domain`, and `engine.materialization` are contract-visible

Slice 3 additions:

- added `tools/operator_modules/schema/xyona-operator-v1.schema.json`
- added `tools/operator_modules/validate_operator_modules.py`
- validator enforces provider/family/module separation, lowercase safe
  `ui.nodeNameStem`, duplicate ID/stem detection, required
  `engine.domain`, required `engine.materialization`, whole-file realtime
  guardrails, CDP provenance, and help ID shape
- Core CTest now runs the validator against existing
  `src/processes/**/meta.yaml` through a transitional legacy adapter

Slice 4 additions:

- `xyona::api::getAllOperators()` and `xyona::api::getOperatorDesc()` now
  normalize discovery defaults for legacy/Core descriptors, including
  provider, provider label, family, module name, short label, node-name stem,
  domain, and materialization
- `audio_clip` is registered by `registerAllProcesses()` and its runtime
  category now matches the existing `meta.yaml` value `I/O`
- added `test_operator_module_runtime`, which scans
  `src/processes/**/meta.yaml`, compares each metadata record to the runtime
  descriptor, and fails if the registered Core operator set drifts from the
  metadata files
- dynamic-pack descriptors with no explicit materialization now normalize to
  the contract value `none`

Slice 10 additions:

- removed the pack-loader fallback path that derived module identity from pack
  ID, operator ID, category, labels, ports, or PVOC string hints
- pack operators without explicit module identity metadata now fail
  registration
- pack IDs accepted by this strict path must use exactly
  `<provider>.<family>.<module>`
- invalid pack `ui.nodeNameStem` values are rejected instead of sanitized into
  a different accepted stem
- updated the Core v2 pack test fixture to use explicit module metadata and
  updated the old metadata-less fixture expectation to a registration reject

### xyona-cdp-pack

Added explicit operator UI metadata to every currently registered CDP operator:

- `ui.shortLabel`
- `ui.nodeNameStem`

Current CDP node-name stems:

| Operator ID | Stem |
| --- | --- |
| `cdp.edit.cut` | `cut` |
| `cdp.edit.cutend` | `cutend` |
| `cdp.modify.loudness_dbgain` | `loud_db_gain` |
| `cdp.modify.loudness_gain` | `loud_gain` |
| `cdp.modify.loudness_normalise` | `loud_norm` |
| `cdp.modify.loudness_phase_invert` | `phase_inv` |
| `cdp.modify.space_mirror` | `space_mirror` |
| `cdp.modify.space_narrow` | `space_narrow` |
| `cdp.pvoc.anal` | `pvoc_anal` |
| `cdp.pvoc.synth` | `pvoc_synth` |
| `cdp.utility.db_gain` | `db_gain` |
| `cdp.utility.generator_probe` | `generator_probe` |
| `cdp.utility.identity` | `identity` |
| `cdp.utility.length_change` | `length_change` |
| `cdp.utility.pvoc_identity` | `pvoc_identity` |
| `cdp.utility.pvoc_probe` | `pvoc_probe` |

Extended the descriptor metadata contract test so CDP operators must expose:

- `provider == cdp`
- `providerLabel == CDP`
- category-matching provider-local `family`
- non-empty `moduleName`
- non-empty `shortLabel`
- exact expected `nodeNameStem`
- valid domain classification
- no Lab-style `CDP: ` label prefix
- matching `ui.nodeNameStem` in operator metadata JSON

Slice 2 additions:

- every CDP engine metadata macro now emits explicit `engine.domain`
- every CDP engine metadata macro now emits explicit
  `engine.materialization`
- descriptor tests now compare descriptor-level `domain` and
  `materialization` against the engine metadata JSON for every current CDP
  operator
- nested artifact materialization, for example `artifact.materialization`, is
  no longer allowed to satisfy the descriptor-level materialization contract

Slice 3 additions:

- added `specs/operators/cdp-current.op.yaml` with one validated record for
  every currently registered CDP pack operator
- added `scripts/validate_operator_modules.py` wrapper that uses the shared
  Core validator from the workspace or `XYONA_CORE_PATH`
- added `cdp_operator_module_metadata_tests` to CTest
- the specs validate the current `provider`, provider-local `family`,
  `moduleName`, `ui.nodeNameStem`, capability, engine domain, materialization,
  and CDP provenance surface without moving the flat C++ operator files yet

Slice 4 additions:

- `cdp_descriptor_metadata_tests` now loads
  `specs/operators/cdp-current.op.yaml`
- the test compares every current loaded pack descriptor against the spec for
  provider, provider label, family, module name, label, operator type,
  category, short label, node-name stem, capabilities, domain, and
  materialization
- the same test compares operator metadata JSON against the spec for process
  shape, domain, materialization, whole-file requirement, length-changing flag,
  short label, and node-name stem
- all current CDP public descriptor labels were made provider-free and
  family-free, for example `Loudness Gain`, `PVOC Analysis`, `dB Gain`, and
  `Cut`, with provider/family context left in structured fields
- metadata-test failures now exit non-interactively instead of relying on a
  debug assert dialog

Slice 5 additions:

- moved `cdp.utility.db_gain`, `cdp.utility.generator_probe`,
  `cdp.utility.identity`, `cdp.utility.length_change`,
  `cdp.utility.pvoc_identity`, and `cdp.utility.pvoc_probe` into canonical
  provider-local module roots under `src/operators/utility/`
- moved utility C++ adapter files into each module's `adapter/` folder
- moved existing `db_gain` and `identity` help docs from
  `src/operators/cdp.utility/...` to `src/operators/utility/...`
- split the six utility records out of `specs/operators/cdp-current.op.yaml`
  into per-module `op.yaml`
- updated `cdp_descriptor_metadata_tests` to scan a repository root for both
  aggregate `*.op.yaml` and module-local `op.yaml` records
- kept the current CMake registration explicit while changing source paths;
  descriptor generation and generated registration remain future work

Slice 6 additions:

- moved `cdp.modify.loudness_gain`, `cdp.modify.loudness_dbgain`,
  `cdp.modify.loudness_normalise`, and
  `cdp.modify.loudness_phase_invert` into canonical provider-local module
  roots under `src/operators/modify/`
- moved loudness C++ adapter files into each module's `adapter/` folder
- moved existing loudness HelpCenter docs from `src/operators/cdp.modify/...`
  to `src/operators/modify/...`
- split the four loudness records out of `specs/operators/cdp-current.op.yaml`
  into per-module `op.yaml`
- updated explicit CMake and include references without changing public
  operator IDs or descriptor metadata

Slice 7 additions:

- moved `cdp.modify.space_mirror` and `cdp.modify.space_narrow` into
  canonical provider-local module roots under `src/operators/modify/`
- moved Space C++ adapter files into each module's `adapter/` folder
- moved existing Space HelpCenter docs from `src/operators/cdp.modify/...` to
  `src/operators/modify/...`
- split the two Space records out of `specs/operators/cdp-current.op.yaml`
  into per-module `op.yaml`
- updated explicit CMake and pack-registration include references without
  changing public operator IDs or descriptor metadata

Slice 8 additions:

- moved the shared `cdp.edit.cut` / `cdp.edit.cutend` adapter into
  `src/operators/edit/cut/adapter/`
- added module-local `op.yaml` records for `cdp.edit.cut` and
  `cdp.edit.cutend`
- removed the two edit records from the transitional aggregate
  `specs/operators/cdp-current.op.yaml`
- updated CMake, Offline Session API includes, pack registration includes, and
  edit tests without changing public operator IDs or descriptor metadata

Slice 9 additions:

- moved `cdp.pvoc.anal` and `cdp.pvoc.synth` into canonical provider-local
  module roots under `src/operators/pvoc/`
- moved PVOC C++ adapter files into each module's `adapter/` folder
- added module-local `op.yaml` records for both PVOC operators
- removed `specs/operators/cdp-current.op.yaml`; all current CDP specs are now
  module-local
- updated `src/operators/README.md` to describe the current module-root layout

Slice 10 additions:

- added explicit runtime metadata fields to every current CDP operator:
  `provider`, `providerLabel`, `family`, and `moduleName`
- strengthened `test_cdp_descriptor_metadata` so operator metadata JSON must
  match module-local `op.yaml` for provider, provider label, family, module
  name, UI naming, engine domain, and materialization
- kept public operator IDs unchanged while removing the loader's ability to
  infer missing CDP metadata from those IDs

Slice 11 additions:

- added `scripts/generate_operator_metadata.py`, which reads
  `src/operators/**/op.yaml` and generates
  `src/generated/cdp_operator_metadata.h`
- generated operator identity/UI metadata fragments from `op.yaml`:
  `provider`, `providerLabel`, `family`, `moduleName`, `ui.shortLabel`, and
  `ui.nodeNameStem`
- generated `engine` metadata fragments from `op.yaml`, including PVOC
  artifact, input-artifact, and spectral contract details
- removed the old shared handwritten `XYONA_CDP_ENGINE_*` macros from
  `src/support/pack_descriptors.h`
- updated all current CDP adapters to concatenate generated identity/UI/engine
  fragments with the still-handwritten CDP provenance and validation fragments
- added `cdp_generated_operator_metadata_tests`, a CTest staleness gate for the
  checked-in generated header
- extended the descriptor metadata test's transitional YAML reader so block
  `engine:` mappings remain covered by the same runtime/spec comparison gate

Slice 12 additions:

- extended `scripts/generate_operator_metadata.py` so it generates complete
  operator metadata JSON from `op.yaml`, not only identity/UI/engine fragments
- moved CDP provenance details such as `command`, `sourceFile`,
  `compatibilityNote`, and validation `cdp8Reference` into module-local
  `op.yaml`
- replaced every adapter's hand-concatenated `cdp` and `validation` operator
  metadata JSON with generated `XYONA_CDP_OP_META_*` macros
- kept compatibility `XYONA_CDP_OP_ENGINE_*` fragments for focused spectral
  tests until the descriptor generator fully replaces those test macros

Slice 13 additions:

- added `ports.inputs`, `ports.outputs`, and detailed `params` metadata to the
  current CDP module-local `op.yaml` files
- corrected stale transitional parameter IDs in module specs, for example
  `cdp.utility.db_gain` now declares `gain_db`,
  `cdp.modify.loudness_dbgain` declares `gain_db`,
  `cdp.modify.loudness_normalise` declares `target_peak`, and
  `cdp.modify.space_narrow` declares `narrowing`
- generated parameter metadata macros from `op.yaml`
- generated input/output port metadata macros from `op.yaml`, including typed
  PVOC data-port metadata and CDP stereo/channel-policy metadata
- replaced all remaining hand-written adapter `param_meta` and `port_meta`
  JSON literals with generated macros

Slice 14 additions:

- added top-level descriptor facts to CDP module-local `op.yaml`:
  `summary`, `description`, `icon`, `version`, and `routingPolicy`
- generated `xyona_pack_v2_op_desc` initializer macros from those `op.yaml`
  fields plus existing capability/category/operator-type fields
- replaced all current CDP adapter `xyona_pack_v2_op_desc` aggregate bodies
  with generated `XYONA_CDP_OP_DESC_*` macros
- corrected the shared Cut/CutEnd adapter so each operator's generated port
  metadata is attached to its own descriptor arrays instead of sharing the
  other operator's generated metadata by accident

Slice 15 additions:

- added `adapter.header` and `adapter.registrationFunction` declarations to
  every current CDP module-local `op.yaml`
- extended `scripts/generate_operator_metadata.py` to generate
  `src/generated/cdp_operator_registration.h` and to include that file in the
  existing staleness check
- replaced the hand-written include list and registration call list in
  `src/pack_registration.cpp` with a call to the generated registration helper

Slice 16 additions:

- added `adapter.source` declarations to every current CDP module-local
  `op.yaml`
- extended `scripts/generate_operator_metadata.py` to generate
  `src/generated/cdp_operator_sources.cmake` and include it in the staleness
  check
- updated `CMakeLists.txt` so `xyona_pack_cdp_ops` consumes the generated
  `XYONA_CDP_OPERATOR_SOURCES` list

Slice 17 additions:

- extended `scripts/generate_operator_metadata.py` to emit generated port
  descriptor macros beside the generated port metadata JSON macros
- included port `tags` in generated port metadata JSON so typed data-port
  descriptors and metadata share the same `op.yaml` source
- replaced all current adapter calls to `makeAudioPortDesc`,
  `makeFixedAudioPortDesc`, and `makeFixedTaggedPortDesc` with generated
  `XYONA_CDP_*_PORT_DESC_*` macros
- corrected the CutEnd `splice_ms` descriptor metadata binding in the shared
  edit adapter

### xyona-lab

Updated `DiscoveryService`:

- no longer mutates descriptor labels to prepend pack provider names
- fills missing provider metadata for Core and Lab-authored operators
- exposes provider, family, short label, and node-name stem through `OpUiMeta`
- uses `shortLabel` for palette display labels when available

Updated `NodeBinder`:

- uses `nodeNameStem` for default Canvas names
- falls back through `moduleName`, `shortLabel`, and final ID segment
- sanitizes fallback stems before passing them to `NodeStore`
- preserves UI identity fields when refreshed operator descriptors are returned
  by Lab-managed operators after topology/default initialization

Updated CDP Canvas smoke coverage:

- CDP descriptors must expose provider/family/node-name metadata
- Lab discovery labels must not contain `CDP: `
- `cdp.utility.db_gain` creates `db_gain1`
- `cdp.modify.loudness_gain` creates `loud_gain1`
- `cdp.modify.loudness_normalise` creates `loud_norm1`

Slice 2 additions:

- `DiscoveryService` now derives missing `family` values from provider-local
  category paths where IDs are shorter than `<provider>.<family>.<module>`
- Canvas parameter persistence coverage now verifies naming metadata for
  Lab-authored `lab.audio_in` and Core `gain`
- the test also instantiates `lab.audio_in` through `NodeBinder` and confirms
  the visible default node name is `audio_in1` while `opId` stays
  `lab.audio_in`

Slice 3 additions:

- added `specs/operators/lab-public.op.yaml` with validated records for 17
  current public Lab-authored host operators
- added `scripts/validate_operator_modules.py` wrapper that uses the shared
  Core validator from the workspace or `XYONA_CORE_PATH`
- added `lab_operator_module_metadata_tests` to CTest
- the specs make Lab-owned host nodes follow the same provider/family/module,
  `ui.nodeNameStem`, capability, domain, and materialization vocabulary as
  Core and pack operators

Slice 4 additions:

- added `OperatorModuleSpecRuntimeTests`, which loads
  `specs/operators/lab-public.op.yaml` and compares it to `DiscoveryService`
  descriptors plus palette UI metadata
- `DiscoveryService` now derives Lab families from the full provider-local
  category tail, for example `lab.system.audio` becomes `system.audio`
- Lab discovery now supplies explicit fallback `domain` and `materialization`
  values for public Lab operators
- the Lab test harness registers analyzer operators so the spec/runtime test
  covers the full public Lab spec set
- `lab.grid_source` now declares the stable node-name stem `grid`

## Boundary Notes

- CDP algorithms remain in `xyona-cdp-pack`.
- Lab consumes descriptors and operator metadata but does not encode CDP
  algorithm knowledge.
- Core owns the transitional descriptor surface and pack loader normalization.
- Lab-authored public operators are handled by the same metadata fallback path
  and are no longer treated as a naming exception.
- `CDP8` was not modified.

## Verification Log

Observed on Windows / MSVC debug builds:

- `xyona-core`
  - `cmake --preset windows-msvc-debug`
  - `cmake --build build/windows-msvc-debug --target test_operator_module_runtime test_operator_packs --config Debug`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R operator_module_runtime_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R operator_module_metadata_tests --output-on-failure`
  - `cmake --build build/windows-msvc-debug --target test_operator_packs --config Debug`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R operator_packs_tests --output-on-failure`
  - Result: passed

- `xyona-cdp-pack`
  - `cmake --preset windows-msvc-debug`
  - `cmake --build build/windows-msvc-debug --target xyona_pack_cdp_ops test_cdp_descriptor_metadata test_cdp_utility_length_change test_cdp_pack test_cdp_pack_env_discovery --config Debug`
  - `cmake --build build/windows-msvc-debug --target xyona_pack_cdp_ops test_cdp_descriptor_metadata test_cdp_modify_loudness_gain test_cdp_modify_loudness_modes test_cdp_modify_loudness_normalise test_cdp_pack test_cdp_pack_env_discovery --config Debug`
  - `cmake --build build/windows-msvc-debug --target xyona_pack_cdp_ops test_cdp_descriptor_metadata test_cdp_modify_space test_cdp_pack test_cdp_pack_env_discovery --config Debug`
  - `cmake --build build/windows-msvc-debug --target xyona_pack_cdp_ops test_cdp_descriptor_metadata test_cdp_edit_cut test_cdp_pack test_cdp_pack_env_discovery --config Debug`
  - `cmake --build build/windows-msvc-debug --target xyona_pack_cdp_ops test_cdp_descriptor_metadata test_cdp_pvoc_analysis test_cdp_pack test_cdp_pack_env_discovery --config Debug`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_operator_module_metadata_tests --output-on-failure`
  - `cmake --build build/windows-msvc-debug --target test_cdp_descriptor_metadata --config Debug`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_descriptor_metadata_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_edit_cut_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_modify_loudness_gain_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_modify_loudness_modes_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_modify_loudness_normalise_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_modify_space_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_pvoc_analysis_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_pvoc_golden_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_utility_length_change_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_pack_loader_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_pack_env_discovery_tests --output-on-failure`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_offline_session_conformance_tests --output-on-failure`
  - `C:\Python3.9.5\python.exe scripts\validate_operator_modules.py`
  - `C:\Python3.9.5\python.exe scripts\generate_operator_metadata.py --check`
  - `cmake --build build/windows-msvc-debug --target xyona_pack_cdp_ops test_cdp_descriptor_metadata test_cdp_spectral_contract test_cdp_pack test_cdp_pack_env_discovery --config Debug`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R "cdp_generated_operator_metadata_tests|cdp_operator_module_metadata_tests|cdp_descriptor_metadata_tests|cdp_spectral_contract_tests|cdp_pack_loader_tests|cdp_pack_env_discovery_tests" --output-on-failure`
  - Result: passed

- `xyona-lab`
  - `cmake --preset windows-dev`
  - `ctest --test-dir build/windows-dev -C Debug -R lab_operator_module_metadata_tests --output-on-failure`
  - `cmake --build build/windows-dev --target xyona_lab_tests --config Debug`
  - `build/windows-dev/tests/Debug/xyona_lab_tests.exe --test="Operator Module Spec Runtime" --xyona-only --summary-only`
  - `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug` with the generated CDP metadata pack
  - `build/windows-dev/tests/Debug/xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only`
  - `build/windows-dev/tests/Debug/xyona_lab_tests.exe --test="Canvas Param Persistence" --xyona-only --summary-only`
  - Result: passed

- Diff hygiene:
  - `git diff --check` passed in affected repositories.

Observed warnings:

- Existing MSVC warning noise remains in the broader builds, including
  descriptor helper shadowing warnings and unrelated Lab/Core warnings.
  These warnings did not fail the targeted verification.

## Remaining Work

This slice intentionally does not finish the full operator module structure.
Remaining roadmap work:

- Move transitional flat descriptor fields behind the final `op.yaml` /
  generated metadata pipeline.
- Remove remaining Core/Lab discovery defaults as those repos migrate to
  canonical `op.yaml` module roots.
- Keep new CDP operators on the module-root path from first commit; do not
  reintroduce flat `src/operators/cdp_*.cpp` public operator files.
- Split the current shared Cut/CutEnd adapter if descriptor generation or
  future edit modes make separate adapters materially cleaner.
- Operator-level CDP provenance, validation, parameter metadata, port
  metadata, port descriptor facts, and top-level pack descriptor initializers
  are now generated; remaining CDP handwritten descriptor debt is parameter
  descriptor arrays plus the small local descriptor array shells that bind
  generated descriptors into each adapter.
- Promote the current focused C++ spec/runtime comparison parsers into the
  final shared validator/codegen path once descriptor generation exists.
- Compare generated descriptors against runtime discovery once the generated
  descriptor pipeline replaces handwritten descriptors.
- Expand the current CDP metadata generator beyond identity/UI/engine JSON
  fragments until it owns complete pack descriptors and registration.
- Replace minimal JSON string extraction in the pack loader with a structured
  parser or generated typed metadata once the final metadata schema stabilizes.

## Commit Map

Slice 1:

- `xyona-core`: `c809629f856e4097c6b84dbfc790b66171f6328e`
  - `feat(core): expose operator module ui identity`
- `xyona-cdp-pack`: `222b4cd4e31e2df9b89d0eac336e32b184c649a9`
  - `feat(cdp-pack): publish operator ui name stems`
- `xyona-lab`: `bcb40d3223740afe06f6a7addc2db694e2793659`
  - `feat(lab): name operator nodes from ui stems`
- Workspace root: `f0b05dafa49794499871f0f8e79c1e32c16414b1`
  - `docs: report operator module naming structure slice`

Slice 2:

- `xyona-core`: `01db404d6b416029d20df1913b8245c5027fd7ed`
  - `feat(core): validate operator ui identity metadata`
- `xyona-cdp-pack`: `85915095730402516df19302fb30ccb85f5813a8`
  - `feat(cdp-pack): require explicit engine domain metadata`
- `xyona-lab`: `473f13905faad3bffe36e4629ed39f551ee01fe7`
  - `test(lab): cover discovery naming metadata`
- Workspace root: `5348070d60b68d46e98a8e49b25eba6cd223943c`
  - `docs: report operator metadata validation slice`

Slice 3:

- `xyona-core`: `6005f573d939d523f2b69b657167c79b516962d5`
  - `feat(core): add operator module validator`
- `xyona-cdp-pack`: `d6d839a771f581ab3478b7b9af87188b449dd04d`
  - `feat(cdp-pack): add operator module specs gate`
- `xyona-lab`: `f2061824f948afe768b87f7f5e8cf263b01818c9`
  - `feat(lab): add public operator module specs gate`
- Workspace root: `0db82e3ae660f86d59ca63131b1c1aff13ae352a`
  - `docs: report operator module validation slice`

Slice 4:

- `xyona-core`: `1c8acd29e0d98906123269c3cfcfe75a0a8bb613`
  - `feat(core): compare operator metadata specs to runtime`
- `xyona-cdp-pack`: `7ade2795f151b84c46f3935c183879d5af556f69`
  - `test(cdp-pack): compare operator specs to runtime metadata`
- `xyona-lab`: `c39c66453e7790ff19de6aabdf8fcc7db1de6cde`
  - `test(lab): compare public operator specs to discovery`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.

Slice 5:

- `xyona-cdp-pack`: `54f442fa8cc3384256d0bdc1067c4cd7708a5161`
  - `refactor(cdp-pack): move utility operators into module roots`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.

Slice 6:

- `xyona-cdp-pack`: `5a5ee2680f3f060fc6e7bf847d9303d8f46fdd49`
  - `refactor(cdp-pack): move loudness operators into module roots`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.

Slice 7:

- `xyona-cdp-pack`: `45f3df6d1fe9a80c5dff5b784591f61bc5abb170`
  - `refactor(cdp-pack): move space operators into module roots`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.

Slice 8:

- `xyona-cdp-pack`: `1aa83934ceaba44ca551ffb298ecdaf65cc6f54a`
  - `refactor(cdp-pack): move edit operators into module roots`

Slice 9:

- `xyona-cdp-pack`: `42c0b7f7a64f0aec2eac4660908ef2b64ef5b0b4`
  - `refactor(cdp-pack): move pvoc operators into module roots`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.

Slice 10:

- `xyona-core`: `33f38f26f04a6006cdfea5ac04b8adc3813ce67e`
  - `feat(core): require explicit pack module metadata`
- `xyona-cdp-pack`: `96df671a8f4773ccd6924f49fd4eb89ae2638b6a`
  - `feat(cdp-pack): publish required module metadata`
- Workspace root: this report/contract/roadmap commit plus the updated
  `xyona-cdp-pack` gitlink.

Slice 11:

- `xyona-cdp-pack`: `d72145796e0e4dcce48a49c51ae4676b7332af5c`
  - `feat(cdp-pack): generate operator metadata fragments`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.

Slice 12:

- `xyona-cdp-pack`: `3a73ca81845d9285b7ccefec28fd59f0cb8ad07d`
  - `feat(cdp-pack): generate full operator metadata json`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.

Slice 13:

- `xyona-cdp-pack`: `4336559f963974ad58f48680f051c400721ba3e8`
  - `feat(cdp-pack): generate port and parameter metadata`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.

Slice 14:

- `xyona-cdp-pack`: `10c48396de25f46fccb579470d25d2021e96811c`
  - `feat(cdp-pack): generate operator descriptor initializers`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.

Slice 15:

- `xyona-cdp-pack`: `bbd72729881f7c8d6f6090dd8a9d8969b383a0e7`
  - `feat(cdp-pack): generate operator registration`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.

Slice 16:

- `xyona-cdp-pack`: `65f8a220cfc123fc418ab3e2c6230993d8f54917`
  - `feat(cdp-pack): generate operator source list`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.

Slice 17:

- `xyona-cdp-pack`: `a45b8a1c6290e647927be560392fc8c0208a9a09`
  - `feat(cdp-pack): generate port descriptors`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.
