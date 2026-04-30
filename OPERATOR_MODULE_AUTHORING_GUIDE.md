# Operator Module Authoring Guide

This is the practical authoring guide for public XYONA operators. It applies to
`xyona-core`, `xyona-cdp-pack`, and Lab-authored public host operators. The
formal naming and descriptor vocabulary lives in `OPERATOR_MODULE_CONTRACT.md`;
port typing and patch compatibility live in
`OPERATOR_PORT_TYPE_AND_COMPATIBILITY_CONTRACT.md`. This guide states the exact
file and implementation structure to use.

## Required Source Shape

Public operator code must live in a module root:

```text
src/operators/<family>/<module_name>/
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

Required rules:

- `src/operators/<family>/<module_name>/op.yaml` is the authoritative operator
  module spec.
- `<family>` is provider-local. Source-module family folders use one safe path
  segment such as `modify`, `pvoc`, `utility`, `dynamics`, or `signal`.
  Multi-segment host families such as `system.audio` and `timeline.grid` are
  metadata values in Lab specs unless Lab introduces a dedicated physical
  module tree for them.
- Source folders may not contain dotted provider-prefixed names such as
  `cdp.modify` or `lab.system.audio`.
- `<module_name>` must match `moduleName` and the final operator ID segment.
- Public operator modules must not live under `src/processes`.
- Public operator modules must not use `meta.yaml`.
- Public CDP operators must not use flat `src/operators/cdp_*.cpp` or
  `src/operators/cdp_*.h` files.
- Shared implementation used by multiple modules in the same family belongs in
  `src/operators/<family>/common/`. It is not an operator module and must not
  contain `op.yaml`.

## Adapter Structure

Adapters are module-owned. A module that needs C++ adapter code places it under
its own `adapter/` directory:

```text
src/operators/edit/cut/
  op.yaml
  adapter/
    cdp_edit_cut.h
    cdp_edit_cut.cpp
```

The module spec must declare the adapter files:

```yaml
adapter:
  header: operators/edit/cut/adapter/cdp_edit_cut.h
  source: src/operators/edit/cut/adapter/cdp_edit_cut.cpp
  registrationFunction: registerEditCutV2
```

If multiple modules share implementation, keep registration adapters separate
and declare shared sources explicitly:

```yaml
adapter:
  header: operators/edit/cutend/adapter/cdp_edit_cutend.h
  source: src/operators/edit/cutend/adapter/cdp_edit_cutend.cpp
  sharedSources:
    - src/operators/edit/common/cdp_edit_cut_sessions.cpp
  registrationFunction: registerEditCutEndV2
```

Do not point one module's `adapter.header` or `adapter.source` at another
module's adapter directory.

## Required Naming

`op.yaml` owns identity and UI naming:

```yaml
schema: xyona-operator-v1
id: cdp.modify.loudness_gain
provider: cdp
providerLabel: CDP
family: modify
moduleName: loudness_gain
label: Loudness Gain
category: CDP/Modify
ui:
  shortLabel: Loudness Gain
  nodeNameStem: loud_gain
```

Rules:

- `id` is immutable and used for lookup, persistence, help, tests, and
  provenance.
- Pack and Lab IDs must start with `<provider>.`.
- `family` must not repeat `provider`.
- `moduleName`, parameter IDs, port IDs, and `ui.nodeNameStem` use lowercase
  ASCII snake_case. Hyphens are not allowed.
- `label` is human-facing text. Do not prefix it with provider text such as
  `CDP:`.
- `ui.shortLabel` is the compact palette/control label.
- `ui.nodeNameStem` is the only source for default Canvas node names. For
  example, `cdp.modify.loudness_gain` creates `loud_gain1`, not
  `cdp.modify.loudness_gain1`.
- Palette, sidebar, and context-menu secondary labels are derived by Lab from
  `providerLabel` and `family` as `<Provider>/<Family Display>`, for example
  `Core/Dynamics`, `CDP/Modify`, or `Lab/System Audio`. Do not use `category`,
  dotted IDs, source paths, or provider-prefixed labels for that UI context.

## Required Port Typing

Every public input and output in `op.yaml` must declare an explicit `type`.
Do not rely on tags, channel count, operator domain, port name, or Lab fallback
logic to imply a type.

```yaml
ports:
  inputs:
    - id: in
      type: xyona.audio.signal
      channelPolicy: any
  outputs:
    - id: out
      type: xyona.audio.signal
      channelPolicy: match_input
```

Typed-data ports must declare enough facts for compatibility without guessing:

```yaml
ports:
  outputs:
    - id: pvoc
      type: cdp.pvoc.analysis.v1
      kind: typed_data
      domain: spectral_pvoc
      rate: offline_artifact
      schema: xyona.cdp.pvoc.analysis.v1
      format: pvoc_analysis
      mergePolicy: single_source
```

Missing `type` or incomplete typed-data metadata is a contract error.

## Required `op.yaml` Surface

Every public operator spec declares:

- identity: `schema`, `id`, `provider`, `providerLabel`, `family`,
  `moduleName`
- display: `label`, `summary`, `description`, `operatorType`, `category`,
  `icon`, `version`, `ui.shortLabel`, `ui.nodeNameStem`
- ownership: `repository`, `license` where applicable, `algorithmOwner`,
  `hostBoundary`
- capabilities: `canRealtime`, `canHQ`
- engine: `processShape`, `domain`, `materialization`,
  `wholeFileRequired`, `lengthChanging`
- ports: `ports.inputs[]` and `ports.outputs[]` with stable IDs, explicit
  port types, channel policy, tags, and typed-data schema/format metadata
  where relevant
- params: stable IDs plus descriptor facts for label, type, range, default,
  unit, group, display, precision, availability, scope, and visibility rules
- help: `help.node.<operator_id>` plus tags/locales where supported
- provenance and validation strategy for algorithmic operators

CDP-derived operators include CDP8 provenance with `sourceFile` under `dev/`
unless the operator is an explicitly technical synthetic fixture.

## Generated Surfaces

Descriptor facts are generated or validated from `op.yaml`. Do not duplicate
them by hand unless the runtime value is genuinely dynamic.

Generated or validated surfaces include:

- operator metadata JSON
- parameter metadata and descriptors
- port metadata and descriptors
- top-level operator descriptors
- registration lists
- build source lists
- help/doc indexes

Adapters keep behavior code: lifecycle, parameter conversion, topology changes
that are genuinely runtime-dependent, DSP/offline-session calls, and ABI
registration glue.

## Package Placement

- `xyona-core`: host-free DSP/runtime operators under
  `src/operators/<family>/<module>/`. Core owns the shared validator and pack
  ABI.
- `xyona-cdp-pack`: dynamic LGPL CDP pack operators under
  `src/operators/<family>/<module>/`. CDP pack owns CDP provenance,
  generated pack descriptors, generated registration, generated source lists,
  and pack-local tests.
- `xyona-lab`: host/UI public operators are declared in Lab specs and explicit
  descriptor metadata. Lab consumes Core/pack descriptors through public
  discovery and must not infer names from private paths or dotted IDs.

## Verification

Before committing an operator-structure change, run the affected package's
validator, generation staleness check if it has one, targeted build, targeted
CTest, and any Lab smoke test that consumes the changed discovery surface.

Use repo-local commands. The workspace root is not a monorepo build.
