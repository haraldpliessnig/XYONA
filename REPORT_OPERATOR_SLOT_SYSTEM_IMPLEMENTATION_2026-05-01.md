# Report: Operator Slot System Implementation

Date: 2026-05-01
Branch: `operator-slot-system`
Roadmap: `ROADMAP_OPERATOR_SLOT_SYSTEM.md`
Contract: `OPERATOR_CONTRACT.md`
Planning report: `REPORT_OPERATOR_SLOT_SYSTEM_2026-05-01.md`
Repositories: `xyona-core`, `xyona-lab`, `xyona-cdp-pack`

## Execution Rules

- Implement the roadmap as reviewable commits or small commit groups.
- Keep the same branch name in all affected repositories.
- Test locally after each batch.
- Commit and push each completed batch.
- Run GitHub Actions at the end when workflows are available.
- Do not merge at the end.

## CI Availability

Checked before implementation:

| Repository | GitHub Actions |
|---|---|
| `xyona-core` | `CI` workflow available |
| `xyona-lab` | `CI` workflow available |
| `xyona-cdp-pack` | `CI` workflow available |
| workspace root `XYONA` | no workflow present |

## Branches

Created and pushed:

| Repository | Branch |
|---|---|
| workspace root `XYONA` | `operator-slot-system` |
| `xyona-core` | `operator-slot-system` |
| `xyona-lab` | `operator-slot-system` |
| `xyona-cdp-pack` | `operator-slot-system` |

## Batch 1 - Contract Transport

Scope:

- Roadmap commits 02-07.
- Core slot descriptor types, parser/codegen, helpers, `slot_gain` migration,
  pack ABI slot transport.
- CDP generator and validator slot metadata transport.

### `xyona-core`

Commits:

| Roadmap | Commit | Summary |
|---|---|---|
| 02 | `c5e3619` | Add core slot descriptor fields |
| 03 | `4362c12` | Teach core codegen slot schema |
| 04 | `1233e5f` | Add core slot descriptor helpers |
| 05 | `bb93859` | Migrate slot gain to canonical slots |
| 06 | `81d3711` | Extend pack ABI with slot metadata |

Implemented facts:

- `SlotSupportDesc` and `SlotMapping` are public descriptor facts.
- `IODesc`, `PortDesc`, and `VariablePortRangeDesc` can carry optional
  `slotMapping`.
- `OpDesc` carries canonical `slots` metadata while legacy routing fields stay
  available as migration transport.
- Core codegen parses and validates `slots.*` and per-port `slotMapping`.
- Validator requires `slotMapping` only for slottable operators and rejects
  slot-addressable metadata on non-slottable operators.
- `slot_gain` is migrated to `slots.supported=true`,
  `defaultCount=1`, `countParamId=slot_count`, and `per_slot` descriptor ports.
- Pack ABI v2.2 transports slot support and per-port slot mapping through
  `struct_size`-gated fields.

Local verification:

```text
cmake --build build --target xyona_core
./build/tests/test_operator_module_runtime
./build/tests/test_signal_processes
./build/tests/test_operator_dispatcher
./build/tests/test_operator_packs
cmake --build build --target test_offline_session_abi test_dsp_quality -- -j8
./build/tests/test_offline_session_abi
./build/tests/test_dsp_quality
ctest --test-dir build --output-on-failure
```

Result:

- Full Core CTest passed: 11/11.

### `xyona-cdp-pack`

Commits:

| Roadmap | Commit | Summary |
|---|---|---|
| 07 | `14b2fad` | Teach CDP generator slot metadata |

Implemented facts:

- CDP metadata generator parses and validates `slots.*` and `slotMapping`.
- CDP generator rejects `slotMapping` on non-slottable operators.
- CDP generator rejects slottable ports that omit `slotMapping`.
- Generated metadata JSON contains slot metadata defaults.
- Generated pack descriptors use ABI v2.2 slot-capable descriptor sizes.
- Existing CDP operators remain non-slottable.

Local verification:

```text
../xyona-core/venv/bin/python scripts/generate_operator_metadata.py --root .
../xyona-core/venv/bin/python scripts/generate_operator_metadata.py --root . --check
cmake --build build/macos-clang-debug --target xyona_pack_cdp_ops -- -j8
ctest --test-dir build/macos-clang-debug --output-on-failure
```

Result:

- Full CDP CTest passed: 21/21.

## Batch 2 - Lab Model And Persistence

Status: pending.

Planned roadmap scope:

- Commit 08: Lab structured endpoint address.
- Commit 09: Lab persistence migration and legacy fixtures.
- Commit 10: connection model split between channel lanes and slot endpoint
  coordinates.
- Commit 11: central port resolver service.

## Batch 3 - Lab Behavior And Runtime

Status: pending.

Planned roadmap scope:

- Commit 12: slot UI model.
- Commit 13: slot count editing.
- Commit 14: per-slot parameter UX and slot-index validation.
- Commit 15: GraphBuilder slot expansion.
- Commit 16: runtime parameter snapshot slot resolution.
- Commit 17: multichannel slot cables.

## Hardening

Status: pending.

Planned roadmap scope:

- Commit 18: product reference operator.
- Commit 19: end-to-end tests.
- Commit 20: documentation and cleanup.

## Current Decision State

Batch 1 is implemented, tested locally, committed, and pushed in the affected
code repositories. Lab implementation must start from the descriptor facts now
available through Core and pack metadata, not from the old routing policy model.
