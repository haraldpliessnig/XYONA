# Roadmap: Unified Operator Module Structure

**Status:** Completed for the current public operator surface
**Date:** 2026-04-29
**Scope:** `xyona-core`, `xyona-cdp-pack`, `xyona-lab`, `CDP8` reference workflow  
**Normative contract:** `OPERATOR_CONTRACT.md`

## Purpose

This roadmap was created to make operator identity, folder structure,
descriptor generation, and Lab node naming consistent across Core, runtime
packs, and Lab-authored public host operators.

The original symptoms were:

- CDP pack labels and Canvas names could leak provider-qualified IDs, for
  example `CDP:cdp.modify.loudness_gain1`.
- Core, CDP pack, and Lab used different metadata and documentation surfaces.
- CDP pack operators were implemented as flat adapter files.
- Core operators still used legacy `src/processes` and `meta.yaml`.
- Lab discovery filled missing naming metadata from IDs/categories and mutated
  labels with provider prefixes.

The current implementation removes those legacy paths for the current public
operator surface.

## Completed End State

### Shared Contract

Done:

- `OPERATOR_CONTRACT.md` defines the required identity, naming, engine,
  materialization, adapter, help, and validation contract.
- `OPERATOR_MODULE_AUTHORING_GUIDE.md` gives the practical module authoring
  rules.
- Root, Core, CDP pack, and Lab `AGENTS.md` files link the relevant guides.
- The shared Core validator is used by Core, CDP pack, and Lab.

### Naming And Discovery

Done:

- Public descriptors expose explicit `provider`, `providerLabel`, `family`,
  `moduleName`, `shortLabel`, `nodeNameStem`, `domain`, and `materialization`.
- CDP pack labels are provider-free human labels such as `Loudness Gain`.
- Lab discovery no longer mutates labels with prefixes such as `CDP:`.
- Lab `NodeBinder` requires a valid `nodeNameStem` and uses it for default
  Canvas names.
- Dotted operator IDs remain immutable machine IDs and are preserved in node
  payload/project state.

### Core

Done:

- Current Core operators live under `src/operators/<family>/<module>/`.
- Core no longer uses public operator `meta.yaml`.
- Core codegen consumes module-local `op.yaml`.
- Core descriptor metadata, parameter descriptors, port descriptors, flags, and
  topology defaults are generated or validated from `op.yaml`.
- Core discovery no longer derives missing public module metadata from IDs,
  categories, labels, or private paths.
- The shared validator rejects reintroduced `src/processes`, `meta.yaml`, and
  structurally invalid module paths.

### CDP Pack

Done:

- Current CDP operators live under `src/operators/<family>/<module>/`.
- CDP pack has no flat public `src/operators/cdp_*.cpp` adapter files.
- Module-local `op.yaml` drives operator metadata, descriptors, parameter
  arrays, port arrays, registration, and CMake source lists.
- Generated files are checked by
  `scripts/generate_operator_metadata.py --check`.
- Module-owned adapters stay under their module root.
- Shared Cut/CutEnd offline-session implementation lives under
  `src/operators/edit/common/` and is declared with `adapter.sharedSources`.

### Lab

Done:

- Current Lab-authored public host operators are declared in
  `specs/operators/lab-public.op.yaml`.
- Lab runtime descriptors apply matching explicit metadata through
  `CustomOperator::applyOperatorModuleMetadata(...)`.
- `CustomOperatorRegistry` rejects incomplete Lab public descriptors.
- `DiscoveryService` passes metadata through rather than deriving it.
- `NodeBinder` refuses to create/restore operator nodes without a valid
  descriptor `nodeNameStem`.
- Lab spec/runtime tests compare public Lab specs against discovery.

Lab host operator C++ classes remain in their host subsystems by design. This
is not a remaining Core/CDP-style physical module migration. If Lab later
introduces physical host-operator modules, they must use the same contract.

### CDP8

Done:

- `CDP8` remains reference-only.
- CDP provenance is captured in CDP pack `op.yaml` records where applicable.

## Phase Completion Table

| Phase | Result |
|---|---|
| Contract freeze | Completed. Root contract, guides, package AGENTS links, shared schema/validator. |
| Naming transport | Completed. Core descriptors, pack metadata, Lab discovery, and Canvas naming use explicit metadata. |
| CDP module migration | Completed for all current 16 CDP public operators. |
| CDP generated descriptors | Completed for current CDP public operators. |
| Core module migration | Completed for all current 16 Core public operators. |
| Core generated descriptor facts | Completed for current Core public operators. |
| Lab public metadata | Completed for current 17 Lab public host operators. |
| Fallback removal | Completed. Core/Lab discovery and NodeBinder no longer mask missing metadata. |
| Structure guardrails | Completed. Shared validator rejects old paths and cross-module adapter ownership. |
| Authoring documentation | Completed in root, Core, CDP pack, and Lab. |

## Verification Gates

Current required gates:

### Core

```powershell
C:\Python3.9.5\python.exe tools\operator_modules\validate_operator_modules.py --root .
C:\Python3.9.5\python.exe tools\operator_modules\test_validate_operator_modules.py
C:\Python3.9.5\python.exe scripts\codegen_params.py --in src\operators --json gen\json --out gen\include\xyona\gen
cmake --build build/windows-msvc-debug --target test_operator_module_runtime test_operator_packs test_operator_dispatcher --config Debug
ctest --test-dir build/windows-msvc-debug -C Debug -R "operator_dispatcher_tests|operator_module_runtime_tests|operator_module_metadata_tests|operator_module_validator_guardrail_tests|operator_packs_tests" --output-on-failure --timeout 60
git diff --check
```

### CDP Pack

```powershell
C:\Python3.9.5\python.exe scripts\generate_operator_metadata.py --check
C:\Python3.9.5\python.exe scripts\validate_operator_modules.py
cmake --build --preset windows-msvc-debug --target xyona_pack_cdp_ops test_cdp_descriptor_metadata test_cdp_pack test_cdp_pack_env_discovery --config Debug
ctest --test-dir build/windows-msvc-debug -C Debug -R "cdp_generated_operator_metadata_tests|cdp_operator_module_metadata_tests|cdp_descriptor_metadata_tests|cdp_pack_loader_tests|cdp_pack_env_discovery_tests" --output-on-failure --timeout 120
git diff --check
```

Add family-specific behavior/offline/golden tests for the operator being
changed.

### Lab

```powershell
C:\Python3.9.5\python.exe scripts\validate_operator_modules.py
ctest --test-dir build/windows-dev -C Debug -R lab_operator_module_metadata_tests --output-on-failure --timeout 60
build/windows-dev/tests/Debug/xyona_lab_tests.exe --test="Operator Module Spec Runtime" --xyona-only --summary-only
git diff --check
```

Run `CDP Pack Canvas Smoke` when pack discovery, descriptor labels,
node-name stems, parameter descriptors, or pack loading behavior change.

## Remaining Follow-Ups

No remaining roadmap item is required to complete the current naming and
operator-structure migration.

Future work outside this completed migration:

- Add generated descriptor/runtime comparison tests automatically for every new
  operator family as generation expands.
- Define installed pack help/doc locations and locale fallback in packaging.
- Continue CDP8 algorithm ports under the established module contract.
- Extend the production Offline Session ABI for future long-running,
  multi-output, PVOC/spectral, or large-source operators.
- Decide whether Lab should ever move host-operator C++ classes into physical
  `src/operators` modules; current explicit spec/runtime metadata is the
  accepted host-side structure.

## Add-Operator Workflow

For Core:

1. Create `src/operators/<family>/<module>/op.yaml`.
2. Add/adjust DSP and `adapter/core_operator.cpp`.
3. Regenerate Core metadata.
4. Add descriptor and behavior tests.
5. Run the Core verification gates.

For CDP pack:

1. Create `src/operators/<family>/<module>/op.yaml`.
2. Add CDP provenance and engine/materialization facts.
3. Add module-owned adapter files and optional family-local common sources.
4. Regenerate pack metadata/registration/source lists.
5. Add behavior/offline/golden tests.
6. Run the CDP pack verification gates.

For Lab public host operators:

1. Add or update the record in `specs/operators/lab-public.op.yaml`.
2. Add matching explicit runtime metadata in Lab descriptor creation.
3. Extend spec/runtime coverage if a new operator is introduced.
4. Run the Lab verification gates.

## Success Criteria

The roadmap is complete when:

- Developers have one documented folder and metadata contract.
- Core, packs, and Lab public operators use the same identity/naming schema.
- Descriptor facts are generated or validated from `op.yaml`.
- Registration and CMake source lists cannot silently omit CDP pack operators.
- Core no longer relies on `src/processes` or `meta.yaml`.
- Lab default Canvas names come from `ui.nodeNameStem`.
- Provider/family context is metadata, not label mutation.
- Structure regressions fail the shared validator.

All of these criteria are met for the current public operator surface as of
2026-04-29.
