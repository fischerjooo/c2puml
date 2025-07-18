#!/usr/bin/env python3
"""
Main entry point for C to PlantUML converter
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from typing import Optional
from .analyzer import Analyzer
from .generator import Generator
from .config import Config


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
Examples:
  %(prog)s analyze ./src
  %(prog)s generate project_model.json
  %(prog)s config config.json
  %(prog)s analyze ./src --verbose
        """
    )
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze C/C++ project')
    analyze_parser.add_argument('project_root', help='Root directory of C/C++ project')
    analyze_parser.add_argument('-o', '--output', default='project_model.json',
                               help='Output JSON model file (default: project_model.json)')
    analyze_parser.add_argument('--recursive', action='store_true', default=True,
                               help='Search subdirectories recursively (default: True)')
    analyze_parser.add_argument('--no-recursive', dest='recursive', action='store_false',
                               help='Disable recursive search')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate PlantUML from JSON model')
    generate_parser.add_argument('model_file', help='JSON model file')
    generate_parser.add_argument('-o', '--output-dir', default='./plantuml_output',
                                help='Output directory for PlantUML files (default: ./plantuml_output)')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Run with configuration file')
    config_parser.add_argument('config_file', help='Configuration JSON file')
    
    return parser


def handle_analyze_command(args: argparse.Namespace) -> int:
    """Handle analyze command - kept for backward compatibility"""
    logger = logging.getLogger(__name__)
    
    # Handle both project_root and project_roots argument names for compatibility
    project_root = getattr(args, 'project_root', None) or getattr(args, 'project_roots', [None])[0]
    if not project_root:
        logger.error("No project root specified")
        return 1
    
    # Handle recursive argument with default
    recursive = getattr(args, 'recursive', True)
    if hasattr(args, 'no_recursive') and args.no_recursive:
        recursive = False
    
    logger.info(f"Analyzing C/C++ project: {project_root}")
    
    if not os.path.exists(project_root):
        logger.error(f"Project root not found: {project_root}")
        return 1
    
    try:
        analyzer = Analyzer()
        model = analyzer.analyze_project(
            project_root=project_root,
            recursive=recursive
        )
        
        # Save model
        model.save(args.output)
        logger.info(f"Analysis complete! Model saved to: {args.output}")
        logger.info(f"Found {len(model.files)} files")
        
        # Print summary
        total_structs = sum(len(f.structs) for f in model.files.values())
        total_enums = sum(len(f.enums) for f in model.files.values())
        total_functions = sum(len(f.functions) for f in model.files.values())
        logger.info(f"Summary: {total_structs} structs, {total_enums} enums, {total_functions} functions")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=getattr(args, 'verbose', False))
        return 1


def handle_generate_command(args: argparse.Namespace) -> int:
    """Handle generate command - kept for backward compatibility"""
    logger = logging.getLogger(__name__)
    
    # Handle both model_file and model_json argument names for compatibility
    model_file = getattr(args, 'model_file', None) or getattr(args, 'model_json', None)
    if not model_file:
        logger.error("No model file specified")
        return 1
    
    logger.info(f"Generating PlantUML diagrams from: {model_file}")
    
    if not os.path.exists(model_file):
        logger.error(f"Model file not found: {model_file}")
        return 1
    
    try:
        generator = Generator()
        generator.generate_from_model(model_file, args.output_dir)
        logger.info(f"PlantUML generation complete! Output in: {args.output_dir}")
        return 0
        
    except Exception as e:
        logger.error(f"Error generating PlantUML: {e}", exc_info=getattr(args, 'verbose', False))
        return 1


def handle_analyze(args: argparse.Namespace) -> int:
    """Handle analyze command"""
    return handle_analyze_command(args)


def handle_generate(args: argparse.Namespace) -> int:
    """Handle generate command"""
    return handle_generate_command(args)


def handle_config(args: argparse.Namespace) -> int:
    """Handle config command"""
    logger = logging.getLogger(__name__)
    logger.info(f"Running with configuration: {args.config_file}")
    
    if not os.path.exists(args.config_file):
        logger.error(f"Config file not found: {args.config_file}")
        return 1
    
    try:
        config = Config.load(args.config_file)
        analyzer = Analyzer()
        generator = Generator()
        
        # Analyze project
        logger.info("Starting project analysis...")
        model = analyzer.analyze_with_config(config)
        
        # Save model to file
        model_filename = f"{config.project_name}_model.json"
        model.save(model_filename)
        logger.info(f"Model saved to: {model_filename}")
        
        # Generate diagrams
        logger.info("Starting PlantUML generation...")
        generator.generate_with_config(model, config)
        
        logger.info("Configuration-based analysis and generation complete!")
        return 0
        
    except Exception as e:
        logger.error(f"Error in configuration-based workflow: {e}", exc_info=getattr(args, 'verbose', False))
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
        'analyze': handle_analyze,
        'generate': handle_generate,
        'config': handle_config
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        logging.error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 