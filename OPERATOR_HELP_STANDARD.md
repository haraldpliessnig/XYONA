# XYONA Operator Help Standard

**Status:** Workspace standard v1, strict
**Date:** 2026-05-02
**Applies to:** `xyona-core`, `xyona-cdp-pack`, `xyona-lab`, and future
runtime packs that publish public operators

This document is the normative help/documentation standard for public XYONA
operators. `ROADMAP_OPERATOR_HELP_STANDARD.md` remains the rollout plan while
existing help files are migrated.

## Source Model

The owning package owns its operator help. Public operator help sources live
beside the operator module:

```text
<pack-root>/src/operators/<family>/<operator>/docs/<locale>.md
```

Lab-authored public host operators currently live in
`xyona-lab/specs/operators/lab-public.op.yaml`. Until Lab introduces physical
host-operator modules, Lab keeps host-operator help under:

```text
xyona-lab/docs/help/lab/<locale>/operators/<module>.md
```

Lab panel, topic, and workflow help is outside this operator standard.

## Render Tiers

Every release-ready operator help source must support three tiers from one
source:

- **Tier 1 tooltip:** `short` frontmatter, 120 characters or less, one
  sentence, no Markdown.
- **Tier 2 inspector/sidebar:** frontmatter plus canonical `Tech Sheet`,
  `Ports`, and `Parameters` sections.
- **Tier 3 help window:** the full localized Markdown article.

The Tier 2 renderer may extract directly from Markdown or from generated
companion metadata produced from the same Markdown and descriptor facts. It
must not use separately maintained duplicate prose.

## Frontmatter

Release-ready operator help files use this frontmatter:

```yaml
---
standard: operator_help_v1
id: help.node.<operator_id>
title: <Human Readable Title>
short: <one-line tooltip description, <= 120 chars>
tags: [node, <provider>, <family>, ...]
provider: <core|cdp|faust|maximilian|lab|...>
family: <family-id>
operator: <operator-id>
capability: [rt, hq]
availability: insertable_rt
process_shape: <engine.processShape>
domain: <engine.domain>
related: [help.node.*, ...]
since: <pack-version>
---
```

Rules:

- `id` equals `help.node.<operator_id>`.
- `short` is the Tier 1 tooltip and matches the first prose line under H1.
- `tags` includes `node` and the provider.
- `related` contains help IDs only, never relative paths.
- Locale variants for the same operator share non-translatable facts:
  `standard`, `id`, `tags`, `provider`, `family`, `operator`, `capability`,
  `availability`, `process_shape`, `domain`, `related`, and `since`.
- Translatable fields are `title`, `short`, and body content.

Backward compatibility with legacy operator help structure is not required.
Every public operator help file must use `standard: operator_help_v1`.

## Section Order

Release-ready operator help files use this exact top-level order:

```text
# <Title>
<short>

## Tech Sheet
## Process
## Ports
## Parameters
## Data
## Application
## Processing Modes
## Requirements
## Detailed Technical Description
## Provenance
## Tips
## See Also
```

Sections that do not apply use explicit text such as `No user parameters.`,
`No typed data.`, or `No related operators.` Provider-specific detail belongs
inside these sections, not in new top-level sections.

## Tech Sheet

`Tech Sheet` is descriptor-derived and contains no prose. In v1 it may be
authored in Markdown and validated, or generated into companion metadata from
the same descriptor facts. A release-ready Markdown tech sheet uses these keys:

```markdown
- **Operator ID:** `<operator_id>`
- **Provider / Family:** `<providerLabel> / <family>`
- **Operator Type:** <operatorType>
- **Capability:** RT+HQ | RT only | HQ only | Data only | Offline only
- **Availability:** <availability class>
- **Process Shape:** <engine.processShape>
- **Domain:** <engine.domain>
- **Materialization:** <engine.materialization>
- **Output Length:** <engine.outputLength>
- **Host Contract:** <engine.abiV2Support | host-owned>
- **Channel Policy:** <inputs -> outputs>
- **Since:** <pack-version>
```

## Validation

The workspace linter is `tools/help_lint/operator_help_lint.py` and is strict
by default:

```bash
python tools/help_lint/operator_help_lint.py --workspace .
```

It requires complete localized help coverage and the v1 structure for all
public operator records in the selected workspace.
