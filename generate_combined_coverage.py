#!/usr/bin/env python3
"""
Generate combined coverage reports: summary and detailed per-file analysis.
This script creates comprehensive coverage reports including both overview and line-by-line details.
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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


def run_coverage_analysis() -> Tuple[bool, Dict]:
    """Run coverage analysis on the project and capture test results."""
    print_header("Running Coverage Analysis")

    # Ensure coverage is installed
    try:
        subprocess.run(["python3", "-m", "coverage", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Coverage not installed. Install with: pip install coverage")
        return False, {}

    # Clean previous coverage data
    print_info("Cleaning previous coverage data...")
    subprocess.run(["python3", "-m", "coverage", "erase"], check=True)

    # Run tests with coverage and capture output
    print_info("Running tests with coverage...")
    result = subprocess.run(
        ["python3", "-m", "coverage", "run", "-m", "pytest", "-v"], capture_output=True, text=True
    )

    # Parse test results from output
    test_results = parse_test_results(result.stdout, result.stderr, result.returncode)

    if result.returncode != 0:
        print_error("Tests failed. Coverage report may be incomplete.")
        print(result.stderr)

    return True, test_results


def parse_test_results(stdout: str, stderr: str, returncode: int) -> Dict:
    """Parse test results from pytest output."""
    test_results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "duration": 0.0,
        "status": "PASSED" if returncode == 0 else "FAILED",
        "test_files": [],
        "failed_tests": [],
    }

    try:
        # Parse the test summary from stdout
        lines = stdout.split("\n")
        for line in lines:
            # Look for the pytest summary line: "======================== 329 passed, 1 warning in 1.28s ========================"
            if line.startswith("========================") and "passed" in line and "in" in line:
                import re

                # Extract passed count
                passed_match = re.search(r"(\d+) passed", line)
                if passed_match:
                    test_results["passed"] = int(passed_match.group(1))
                    test_results["total_tests"] = test_results[
                        "passed"
                    ]  # Assume all tests passed if no failures

                # Extract failed count
                failed_match = re.search(r"(\d+) failed", line)
                if failed_match:
                    test_results["failed"] = int(failed_match.group(1))
                    test_results["total_tests"] += test_results["failed"]

                # Extract skipped count
                skipped_match = re.search(r"(\d+) skipped", line)
                if skipped_match:
                    test_results["skipped"] = int(skipped_match.group(1))
                    test_results["total_tests"] += test_results["skipped"]

                # Extract error count
                error_match = re.search(r"(\d+) error", line)
                if error_match:
                    test_results["errors"] = int(error_match.group(1))
                    test_results["total_tests"] += test_results["errors"]

                # Extract duration
                duration_match = re.search(r"in ([\d.]+)s", line)
                if duration_match:
                    test_results["duration"] = float(duration_match.group(1))

                break  # Found the summary line, no need to continue

            # Also look for the "collected X items" line as backup
            elif "collected" in line and "items" in line:
                import re

                match = re.search(r"collected (\d+) items?", line)
                if match:
                    test_results["total_tests"] = int(match.group(1))

            # Capture failed test details
            elif line.startswith("FAILED") or line.startswith("ERROR"):
                test_results["failed_tests"].append(line.strip())

        # If we still don't have test counts, try to count from individual test results
        if test_results["total_tests"] == 0:
            test_lines = [
                line for line in lines if "PASSED" in line or "FAILED" in line or "SKIPPED" in line
            ]
            test_results["total_tests"] = len(test_lines)
            test_results["passed"] = len([line for line in lines if "PASSED" in line])
            test_results["failed"] = len([line for line in lines if "FAILED" in line])
            test_results["skipped"] = len([line for line in lines if "SKIPPED" in line])

    except Exception as e:
        print_error(f"Error parsing test results: {e}")

    return test_results


def get_coverage_data() -> Optional[Dict]:
    """Get coverage data in JSON format."""
    print_info("Generating coverage JSON data...")

    result = subprocess.run(
        ["python3", "-m", "coverage", "json", "-o", "-"], capture_output=True, text=True
    )

    if result.returncode != 0:
        print_error("Failed to generate coverage JSON")
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print_error("Failed to parse coverage JSON")
        return None


def generate_coverage_summary(coverage_data: Dict, output_dir: Path) -> None:
    """Generate coverage summary report."""
    print_info("Generating coverage summary...")

    summary_file = output_dir / "coverage_summary.txt"

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("Coverage Summary Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        # Overall statistics
        summary = coverage_data.get("totals", {})
        total_lines = summary.get("num_statements", 0)
        covered_lines = summary.get("covered_lines", 0)
        missing_lines = summary.get("missing_lines", 0)
        coverage_percent = summary.get("percent_covered", 0)

        f.write("Overall Statistics:\n")
        f.write(f"  Total statements: {total_lines:,}\n")
        f.write(f"  Covered lines: {covered_lines:,}\n")
        f.write(f"  Missing lines: {missing_lines:,}\n")
        f.write(f"  Coverage: {coverage_percent:.1f}%\n\n")

        # Per-file summary
        f.write("Per-File Summary:\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'File':<50} {'Stmts':>8} {'Miss':>8} {'Cover':>8}\n")
        f.write("-" * 80 + "\n")

        files_data = coverage_data.get("files", {})
        for filename, file_data in sorted(files_data.items()):
            summary = file_data.get("summary", {})
            stmts = summary.get("num_statements", 0)
            miss = summary.get("missing_lines", 0)
            cover = summary.get("percent_covered", 0)

            # Truncate filename if too long
            display_name = filename if len(filename) <= 50 else "..." + filename[-47:]
            f.write(f"{display_name:<50} {stmts:>8} {miss:>8} {cover:>7.1f}%\n")

        f.write("-" * 80 + "\n")

    print_success(f"Summary report generated: {summary_file}")


def generate_test_summary_html(test_results: Dict, output_dir: Path) -> None:
    """Generate HTML test summary report showing actual test results."""
    print_info("Generating HTML test summary...")

    summary_file = output_dir.parent / "test_summary.html"

    # Get test statistics
    total_tests = test_results.get("total_tests", 0)
    passed = test_results.get("passed", 0)
    failed = test_results.get("failed", 0)
    skipped = test_results.get("skipped", 0)
    errors = test_results.get("errors", 0)
    duration = test_results.get("duration", 0.0)
    status = test_results.get("status", "UNKNOWN")
    failed_tests = test_results.get("failed_tests", [])

    # Calculate success rate
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(
            f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Results Summary</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-card {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        .success-rate {{
            font-size: 48px;
            color: {'#4caf50' if success_rate >= 90 else '#ff9800' if success_rate >= 70 else '#f44336'};
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            text-transform: uppercase;
            color: white;
            background: {'#4caf50' if status == 'PASSED' else '#f44336'};
        }}
        .failed-tests {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
            margin-top: 20px;
        }}
        .failed-header {{
            background: #f44336;
            color: white;
            padding: 15px 20px;
            font-weight: bold;
        }}
        .failed-item {{
            padding: 15px 20px;
            border-bottom: 1px solid #e0e0e0;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
        }}
        .failed-item:last-child {{
            border-bottom: none;
        }}
        .download-links {{
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .download-links a {{
            color: #0066cc;
            text-decoration: none;
            margin-right: 20px;
        }}
        .download-links a:hover {{
            text-decoration: underline;
        }}
        .back-link {{
            margin-bottom: 20px;
        }}
        .back-link a {{
            color: #0066cc;
            text-decoration: none;
        }}
        .back-link a:hover {{
            text-decoration: underline;
        }}
        .test-details {{
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .test-details h3 {{
            margin-top: 0;
            color: #333;
        }}
        .test-details p {{
            margin: 5px 0;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="back-link">
            <a href="index.html">← Back to Coverage Index</a>
        </div>

        <h1>Test Results Summary</h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>

        <div class="summary-card">
            <h2 style="margin-top: 0;">Test Execution Results</h2>
            <div style="margin-bottom: 20px;">
                <span class="status-badge">{status}</span>
                <span style="margin-left: 10px; color: #666;">Execution completed in {duration:.2f} seconds</span>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value success-rate">{success_rate:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_tests}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #4caf50">{passed}</div>
                    <div class="stat-label">Passed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #f44336">{failed}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #ff9800">{skipped}</div>
                    <div class="stat-label">Skipped</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #9c27b0">{errors}</div>
                    <div class="stat-label">Errors</div>
                </div>
            </div>

            <div class="test-details">
                <h3>Test Execution Details</h3>
                <p><strong>Total Tests:</strong> {total_tests:,}</p>
                <p><strong>Passed:</strong> {passed:,} ({(passed/total_tests*100) if total_tests > 0 else 0.0:.1f}%)</p>
                <p><strong>Failed:</strong> {failed:,} ({(failed/total_tests*100) if total_tests > 0 else 0.0:.1f}%)</p>
                <p><strong>Skipped:</strong> {skipped:,} ({(skipped/total_tests*100) if total_tests > 0 else 0.0:.1f}%)</p>
                <p><strong>Errors:</strong> {errors:,} ({(errors/total_tests*100) if total_tests > 0 else 0.0:.1f}%)</p>
                <p><strong>Execution Time:</strong> {duration:.2f} seconds</p>
                <p><strong>Overall Status:</strong> {status}</p>
            </div>


        </div>
"""
        )

        # Show failed tests if any
        if failed_tests:
            f.write(
                f"""        <div class="failed-tests">
            <div class="failed-header">Failed Tests ({len(failed_tests)})</div>
"""
            )

            for failed_test in failed_tests:
                f.write(
                    f"""            <div class="failed-item">{html.escape(failed_test)}</div>
"""
                )

            f.write(
                """        </div>
"""
            )

        f.write(
            """    </div>
</body>
</html>
"""
        )

    print_success(f"HTML test summary generated: {summary_file}")


def generate_html_file_report(
    filename: str, source_path: Path, coverage_info: Dict, output_dir: Path
) -> Tuple[str, float, Dict]:
    """Generate detailed HTML coverage report for a single file."""
    print_info(f"Generating HTML report for: {filename}")

    # Read source file
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            source_lines = f.readlines()
    except Exception as e:
        print_error(f"Failed to read {filename}: {e}")
        return None, 0, {}

    # Get coverage data
    covered_lines = coverage_info.get("executed_lines", [])
    missing_lines = coverage_info.get("missing_lines", [])
    excluded_lines = coverage_info.get("excluded_lines", [])

    # Calculate statistics
    total_statements = len(covered_lines) + len(missing_lines)
    coverage_percent = (
        (len(covered_lines) / total_statements * 100) if total_statements > 0 else 100.0
    )

    # Create output filename
    safe_filename = filename.replace("/", "_").replace("\\", "_")
    output_file = output_dir / f"{safe_filename}.html"

    # Generate HTML
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(
            f"""<!DOCTYPE html>
<html>
<head>
    <title>Coverage Report: {html.escape(filename)}</title>
    <style>
        body {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        h1 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 24px;
        }}
        .stats {{
            display: flex;
            gap: 30px;
            margin-top: 20px;
        }}
        .stat {{
            display: flex;
            flex-direction: column;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .coverage-bar {{
            width: 200px;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 5px;
        }}
        .coverage-fill {{
            height: 100%;
            background: {'#4caf50' if coverage_percent >= 80 else '#ff9800' if coverage_percent >= 60 else '#f44336'};
            transition: width 0.3s ease;
        }}
        .code-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .code-header {{
            background: #333;
            color: white;
            padding: 10px 20px;
            font-size: 14px;
        }}
        .code-lines {{
            display: table;
            width: 100%;
        }}
        .code-line {{
            display: table-row;
            transition: background-color 0.2s;
        }}
        .code-line:hover {{
            background-color: #f0f0f0;
        }}
        .line-number {{
            display: table-cell;
            width: 50px;
            padding: 0 10px;
            text-align: right;
            background: #f8f8f8;
            color: #999;
            border-right: 1px solid #e0e0e0;
            user-select: none;
            font-size: 12px;
            vertical-align: top;
        }}
        .line-status {{
            display: table-cell;
            width: 30px;
            text-align: center;
            font-size: 14px;
            vertical-align: top;
            padding: 0 5px;
        }}
        .line-content {{
            display: table-cell;
            padding: 0 20px;
            white-space: pre;
            font-size: 14px;
            vertical-align: top;
        }}
        .covered {{
            background-color: #e8f5e9;
        }}
        .covered .line-status {{
            color: #4caf50;
        }}
        .missing {{
            background-color: #ffebee;
        }}
        .missing .line-status {{
            color: #f44336;
        }}
        .excluded {{
            background-color: #f5f5f5;
            color: #999;
        }}
        .excluded .line-status {{
            color: #999;
        }}
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            vertical-align: middle;
            margin-right: 5px;
            border-radius: 3px;
        }}
        .timestamp {{
            color: #666;
            font-size: 12px;
        }}
        /* Syntax highlighting */
        .keyword {{ color: #0000ff; font-weight: bold; }}
        .string {{ color: #008000; }}
        .comment {{ color: #808080; font-style: italic; }}
        .number {{ color: #098658; }}
        .function {{ color: #795E26; }}
        .class {{ color: #267F99; font-weight: bold; }}
        .back-link {{
            margin-bottom: 20px;
        }}
        .back-link a {{
            color: #0066cc;
            text-decoration: none;
        }}
        .back-link a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="back-link">
        <a href="index.html">← Back to Coverage Index</a>
    </div>

    <div class="header">
        <h1>Coverage Report: {html.escape(filename)}</h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>

        <div class="stats">
            <div class="stat">
                <span class="stat-label">Coverage</span>
                <span class="stat-value">{coverage_percent:.1f}%</span>
                <div class="coverage-bar">
                    <div class="coverage-fill" style="width: {coverage_percent}%"></div>
                </div>
            </div>
            <div class="stat">
                <span class="stat-label">Statements</span>
                <span class="stat-value">{total_statements}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Covered</span>
                <span class="stat-value" style="color: #4caf50">{len(covered_lines)}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Missing</span>
                <span class="stat-value" style="color: #f44336">{len(missing_lines)}</span>
            </div>
            <div class="stat">
                <span class="stat-label">Excluded</span>
                <span class="stat-value" style="color: #999">{len(excluded_lines)}</span>
            </div>
        </div>
    </div>

    <div class="code-container">
        <div class="code-header">Source Code</div>
        <div class="code-lines">
"""
        )

        # Generate line-by-line HTML
        in_multiline_comment = False
        for i, line in enumerate(source_lines, 1):
            # Check if line is empty or contains only whitespace
            stripped_line = line.rstrip("\n").rstrip()
            is_empty = not stripped_line

            # Check if line is a comment (starts with # or contains only whitespace + #)
            is_comment = stripped_line.lstrip().startswith("#")

            # Check if line starts with """ (docstring start/end)
            is_docstring_line = stripped_line.lstrip().startswith(
                '"""'
            ) or stripped_line.lstrip().startswith("'''")

            # Check for multiline comments (docstrings)
            if '"""' in stripped_line or "'''" in stripped_line:
                # Count quotes to determine if we're entering/exiting a multiline comment
                triple_double = stripped_line.count('"""')
                triple_single = stripped_line.count("'''")
                total_triple_quotes = triple_double + triple_single

                # If odd number of quotes, we're toggling the multiline comment state
                if total_triple_quotes % 2 == 1:
                    in_multiline_comment = not in_multiline_comment

            # Check if line is part of a multiline comment
            is_multiline_comment = in_multiline_comment or (
                stripped_line.startswith('"""') or stripped_line.startswith("'''")
            )

            if i in missing_lines:
                line_class = "missing"
                status_symbol = "&#10008;"
            elif (
                not is_empty
                and not is_comment
                and not is_multiline_comment
                and not is_docstring_line
            ):
                line_class = "covered"
                status_symbol = "&#10004;"
            else:
                line_class = ""
                status_symbol = ""

            # Simple HTML escaping without syntax highlighting to avoid issues
            highlighted_line = html.escape(line.rstrip("\n"))

            f.write(
                f"""            <div class="code-line {line_class}">
                <div class="line-number">{i}</div>
                <div class="line-status">{status_symbol}</div>
                <div class="line-content">{highlighted_line}</div>
            </div>
"""
            )

        f.write(
            """        </div>
    </div>

    <div class="legend">
        <h3 style="margin-top: 0;">Legend</h3>
        <div class="legend-item">
            <span class="legend-color" style="background: #e8f5e9;"></span>
            <span>&#10004; Covered</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #ffebee;"></span>
            <span>&#10008; Not Covered</span>
        </div>
        <div class="legend-item">
            <span class="legend-color" style="background: #f5f5f5;"></span>
            <span>&#8212; Excluded</span>
        </div>
    </div>
</body>
</html>
"""
        )

    print_success(f"HTML report generated: {output_file}")

    return (
        filename,
        coverage_percent,
        {"covered": len(covered_lines), "missing": len(missing_lines)},
    )


def generate_combined_index(
    output_dir: Path, file_reports: List[Tuple[str, float, Dict]], coverage_data: Dict
) -> None:
    """Generate a combined index HTML file with summary and links to detailed reports."""
    print_info("Generating combined index...")

    index_file = output_dir / "index.html"

    # Sort files by coverage percentage (ascending) so worst coverage is at top
    file_reports.sort(key=lambda x: x[1])

    # Get overall statistics
    summary = coverage_data.get("totals", {})
    overall_coverage = summary.get("percent_covered", 0)
    total_statements = summary.get("num_statements", 0)
    covered_lines = summary.get("covered_lines", 0)
    missing_lines = summary.get("missing_lines", 0)

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(
            f"""<!DOCTYPE html>
<html>
<head>
    <title>Combined Coverage Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .stat-card {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        .overall-coverage {{
            font-size: 48px;
            color: {'#4caf50' if overall_coverage >= 80 else '#ff9800' if overall_coverage >= 60 else '#f44336'};
        }}
        .file-list {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .file-header {{
            background: #333;
            color: white;
            padding: 15px 20px;
            font-weight: bold;
        }}
        .file-item {{
            display: flex;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid #e0e0e0;
            transition: background-color 0.2s;
        }}
        .file-item:hover {{
            background-color: #f8f9fa;
        }}
        .file-item:last-child {{
            border-bottom: none;
        }}
        .file-name {{
            flex: 1;
            margin-right: 20px;
        }}
        .file-name a {{
            color: #0066cc;
            text-decoration: none;
        }}
        .file-name a:hover {{
            text-decoration: underline;
        }}
        .file-stats {{
            display: flex;
            gap: 20px;
            align-items: center;
        }}
        .stat-item {{
            text-align: center;
            min-width: 80px;
        }}
        .stat-number {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }}
        .stat-label-small {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .coverage-percent {{
            font-size: 18px;
            font-weight: bold;
            color: {'#4caf50' if overall_coverage >= 80 else '#ff9800' if overall_coverage >= 60 else '#f44336'};
        }}
        .coverage-bar {{
            width: 150px;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-left: 20px;
        }}
        .coverage-fill {{
            height: 100%;
            transition: width 0.3s ease;
        }}
        .coverage-high {{ background: #4caf50; }}
        .coverage-medium {{ background: #ff9800; }}
        .coverage-low {{ background: #f44336; }}
        .filter-buttons {{
            margin-bottom: 20px;
        }}
        .filter-btn {{
            padding: 8px 16px;
            margin-right: 10px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .filter-btn:hover {{
            background: #f0f0f0;
        }}
        .filter-btn.active {{
            background: #0066cc;
            color: white;
            border-color: #0066cc;
        }}
        .download-links {{
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .download-links a {{
            color: #0066cc;
            text-decoration: none;
            margin-right: 20px;
        }}
        .download-links a:hover {{
            text-decoration: underline;
        }}
    </style>
    <script>
        function filterFiles(minCoverage, maxCoverage) {{
            const items = document.querySelectorAll('.file-item');
            items.forEach(item => {{
                const coverage = parseFloat(item.dataset.coverage);
                if (coverage >= minCoverage && coverage <= maxCoverage) {{
                    item.style.display = 'flex';
                }} else {{
                    item.style.display = 'none';
                }}
            }});

            // Update active button
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <h1>Combined Coverage Report</h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>

        <div class="summary-card">
            <h2 style="margin-top: 0;">Overall Project Coverage</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value overall-coverage">{overall_coverage:.1f}%</div>
                    <div class="stat-label">Overall Coverage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(file_reports)}</div>
                    <div class="stat-label">Files Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_statements:,}</div>
                    <div class="stat-label">Total Statements</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #4caf50">{covered_lines:,}</div>
                    <div class="stat-label">Covered Lines</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #f44336">{missing_lines:,}</div>
                    <div class="stat-label">Missing Lines</div>
                </div>
            </div>


        </div>

        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterFiles(0, 100)">All Files</button>
            <button class="filter-btn" onclick="filterFiles(0, 60)">Low Coverage (&lt;60%)</button>
            <button class="filter-btn" onclick="filterFiles(60, 80)">Medium Coverage (60-80%)</button>
            <button class="filter-btn" onclick="filterFiles(80, 100)">High Coverage (&gt;80%)</button>
        </div>

        <div class="file-list">
            <div class="file-header">Detailed Per-File Coverage Reports</div>
"""
        )

        for filename, coverage_percent, stats in file_reports:
            safe_filename = filename.replace("/", "_").replace("\\", "_")
            coverage_class = (
                "coverage-high"
                if coverage_percent >= 80
                else "coverage-medium" if coverage_percent >= 60 else "coverage-low"
            )
            coverage_color = (
                "#4caf50"
                if coverage_percent >= 80
                else "#ff9800" if coverage_percent >= 60 else "#f44336"
            )

            statements = stats.get("covered", 0) + stats.get("missing", 0)
            missing = stats.get("missing", 0)

            f.write(
                f"""            <div class="file-item" data-coverage="{coverage_percent}">
                <div class="file-name">
                    <a href="{safe_filename}.html">{html.escape(filename)}</a>
                </div>
                <div class="file-stats">
                    <div class="stat-item">
                        <div class="stat-number">{statements}</div>
                        <div class="stat-label-small">Statements</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" style="color: #f44336">{missing}</div>
                        <div class="stat-label-small">Missing</div>
                    </div>
                    <div class="stat-item">
                        <div class="coverage-percent" style="color: {coverage_color}">{coverage_percent:.1f}%</div>
                        <div class="stat-label-small">Coverage</div>
                    </div>
                    <div class="coverage-bar">
                        <div class="coverage-fill {coverage_class}" style="width: {coverage_percent}%"></div>
                    </div>
                </div>
            </div>
"""
            )

        f.write(
            """        </div>
    </div>
</body>
</html>
"""
        )

    print_success(f"Combined index generated: {index_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate combined coverage reports with summary and detailed per-file analysis"
    )
    parser.add_argument(
        "--output-dir",
        default="tests/reports/coverage",
        help="Output directory for all coverage reports",
    )
    parser.add_argument(
        "--run-tests", action="store_true", help="Run tests with coverage before generating reports"
    )
    parser.add_argument("--source-dir", default="c_to_plantuml", help="Source directory to analyze")

    args = parser.parse_args()

    print_header("Combined Coverage Report Generator")

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run coverage analysis if requested
    test_results = {}
    if args.run_tests:
        success, test_results = run_coverage_analysis()
        if not success:
            return 1

    # Get coverage data
    coverage_data = get_coverage_data()
    if not coverage_data:
        print_error(
            "No coverage data available. Run with --run-tests flag or ensure tests have been run with coverage."
        )
        return 1

    # Generate standard coverage reports
    print_subheader("Generating Standard Coverage Reports")

    # Terminal report
    subprocess.run(["python3", "-m", "coverage", "report", "-m"], check=False)

    # XML report
    subprocess.run(
        ["python3", "-m", "coverage", "xml", "-o", str(output_dir / "coverage.xml")], check=False
    )

    # JSON report (for reference)
    subprocess.run(
        ["python3", "-m", "coverage", "json", "-o", str(output_dir / "coverage.json")], check=False
    )

    # HTML coverage report
    subprocess.run(
        ["python3", "-m", "coverage", "html", "-d", str(output_dir / "htmlcov")], check=False
    )

    # Generate coverage summary
    generate_coverage_summary(coverage_data, output_dir)

    # Generate HTML test summary
    generate_test_summary_html(test_results, output_dir)

    # Process each file for detailed reports
    files_data = coverage_data.get("files", {})
    if not files_data:
        print_error("No files found in coverage data")
        return 1

    print_subheader(f"Generating Detailed Reports for {len(files_data)} Files")

    file_reports = []

    for filename, file_coverage in files_data.items():
        # Skip non-source files
        if not filename.startswith(args.source_dir):
            continue

        source_path = Path(filename)
        if not source_path.exists():
            print_error(f"Source file not found: {filename}")
            continue

        report_data = generate_html_file_report(filename, source_path, file_coverage, output_dir)

        if report_data[0]:  # Check if report was generated successfully
            file_reports.append(report_data)

    # Generate combined index
    if file_reports:
        generate_combined_index(output_dir, file_reports, coverage_data)

    print_header("Coverage Report Generation Complete!")
    print_info(f"All reports available in: {output_dir}")
    print_info(f"Open {output_dir}/index.html in your browser for the full report")
    print_success("Reports include:")
    print_success("  - Combined index with overall statistics")
    print_success("  - Per-file detailed coverage reports")
    print_success("  - Standard HTML coverage report in htmlcov/")
    print_success("  - Text summary report")
    print_success("  - XML and JSON exports")
    print_info("\nCoverage includes:")
    print_info("  - Unit test coverage")
    print_info("  - Execution coverage from example generation (if run)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
