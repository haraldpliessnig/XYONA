# Operator Module Authoring Guide

This guide is the practical companion to `OPERATOR_MODULE_CONTRACT.md`.
Follow it before adding, moving, or wiring any public operator in Core, Lab, or
a runtime pack.

## Canonical Module Shape

Every new public operator must have one module root:

```text
src/operators/<provider-local-family>/<module_name>/
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

`family` is provider-local. Use `modify`, `pvoc`, `utility`,
`system.audio`, or `timeline.grid`; never use provider-prefixed family folders
such as `cdp.modify` or `lab.system.audio`.

Current legacy Core code may still exist under `src/processes` while the Core
folder migration is active. Do not create new flat operator files or new
provider-prefixed folders. If a repository cannot yet build from
`src/operators`, add the smallest migration slice first or document the
temporary exception in that package.

## Naming Rules

`op.yaml` is authoritative for identity and UI naming.

Required identity fields:

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

- `id` is the immutable machine identity for lookup, persistence, help, tests,
  and provenance.
- Pack and Lab IDs must start with `<provider>.`.
- `family` must not repeat `provider`.
- `moduleName`, parameter IDs, and `ui.nodeNameStem` use lowercase ASCII
  snake_case. Do not use hyphens.
- `label` is a human label. Do not prefix it with `CDP:` or provider/family
  text that belongs in metadata.
- `ui.nodeNameStem` is the Canvas default-name stem. It must not contain dots or
  provider namespace fragments. `cdp.modify.loudness_gain` should create
  `loud_gain1`, not `cdp.modify.loudness_gain1`.

## `op.yaml` Contents

Every public operator spec must declare:

- identity: `id`, `provider`, `providerLabel`, `family`, `moduleName`
- display: `label`, `summary`, `description`, `category`, `icon`, `version`,
  `ui.shortLabel`, `ui.nodeNameStem`
- ownership: repository, license, algorithm owner, host boundary
- capabilities: `canRealtime`, `canHQ`
- engine: `processShape`, `domain`, `materialization`, whole-file and
  length-changing flags
- ports: input/output IDs, channel policy, typed-data tags, and data metadata
- params: IDs plus descriptor facts for label, type, range, default, unit,
  group, display, precision, and RT/HQ availability
- help: `help.node.<operator_id>`, locales/tags where supported
- provenance and validation strategy

CDP-derived operators must include CDP8 provenance with `sourceFile` under
`dev/` unless the operator is explicitly marked as a technical synthetic host
fixture.

## Layering

Use these ownership boundaries:

- `dsp/`: host-agnostic DSP and data transforms only.
- `adapter/`: Core operator or pack ABI lifecycle, parameter conversion,
  descriptor binding, and registration.
- `docs/`: HelpCenter prose with front matter matching `help.node.<id>`.
- `tests/`: descriptor, behavior, host-contract, and golden validation.
- `golden/`: fixtures and manifests when a stable reference exists.

Lab does not own Core or CDP DSP. Lab-authored public operators are host
operators and still need the same identity and naming metadata.

## Generated Surfaces

Descriptor facts should be generated or validated from `op.yaml`, not repeated
by hand:

- operator metadata JSON
- parameter metadata and parameter descriptors
- port metadata and port descriptors
- top-level operator descriptors
- registration lists
- build source lists
- help/doc indexes

Adapters should keep behavior code and reference generated descriptor surfaces.

## Verification

Before committing an operator-structure change, run the affected package's
validator, generation staleness check, targeted build, targeted CTest, and any
Lab smoke test that consumes the operator discovery surface.

Use repo-local commands. The workspace root is not a monorepo build.

## Package Notes

- `xyona-core`: Core operators are host-free DSP/runtime operators. Current
  legacy modules under `src/processes` are migration debt; new structure should
  move toward `src/operators/<family>/<module>/op.yaml`.
- `xyona-cdp-pack`: CDP operators must be dynamic-pack modules under
  `src/operators/<family>/<module>/` and must use the generated descriptor,
  registration, and source-list pipeline.
- `xyona-lab`: Lab owns host/UI public operators and HelpCenter consumption.
  It must consume Core/pack metadata through public discovery and must not
  infer names from private folders or dotted IDs.
