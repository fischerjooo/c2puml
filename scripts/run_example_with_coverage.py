#!/usr/bin/env python3
"""
Run example generation with coverage tracking.
This script executes the C to PlantUML converter on the example project
to ensure execution coverage of the main code paths.
"""

import os
import subprocess
import sys
from pathlib import Path


def print_header(text: str) -> None:
    """Print a header with formatting."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"ℹ️  {text}")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"✅ {text}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"❌ {text}")


def run_example_generation():
    """Run the example generation with coverage."""
    print_header("Running Example Generation with Coverage")

    # Ensure we're in the workspace directory (project root, not scripts/)
    workspace_dir = Path(__file__).parent.parent
    os.chdir(workspace_dir)

    # Create output directory if it doesn't exist
    output_dir = workspace_dir / "output"
    output_dir.mkdir(exist_ok=True)

    # Run the full workflow (parse, transform, generate)
    print_info("Running full C to PlantUML workflow on example project...")

    commands = [
        # Full workflow
        [
            "coverage",
            "run",
            "-a",
            "-m",
            "c2puml.main",
            "--config",
            "tests/example/config.json",
        ],
        # Individual steps for better coverage
        [
            "coverage",
            "run",
            "-a",
            "-m",
            "c2puml.main",
            "--config",
            "tests/example/config.json",
            "parse",
        ],
        [
            "coverage",
            "run",
            "-a",
            "-m",
            "c2puml.main",
            "--config",
            "tests/example/config.json",
            "transform",
        ],
        [
            "coverage",
            "run",
            "-a",
            "-m",
            "c2puml.main",
            "--config",
            "tests/example/config.json",
            "generate",
        ],
        # Try with verbose flag
        [
            "coverage",
            "run",
            "-a",
            "-m",
            "c2puml.main",
            "--config",
            "tests/example/config.json",
            "--verbose",
        ],
    ]

    success = True
    for cmd in commands:
        print_info(f"Running: {' '.join(cmd[3:])}")  # Print without coverage command
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print_success(f"Command completed successfully")
                if result.stdout:
                    print(result.stdout)
            else:
                print_error(f"Command failed with return code {result.returncode}")
                if result.stderr:
                    print(result.stderr)
                success = False
        except Exception as e:
            print_error(f"Error running command: {e}")
            success = False

    # Check if output files were generated
    expected_outputs = [
                    "artifacts/output_example/model.json",
            "artifacts/output_example/model_transformed.json",
    ]

    print_info("\nChecking generated outputs...")
    for output_file in expected_outputs:
        if Path(output_file).exists():
            print_success(f"Generated: {output_file}")
        else:
            print_error(f"Missing: {output_file}")

    # Check for PlantUML files
    puml_files = list(Path("output").glob("*.puml"))
    if puml_files:
        print_success(f"Generated {len(puml_files)} PlantUML files:")
        for puml in puml_files:
            print(f"  - {puml.name}")
    else:
        print_error("No PlantUML files generated")

    return success


def main():
    """Main function."""
    print_header("Example Generation Coverage Runner")

    # Check if coverage is available
    try:
        subprocess.run(["coverage", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Coverage not installed. Install with: pip install coverage")
        return 1

    # Run example generation
    success = run_example_generation()

    if success:
        print_header("Example Generation Complete!")
        print_success("All example generation commands executed")
        print_info("Coverage data has been appended to .coverage file")
        print_info("Run coverage report generation to see updated results")
    else:
        print_error("Some example generation commands failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
