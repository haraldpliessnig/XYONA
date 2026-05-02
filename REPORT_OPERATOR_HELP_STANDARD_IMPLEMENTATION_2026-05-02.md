# Report: Operator Help Standard Implementation

**Date:** 2026-05-02
**Branch:** `codex/operator-help-standard`
**Scope:** Workspace standard, Core metadata transport, CDP pack metadata,
workspace linting, and Lab help indexing

## Feasibility Review

`ROADMAP_OPERATOR_HELP_STANDARD.md` is technically implementable and aligned
with the existing operator-module contract. The current codebase already has
the required foundations: module-local `docs/<locale>.md` files in Core and
CDP, descriptor-owned IDs and port types, Core frontmatter parsing, CDP
generated metadata, and Lab filesystem help indexing.

The high-quality path still needs staged commits, but there is no compatibility
requirement for legacy help structure. Existing Core/CDP articles are
legacy-shaped, CDP has operators without localized help files, and Lab
host-operator specs currently do not carry the full parameter descriptor
surface required for richly authored Tier 2 prose. The implementation therefore
replaces the current operator-help shape with descriptor-grounded
`operator_help_v1` files and makes the linter strict by default.

## Technical Decisions

- `OPERATOR_HELP_STANDARD.md` is the normative v1 help standard.
- `ROADMAP_OPERATOR_HELP_STANDARD.md` remains the active rollout tracker.
- All public operator help files must declare `standard: operator_help_v1`.
- `Tech Sheet` may be authored and validated in Markdown or generated into
  companion metadata from descriptor facts; no prose belongs in the block.
- The workspace help linter is strict by default; no legacy operator-help
  compatibility mode is part of the implementation.

## Commit Log

This table is updated as implementation commits are produced and pushed.

| Repo | Commit | Subject | Local validation | Push |
|---|---|---|---|---|
| XYONA | `cb4754c` | `docs: define operator help standard` | `git diff --check` | pushed to `origin/codex/operator-help-standard` |
| XYONA | `da3a026` | `docs: require operator help v1` | `git diff --check` | pushed to `origin/codex/operator-help-standard` |
| xyona-core | `d0d23f9` | `help: enforce operator help v1 in core` | `validate_operator_modules.py`; `codegen_params.py`; `git diff --check`; `cmake --build build/macos-clang-debug --target xyona_core test_operator_module_runtime --parallel 8`; `ctest -R "operator_module_runtime_tests\|operator_module_metadata_tests\|operator_module_validator_guardrail_tests\|operator_packs_tests"` | pushed to `origin/codex/operator-help-standard` |
| xyona-cdp-pack | `b13f225` | `help: enforce operator help v1 in cdp pack` | `validate_operator_modules.py`; `generate_operator_metadata.py --check`; `git diff --check`; `cmake --build build/macos-clang-debug --target xyona_pack_cdp_ops test_cdp_descriptor_metadata test_cdp_spectral_contract test_cdp_pack test_cdp_pack_env_discovery --parallel 8`; `ctest -R "cdp_generated_operator_metadata_tests\|cdp_operator_module_metadata_tests\|cdp_descriptor_metadata_tests\|cdp_spectral_contract_tests\|cdp_pack_loader_tests\|cdp_pack_env_discovery_tests"` | pushed to `origin/codex/operator-help-standard` |
| xyona-lab | `0b0e975c` | `help: index operator help by provider` | `validate_operator_modules.py`; manual docs sync/index smoke test; `git diff --check`; `./build-dev.sh`; `ctest -R "lab_operator_module_metadata_tests"`; `ctest -R "xyona_lab_tests"` | pushed to `origin/codex/operator-help-standard` |
| XYONA | `40afa9c` | `help: add strict operator help lint` | `tools/help_lint/operator_help_lint.py --workspace .`; `git diff --check` | pushed to `origin/codex/operator-help-standard` |
| XYONA | `3e9d1d8` | `docs: record operator help implementation` | `git diff --check` | pushed to `origin/codex/operator-help-standard` |
| xyona-core | `b4e2e4f` | `help: use application summaries in core help` | `codegen_params.py`; `validate_operator_modules.py`; `git diff --check`; `cmake --build build/macos-clang-debug --target xyona_core test_operator_module_runtime --parallel 8`; `ctest -R "operator_module_runtime_tests\|operator_module_metadata_tests\|operator_module_validator_guardrail_tests\|operator_packs_tests"` | pushed to `origin/codex/operator-help-standard` |
| xyona-cdp-pack | `cea001f` | `help: refine cdp application summaries` | `generate_operator_metadata.py`; `generate_operator_metadata.py --check`; `validate_operator_modules.py`; `git diff --check`; `cmake --build build/macos-clang-debug --target xyona_pack_cdp_ops test_cdp_descriptor_metadata test_cdp_spectral_contract test_cdp_pack test_cdp_pack_env_discovery --parallel 8`; `ctest -R "cdp_generated_operator_metadata_tests\|cdp_operator_module_metadata_tests\|cdp_descriptor_metadata_tests\|cdp_spectral_contract_tests\|cdp_pack_loader_tests\|cdp_pack_env_discovery_tests"` | pushed to `origin/codex/operator-help-standard` |
| xyona-lab | `dffab88a` | `help: expose operator summary metadata` | `validate_operator_modules.py`; `git diff --check`; `./build-dev.sh`; `cmake --build build/macos-dev --target xyona_lab_tests --parallel 8`; `ctest -R "lab_operator_module_metadata_tests\|xyona_lab_tests"` | pushed to `origin/codex/operator-help-standard` |
| XYONA | `e7c5b62` | `docs: clarify operator summary tooltips` | `tools/help_lint/operator_help_lint.py --workspace .`; `git diff --check` | pushed to `origin/codex/operator-help-standard` |
| XYONA | `352131e` | `docs: record operator summary refinement` | `git diff --check` | pushed to `origin/codex/operator-help-standard` |
| xyona-lab | `1ddee90d` | `help: surface operator summaries in sidebars` | `git diff --check`; `git diff --cached --check`; `cmake --build build/macos-dev --target xyona_lab_tests --parallel 8`; `./build-dev.sh`; `ctest -R "lab_operator_module_metadata_tests\|xyona_lab_tests"` | pushed to `origin/codex/operator-help-standard` |

## Current Result

- Public operator help now uses strict `operator_help_v1`; no legacy-help
  compatibility path is required or implemented.
- Core transports structured help metadata in generated descriptors.
- CDP generated metadata now requires localized help frontmatter and embeds the
  help payload.
- Lab syncs Core and CDP module-local help by provider, indexes YAML
  frontmatter, and includes Lab-owned operator help.
- The workspace linter validates all current public Core, CDP, and Lab
  operators across `en` and `de`.
- Tier 1 `short` text is now defined as an application-focused operator
  browser/sidebar summary. Provider (`core`, `cdp`, `lab`), processing domain,
  and capability are rendered as a separate compact technical line from
  metadata, not embedded in `short`.
- Lab now uses that metadata in the operator sidebar row hover tooltip.
- Lab now renders the focused operator `short` directly below the Parameter
  sidebar title.

Final GitHub Actions verification is intentionally run only after all
implementation and report commits are pushed.
