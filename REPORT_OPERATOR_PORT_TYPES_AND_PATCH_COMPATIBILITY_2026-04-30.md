# Report: Operator Port Types And Patch Compatibility

**Date:** 2026-04-30
**Branch:** `port-type-taxonomy`
**Roadmap:** `ROADMAP_OPERATOR_PORT_TYPES_AND_PATCH_COMPATIBILITY.md`
**Contract:** `OPERATOR_PORT_TYPE_AND_COMPATIBILITY_CONTRACT.md`

## Summary

This work formalizes XYONA operator patching as an explicit descriptor-port
contract. The goal is to stop relying on implicit audio defaults, generic
Canvas port names, tags-only classification, or operator-domain guesses.

The current built-in taxonomy is `xyona.audio`, `xyona.signal`,
`xyona.signal.cv`, `xyona.signal.gate`, `xyona.signal.clock`, and
`xyona.midi.*`.

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
  - `xyona.audio` for audio ports
  - `xyona.signal` for generic non-audio signal streams
  - `xyona.signal.cv` for Core CV signal ports

CDP pack:

- All public CDP `op.yaml` ports now declare explicit type facts.
- Audio CDP ports use `xyona.audio`.
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
- Updated Core pack loader so versioned pack port metadata populates `IODesc`
  and `PortDesc`.
- Documented the CDP distinction between canonical port type
  `cdp.pvoc.analysis.v1` and payload schema `xyona.cdp.pvoc.analysis.v1`.

## Phase 3 Status

Completed.

Completed in this phase:

- Updated `xyona-lab/specs/operators/lab-public.op.yaml` so every public Lab
  operator port declares a type.
- Added Lab CustomOperator port factory helpers for:
  - `xyona.audio`
  - `xyona.signal`
  - `xyona.signal.cv`
  - `xyona.signal.gate`
  - `xyona.signal.clock`
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
- Removed unreachable disabled flow-overlay code in the then-current cable renderer, which
  eliminated the C4702 build warning without changing cable rendering behavior.
- Corrected Lab signal selector/provider/CV sink contract ports that carry
  scalar CV values to `xyona.signal.cv`.
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
- Cable rendering asks `PortVisualRegistry` for cable color/thickness tokens.
  The current palette intentionally preserves the existing neutral cable look.
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
  existing single-lane aggregate construction and serialization.
- Canvas validates every lane atomically through `ConnectionCompatibility` and
  rejects duplicate or incompatible bundled lanes without partial creation.
- Project connection export/import now round-trips explicit `lanes` arrays.
- Canvas cable rendering renders and hit-tests multicore as one cable and derives
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

## Phase 8 Status

Canvas cable layer cleanup complete.

Completed in this phase slice:

- Removed Lab's app-wide transparent `PatchCableOverlay` component and
  `MainComponent` cable overlay ownership.
- Removed the obsolete multi-provider `AnchorRegistry`; Sidebar and
  ParameterBar are not patch surfaces.
- Added Canvas-owned `CanvasCableRenderer`, a non-component helper that draws
  and hit-tests cables from the Canvas paint path.
- Changed cable anchor coordinates to Canvas-local screen coordinates.
- Preserved drag-to-connect, hover/selection, compatible target hover, focus
  highlighting, endpoint detach, right-click cable context menu, debug anchor
  rects, multicore cable hit-testing, and descriptor-backed cable visual token
  usage.
- Removed cable hover tooltips/toolbox behavior; cable deletion remains
  available through both the cable context menu and cable selection plus
  Delete/Backspace.
- Updated the cable visual test surface from `Overlay Visual` to
  `Canvas Cable Visual`.

Verification for this phase slice:

- `git diff --check`
- `xyona-lab`: `git diff --check`
- `xyona-lab`: `./build-dev.sh`
- `xyona-lab`: `./build/macos-dev/tests/xyona_lab_tests --test="Canvas Cable Visual" --xyona-only --summary-only`
- `xyona-lab`: `./build/macos-dev/tests/xyona_lab_tests --test="Connection System" --xyona-only --summary-only`

## Phase 9 Status

Built-in port taxonomy complete.

Completed in this phase slice:

- Replaced the public built-in port vocabulary across Core, Lab, CDP pack, and
  root documentation with:
  - `xyona.audio`
  - `xyona.signal`
  - `xyona.signal.cv`
  - `xyona.signal.gate`
  - `xyona.signal.clock`
  - `xyona.midi.*`
- Removed old public type IDs from source specs, descriptors, generated CDP
  metadata, tests, validators, visual tokens, Canvas compatibility rules, and
  docs.
- Added `xyona.signal` as the generic non-audio signal stream type in the root
  contract, Core validator vocabulary, Lab Canvas compatibility, and Lab port
  visual registry.
- Updated Core pack metadata loading so pack ports using `xyona.audio`,
  `xyona.signal`, and concrete signal subtypes map to the correct host-neutral
  `PortKind` and `SignalKind`.
- Added dedicated audio outputs on audio-capable signal generators:
  `signal_lfo`, `signal_noise`, `signal_dust`, `signal_velvet`, and
  `signal_crackle` now expose `out_0` as `xyona.signal.cv` and `out_1` as
  `xyona.audio`.
- Signal generator processing computes each sample once and writes it to the
  CV and audio buffers only when those buffers are present.
- Lab graph processing now allocates per-node output scratch buffers only for
  ports demanded by downstream wires or observer taps.
- Lab's Core host adapter omits disconnected multi-output Core port groups
  from `ProcessContext`, so dual outputs such as `out_1` audio are not cooked
  when not connected.
- Single-output Core operators keep the trash-buffer fallback for
  `ctx.output("out")` safety.
- Updated Core signal operator README/help docs and Lab boundary tests for the
  dual-output contract.

Verification for this phase slice:

- Workspace/root/Core/Lab/CDP: `git diff --check`
- Workspace retired public type ID sweeps across non-build files.
- `xyona-core`: `./.venv/bin/python tools/operator_modules/validate_operator_modules.py --root .`
- `xyona-core`: `./.venv/bin/python tools/operator_modules/test_validate_operator_modules.py`
- `xyona-core`: `cmake --build build/macos-clang-debug --target test_signal_processes`
- `xyona-core`: `build/macos-clang-debug/tests/test_signal_processes`
- `xyona-lab`: `cmake --build build/macos-dev --target xyona_lab_tests`
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="CoreOperatorHostAdapter" --xyona-only --summary-only`
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --xyona-only --summary-only`
- `xyona-lab`: `build/macos-dev/tests/xyona_lab_tests --xyona-only --summary-only`
- `xyona-cdp-pack`: `../xyona-core/.venv/bin/python scripts/validate_operator_modules.py --root .`
- `xyona-cdp-pack`: `../xyona-core/.venv/bin/python scripts/generate_operator_metadata.py --check`
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug --target xyona_pack_cdp_ops`
- `xyona-cdp-pack`: `cmake --build build/macos-clang-debug --target test_cdp_descriptor_metadata`
- `xyona-cdp-pack`: `ctest --test-dir build/macos-clang-debug --output-on-failure`

Result:

- Core operator module validation passed: 16 `op.yaml` records.
- Core operator module validator guardrail tests passed: 7 tests.
- Core signal process tests passed.
- Root/Core/Lab/CDP `git diff --check` passed.
- Retired public type ID sweeps returned no matches.
- Lab `CoreOperatorHostAdapter` passed: 4 tests, 136 passes, 0 failures.
- Lab `AudioEngineManager Minimal Plan` passed: 38 tests, 566 passes,
  0 failures.
- Lab `xyona_lab_tests --xyona-only --summary-only` passed: 1191 tests,
  944300 passes, 0 failures.
- CDP operator module validation passed: 16 `op.yaml` records.
- CDP generated metadata check passed.
- CDP pack CTest passed: 21 tests, 0 failures.
- Lab optional CDP Pack Canvas Smoke and SOFA smoke cases were skipped in the
  full Lab run because `XYONA_OPERATOR_PACK_PATH` and `XYONA_TEST_SOFA_PATH`
  were not set for that invocation. CDP pack behavior was verified separately
  in the CDP pack repo.

## Verification

Completed for the current `port-type-taxonomy` branch on macOS:

```text
git diff --check
./.venv/bin/python tools/operator_modules/validate_operator_modules.py --root .
./.venv/bin/python tools/operator_modules/test_validate_operator_modules.py
cmake --build build/macos-clang-debug --target test_signal_processes
build/macos-clang-debug/tests/test_signal_processes
../xyona-core/.venv/bin/python scripts/validate_operator_modules.py --root .
../xyona-core/.venv/bin/python scripts/generate_operator_metadata.py --check
cmake --build build/macos-clang-debug --target xyona_pack_cdp_ops test_cdp_descriptor_metadata
ctest --test-dir build/macos-clang-debug --output-on-failure
cmake --build build/macos-dev --target xyona_lab_tests
build/macos-dev/tests/xyona_lab_tests --test="CoreOperatorHostAdapter" --xyona-only --summary-only
build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager Minimal Plan" --xyona-only --summary-only
build/macos-dev/tests/xyona_lab_tests --xyona-only --summary-only
```

Result:

- Root/Core/Lab/CDP diff checks passed.
- Retired public type ID sweeps returned no matches across non-build files.
- Core operator module validation passed: 16 `op.yaml` records.
- Core operator module validator guardrail tests passed: 7 tests.
- Core signal process tests passed.
- CDP operator module validation passed: 16 `op.yaml` records.
- CDP generated metadata check passed.
- CDP pack CTest passed: 21 tests, 0 failures.
- Lab `xyona_lab_tests` build passed.
- Lab `CoreOperatorHostAdapter` passed: 4 tests, 136 passes.
- Lab `AudioEngineManager Minimal Plan` passed: 38 tests, 566 passes.
- Lab full `xyona_lab_tests --xyona-only --summary-only` passed: 1191 tests,
  944300 passes, 0 failures.

Notes:

- Lab optional CDP Pack Canvas Smoke and SOFA smoke cases were skipped in the
  full Lab run because `XYONA_OPERATOR_PACK_PATH` and `XYONA_TEST_SOFA_PATH`
  were not set for that invocation. CDP pack behavior was verified separately
  in the CDP pack repo.

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
