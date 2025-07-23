#!/usr/bin/env python3
"""
Debug entry point for C to PlantUML converter

This script provides a convenient way to debug the converter with predefined configurations.
It can be run directly from VSCode in debug mode.

Usage:
    python debug.py [command] [options]

Commands:
    parse      - Run parsing step only
    transform  - Run transformation step only  
    generate   - Run generation step only
    example    - Run with example configuration
    full       - Run full workflow (default)
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from c_to_plantuml.main import main as main_function


def setup_debug_logging():
    """Setup logging for debug mode"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def create_test_config():
    """Create a test configuration for debugging"""
    config = {
        "project_name": "Debug_Test_Project",
        "source_folders": ["./example"],
        "output_dir": "./output/debug",
        "model_output_path": "debug_model.json",
        "recursive_search": True,
        "include_depth": 2,
        "file_filters": {
            "include": [r".*\.(c|h)$"],
            "exclude": [r".*test.*", r".*mock.*"]
        },
        "element_filters": {
            "structs": {
                "include": [r".*"],
                "exclude": [r".*internal.*", r".*private.*"]
            },
            "functions": {
                "include": [r".*"],
                "exclude": [r".*test.*", r".*mock.*"]
            }
        },
        "transformations": {
            "file_selection": {
                "selected_files": [r".*\.c$"]
            }
        }
    }
    
    # Create output directory
    os.makedirs("./output/debug", exist_ok=True)
    
    # Save config to file
    config_path = "./output/debug/debug_config.json"
    import json
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return config_path


def create_example_config():
    """Create an example configuration for debugging"""
    config = {
        "project_name": "Example_Project",
        "source_folders": ["./example"],
        "output_dir": "./output/example",
        "model_output_path": "example_model.json",
        "recursive_search": True,
        "include_depth": 1,
        "file_filters": {
            "include": [r".*\.(c|h)$"],
            "exclude": []
        },
        "element_filters": {},
        "transformations": {}
    }
    
    # Create output directory
    os.makedirs("./output/example", exist_ok=True)
    
    # Save config to file
    config_path = "./output/example/example_config.json"
    import json
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return config_path


def main():
    """Main debug entry point"""
    parser = argparse.ArgumentParser(
        description="Debug entry point for C to PlantUML converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python debug.py                    # Run full workflow with test config
    python debug.py parse              # Run parsing step only
    python debug.py transform          # Run transformation step only
    python debug.py generate           # Run generation step only
    python debug.py example            # Run with example configuration
    python debug.py full               # Run full workflow (explicit)
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        choices=["parse", "transform", "generate", "example", "full"],
        default="full",
        help="Which step to run (default: full)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to custom config file (overrides default test config)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        setup_debug_logging()
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
    
    # Determine config path
    if args.config:
        config_path = args.config
        logging.info(f"Using custom config: {config_path}")
    elif args.command == "example":
        config_path = create_example_config()
        logging.info(f"Created example config: {config_path}")
    else:
        config_path = create_test_config()
        logging.info(f"Created test config: {config_path}")
    
    # Set up sys.argv to simulate command line arguments for main function
    original_argv = sys.argv.copy()
    
    try:
        # Prepare arguments for main function
        main_args = ["debug.py"]  # Script name
        
        if args.config or args.command in ["example", "full"]:
            # Use config file
            main_args.extend(["--config", config_path])
        
        if args.command != "full":
            main_args.append(args.command)
        
        if args.verbose:
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