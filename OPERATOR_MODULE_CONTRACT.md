# XYONA Operator Module Contract

**Status:** Workspace standard  
**Version:** 1.0-draft  
**Date:** 2026-04-27  
**Applies to:** `xyona-core`, `xyona-cdp-pack`, future operator packs, Lab help consumption

## Intent

All public XYONA operators must be authored, documented, indexed, and exposed
through the same structure, independent of whether the operator ships in
`xyona-core` or in a dynamic pack.

This contract exists because the current workspace has several partially
overlapping conventions:

- Core operators use process folders, `meta.yaml`, generated JSON, C++ runtime
  descriptors, and operator help files.
- CDP pack operators use flat C++ files with C ABI descriptors and JSON metadata
  embedded in code.
- Lab has its own filesystem help layout and a generated help index.
- CDP8 has useful original process documentation, but its user text is CLI- and
  CDP-specific, not a Lab-ready help format.

The standard below is the canonical shape. Existing code can migrate in phases,
but new public operators should follow this contract.

## Required Module Shape

Every public operator must have one module root:

```text
src/operators/<family>/<module>/
  op.yaml
  README.md
  docs/
    en.md
    de.md
  dsp/
  adapter/
  tests/
  golden/
```

For legacy Core code, the same internal shape may temporarily live under:

```text
src/processes/<family>/<module>/
```

The target path is `src/operators`. `src/processes` is a compatibility location,
not a different standard.

## Required Files

`op.yaml` is required for every public operator.

`docs/en.md` is required for every public operator.

`docs/de.md` is required for all release-ready operators. During development it
may lag behind, but release validation must fail if the German file is missing.

`README.md` is required for non-trivial operators and recommended for all
operators. It is developer-facing. The HelpCenter uses `docs/<locale>.md`, not
the module README.

Tests are required for every implemented operator. Operators that cannot have a
stable audio golden reference must still have descriptor and behavioral tests.

## Offline ABI Guardrail

The current whole-buffer offline ABI, currently named `offline_packs_v1`, is a
prototype/reference surface only. If represented in an operator module, use an
explicit prototype name such as `adapter/offline_whole_buffer_prototype.cpp`, not
a name that implies a released production ABI. The prototype may describe
bounded, same-length, whole-buffer operators such as the current CDP
loudness-normalise slice while the production Offline Session ABI is being
built.

Production-scale offline operators must target the session/streaming offline
contract once the Offline Session ABI exists. This includes length-changing,
PVOC/spectral, multi-output, multi-file, long-running, or large-source CDP
operators.

The module contract must therefore be able to describe both:

- a prototype whole-buffer adapter for bounded same-length work
- a production offline-session adapter for streamed execution, progress,
  cancellation, output-length discovery, and host asset/scratch policy

Before release, public operators that still use the prototype whole-buffer ABI
must be ported to the Offline Session ABI, or the prototype surface must be
explicitly scoped as an internal test helper instead of a pack contract.

## `op.yaml` Ownership

`op.yaml` is the source of truth for:

- public operator ID
- provider namespace
- family and module name
- label, summary, description, category, icon, version
- operator type
- RT/HQ capabilities
- engine/process shape
- input/output port descriptors
- parameter descriptors
- parameter availability and scope
- help ID, locale list, tags, and related articles
- provenance
- validation strategy
- host boundary and ownership

C++ code is the source of truth only for behavior.

## Required `op.yaml` Fields

Minimum schema:

```yaml
schema: xyona-operator-v1

id: cdp.modify.loudness_gain
provider: cdp
family: cdp.modify
moduleName: loudness_gain
label: CDP Modify Loudness Gain
summary: Adjusts loudness by a linear CDP gain factor.
description: |
  CDP8 rewrite of modify loudness mode 1.
operatorType: processor
category: CDP/Modify
icon: volume-2
version: 0.1.0

ownership:
  repository: xyona-cdp-pack
  license: LGPL-2.1-or-later
  algorithmOwner: pack
  hostBoundary: no_lab_dependencies

capabilities:
  canRealtime: true
  canHQ: true

engine:
  processShape: block_length_preserving
  outputLength: same_as_input
  wholeFileRequired: false
  lengthChanging: false
  audioOutput: true
  multiOutput: false
  abiV2Support: direct

ports:
  inputs: []
  outputs: []

params: []

help:
  id: help.node.cdp.modify.loudness_gain
  locales: [en, de]
  tags: [node, cdp, modify, loudness, gain]
  related: []

validation:
  strategy: analytic_golden_buffer
```

CDP-derived operators must also include:

```yaml
provenance:
  source: cdp8
  cdp:
    library: modify
    program: modify
    process: loudness
    mode: LOUDNESS_GAIN
    processNumber: 195
    modeNumber: 0
    commandMode: 1
    sourceFile: dev/modify/gain.c
```

## Operator ID Rules

Core operator IDs use plain stable IDs:

```text
gain
hq_gain
slot_gain
signal_lfo
```

Pack operator IDs must start with the pack provider namespace:

```text
cdp.utility.identity
cdp.modify.loudness_gain
cdp.modify.space_mirror
```

The filesystem path is not authoritative. `op.yaml:id` is authoritative.

## Help ID Rules

Every public operator help article uses:

```text
help.node.<operator_id>
```

Examples:

```text
help.node.gain
help.node.slot_gain
help.node.cdp.utility.identity
help.node.cdp.modify.loudness_gain
```

The HelpCenter must treat Core and pack operators identically after discovery.

## Help File Front Matter

All operator help files must start with YAML front matter:

```yaml
---
id: help.node.<operator_id>
title: <Display Name>
tags: [node, <provider-or-domain>, <feature>]
related: []
---
```

Rules:

- `id` must match `op.yaml:help.id`.
- `title` should match the user-facing operator label unless localization needs
  a natural translation.
- `tags` must include `node`.
- Pack docs must include the provider tag, for example `cdp`.
- CDP-derived docs should include family/process tags such as `modify`,
  `loudness`, or `space`.
- `related` may be empty but must be present in release-ready docs.

## Help File Content Order

Use the same structure across all operators:

```text
# Title

Brief behavior description.

## Parameters

## Usage

## Processing Modes

## Requirements

## Provenance

## Tips

## See Also
```

`## Provenance` is required for CDP-derived operators. For non-CDP operators it
may be omitted.

`## Parameters` must state "No user parameters" for parameterless operators.

`## Processing Modes` must match `op.yaml:capabilities`.

`## Requirements` must document channel count, whole-file requirements, and any
host contract that matters to the user.

## CDP Documentation Policy

CDP8 documentation and CDP8 CLI usage text are reference material, not direct
HelpCenter content.

Use CDP docs to extract:

- original command name
- original mode number/name
- parameter meaning and ranges
- file shape requirements
- behavior notes and edge cases

Then rewrite the help into XYONA structure:

- Lab/node language instead of CLI-only language
- RT/HQ behavior stated explicitly
- parameter names matching XYONA descriptors
- channel and whole-file requirements stated as host requirements
- CDP provenance preserved in `## Provenance`

Do not paste large CDP manual sections directly into XYONA help. The help files
must be authored as XYONA operator documentation.

## Generated Artifacts

From `op.yaml`, generation or validation should cover:

- runtime descriptor helpers
- generated JSON metadata
- pack ABI descriptor arrays
- registration lists
- help metadata
- docs install manifests
- CMake source lists
- descriptor smoke tests

Hand-written descriptor data is allowed only during migration and must be
validated against `op.yaml`.

## Validation Requirements

A repository-level validator should fail if:

- a public operator lacks `op.yaml`
- `docs/en.md` is missing
- release mode lacks `docs/de.md`
- help front matter ID does not match `op.yaml:help.id`
- a parameter in `op.yaml` is missing from help
- RT/HQ capability docs disagree with metadata
- a pack operator ID does not start with `<provider>.`
- a CDP operator lacks provenance
- a whole-file or length-changing operator claims realtime without an explicit
  realtime contract
- a prototype whole-buffer adapter is used for length-changing, PVOC/spectral,
  multi-output, multi-file, long-running, or large-source production work
- a production offline operator lacks a declared Offline Session ABI contract
  once that ABI is available
- generated JSON is stale or missing
- registration omits an implemented operator

## Lab Consumption Contract

Lab owns HelpCenter UI and Lab-only docs. Lab does not own operator help for
Core or packs.

Lab help namespaces:

```text
help.node.*      Core and pack operators
help.panel.*     Lab panels/windows
help.topic.*     Lab concepts and technical topics
help.workflow.*  Lab workflows/how-tos
```

Lab-only source files:

```text
docs/help/lab/<locale>/nodes/
docs/help/lab/<locale>/panels/
docs/help/lab/<locale>/topics/
docs/help/lab/<locale>/workflows/
```

Pack/Core operator source files:

```text
src/operators/<family>/<module>/docs/<locale>.md
```

During migration, Core may still expose:

```text
src/processes/<family>/<module>/docs/<locale>.md
```

Lab should consume operator help through Core's public discovery/help surface
whenever possible, not by hardcoding private pack source paths.

## References

- `ROADMAP_OPERATOR_MODULE_STRUCTURE.md` - migration plan and rationale.
- `xyona-core/src/processes/HELP_STANDARDS.md` - Core compatibility standard.
- `xyona-cdp-pack/docs/HELP_STANDARDS.md` - CDP pack authoring standard.
- `xyona-lab/docs/help/lab/README.md` - Lab-only help layout.
