#!/usr/bin/env python3
"""
Main entry point for C to PlantUML converter with JSON model approach
"""

import os
import sys
import argparse
import json
import shutil
from pathlib import Path

from .project_analyzer import ProjectAnalyzer, load_config_and_analyze
from .generators.plantuml_generator import generate_plantuml_from_json

def main():
    """Main entry point for the C to PlantUML converter"""
    parser = argparse.ArgumentParser(
        description="Convert C/C++ projects to PlantUML diagrams using enhanced parsing and JSON models"
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='test_config.json',
        help='Configuration file path (default: test_config.json)'
    )
    
    parser.add_argument(
        '--analyze-only', '-a',
        action='store_true',
        help='Only perform analysis and save JSON model, skip PlantUML generation'
    )
    
    parser.add_argument(
        '--generate-only', '-g',
        type=str,
        metavar='JSON_MODEL',
        help='Generate PlantUML from existing JSON model file'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        help='Output directory for PlantUML files (overrides config)'
    )
    
    parser.add_argument(
        '--clean', 
        action='store_true',
        help='Clean output directories before generation'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"C to PlantUML Converter")
        print(f"Configuration: {args.config}")
    
    try:
        if args.generate_only:
            # Generate PlantUML from existing JSON model
            if not os.path.exists(args.generate_only):
                print(f"Error: JSON model file not found: {args.generate_only}")
                sys.exit(1)
            
            output_dir = args.output_dir or './output_uml'
            
            if args.clean and os.path.exists(output_dir):
                shutil.rmtree(output_dir)
                if args.verbose:
                    print(f"Cleaned output directory: {output_dir}")
            
            print(f"Generating PlantUML from JSON model: {args.generate_only}")
            generate_plantuml_from_json(args.generate_only, output_dir)
            
        else:
            # Full workflow: analyze and optionally generate
            if not os.path.exists(args.config):
                print(f"Error: Configuration file not found: {args.config}")
                sys.exit(1)
            
            # Load configuration
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Clean model output if requested
            model_output_path = config.get('model_output_path', './project_model.json')
            if args.clean and os.path.exists(model_output_path):
                os.remove(model_output_path)
                if args.verbose:
                    print(f"Cleaned model file: {model_output_path}")
            
            # Analyze project and create JSON model
            print("Starting project analysis...")
            model = load_config_and_analyze(args.config)
            
            if args.analyze_only:
                print("Analysis complete. JSON model saved.")
                print(f"Model location: {model_output_path}")
                return
            
            # Generate PlantUML from the created model
            output_dir = args.output_dir or config.get('output_dir', './output_uml')
            
            if args.clean and os.path.exists(output_dir):
                shutil.rmtree(output_dir)
                if args.verbose:
                    print(f"Cleaned PlantUML output directory: {output_dir}")
            
            print("Generating PlantUML diagrams...")
            generate_plantuml_from_json(model_output_path, output_dir)
            
            # Also run packager if configured
            if 'output_dir_packaged' in config:
                output_dir_packaged = config['output_dir_packaged']
                
                if args.clean and os.path.exists(output_dir_packaged):
                    shutil.rmtree(output_dir_packaged)
                    if args.verbose:
                        print(f"Cleaned packaged output directory: {output_dir_packaged}")
                
                print("Running packager...")
                from packager.packager import package_puml_files
                package_puml_files(output_dir, output_dir_packaged, config.get('project_roots', []))
        
        print("Process completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def analyze_project_cli():
    """CLI entry point for project analysis only"""
    parser = argparse.ArgumentParser(
        description="Analyze C/C++ project and create JSON model"
    )
    
    parser.add_argument(
        'project_roots',
        nargs='+',
        help='Project root directories to analyze'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='project_model.json',
        help='Output JSON model file (default: project_model.json)'
    )
    
    parser.add_argument(
        '--name', '-n',
        type=str,
        default='C_Project',
        help='Project name (default: C_Project)'
    )
    
    parser.add_argument(
        '--prefixes', '-p',
        nargs='*',
        help='C file prefixes to filter'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Disable recursive directory scanning'
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = ProjectAnalyzer()
        model = analyzer.analyze_and_save(
            project_roots=args.project_roots,
            output_path=args.output,
            project_name=args.name,
            c_file_prefixes=args.prefixes or [],
            recursive=not args.no_recursive
        )
        
        print(f"Analysis complete!")
        print(f"Files analyzed: {len(model.files)}")
        print(f"Model saved to: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def generate_plantuml_cli():
    """CLI entry point for PlantUML generation only"""
    parser = argparse.ArgumentParser(
        description="Generate PlantUML diagrams from JSON model"
    )
    
    parser.add_argument(
        'json_model',
        help='JSON model file path'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./output_uml',
        help='Output directory for PlantUML files (default: ./output_uml)'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean output directory before generation'
    )
    
    args = parser.parse_args()
    
    try:
        if not os.path.exists(args.json_model):
            print(f"Error: JSON model file not found: {args.json_model}")
            sys.exit(1)
        
        if args.clean and os.path.exists(args.output):
            shutil.rmtree(args.output)
            print(f"Cleaned output directory: {args.output}")
        
        generate_plantuml_from_json(args.json_model, args.output)
        print("PlantUML generation complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 