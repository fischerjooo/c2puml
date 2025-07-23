#!/usr/bin/env python3
"""
Main entry point for C to PlantUML converter

Processing Flow:
1. Parse C/C++ files and generate model.json
2. Transform model based on configuration
3. Generate PlantUML files from the transformed model
"""

import argparse
import logging
import os
import sys
import json
from pathlib import Path

from .generator import Generator
from .parser import Parser
from .transformer import Transformer
from .config import Config


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
        "--config", "-c", type=str, default=None, help="Path to config.json or config folder (optional, default: current directory)"
    )
    parser.add_argument(
        "command", nargs="?", choices=["parse", "transform", "generate"], help="Which step to run: parse, transform, or generate. If omitted, runs full workflow."
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

    logging.info(f"Using config: {config_path}")

    # Load config
    try:
        config_data = load_config_from_path(config_path)
        config = Config(**config_data)
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return 1

    # Determine output folder from config, default to ./output
    output_folder = getattr(config, "output_dir", None) or os.path.join(os.getcwd(), "output")
    output_folder = os.path.abspath(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    logging.info(f"Output folder: {output_folder}")

    model_file = os.path.join(output_folder, "model.json")
    transformed_model_file = os.path.join(output_folder, "model_transformed.json")

    # Parse command
    if args.command == "parse":
        try:
            parser_obj = Parser()
            parser_obj.parse(
                project_root=config.source_folders[0],
                output_file=model_file,
                recursive_search=getattr(config, "recursive_search", True),
                config=config,
            )
            logging.info(f"Model saved to: {model_file}")
            return 0
        except Exception as e:
            logging.error(f"Error during parsing: {e}")
            return 1

    # Transform command
    if args.command == "transform":
        try:
            transformer = Transformer()
            transformer.transform(
                model_file=model_file,
                config_file=config_path if Path(config_path).is_file() else str(list(Path(config_path).glob("*.json"))[0]),
                output_file=transformed_model_file,
            )
            logging.info(f"Transformed model saved to: {transformed_model_file}")
            return 0
        except Exception as e:
            logging.error(f"Error during transformation: {e}")
            return 1

            # Generate command
        if args.command == "generate":
            try:
                generator = Generator()
                # Prefer transformed model, else fallback to model.json
                if os.path.exists(transformed_model_file):
                    model_to_use = transformed_model_file
                elif os.path.exists(model_file):
                    model_to_use = model_file
                else:
                    logging.error("No model file found for generation.")
                    return 1
                generator.generate(
                    model_file=model_to_use,
                    output_dir=output_folder,
                    include_depth=getattr(config, "include_depth", 1),
                )
                logging.info(f"PlantUML generation complete! Output in: {output_folder}")
                return 0
            except Exception as e:
                logging.error(f"Error generating PlantUML: {e}")
                return 1

    # Default: full workflow
    try:
        # Step 1: Parse
        parser_obj = Parser()
        parser_obj.parse(
            project_root=config.source_folders[0],
            output_file=model_file,
            recursive_search=getattr(config, "recursive_search", True),
            config=config,
        )
        logging.info(f"Model saved to: {model_file}")
        # Step 2: Transform
        transformer = Transformer()
        transformer.transform(
            model_file=model_file,
            config_file=config_path if Path(config_path).is_file() else str(list(Path(config_path).glob("*.json"))[0]),
            output_file=transformed_model_file,
        )
        logging.info(f"Transformed model saved to: {transformed_model_file}")
        # Step 3: Generate
        generator = Generator()
        generator.generate(
            model_file=transformed_model_file,
            output_dir=output_folder,
            include_depth=getattr(config, "include_depth", 1),
        )
        logging.info(f"PlantUML generation complete! Output in: {output_folder}")
        logging.info("Complete workflow finished successfully!")
        return 0
    except Exception as e:
        logging.error(f"Error in workflow: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
