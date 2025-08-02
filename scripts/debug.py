#!/usr/bin/env python3
"""
Debug entry point for C to PlantUML converter

This script provides a convenient way to debug the converter with predefined configurations.
It uses the standalone c2puml.py script directly.

Configuration is done by modifying the constants at the top of this file, or by passing
command line arguments.

Usage:
    python debug.py                           # Uses internal DEBUG CONFIGURATION
    python debug.py parse                     # Parse only workflow
    python debug.py transform                 # Transform only workflow
    python debug.py generate                  # Generate only workflow
    python debug.py --config ./my_config.json # Use custom config file
    python debug.py parse --config ./my_config.json # Parse with custom config
"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

# =============================================================================
# DEBUG CONFIGURATION - Modify these constants as needed
# =============================================================================

# Workflow selection: "full", "parse", "transform", "generate"
WORKFLOW: str = "full"

# Configuration file path (relative to project root)
CONFIG_PATH: str = "./tests/example/config.json"

# Verbose output
VERBOSE: bool = True

# =============================================================================
# END CONFIGURATION
# =============================================================================


def setup_logging(verbose: bool):
    """Setup logging based on configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Debug entry point for C to PlantUML converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Uses internal DEBUG CONFIGURATION
  %(prog)s parse                     # Parse only workflow
  %(prog)s transform                 # Transform only workflow
  %(prog)s generate                  # Generate only workflow
  %(prog)s --config ./my_config.json # Use custom config file
  %(prog)s parse --config ./my_config.json # Parse with custom config
        """,
    )
    parser.add_argument(
        "workflow",
        nargs="?",
        choices=["parse", "transform", "generate"],
        help="Which workflow to run: parse, transform, or generate. If omitted, runs full workflow.",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to config file (optional, uses internal CONFIG_PATH if not provided)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output (overrides internal VERBOSE setting)",
    )

    return parser.parse_args()


def main():
    """Main debug entry point"""
    # Parse command line arguments
    args = parse_arguments()

    # Determine workflow from arguments or use default
    workflow = args.workflow if args.workflow else WORKFLOW

    # Determine config path from arguments or use default
    config_path = args.config if args.config else CONFIG_PATH

    # Determine verbose setting from arguments or use default
    verbose = args.verbose if args.verbose is not None else VERBOSE

    # Setup logging
    setup_logging(verbose)

    # Validate configuration
    if workflow not in ["full", "parse", "transform", "generate"]:
        logging.error(
            "Invalid workflow: %s. Must be one of: full, parse, transform, generate",
            workflow,
        )
        return 1

    # Check if config file exists
    if not os.path.exists(config_path):
        logging.error("Configuration file not found: %s", config_path)
        logging.error(
            "Please ensure the config file exists or update CONFIG_PATH in debug.py"
        )
        return 1

    logging.info("Debug Configuration:")
    logging.info("  Workflow: %s", workflow)
    logging.info("  Config: %s", config_path)
    logging.info("  Verbose: %s", verbose)

    # Get project root (go up one level from scripts/ directory)
    project_root = Path(__file__).parent.parent
    c2puml_script = project_root / "c2puml.py"

    if not c2puml_script.exists():
        logging.error("c2puml.py not found at: %s", c2puml_script)
        return 1

    # Build command for c2puml.py
    cmd = [sys.executable, str(c2puml_script), "--config", config_path]

    # Add workflow command
    if workflow != "full":
        cmd.append(workflow)

    # Add verbose flag
    if verbose:
        cmd.append("--verbose")

    logging.info("Running command: %s", " ".join(cmd))

    try:
        # Run c2puml.py
        result = subprocess.run(cmd, cwd=project_root)
        
        logging.info("Debug run completed with result: %s", result.returncode)
        return result.returncode

    except Exception as e:
        logging.error("Debug run failed: %s", e)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
