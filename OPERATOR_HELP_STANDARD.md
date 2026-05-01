---
title: XYONA Operator Help Standard
status: draft
owners: workspace
parent: OPERATOR_CONTRACT.md
applies_to:
  - xyona-core
  - xyona-cdp-pack
  - xyona-faust-pack (planned)
  - xyona-maximilian-pack (planned)
  - xyona-lab (host & lab-only operators)
---

## XYONA Operator Help Standard

A single help/documentation contract for **every** XYONA operator, regardless of
pack (CDP, Faust, Maximilian, Core, Lab, future). One template. One section
order. One frontmatter schema. Operators may carry **less** content per
section, but never a **different** structure.

This standard is workspace-level. Pack-local help docs (e.g.
`xyona-cdp-pack/docs/HELP_STANDARDS.md`) extend this contract with
pack-specific provenance and validation rules — they do not replace it.

> **Why a single standard?** XYONA operators come from very different worlds
> (typed CDP file processes, Faust block diagrams, Maximilian C++ classes,
> hand-written DSP). Users should not have to learn three documentation
> dialects. The same eye-shape every time: tech sheet → process → ports →
> data → application → detail.

---

## 1. Reference Doc Cultures

The standard is informed by three established reference cultures. We do not
copy them; we extract the shape.

| Source | What we take | What we drop |
|---|---|---|
| **CDP8 manuals & CLI help** | Process-centric structure, explicit modes, range/default per parameter, "ON THE PROCESS" notes section, source provenance | File-centric/CLI wording, `infile outfile` syntax as primary instruction |
| **Max/MSP 9 refpages** | Tooltip line + short description + arguments/attributes table + inlets/outlets + see-also; tiered rendering (tooltip → inspector → ref window) | Per-message verb tables (XYONA has typed ports, not message dispatch) |
| **TouchDesigner OP help** | Strict identical layout for every operator, "Parameters" pages, separate "Inputs"/"Outputs", "Info CHOP Channels" (introspection), "Common" page, build/version footer | Page-tab UI metaphor (we use one scrollable doc), TouchDesigner-specific channel/CHOP semantics |

The XYONA shape is **CDP rigor + TouchDesigner uniformity + Max tiering**.

---

## 2. Three Render Tiers

Every operator's help content must render in three tiers. The same source file
feeds all three; no parallel content.

### Tier 1 — Tooltip (one line)

- Source: `description` field in `op.yaml` / descriptor (mirrored as the first
  prose line under H1 in the help file).
- Length budget: **≤ 120 chars**, single sentence, no markdown.
- Surface: hover on palette item, hover on canvas node header.
- Example: *"Apply a linear gain factor to audio samples (CDP modify loudness)."*

### Tier 2 — Sidebar / Parameter Inspector (minimal)

- Source: frontmatter + the **Tech Sheet**, **Ports**, and **Parameters**
  sections of the help file (see §4). Renderer extracts these; it does not
  reflow prose.
- Length budget: fits one inspector pane without scrolling on a 720 px tall
  sidebar.
- Surface: Lab parameter sidebar, "i" button on a node, palette long-press.
- Mandatory content: title, one-line description, operator-technical-summary
  (per `OPERATOR_CONTRACT.md` §"Operator Technical Summary For Lab"),
  parameter list with id/range/default/unit, port list with id/type, capability
  badges (RT / HQ / Data / Offline).

### Tier 3 — Help Window (full)

- Source: the entire `docs/<locale>.md` rendered as Markdown.
- Surface: dedicated help window, web help portal, packaged offline help.
- Includes everything: usage, processing modes, requirements, provenance,
  detailed technical description, tips, see-also.

A help file that does not satisfy Tier 1 + Tier 2 extraction is **not
release-ready**, even if the Tier 3 prose is excellent.

---

## 3. File Layout & Frontmatter

### 3.1 Path

The canonical source path for an operator's help file is:

```text
<pack-root>/src/operators/<family>/<operator>/docs/<locale>.md
```

- `<family>` is the provider-local family (no provider prefix).
- One file per locale. **Never** combine languages in one file.
- Help files live **next to the operator's source code**, not in a central
  `docs/` tree. The operator module owns its help.

#### Per-pack canonical paths (today)

| Pack | Provider | Source path |
|---|---|---|
| `xyona-core` | `core` | `xyona-core/src/operators/<family>/<operator>/docs/<locale>.md` |
| `xyona-cdp-pack` | `cdp` | `xyona-cdp-pack/src/operators/<family>/<operator>/docs/<locale>.md` |
| `xyona-faust-pack` (planned) | `faust` | `xyona-faust-pack/src/operators/<family>/<operator>/docs/<locale>.md` |
| `xyona-maximilian-pack` (planned) | `maximilian` | `xyona-maximilian-pack/src/operators/<family>/<operator>/docs/<locale>.md` |
| `xyona-lab` host operators | `lab` | `xyona-lab/src/operators/<family>/<operator>/docs/<locale>.md` |

Existing examples (today, in tree):

```text
xyona-core/src/operators/dynamics/gain/docs/en.md
xyona-core/src/operators/dynamics/gain/docs/de.md
xyona-cdp-pack/src/operators/modify/loudness_gain/docs/en.md
xyona-cdp-pack/src/operators/modify/loudness_gain/docs/de.md
```

#### Build / runtime path (consumed by Lab)

The Lab build collects per-operator help into a flat help tree:

```text
xyona-lab/build/<preset>/docs/help/<provider>/<family>/<operator>/docs/<locale>.md
```

This path is **build output** — never edit it, never check it in. The source
of truth is always the per-pack path above. The build copy exists so that
Lab can resolve `help.node.<operator_id>` without knowing which pack a given
operator came from.

#### Lab panel / topic docs (out of scope here)

Files like `xyona-lab/src/app/lab/helpcenter/docs/OVERVIEW.md` document Lab
**panels and workflows**, not operators. They are not bound by this
standard. This standard governs only operator help (`help.node.*`).

### 3.2 Localization

- **`en.md` is mandatory for every operator in every pack.**
- **`de.md` is mandatory for `xyona-core` and `xyona-cdp-pack`** — both ship
  fully-localized today (Core: 16 en + 16 de operators; CDP pack: 8 en +
  8 de). New operators in these packs must ship `de.md` in the same PR as
  `en.md`; an English-only addition is a release-gate failure.
- Future packs (`faust`, `maximilian`, third-party) declare their locale set
  in their pack manifest. Whatever set they declare, all operators in the
  pack must satisfy it — no locale-sparse packs.
- Locale parity is enforced structurally, not by translation quality:
  - same `id`, `tags`, `related`, `capability`, `availability`,
    `process_shape`, `domain` in frontmatter,
  - same section order (§4),
  - same set of `### <Parameter>` blocks under `## Parameters`,
  - same set of port blocks under `## Ports`.
  - Translatable keys: `title`, `short`, and all prose body content.
- File encoding is UTF-8 (no BOM). Line endings are LF. German `ß` and
  umlauts are written literally, never as HTML entities.
- New locales (e.g. `fr.md`, `ja.md`) follow the same rules. Locale codes are
  ISO 639-1 lowercase, no region suffix unless ambiguous.

### 3.2 Frontmatter (canonical)

```yaml
---
id: help.node.<operator_id>
title: <Human Readable Title>
short: <≤120-char one-line tooltip description>
tags: [node, <provider>, <family>, ...]
provider: <core|cdp|faust|maximilian|lab|...>
family: <family-id>
operator: <operator-id>
capability: [rt, hq]            # subset of: rt, hq, data, offline
availability: insertable_rt      # one of OPERATOR_CONTRACT.md availability classes
process_shape: <engine.processShape>
domain: <engine.domain>
related: [help.node.*, ...]      # IDs only, never relative paths
since: <pack-version>            # optional but recommended
---
```

Rules:

- `id` always equals `help.node.<operator_id>`; the operator ID is the one
  established by `OPERATOR_CONTRACT.md` (§"Identity And Naming").
- `short` is the Tier-1 tooltip and **must** match the first prose line under
  the H1 heading in the body.
- `tags` always includes `node` and the provider (`cdp`, `faust`,
  `maximilian`, `core`, `lab`).
- `related` contains help IDs only.
- All locale files for the same operator must share `id`, `tags`, `related`,
  `capability`, `availability`, `process_shape`, `domain`. Translatable keys
  are `title` and `short`.

---

## 4. Canonical Section Order (strict)

Every help file uses **exactly this order**. Sections that do not apply are
either marked explicit-empty (`No user parameters.`, `No data ports.`) or
omitted only if §6 marks them optional. Order never changes.

```text
# <Title>                              ← H1
<short description>                    ← one paragraph, ≤ 3 sentences

## Tech Sheet                          ← Tier-2 anchor, machine-extractable
## Process                             ← what the operator does, abstractly
## Ports                               ← I/O ports (audio, typed-data, control)
## Parameters                          ← user-facing parameters
## Data                                ← typed-data semantics (schemas, units, ranges)
## Application                         ← when to use this; musical / sound-design intent
## Processing Modes                    ← RT / HQ / Data / Offline behaviour
## Requirements                        ← channels, dependencies, host contract
## Detailed Technical Description      ← the deep dive (algorithm, math, gotchas)
## Provenance                          ← upstream source / origin
## Tips                                ← short bullets
## See Also                            ← cross-links
```

The first six sections (Tech Sheet → Application) are the **public face**.
Detailed Technical Description → See Also are the **deep face**. A user
should be able to stop reading after Application and still know what the
operator is for.

### 4.1 Section content rules

#### Tech Sheet (required, machine-readable)

A fixed key/value block. Renderers parse this verbatim for Tier 2. Keys are
literal; values come from descriptor metadata.

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
- **Channel Policy:** <inputs → outputs>
- **Since:** <pack-version>
```

This block mirrors `OPERATOR_CONTRACT.md` §"Operator Technical Summary For
Lab". It is the operator's spec sheet. **No prose** belongs here.

#### Process (required)

One paragraph. Plain language. Describes *what the operator does* without
implementation detail. Audience: a sound designer who has never read a CDP
manual.

> *Bad:* "Calls `modify_loudness_gain()` with command-mode 1."
> *Good:* "Multiplies every audio sample by a gain factor, raising or
> lowering perceived loudness without changing timing."

#### Ports (required)

For each port, a sub-list:

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

If the operator has no ports of a kind, write `No data ports.` / `No control
ports.` explicitly. Silence is not allowed.

#### Parameters (required)

Per parameter, identical block:

```markdown
### <Display Name>

- **ID:** `<param_id>`
- **Type:** float | int | enum | trigger | bool | breakpoint | curve | text
- **Range:** <min> to <max>      (or: enum values, or: n/a)
- **Default:** <value>
- **Unit:** <unit or "linear factor", "dB", "Hz", "samples", …>
- **Modulatable:** yes | no | rt-only
- **Topology-sensitive:** yes | no
- **Available in:** realtime | HQ | both
```

Optional one-line note follows the block. `No user parameters.` if none.

#### Data (required if any typed-data port exists; otherwise `No typed data.`)

Describes what flows on typed-data ports: schema fields, units, sample rates,
expected ranges. This is where Faust `bargraph` data, Maximilian envelope
data, CDP analysis frames, etc., are documented. Tables are encouraged.

#### Application (required)

Two short paragraphs maximum. *When* would I reach for this operator? *What
musical/sound-design problem does it solve?* This is the only section
authored from the user's perspective rather than the operator's.

#### Processing Modes (required)

Bullets covering RT, HQ/offline, Data, latency, output-length behaviour.
Mirrors `engine.*` in the descriptor.

#### Requirements (required)

Channel constraints, mandatory upstream operators (e.g. PVOC analysis before
PVOC synth), host-contract version, sample-rate constraints, file-format
constraints (CDP soundfile lists), runtime dependencies (Faust libfaust
build, Maximilian header version).

#### Detailed Technical Description (required)

The deep dive. Algorithm sketch, math when relevant, internal stages, known
artefacts, performance characteristics, edge cases, numerical-stability
notes. This is where CDP "ON THE PROCESS" prose, Faust block-diagram notes,
and Maximilian class semantics land. Length: as long as it needs to be.

#### Provenance (required)

Upstream attribution. Per provider:

- **CDP** — source file, program, process, mode, command-mode (existing
  pattern in `xyona-cdp-pack/docs/HELP_STANDARDS.md`).
- **Faust** — `.dsp` source path (in pack), library version, original author
  if forked.
- **Maximilian** — header path, class name, upstream commit/version.
- **Core / Lab** — author, design notes file, related ROADMAP/REPORT
  documents.

#### Tips (optional but recommended)

≤ 6 bullets. Each tip is one short imperative sentence.

#### See Also (required if `related` non-empty)

Markdown links rendered from `related` IDs.

---

## 5. Per-Provider Adaptations

Every provider follows the same 13 sections. They differ only in **which
sections carry weight** and what goes in **Provenance**.

| Section | Core | CDP | Faust | Maximilian | Lab |
|---|---|---|---|---|---|
| Tech Sheet | required | required | required | required | required |
| Process | required | required | required | required | required |
| Ports | required | required | required | required | required |
| Parameters | required | required | required | required | required |
| Data | if typed | if typed (PVOC, pitch, …) | if typed (bargraph, soundfile) | if typed | if typed |
| Application | required | required | required | required | required |
| Processing Modes | required | required (RT+HQ explicit) | required | required | required |
| Requirements | required | required (channel/format) | required (libfaust) | required (header version) | required |
| Detailed Technical | required | "ON THE PROCESS" content | block-diagram notes | class semantics | algorithm |
| Provenance | author + design doc | CDP source/process/mode | `.dsp` path + libfaust | header + class + commit | author |
| Tips | optional | optional | optional | optional | optional |
| See Also | required-if | required-if | required-if | required-if | required-if |

No provider may add new top-level sections. Sub-headings inside a section are
free.

---

## 6. Minimal Operator Skeleton

For a parameterless utility, the skeleton still uses every required section:

```markdown
---
id: help.node.cdp.utility.identity
title: CDP Utility Identity
short: Pass audio through unchanged (CDP utility identity).
tags: [node, cdp, utility, identity]
provider: cdp
family: utility
operator: identity
capability: [rt, hq]
availability: insertable_rt
process_shape: stream
domain: time_audio
related: []
---

# CDP Utility Identity

Pass audio through unchanged (CDP utility identity).

## Tech Sheet

- **Operator ID:** `cdp.utility.identity`
- **Provider / Family:** CDP / utility
- **Operator Type:** stream
- **Capability:** RT+HQ
- **Availability:** insertable_rt
- **Process Shape:** stream
- **Domain:** time_audio
- **Materialization:** none
- **Output Length:** same as input
- **Host Contract:** abiV2
- **Channel Policy:** match_input
- **Since:** 0.1.0

## Process

Copies the input audio buffer to the output without modification.

## Ports

### in `xyona.audio` (input)

- Channels: any

### out `xyona.audio` (output)

- Channels: match_input

## Parameters

No user parameters.

## Data

No typed data.

## Application

Used as a placeholder while wiring patches, or as a structural anchor in
generated graphs. Not a creative operator.

## Processing Modes

- Realtime: supported.
- HQ/offline: supported.
- Output length: same as input.
- Latency: zero.

## Requirements

- One audio input and one audio output.
- Input and output channel counts must match.

## Detailed Technical Description

The operator performs a buffer copy. No DSP work is performed. Channel order
is preserved. No interpolation, dithering, or rate conversion is applied.

## Provenance

- CDP8 source: passthrough wrapper, no upstream CDP program.
- Authored: XYONA CDP pack.

## Tips

- Prefer a direct cable connection unless an explicit anchor node is needed.

## See Also

(none)
```

---

## 7. Validation & Release Gate

A help file is release-ready when **all** of the following hold:

1. File exists at canonical path for every required locale.
2. Frontmatter parses; required keys present; ID matches descriptor operator
   ID.
3. Section headings appear **in the canonical order** of §4, with no extra
   top-level sections.
4. Tech Sheet block is parseable as a key/value list with the canonical
   keys.
5. Every parameter listed in the descriptor has a matching `### <Name>` block
   under `## Parameters`, and vice versa.
6. Every public input/output port in the descriptor appears under `## Ports`.
7. `short` frontmatter ≤ 120 chars and matches the first prose line under H1.
8. `related` IDs resolve to existing help files.
9. For CDP, the pack-local CDP source policy in
   `xyona-cdp-pack/docs/HELP_STANDARDS.md` is satisfied (provenance, no raw
   CLI as primary instruction).
10. Locale parity: `en.md` and `de.md` have identical structure (same
    sections, same parameter blocks, same port blocks).

A workspace-level linter (`tools/help_lint`, to be authored) enforces 1–10.
Until that exists, reviewers enforce by hand using §4 + §6 as the diff
reference.

---

## 8. What This Replaces

- **Replaces nothing yet.** This is the workspace-level standard. Existing
  pack-local help docs (`xyona-cdp-pack/docs/HELP_STANDARDS.md`) become
  *extensions* of this standard — they are kept, but their section-order
  list is superseded by §4 here once the migration completes.
- The current CDP help files (e.g.
  `xyona-cdp-pack/src/operators/modify/loudness_gain/docs/en.md`) align with
  most of §4 already; missing sections are **Tech Sheet**, **Process**,
  **Ports**, **Data**, **Application**, **Detailed Technical Description**.
  Migration is incremental, operator-by-operator.

---

## 9. Open Questions (deliberately unresolved)

- Do we author Tech Sheet by hand, or generate it from `op.yaml` + descriptor
  metadata at build time? Recommendation: **generate**, then commit, so the
  file remains the source of truth for help rendering.
- Tier-2 sidebar rendering: do we extract from Markdown, or require an
  intermediate JSON? Recommendation: **extract** — keep Markdown as the
  single source.
- Do third-party packs (community-authored) inherit this contract verbatim?
  Recommendation: yes; §7 validation gates pack acceptance.
- How are video / image / interactive examples carried? Out of scope for v1
  of this standard; revisit when Lab help renderer ships.

---

## 10. Related Documents

- `OPERATOR_CONTRACT.md` — workspace operator contract (§"Help Contract",
  §"Operator Technical Summary For Lab").
- `OPERATOR_MODULE_AUTHORING_GUIDE.md` — module authoring rules.
- `xyona-cdp-pack/docs/HELP_STANDARDS.md` — CDP-pack-specific help rules.
- `xyona-cdp-pack/docs/CDP_PORT_TYPES.md` — CDP port type contract (feeds
  §"Ports" content).
- `ROADMAP_OPERATOR_PORT_TYPES_AND_PATCH_COMPATIBILITY.md` — port-type model
  driving the Ports section.
- `ROADMAP_OPERATOR_SLOT_SYSTEM.md` — slot system, surfaces in Tech Sheet
  via slot-aware parameters.
