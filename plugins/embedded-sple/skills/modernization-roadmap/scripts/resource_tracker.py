#!/usr/bin/env python3
"""
RAM/ROM Usage Tracker for Modernization Steps.

Compares resource usage before and after changes to ensure
the 10% limit per step is respected.

Usage:
    python resource_tracker.py baseline <map_file> <output_json>
    python resource_tracker.py compare <baseline_json> <map_file>
    python resource_tracker.py report <baseline_json> <current_json>
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ResourceMetrics:
    """Resource usage metrics."""
    ram_bytes: int
    rom_bytes: int
    source_file: str
    timestamp: str


def parse_map_file(map_file: Path) -> Optional[ResourceMetrics]:
    """
    Parse a linker map file to extract RAM and ROM usage.
    
    Supports ARM GCC map files (.bss/.text sections) and ARM/Keil summary
    format (Total RO/RW Size lines). If both formats are present, the
    summary format takes precedence.
    Returns None if the file does not exist.
    """
    if not map_file.exists():
        print(f"Error: Map file not found: {map_file}", file=sys.stderr)
        return None
    
    content = map_file.read_text(encoding='utf-8', errors='ignore')
    
    ram_bytes = 0
    rom_bytes = 0
    
    # Pattern for ARM GCC map files (Memory Configuration section)
    # Look for .data, .bss sections (RAM) and .text, .rodata sections (ROM)
    
    # Try ARM GCC format first
    ram_pattern = r'\.bss\s+\w+\s+(\w+)'
    rom_pattern = r'\.text\s+\w+\s+(\w+)'
    
    bss_match = re.search(ram_pattern, content)
    text_match = re.search(rom_pattern, content)
    
    if bss_match and text_match:
        try:
            ram_bytes = int(bss_match.group(1), 16)
            rom_bytes = int(text_match.group(1), 16)
        except ValueError:
            pass
    
    # Try summary section format
    # "Total RO  Size (Code + RO Data)    12345 bytes"
    # "Total RW  Size (RW Data + ZI Data) 12345 bytes"
    ro_match = re.search(r'Total RO\s+Size.*?(\d+)\s*(?:\(|bytes)', content)
    rw_match = re.search(r'Total RW\s+Size.*?(\d+)\s*(?:\(|bytes)', content)
    
    if ro_match:
        if rom_bytes > 0:
            print(f"Note: Summary format overrides ARM GCC .text value ({rom_bytes} -> {int(ro_match.group(1))})", file=sys.stderr)
        rom_bytes = int(ro_match.group(1))
    if rw_match:
        if ram_bytes > 0:
            print(f"Note: Summary format overrides ARM GCC .bss value ({ram_bytes} -> {int(rw_match.group(1))})", file=sys.stderr)
        ram_bytes = int(rw_match.group(1))
    
    if ram_bytes == 0 and rom_bytes == 0:
        print(f"Warning: No RAM/ROM data extracted from {map_file} — "
              "neither ARM GCC (.bss/.text) nor summary (Total RO/RW Size) "
              "format matched. Verify the map file format.", file=sys.stderr)

    return ResourceMetrics(
        ram_bytes=ram_bytes,
        rom_bytes=rom_bytes,
        source_file=str(map_file),
        timestamp=datetime.now().isoformat()
    )


def save_baseline(metrics: ResourceMetrics, output_file: Path) -> None:
    """Save metrics to JSON file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(asdict(metrics), f, indent=2)
    print(f"Baseline saved to: {output_file}")


def load_metrics(json_file: Path) -> Optional[ResourceMetrics]:
    """Load metrics from JSON file."""
    if not json_file.exists():
        print(f"Error: Metrics file not found: {json_file}", file=sys.stderr)
        return None
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return ResourceMetrics(**data)


def compare_metrics(baseline: ResourceMetrics, current: ResourceMetrics, limit_percent: float = 10.0) -> dict:
    """
    Compare current metrics against baseline.
    
    Returns dict with comparison results and pass/fail status.
    When baseline is zero and current is non-zero, the comparison
    fails because a percentage delta cannot be computed meaningfully.
    """
    ram_delta = current.ram_bytes - baseline.ram_bytes
    rom_delta = current.rom_bytes - baseline.rom_bytes
    
    # Zero baseline with non-zero current: percentage is meaningless,
    # flag as not within limit so the human reviewer gets to decide.
    ram_zero_baseline = baseline.ram_bytes == 0 and current.ram_bytes > 0
    rom_zero_baseline = baseline.rom_bytes == 0 and current.rom_bytes > 0

    ram_percent = (ram_delta / baseline.ram_bytes * 100) if baseline.ram_bytes > 0 else 0
    rom_percent = (rom_delta / baseline.rom_bytes * 100) if baseline.rom_bytes > 0 else 0
    
    ram_ok = abs(ram_percent) <= limit_percent and not ram_zero_baseline
    rom_ok = abs(rom_percent) <= limit_percent and not rom_zero_baseline
    
    warnings = []
    if ram_zero_baseline:
        warnings.append(f"RAM baseline is 0 but current is {current.ram_bytes} bytes — cannot compute percentage delta")
    if rom_zero_baseline:
        warnings.append(f"ROM baseline is 0 but current is {current.rom_bytes} bytes — cannot compute percentage delta")

    result = {
        'baseline': asdict(baseline),
        'current': asdict(current),
        'delta': {
            'ram_bytes': ram_delta,
            'rom_bytes': rom_delta,
            'ram_percent': round(ram_percent, 2),
            'rom_percent': round(rom_percent, 2),
        },
        'limits': {
            'max_percent': limit_percent,
            'ram_within_limit': ram_ok,
            'rom_within_limit': rom_ok,
        },
        'overall_pass': ram_ok and rom_ok,
    }
    if warnings:
        result['warnings'] = warnings
    return result


def print_comparison_report(result: dict) -> None:
    """Print a human-readable comparison report."""
    print("\n" + "=" * 60)
    print("RESOURCE USAGE COMPARISON REPORT")
    print("=" * 60)
    
    print(f"\n{'Metric':<20} {'Baseline':>12} {'Current':>12} {'Delta':>12} {'%':>8}")
    print("-" * 60)
    
    baseline = result['baseline']
    current = result['current']
    delta = result['delta']
    limits = result['limits']
    
    ram_status = "✅" if limits['ram_within_limit'] else "❌"
    rom_status = "✅" if limits['rom_within_limit'] else "❌"
    
    print(f"{'RAM (bytes)':<20} {baseline['ram_bytes']:>12} {current['ram_bytes']:>12} "
          f"{delta['ram_bytes']:>+12} {delta['ram_percent']:>+7.1f}% {ram_status}")
    print(f"{'ROM (bytes)':<20} {baseline['rom_bytes']:>12} {current['rom_bytes']:>12} "
          f"{delta['rom_bytes']:>+12} {delta['rom_percent']:>+7.1f}% {rom_status}")
    
    print("-" * 60)
    print(f"Limit: ±{limits['max_percent']}% per step")
    
    if result['overall_pass']:
        print("\n✅ PASS: Resource usage within limits")
    else:
        print("\n❌ FAIL: Resource usage exceeds limits!")
        print("   Consider splitting this step into smaller changes.")
    
    if result.get('warnings'):
        print("\n⚠️  WARNINGS:")
        for warning in result['warnings']:
            print(f"   {warning}")
    
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Track RAM/ROM usage for modernization steps')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # baseline command
    baseline_parser = subparsers.add_parser('baseline', help='Create baseline from map file')
    baseline_parser.add_argument('map_file', type=Path, help='Linker map file')
    baseline_parser.add_argument('output', type=Path, help='Output JSON file')
    
    # compare command
    compare_parser = subparsers.add_parser('compare', help='Compare current map file against baseline')
    compare_parser.add_argument('baseline', type=Path, help='Baseline JSON file')
    compare_parser.add_argument('map_file', type=Path, help='Current linker map file')
    compare_parser.add_argument('--limit', type=float, default=10.0, help='Max percent change (default: 10)')
    compare_parser.add_argument('--output', type=Path, help='Save comparison result to JSON')
    
    # report command
    report_parser = subparsers.add_parser('report', help='Generate report from two JSON files')
    report_parser.add_argument('baseline', type=Path, help='Baseline JSON file')
    report_parser.add_argument('current', type=Path, help='Current JSON file')
    report_parser.add_argument('--limit', type=float, default=10.0, help='Max percent change (default: 10)')
    
    args = parser.parse_args()
    
    if args.command == 'baseline':
        metrics = parse_map_file(args.map_file)
        if metrics:
            save_baseline(metrics, args.output)
            print(f"RAM: {metrics.ram_bytes} bytes")
            print(f"ROM: {metrics.rom_bytes} bytes")
        else:
            sys.exit(1)
    
    elif args.command == 'compare':
        baseline = load_metrics(args.baseline)
        current = parse_map_file(args.map_file)
        
        if baseline and current:
            result = compare_metrics(baseline, current, args.limit)
            print_comparison_report(result)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                print(f"Comparison saved to: {args.output}")
            
            sys.exit(0 if result['overall_pass'] else 1)
        else:
            sys.exit(1)
    
    elif args.command == 'report':
        baseline = load_metrics(args.baseline)
        current = load_metrics(args.current)
        
        if baseline and current:
            result = compare_metrics(baseline, current, args.limit)
            print_comparison_report(result)
            sys.exit(0 if result['overall_pass'] else 1)
        else:
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
