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
- Port visuals do not include icons/glyphs. Port differentiation is via central
  color/stroke/shape, tooltip text, and cable styling.
- Future multicore/bundled cables require an explicit graph/serialization
  model; visual thickness is prepared centrally but bundling semantics are not
  inferred.

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

- All public CDP `op.yaml` ports now declare explicit type facts.
- Audio CDP ports use `xyona.audio.signal`.
- PVOC typed-data ports use canonical port type `cdp.pvoc.analysis.v1` and
  payload schema `xyona.cdp.pvoc.analysis.v1`.
- Generated CDP port metadata keeps `xyona.schema=port_meta` as the envelope
  marker and emits typed-data payload schema as `xyona.dataSchema`.
- Core pack loading maps generated pack port metadata into `IODesc` and
  `PortDesc`, so Lab can consume CDP port facts without parsing CDP-private
  source files.

Lab:

- Lab public operator specs now declare explicit port types.
- Lab CustomOperator runtime descriptors now use typed port factory helpers for
  audio, CV, gate, and clock ports.
- Lab custom operator registration rejects incomplete public port type
  metadata.
- Lab DiscoveryService filters incomplete descriptors out of normal
  palette/discovery results.
- Canvas/GraphBuilder compatibility still needs a central service.

## Phase 2 Status

Completed.

Completed in this phase:

- Updated CDP `op.yaml` files with explicit port `type`.
- Updated CDP generator to emit port type facts for audio and PVOC typed-data
  ports.
- Regenerated CDP operator metadata.
- Extended CDP descriptor metadata tests to assert descriptor and metadata port
  type facts.
- Updated Core pack loader so V2 pack port metadata populates `IODesc` and
  `PortDesc`.
- Documented the CDP distinction between canonical port type
  `cdp.pvoc.analysis.v1` and payload schema `xyona.cdp.pvoc.analysis.v1`.

## Phase 3 Status

Completed.

Completed in this phase:

- Updated `xyona-lab/specs/operators/lab-public.op.yaml` so every public Lab
  operator port declares a type.
- Added Lab CustomOperator port factory helpers for:
  - `xyona.audio.signal`
  - `xyona.control.cv`
  - `xyona.control.gate`
  - `xyona.control.clock`
- Replaced Lab-authored raw `IODesc` port construction with typed helpers.
- Extended Lab custom operator registration and DiscoveryService to reject or
  skip incomplete public port type metadata.
- Extended Lab runtime metadata tests to compare spec port IDs/types against
  Discovery descriptors.

## Phase 4 Status

Complete.

Completed in this phase slice:

- Added Lab `ConnectionCompatibility`, a central descriptor-port compatibility
  service.
- Added Lab `PortIdentity`, a central visible-port-ID helper for descriptor
  ports and channel expansion.
- `NodeData`, `NodeBinder`, and Canvas topology refresh now carry descriptor
  visible port IDs for rendering, hit-testing, and anchors.
- Canvas anchors are side-aware when needed, so an operator can legally reuse a
  descriptor ID such as `pvoc` on input and output without drawing cables from
  the wrong side.
- Wired Canvas `createConnection()` through that service, so command/undo and
  direct programmatic connection creation share the same blocking rule.
- Wired drag hover/highlighting and mouse-up connection creation through the
  same service, so incompatible targets are not presented as valid drag
  targets.
- Added `single_source` target enforcement for descriptor-backed inputs.
- Updated project connection import so descriptor-backed edges are validated by
  the same Canvas connection path instead of being limited to generic
  `out_N -> in_N` port names.
- Updated Generic node rendering and hit-testing to use visible descriptor
  port IDs instead of local generic aliases for descriptor-backed operators.
- Removed unreachable disabled flow-overlay code in `PatchCableOverlay`, which
  eliminated the C4702 build warning without changing cable rendering behavior.
- Corrected Lab signal selector/provider/CV sink contract ports that carry
  scalar CV values to `xyona.control.cv`.
- Typed older test-only fake descriptors that participate in Canvas
  connections, so tests no longer rely on implicit audio fallbacks.
- Added focused Canvas connection tests for valid audio, invalid audio/CV,
  valid PVOC typed data, invalid PVOC-to-audio, and invalid audio-to-PVOC
  edges.
- Added focused anchor tests proving descriptor IDs like `out` and `in`
  resolve without `out_0`/`in_0` aliases, and reused IDs like `pvoc` resolve
  correctly on both input and output sides.

## Phase 5 Status

Complete.

Completed in this phase slice:

- Realtime `GraphBuilder` and `OfflineGraphBuilder` now revalidate descriptor
  compatibility before building adjacency and wires.
- Analyzer observer extraction and analyzer-only live closure use the same
  compatibility guard.
- Runtime guardrail diagnostics include source node/port, target node/port,
  concrete source/target port types, and the blocking rule.

## Phase 6 Status

Technical scaffold complete; final differentiated palette pending.

Completed in this phase slice:

- Added Lab `PortVisuals`, a central descriptor-backed port visual registry in
  `xyona-lab/src/app/lab/canvas/ports/`.
- `NodeData`, `NodeBinder`, Canvas topology refresh, and descriptor test
  helpers now carry `PortVisualFacts` beside visible descriptor port IDs.
- Generic node port rendering asks the registry for neutral port fill/outline
  tokens instead of hardcoding per-renderer port visuals.
- `PatchCableOverlay` asks the registry for cable color/thickness tokens. The
  current palette intentionally preserves the existing neutral cable look.
- Canvas exposes port and connection tooltips derived from descriptor facts:
  type, kind, domain, rate, schema, format, merge policy, and compatibility
  hint.
- The registry has a reserved `laneCount -> cableThicknessScale` hook for
  future multicore/bundled cables. Current connections use lane count 1.
- Port icons/glyphs are explicitly out of scope.
- Phase 6 keeps the current neutral port/cable look. It changes ownership and
  data flow, not the visible palette.

## Phase 7 Status

Foundation complete.

Completed in this phase slice:

- Extended Lab `Connection` with optional multicore lane pairs while preserving
  legacy single-lane aggregate construction and serialization.
- Canvas validates every lane atomically through `ConnectionCompatibility` and
  rejects duplicate or incompatible bundled lanes without partial creation.
- Project connection export/import now round-trips explicit `lanes` arrays.
- `PatchCableOverlay` renders and hit-tests multicore as one cable and derives
  cable thickness from lane count through `PortVisualRegistry`.
- Realtime and offline GraphBuilder paths expand bundled lanes to normal
  per-port wires before adjacency, wire routing, observer extraction, and
  typed-data edge handling.
- Tests cover descriptor-backed multicore validation, invalid lane rejection,
  serialization round-trip, overlay hit-testing, and slot-based GraphBuilder
  wire expansion.

Remaining product work:

- Add user-facing cable creation gestures for slot groups.
- Add descriptor/UX rules for automatic lane grouping beyond explicit port IDs.

## Verification

Completed:

```text
git diff --check
C:\Python3.9.5\python.exe tools\operator_modules\test_validate_operator_modules.py
C:\Python3.9.5\python.exe tools\operator_modules\validate_operator_modules.py --root .
cmake --build build/windows-msvc-debug --target test_operator_module_runtime test_operator_packs test_signal_processes --config Debug
ctest --test-dir build/windows-msvc-debug -C Debug -R "operator_module_runtime_tests|operator_module_metadata_tests|operator_module_validator_guardrail_tests|operator_packs_tests" --output-on-failure
ctest --test-dir build/windows-msvc-debug -C Debug -R "signal_process_tests" --output-on-failure
C:\Python3.9.5\python.exe scripts\validate_operator_modules.py
C:\Python3.9.5\python.exe scripts\generate_operator_metadata.py --check
cmake --build build/windows-msvc-debug --target xyona_pack_cdp_ops test_cdp_descriptor_metadata test_cdp_spectral_contract test_cdp_pack test_cdp_pack_env_discovery --config Debug
ctest --test-dir build/windows-msvc-debug -C Debug -R "cdp_generated_operator_metadata_tests|cdp_operator_module_metadata_tests|cdp_descriptor_metadata_tests|cdp_spectral_contract_tests|cdp_pack_loader_tests|cdp_pack_env_discovery_tests" --output-on-failure
cmake --build build/windows-dev --target xyona_lab_tests --config Debug
ctest --test-dir build/windows-dev -C Debug -R lab_operator_module_metadata_tests --output-on-failure
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Operator Module Spec Runtime" --xyona-only --summary-only
$env:XYONA_OPERATOR_PACK_PATH='D:\GITHUB\XYONA\xyona-cdp-pack\build\windows-msvc-debug\Debug'; build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Connection System" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Overlay Visual" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Wire Routing" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="GridSourceHostAdapter" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="GridActionFilterHostAdapter" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="GridValueHostAdapter" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Signal" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Adapter Lifetime" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="AudioEngineManager Minimal Plan" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Stage 11 - AudioEngineManager Integration" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Audio Routing Integration" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="BusAccumulator" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Connection Persistence" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="DeleteNodeCommand Tests" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Canvas Param Persistence" --xyona-only --summary-only
build\windows-dev\tests\Debug\xyona_lab_tests.exe --test="Canvas Stress Suite" --xyona-only --summary-only
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
- CDP operator module validation passed: 16 `op.yaml` records.
- CDP generated metadata check passed.
- CDP targeted CTest passed: 6 tests, 0 failures.
- Lab operator module validation passed: 17 `op.yaml` records.
- Lab operator module metadata CTest passed.
- Lab `Operator Module Spec Runtime` passed: 1 test, 513 passes.
- Lab `CDP Pack Canvas Smoke` passed with `XYONA_OPERATOR_PACK_PATH` set to the
  CDP debug pack folder: 14 tests, 410 passes.
- Lab `Connection System` passed: 24 tests, 82 passes.
- Lab `Overlay Visual` passed: 9 tests, 20 passes.
- Lab `Wire Routing` passed: 8 tests, 27 passes.
- Lab `AudioEngineManager Minimal Plan` passed: 38 tests, 566 passes.
- Lab `Canvas Stress Suite` passed: 3 tests, 3004 passes.
- Lab `Connection Persistence` passed: 5 tests, 19 passes.
- Lab targeted Canvas/connection-adjacent tests passed:
  `GridSourceHostAdapter`, `GridActionFilterHostAdapter`,
  `GridValueHostAdapter`, `Signal`, `Adapter Lifetime`,
  `AudioEngineManager Minimal Plan`, `Stage 11 - AudioEngineManager
  Integration`, `Audio Routing Integration`, `BusAccumulator`,
  `Connection Persistence`, `DeleteNodeCommand Tests`, `Overlay Visual`,
  `Canvas Param Persistence`, and `Canvas Stress Suite`.

Notes:

- Existing Windows line-ending warnings are present.
- No whitespace errors were reported.
- A full unfiltered `xyona_lab_tests --xyona-only --summary-only` run was
  attempted and timed out after 10 minutes; targeted affected suites above
  completed successfully.

## Open Risks

- Making validator failure immediate will expose every untyped public operator
  at once. That is correct architecturally, but the implementation should be
  staged so each repo can be made green before moving to the next layer.
- `IODesc` is marked deprecated but still consumed in Lab and pack discovery.
  The bridge from `IODesc` to richer port type facts must be deliberate.
- Builder validation currently skips invalid edges and logs diagnostics. If a
  future caller needs a hard plan-build failure, that should be added as an
  explicit policy above the shared compatibility check.
- Multicore/bundled cable model is present, but there is not yet a user-facing
  slot-group gesture or descriptor-driven automatic grouping policy.

## Next Step

Define multicore UX:

- how a user creates a bundled cable from slot groups
- how bundled lanes are shown/edited/removed in the inspector
- how descriptors advertise recommended lane groups beyond explicit port IDs
