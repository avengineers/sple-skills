# Integration Test Build and Execution Scripts

Copy-paste-ready build commands and Python orchestration scripts for building and running integration tests across product variants. Adapt variant names and subsystem targets to your context.

## PowerShell Build Commands

### Basic Integration Test Build

```powershell
# Build integration tests for a specific variant
.\build.ps1 -build -buildKit test -buildType Debug -variants <VariantName>

# Build and run specific integration test
.\build.ps1 -build -buildKit test -variants <VariantName> -target integration_<subsystem>_test

# Build all integration tests
.\build.ps1 -build -buildKit test -buildType Debug -variants all

# Run self-tests (includes integration tests)
.\build.ps1 -selftests
```

### Variant-Specific Commands

```powershell
# Build Disco variant integration tests
.\build.ps1 -build -buildKit test -buildType Debug -variants Disco

# Build Spa variant integration tests  
.\build.ps1 -build -buildKit test -buildType Debug -variants Spa

# Build Base variant integration tests
.\build.ps1 -build -buildKit test -buildType Debug -variants Base

# Run all variant integration tests
foreach ($variant in @("Disco", "Spa", "Base")) {
    Write-Host "Testing variant: $variant"
    .\build.ps1 -build -buildKit test -buildType Debug -variants $variant
}
```

## Python Test Orchestration Scripts

### Basic Integration Test Runner

```python
#!/usr/bin/env python3
"""Integration test orchestration for embedded C components."""

import subprocess
import sys
import os
from pathlib import Path

def run_integration_tests(variant_name, test_filter=None):
    """Run integration tests for specific variant."""
    
    build_cmd = [
        "powershell", "-ExecutionPolicy", "Bypass",
        "./build.ps1", "-build", "-buildKit", "test", 
        "-buildType", "Debug", "-variants", variant_name
    ]
    
    if test_filter:
        build_cmd.extend(["-target", f"integration_{test_filter}_test"])
    
    print(f"Building integration tests for {variant_name}...")
    result = subprocess.run(build_cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Build failed for {variant_name}: {result.stderr}")
        return False
    
    print(f"Integration tests passed for {variant_name}")
    return True

def run_all_variants():
    """Run integration tests across all variants."""
    variants = ["Disco", "Spa", "Base"]
    results = {}
    
    for variant in variants:
        results[variant] = run_integration_tests(variant)
    
    # Report summary
    print("\nIntegration Test Results:")
    for variant, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {variant}: {status}")
    
    return all(results.values())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        variant = sys.argv[1]
        test_filter = sys.argv[2] if len(sys.argv) > 2 else None
        success = run_integration_tests(variant, test_filter)
    else:
        success = run_all_variants()
    
    sys.exit(0 if success else 1)
```

### Variant Configuration Test Script

```python
#!/usr/bin/env python3
"""Test integration tests with different variant configurations."""

import json
import subprocess
from pathlib import Path

class VariantTestRunner:
    def __init__(self, config_file="test_variants.json"):
        self.config_file = Path(config_file)
        self.load_config()
    
    def load_config(self):
        """Load variant test configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "variants": {
                    "Disco": {
                        "components": ["light_controller", "main_control_knob", "power_button"],
                        "features": {"CONFIG_BLINKING": "y", "CONFIG_LIGHT_INTENSITY_LEVELS": "5"},
                        "integration_tests": ["light_subsystem", "power_subsystem"]
                    },
                    "Spa": {
                        "components": ["light_controller", "main_control_knob", "power_button", "auto_off_timer"],
                        "features": {"CONFIG_AUTO_OFF": "y", "CONFIG_TIMER_DURATION": "300"},
                        "integration_tests": ["light_subsystem", "power_subsystem", "timer_subsystem"]
                    },
                    "Base": {
                        "components": ["light_controller", "power_button"],
                        "features": {},
                        "integration_tests": ["light_subsystem"]
                    }
                }
            }
    
    def run_variant_tests(self, variant_name):
        """Run all integration tests for a specific variant."""
        if variant_name not in self.config["variants"]:
            print(f"Unknown variant: {variant_name}")
            return False
        
        variant_config = self.config["variants"][variant_name]
        print(f"Testing variant: {variant_name}")
        print(f"Components: {variant_config['components']}")
        print(f"Features: {variant_config['features']}")
        
        # Run each integration test
        all_passed = True
        for test_name in variant_config["integration_tests"]:
            print(f"  Running {test_name} integration test...")
            
            cmd = [
                "powershell", "-ExecutionPolicy", "Bypass",
                "./build.ps1", "-build", "-buildKit", "test",
                "-buildType", "Debug", "-variants", variant_name,
                "-target", f"integration_{test_name}_test"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"    ✓ {test_name} PASSED")
            else:
                print(f"    ✗ {test_name} FAILED")
                print(f"      Error: {result.stderr}")
                all_passed = False
        
        return all_passed
    
    def run_all_variants(self):
        """Run integration tests for all configured variants."""
        results = {}
        
        for variant_name in self.config["variants"]:
            results[variant_name] = self.run_variant_tests(variant_name)
        
        # Summary
        print("\n" + "="*50)
        print("INTEGRATION TEST SUMMARY")
        print("="*50)
        
        for variant, passed in results.items():
            status = "PASS" if passed else "FAIL"
            print(f"{variant:20} {status}")
        
        total_pass = sum(results.values())
        total_count = len(results)
        print(f"\nTotal: {total_pass}/{total_count} variants passed")
        
        return all(results.values())

if __name__ == "__main__":
    runner = VariantTestRunner()
    
    import sys
    if len(sys.argv) > 1:
        variant = sys.argv[1]
        success = runner.run_variant_tests(variant)
    else:
        success = runner.run_all_variants()
    
    sys.exit(0 if success else 1)
```

## Debug Helper Scripts

### Integration Test Debugger

```bash
#!/bin/bash
# Debug integration test failures

VARIANT=$1
TEST_NAME=$2

if [ -z "$VARIANT" ] || [ -z "$TEST_NAME" ]; then
    echo "Usage: $0 <variant> <test_name>"
    echo "Example: $0 Disco light_subsystem"
    exit 1
fi

echo "Debugging integration test: $TEST_NAME for variant: $VARIANT"

# Build with debug symbols
echo "Building with debug information..."
powershell -ExecutionPolicy Bypass -Command "
    ./build.ps1 -build -buildKit test -buildType Debug -variants $VARIANT -target integration_${TEST_NAME}_test
"

# Run with verbose output
echo "Running test with verbose output..."
./build/test_$VARIANT/integration_${TEST_NAME}_test --gtest_verbose

echo "Debug session complete."
```

### Test Report Generator

```python
#!/usr/bin/env python3
"""Generate integration test reports."""

import xml.etree.ElementTree as ET
from pathlib import Path
import json
from datetime import datetime

def generate_test_report(variant_name, test_results_dir):
    """Generate integration test report for variant."""
    
    results_path = Path(test_results_dir)
    report_data = {
        "variant": variant_name,
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "summary": {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
    }
    
    # Parse GTest XML reports
    for xml_file in results_path.glob("**/*integration*.xml"):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        for testcase in root.findall(".//testcase"):
            test_info = {
                "name": testcase.get("name"),
                "classname": testcase.get("classname"),
                "time": float(testcase.get("time", 0)),
                "status": "passed"
            }
            
            # Check for failures/errors
            if testcase.find("failure") is not None:
                test_info["status"] = "failed"
                test_info["failure"] = testcase.find("failure").text
            elif testcase.find("error") is not None:
                test_info["status"] = "error" 
                test_info["error"] = testcase.find("error").text
            elif testcase.find("skipped") is not None:
                test_info["status"] = "skipped"
            
            report_data["tests"].append(test_info)
            report_data["summary"]["total"] += 1
            
            if test_info["status"] == "passed":
                report_data["summary"]["passed"] += 1
            elif test_info["status"] in ["failed", "error"]:
                report_data["summary"]["failed"] += 1
            else:
                report_data["summary"]["skipped"] += 1
    
    # Write report
    report_file = f"integration_test_report_{variant_name}.json"
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"Generated integration test report: {report_file}")
    return report_data

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python3 generate_report.py <variant> <test_results_dir>")
        sys.exit(1)
    
    variant = sys.argv[1]
    results_dir = sys.argv[2]
    
    report = generate_test_report(variant, results_dir)
    
    # Print summary
    summary = report["summary"]
    print(f"\nIntegration Test Summary for {variant}:")
    print(f"  Total: {summary['total']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Skipped: {summary['skipped']}")
```