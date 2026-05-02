---
title: Roadmap: XYONA Operator Help Standard
status: Active planing
owners: workspace
parent: OPERATOR_CONTRACT.md
started: 2026-05-01
applies_to:
  - xyona-core
  - xyona-cdp-pack
  - xyona-faust-pack (planned)
  - xyona-maximilian-pack (planned)
  - xyona-lab (host & lab-only operators)
---

# Roadmap: XYONA Operator Help Standard

**Status:** Active planing

**Started:** 2026-05-01

**Primary contract:** `OPERATOR_CONTRACT.md`

**Scope:** `xyona-core`, `xyona-cdp-pack`, future runtime packs, and
Lab-authored public host operators

This active roadmap follows the workspace naming convention used by the
archived operator roadmaps in `docs/done`: current work lives as a root
`ROADMAP_*.md`; once closed, the roadmap and any matching `REPORT_*.md` can be
archived under `docs/done`.

## Goal

Create one help/documentation contract for every public XYONA operator,
regardless of provider or pack.

The end state is:

```text
operator op.yaml / descriptor facts
        -> module-local docs/<locale>.md
        -> validated Tier 1 / Tier 2 / Tier 3 help content
        -> Lab tooltip, inspector, help window, packaged offline help
```

Users should see one repeatable documentation shape:

```text
tech sheet -> process -> ports -> data -> application -> detail
```

The target standard combines:

- CDP rigor: explicit process, mode, provenance, parameter ranges, and
  process notes.
- TouchDesigner uniformity: every operator uses the same page shape.
- Max/MSP tiering: tooltip, compact inspector summary, and full reference page
  are rendered from the same source.

## Current Baseline

This roadmap was checked against the workspace code on 2026-05-01.

### Contract And Module State

Current facts:

- `OPERATOR_CONTRACT.md` already defines `help.node.<operator_id>` as the help
  ID form for public operators.
- `OPERATOR_CONTRACT.md` already requires Lab to present operator-level
  technical facts: provider/family, type, capability, availability, process
  shape, domain, materialization, output length, host contract, ports, and
  parameter summary.
- `xyona-core` has 16 current operator `op.yaml` records under
  `src/operators/<family>/<operator>/`.
- `xyona-cdp-pack` has 16 current operator `op.yaml` records under
  `src/operators/<family>/<operator>/`.
- `xyona-lab` has 17 current public host-operator records in
  `specs/operators/lab-public.op.yaml`.
- Core, CDP pack, and Lab operator-module validators pass when run with the
  repo Python environments.

### Help Source State

Current facts:

- Core help files already live beside operator modules:
  `xyona-core/src/operators/<family>/<operator>/docs/<locale>.md`.
- Core currently has 16 English and 16 German operator help files.
- CDP pack help files already live beside operator modules:
  `xyona-cdp-pack/src/operators/<family>/<operator>/docs/<locale>.md`.
- CDP pack currently has 8 English and 8 German operator help files.
- The remaining CDP `op.yaml` records do not all have help files yet; closing
  that gap is part of this roadmap.
- Existing Core and CDP help files use legacy section shapes such as
  `Parameters`, `Usage`, `Processing Modes`, `Requirements`, `Provenance`,
  `Tips`, and `See Also`.
- Existing help files do not yet use the target `Tech Sheet`, `Process`,
  `Ports`, `Data`, `Application`, and `Detailed Technical Description`
  structure consistently.
- Some Core signal operator help files are still minimal articles rather than
  release-ready full help pages.

### Runtime And Build State

Current facts:

- Core code generation parses help frontmatter from
  `src/operators/*/*/docs/*.md` and validates basic help IDs/tags.
- Core can generate HTML fragments from module-local operator Markdown.
- Core install rules place operator Markdown under
  `share/xyona-core/help/<operator_id>/`.
- Lab `HelpService` loads `help.node.*` through the Core API and Lab-owned
  panel/topic/workflow help from Lab's filesystem docs.
- Lab's current `sync_docs` target copies `xyona-lab/docs/help` into the build
  docs tree and still contains a legacy `xyona-core/src/processes` copy hook.
- Lab does not yet collect all operator help into the target
  `<provider>/<family>/<operator>/docs/<locale>.md` build tree.
- A workspace-level `tools/help_lint` does not exist yet.

## Current Problem

The codebase has the right operator module shape and enough help-system
plumbing to support a unified standard, but the help content contract is not
yet enforced end to end.

The gaps are:

- Existing help pages are useful but structurally inconsistent across Core,
  CDP, and Lab.
- Frontmatter does not yet carry the full target schema: `short`, `provider`,
  `family`, `operator`, `capability`, `availability`, `process_shape`,
  `domain`, and `since`.
- Tier 1 tooltip content is currently descriptor-driven in practice, not
  guaranteed to match a `short` field and the first prose line under H1.
- Tier 2 inspector extraction has no canonical Markdown anchors yet.
- Tech-sheet facts are not generated or validated from descriptor metadata.
- CDP has public operator specs without corresponding localized help files.
- Lab packaging/indexing does not yet consume Core, CDP pack, Lab host
  operators, and future packs through one provider-aware help tree.
- Locale parity is not enforced by a shared linter.

## Non-Goals

- Do not move DSP or pack implementation code as part of this roadmap.
- Do not make Lab author CDP or Core DSP help as a substitute for owning
  package help.
- Do not add fallback logic that guesses incomplete operator help metadata from
  labels, source paths, categories, or dotted IDs.
- Do not require third-party packs to translate into German unless their pack
  manifest declares German as a shipped locale.
- Do not redesign the Lab HelpCenter UI before the content contract and
  indexing surface are stable.

## Target Help Contract

This section is the target standard to implement through the phases below. It
is not fully satisfied by the current tree yet.

### Render Tiers

Every operator help source must support three render tiers from the same
content.

Tier 1: Operator-list tooltip and compact summary.

- Source: `short` in help frontmatter, mirrored by descriptor/help metadata as
  needed.
- Length budget: 180 characters or less.
- Shape: one or two user-facing application sentences, no Markdown.
- Surface: operator browser/sidebar hover, parameter sidebar summary, compact
  context labels. Canvas node hover is not an operator-help surface.
- Technical classification such as provider (`core`, `cdp`, `lab`), processing
  domain (`time_audio`, `spectral_pvoc`), and capability (`RT`, `HQ`, `Data`)
  is rendered as a separate mini line from existing metadata, not embedded in
  `short`.

Tier 2: Sidebar / Parameter Inspector.

- Source: frontmatter plus `Tech Sheet`, `Ports`, and `Parameters`.
- Required facts: title, short description, operator technical summary,
  parameters with id/range/default/unit, ports with id/type, capability badges,
  availability, process shape, and domain.
- Renderer rule: extract from canonical Markdown anchors or generated
  companion metadata; do not maintain parallel prose.

Tier 3: Help Window.

- Source: full `docs/<locale>.md`.
- Surface: Lab help window, web help portal, packaged offline help.
- Includes usage, modes, requirements, provenance, detailed technical notes,
  tips, and links.

### Canonical Source Path

The source of truth for public operator help is:

```text
<pack-root>/src/operators/<family>/<operator>/docs/<locale>.md
```

Per-provider examples:

```text
xyona-core/src/operators/dynamics/gain/docs/en.md
xyona-core/src/operators/dynamics/gain/docs/de.md
xyona-cdp-pack/src/operators/modify/loudness_gain/docs/en.md
xyona-cdp-pack/src/operators/modify/loudness_gain/docs/de.md
xyona-lab/src/operators/<family>/<operator>/docs/<locale>.md        # future physical Lab host modules, if introduced
```

Current Lab panel/topic/workflow docs such as
`xyona-lab/src/app/lab/helpcenter/docs/OVERVIEW.md` and
`xyona-lab/docs/help/lab/<locale>/topics/*.md` are out of scope for the
operator-help standard.

### Target Frontmatter

```yaml
---
id: help.node.<operator_id>
title: <Human Readable Title>
short: <application tooltip text, 1-2 sentences, <= 180 chars>
tags: [node, <provider>, <family>, ...]
provider: <core|cdp|faust|maximilian|lab|...>
family: <family-id>
operator: <operator-id>
capability: [rt, hq]            # subset of rt, hq, data, offline
availability: insertable_rt      # OPERATOR_CONTRACT.md availability class
process_shape: <engine.processShape>
domain: <engine.domain>
related: [help.node.*, ...]
since: <pack-version>
---
```

Rules:

- `id` equals `help.node.<operator_id>`.
- `operator_id` is the stable descriptor ID from `OPERATOR_CONTRACT.md`.
- `short` is the Tier 1 application summary and matches the first prose line
  under H1.
- `short` describes user intent and must not carry schema, descriptor,
  host-contract, fixture, or internal workflow wording.
- `tags` includes `node` and the provider.
- `related` contains help IDs only, never relative paths.
- Locale variants for the same operator share non-translatable identity,
  capability, availability, process, domain, related, and tag facts.
- Translatable fields are `title`, `short`, and prose body content.

### Canonical Section Order

Every release-ready operator help file uses this top-level order:

```text
# <Title>
<short description>

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

Rules:

- Top-level section order is strict.
- Sections that do not apply use explicit empty text, such as
  `No user parameters.` or `No typed data.`.
- Provider-specific detail belongs inside these sections, not in new top-level
  sections.

### Tech Sheet

`Tech Sheet` is a machine-readable key/value block generated or validated from
descriptor metadata:

```markdown
## Tech Sheet

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

No prose belongs in this block.

### Ports

`Ports` documents every public descriptor input and output. Each port block
names the descriptor port ID and the explicit port type.

Example:

```markdown
### in `xyona.audio` (input)

- Channels: any
- Merge policy: single_source
- Notes: must match output channel count.

### pvoc `cdp.pvoc.analysis.v1` (output)

- Kind: typed_data
- Schema: `xyona.cdp.pvoc.analysis.v1`
- Format: `pvoc_analysis`
- Rate: offline_artifact
```

The linter must reject public ports that exist in descriptors but not in help,
and help port blocks that no longer exist in descriptors.

### Parameters

Each visible user parameter uses this block:

```markdown
### <Display Name>

- **ID:** `<param_id>`
- **Type:** float | int | enum | trigger | bool | breakpoint | curve | text
- **Range:** <min> to <max>
- **Default:** <value>
- **Unit:** <unit>
- **Modulatable:** yes | no | rt-only
- **Topology-sensitive:** yes | no
- **Available in:** realtime | HQ | both
```

Parameterless operators write `No user parameters.`

### Provider Adaptations

All providers keep the same top-level sections. They differ only in emphasis
and provenance detail:

| Section | Core | CDP | Faust | Maximilian | Lab |
|---|---|---|---|---|---|
| Tech Sheet | descriptor facts | descriptor facts | descriptor facts | descriptor facts | host descriptor facts |
| Process | DSP behavior | CDP process/mode behavior | block behavior | class behavior | host behavior |
| Ports | Core port types | audio + CDP typed data | audio/control/data | audio/control/data | host-owned ports |
| Parameters | descriptor params | CDP params/ranges | Faust UI controls | class properties | host params |
| Data | if typed | PVOC/pitch/etc. | bargraph/soundfile/etc. | if typed | if typed |
| Provenance | author/design doc | CDP8 source/process/mode | `.dsp` source/version | header/class/commit | author/design doc |

## Phase 0: Baseline Audit

Status: complete for this roadmap.

Deliverables:

- Verify root contract and authoring guide references.
- Count current Core, CDP pack, and Lab public operator specs.
- Count current localized operator help files.
- Inspect existing section order in representative Core and CDP help files.
- Verify current module validators.
- Identify runtime/build mismatches between the target standard and Lab/Core
  help loading.

Exit criteria:

- Current facts are recorded in this roadmap.
- Any aspirational statement is clearly marked as target, not current state.

Progress:

- Core validator passed: 16 `op.yaml` records.
- CDP pack validator passed: 16 `op.yaml` records.
- CDP generated metadata check passed.
- Lab validator passed: 17 public host-operator records.
- Current Core/CDP help files were confirmed to be legacy-shape articles, not
  fully migrated standard-shape articles.

## Phase 1: Contract Freeze

Status: pending.

Deliverables:

- Keep this rollout document as `ROADMAP_OPERATOR_HELP_STANDARD.md` while the
  help migration is active.
- Decide whether the final normative standard becomes a separate
  `OPERATOR_HELP_STANDARD.md` after implementation is complete.
- Add a concise `Help Standard` section to `OPERATOR_CONTRACT.md` or link this
  roadmap as the active rollout document from the contract.
- Update package-local help standards to state that their current section
  orders are transitional until this roadmap completes:
  - `xyona-core/src/operators/HELP_STANDARDS.md`
  - `xyona-cdp-pack/docs/HELP_STANDARDS.md`
- Define whether `Tech Sheet` is generated into Markdown, generated into a
  companion metadata artifact, or authored manually and validated.

Exit criteria:

- No package-local document contradicts the target workspace standard.
- The source of truth for generated versus authored fields is explicit.

## Phase 2: Frontmatter And Locale Contract

Status: pending.

Deliverables:

- Extend Core help frontmatter parsing/codegen to accept and preserve:
  `short`, `provider`, `family`, `operator`, `capability`, `availability`,
  `process_shape`, `domain`, `related`, and `since`.
- Extend CDP pack metadata/help generation or validation with the same
  frontmatter facts.
- Decide how Lab public host-operator help is represented while Lab host
  operator specs live in `specs/operators/lab-public.op.yaml`.
- Define pack manifest locale declarations for future packs.
- Keep German mandatory for current Core and current CDP operator help.

Exit criteria:

- Existing minimal frontmatter still loads during migration.
- New release-ready help files use the target frontmatter.
- Locale variants agree on non-translatable metadata.

## Phase 3: Workspace Help Linter

Status: pending.

Deliverables:

- Add a workspace-level help linter, for example `tools/help_lint`.
- Validate source paths and required locale files.
- Parse frontmatter with YAML, not ad hoc text rules.
- Validate `id == help.node.<operator_id>` against descriptor/operator specs.
- Validate strict top-level section order for migrated help files.
- Validate `short` length and H1 first-line parity.
- Validate descriptor parameters against `## Parameters`.
- Validate descriptor ports against `## Ports`.
- Validate `related` IDs against available help files.
- Validate locale parity for sections, parameter blocks, and port blocks.

Exit criteria:

- The linter can run across Core, CDP pack, and Lab public host-operator help.
- It supports a transitional allowlist for not-yet-migrated files.
- It fails newly added release-ready operators that do not satisfy the target
  standard.

## Phase 4: Core Help Migration

Status: pending.

Deliverables:

- Migrate all 16 current Core English help files to the target section order.
- Migrate all 16 current Core German help files with matching structure.
- Add full `Tech Sheet`, `Process`, `Ports`, `Data`, `Application`, and
  `Detailed Technical Description` content.
- Replace legacy-only sections such as `Usage`, `How It Works`, `Overview`,
  and `Technical Details` with content placed under canonical target
  sections.
- Preserve existing useful prose, tips, and links where correct.

Exit criteria:

- Core help linter passes for all current Core operators.
- Core codegen still validates help IDs and tags.
- Core generated metadata remains stable except for intentional help metadata
  additions.

## Phase 5: CDP Pack Help Migration

Status: pending.

Deliverables:

- Migrate the existing 8 English and 8 German CDP help files to the target
  section order.
- Add English and German help files for all remaining public CDP operator
  specs that currently lack them.
- Preserve CDP provenance:
  source file, library/program/process/mode, command mode, process number, and
  validation strategy where available.
- Document CDP typed-data ports, especially PVOC analysis/synthesis schemas.
- Keep raw CDP CLI syntax out of the primary user instruction unless the
  operator actually exposes file/CLI semantics.

Exit criteria:

- CDP help linter passes for all 16 current CDP public operators.
- `scripts/generate_operator_metadata.py --check` remains clean.
- CDP source/provenance policy from `xyona-cdp-pack/docs/HELP_STANDARDS.md` is
  satisfied.

## Phase 6: Lab Host-Operator Help

Status: pending.

Deliverables:

- Decide whether Lab public host operators keep help under `docs/help/lab` or
  gain physical `src/operators/<family>/<operator>/docs/<locale>.md` modules.
- Add target-shape help for current Lab-authored public host operators.
- Keep Lab panel/topic/workflow docs outside the operator standard.
- Ensure Lab host-operator help uses host-owned provenance and host contract
  language, not DSP-pack language.

Exit criteria:

- Lab public host operators can resolve `help.node.lab.*` articles.
- Lab panel/topic/workflow help remains indexed and unaffected.
- Lab validator and help linter agree on public host-operator help coverage.

## Phase 7: Lab Build, Indexing, And Runtime Resolution

Status: pending.

Deliverables:

- Replace the legacy `xyona-core/src/processes` docs copy hook in Lab.
- Define and implement the build/runtime operator help tree consumed by Lab.
- Recommended target:

  ```text
  <build>/docs/help/<provider>/<family>/<operator>/docs/<locale>.md
  ```

- Make Core, CDP packs, Lab host operators, and future packs contribute help
  through provider-aware metadata.
- Extend `tools/i18n/build_docs_index.py` or its successor to index operator
  help by `help.node.*`, locale, provider, family, tags, and related IDs.
- Preserve Lab topic/panel/workflow help indexing.

Exit criteria:

- Lab can resolve Core, CDP pack, and Lab host-operator help from one indexed
  surface.
- Pack-provided operator help remains owned by the pack and dynamically
  replaceable with the pack.
- No build output is treated as source of truth.

## Phase 8: Tier 2 Extraction And UI Integration

Status: pending.

Deliverables:

- Implement Tier 1 operator browser/sidebar hover and parameter-sidebar summary
  lookup from `short` or descriptor-mirrored metadata.
- Render provider/domain/capability as a separate compact technical line in
  Tier 1 surfaces.
- Implement Tier 2 inspector extraction from frontmatter plus canonical
  `Tech Sheet`, `Ports`, and `Parameters` content.
- Add capability and availability badges using descriptor facts.
- Surface disabled/unavailable reasons from descriptor validation, not help
  prose.
- Keep Tier 3 help window rendering from the full Markdown article.

Exit criteria:

- Palette hover, node hover, parameter inspector, and help window all use the
  same operator help source.
- Tier 2 has no hand-maintained duplicate prose separate from operator docs.
- Missing required Tier 2 anchors are release-gate failures.

## Validation Gates

Until `tools/help_lint` exists, use these gates plus manual review of the
target section contract.

### Workspace

```bash
git diff --check
```

### Core

```bash
/Users/haraldpliessnig/Github/XYONA/xyona-core/.venv/bin/python \
  tools/operator_modules/validate_operator_modules.py --root .
```

When changing Core generation or runtime help loading, also run the relevant
Core codegen/build/test targets from `xyona-core/OPERATOR_MODULE_AUTHORING_GUIDE.md`.

### CDP Pack

```bash
/Users/haraldpliessnig/Github/XYONA/xyona-core/.venv/bin/python \
  scripts/validate_operator_modules.py

/Users/haraldpliessnig/Github/XYONA/xyona-core/.venv/bin/python \
  scripts/generate_operator_metadata.py --check
```

When changing CDP behavior, descriptor generation, pack loading, or typed-data
help, also run the package-local CDP tests for the affected operator family.

### Lab

```bash
/Users/haraldpliessnig/Github/XYONA/xyona-lab/.venv/bin/python \
  scripts/validate_operator_modules.py
```

When changing Lab indexing, runtime resolution, inspector extraction, or help
UI, prefer `./build-dev.sh` and the relevant HelpCenter/operator-module tests.

## Success Criteria

The roadmap is complete when:

- Every current public Core operator has release-ready English and German help
  in the target section order.
- Every current public CDP operator has release-ready English and German help
  in the target section order.
- Lab public host operators have release-ready operator help in the agreed
  Lab-owned location.
- Future packs can declare required locales and validate every operator against
  that locale set.
- The workspace help linter enforces frontmatter, section order, descriptor
  parameter parity, descriptor port parity, related-ID resolution, and locale
  parity.
- Lab can render tooltip, inspector/sidebar, and full help window content from
  the same source without parallel hand-authored content.
- Lab's build/indexing path no longer depends on legacy `src/processes`.
- Package-local help standards extend the workspace standard rather than
  contradicting it.

## Open Decisions

- Whether `Tech Sheet` should be generated into Markdown and committed, or
  generated at build time as a companion artifact.
- Whether Tier 2 should extract directly from Markdown or consume generated
  JSON produced from the same source and descriptor facts.
- The final source path for Lab public host-operator help while Lab host specs
  remain centralized.
- How dynamically loaded third-party packs publish help files and locale
  manifests to Lab.
- Whether image, video, and interactive examples belong in v1 help validation
  or a later media extension.

## Related Documents

- `OPERATOR_CONTRACT.md` - workspace operator contract.
- `OPERATOR_MODULE_AUTHORING_GUIDE.md` - practical module authoring rules.
- `xyona-core/src/operators/HELP_STANDARDS.md` - current Core transitional
  help documentation.
- `xyona-cdp-pack/docs/HELP_STANDARDS.md` - current CDP-pack-specific help
  rules.
- `xyona-cdp-pack/docs/CDP_PORT_TYPES.md` - CDP typed-data port contract.
- `xyona-lab/src/app/lab/helpcenter/docs/OVERVIEW.md` - current Lab
  HelpCenter implementation notes.
- `docs/done/ROADMAP_OPERATOR_PORT_TYPES_AND_PATCH_COMPATIBILITY.md` -
  completed port-type rollout.
- `docs/done/ROADMAP_OPERATOR_SLOT_SYSTEM.md` - completed slot-system rollout.
