# Post-Roadmap Fix Index

This index tracks bugs and corrective changes discovered after a roadmap has
been completed, archived, or continued on a follow-up branch.

## Naming

Every entry uses the fix id format:

```text
FIX_<THEME>_<YYYY-MM-DD>_<SHORT_TITLE>
```

`<THEME>` must match the roadmap/report theme token, for example:

```text
ROADMAP_PARAMETER_AUTOMATION_SYSTEM.md
REPORT_PARAMETER_AUTOMATION_SYSTEM_IMPLEMENTATION_2026-05-01.md
FIX_PARAMETER_AUTOMATION_SYSTEM_2026-05-02_TIMELINE_RETARGET_EDITING
```

## Entry Requirements

Each post-roadmap fix entry must record:

- Related roadmap and implementation report.
- Affected repository and branch.
- User-visible symptom.
- Root cause.
- Fix summary.
- Fix commit hash once committed.
- Local and CI verification, where applicable.
- Remaining regression-test gap, if any.

The matching implementation report must also contain a `Post-Completion Fixes`
section that links or names the same fix id.

## FIX_PARAMETER_AUTOMATION_SYSTEM_2026-05-02_TIMELINE_RETARGET_EDITING

Date: 2026-05-02
Theme: `PARAMETER_AUTOMATION_SYSTEM`
Roadmap: `ROADMAP_PARAMETER_AUTOMATION_SYSTEM.md`
Report: `REPORT_PARAMETER_AUTOMATION_SYSTEM_IMPLEMENTATION_2026-05-01.md`
Repository: `xyona-lab`
Branch: `codex/operator-help-standard`
Status: committed and pushed
Commit: `ea9ec70c`

Symptom:

```text
After selecting a parameter in a timeline automation lane, for example TestTone
frequency, the lane no longer accepts drawn points. Modulation lanes still allow
point drawing.
```

Root cause:

```text
Timeline::handleAutomationLaneTargetChanged validated the requested target but
did not assign that ParamAddress to the visible current lane on the new-target
path. The lane stayed targetless/unresolved, so the new automation
value-presentation gate disabled editing because target presentation is
required but unresolved.
```

Fix summary:

```text
Assign the requested target to the current visible automation lane, reset the
lane segment document, mark the lane as Normalized01 and resolved, refresh the
automation UI, and keep the lane focused. When retargeting a lane that already
had a persistent target, preserve the old lane as hidden history and roll that
hidden clone back if the visible-lane update fails.
```

Verification:

```text
xyona-lab: git diff --check passed
xyona-lab: cmake --build build --target xyona_lab_tests -- -j8 passed
xyona-lab: ./build/tests/xyona_lab_tests --match "TimelineLaneStackController" --summary-only passed, 17 tests, 149 passes, 0 failures
xyona-lab: ./build/tests/xyona_lab_tests --match "Timeline Sidebar Bindings" --summary-only passed, 4 tests, 12 passes, 0 failures
xyona-lab: ./build/tests/xyona_lab_tests --match "Timeline Automation Lane Resolver" --summary-only passed, 4 tests, 32 passes, 0 failures
xyona-lab: ./build/tests/xyona_lab_tests --match "Timeline Automation Reconciliation" --summary-only passed, 7 tests, 62 passes, 0 failures
xyona-lab: ./build/tests/xyona_lab_tests --match "ProjectState Timeline Automation" --summary-only passed, 19 tests, 290 passes, 0 failures
```

Regression-test gap:

```text
The exact UI retarget handler path is private behind Timeline/HeaderColumn
callbacks. Existing resolver, sidebar, lane-controller, reconciliation, and
ProjectState tests cover the surrounding contracts, but a direct regression test
would require a small testable retargeting helper or a broader UI harness.
```

## FIX_PARAMETER_AUTOMATION_SYSTEM_2026-05-02_RECORDER_RECORDING_ELIGIBILITY

Date: 2026-05-02
Theme: `PARAMETER_AUTOMATION_SYSTEM`
Roadmap: `ROADMAP_PARAMETER_AUTOMATION_SYSTEM.md`
Report: `REPORT_PARAMETER_AUTOMATION_SYSTEM_IMPLEMENTATION_2026-05-01.md`
Repository: `xyona-lab`
Branch: `codex/operator-help-standard`
Status: committed and pushed
Commit: `0b298ab0`

Symptom:

```text
Live automation recording used the target resolver and normalized codec, but it
did not enforce the explicit recording eligibility policy. A resolved parameter
with recordable=false could still be recorded if its descriptor had a valid
normalized codec.
```

Root cause:

```text
AutomationRecorder::handleBaseValueEvent called IParamTargetResolver::resolve()
directly and encoded through the descriptor. It bypassed ParamTargetEligibility
with ParamTargetPurpose::Recording, while PreparedParameterAutomationRuntime and
other callers use the eligibility service for their target purpose.
```

Fix summary:

```text
Use ParamTargetEligibilityService with ParamTargetPurpose::Recording before lane
lookup or point append. Reject not-recordable targets before creating lanes, and
use the canonical resolved ParamAddress for lane lookup so recorder-created
lanes follow resolver target identity.
```

Verification:

```text
xyona-lab: git diff --check passed
xyona-lab: cmake --build build --target xyona_lab_tests -- -j8 passed
xyona-lab: ./build/tests/xyona_lab_tests --match "AutomationRecorder" --summary-only passed, 8 tests, 22 passes, 0 failures
xyona-lab: ./build/tests/xyona_lab_tests --match "Timeline Automation Recorder Bindings" --summary-only passed, 3 tests, 12 passes, 0 failures
xyona-lab: ./build/tests/xyona_lab_tests --match "Timeline Automation Reconciliation" --summary-only passed, 7 tests, 62 passes, 0 failures
xyona-lab: ./build/tests/xyona_lab_tests --match "ParamTargetEligibility" --summary-only passed, 5 tests, 56 passes, 0 failures
xyona-lab: ./build/tests/xyona_lab_tests --match "PreparedParameterAutomationRuntime" --summary-only passed, 3 tests, 18 passes, 0 failures
xyona-lab: ./build/tests/xyona_lab_tests --match "AudioGraphProcessor Parameter Automation Runtime" --summary-only passed, 6 tests, 28 passes, 0 failures
xyona-lab: GitHub Actions CI run 25249097977 passed on codex/operator-help-standard at 0b298ab0; macOS Clang Debug and Windows MSVC Debug succeeded
```

Remaining follow-up:

```text
This fix enforces the semantic contract. It does not add a product-level
notification surface for rejected recording attempts; that remains a separate
UX/diagnostics follow-up.
```
