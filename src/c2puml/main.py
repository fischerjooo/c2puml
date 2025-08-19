#!/usr/bin/env python3
"""
Main entry point for C to PlantUML converter

Processing Flow:
1. Parse C/C++ files and generate model.json
2. Transform model based on configuration
3. Generate PlantUML files from the transformed model
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from .config import Config
from .core.generator import Generator
from .core.parser import Parser
from .core.transformer import Transformer


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def load_config_from_path(config_path: str) -> dict:
    path = Path(config_path)
    if path.is_file():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif path.is_dir():
        # Merge all .json files in the folder
        config = {}
        for file in path.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                config.update(data)
        return config
    else:
        raise FileNotFoundError(f"Config path not found: {config_path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="C to PlantUML Converter (Simplified CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage:
  %(prog)s --config config.json [parse|transform|generate]
  %(prog)s config_folder [parse|transform|generate]
  %(prog)s [parse|transform|generate]  # Uses current directory as config folder
  %(prog)s              # Full workflow (parse, transform, generate)
        """,
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=None,
        help="Path to config.json or config folder (optional, default: current directory)",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["parse", "transform", "generate"],
        help="Which step to run: parse, transform, or generate. If omitted, runs full workflow.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()

    setup_logging(args.verbose)

    # Determine config path
    config_path = args.config
    if config_path is None:
        config_path = os.getcwd()

    logging.info("Using config: %s", config_path)

    # Load config
    try:
        config_data = load_config_from_path(config_path)
        config = Config(**config_data)
    except Exception as e:
        logging.error("Failed to load configuration: %s", e)
        return 1

    # Determine output folder from config, default to ./output
    output_folder = getattr(config, "output_dir", None) or os.path.join(
        os.getcwd(), "output"
    )
    output_folder = os.path.abspath(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    logging.info("Output folder: %s", output_folder)

    model_file = os.path.join(output_folder, "model.json")
    transformed_model_file = os.path.join(output_folder, "model_transformed.json")

    # Parse command
    if args.command == "parse":
        try:
            parser_obj = Parser()
            # Use the parse function with multiple source folders
            parser_obj.parse(
                source_folders=config.source_folders,
                output_file=model_file,
                recursive_search=getattr(config, "recursive_search", True),
                config=config,
            )
            logging.info("Model saved to: %s", model_file)
            return 0
        except (OSError, ValueError, RuntimeError) as e:
            logging.error("Error during parsing: %s", e)
            # Provide additional context for common issues
            if "Source folder not found" in str(e):
                logging.error("Please check that the source_folders in your configuration exist and are accessible.")
                logging.error("You can use absolute paths or relative paths from the current working directory.")
            elif "Permission denied" in str(e):
                logging.error("Please check file permissions for the source folders.")
            elif "Invalid JSON" in str(e):
                logging.error("Please check that your configuration file contains valid JSON.")
            return 1

    # Transform command
    if args.command == "transform":
        try:
            transformer = Transformer()
            transformer.transform(
                model_file=model_file,
                config_file=(
                    config_path
                    if Path(config_path).is_file()
                    else str(list(Path(config_path).glob("*.json"))[0])
                ),
                output_file=transformed_model_file,
            )
            logging.info("Transformed model saved to: %s", transformed_model_file)
            return 0
        except (OSError, ValueError, RuntimeError) as e:
            logging.error("Error during transformation: %s", e)
            return 1

    # Generate command
    if args.command == "generate":
        try:
            generator = Generator()
            # Apply config for signature truncation and macro display
            Generator.max_function_signature_chars = getattr(config, "max_function_signature_chars", 0)
            Generator.hide_macro_values = getattr(config, "hide_macro_values", False)
            Generator.convert_empty_class_to_artifact = getattr(config, "convert_empty_class_to_artifact", False)
            # Prefer transformed model, else fallback to model.json
            if os.path.exists(transformed_model_file):
                model_to_use = transformed_model_file
            elif os.path.exists(model_file):
                model_to_use = model_file
            else:
                logging.error("No model file found for generation.")
                logging.error("Please run the parse step first to generate a model file.")
                return 1
            generator.generate(
                model_file=model_to_use,
                output_dir=output_folder,
            )
            logging.info("PlantUML generation complete! Output in: %s", output_folder)
            return 0
        except (OSError, ValueError, RuntimeError) as e:
            logging.error("Error generating PlantUML: %s", e)
            return 1

    # Default: full workflow
    try:
        # Step 1: Parse
        parser_obj = Parser()
        # Use the parse function with multiple source folders
        parser_obj.parse(
            source_folders=config.source_folders,
            output_file=model_file,
            recursive_search=getattr(config, "recursive_search", True),
            config=config,
        )
        logging.info("Model saved to: %s", model_file)
        # Step 2: Transform
        transformer = Transformer()
        transformer.transform(
            model_file=model_file,
            config_file=(
                config_path
                if Path(config_path).is_file()
                else str(list(Path(config_path).glob("*.json"))[0])
            ),
            output_file=transformed_model_file,
        )
        logging.info("Transformed model saved to: %s", transformed_model_file)
        # Step 3: Generate
        generator = Generator()
        # Apply config for signature truncation and macro display
        Generator.max_function_signature_chars = getattr(config, "max_function_signature_chars", 0)
        Generator.hide_macro_values = getattr(config, "hide_macro_values", False)
        Generator.convert_empty_class_to_artifact = getattr(config, "convert_empty_class_to_artifact", False)
        generator.generate(
            model_file=transformed_model_file,
            output_dir=output_folder,
        )
        logging.info("PlantUML generation complete! Output in: %s", output_folder)
        logging.info("Complete workflow finished successfully!")
        return 0
    except (OSError, ValueError, RuntimeError) as e:
        logging.error("Error in workflow: %s", e)
        # Provide additional context for common issues
        if "Source folder not found" in str(e):
            logging.error("Please check that the source_folders in your configuration exist and are accessible.")
            logging.error("You can use absolute paths or relative paths from the current working directory.")
        elif "Permission denied" in str(e):
            logging.error("Please check file permissions for the source folders.")
        elif "Invalid JSON" in str(e):
            logging.error("Please check that your configuration file contains valid JSON.")
        elif "Configuration must contain" in str(e):
            logging.error("Please check that your configuration file has the required 'source_folders' field.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
