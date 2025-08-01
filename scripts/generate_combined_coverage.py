#!/usr/bin/env python3
"""
Generate coverage reports using the standard coverage tool.
This script runs tests with coverage and generates standard HTML reports.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict


def print_header(text: str) -> None:
    """Print a header with formatting."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


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
        subprocess.run(
            ["python3", "-m", "coverage", "--version"], check=True, capture_output=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Coverage not installed. Install with: pip install coverage")
        return False

    # Clean previous coverage data
    print_info("Cleaning previous coverage data...")
    subprocess.run(["python3", "-m", "coverage", "erase"], check=True)

    # Run tests with coverage
    print_info("Running tests with coverage...")
    result = subprocess.run(
        ["python3", "-m", "coverage", "run", "-m", "pytest", "-v"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print_error("Tests failed. Coverage report may be incomplete.")
        print(result.stderr)
        return False

    print_success("Tests completed successfully")
    return True


def generate_coverage_reports(output_dir: Path) -> None:
    """Generate standard coverage reports."""
    print_header("Generating Coverage Reports")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Terminal report
    print_info("Generating terminal report...")
    subprocess.run(["python3", "-m", "coverage", "report", "-m"], check=False)

    # XML report
    print_info("Generating XML report...")
    subprocess.run(
        ["python3", "-m", "coverage", "xml", "-o", str(output_dir / "coverage.xml")],
        check=False,
    )

    # JSON report
    print_info("Generating JSON report...")
    subprocess.run(
        ["python3", "-m", "coverage", "json", "-o", str(output_dir / "coverage.json")],
        check=False,
    )

    # HTML coverage report (this creates the htmlcov directory)
    print_info("Generating HTML report...")
    subprocess.run(
        ["python3", "-m", "coverage", "html", "-d", str(output_dir / "htmlcov")],
        check=False,
    )

    print_success("All coverage reports generated successfully")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate standard coverage reports using the coverage tool"
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts/coverage",
        help="Output directory for coverage reports (default: artifacts/coverage)",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Run tests with coverage before generating reports",
    )

    args = parser.parse_args()

    print_header("Coverage Report Generator")

    # Run coverage analysis if requested
    if args.run_tests:
        if not run_coverage_analysis():
            return 1

    # Generate coverage reports
    output_dir = Path(args.output_dir)
    generate_coverage_reports(output_dir)

    print_header("Coverage Report Generation Complete!")
    print_info(f"All reports available in: {output_dir}")
    print_info(
        f"Open {output_dir}/htmlcov/index.html in your browser for the HTML report"
    )
    print_success("Reports include:")
    print_success("  - Standard HTML coverage report in htmlcov/")
    print_success("  - XML report (coverage.xml)")
    print_success("  - JSON report (coverage.json)")
    print_success("  - Terminal summary")

    return 0


if __name__ == "__main__":
    sys.exit(main())
