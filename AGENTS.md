# XYONA Workspace Instructions

## Workspace Model

This directory is a workspace, not a monorepo product tree.

`/Users/haraldpliessnig/Github/XYONA` contains multiple independent repositories.
Always identify the actual repository before planning edits, running builds, or
describing git state.

Current workspace repositories:

- `xyona-core/` - host-agnostic C++ DSP/runtime foundation.
- `xyona-lab/` - JUCE host application, visual patcher, graph/UI/orchestration.
- `xyona-cdp-pack/` - LGPL CDP operator pack, built as a dynamic runtime pack.
- `CDP8/` - original/reference CDP code, used for study and validation.

There is also workspace-level state in the XYONA root. Do not treat a root git
status as the full state of the nested repositories. Check `git status` inside
the specific repo or repos you will touch.

## Repository Ownership

## Operator Module Authoring

Before adding, moving, or wiring any public operator, read
`OPERATOR_MODULE_AUTHORING_GUIDE.md` and `OPERATOR_MODULE_CONTRACT.md`.

Do not create flat public operator files, provider-prefixed module folders such
as `src/operators/cdp.modify`, provider-prefixed labels such as `CDP: ...`, or
Canvas default names derived from dotted operator IDs. Operator identity,
provider, family/type, module name, short label, node-name stem, engine domain,
materialization, ports, params, help, provenance, and generated descriptor
surfaces must come from the operator module contract.

Each package also has a package-local guide and, where present, a package-local
`AGENTS.md`. Follow those before package edits:

- `xyona-core/OPERATOR_MODULE_AUTHORING_GUIDE.md`
- `xyona-cdp-pack/OPERATOR_MODULE_AUTHORING_GUIDE.md`
- `xyona-lab/OPERATOR_MODULE_AUTHORING_GUIDE.md`
- `xyona-lab/AGENTS.md`

### xyona-core

`xyona-core` owns pure processing and host-agnostic deterministic runtime code:

- DSP algorithms and reusable DSP families.
- `xyona::Operator` implementations.
- Operator metadata/descriptors (`OpDesc`, `ParamDesc`, `IODesc`,
  capabilities, `meta.yaml`, generated metadata).
- Processing-level file I/O operators such as audio clip/file-out operators.
- Host-agnostic runtime kernels when they do not know about Lab, UI, projects,
  devices, graph plans, windows, timeline models, or product-specific bindings.

Core must remain UI-free and host-free. Do not add JUCE, Canvas, node graph,
device routing, windowing, project state, or Lab-specific schema knowledge to
core.

Core treats channels as generic channel counts. Semantic layouts such as mono,
stereo, 5.1, 7.1, immersive, and physical output mapping are Lab/host concerns.

### xyona-lab

`xyona-lab` is one host for `xyona-core`. It owns orchestration and product UI:

- Canvas, nodes, visual graph editing, patch cables, windowing, expanders.
- Graph building/execution (`AudioGraphBuilder`, `OfflineGraphBuilder`,
  `GraphPlan`, `AudioEngineManager`, realtime and offline engines).
- Audio/MIDI device I/O, MainBus, MonitoringSystem, physical output routing.
- Parameter UI/model binding, ParameterCenter, ParameterBar, undo/redo.
- Project state, persistence, render jobs, scheduling, cancellation, progress,
  render dialogs, and host-side caches.

Lab consumes core descriptors and calls core operators. Lab must not duplicate or
invent DSP formulas that belong in core or a pack.

For Lab-specific UI work, also follow `xyona-lab/AGENTS.md`.

### xyona-cdp-pack

`xyona-cdp-pack` is the separately licensed CDP operator pack.

- It is the LGPL component and must remain dynamically loadable/replaceable.
- It builds `xyona_pack_cdp_ops` as a shared library.
- It uses `xyona-core` package headers/C ABI surface and does not make Lab
  compile CDP algorithms directly.
- Its internal layering should stay: CDP algorithm/spec layer -> pack operator
  adapters -> Core pack descriptors/API -> Lab descriptor consumption.
- Lab discovers/loads the pack at runtime via `XYONA_OPERATOR_PACK_PATH` during
  development or from the bundled `operator_packs` folder in installed builds.

Do not move CDP pack algorithms into Lab. Do not make Lab depend directly on CDP
implementation files.

### CDP8

`CDP8` is reference code. Treat it as read-only unless the user explicitly asks
for changes in that repository.

Use CDP8 to understand original algorithms and produce validation references.
Ports and modernized implementations belong in `xyona-core` or, for separately
licensed CDP pack work, in `xyona-cdp-pack`.

## Dependency Shape

The intended dependency direction is:

```text
CDP8              reference only
xyona-core        independent DSP/runtime foundation
xyona-cdp-pack    dynamic pack built against core package/API
xyona-lab         host app; depends on core and loads packs at runtime
```

`xyona-lab` resolves core through `xyona-lab/cmake/xyona_core_provider.cmake`:

1. `XYONA_CORE_PATH` CMake/env variable.
2. Relative sibling path `../xyona-core`.
3. `find_package(xyona-core CONFIG)`.
4. FetchContent fallback at the pinned core tag.

Do not hardcode absolute core paths into Lab CMake files.

## Boundary Checklist

Before adding or moving code, classify the responsibility:

- Implements signal/audio/control DSP, analysis, synthesis, transforms,
  oversampling, accumulation, capture, layer mixing, render/file-out processing:
  `xyona-core` or `xyona-cdp-pack`.
- Defines operator metadata/capabilities or reusable DSP parameter semantics:
  `xyona-core` or the relevant pack.
- Manages nodes, graph topology, graph plans, execution scheduling, PDC wiring
  across nodes, render jobs, devices, buses, monitor profiles, UI, windows,
  project state, undo/redo, or persistence: `xyona-lab`.
- Studies original CDP behavior or creates golden references: `CDP8`.

When uncertain, prefer keeping algorithms below the host boundary and adapters
above it.

## Working Rules For Codex

- Start by determining which repository is relevant. Use repo-local paths,
  build scripts, tests, and git status.
- For cross-repo work, describe and verify each repo separately.
- Do not assume root-level commands cover nested repos.
- Preserve unrelated dirty work in any repo.
- For substantial tasks, read the relevant repo context first:
  - Workspace: `CONTEXT.md`
  - Core: `xyona-core/CONTEXT.md`
  - Lab: `xyona-lab/CONTEXT.md` and `xyona-lab/AGENTS.md`
  - Pack: `xyona-cdp-pack/README.md`
  - CDP reference: `CDP8/README.md`
- Prefer existing build scripts in the target repo. For Lab, `./build-dev.sh`
  is the preferred verification path when a build is needed.
