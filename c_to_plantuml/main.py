#!/usr/bin/env python3
"""
Main entry point for C to PlantUML converter with JSON model approach
"""

import argparse
import sys
import os
import json
from .project_analyzer import ProjectAnalyzer, load_config_and_analyze
from .generators.plantuml_generator import generate_plantuml_from_json
from .models.project_model import ProjectModel

def create_analyze_parser(subparsers):
    """Create the analyze subcommand parser"""
    analyze_parser = subparsers.add_parser(
        'analyze', 
        help='Analyze C code and create JSON model'
    )
    analyze_parser.add_argument(
        'project_roots', 
        nargs='+', 
        help='Root directories of C projects to analyze'
    )
    analyze_parser.add_argument(
        '-o', '--output', 
        default='./project_model.json',
        help='Output path for JSON model (default: ./project_model.json)'
    )
    analyze_parser.add_argument(
        '-n', '--name', 
        default='C_Project',
        help='Project name (default: C_Project)'
    )
    analyze_parser.add_argument(
        '-p', '--prefixes', 
        nargs='*',
        help='C file prefixes to include (e.g., main_ test_)'
    )
    analyze_parser.add_argument(
        '--no-recursive', 
        action='store_true',
        help='Disable recursive directory search'
    )
    return analyze_parser

def create_generate_parser(subparsers):
    """Create the generate subcommand parser"""
    generate_parser = subparsers.add_parser(
        'generate', 
        help='Generate PlantUML diagrams from JSON model'
    )
    generate_parser.add_argument(
        'model_json', 
        help='Path to JSON model file'
    )
    generate_parser.add_argument(
        '-o', '--output-dir', 
        default='./plantuml_output',
        help='Output directory for PlantUML files (default: ./plantuml_output)'
    )
    return generate_parser

def create_config_parser(subparsers):
    """Create the config subcommand parser"""
    config_parser = subparsers.add_parser(
        'config', 
        help='Run analysis using configuration file'
    )
    config_parser.add_argument(
        'config_file', 
        help='Path to JSON configuration file'
    )
    return config_parser

def create_filter_parser(subparsers):
    """Create the filter subcommand parser"""
    filter_parser = subparsers.add_parser(
        'filter', 
        help='Apply filtering and transformations to existing JSON model'
    )
    filter_parser.add_argument(
        'model_file', 
        help='Existing JSON model file to transform'
    )
    filter_parser.add_argument(
        'config_files', 
        nargs='+',
        help='JSON configuration file(s) with transformation settings'
    )
    filter_parser.add_argument(
        '-o', '--output', 
        help='Output path for transformed model (default: overwrites input)'
    )
    return filter_parser

def create_full_parser(subparsers):
    """Create the full workflow subcommand parser"""
    full_parser = subparsers.add_parser(
        'full', 
        help='Complete workflow: analyze and generate PlantUML'
    )
    full_parser.add_argument(
        'project_roots', 
        nargs='+', 
        help='Root directories of C projects to analyze'
    )
    full_parser.add_argument(
        '-o', '--output-dir', 
        default='./c2plantuml_output',
        help='Output directory (default: ./c2plantuml_output)'
    )
    full_parser.add_argument(
        '-n', '--name', 
        default='C_Project',
        help='Project name (default: C_Project)'
    )
    full_parser.add_argument(
        '-p', '--prefixes', 
        nargs='*',
        help='C file prefixes to include'
    )
    full_parser.add_argument(
        '--no-recursive', 
        action='store_true',
        help='Disable recursive directory search'
    )
    full_parser.add_argument(
        '--keep-json', 
        action='store_true',
        help='Keep the intermediate JSON model file'
    )
    return full_parser

def handle_analyze_command(args):
    """Handle the analyze subcommand"""
    print(f"Analyzing C project(s): {', '.join(args.project_roots)}")
    
    analyzer = ProjectAnalyzer()
    model = analyzer.analyze_and_save(
        project_roots=args.project_roots,
        output_path=args.output,
        project_name=args.name,
        c_file_prefixes=args.prefixes,
        recursive=not args.no_recursive
    )
    
    print(f"Analysis complete! JSON model saved to: {args.output}")
    print(f"Analyzed {len(model.files)} C files")
    return 0

def handle_generate_command(args):
    """Handle the generate subcommand"""
    print(f"Generating PlantUML diagrams from: {args.model_json}")
    
    if not os.path.exists(args.model_json):
        print(f"Error: Model file not found: {args.model_json}")
        return 1
    
    try:
        generate_plantuml_from_json(args.model_json, args.output_dir)
        print(f"PlantUML generation complete! Output in: {args.output_dir}")
        return 0
    except Exception as e:
        print(f"Error generating PlantUML: {e}")
        return 1

def handle_config_command(args):
    """Handle the config subcommand"""
    print(f"Running analysis using config: {args.config_file}")
    
    if not os.path.exists(args.config_file):
        print(f"Error: Config file not found: {args.config_file}")
        return 1
    
    try:
        model = load_config_and_analyze(args.config_file)
        print(f"Config-based analysis complete!")
        print(f"Analyzed {len(model.files)} C files")
        return 0
    except Exception as e:
        print(f"Error in config-based analysis: {e}")
        return 1

def handle_filter_command(args):
    """Handle the filter subcommand"""
    print(f"Transforming model: {args.model_file}")
    print(f"Using transformation configs: {', '.join(args.config_files)}")
    
    if not os.path.exists(args.model_file):
        print(f"Error: Model file not found: {args.model_file}")
        return 1
    
    # Check all config files exist
    for config_file in args.config_files:
        if not os.path.exists(config_file):
            print(f"Error: Config file not found: {config_file}")
            return 1
    
    try:
        from .models.project_model import ProjectModel
        from .manipulators.model_transformer import ModelTransformer
        
        # Load existing model
        model = ProjectModel.load_from_json(args.model_file)
        print(f"Loaded model with {len(model.files)} files")
        
        # Load and apply transformations
        model_transformer = ModelTransformer()
        if len(args.config_files) == 1:
            model_transformer.load_config(args.config_files[0])
        else:
            model_transformer.load_multiple_configs(args.config_files)
        
        transformed_model = model_transformer.apply_all_filters(model)
        
        # Save transformed model
        output_path = args.output or args.model_file
        transformed_model.save_to_json(output_path)
        
        print(f"Transformed model saved to: {output_path}")
        print(f"Transformed model contains {len(transformed_model.files)} files")
        
        return 0
    except Exception as e:
        print(f"Error transforming model: {e}")
        return 1

def handle_full_command(args):
    """Handle the full workflow subcommand"""
    print(f"Running complete workflow for: {', '.join(args.project_roots)}")
    
    # Step 1: Analysis
    model_path = os.path.join(args.output_dir, f"{args.name}_model.json")
    
    analyzer = ProjectAnalyzer()
    model = analyzer.analyze_and_save(
        project_roots=args.project_roots,
        output_path=model_path,
        project_name=args.name,
        c_file_prefixes=args.prefixes,
        recursive=not args.no_recursive
    )
    
    print(f"Analysis complete! Analyzed {len(model.files)} C files")
    
    # Step 2: PlantUML Generation
    try:
        generate_plantuml_from_json(model_path, args.output_dir)
        print(f"PlantUML generation complete!")
    except Exception as e:
        print(f"Error generating PlantUML: {e}")
        return 1
    
    # Step 3: Cleanup (if requested)
    if not args.keep_json:
        try:
            os.remove(model_path)
            print(f"Cleaned up intermediate JSON file")
        except OSError:
            print(f"Warning: Could not remove {model_path}")
    
    print(f"Complete workflow finished! Output in: {args.output_dir}")
    return 0

def main():
    """Main entry point for the C to PlantUML converter"""
    
    parser = argparse.ArgumentParser(
        description='Convert C code to PlantUML diagrams',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze C code and create JSON model
  c2plantuml analyze /path/to/project -o project.json -n MyProject
  
  # Generate PlantUML from existing JSON model
  c2plantuml generate project.json -o plantuml_diagrams/
  
  # Complete workflow: analyze and generate
  c2plantuml full /path/to/project -o output/ -n MyProject
  
  # Use configuration file
  c2plantuml config my_config.json
  
  # Transform existing JSON model with single config
  c2plantuml filter project.json transform_config.json -o transformed_project.json
  
  # Transform with multiple config files
  c2plantuml filter project.json filters.json transformations.json additions.json -o result.json
  
  # Filter files by prefix
  c2plantuml analyze /project -p main_ test_ -o filtered.json
        """)
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create subcommand parsers
    create_analyze_parser(subparsers)
    create_generate_parser(subparsers)
    create_config_parser(subparsers)
    create_filter_parser(subparsers)
    create_full_parser(subparsers)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate handler
    try:
        if args.command == 'analyze':
            return handle_analyze_command(args)
        elif args.command == 'generate':
            return handle_generate_command(args)
        elif args.command == 'config':
            return handle_config_command(args)
        elif args.command == 'filter':
            return handle_filter_command(args)
        elif args.command == 'full':
            return handle_full_command(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

def c2plantuml_analyze():
    """Entry point for c2plantuml-analyze command"""
    parser = create_analyze_parser(argparse.ArgumentParser())
    args = parser.parse_args()
    return handle_analyze_command(args)

def c2plantuml_generate():
    """Entry point for c2plantuml-generate command"""
    parser = create_generate_parser(argparse.ArgumentParser())
    args = parser.parse_args()
    return handle_generate_command(args)

if __name__ == '__main__':
    sys.exit(main()) 