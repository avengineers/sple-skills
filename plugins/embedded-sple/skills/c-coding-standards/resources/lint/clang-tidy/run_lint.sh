#!/usr/bin/env bash
set -euo pipefail

# Managed by c-coding-standards skill (resources/lint/clang-tidy/run_lint.sh)
#
# Runs clang-tidy using a compilation database directory (-p <build-dir>),
# which should contain compile_commands.json. [5](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)[4](https://developers.redhat.com/blog/2020/03/26/static-analysis-in-gcc-10)
#
# Usage:
#   ./run-lint.sh [build_dir] [--fixes fixes.yaml] [--roots "src include drivers"]
#
# Examples:
#   ./run-lint.sh build
#   ./run-lint.sh build --fixes clang-tidy-fixes.yaml
#   ./run-lint.sh build --roots "src include"

BUILD_DIR="${1:-build}"
FIXES_FILE=""
ROOTS_STR="src include drivers"

shift $(( $# > 0 ? 1 : 0 )) || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fixes)
      FIXES_FILE="${2:-clang-tidy-fixes.yaml}"
      shift 2
      ;;
    --roots)
      ROOTS_STR="${2:-$ROOTS_STR}"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" 1>&2
      exit 2
      ;;
  esac
done

if [[ ! -f "${BUILD_DIR}/compile_commands.json" ]]; then
  echo "ERROR: ${BUILD_DIR}/compile_commands.json not found." 1>&2
  echo "Hint: generate it (e.g. CMake CMAKE_EXPORT_COMPILE_COMMANDS=ON) and point to the build dir." 1>&2
  exit 2
fi

IFS=' ' read -r -a ROOTS <<< "${ROOTS_STR}"

FILES=()
for r in "${ROOTS[@]}"; do
  if [[ -d "$r" ]]; then
    while IFS= read -r -d '' f; do
      FILES+=("$f")
    done < <(find "$r" -type f \( -name "*.c" -o -name "*.h" \) -print0)
  fi
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No .c/.h files found under roots: ${ROOTS[*]}"
  exit 0
fi

TIDY_ARGS=(-p "${BUILD_DIR}")

# clang-tidy will auto-discover .clang-tidy by searching parent directories when not specified. [3](https://lindevs.com/generate-json-compilation-database-using-cmake)
# If you want to force a config file explicitly, uncomment:
# TIDY_ARGS+=(--config-file "$(pwd)/.clang-tidy")  # [3](https://lindevs.com/generate-json-compilation-database-using-cmake)

if [[ -n "${FIXES_FILE}" ]]; then
  TIDY_ARGS+=(--export-fixes "${FIXES_FILE}")  # clang-tidy supports exporting fixes. [3](https://lindevs.com/generate-json-compilation-database-using-cmake)
fi

echo "Running clang-tidy..."
echo "  Build DB: ${BUILD_DIR}/compile_commands.json"
echo "  Roots:    ${ROOTS[*]}"
if [[ -n "${FIXES_FILE}" ]]; then
  echo "  Fixes:    ${FIXES_FILE}"
fi

clang-tidy "${TIDY_ARGS[@]}" "${FILES[@]}"

echo "clang-tidy OK"
