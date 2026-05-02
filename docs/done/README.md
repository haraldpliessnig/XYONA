# Done Documentation Archive

This folder contains completed, closed, or superseded XYONA root roadmaps and
their reports. Some archived roadmaps still mention future work; those notes are
historical follow-ups and should become new current roadmaps when work resumes.

## Naming Contract

New roadmap-driven work uses one stable uppercase snake-case theme token across
all related docs:

- Roadmap: `ROADMAP_<THEME>.md`
- Technical review report, when present:
  `REPORT_<THEME>_TECHNICAL_REVIEW_<YYYY-MM-DD>.md`
- Implementation report: `REPORT_<THEME>_IMPLEMENTATION_<YYYY-MM-DD>.md`
- Post-completion fix id:
  `FIX_<THEME>_<YYYY-MM-DD>_<SHORT_TITLE>`

Existing historical files may keep their archived names. When a current or
future roadmap/report is created or touched, prefer the naming contract above.

## Post-Completion Fix Tracking

After a roadmap is completed or archived, later bugfixes are tracked in two
places:

- The matching implementation report under `Post-Completion Fixes`.
- The central index `POST_ROADMAP_FIXES.md`.

Each fix entry records the theme token, roadmap, report, affected repo and
branch, symptom, root cause, fix commit, verification, and any regression-test
gap. The roadmap itself remains the historical plan and should not be rewritten
as if the later bugfix had been part of the original implementation.

## Archived 2026-05-01

- `ROADMAP_OPERATOR_MODULE_STRUCTURE.md`
- `REPORT_OPERATOR_MODULE_NAMING_STRUCTURE.md`
- `ROADMAP_OPERATOR_PORT_TYPES_AND_PATCH_COMPATIBILITY.md`
- `REPORT_OPERATOR_PORT_TYPES_AND_PATCH_COMPATIBILITY_2026-04-30.md`
- `ROADMAP_OPERATOR_SLOT_SYSTEM.md`
- `REPORT_OPERATOR_SLOT_SYSTEM_2026-05-01.md`
- `REPORT_OPERATOR_SLOT_SYSTEM_IMPLEMENTATION_2026-05-01.md`
- `CDP8_OFFLINE_SPECTRAL_ROADMAP.md`
- `CDP8_OFFLINE_SPECTRAL_IMPLEMENTATION_REPORT.md`

## Archived 2026-05-02

- `ROADMAP_PARAMETER_AUTOMATION_SYSTEM.md`
- `REPORT_PARAMETER_AUTOMATION_SYSTEM_TECHNICAL_REVIEW_2026-05-01.md`
- `REPORT_PARAMETER_AUTOMATION_SYSTEM_IMPLEMENTATION_2026-05-01.md`
- `ROADMAP_OPERATOR_HELP_STANDARD.md`
- `REPORT_OPERATOR_HELP_STANDARD_IMPLEMENTATION_2026-05-02.md`
- `POST_ROADMAP_FIXES.md`

## Active Follow-Ups

- `../../ROADMAP_OPERATOR_HELP_STANDARD_FOLLOWUP.md`
