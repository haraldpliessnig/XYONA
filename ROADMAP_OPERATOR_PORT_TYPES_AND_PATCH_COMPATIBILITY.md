# Roadmap: Operator Port Types And Patch Compatibility

**Status:** Active
**Started:** 2026-04-30
**Branch:** `operator-port-types-contract`
**Primary contract:** `OPERATOR_PORT_TYPE_AND_COMPATIBILITY_CONTRACT.md`
**Applies to:** `xyona-core`, `xyona-lab`, `xyona-cdp-pack`, future operator
packs

## Goal

Make operator patching explicit, typed, and enforceable across descriptor
generation, pack discovery, Canvas UI, project persistence, and graph building.

The end state is:

```text
operator op.yaml -> generated descriptor -> Lab Canvas ports
                 -> central compatibility service -> GraphBuilder validation
```

No public operator port may be untyped. Lab must never guess missing port type
metadata.

## Current Problem

The current system has useful pieces but no single enforced port-type contract:

- Core has `SignalKind`, `PortKind`, `IODesc`, and `PortDesc`, but descriptor
  consumption still often flows through tag-based or legacy-compatible shapes.
- CDP PVOC typed-data metadata exists, but it is expressed through port JSON
  and tags rather than a canonical port type field used by all layers.
- Lab Canvas still has generic port naming paths such as `in_0` and `out_0`
  that can become semantic stand-ins.
- Graph building classifies edges later from descriptor tags instead of using
  one central compatibility decision.

This is not acceptable for a high-end patcher once spectral data, control data,
MIDI, future Faust/Maximilian packs, and custom packs coexist.

## Non-Goals

- No legacy project compatibility mode.
- No hardcoded exhaustive list of all future third-party formats.
- No Lab-specific port type source of truth.
- No implicit conversion between audio, spectral typed data, control, or MIDI.

## Phase 0: Contract And Agent Guardrails

Status: complete.

Deliverables:

- Root contract:
  `OPERATOR_PORT_TYPE_AND_COMPATIBILITY_CONTRACT.md`
- Root operator contract and authoring guide references.
- Repo-local guidance:
  - `xyona-core/docs/OPERATOR_PORT_TYPES.md`
  - `xyona-lab/docs/subsystems/canvas/CANVAS_PORT_TYPES_AND_PATCH_COMPATIBILITY.md`
  - `xyona-lab/docs/subsystems/ui/OPERATOR_PORT_VISUAL_TOKENS.md`
  - `xyona-cdp-pack/docs/CDP_PORT_TYPES.md`
- `AGENTS.md` references in Root, Core, Lab, and CDP-Pack.

Exit criteria:

- Agents are pointed to the contract before touching operator ports, pack
  metadata, Canvas wiring, GraphBuilder connection validation, or port visuals.
- `git diff --check` passes in all affected repos.

## Phase 1: Core Descriptor And Validator Surface

Status: complete.

Deliverables:

- Define canonical port type constants and descriptor fields in Core.
- Extend `IODesc`/`PortDesc` or introduce a host-neutral bridge that exposes:
  `type`, `kind`, `domain`, `rate`, `schema`, `format`, `channelPolicy`,
  `mergePolicy`, and `executionContext`.
- Extend Core operator-module validator to reject:
  - missing `ports.*[].type`
  - invalid type IDs
  - typed-data ports without schema/format
  - descriptor surfaces that require Lab-side guessing
- Add validator guardrail tests.

Exit criteria:

- Core validator tests cover valid audio ports and invalid missing types.
- Core descriptors can transport explicit type facts without Lab-specific code.

Progress:

- Core operator-module validator now requires `type` on fixed and variable
  public ports.
- Core validator tests cover missing port type and typed-data schema guardrails.
- Current Core operator specs declare `xyona.audio.signal` or
  `xyona.control.cv` as appropriate.
- Core `IODesc`, `VariablePortRangeDesc`, and `PortDesc` now carry explicit
  port type fields and optional typed-data compatibility facts.
- Core codegen transports port type facts from `op.yaml` into runtime `OpDesc`.
- Core runtime descriptor tests compare port type facts against `op.yaml`.

## Phase 2: CDP Pack Typed Port Metadata

Status: complete.

Deliverables:

- Update all public CDP `op.yaml` files with explicit port types.
- Use `xyona.audio.signal` for audio ports.
- Use `cdp.pvoc.analysis.v1` for PVOC typed-data ports.
- Update CDP metadata generator and generated surfaces.
- Extend CDP tests for PVOC analysis/synth compatibility metadata.

Exit criteria:

- CDP pack generation check passes.
- CDP descriptor metadata tests assert port type facts.
- CDP PVOC typed-data cannot be represented as a generic audio edge.

Progress:

- All public CDP operator ports declare explicit `type` in `op.yaml`.
- CDP audio ports use `xyona.audio.signal`.
- CDP PVOC typed-data ports use `cdp.pvoc.analysis.v1` with
  `kind=typed_data`, `domain=spectral_pvoc`, `rate=offline_artifact`,
  payload schema `xyona.cdp.pvoc.analysis.v1`, format `pvoc_analysis`, and
  `mergePolicy=single_source`.
- Generated CDP port metadata preserves `xyona.schema=port_meta` and emits the
  payload schema as `xyona.dataSchema`.
- Core pack loading maps generated pack port metadata into `IODesc` and
  `PortDesc` type facts.
- CDP descriptor metadata tests assert audio and PVOC typed-data port facts.

## Phase 3: Lab Public Operators And Discovery

Status: complete.

Deliverables:

- Update `xyona-lab/specs/operators/lab-public.op.yaml` with explicit port
  types.
- Update Lab runtime descriptor metadata tables to match specs.
- Make Lab discovery reject/quarantine incomplete descriptor port type data for
  normal palette use.
- Keep diagnostics available for development.

Exit criteria:

- Lab public operator metadata tests pass.
- No Lab-authored public operator has untyped ports.

Progress:

- `xyona-lab/specs/operators/lab-public.op.yaml` now declares explicit port
  types for all Lab-authored public operators.
- Lab CustomOperator port factories create typed audio/control/gate/clock
  descriptor ports instead of raw untyped `IODesc` records.
- Lab custom operator registration rejects descriptors with incomplete public
  port type metadata.
- Lab discovery filters incomplete descriptors out of normal palette/discovery
  results and logs the skipped operator ID.
- Lab runtime metadata tests compare spec port IDs/types against Discovery
  descriptors.

## Phase 4: Canvas Port Identity And Compatibility Service

Status: complete.

Deliverables:

- Canvas resolves and stores descriptor port IDs.
- Add central `ConnectionCompatibility` service.
- Drag highlighting uses the service.
- Connection creation and undo commands use the service.
- Project import validates persisted edges.

Exit criteria:

- Valid audio-to-audio connection works.
- Valid PVOC analysis-to-synth connection works.
- PVOC typed data to audio input is blocked.
- Audio signal to PVOC typed-data input is blocked unless the target input is
  actually an audio input on an analysis operator.

Progress:

- Added central `PortIdentity` helpers for descriptor-derived visible port IDs
  and channel expansion.
- `NodeData` now stores visible input/output port IDs derived from descriptors.
- `NodeBinder` and Canvas topology refresh populate those IDs from the
  operator contract.
- Added a central Lab `ConnectionCompatibility` service for descriptor-backed
  port resolution and default compatibility rules.
- Generic node rendering, anchor resolution, and port hit-testing now use the
  same visible descriptor IDs instead of inventing generic aliases for
  descriptor-backed ports.
- Canvas anchors carry optional side information so reused descriptor IDs such
  as `pvoc` can resolve to separate input and output anchor positions.
- Drag hover/highlighting and mouse-up connection creation now use
  `ConnectionCompatibility`, including duplicate and `single_source` input
  checks.
- Canvas `createConnection()` now rejects incompatible descriptor-backed
  edges, missing descriptor ports, missing port types, and duplicate incoming
  edges to `single_source` inputs.
- Project connection import now lets descriptor-backed nodes validate through
  `createConnection()` instead of forcing generic `out_N -> in_N` names.
- Lab signal sink/source host ports that represent CV values now use
  `xyona.control.cv` consistently.
- Tests cover:
  - audio signal -> audio signal valid
  - audio signal -> CV invalid
  - PVOC typed data -> PVOC typed data valid
  - PVOC typed data -> audio invalid
  - audio signal -> PVOC typed data invalid

## Phase 5: GraphBuilder Runtime Guardrail

Status: complete.

Deliverables:

- GraphBuilder revalidates compatibility before execution.
- Realtime and offline paths share the same compatibility semantics.
- Typed-data merge/source constraints are enforced.

Exit criteria:

- Non-UI construction paths cannot execute invalid cross-domain edges.
- Error messages identify source port type, target port type, and blocking
  rule.

Progress:

- Realtime `GraphBuilder` and `OfflineGraphBuilder` revalidate descriptor
  compatibility before building adjacency and wires.
- Observer extraction and analyzer-only live closure use the same validation
  guard.
- Guardrail logs source node/port, target node/port, concrete source/target
  port type pair, and the blocking rule.

## Phase 6: Visual Tokens And UX Polish

Status: technical scaffold complete; final differentiated palette pending.

Deliverables:

- Central Lab port visual token registry.
- Port colors, labels, and tooltips derived from type facts.
- Cable styling aligned with port type.
- Multicore/bundled cable thickness reserved in the central visual registry;
  actual bundled connection semantics require a separate graph-model plan.
- Header runtime stripes remain separate from port-type visuals.
- No port icons/glyphs. Port visuals use geometry, color/stroke, tooltips, and
  cable styling only.

Exit criteria:

- No individual renderer hardcodes port type colors.
- Incompatible targets are visually unavailable during drag. Done by Phase 4
  compatibility hover checks; Phase 6 still owns type-derived visual language.

Progress:

- Lab now has `PortVisuals.h` in `src/app/lab/canvas/ports/` with
  descriptor-backed port facts, visual-family classification, neutral palettes,
  tooltip text, and a future lane-count thickness hook.
- Generic node rendering and `PatchCableOverlay` consume the registry instead
  of deriving port/cable styling locally.

## Verification Matrix

Run repo-local checks. A root workspace status or build is not sufficient.

Core:

```powershell
C:\Python3.9.5\python.exe tools\operator_modules\validate_operator_modules.py --root .
C:\Python3.9.5\python.exe tools\operator_modules\test_validate_operator_modules.py
ctest --test-dir build/windows-msvc-debug -C Debug -R "operator_module_runtime_tests|operator_module_metadata_tests|operator_module_validator_guardrail_tests|operator_packs_tests" --output-on-failure
git diff --check
```

CDP pack:

```powershell
C:\Python3.9.5\python.exe scripts\generate_operator_metadata.py --check
C:\Python3.9.5\python.exe scripts\validate_operator_modules.py
ctest --test-dir build/windows-msvc-debug -C Debug -R "cdp_generated_operator_metadata_tests|cdp_operator_module_metadata_tests|cdp_descriptor_metadata_tests|cdp_spectral_contract_tests|cdp_pack_loader_tests|cdp_pack_env_discovery_tests" --output-on-failure
git diff --check
```

Lab:

```powershell
C:\Python3.9.5\python.exe scripts\validate_operator_modules.py
ctest --test-dir build/windows-dev -C Debug -R lab_operator_module_metadata_tests --output-on-failure
build/windows-dev/tests/Debug/xyona_lab_tests.exe --test="CDP Pack Canvas Smoke" --xyona-only --summary-only
git diff --check
```

## Reporting

Update `REPORT_OPERATOR_PORT_TYPES_AND_PATCH_COMPATIBILITY_2026-04-30.md`
after each completed phase with:

- repos touched
- files changed
- verification run
- decisions made
- remaining risks
