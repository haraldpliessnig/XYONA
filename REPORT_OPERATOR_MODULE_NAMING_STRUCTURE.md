# Report: Operator Module Naming Structure

Status: Implementation slices 1-4 landed
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
gate for current Core, CDP-pack, and Lab operator surfaces, and by comparing
those declared surfaces against runtime discovery descriptors.

## Executive Status

The first four cross-repository naming/metadata slices are implemented and
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

The loader remains backward-compatible with existing packs because every field
has a deterministic fallback.

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
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_operator_module_metadata_tests --output-on-failure`
  - `cmake --build build/windows-msvc-debug --target test_cdp_descriptor_metadata --config Debug`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_descriptor_metadata_tests --output-on-failure`
  - Result: passed

- `xyona-lab`
  - `cmake --preset windows-dev`
  - `ctest --test-dir build/windows-dev -C Debug -R lab_operator_module_metadata_tests --output-on-failure`
  - `cmake --build build/windows-dev --target xyona_lab_tests --config Debug`
  - `build/windows-dev/tests/Debug/xyona_lab_tests.exe --test="Operator Module Spec Runtime" --xyona-only --summary-only`
  - `XYONA_OPERATOR_PACK_PATH=D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug`
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
- Split transitional aggregate `*.op.yaml` files into canonical per-operator
  module roots as folders are migrated.
- Promote the current focused C++ spec/runtime comparison parsers into the
  final shared validator/codegen path once descriptor generation exists.
- Compare generated descriptors against runtime discovery once the generated
  descriptor pipeline replaces handwritten descriptors.
- Move explicit `engine.domain` and `engine.materialization` facts out of
  handwritten JSON/string macros and into generated metadata from `op.yaml`.
- Replace minimal JSON string extraction in the pack loader with a structured
  parser once the final metadata schema stabilizes.
- Decide whether very old persisted dotted node names should be migrated or
  left unchanged as user-authored project data.

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
