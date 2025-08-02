#!/usr/bin/env python3
"""
Debug entry point for C to PlantUML converter

This script provides a convenient way to debug the converter with predefined configurations.
It uses the standalone c2puml.py script directly.

Configuration is done by modifying the constants at the top of this file.
All command line arguments are forwarded directly to c2puml.py.

Usage:
    python debug.py                           # Uses internal DEBUG CONFIGURATION
    python debug.py parse                     # Parse only workflow
    python debug.py transform                 # Transform only workflow
    python debug.py generate                  # Generate only workflow
    python debug.py --config ./my_config.json # Use custom config file
    python debug.py parse --config ./my_config.json # Parse with custom config
"""

import logging
import subprocess
import sys
from pathlib import Path

# =============================================================================
# DEBUG CONFIGURATION - Modify these constants as needed
# Uncomment and modify the constants you want to use to override parameters
# =============================================================================

# Default command to run (parse, transform, generate, or leave empty for full workflow)
# COMMAND: str = "parse"

# Default configuration file path (relative to project root)
# CONFIG_PATH: str = "./tests/example/config.json"

# Default verbose output
# VERBOSE: bool = True

# =============================================================================
# END CONFIGURATION
# =============================================================================


def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    """Main debug entry point"""
    setup_logging()

    # Get project root (go up one level from scripts/ directory)
    project_root = Path(__file__).parent.parent
    c2puml_script = project_root / "c2puml.py"

    if not c2puml_script.exists():
        logging.error("c2puml.py not found at: %s", c2puml_script)
        return 1

    # Build command for c2puml.py
    cmd = [sys.executable, str(c2puml_script)]

    # Check if constants are defined (uncommented)
    has_command = 'COMMAND' in globals()
    has_config = 'CONFIG_PATH' in globals()
    has_verbose = 'VERBOSE' in globals()

    # Get command line arguments (excluding script name)
    args = sys.argv[1:]

    # Handle COMMAND constant
    if has_command:
        # Check if a command is already specified in arguments
        command_specified = any(arg in ['parse', 'transform', 'generate'] for arg in args)
        if not command_specified:
            cmd.append(COMMAND)
            logging.info("Using default command: %s", COMMAND)

    # Handle CONFIG_PATH constant
    if has_config:
        # Check if config is already specified in arguments
        config_specified = any(arg.startswith('--config') or arg.startswith('-c') for arg in args)
        if not config_specified:
            cmd.extend(["--config", CONFIG_PATH])
            logging.info("Using default config: %s", CONFIG_PATH)

    # Handle VERBOSE constant
    if has_verbose:
        # Check if verbose is already specified in arguments
        verbose_specified = any(arg.startswith('--verbose') or arg.startswith('-v') for arg in args)
        if not verbose_specified and VERBOSE:
            cmd.append("--verbose")
            logging.info("Using default verbose: %s", VERBOSE)

    # Forward all command line arguments
    cmd.extend(args)

    # Log configuration summary
    logging.info("Debug Configuration:")
    if has_command:
        logging.info("  Default Command: %s", COMMAND)
    if has_config:
        logging.info("  Default Config: %s", CONFIG_PATH)
    if has_verbose:
        logging.info("  Default Verbose: %s", VERBOSE)
    if not any([has_command, has_config, has_verbose]):
        logging.info("  No defaults configured - forwarding arguments as-is")
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
