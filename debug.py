#!/usr/bin/env python3
"""
Debug entry point for C to PlantUML converter

This script provides a convenient way to debug the converter with predefined configurations.
It can be run directly from VSCode in debug mode.

Configuration is done by modifying the variables at the top of this file.
"""

import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from c_to_plantuml.main import main as main_function

# =============================================================================
# DEBUG CONFIGURATION - Modify these variables as needed
# =============================================================================

# Workflow selection: "full", "parse", "transform", "generate"
WORKFLOW = "full"

# Configuration file path (relative to project root)
CONFIG_PATH = "./example/config.json"

# Verbose output
VERBOSE = True

# =============================================================================
# END CONFIGURATION
# =============================================================================


def setup_logging():
    """Setup logging based on configuration"""
    level = logging.DEBUG if VERBOSE else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    """Main debug entry point"""
    # Setup logging
    setup_logging()
    
    # Validate configuration
    if WORKFLOW not in ["full", "parse", "transform", "generate"]:
        logging.error(f"Invalid workflow: {WORKFLOW}. Must be one of: full, parse, transform, generate")
        return 1
    
    # Check if config file exists
    if not os.path.exists(CONFIG_PATH):
        logging.error(f"Configuration file not found: {CONFIG_PATH}")
        logging.error("Please ensure the config file exists or update CONFIG_PATH in debug.py")
        return 1
    
    logging.info(f"Debug Configuration:")
    logging.info(f"  Workflow: {WORKFLOW}")
    logging.info(f"  Config: {CONFIG_PATH}")
    logging.info(f"  Verbose: {VERBOSE}")
    
    # Set up sys.argv to simulate command line arguments for main function
    original_argv = sys.argv.copy()
    
    try:
        # Prepare arguments for main function
        main_args = ["debug.py"]  # Script name
        
        # Add config file
        main_args.extend(["--config", CONFIG_PATH])
        
        # Add workflow command
        if WORKFLOW != "full":
            main_args.append(WORKFLOW)
        
        # Add verbose flag
        if VERBOSE:
            main_args.append("--verbose")
        
        # Replace sys.argv
        sys.argv = main_args
        
        logging.info(f"Running with arguments: {main_args}")
        
        # Call the main function
        result = main_function()
        
        logging.info(f"Debug run completed with result: {result}")
        return result
        
    except Exception as e:
        logging.error(f"Debug run failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Restore original argv
        sys.argv = original_argv


if __name__ == "__main__":
    sys.exit(main())