# Report: Parameter Automation System Technical Review

Date: 2026-05-01
Branch: `parameter-automation-review`
Roadmap reviewed: `ROADMAP_PARAMETER_AUTOMATION_SYSTEM.md`
Repositories audited: workspace root, `xyona-core`, `xyona-lab`, `xyona-cdp-pack`
Implementation status: not started

## Verdict

The roadmap identifies the right high-value problem: parameter automation mixes
native/plain values and normalized `0..1` values. The direction is broadly
correct: explicit value domains, one codec, target-aware timeline/MIDI/
modulation paths, and prepared runtime automation are the right architecture.

It is not technically safe to implement the roadmap in its current form.
Several milestones depend on missing design decisions or incorrect integration
assumptions. Starting the requested branch-by-branch implementation now would
create churn in all three active repositories before the contract is precise
enough to preserve patch compatibility.

## Blocking Findings

### B1 - Roadmap branch metadata is wrong

The roadmap declares:

- `Branch: operator-slot-system`

That is the completed slot-system branch name, not a parameter automation
branch. The suggested milestone branch names later in the document are
different. This is enough to block the requested "same-named branch" execution
because the branch name is ambiguous at the top-level contract point.

Required correction:

- Declare one canonical implementation branch family or explicitly say that
  each milestone uses its own branch.
- Keep the same branch name across every repository only for the milestones
  that actually touch those repositories.

### B2 - M1 migration cannot be done in `ProjectState` as written

M1.5 says legacy lanes should be converted on load based on the resolved target
descriptor. The current persistence layer reads timeline lanes from
`ProjectState`, which does not have descriptor/discovery context. Target
resolution lives above it in Lab/Canvas/discovery territory.

Current facts:

- `ProjectState` stores automation target node and param id, then rebuilds the
  scalar segment document from stored point values.
- The loader has no reliable access to pack availability, descriptor revisions,
  operator ids, or slot topology at that point.

Required correction:

- Split migration into a persistence-safe schema marker and a descriptor-aware
  post-load reconciliation pass.
- For unresolved targets, preserve raw values and explicit migration status
  without attempting conversion in the low-level state reader.

### B3 - M1 depends on descriptor lookup but the recorder/playback API has no
semantic resolver

The planned fix says the recorder converts plain to normalized and playback
converts normalized to plain. The current `AutomationRecorder` only receives a
lane id resolver and point appender; `AutomationPlaybackEngine` only receives
lanes and a `ParameterControlHub`. Neither component has a parameter descriptor
or semantic lookup dependency.

Required correction:

- Introduce an explicit resolver interface before changing the stored value
  domain.
- Define behavior for missing descriptors, stale descriptors, and topology/
  slot-scoped targets.
- Add tests for resolver failure paths before data migration.

### B4 - Core codec ownership is right, but the proposed `ParamSemantics` shape
is not pack ABI complete

Moving the deterministic codec into `xyona-core` is the right boundary. However,
M2 does not define how scale/step/control/smoothing policy moves through the
pack ABI. CDP currently has `ui.scale` and `ui.step` in generated metadata JSON,
while Core loads pack params into `ParamDesc` without first-class semantic
fields.

Required correction:

- Decide whether semantic policy becomes `ParamDesc` fields, sidecar metadata,
  or a versioned pack ABI extension.
- Define old-pack behavior and missing-metadata defaults.
- Add ABI/version tests before Lab consumes pack semantics as authoritative.

### B5 - "No conversion path bypasses the codec" is too broad for one M3
acceptance gate

Lab currently has conversion logic in:

- `ParamFormatter`
- `ParamTextFieldView::FormatConfig`
- `CanvasParamModel`
- Canvas mini parameter gestures
- MIDI mapping
- modulation math
- legacy `Parameter` model helpers

The M3 acceptance criterion requires eliminating every bypass by the end of M3,
but the commit list leaves modulation semantics to M8 and runtime target work
to M6. That sequencing is inconsistent.

Required correction:

- Define an allowed transitional compatibility list.
- Move modulation/MIDI/runtime conversion acceptance to the milestones that
  actually touch those paths.
- Add a guardrail test or static inventory test only after all planned call
  sites are migrated.

### B6 - Topology policy cannot be enforced only at the hub

M4.4 says `ParameterControlHub`/target resolver rejects invalid ordinary control
writes. The hub currently sees `ParamAddress` and raw values, not descriptors or
operator policy. Putting descriptor knowledge into the hub would make it a
policy registry and risks duplicating Canvas/discovery responsibilities.

Required correction:

- Enforce target eligibility at target selection and prepared-target compile
  time.
- Keep the hub as value arbitration unless a narrow, descriptor-backed target
  policy provider is explicitly injected.
- Define how existing invalid lanes/routes/mappings load disabled without
  silently changing project state.

### B7 - M5 runtime automation conflicts with existing automation event path

`AudioGraphProcessor` already has an automation event application path that
writes parameter updates by hash. M5 introduces prepared automation runtime in
the audio/offline processor, but does not define whether the existing event path
is removed, replaced, or becomes a compatibility adapter.

Required correction:

- Inventory current automation event producers.
- Define one authoritative runtime source.
- State the ordering relative to parameter queue, manual base state,
  modulation, and offline graph snapshots in terms of the existing processor
  APIs, not only target architecture.

### B8 - M7 is necessary but should move earlier for target identity

The roadmap correctly notes that modulation and MIDI do not persist full
`ParamAddress`. But M1 and M4 already need full target identity for policy,
legacy migration, and slot safety. Deferring slot-aware target identity to M7
means earlier migrations may encode incomplete target state.

Required correction:

- Introduce full `ParamAddress` storage as an early compatibility foundation,
  at least for any path touched by M1-M4.
- Keep old node+param fields as migration input only.

## Confirmed Correct Roadmap Claims

### F0 automation value-domain mismatch is real

Verified current behavior:

- `AutomationRecorder` writes `event.baseValue` directly into
  `TimelineAutomationPoint::value`.
- `AutomationPlaybackEngine` reads the lane source value and passes it directly
  to `ParameterControlHub::setAutomationBase`.
- Timeline parameter automation signal sources declare `Unipolar01` and attach
  scalar evaluation with unipolar normalization.

This confirms the main bug: stored point values are not self-describing and
different paths treat them as different domains.

### F1 `ParamDesc` is not enough for high-end parameter semantics

`ParamDesc` has type, range, default, enum values, unit/display/precision,
availability, topology, and scope support. It does not carry canonical scale,
step, automation/modulation/MIDI policy, smoothing ownership, or parse/format
policy.

### F2 Lab has multiple conversion implementations

Verified conversion logic exists outside a single canonical codec, including
the text field view and MIDI mapping path.

### F3 CDP pack has richer parameter metadata than Lab consumes

CDP pack `op.yaml` and generated metadata contain `ui.step` and `ui.scale`,
including `linear_db`. Core currently maps pack params into `ParamDesc` without
first-class semantic fields for those facts.

### F5 slot identity gap is real

`ParamAddress` supports optional `slotIndex`, but `ModulationRoute` and
`MidiMapping` persist target node plus param name only. The prepared modulation
runtime can carry a full `ParamAddress`, but the route source data has already
lost slot identity.

## Required Roadmap Rewrite Before Implementation

Recommended replacement structure:

1. `M0` - Baseline characterization and report-only review cleanup.
2. `M1a` - Add resolver interfaces and automation lane value-domain schema only.
3. `M1b` - Fix new recording/playback for resolved targets; keep legacy lanes
   read-only/compat until descriptor-aware migration exists.
4. `M1c` - Descriptor-aware post-load migration with explicit unresolved and
   ambiguous statuses.
5. `M2` - Core codec plus semantic contract and ABI transport decision.
6. `M3` - Lab resolver and narrow surface migration with an explicit
   transitional bypass list.
7. `M4` - Full `ParamAddress` persistence for automation, modulation, and MIDI.
8. `M5` - Pack semantic consumption and target policy enforcement.
9. `M6` - Authoritative audio/offline automation runtime and replacement plan
   for existing automation events.
10. `M7+` - Compiled targets, nonlinear modulation modes, smoothing, macros,
    value sources, and diagnostics.

## Implementation Decision

No implementation branches were created in `xyona-core`, `xyona-lab`, or
`xyona-cdp-pack` for this roadmap review because the roadmap did not pass the
strict correctness/implementability gate requested by the user.

## Commit Tracking

This report is a review artifact. The report-only commit cannot record its own
final hash without changing that hash; the final assistant response should cite
the commit hash after the commit is created.
