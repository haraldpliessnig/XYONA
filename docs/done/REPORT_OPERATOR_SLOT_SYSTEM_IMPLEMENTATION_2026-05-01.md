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
| 05 docs | `ffd5b51` | Clarify slot gain slot groups |

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
| 20 docs | `4181fa3` | Align CDP docs with operator contract wording |

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

Status: implemented, tested, committed, and pushed.

Scope:

- Commit 08: Lab structured endpoint address.
- Commit 09: Lab persistence migration and legacy fixtures.
- Commit 10: connection model split between channel lanes and slot endpoint
  coordinates.
- Commit 11: central port resolver service.

### `xyona-lab`

Commits:

| Roadmap | Commit | Summary |
|---|---|---|
| 08 | `86c90e09` | Add lab structured endpoint model |
| 09 | `e186a412` | Persist structured connection endpoints |
| 10 | `aaf0e94a` | Split connection endpoint pairs from lanes |
| 11 | `fef9cf8f` | Centralize lab endpoint compatibility |

Implemented facts:

- Lab has an explicit `EndpointAddress` value object carrying
  `nodeId`, `descriptorPortId`, optional `channelIndex`, and optional
  `slotIndex`.
- Descriptor-backed visible IDs resolve through descriptor facts, including
  channel expansion and per-slot expansion.
- Legacy slottable mono aliases such as `in_2` / `out_2` are recognized only
  when descriptor facts prove a mono `per_slot` port.
- Project persistence writes structured `srcEndpoint` / `dstEndpoint` facts
  while retaining legacy string fields for compatibility.
- Connection lanes remain as multichannel bundle transport, while slot
  coordinates are represented as endpoint facts.
- Duplicate detection and `single_source` input checks compare canonical
  endpoint addresses, so text aliases cannot bypass slot identity.
- Mouse hover/visual facts, connection creation, project import, and
  GraphBuilder descriptor classification use the shared endpoint resolver path.
- Slot-mapping compatibility rejects invalid slot coordinates on `shared`
  ports and requires explicit coordinates for `per_slot` ports when the
  effective slot count is greater than one.

Local verification:

```text
cmake --build build/macos-dev --target xyona_lab_tests -- -j8
./build/macos-dev/tests/xyona_lab_tests --test="Connection System" --xyona-only --summary-only
```

Result:

- Targeted Lab slot/connection scope passed: 32 tests, 121 passes, 0 failures.

Additional broad check:

```text
ctest --test-dir build/macos-dev --output-on-failure
```

Result:

- Not used as a passing gate for this batch in the current local buildtree.
- Failing/not-run cases were unrelated setup or pre-existing broad-suite
  failures:
  - Core-local CTest entries could not run because
    `build/macos-dev/xyona-core-local/tests/*` executables were absent.
  - `xyona_lab_cdp_offline_smoke` failed because
    `XYONA_OPERATOR_PACK_PATH` was not set.
  - Full `xyona_lab_tests` reported existing `CommitRouter.cpp` JUCE assertion
    failures outside the operator-slot connection scope.

## Batch 3 - Lab Behavior And Runtime

Status: implemented, tested, committed, and pushed.

Scope:

- Commit 12: slot UI model.
- Commit 13: slot count editing.
- Commit 14: per-slot parameter UX and slot-index validation.
- Commit 15: GraphBuilder slot expansion.
- Commit 16: runtime parameter snapshot slot resolution.
- Commit 17: multichannel slot cables.

### `xyona-lab`

Commits:

| Roadmap | Commit | Summary |
|---|---|---|
| 12 | `a747bc9e` | Model lab slot UI facts |
| 13 | `23e9b872` | Handle slot count topology edits |
| 14 | `4db86e56` | Validate per-slot parameter addresses |
| 15 | `93172ab4` | Expand graph slots into runtime ports |
| 16 | `672e1fa8` | Resolve runtime slot parameter snapshots |
| 17 | `8a121969` | Cover multichannel slot cables |

Implemented facts:

- `CorePayload` derives a `NodeSlotUiModel` from canonical descriptor facts:
  slot support, default/min/max/count-param facts, slot groups, slot labels,
  per-slot parameter IDs, and input/output slot mapping.
- Slot count topology edits are detected through `slots.countParamId` even when
  the parameter descriptor was not manually flagged as topology.
- Slot count shrink/restore updates visible ports, removes out-of-range slot
  wires, and keeps surviving slot-zero connections normalized.
- Per-slot parameter writes, clears, and value-source writes are rejected unless
  the operator is slottable, the parameter supports `ParamScope::PerSlot`, and
  `slotIndex` is within the effective slot count.
- Core operator host adapters expose Lab-visible slot endpoint names such as
  `in@slot=3` and `out_1@slot=2` while preserving Core runtime port IDs.
- GraphBuilder constructs Core host adapters with the active slot count derived
  from descriptor defaults plus `CorePayload::paramValues`.
- Runtime parameter snapshots include valid sparse keys such as
  `gain@slot=3` and filter malformed or out-of-range slot keys before they can
  enter the realtime parameter hash surface.
- Connection lanes and slot coordinates are orthogonal:
  mono/non-slottable, multichannel/non-slottable, mono/slottable, and
  multichannel/slottable cables are covered explicitly.
- A slotted multichannel cable with two channels and two slots expands to four
  GraphBuilder wires and preserves both axes in wire port names.

Local verification:

```text
cmake --build build/macos-dev --target xyona_lab_tests
./build/macos-dev/tests/xyona_lab_tests --test="Connection System" --xyona-only --summary-only
./build/macos-dev/tests/xyona_lab_tests --test="CoreOperatorHostAdapter" --xyona-only --summary-only
./build/macos-dev/tests/xyona_lab_tests --test="Runtime Slot Snapshot" --xyona-only --summary-only
./build/macos-dev/tests/xyona_lab_tests --test="Multichannel Slot Cable Graph" --xyona-only --summary-only
./build/macos-dev/tests/xyona_lab_tests --test="Param producer single-event contract" --xyona-only --summary-only
./build/macos-dev/tests/xyona_lab_tests --test="Canvas Param Persistence" --xyona-only --summary-only
```

Result:

- `Connection System`: 35 tests, 155 passes, 0 failures.
- `CoreOperatorHostAdapter`: 4 tests, 140 passes, 0 failures.
- `Runtime Slot Snapshot`: 1 test, 10 passes, 0 failures.
- `Multichannel Slot Cable Graph`: 1 test, 9 passes, 0 failures.
- `Param producer single-event contract`: 10 tests, 82 passes, 0 failures.
- `Canvas Param Persistence`: 16 tests, 116 passes, 0 failures.

## Hardening

Status: implemented, tested, committed, and pushed where applicable.

Scope:

- Commit 18: product reference operator.
- Commit 19: end-to-end tests.
- Commit 20: documentation and cleanup.

Commits:

| Roadmap | Repository | Commit | Summary |
|---|---|---|---|
| 18 | `xyona-lab` | `fdeddfc6` | Harden slot gain reference adapter |
| hardening | `xyona-lab` | `cd164bb5` | Keep MainBusOut separate from slot topology |
| CI hardening | `xyona-core` | `7fb5aaf` | Emit UTF-8 byte escapes from core codegen |
| CI hardening | `xyona-lab` | `be316cb8` | Install WebView2 SDK in Lab CI |
| 19 | workspace root `XYONA` | `cc35624` | Add operator slot system check |
| 20 | workspace root/Core/CDP docs | this update | Final documentation cleanup and report |

Implemented facts:

- `slot_gain` remains the product reference operator. Lab now verifies a
  six-slot reference case through one `CoreOperatorHostAdapter`, with global
  gain fallback plus sparse overrides for individual slots.
- `lab.mainbus_out` no longer encodes bus channel layout as `slotCount` or
  `slotGroups`. It remains a normal multi-input sink (`in_0..in_N`) and is
  explicitly tested as non-slottable, so bus layouts cannot trip slot-mapping
  compatibility.
- The workspace has a reproducible E2E script:
  `scripts/check_operator_slot_system.sh`.
- The E2E script configures CDP against the Core build it just verified and
  clean-builds the CDP test tree, avoiding stale local RPATHs to older Core
  build directories.
- Core slot docs now describe canonical `slots.*`, `slotMapping`, and helper
  APIs instead of the old `routingPolicy` helper model.
- Core variable-port docs no longer describe `slot_gain` as publishing
  generated `in_N` / `out_N` descriptor ports.
- CDP port docs explicitly state current non-slottable defaults and future
  slot metadata validation rules.
- Core codegen now emits non-ASCII descriptor strings as explicit UTF-8 byte
  escapes, avoiding MSVC source-codepage drift in generated descriptors.
- Lab Windows CI installs the official `Microsoft.Web.WebView2` NuGet package
  and passes `JUCE_WEBVIEW2_PACKAGE_LOCATION` to CMake. JUCE provides the
  WebView2 integration, but the static WebView2 SDK package is an external
  Windows CI dependency.

Local verification:

```text
./scripts/check_operator_slot_system.sh
```

Result:

- Core CTest passed: 11/11.
- CDP CTest passed: 21/21.
- Lab slot gates passed:
  - `Connection System`: 35 tests, 155 passes, 0 failures.
  - `CoreOperatorHostAdapter`: 5 tests, 210 passes, 0 failures.
  - `Runtime Slot Snapshot`: 1 test, 10 passes, 0 failures.
  - `Multichannel Slot Cable Graph`: 1 test, 9 passes, 0 failures.
  - `Param producer single-event contract`: 10 tests, 82 passes, 0 failures.
  - `Canvas Param Persistence`: 16 tests, 116 passes, 0 failures.
  - `MainBusOutOperator`: 6 tests, 75 passes, 0 failures.
  - `AudioEngineManager`: 46 tests, 2666 passes, 0 failures.
- After the Core UTF-8 codegen hardening, Core was rebuilt locally with
  `cmake --build --preset macos-clang-debug` and retested with
  `ctest --preset macos-clang-debug --output-on-failure`: 11/11 passed.

## Final GitHub Actions Verification

Actions were available and were run after implementation on the shared
`operator-slot-system` branch.

| Repository | Workflow run | Head | Result | Platforms |
|---|---|---|---|---|
| `xyona-core` | `25214627411` | `7fb5aaf` | success | Windows MSVC Debug, macOS Clang Debug |
| `xyona-cdp-pack` | `25214627420` | `31696c2` | success | Windows MSVC Debug, macOS Clang Debug |
| `xyona-lab` | `25214928983` | `be316cb8` | success | Windows MSVC Debug, macOS Clang Debug |

Resolved CI findings:

- Core Windows initially failed `operator_module_runtime_tests` because the
  generated descriptor helper emitted `"\u00d7"` into C++ source and MSVC
  decoded it differently from the YAML expectation. Fixed by byte-stable UTF-8
  C++ string generation.
- Lab Windows initially failed `Configure Lab` because JUCE's WebView2 CMake
  module could not find the external WebView2 SDK package. Fixed by installing
  `Microsoft.Web.WebView2` in the Windows workflow and passing the package root
  to JUCE.

## Current Decision State

The implementation roadmap is complete, committed, pushed, locally verified,
and CI-verified in all affected repositories. No merge was performed.
