# Report: Operator Module Naming Structure

Status: Implementation slice 1 landed  
Scope: workspace, xyona-core, xyona-cdp-pack, xyona-lab  
Date: 2026-04-29  
Roadmap: `ROADMAP_OPERATOR_MODULE_STRUCTURE.md`  
Contract: `OPERATOR_MODULE_CONTRACT.md`

This report tracks the first implementation slice for structured operator
identity, provider-aware UI metadata, and deterministic Canvas node naming.
The goal of this slice is to remove Lab-side label mutation such as `CDP: ...`
and stop deriving default node names from dotted operator IDs such as
`cdp.modify.loudness_gain`.

## Executive Status

The first cross-repository naming slice is implemented and verified.

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
  - `cmake --build build/windows-msvc-debug --target test_operator_packs --config Debug`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R operator_packs_tests --output-on-failure`
  - Result: passed

- `xyona-cdp-pack`
  - `cmake --build build/windows-msvc-debug --target test_cdp_descriptor_metadata --config Debug`
  - `ctest --test-dir build/windows-msvc-debug -C Debug -R cdp_descriptor_metadata --output-on-failure`
  - Result: passed

- `xyona-lab`
  - `cmake --build build/windows-dev --target xyona_lab_tests --config Debug`
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
- Add schema validation for Core, CDP pack, and Lab-authored operator metadata.
- Add uniqueness checks for `ui.nodeNameStem` across the discovered operator
  set.
- Add explicit `engine.materialization` coverage for all operators rather than
  relying on fallback/empty values.
- Replace minimal JSON string extraction in the pack loader with a structured
  parser once the final metadata schema stabilizes.
- Decide whether very old persisted dotted node names should be migrated or
  left unchanged as user-authored project data.

## Commit Map

To be filled by the final repository commits for this slice:

- `xyona-core`: `c809629f856e4097c6b84dbfc790b66171f6328e`
  - `feat(core): expose operator module ui identity`
- `xyona-cdp-pack`: `222b4cd4e31e2df9b89d0eac336e32b184c649a9`
  - `feat(cdp-pack): publish operator ui name stems`
- `xyona-lab`: `bcb40d3223740afe06f6a7addc2db694e2793659`
  - `feat(lab): name operator nodes from ui stems`
- Workspace root: this report commit plus the updated `xyona-cdp-pack`
  gitlink.
