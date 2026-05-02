# Report: Operator Help Standard Implementation

**Date:** 2026-05-02
**Branch:** `codex/operator-help-standard`
**Scope:** Workspace standard, Core metadata transport, CDP pack metadata,
workspace linting, and Lab help indexing

## Feasibility Review

`ROADMAP_OPERATOR_HELP_STANDARD.md` is technically implementable and aligned
with the existing operator-module contract. The current codebase already has
the required foundations: module-local `docs/<locale>.md` files in Core and
CDP, descriptor-owned IDs and port types, Core frontmatter parsing, CDP
generated metadata, and Lab filesystem help indexing.

The high-quality path still needs staged commits, but there is no compatibility
requirement for legacy help structure. Existing Core/CDP articles are
legacy-shaped, CDP has operators without localized help files, and Lab
host-operator specs currently do not carry the full parameter descriptor
surface required for richly authored Tier 2 prose. The implementation therefore
replaces the current operator-help shape with descriptor-grounded
`operator_help_v1` files and makes the linter strict by default.

## Technical Decisions

- `OPERATOR_HELP_STANDARD.md` is the normative v1 help standard.
- `ROADMAP_OPERATOR_HELP_STANDARD.md` remains the active rollout tracker.
- All public operator help files must declare `standard: operator_help_v1`.
- `Tech Sheet` may be authored and validated in Markdown or generated into
  companion metadata from descriptor facts; no prose belongs in the block.
- The workspace help linter is strict by default; no legacy operator-help
  compatibility mode is part of the implementation.

## Commit Log

This table is updated as implementation commits are produced and pushed.

| Repo | Commit | Subject | Local validation | Push |
|---|---|---|---|---|
