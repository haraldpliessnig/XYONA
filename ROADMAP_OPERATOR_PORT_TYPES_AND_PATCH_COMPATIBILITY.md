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

Status: in progress.

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

## Phase 2: CDP Pack Typed Port Metadata

Status: pending.

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

## Phase 3: Lab Public Operators And Discovery

Status: pending.

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

## Phase 4: Canvas Port Identity And Compatibility Service

Status: pending.

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

## Phase 5: GraphBuilder Runtime Guardrail

Status: pending.

Deliverables:

- GraphBuilder revalidates compatibility before execution.
- Realtime and offline paths share the same compatibility semantics.
- Typed-data merge/source constraints are enforced.

Exit criteria:

- Non-UI construction paths cannot execute invalid cross-domain edges.
- Error messages identify source port type, target port type, and blocking
  rule.

## Phase 6: Visual Tokens And UX Polish

Status: pending.

Deliverables:

- Central Lab port visual token registry.
- Port colors/icons/tooltips derived from type facts.
- Cable styling aligned with port type.
- Header runtime stripes remain separate from port-type visuals.

Exit criteria:

- No individual renderer hardcodes port type colors.
- Incompatible targets are visually unavailable during drag.

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
