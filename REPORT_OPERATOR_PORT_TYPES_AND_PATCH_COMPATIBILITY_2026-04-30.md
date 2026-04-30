# Report: Operator Port Types And Patch Compatibility

**Date:** 2026-04-30
**Branch:** `operator-port-types-contract`
**Roadmap:** `ROADMAP_OPERATOR_PORT_TYPES_AND_PATCH_COMPATIBILITY.md`
**Contract:** `OPERATOR_PORT_TYPE_AND_COMPATIBILITY_CONTRACT.md`

## Summary

This work formalizes XYONA operator patching as an explicit descriptor-port
contract. The goal is to stop relying on implicit audio defaults, generic
Canvas port names, tags-only classification, or operator-domain guesses.

## Decisions

- There is no legacy project compatibility mode.
- Missing public operator port types are errors.
- Patch compatibility is based on source and target port facts.
- Operator domain remains a scheduling/semantic fact, not the only connection
  rule.
- Lab renders and enforces port compatibility but does not invent missing port
  metadata.
- Packs may add namespaced concrete port types that map to known broad kinds.

## Phase 0 Status

Completed.

Completed in this phase:

- Added root workspace contract:
  `OPERATOR_PORT_TYPE_AND_COMPATIBILITY_CONTRACT.md`
- Updated root:
  - `AGENTS.md`
  - `OPERATOR_MODULE_CONTRACT.md`
  - `OPERATOR_MODULE_AUTHORING_GUIDE.md`
- Added Core implementation contract:
  `xyona-core/docs/OPERATOR_PORT_TYPES.md`
- Updated Core:
  - `xyona-core/AGENTS.md`
  - `xyona-core/OPERATOR_MODULE_AUTHORING_GUIDE.md`
- Added Lab implementation contracts:
  - `xyona-lab/docs/subsystems/canvas/CANVAS_PORT_TYPES_AND_PATCH_COMPATIBILITY.md`
  - `xyona-lab/docs/subsystems/ui/OPERATOR_PORT_VISUAL_TOKENS.md`
- Updated Lab:
  - `xyona-lab/AGENTS.md`
  - `xyona-lab/OPERATOR_MODULE_AUTHORING_GUIDE.md`
- Added CDP implementation contract:
  `xyona-cdp-pack/docs/CDP_PORT_TYPES.md`
- Updated CDP pack:
  - `xyona-cdp-pack/AGENTS.md`
  - `xyona-cdp-pack/OPERATOR_MODULE_AUTHORING_GUIDE.md`

## Current Technical Findings

Core:

- `IODesc` currently carries `id`, `channels`, and `tags`.
- `IODesc`, `VariablePortRangeDesc`, and `PortDesc` now carry canonical
  namespaced port `type` plus optional compatibility facts for `kind`,
  `domain`, `rate`, `schema`, `format`, `channelPolicy`, `mergePolicy`, and
  `executionContext`.
- The Core operator-module validator now checks explicit `type` for fixed and
  variable public ports.
- Core codegen now transports port type facts from `op.yaml` into runtime
  `OpDesc` descriptors.
- Core runtime descriptor tests now compare port type facts against `op.yaml`.
- The current Core `op.yaml` set now declares:
  - `xyona.audio.signal` for audio ports
  - `xyona.control.cv` for Core signal/CV ports

CDP pack:

- PVOC typed-data metadata already carries schema/format-like facts in port
  metadata JSON.
- Audio ports and many non-PVOC CDP ports do not yet expose canonical
  `xyona.audio.signal` type facts through a shared field.

Lab:

- Lab public operator specs currently list port IDs without explicit type
  fields.
- Canvas/GraphBuilder compatibility still needs a central service.

## Verification

Completed:

```text
git diff --check
C:\Python3.9.5\python.exe tools\operator_modules\test_validate_operator_modules.py
C:\Python3.9.5\python.exe tools\operator_modules\validate_operator_modules.py --root .
cmake --build build/windows-msvc-debug --target test_operator_module_runtime test_operator_packs test_signal_processes --config Debug
ctest --test-dir build/windows-msvc-debug -C Debug -R "operator_module_runtime_tests|operator_module_metadata_tests|operator_module_validator_guardrail_tests|operator_packs_tests" --output-on-failure
ctest --test-dir build/windows-msvc-debug -C Debug -R "signal_process_tests" --output-on-failure
```

Result:

- Passed in Root.
- Passed in `xyona-core`.
- Passed in `xyona-lab`.
- Passed in `xyona-cdp-pack`.
- Core operator module validator guardrail tests passed: 7 tests.
- Core operator module validation passed: 16 `op.yaml` records.
- Core targeted CTest passed: 4 tests, 0 failures.
- Core signal process CTest passed: 1 test, 0 failures.

Notes:

- Existing Windows line-ending warnings are present.
- No whitespace errors were reported.

## Open Risks

- Making validator failure immediate will expose every untyped public operator
  at once. That is correct architecturally, but the implementation should be
  staged so each repo can be made green before moving to the next layer.
- `IODesc` is marked deprecated but still consumed in Lab and pack discovery.
  The bridge from `IODesc` to richer port type facts must be deliberate.
- CDP PVOC currently uses schema string `xyona.cdp.pvoc.analysis.v1` in some
  metadata. The new canonical type proposal uses `cdp.pvoc.analysis.v1`; the
  implementation needs one explicit mapping decision rather than silent drift.

## Next Step

Continue with Phase 2/bridge preparation:

- repeat explicit typing work for CDP pack metadata generation
- map CDP PVOC metadata to canonical type `cdp.pvoc.analysis.v1`
- update Lab public operator specs and runtime metadata to carry explicit
  type facts
- then implement Lab connection compatibility against these descriptor facts
