#!/usr/bin/env python3
"""
Main entry point for C to PlantUML converter

Processing Flow:
1. Parse C/C++ files and generate model.json
2. Transform model based on configuration
3. Generate PlantUML files from the transformed model
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from typing import Optional
from .parser import Parser
from .transformer import Transformer
from .generator import Generator


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        description='Convert C/C++ code to PlantUML diagrams',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Processing Flow:
1. Parse C/C++ files and generate model.json
2. Transform model based on configuration  
3. Generate PlantUML files from the transformed model

Examples:
  %(prog)s parse ./src
  %(prog)s transform model.json config.json
  %(prog)s generate model.json
  %(prog)s workflow ./src config.json
  %(prog)s parse ./src --verbose
        """
    )
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command - Step 1: Parse C files and generate model
    parse_parser = subparsers.add_parser('parse', help='Step 1: Parse C/C++ project and generate model.json')
    parse_parser.add_argument('project_root', help='Root directory of C/C++ project')
    parse_parser.add_argument('-o', '--output', default='model.json',
                             help='Output JSON model file (default: model.json)')
    parse_parser.add_argument('--recursive', action='store_true', default=True,
                             help='Search subdirectories recursively (default: True)')
    parse_parser.add_argument('--no-recursive', dest='recursive', action='store_false',
                             help='Disable recursive search')
    
    # Transform command - Step 2: Transform model based on configuration
    transform_parser = subparsers.add_parser('transform', help='Step 2: Transform model based on configuration')
    transform_parser.add_argument('model_file', help='Input JSON model file')
    transform_parser.add_argument('config_file', help='Configuration JSON file')
    transform_parser.add_argument('-o', '--output', help='Output transformed model file (default: overwrites input)')
    
    # Generate command - Step 3: Generate PlantUML from model
    generate_parser = subparsers.add_parser('generate', help='Step 3: Generate PlantUML from JSON model')
    generate_parser.add_argument('model_file', help='JSON model file')
    generate_parser.add_argument('-o', '--output-dir', default='./plantuml_output',
                                help='Output directory for PlantUML files (default: ./plantuml_output)')
    
    # Workflow command - Complete workflow (Steps 1-3)
    workflow_parser = subparsers.add_parser('workflow', help='Complete workflow: Parse, transform, and generate')
    workflow_parser.add_argument('project_root', help='Root directory of C/C++ project')
    workflow_parser.add_argument('config_file', help='Configuration JSON file')
    workflow_parser.add_argument('--recursive', action='store_true', default=True,
                                help='Search subdirectories recursively (default: True)')
    workflow_parser.add_argument('--no-recursive', dest='recursive', action='store_false',
                                help='Disable recursive search')
    
    return parser


def handle_parse_command(args: argparse.Namespace) -> int:
    """Handle parse command - Step 1: Parse C files and generate model.json"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Step 1: Parsing C/C++ project: {args.project_root}")
    
    if not os.path.exists(args.project_root):
        logger.error(f"Project root not found: {args.project_root}")
        return 1
    
    try:
        parser = Parser()
        output_file = parser.parse(
            project_root=args.project_root,
            output_file=args.output,
            recursive=args.recursive
        )
        
        logger.info(f"Step 1 complete! Model saved to: {output_file}")
        return 0
        
    except Exception as e:
        logger.error(f"Error during parsing: {e}", exc_info=getattr(args, 'verbose', False))
        return 1


def handle_transform_command(args: argparse.Namespace) -> int:
    """Handle transform command - Step 2: Transform model based on configuration"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Step 2: Transforming model: {args.model_file}")
    
    if not os.path.exists(args.model_file):
        logger.error(f"Model file not found: {args.model_file}")
        return 1
    
    if not os.path.exists(args.config_file):
        logger.error(f"Config file not found: {args.config_file}")
        return 1
    
    try:
        transformer = Transformer()
        output_file = transformer.transform(
            model_file=args.model_file,
            config_file=args.config_file,
            output_file=args.output
        )
        
        logger.info(f"Step 2 complete! Transformed model saved to: {output_file}")
        return 0
        
    except Exception as e:
        logger.error(f"Error during transformation: {e}", exc_info=getattr(args, 'verbose', False))
        return 1


def handle_generate_command(args: argparse.Namespace) -> int:
    """Handle generate command - Step 3: Generate PlantUML from model"""
    logger = logging.getLogger(__name__)
    
    logger.info(f"Step 3: Generating PlantUML diagrams from: {args.model_file}")
    
    if not os.path.exists(args.model_file):
        logger.error(f"Model file not found: {args.model_file}")
        return 1
    
    try:
        generator = Generator()
        output_dir = generator.generate(
            model_file=args.model_file,
            output_dir=args.output_dir
        )
        
        logger.info(f"Step 3 complete! PlantUML generation complete! Output in: {output_dir}")
        return 0
        
    except Exception as e:
        logger.error(f"Error generating PlantUML: {e}", exc_info=getattr(args, 'verbose', False))
        return 1


def handle_workflow_command(args: argparse.Namespace) -> int:
    """Handle workflow command - Complete workflow (Steps 1-3)"""
    logger = logging.getLogger(__name__)
    logger.info(f"Running complete workflow: {args.project_root} with {args.config_file}")
    
    if not os.path.exists(args.project_root):
        logger.error(f"Project root not found: {args.project_root}")
        return 1
    
    if not os.path.exists(args.config_file):
        logger.error(f"Config file not found: {args.config_file}")
        return 1
    
    try:
        # Step 1: Parse
        logger.info("Step 1: Starting project parsing...")
        parser = Parser()
        model_file = parser.parse(
            project_root=args.project_root,
            output_file="temp_model.json",
            recursive=args.recursive
        )
        logger.info(f"Step 1 complete! Model saved to: {model_file}")
        
        # Step 2: Transform
        logger.info("Step 2: Starting model transformation...")
        transformer = Transformer()
        transformed_model_file = transformer.transform(
            model_file=model_file,
            config_file=args.config_file,
            output_file="transformed_model.json"
        )
        logger.info(f"Step 2 complete! Transformed model saved to: {transformed_model_file}")
        
        # Step 3: Generate
        logger.info("Step 3: Starting PlantUML generation...")
        generator = Generator()
        output_dir = generator.generate(
            model_file=transformed_model_file,
            output_dir="./plantuml_output"
        )
        logger.info(f"Step 3 complete! PlantUML generation complete! Output in: {output_dir}")
        
        # Clean up temporary files
        try:
            os.remove(model_file)
            os.remove(transformed_model_file)
            logger.debug("Cleaned up temporary files")
        except:
            pass
        
        logger.info("Complete workflow finished successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error in workflow: {e}", exc_info=getattr(args, 'verbose', False))
        return 1


def main() -> int:
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(getattr(args, 'verbose', False))
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Handle commands
    command_handlers = {
        'parse': handle_parse_command,
        'transform': handle_transform_command,
        'generate': handle_generate_command,
        'workflow': handle_workflow_command
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        logging.error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 