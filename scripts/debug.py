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
    c2puml_script = project_root / "c2puml_standalone.py"

    if not c2puml_script.exists():
        logging.error("c2puml_standalone.py not found at: %s", c2puml_script)
        return 1

    # Build command for c2puml_standalone.py
    cmd = [sys.executable, str(c2puml_script)]

    # Check if constants are defined (uncommented)
    has_command = 'COMMAND' in globals()
    has_config = 'CONFIG_PATH' in globals()
    has_verbose = 'VERBOSE' in globals()

    # Get command line arguments (excluding script name)
    args = sys.argv[1:]

    # Handle COMMAND constant - overrides any command in arguments
    if has_command:
        cmd.append(COMMAND)
        logging.info("Overriding command with: %s", COMMAND)
        # Remove any existing command from arguments
        args = [arg for arg in args if arg not in ['parse', 'transform', 'generate']]

    # Handle CONFIG_PATH constant - overrides any config in arguments
    if has_config:
        cmd.extend(["--config", CONFIG_PATH])
        logging.info("Overriding config with: %s", CONFIG_PATH)
        # Remove any existing config arguments
        args = [arg for i, arg in enumerate(args) if not (arg.startswith('--config') or arg.startswith('-c')) and (i == 0 or not args[i-1].startswith('--config'))]

    # Handle VERBOSE constant - overrides any verbose in arguments
    if has_verbose:
        if VERBOSE:
            cmd.append("--verbose")
            logging.info("Overriding verbose with: %s", VERBOSE)
        # Remove any existing verbose arguments
        args = [arg for arg in args if not (arg.startswith('--verbose') or arg.startswith('-v'))]

    # Forward remaining command line arguments
    cmd.extend(args)

    # Log configuration summary
    logging.info("Debug Configuration:")
    if has_command:
        logging.info("  Override Command: %s", COMMAND)
    if has_config:
        logging.info("  Override Config: %s", CONFIG_PATH)
    if has_verbose:
        logging.info("  Override Verbose: %s", VERBOSE)
    if not any([has_command, has_config, has_verbose]):
        logging.info("  No overrides configured - forwarding arguments as-is")
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
