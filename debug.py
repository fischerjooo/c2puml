#!/usr/bin/env python3
"""
Debug entry point for C to PlantUML converter

This script provides a convenient way to debug the converter with predefined configurations.
It can be run directly from VSCode in debug mode with interactive configuration options.

Usage:
    python debug.py [command] [options]
    python debug.py --interactive  # Interactive mode

Commands:
    parse      - Run parsing step only
    transform  - Run transformation step only  
    generate   - Run generation step only
    example    - Run with example configuration
    full       - Run full workflow (default)
    interactive - Interactive mode to select workflow and configuration
"""

import argparse
import logging
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

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
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return config_path


def create_custom_config():
    """Create a custom configuration with user input"""
    print("\n=== Custom Configuration Setup ===")
    
    # Project settings
    project_name = input("Project name [Debug_Custom_Project]: ").strip() or "Debug_Custom_Project"
    source_folders_input = input("Source folders (comma-separated) [./example]: ").strip() or "./example"
    source_folders = [f.strip() for f in source_folders_input.split(",")]
    
    output_dir = input("Output directory [./output/custom]: ").strip() or "./output/custom"
    model_output_path = input("Model output filename [custom_model.json]: ").strip() or "custom_model.json"
    
    # Processing settings
    recursive_search = input("Recursive search? (y/n) [y]: ").strip().lower() != 'n'
    include_depth = int(input("Include depth [1]: ").strip() or "1")
    
    # File filters
    print("\n--- File Filters ---")
    include_patterns_input = input("Include patterns (comma-separated regex) [.*\\.(c|h)$]: ").strip() or r".*\.(c|h)$"
    include_patterns = [p.strip() for p in include_patterns_input.split(",")]
    
    exclude_patterns_input = input("Exclude patterns (comma-separated regex) []: ").strip()
    exclude_patterns = [p.strip() for p in exclude_patterns_input.split(",")] if exclude_patterns_input else []
    
    # Element filters
    print("\n--- Element Filters ---")
    filter_structs = input("Filter structs? (y/n) [n]: ").strip().lower() == 'y'
    filter_functions = input("Filter functions? (y/n) [n]: ").strip().lower() == 'y'
    
    config = {
        "project_name": project_name,
        "source_folders": source_folders,
        "output_dir": output_dir,
        "model_output_path": model_output_path,
        "recursive_search": recursive_search,
        "include_depth": include_depth,
        "file_filters": {
            "include": include_patterns,
            "exclude": exclude_patterns
        },
        "element_filters": {},
        "transformations": {}
    }
    
    # Add element filters if requested
    if filter_structs:
        struct_include = input("Struct include patterns (comma-separated) [.*]: ").strip() or ".*"
        struct_exclude = input("Struct exclude patterns (comma-separated) []: ").strip()
        config["element_filters"]["structs"] = {
            "include": [p.strip() for p in struct_include.split(",")],
            "exclude": [p.strip() for p in struct_exclude.split(",")] if struct_exclude else []
        }
    
    if filter_functions:
        func_include = input("Function include patterns (comma-separated) [.*]: ").strip() or ".*"
        func_exclude = input("Function exclude patterns (comma-separated) []: ").strip()
        config["element_filters"]["functions"] = {
            "include": [p.strip() for p in func_include.split(",")],
            "exclude": [p.strip() for p in func_exclude.split(",")] if func_exclude else []
        }
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save config to file
    config_path = os.path.join(output_dir, "custom_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\nCustom configuration saved to: {config_path}")
    return config_path


def interactive_mode():
    """Interactive mode for selecting workflow and configuration"""
    print("=== C to PlantUML Converter - Interactive Debug Mode ===\n")
    
    # Step 1: Select workflow
    print("1. Select Workflow:")
    print("   1. Full Workflow (parse → transform → generate)")
    print("   2. Parse Only (generate model.json)")
    print("   3. Transform Only (transform existing model.json)")
    print("   4. Generate Only (generate PlantUML from model)")
    print("   5. Parse + Transform (skip generation)")
    print("   6. Transform + Generate (skip parsing)")
    
    while True:
        workflow_choice = input("\nSelect workflow (1-6) [1]: ").strip() or "1"
        if workflow_choice in ["1", "2", "3", "4", "5", "6"]:
            break
        print("Invalid choice. Please select 1-6.")
    
    # Step 2: Select configuration
    print("\n2. Select Configuration:")
    print("   1. Test Configuration (with filters)")
    print("   2. Example Configuration (minimal)")
    print("   3. Custom Configuration (interactive setup)")
    print("   4. Use existing config file")
    
    while True:
        config_choice = input("\nSelect configuration (1-4) [1]: ").strip() or "1"
        if config_choice in ["1", "2", "3", "4"]:
            break
        print("Invalid choice. Please select 1-4.")
    
    # Step 3: Handle custom configuration
    config_path = None
    if config_choice == "1":
        config_path = create_test_config()
        print(f"Using test configuration: {config_path}")
    elif config_choice == "2":
        config_path = create_example_config()
        print(f"Using example configuration: {config_path}")
    elif config_choice == "3":
        config_path = create_custom_config()
    elif config_choice == "4":
        config_path = input("Enter path to existing config file: ").strip()
        if not os.path.exists(config_path):
            print(f"Error: Config file not found: {config_path}")
            return 1
    
    # Step 4: Select verbosity
    verbose = input("\n3. Verbose output? (y/n) [n]: ").strip().lower() == 'y'
    
    # Step 5: Execute workflow
    print(f"\n=== Executing Workflow ===")
    print(f"Workflow: {workflow_choice}")
    print(f"Config: {config_path}")
    print(f"Verbose: {verbose}")
    
    # Map workflow choices to commands
    workflow_map = {
        "1": "full",
        "2": "parse", 
        "3": "transform",
        "4": "generate",
        "5": "parse_transform",  # Custom handling needed
        "6": "transform_generate"  # Custom handling needed
    }
    
    command = workflow_map[workflow_choice]
    
    # Handle special cases
    if command in ["parse_transform", "transform_generate"]:
        return execute_custom_workflow(command, config_path, verbose)
    else:
        return execute_standard_workflow(command, config_path, verbose)


def execute_standard_workflow(command: str, config_path: str, verbose: bool) -> int:
    """Execute standard workflow with given command"""
    # Set up sys.argv to simulate command line arguments for main function
    original_argv = sys.argv.copy()
    
    try:
        # Prepare arguments for main function
        main_args = ["debug.py"]  # Script name
        
        if config_path:
            main_args.extend(["--config", config_path])
        
        if command != "full":
            main_args.append(command)
        
        if verbose:
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


def execute_custom_workflow(workflow: str, config_path: str, verbose: bool) -> int:
    """Execute custom workflow (parse+transform or transform+generate)"""
    print(f"\nExecuting custom workflow: {workflow}")
    
    # Load configuration
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return 1
    
    # Determine output paths
    output_dir = config_data.get("output_dir", "./output")
    model_file = os.path.join(output_dir, config_data.get("model_output_path", "model.json"))
    transformed_model_file = os.path.join(output_dir, "model_transformed.json")
    
    try:
        if workflow == "parse_transform":
            # Step 1: Parse
            print("Step 1: Parsing...")
            from c_to_plantuml.parser import Parser
            parser_obj = Parser()
            parser_obj.parse(
                project_root=config_data["source_folders"],
                output_file=model_file,
                recursive_search=config_data.get("recursive_search", True),
                config=None  # We'll handle config manually
            )
            print(f"Model saved to: {model_file}")
            
            # Step 2: Transform
            print("Step 2: Transforming...")
            from c_to_plantuml.transformer import Transformer
            transformer = Transformer()
            transformer.transform(
                model_file=model_file,
                config_file=config_path,
                output_file=transformed_model_file,
            )
            print(f"Transformed model saved to: {transformed_model_file}")
            
        elif workflow == "transform_generate":
            # Step 1: Transform (requires existing model.json)
            if not os.path.exists(model_file):
                print(f"Error: Model file not found: {model_file}")
                print("Please run parsing step first or ensure model.json exists.")
                return 1
            
            print("Step 1: Transforming...")
            from c_to_plantuml.transformer import Transformer
            transformer = Transformer()
            transformer.transform(
                model_file=model_file,
                config_file=config_path,
                output_file=transformed_model_file,
            )
            print(f"Transformed model saved to: {transformed_model_file}")
            
            # Step 2: Generate
            print("Step 2: Generating PlantUML...")
            from c_to_plantuml.generator import Generator
            generator = Generator()
            generator.generate(
                model_file=transformed_model_file,
                output_dir=output_dir,
                include_depth=config_data.get("include_depth", 1),
            )
            print(f"PlantUML generation complete! Output in: {output_dir}")
        
        print("Custom workflow completed successfully!")
        return 0
        
    except Exception as e:
        logging.error(f"Custom workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


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
    python debug.py --interactive      # Interactive mode to select workflow and config
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
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode to select workflow and configuration"
    )
    
    args = parser.parse_args()
    
    # Handle interactive mode
    if args.interactive:
        return interactive_mode()
    
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
    
    return execute_standard_workflow(args.command, config_path, args.verbose)


if __name__ == "__main__":
    sys.exit(main())