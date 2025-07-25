#!/usr/bin/env python3
"""
Generate detailed per-file coverage reports showing covered and uncovered lines.
This script extends the standard coverage report with per-file detailed analysis.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
from datetime import datetime


def print_header(text: str) -> None:
    """Print a header with formatting."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_subheader(text: str) -> None:
    """Print a subheader with formatting."""
    print(f"\n{'-' * 40}")
    print(f"  {text}")
    print(f"{'-' * 40}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"✅ {text}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"❌ {text}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"ℹ️  {text}")


def run_coverage_analysis() -> bool:
    """Run coverage analysis on the project."""
    print_header("Running Coverage Analysis")
    
    # Ensure coverage is installed
    try:
        subprocess.run(["coverage", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Coverage not installed. Install with: pip install coverage")
        return False
    
    # Clean previous coverage data
    print_info("Cleaning previous coverage data...")
    subprocess.run(["coverage", "erase"], check=True)
    
    # Run tests with coverage
    print_info("Running tests with coverage...")
    result = subprocess.run(
        ["coverage", "run", "-m", "pytest", "-v"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print_error("Tests failed. Coverage report may be incomplete.")
        print(result.stderr)
    
    return True


def get_coverage_data() -> Optional[Dict]:
    """Get coverage data in JSON format."""
    print_info("Generating coverage JSON data...")
    
    result = subprocess.run(
        ["coverage", "json", "-o", "-"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print_error("Failed to generate coverage JSON")
        return None
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print_error("Failed to parse coverage JSON")
        return None


def analyze_file_coverage(
    filename: str,
    coverage_info: Dict,
    source_lines: List[str]
) -> Tuple[List[int], List[int], List[int]]:
    """
    Analyze coverage for a single file.
    
    Returns:
        Tuple of (covered_lines, missing_lines, excluded_lines)
    """
    covered_lines = coverage_info.get("executed_lines", [])
    missing_lines = coverage_info.get("missing_lines", [])
    excluded_lines = coverage_info.get("excluded_lines", [])
    
    return covered_lines, missing_lines, excluded_lines


def generate_file_report(
    filename: str,
    source_path: Path,
    coverage_info: Dict,
    output_dir: Path
) -> None:
    """Generate detailed coverage report for a single file."""
    print_info(f"Generating report for: {filename}")
    
    # Read source file
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            source_lines = f.readlines()
    except Exception as e:
        print_error(f"Failed to read {filename}: {e}")
        return
    
    # Analyze coverage
    covered_lines, missing_lines, excluded_lines = analyze_file_coverage(
        filename, coverage_info, source_lines
    )
    
    # Create output filename
    safe_filename = filename.replace('/', '_').replace('\\', '_')
    output_file = output_dir / f"{safe_filename}.coverage.txt"
    
    # Generate report
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"Coverage Report for: {filename}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # Write summary
        total_statements = len(covered_lines) + len(missing_lines)
        if total_statements > 0:
            coverage_percent = (len(covered_lines) / total_statements) * 100
        else:
            coverage_percent = 100.0
        
        f.write("Summary:\n")
        f.write(f"  Total statements: {total_statements}\n")
        f.write(f"  Covered lines: {len(covered_lines)}\n")
        f.write(f"  Missing lines: {len(missing_lines)}\n")
        f.write(f"  Excluded lines: {len(excluded_lines)}\n")
        f.write(f"  Coverage: {coverage_percent:.1f}%\n\n")
        
        # Write line-by-line analysis
        f.write("Line-by-Line Analysis:\n")
        f.write("-" * 80 + "\n")
        f.write("Status | Line # | Code\n")
        f.write("-" * 80 + "\n")
        
        for i, line in enumerate(source_lines, 1):
            if i in covered_lines:
                status = "✓ COV"
            elif i in missing_lines:
                status = "✗ MISS"
            elif i in excluded_lines:
                status = "- EXCL"
            else:
                status = "     "
            
            # Remove trailing newline for display
            code_line = line.rstrip('\n')
            f.write(f"{status:6} | {i:6} | {code_line}\n")
        
        # Write missing lines summary
        if missing_lines:
            f.write("\n" + "=" * 80 + "\n")
            f.write("Missing Lines Summary:\n")
            f.write("-" * 80 + "\n")
            
            # Group consecutive lines
            missing_ranges = []
            start = missing_lines[0]
            end = start
            
            for line in missing_lines[1:]:
                if line == end + 1:
                    end = line
                else:
                    if start == end:
                        missing_ranges.append(str(start))
                    else:
                        missing_ranges.append(f"{start}-{end}")
                    start = end = line
            
            # Add the last range
            if start == end:
                missing_ranges.append(str(start))
            else:
                missing_ranges.append(f"{start}-{end}")
            
            f.write(f"Missing lines: {', '.join(missing_ranges)}\n")
    
    print_success(f"Report generated: {output_file}")


def generate_html_report(output_dir: Path) -> None:
    """Generate an HTML index for all coverage reports."""
    print_info("Generating HTML index...")
    
    index_file = output_dir / "index.html"
    
    # Get all coverage report files
    report_files = sorted(output_dir.glob("*.coverage.txt"))
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Detailed Coverage Reports</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .report-list { margin-top: 20px; }
        .report-item { margin: 10px 0; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>Detailed Coverage Reports</h1>
    <p class="timestamp">Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    <div class="report-list">
        <h2>Per-File Reports:</h2>
        <ul>
""")
        
        for report_file in report_files:
            # Extract original filename from report filename
            original_name = report_file.stem.replace('.coverage', '').replace('_', '/')
            f.write(f'            <li class="report-item"><a href="{report_file.name}">{original_name}</a></li>\n')
        
        f.write("""        </ul>
    </div>
</body>
</html>
""")
    
    print_success(f"HTML index generated: {index_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate detailed per-file coverage reports"
    )
    parser.add_argument(
        "--output-dir",
        default="tests/reports/detailed-coverage",
        help="Output directory for coverage reports"
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run tests with coverage before generating reports"
    )
    parser.add_argument(
        "--source-dir",
        default="c_to_plantuml",
        help="Source directory to analyze"
    )
    
    args = parser.parse_args()
    
    print_header("Detailed Coverage Report Generator")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run coverage analysis if requested
    if args.run_tests:
        if not run_coverage_analysis():
            return 1
    
    # Get coverage data
    coverage_data = get_coverage_data()
    if not coverage_data:
        print_error("No coverage data available. Run with --run-tests flag.")
        return 1
    
    # Process each file
    files_data = coverage_data.get("files", {})
    if not files_data:
        print_error("No files found in coverage data")
        return 1
    
    print_subheader(f"Processing {len(files_data)} files")
    
    for filename, file_coverage in files_data.items():
        # Skip non-source files
        if not filename.startswith(args.source_dir):
            continue
        
        source_path = Path(filename)
        if not source_path.exists():
            print_error(f"Source file not found: {filename}")
            continue
        
        generate_file_report(
            filename,
            source_path,
            file_coverage,
            output_dir
        )
    
    # Generate HTML index
    generate_html_report(output_dir)
    
    # Generate standard coverage reports too
    print_subheader("Generating Standard Coverage Reports")
    
    subprocess.run(["coverage", "report", "-m"], check=False)
    subprocess.run(
        ["coverage", "html", "-d", str(output_dir.parent / "coverage-html")],
        check=False
    )
    
    print_header("Coverage Report Generation Complete!")
    print_info(f"Detailed reports available in: {output_dir}")
    print_info(f"HTML index: {output_dir}/index.html")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())