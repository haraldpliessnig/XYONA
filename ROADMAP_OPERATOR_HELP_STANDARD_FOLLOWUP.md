---
title: Roadmap: Operator Help Standard Follow-Up
status: Active follow-up
owners: workspace
parent: OPERATOR_HELP_STANDARD.md
created: 2026-05-02
supersedes:
  - docs/done/ROADMAP_OPERATOR_HELP_STANDARD.md
evidence:
  - docs/done/REPORT_OPERATOR_HELP_STANDARD_IMPLEMENTATION_2026-05-02.md
applies_to:
  - xyona-core
  - xyona-cdp-pack
  - xyona-lab
  - future runtime packs
---

# Roadmap: Operator Help Standard Follow-Up

**Status:** Active follow-up

**Created:** 2026-05-02

**Normative standard:** `OPERATOR_HELP_STANDARD.md`

**Archived implementation evidence:**
`docs/done/REPORT_OPERATOR_HELP_STANDARD_IMPLEMENTATION_2026-05-02.md`

## Baseline Already Closed

The first operator-help implementation slice is closed and archived. It
delivered:

- `OPERATOR_HELP_STANDARD.md` as the strict v1 standard.
- `standard: operator_help_v1` validation across current public Core, CDP, and
  Lab operator help.
- Application-focused `short` summaries with a separate metadata-derived
  provider/domain/capability line.
- Core help metadata transport through the Host API.
- CDP help payload transport through generated pack metadata.
- Lab provider-aware operator help sync/indexing.
- Lab operator-sidebar row tooltips from help metadata.
- Lab Parameter sidebar `short` summary under the focused operator title.
- Local validation plus final Lab GitHub Actions CI on 2026-05-02.

## Remaining Scope

This follow-up owns the parts of the original roadmap that are intentionally
not complete yet.

## F1: Release-Ready Operator Articles

Goal: make every current public operator article fully release-ready, not only
schema-valid.

Deliverables:

- Migrate current Core operator help to the complete canonical section order.
- Migrate current CDP operator help to the complete canonical section order.
- Keep current Lab host-operator help in the agreed Lab-owned location unless
  physical Lab operator modules are introduced first.
- Fill `Tech Sheet`, `Process`, `Ports`, `Parameters`, `Data`, `Application`,
  `Processing Modes`, `Requirements`, `Detailed Technical Description`,
  `Provenance`, `Tips`, and `See Also` with package-owned content where
  applicable.

Exit criteria:

- All current public Core, CDP, and Lab operators have release-ready English
  and German articles.
- Package-local help standards no longer describe transitional section orders.

## F2: Strict Structural Linter V2

Goal: move from v1 metadata validation to complete structural release gates.

Deliverables:

- Validate canonical top-level section order.
- Validate `short` and first prose line parity.
- Validate descriptor parameter parity against `## Parameters`.
- Validate descriptor port parity against `## Ports`.
- Validate `related` IDs against the available help index.
- Validate locale parity for sections, parameter blocks, and port blocks.
- Add pack locale manifest validation for future runtime packs.

Exit criteria:

- Newly added or changed public operators cannot pass validation with missing
  required release-help structure.

## F3: Tier 2 Inspector Extraction

Goal: make the Parameter inspector/sidebar consume the same source as Tier 3
without parallel hand-authored prose.

Deliverables:

- Decide whether Tier 2 reads canonical Markdown anchors directly or generated
  companion JSON from the same sources and descriptor facts.
- Render `Tech Sheet`, port facts, parameter facts, capability badges, and
  availability in the inspector.
- Surface disabled/unavailable reasons from descriptor validation, not help
  prose.
- Keep Tier 1 tooltip/summary and Tier 3 full help window on the same help
  source.

Exit criteria:

- Tier 2 contains no separately maintained duplicate operator prose.
- Missing required Tier 2 anchors or generated facts fail validation.

## F4: Dynamic Pack Help Publishing

Goal: define the runtime-pack help contract beyond current Core/CDP/Lab.

Deliverables:

- Define how dynamically loaded third-party packs publish help files and locale
  declarations.
- Keep pack-provided help owned by the pack and replaceable with the pack.
- Decide whether media examples belong in v1 validation or a later extension.

Exit criteria:

- Future packs can declare locale coverage and validate every shipped public
  operator help file against the workspace standard.

## Validation Gates

Workspace:

```bash
git diff --check
tools/help_lint/operator_help_lint.py --workspace .
```

Package-specific changes must also use the package-local validators and build
or test targets documented in the relevant `AGENTS.md` and authoring guides.

## Archive Note

The original `ROADMAP_OPERATOR_HELP_STANDARD.md` is archived under
`docs/done/` as the completed first implementation slice. This follow-up is the
current source for remaining operator-help product work.
