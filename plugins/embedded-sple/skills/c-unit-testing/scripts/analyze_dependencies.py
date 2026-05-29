#!/usr/bin/env python3
"""
Analyze C source file dependencies for legacy/characterization testing.

This script identifies:
- External function calls (potential mocks needed)
- Global variables accessed
- Hardware register accesses (MMIO patterns)
- Static functions (may need preprocessor seam)
- Include dependencies

Usage:
    python analyze_dependencies.py <c_source_file>

Example:
    python scripts/analyze_dependencies.py components/examples/adc/src/adc.c
"""

import re
import sys
from pathlib import Path
from typing import List, Set, Dict


class DependencyAnalyzer:
    """Analyze C source file for testing dependencies."""

    def __init__(self, source_file: Path):
        self.source_file = source_file
        self.content = source_file.read_text(encoding="utf-8", errors="replace")

        # Results
        self.external_functions: Set[str] = set()
        self.global_variables: Set[str] = set()
        self.static_functions: Set[str] = set()
        self.hardware_accesses: List[Dict[str, str]] = []
        self.includes: Set[str] = set()

    def analyze(self):
        """Run all analysis."""
        self._find_includes()
        self._find_functions()
        self._find_globals()
        self._find_hardware_accesses()

    def _find_includes(self):
        """Find #include statements."""
        pattern = r'#include\s+[<"]([^>"]+)[>"]'
        self.includes = set(re.findall(pattern, self.content))

    def _find_functions(self):
        """Find function declarations and calls."""
        # Find static function definitions
        static_pattern = r"static\s+\w+\s+(\w+)\s*\([^)]*\)"
        self.static_functions = set(re.findall(static_pattern, self.content))

        # Find function calls (simplified heuristic)
        call_pattern = r"\b(\w+)\s*\("
        potential_calls = set(re.findall(call_pattern, self.content))

        # Filter out known keywords and static functions
        keywords = {"if", "while", "for", "switch", "return", "sizeof"}
        self.external_functions = potential_calls - self.static_functions - keywords

    def _find_globals(self):
        """Find global variable declarations (heuristic)."""
        lines = self.content.split("\n")
        for line in lines:
            line = line.strip()
            # Skip preprocessor, comments, function definitions
            if line.startswith("#") or line.startswith("//") or "(" in line:
                continue
            # Look for variable declarations
            if re.match(r"^(extern\s+)?\w+\s+\w+(\s*=.*)?;", line):
                match = re.search(r"\b(\w+)\s*(?:=|;)", line)
                if match:
                    self.global_variables.add(match.group(1))

    def _find_hardware_accesses(self):
        """Find potential hardware register accesses (MMIO)."""
        # Pattern: *(volatile type*)0xADDRESS
        pattern = r"\*\s*\(\s*volatile\s+\w+\s*\*\s*\)\s*(0x[0-9A-Fa-f]+)"
        matches = re.findall(pattern, self.content)
        for addr in matches:
            self.hardware_accesses.append(
                {"address": addr, "context": "Direct MMIO access"}
            )

        # Pattern: #define REGISTER (*(volatile type*)0xADDR)
        define_pattern = r"#define\s+(\w+)\s+.*?(0x[0-9A-Fa-f]+)"
        matches = re.findall(define_pattern, self.content)
        for name, addr in matches:
            if "volatile" in self.content[self.content.find(name) :]:
                self.hardware_accesses.append(
                    {
                        "address": addr,
                        "register_name": name,
                        "context": "Register macro",
                    }
                )

    def print_report(self):
        """Print analysis report."""
        print(f"\n{'='*60}")
        print(f"Dependency Analysis: {self.source_file.name}")
        print(f"{'='*60}\n")

        print("INCLUDES")
        for inc in sorted(self.includes):
            print(f"  - {inc}")
        print()

        print("EXTERNAL FUNCTIONS (potential mocks needed)")
        for func in sorted(self.external_functions):
            print(f"  - {func}()")
        print()

        print("GLOBAL VARIABLES (need reset in tests)")
        for var in sorted(self.global_variables):
            print(f"  - {var}")
        print()

        print("STATIC FUNCTIONS (test through public API preferred)")
        for func in sorted(self.static_functions):
            print(f"  - {func}()")
        print()

        print("HARDWARE ACCESSES (need mock/fake)")
        for hw in self.hardware_accesses:
            name = hw.get("register_name", "Direct access")
            addr = hw["address"]
            print(f"  - {name}: {addr}")
        print()

        self._print_recommendations()

    def _print_recommendations(self):
        """Print testing recommendations."""
        print("TESTING RECOMMENDATIONS\n")

        if self.hardware_accesses:
            print("1. Mock hardware register accesses:")
            print("   - Use SPLE_UNIT_TESTING guard pattern")
            print("   - See hw-register-testing.md reference\n")

        if self.external_functions:
            print("2. Mock external function calls:")
            print("   - Use CREATE_MOCK(mymock) pattern")
            print("   - Add EXPECT_CALL for each dependency\n")

        if self.global_variables:
            print("3. Reset global variables in test fixture:")
            print("   - Implement SetUp() to reset state")
            print("   - Use extern declarations\n")

        if self.static_functions:
            print("4. Test static functions:")
            print("   - Preferred: Test through public API (black-box)")
            print("   - Alternative: Use UNIT_TEST preprocessor seam\n")

        component_name = self.source_file.stem
        print("5. For characterization testing:")
        print("   - See characterization-testing.md reference")
        print(f"   - Create test file: test/test_<Component>_{component_name}.cc\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_dependencies.py <c_source_file>")
        print(
            "\nExample: python analyze_dependencies.py components/examples/adc/src/adc.c"
        )
        sys.exit(1)

    source_file = Path(sys.argv[1])

    if not source_file.exists():
        print(f"Error: File not found: {source_file}")
        sys.exit(1)

    if source_file.suffix not in [".c", ".h"]:
        print(f"Warning: Expected .c or .h file, got {source_file.suffix}")

    analyzer = DependencyAnalyzer(source_file)
    analyzer.analyze()
    analyzer.print_report()


if __name__ == "__main__":
    main()
