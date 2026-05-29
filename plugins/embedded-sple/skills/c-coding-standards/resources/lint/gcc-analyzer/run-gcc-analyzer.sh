#!/usr/bin/env bash
set -euo pipefail

# Managed by c-coding-standards skill (resources/lint/gcc-analyzer/run-gcc-analyzer.sh)
#
# Runs GCC's integrated static analyzer using -fanalyzer.
# Reference: Download your organization's coding standard (e.g., Barr-C 2018) from a shared location.
#
# Usage:
#   ./run-gcc-analyzer.sh [src_root] [--roots "src drivers"] [--out-dir build/gcc-analyzer]
#
# Notes:
# - This compiles each .c file with analyzer flags (analysis happens during compilation).
# - You may need to add include paths (-I...) and defines (-D...) for your project.

SRC_ROOT="${1:-.}"
OUT_DIR="build/gcc-analyzer"
ROOTS_STR="src drivers"

shift $(( $# > 0 ? 1 : 0 )) || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --roots)
      ROOTS_STR="${2:-$ROOTS_STR}"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="${2:-$OUT_DIR}"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" 1>&2
      exit 2
      ;;
  esac
done

FLAGS_FILE="tools/gcc-analyzer.flags"
if [[ ! -f "${FLAGS_FILE}" ]]; then
  echo "ERROR: ${FLAGS_FILE} not found (expected to be installed into project tools/)." 1>&2
  exit 2
fi

mkdir -p "${OUT_DIR}"

mapfile -t FLAGS < "${FLAGS_FILE}"

IFS=' ' read -r -a ROOTS <<< "${ROOTS_STR}"

FILES=()
for r in "${ROOTS[@]}"; do
  if [[ -d "${SRC_ROOT}/${r}" ]]; then
    while IFS= read -r -d '' f; do
      FILES+=("$f")
    done < <(find "${SRC_ROOT}/${r}" -type f -name "*.c" -print0)
  fi
done

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No .c files found under: ${ROOTS[*]} (within ${SRC_ROOT})"
  exit 0
fi

echo "Running gcc -fanalyzer..."
echo "  Roots:   ${ROOTS[*]}"
echo "  OutDir:  ${OUT_DIR}"

for f in "${FILES[@]}"; do
  obj="${OUT_DIR}/$(basename "$f").o"
  echo "[gcc -fanalyzer] $f"
  gcc "${FLAGS[@]}" -c "$f" -o "$obj"
done

echo "gcc -fanalyzer OK"
