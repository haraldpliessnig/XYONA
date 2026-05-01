#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

run_step() {
  local repo="$1"
  shift
  printf '\n==> %s: %s\n' "$repo" "$*"
  (cd "${ROOT_DIR}/${repo}" && "$@")
}

run_step xyona-core cmake --build build --target xyona_core
run_step xyona-core ./build/tests/test_operator_dispatcher
run_step xyona-core ./build/tests/test_operator_packs
run_step xyona-core ctest --test-dir build --output-on-failure

run_step xyona-cdp-pack cmake -S . -B build/macos-clang-debug \
  -DXYONA_CORE_ROOT="${ROOT_DIR}/xyona-core" \
  "-Dxyona-core_DIR:PATH=${ROOT_DIR}/xyona-core/build/xyona-core-build"
run_step xyona-cdp-pack ../xyona-core/venv/bin/python scripts/generate_operator_metadata.py --root . --check
run_step xyona-cdp-pack cmake --build build/macos-clang-debug --clean-first
run_step xyona-cdp-pack ctest --test-dir build/macos-clang-debug --output-on-failure

run_step xyona-lab cmake --build build/macos-dev --target xyona_lab_tests
run_step xyona-lab ./build/macos-dev/tests/xyona_lab_tests --test="Connection System" --xyona-only --summary-only
run_step xyona-lab ./build/macos-dev/tests/xyona_lab_tests --test="CoreOperatorHostAdapter" --xyona-only --summary-only
run_step xyona-lab ./build/macos-dev/tests/xyona_lab_tests --test="Runtime Slot Snapshot" --xyona-only --summary-only
run_step xyona-lab ./build/macos-dev/tests/xyona_lab_tests --test="Multichannel Slot Cable Graph" --xyona-only --summary-only
run_step xyona-lab ./build/macos-dev/tests/xyona_lab_tests --test="Param producer single-event contract" --xyona-only --summary-only
run_step xyona-lab ./build/macos-dev/tests/xyona_lab_tests --test="Canvas Param Persistence" --xyona-only --summary-only
run_step xyona-lab ./build/macos-dev/tests/xyona_lab_tests --test="MainBusOutOperator" --xyona-only --summary-only
run_step xyona-lab env XYONA_OPERATOR_PACK_PATH="${ROOT_DIR}/xyona-cdp-pack/build/macos-clang-debug" ./build/macos-dev/tests/xyona_lab_tests --test="AudioEngineManager" --xyona-only --summary-only

printf '\nOperator slot system checks passed.\n'
