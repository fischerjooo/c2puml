#!/usr/bin/env python3
"""
Main entry point for C to PlantUML converter
"""

import argparse
import sys
import os
from pathlib import Path
from .analyzer import Analyzer
from .generator import Generator
from .config import Config


def create_parser():
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        description='Convert C/C++ code to PlantUML diagrams',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze ./src
  %(prog)s generate project_model.json
  %(prog)s config config.json
        """
    )
    
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


def handle_analyze(args):
    """Handle analyze command"""
    print(f"Analyzing C/C++ project: {args.project_root}")
    
    if not os.path.exists(args.project_root):
        print(f"Error: Project root not found: {args.project_root}")
        return 1
    
    try:
        analyzer = Analyzer()
        model = analyzer.analyze_project(
            project_root=args.project_root,
            recursive=args.recursive
        )
        
        # Save model
        model.save(args.output)
        print(f"Analysis complete! Model saved to: {args.output}")
        print(f"Found {len(model.files)} files")
        return 0
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1


def handle_generate(args):
    """Handle generate command"""
    print(f"Generating PlantUML diagrams from: {args.model_file}")
    
    if not os.path.exists(args.model_file):
        print(f"Error: Model file not found: {args.model_file}")
        return 1
    
    try:
        generator = Generator()
        generator.generate_from_model(args.model_file, args.output_dir)
        print(f"PlantUML generation complete! Output in: {args.output_dir}")
        return 0
        
    except Exception as e:
        print(f"Error generating PlantUML: {e}")
        return 1


def handle_config(args):
    """Handle config command"""
    print(f"Running with configuration: {args.config_file}")
    
    if not os.path.exists(args.config_file):
        print(f"Error: Config file not found: {args.config_file}")
        return 1
    
    try:
        config = Config.load(args.config_file)
        analyzer = Analyzer()
        generator = Generator()
        
        # Analyze project
        model = analyzer.analyze_with_config(config)
        
        # Save model to file
        model_filename = f"{config.project_name}_model.json"
        model.save(model_filename)
        print(f"Model saved to: {model_filename}")
        
        # Generate diagrams
        generator.generate_with_config(model, config)
        
        print("Configuration-based analysis and generation complete!")
        return 0
        
    except Exception as e:
        print(f"Error in configuration-based workflow: {e}")
        return 1


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'analyze':
        return handle_analyze(args)
    elif args.command == 'generate':
        return handle_generate(args)
    elif args.command == 'config':
        return handle_config(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 