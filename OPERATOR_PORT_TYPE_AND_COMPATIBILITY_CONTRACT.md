# XYONA Operator Port Type And Patch Compatibility Contract

**Status:** Workspace standard
**Version:** 1.0
**Date:** 2026-04-30
**Applies to:** `xyona-core`, `xyona-lab`, `xyona-cdp-pack`, future operator
packs, and Lab-authored public host operators

## Intent

XYONA operator patching is port-based. Operator domain describes what an
operator does; port type describes what flows through a connection. Canvas
wiring, graph building, project persistence, pack metadata, and tests must use
the same explicit port contract.

This contract exists to prevent hidden assumptions such as "missing port type
means audio", "spectral operator cannot have audio ports", or "generic `in_0`
and `out_0` names are enough to decide patch compatibility".

## No Legacy Port Compatibility Mode

There are no legacy project contracts to preserve. Do not add compatibility
fallbacks for untyped public ports.

Rules:

- Every public operator input and output port must declare an explicit
  `type`.
- A missing port type is a contract error, not a warning.
- Lab must not infer missing port types from port ID, operator ID, label,
  category, engine domain, tags, channel count, or source path.
- Generic Canvas names such as `in_0` and `out_0` are never semantic
  substitutes for descriptor port IDs.
- Project state must persist stable descriptor port IDs.

## Ownership

- `xyona-core` owns host-neutral port type descriptors, validation vocabulary,
  descriptor transport, pack ABI metadata surfaces, and compatibility facts
  that are independent of any UI.
- `xyona-cdp-pack` owns CDP-specific port type declarations and schema facts,
  for example PVOC analysis data, pitch tracks, envelope files, and breakpoint
  lists.
- `xyona-lab` owns Canvas rendering, drag highlighting, connection blocking,
  import validation, GraphBuilder revalidation, and visual tokens for port
  types.
- `CDP8` is reference only. It can justify CDP type semantics, but modern
  descriptors and validation belong in Core and the CDP pack.

## Port Type Model

Every public descriptor port must resolve to a port type record with these
facts:

| Field | Meaning | Example |
|---|---|---|
| `type` | Stable namespaced port type ID. | `xyona.audio.signal` |
| `kind` | Broad runtime class. | `audio`, `control`, `event`, `midi`, `typed_data` |
| `domain` | Fachlicher signal/data Bereich. | `time_audio`, `spectral_pvoc`, `control_data` |
| `rate` | Execution/data cadence. | `audio_rate`, `control_rate`, `event_rate`, `offline_artifact` |
| `schema` | Required payload/schema contract for typed data. | `xyona.cdp.pvoc.analysis.v1` |
| `format` | Concrete data format/profile where needed. | `pvoc_analysis`, `breakpoint_curve` |
| `channelPolicy` | Channel behavior. | `mono`, `stereo`, `any`, `match_input`, `fixed_n` |
| `mergePolicy` | Whether multiple incoming edges can merge. | `sum`, `merge`, `single_source` |
| `executionContext` | Runtime limits. | `realtime`, `offline`, `realtime_or_offline` |

YAML shape:

```yaml
ports:
  inputs:
    - id: in
      type: xyona.audio.signal
      channelPolicy: any
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

The exact on-disk field layout may evolve, but the generated descriptor and
public discovery surface must expose enough information for Lab to decide
compatibility without guessing.

When generated JSON metadata uses `xyona.schema` as the metadata envelope
marker, the typed-data payload schema must be emitted under a non-conflicting
key such as `xyona.dataSchema` and mapped into descriptor `schema`.

## Built-In Type Vocabulary

Core provides the small canonical vocabulary. It is not an exhaustive list of
all future formats; packs may add namespaced concrete types that map to these
broad kinds.

| Type ID | Kind | Domain | Notes |
|---|---|---|---|
| `xyona.audio.signal` | `audio` | `time_audio` | Realtime or block audio signal. |
| `xyona.audio.buffer` | `typed_data` | `time_audio` | Materialized audio buffer or whole-file artifact. |
| `xyona.control.cv` | `control` | `control_data` | Continuous scalar/modulation value. |
| `xyona.control.gate` | `event` | `control_data` | Gate/trigger edge. |
| `xyona.control.clock` | `event` | `control_data` | Clock/transport pulse. |
| `xyona.midi.v1` | `midi` | `control_data` | MIDI 1.0 event stream. |
| `xyona.midi.mpe.v1` | `midi` | `control_data` | MPE profile, compatible only by rule. |
| `xyona.midi.v2` | `midi` | `control_data` | Reserved future MIDI 2.0 profile. |
| `xyona.visual.stream` | `visual` | `visual_data` | Analyzer/visual streams if made patchable. |

CDP and other packs add concrete typed-data IDs under their namespace, for
example `cdp.pvoc.analysis.v1`.

## Compatibility Rules

Compatibility is decided by port facts, not by operator facts.

Default rules:

- `xyona.audio.signal` connects to `xyona.audio.signal`.
- `xyona.control.cv` connects to `xyona.control.cv`.
- `xyona.control.gate` connects to `xyona.control.gate`.
- `xyona.control.clock` connects to `xyona.control.clock`.
- MIDI ports connect only when the MIDI profile compatibility rule allows it.
- Typed-data ports connect only when `type`, `schema`, and `format` are
  compatible.
- A typed-data port does not connect directly to an audio signal port.
- An audio signal port does not connect directly to a typed-data input.
- Cross-domain conversion requires an explicit operator.

Valid spectral example:

```text
xyona.audio.signal -> cdp.pvoc.anal.in
cdp.pvoc.anal.pvoc -> cdp.pvoc.synth.pvoc
cdp.pvoc.synth.out -> xyona.audio.signal
```

Invalid examples:

```text
cdp.pvoc.analysis.v1 -> xyona.audio.signal
xyona.audio.signal -> cdp.pvoc.analysis.v1
cdp.pvoc.analysis.v1 -> xyona.control.cv
```

## Operator Domain Is Not Patch Compatibility

`engine.domain` remains important for scheduling, palette grouping, help, and
runtime capability decisions. It must not be used as the only patchability
rule.

Examples:

- A spectral PVOC analysis operator may have an audio input and a PVOC
  typed-data output.
- A spectral PVOC synthesis operator may have a PVOC typed-data input and an
  audio output.
- A time-audio operator may be incompatible with PVOC typed data even when both
  are offline-capable.

The rule is:

```text
operator domain = what the operator does
port type       = what flows through the connection
compatibility   = whether this exact connection may exist
```

## Extension Rules For Future Packs

Future packs such as Faust, Maximilian, or vendor-specific XYONA packs may
register namespaced port types. New concrete types must:

- use a stable namespaced ID, for example `faust.audio.signal` or
  `vendor.spectral.frame.v1`
- map to a known broad `kind`
- declare `domain`, `rate`, and `executionContext`
- declare `schema` and `format` for typed data
- declare compatibility with built-in or pack-local types explicitly
- avoid relying on Lab-specific colors, icons, or renderer behavior

Core should only grow a new broad `kind` when a new runtime class genuinely
cannot be modeled by the existing vocabulary.

## Enforcement Points

This contract must be enforced at multiple layers:

- Operator module validators reject missing or incomplete port type metadata.
- Generated descriptors expose stable descriptor port IDs and type facts.
- Pack loaders reject invalid public descriptors for normal discovery.
- Lab discovery does not repair incomplete descriptors.
- Canvas drag highlighting only marks compatible targets.
- Canvas connection creation rejects incompatible edges.
- Project import rejects or quarantines invalid edges.
- GraphBuilder validates compatibility again before execution.
- Tests cover valid and invalid audio, control, MIDI, and typed-data edges.

## Visual Tokens

Port colors, icons, tooltip text, and hit-target styling are Lab concerns. They
must be derived from port type facts through a Lab registry, not hardcoded in
individual node renderers.

Core and packs may provide semantic facts. They must not provide JUCE colors or
Canvas layout rules.

## Initial Implementation Plan

1. Add contract docs and AGENTS references in Root, Core, Lab, and CDP pack.
2. Extend Core descriptor/metadata surfaces with explicit port type facts.
3. Make Core and pack validators fail on untyped public ports.
4. Update CDP PVOC operators to declare `cdp.pvoc.analysis.v1` consistently.
5. Update Lab public operator specs and runtime metadata to carry port types.
6. Replace generic Canvas semantic wiring with descriptor port IDs.
7. Add a central Lab connection compatibility service.
8. Wire compatibility into drag highlighting, connection creation, import, and
   GraphBuilder validation.
9. Add focused tests before broad UI polish.
