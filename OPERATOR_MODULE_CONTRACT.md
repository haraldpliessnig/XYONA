# XYONA Operator Module Contract

**Status:** Workspace standard
**Version:** 1.3
**Date:** 2026-04-29
**Applies to:** `xyona-core`, `xyona-cdp-pack`, future operator packs, and
Lab-authored public host operators

## Intent

Public XYONA operators must expose one stable identity, naming, descriptor, and
help contract regardless of where the implementation lives. The contract
separates immutable machine identity from provider/family metadata, labels, UI
node names, engine domain, and host materialization.

This exists to prevent names such as `CDP:cdp.modify.loudness_gain1` and to
avoid drift between YAML, generated descriptors, C++ registration, help, tests,
and Lab discovery.

## No Backward-Compatibility Layer

The operator-module migration intentionally removed legacy naming and metadata
fallbacks. Do not reintroduce them.

Rules:

- Do not add compatibility aliases for old operator IDs or old module paths.
- Do not accept pack descriptors that omit required module identity metadata.
- Do not derive `provider`, `family`, `moduleName`, `ui.nodeNameStem`,
  `engine.domain`, or `engine.materialization` from IDs, labels, categories, or
  private file paths.
- Do not use provider-prefixed visible labels such as `CDP: Loudness Gain`.
- Do not create public operator modules under `src/processes`.
- Do not create public operator `meta.yaml` files.
- Do not create provider-prefixed source folders such as
  `src/operators/cdp.modify`.
- Do not create flat public CDP adapter files such as
  `src/operators/cdp_modify_loudness_gain.cpp`.

## Required Source Shape

Core operators, CDP pack operators, and future pack implementation modules use:

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

Not every optional subfolder is needed for every operator, but `op.yaml` is
required for every public implementation module.

Path rules:

- `<family>` is provider-local and must not include the provider namespace.
- `<family>` and `<module_name>` path parts must match `family` and
  `moduleName` in `op.yaml`.
- Shared implementation for multiple modules in the same family belongs in
  `src/operators/<family>/common/` and is not itself an operator module.
- Shared implementation must be declared explicitly where the generator needs
  it, for example with CDP pack `adapter.sharedSources`.

Lab-authored public host operators are currently declared in
`xyona-lab/specs/operators/lab-public.op.yaml` and must apply matching runtime
metadata through Lab's explicit descriptor metadata table. If Lab later moves
host operators into physical source modules, those modules must use the same
`src/operators/<family>/<module_name>/op.yaml` shape.

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
- ports: `ports.inputs[]` and `ports.outputs[]` with stable IDs, channel
  policy, tags, and typed-data metadata where relevant
- params: stable IDs plus descriptor facts for label, type, range, default,
  unit, group, display, precision, availability, scope, and visibility rules
- help: `help.node.<operator_id>` plus tags/locales where supported
- provenance and validation strategy for algorithmic operators

CDP-derived operators include CDP8 provenance with `sourceFile` under `dev/`
unless the operator is an explicitly technical synthetic fixture.

## Identity And Naming

| Field | Meaning | Example |
|---|---|---|
| `id` | Immutable machine identity for lookup, persistence, help, tests. | `cdp.modify.loudness_gain` |
| `provider` | Stable lowercase namespace of the shipping source. | `cdp` |
| `providerLabel` | Human provider label. | `CDP` |
| `family` | Provider-local family/type, without provider prefix. | `modify` |
| `moduleName` | Provider-local module identifier. | `loudness_gain` |
| `label` | Human operator name without forced provider/family prefix. | `Loudness Gain` |
| `ui.shortLabel` | Compact UI label. | `Loudness Gain` |
| `ui.nodeNameStem` | Canvas default instance-name stem. | `loud_gain` |

Rules:

- `provider` is required for every public operator. Current providers are
  `core`, `cdp`, and `lab`.
- Pack and Lab operator IDs must start with `<provider>.`.
- New pack IDs should normally use `<provider>.<family>.<moduleName>`.
- Core operator IDs may remain plain stable IDs such as `gain` or
  `signal_lfo`; the metadata must still declare `provider: core`, `family`, and
  `moduleName`.
- Existing Lab public IDs may remain stable product IDs such as `lab.audio_in`;
  the structural family is still carried in `family`.
- `moduleName`, parameter IDs, port IDs, and `ui.nodeNameStem` use lowercase
  ASCII snake_case. Hyphens are not allowed.
- `ui.nodeNameStem` must not contain dots or provider namespace fragments.
- Default Canvas names must be generated from `ui.nodeNameStem`, not from `id`.
- Palette, sidebar, and context-menu secondary labels must use the canonical
  owner/family context derived from `providerLabel` and `family`, formatted as
  `<Provider>/<Family Display>`, for example `Core/Dynamics`, `Core/Signal`,
  `CDP/Modify`, or `Lab/System Audio`.
- UI secondary labels must not use `category`, `id`, source paths, or
  provider-prefixed labels as owner/family context. `category` may still serve
  filtering or product grouping, but it is not the canonical owner context.

Example:

```yaml
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

The default node names are `loud_gain1`, `loud_gain2`, and so on. The persisted
operator ID remains `cdp.modify.loudness_gain`.

## Engine Taxonomy

Execution capability is expressed by:

- `capabilities.canRealtime`
- `capabilities.canHQ`

Process shape is one of:

- `block_length_preserving`
- `block_stateful_length_preserving`
- `whole_file_length_preserving`
- `whole_file_length_changing`
- `generator`
- `analysis_data_output`
- `typed_data_transform`
- `multi_output_or_multi_file_output`
- `host_source`
- `host_sink`
- `host_processor`

Domain is one of:

- `time_audio`
- `spectral_pvoc`
- `control_data`
- `generator`
- `hybrid`

Materialization is one of:

- `none`
- `audio_buffer`
- `audio_file`
- `spectral_data`
- `control_data`
- `report`
- `file_collection`

Whole-file and length-changing operators must not claim realtime support unless
there is an explicit realtime/preview contract.

## Descriptor And ABI Transport

The naming contract must reach Lab through public discovery. Private source
paths, C++ filenames, and pack-local naming conventions are not valid transport
surfaces.

The public descriptor/discovery surface consumed by Lab must expose:

- `provider`
- `providerLabel`
- `family`
- `moduleName`
- `label`
- `ui.shortLabel`
- `ui.nodeNameStem`
- `engine.processShape`
- `engine.domain`
- `engine.materialization`

Current implementation requirements:

- Core descriptors carry explicit module metadata generated from `op.yaml`.
- CDP pack descriptors and metadata are generated from module-local `op.yaml`.
- Pack metadata is parsed structurally by Core.
- Missing pack module metadata is a load/registration error.
- Lab-owned public operators apply explicit descriptor metadata and the
  registry rejects incomplete descriptors.
- Lab discovery and `NodeBinder` do not fill missing metadata from IDs, labels,
  categories, or private paths.

## Adapter Rules

Module-owned adapters stay under the module root:

```yaml
adapter:
  header: operators/edit/cut/adapter/cdp_edit_cut.h
  source: src/operators/edit/cut/adapter/cdp_edit_cut.cpp
  registrationFunction: registerEditCutV2
```

Shared implementation stays under the family `common` folder and is declared
explicitly:

```yaml
adapter:
  header: operators/edit/cutend/adapter/cdp_edit_cutend.h
  source: src/operators/edit/cutend/adapter/cdp_edit_cutend.cpp
  sharedSources:
    - src/operators/edit/common/cdp_edit_cut_sessions.cpp
  registrationFunction: registerEditCutEndV2
```

Do not point one module's `adapter.header` or `adapter.source` into another
module's adapter directory.

## Help Contract

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
help.node.lab.audio_in
```

Core and pack operator help belongs with the owning package. Lab owns Lab-only
panels, topics, workflows, and host-operator help. Lab must not author CDP or
Core DSP help as a substitute for the owning package.

## Validation Requirements

The shared validator must fail when:

- a public implementation module under `src/operators` lacks module-local
  `op.yaml`
- `src/processes` contains public operator sources/specs
- public operator `meta.yaml` is present
- provider-prefixed dotted source directories are present under `src/operators`
- flat public CDP adapter files are present under `src/operators`
- path family/module does not match `family` and `moduleName`
- adapter header/source paths leave the owning module root
- shared adapter sources leave `src/operators/<family>/common/`
- `provider`, `family`, `moduleName`, `ui.shortLabel`, `ui.nodeNameStem`,
  `engine.domain`, or `engine.materialization` is missing
- `family` repeats the provider namespace
- a pack or Lab operator ID does not start with `<provider>.`
- `ui.nodeNameStem` contains dots, provider fragments, or invalid characters
- labels are provider-prefixed with strings such as `CDP:`
- whole-file or length-changing operators claim realtime without an explicit
  contract
- generated descriptors, registration, or source lists are stale

Package-local runtime/spec tests then compare generated descriptors to runtime
discovery.

## Verification

Before committing operator-structure work:

- Run the affected repo's operator-module validator.
- Run generation staleness checks where the repo has generated artifacts.
- Run targeted build and CTest for the affected operator/discovery surface.
- Run Lab Canvas smoke tests when labels, node-name stems, descriptor metadata,
  or pack discovery change.
- Run `git diff --check`.

Use repo-local commands. The XYONA root is a workspace, not a monorepo build.

## References

- `OPERATOR_MODULE_AUTHORING_GUIDE.md` - practical authoring instructions.
- `ROADMAP_OPERATOR_MODULE_STRUCTURE.md` - completion record and remaining
  non-migration follow-ups.
- `REPORT_OPERATOR_MODULE_NAMING_STRUCTURE.md` - detailed slice-by-slice
  implementation report.
