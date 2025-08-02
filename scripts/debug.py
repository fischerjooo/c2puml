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
# =============================================================================

# Default configuration file path (relative to project root)
CONFIG_PATH: str = "./tests/example/config.json"

# Default verbose output
VERBOSE: bool = True

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

    # Add default config if no config specified in arguments
    if not any(arg.startswith('--config') or arg.startswith('-c') for arg in sys.argv[1:]):
        cmd.extend(["--config", CONFIG_PATH])

    # Add default verbose if not specified in arguments
    if VERBOSE and not any(arg.startswith('--verbose') or arg.startswith('-v') for arg in sys.argv[1:]):
        cmd.append("--verbose")

    # Forward all command line arguments
    cmd.extend(sys.argv[1:])

    logging.info("Debug Configuration:")
    logging.info("  Default Config: %s", CONFIG_PATH)
    logging.info("  Default Verbose: %s", VERBOSE)
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
