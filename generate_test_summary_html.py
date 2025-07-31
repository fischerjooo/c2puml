#!/usr/bin/env python3
"""
Generate HTML test summary from test results.
This script reads test output and generates a beautiful HTML summary.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def parse_test_output(log_file: Path) -> Dict:
    """Parse test output log and extract statistics."""
    if not log_file.exists():
        return {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "execution_time": 0,
            "status": "UNKNOWN",
            "test_summary": "",
            "failed_tests": [],
        }

    content = log_file.read_text()

    # Initialize default values
    stats = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "execution_time": 0,
        "status": "UNKNOWN",
        "test_summary": "",
        "failed_tests": [],
    }

    # Extract test summary line - handle both unittest and pytest formats
    test_summary_match = re.search(r"Ran (\d+) test", content)
    if test_summary_match:
        # unittest format
        stats["total_tests"] = int(test_summary_match.group(1))

        # Check for OK or FAILED status (unittest)
        if "OK" in content:
            stats["status"] = "PASSED"
            stats["passed"] = stats["total_tests"]
        elif "FAILED" in content:
            stats["status"] = "FAILED"
            # Extract failure details
            failed_match = re.search(
                r"FAILED \(.*?failures=(\d+).*?errors=(\d+)\)", content
            )
            if failed_match:
                stats["failed"] = int(failed_match.group(1))
                stats["errors"] = int(failed_match.group(2))
                stats["passed"] = (
                    stats["total_tests"] - stats["failed"] - stats["errors"]
                )
    else:
        # pytest format - look for summary line like "329 passed in 2.66s"
        pytest_summary_match = re.search(r"(\d+) passed in ([\d.]+)s", content)
        if pytest_summary_match:
            stats["total_tests"] = int(pytest_summary_match.group(1))
            stats["passed"] = stats["total_tests"]
            stats["status"] = "PASSED"
            stats["execution_time"] = float(pytest_summary_match.group(2))
        else:
            # Look for pytest summary with failures/errors
            pytest_failed_match = re.search(
                r"(\d+) passed.*?(\d+) failed.*?(\d+) error.*?in ([\d.]+)s", content
            )
            if pytest_failed_match:
                stats["total_tests"] = (
                    int(pytest_failed_match.group(1))
                    + int(pytest_failed_match.group(2))
                    + int(pytest_failed_match.group(3))
                )
                stats["passed"] = int(pytest_failed_match.group(1))
                stats["failed"] = int(pytest_failed_match.group(2))
                stats["errors"] = int(pytest_failed_match.group(3))
                stats["status"] = "FAILED"
                stats["execution_time"] = float(pytest_failed_match.group(4))
            else:
                # Look for pytest summary with just failures
                pytest_failed_only_match = re.search(
                    r"(\d+) passed.*?(\d+) failed.*?in ([\d.]+)s", content
                )
                if pytest_failed_only_match:
                    stats["total_tests"] = int(pytest_failed_only_match.group(1)) + int(
                        pytest_failed_only_match.group(2)
                    )
                    stats["passed"] = int(pytest_failed_only_match.group(1))
                    stats["failed"] = int(pytest_failed_only_match.group(2))
                    stats["status"] = "FAILED"
                    stats["execution_time"] = float(pytest_failed_only_match.group(3))

    # Extract execution time (only if not already set by pytest parsing)
    if stats["execution_time"] == 0:
        time_match = re.search(r"in ([\d.]+)s", content)
        if time_match:
            stats["execution_time"] = float(time_match.group(1))

    # Extract failed test details
    failed_lines = []
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "FAILED" in line or "ERROR" in line:
            # Get context around the failure
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            failed_lines.extend(lines[start:end])

    stats["failed_tests"] = failed_lines[:20]  # Limit to first 20 lines

    return stats


def generate_html_summary(stats: Dict, output_file: Path) -> None:
    """Generate HTML test summary."""

    # Calculate success rate
    total = stats["total_tests"]
    passed = stats["passed"]
    success_rate = (passed / total * 100) if total > 0 else 0

    # Determine status color
    status_color = "#4caf50" if stats["status"] == "PASSED" else "#f44336"

    html_content = f"""<!DOCTYPE html>
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
            color: #4caf50;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            text-transform: uppercase;
            color: white;
            background: {status_color};
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
            white-space: pre-wrap;
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
        .nav {{ 
            background: #0366d6; 
            color: white; 
            padding: 15px 20px; 
            border-radius: 6px; 
            margin-bottom: 20px; 
        }}
        .nav a {{ 
            color: white; 
            text-decoration: none; 
            margin-right: 20px; 
            font-weight: 500; 
        }}
        .nav a:hover {{ 
            text-decoration: underline; 
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="../../index.html">🏠 Home</a>
            <a href="coverage/htmlcov/index.html">📊 Coverage</a>
            <span style="background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 4px;">📝 Tests</span>
            <a href="../../output/diagram_index.html">📊 Diagrams</a>
            <a href="../../example/">📋 Examples</a>
        </div>

        <h1>Test Results Summary</h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>

        <div class="summary-card">
            <h2 style="margin-top: 0;">Test Execution Results</h2>
            <div style="margin-bottom: 20px;">
                <span class="status-badge">{stats['status']}</span>
                <span style="margin-left: 10px; color: #666;">Execution completed in {stats['execution_time']:.2f} seconds</span>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value success-rate">{success_rate:.1f}%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{stats['total_tests']}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #4caf50">{stats['passed']}</div>
                    <div class="stat-label">Passed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #f44336">{stats['failed']}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #ff9800">{stats['skipped']}</div>
                    <div class="stat-label">Skipped</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: #9c27b0">{stats['errors']}</div>
                    <div class="stat-label">Errors</div>
                </div>
            </div>

            <div class="test-details">
                <h3>Test Execution Details</h3>
                <p><strong>Total Tests:</strong> {stats['total_tests']}</p>
                <p><strong>Passed:</strong> {stats['passed']} ({success_rate:.1f}%)</p>
                <p><strong>Failed:</strong> {stats['failed']} ({(stats['failed']/total*100) if total > 0 else 0:.1f}%)</p>
                <p><strong>Skipped:</strong> {stats['skipped']} ({(stats['skipped']/total*100) if total > 0 else 0:.1f}%)</p>
                <p><strong>Errors:</strong> {stats['errors']} ({(stats['errors']/total*100) if total > 0 else 0:.1f}%)</p>
                <p><strong>Execution Time:</strong> {stats['execution_time']:.2f} seconds</p>
                <p><strong>Overall Status:</strong> {stats['status']}</p>
            </div>

            {f'''
            <div class="failed-tests">
                <div class="failed-header">Failed Tests Details</div>
                {''.join(f'<div class="failed-item">{line}</div>' for line in stats['failed_tests'])}
            </div>
            ''' if stats['failed_tests'] else ''}

        </div>
    </div>
</body>
</html>"""

    output_file.write_text(html_content)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate HTML test summary from test results"
    )
    parser.add_argument(
        "--log-file",
        default="tests/reports/test-output.log",
        help="Path to test output log file (default: tests/reports/test-output.log)",
    )
    parser.add_argument(
        "--output-file",
        default="tests/reports/test_summary.html",
        help="Path to output HTML file (default: tests/reports/test_summary.html)",
    )

    args = parser.parse_args()

    log_file = Path(args.log_file)
    output_file = Path(args.output_file)

    print(f"📊 Generating HTML test summary...")
    print(f"📁 Reading test results from: {log_file}")

    # Parse test output
    stats = parse_test_output(log_file)

    # Generate HTML summary
    generate_html_summary(stats, output_file)

    print(f"✅ HTML test summary generated: {output_file}")
    print(f"📈 Test Statistics:")
    print(f"   - Total Tests: {stats['total_tests']}")
    print(f"   - Passed: {stats['passed']}")
    print(f"   - Failed: {stats['failed']}")
    print(f"   - Errors: {stats['errors']}")
    print(f"   - Status: {stats['status']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
