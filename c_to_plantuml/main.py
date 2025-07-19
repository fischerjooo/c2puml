#!/usr/bin/env python3
"""
Main entry point for C to PlantUML converter

Processing Flow:
1. Parse C/C++ files and generate model
2. Apply configuration/transformers to the model
3. Generate PlantUML files from the transformed model
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from typing import Optional
try:
    from .analyzer import Analyzer
    from .generator import Generator
    from .config import Config
except ImportError:
    # Handle case when running as script directly
    import sys
    from pathlib import Path
    
    # Add the parent directory to the path so we can import the package
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    
    # Now import from the package
    from c_to_plantuml.analyzer import Analyzer
    from c_to_plantuml.generator import Generator
    from c_to_plantuml.config import Config


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        description='Convert C/C++ code to PlantUML diagrams',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Processing Flow:
1. Parse C/C++ files and generate model
2. Apply configuration/transformers to the model  
3. Generate PlantUML files from the transformed model

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
    
    # Analyze command - Step 1: Parse and generate model
    analyze_parser = subparsers.add_parser('analyze', help='Step 1: Analyze C/C++ project and generate model')
    analyze_parser.add_argument('project_root', help='Root directory of C/C++ project')
    analyze_parser.add_argument('-o', '--output', default='project_model.json',
                               help='Output JSON model file (default: project_model.json)')
    analyze_parser.add_argument('--recursive', action='store_true', default=True,
                               help='Search subdirectories recursively (default: True)')
    analyze_parser.add_argument('--no-recursive', dest='recursive', action='store_false',
                               help='Disable recursive search')
    
    # Generate command - Step 3: Generate PlantUML from model
    generate_parser = subparsers.add_parser('generate', help='Step 3: Generate PlantUML from JSON model')
    generate_parser.add_argument('model_file', help='JSON model file')
    generate_parser.add_argument('-o', '--output-dir', default='./plantuml_output',
                                help='Output directory for PlantUML files (default: ./plantuml_output)')
    
    # Config command - Complete workflow (Steps 1-3)
    config_parser = subparsers.add_parser('config', help='Complete workflow: Analyze, transform, and generate using configuration')
    config_parser.add_argument('config_file', help='Configuration JSON file')
    
    return parser


def validate_project_root(project_root: str) -> bool:
    """Validate that project root exists and is accessible"""
    if not os.path.exists(project_root):
        logging.error(f"Project root not found: {project_root}")
        return False
    return True


def validate_model_file(model_file: str) -> bool:
    """Validate that model file exists and is accessible"""
    if not os.path.exists(model_file):
        logging.error(f"Model file not found: {model_file}")
        return False
    return True


def validate_config_file(config_file: str) -> bool:
    """Validate that config file exists and is accessible"""
    if not os.path.exists(config_file):
        logging.error(f"Config file not found: {config_file}")
        return False
    return True


def print_analysis_summary(model) -> None:
    """Print summary of analysis results"""
    total_structs = sum(len(f.structs) for f in model.files.values())
    total_enums = sum(len(f.enums) for f in model.files.values())
    total_functions = sum(len(f.functions) for f in model.files.values())
    total_unions = sum(len(f.unions) for f in model.files.values())
    total_typedefs = sum(len(f.typedefs) for f in model.files.values())
    
    logging.info(f"Analysis Summary:")
    logging.info(f"  Files processed: {len(model.files)}")
    logging.info(f"  Structs found: {total_structs}")
    logging.info(f"  Enums found: {total_enums}")
    logging.info(f"  Unions found: {total_unions}")
    logging.info(f"  Functions found: {total_functions}")
    logging.info(f"  Typedefs found: {total_typedefs}")


def handle_analyze_command(args: argparse.Namespace) -> int:
    """Handle analyze command - Step 1: Parse C files and generate model"""
    logger = logging.getLogger(__name__)
    
    # Handle both project_root and project_roots attributes for compatibility
    project_root = getattr(args, 'project_root', None)
    if project_root is None:
        project_roots = getattr(args, 'project_roots', None)
        if project_roots is not None and isinstance(project_roots, list) and len(project_roots) > 0:
            project_root = project_roots[0]
        else:
            logger.error("Neither project_root nor project_roots found in arguments")
            return 1
    
    if not validate_project_root(project_root):
        return 1
    
    logger.info(f"Step 1: Analyzing C/C++ project: {project_root}")
    
    try:
        analyzer = Analyzer()
        model = analyzer.analyze_project(
            project_root=project_root,
            recursive=args.recursive
        )
        
        # Save model
        model.save(args.output)
        logger.info(f"Step 1 complete! Model saved to: {args.output}")
        
        # Print summary
        print_analysis_summary(model)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=args.verbose)
        return 1


def handle_generate_command(args: argparse.Namespace) -> int:
    """Handle generate command - Step 3: Generate PlantUML from model"""
    logger = logging.getLogger(__name__)
    
    if not validate_model_file(args.model_file):
        return 1
    
    logger.info(f"Step 3: Generating PlantUML diagrams from: {args.model_file}")
    
    try:
        generator = Generator()
        generator.generate_from_model(args.model_file, args.output_dir)
        logger.info(f"Step 3 complete! PlantUML generation complete! Output in: {args.output_dir}")
        return 0
        
    except Exception as e:
        logger.error(f"Error generating PlantUML: {e}", exc_info=args.verbose)
        return 1


def handle_config_command(args: argparse.Namespace) -> int:
    """Handle config command - Complete workflow (Steps 1-3)"""
    logger = logging.getLogger(__name__)
    
    if not validate_config_file(args.config_file):
        return 1
    
    logger.info(f"Running complete workflow with configuration: {args.config_file}")
    
    try:
        config = Config.load(args.config_file)
        analyzer = Analyzer()
        generator = Generator()
        
        # Step 1: Analyze project and generate model
        logger.info("Step 1: Starting project analysis...")
        model = analyzer.analyze_with_config(config)
        
        # Save model to file
        model_filename = config.model_output_path
        model.save(model_filename)
        logger.info(f"Step 1 complete! Model saved to: {model_filename}")
        
        # Print analysis summary
        print_analysis_summary(model)
        
        # Step 2: Apply configuration/transformers (handled in analyze_with_config)
        logger.info("Step 2: Configuration/transformers applied during analysis")
        
        # Step 3: Generate diagrams
        logger.info("Step 3: Starting PlantUML generation...")
        generator.generate_with_config(model, config)
        
        logger.info("Complete workflow finished successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error in configuration-based workflow: {e}", exc_info=args.verbose)
        return 1


def main() -> int:
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle commands
    if args.command == 'analyze':
        return handle_analyze_command(args)
    elif args.command == 'generate':
        return handle_generate_command(args)
    elif args.command == 'config':
        return handle_config_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main()) 