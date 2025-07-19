#!/usr/bin/env python3
"""
Central script to run all examples and generate their outputs.

This script processes each example in the examples directory and generates
PlantUML diagrams for demonstration purposes.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to the path to import c_to_plantuml
sys.path.insert(0, str(Path(__file__).parent.parent))

from c_to_plantuml import main as c_to_plantuml_main


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def get_example_directories() -> List[Path]:
    """Get all example directories"""
    examples_dir = Path(__file__).parent
    return [d for d in examples_dir.iterdir() if d.is_dir() and d.name != '__pycache__']


def run_example(example_dir: Path, verbose: bool = False) -> bool:
    """Run a single example"""
    logger = logging.getLogger(__name__)
    
    example_name = example_dir.name
    logger.info(f"Processing example: {example_name}")
    
    # Check if example has required files
    config_file = example_dir / "config.json"
    input_dir = example_dir / "input"
    expected_output_dir = example_dir / "expected_output"
    
    if not config_file.exists():
        logger.warning(f"Example {example_name} has no config.json file")
        return False
    
    if not input_dir.exists():
        logger.warning(f"Example {example_name} has no input directory")
        return False
    
    # Create output directory
    output_dir = example_dir / "generated_output"
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Run the complete workflow using config
        cmd = [
            sys.executable, "-m", "c_to_plantuml", "config", 
            str(config_file)
        ]
        
        if verbose:
            cmd.extend(["--verbose"])
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=example_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            logger.info(f"Example {example_name} completed successfully")
            
            # Check if output was generated
            if output_dir.exists() and any(output_dir.iterdir()):
                logger.info(f"Output generated in: {output_dir}")
                return True
            else:
                logger.warning(f"Example {example_name} completed but no output generated")
                return False
        else:
            logger.error(f"Example {example_name} failed with return code {result.returncode}")
            if result.stdout:
                logger.error(f"Stdout: {result.stdout}")
            if result.stderr:
                logger.error(f"Stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Example {example_name} timed out after 5 minutes")
        return False
    except Exception as e:
        logger.error(f"Error running example {example_name}: {e}")
        return False


def create_example_summary(examples: List[Dict[str, Any]]) -> str:
    """Create a summary of all examples"""
    summary = "# Examples Summary\n\n"
    summary += "This directory contains example use cases for the C to PlantUML converter.\n\n"
    
    summary += "## Available Examples\n\n"
    
    for example in examples:
        status = "✅" if example["success"] else "❌"
        summary += f"### {status} {example['name']}\n"
        summary += f"- **Description**: {example['description']}\n"
        summary += f"- **Input**: {example['input_files']} files\n"
        summary += f"- **Output**: {example['output_files']} files\n"
        summary += f"- **Configuration**: {example['config']}\n\n"
    
    summary += "## Running Examples\n\n"
    summary += "To run all examples:\n```bash\npython run_examples.py\n```\n\n"
    summary += "To run with verbose output:\n```bash\npython run_examples.py --verbose\n```\n\n"
    summary += "To run a specific example:\n```bash\npython run_examples.py --example <example_name>\n```\n\n"
    
    summary += "## Example Structure\n\n"
    summary += "Each example directory contains:\n"
    summary += "- `input/` - Source C/C++ files\n"
    summary += "- `config.json` - Configuration file\n"
    summary += "- `expected_output/` - Expected PlantUML output (for reference)\n"
    summary += "- `generated_output/` - Generated output (created by running the example)\n"
    summary += "- `README.md` - Example-specific documentation\n\n"
    
    return summary


def main() -> int:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run all examples')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--example', help='Run only the specified example')
    parser.add_argument('--summary', action='store_true', help='Generate summary only')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Get example directories
    example_dirs = get_example_directories()
    
    if not example_dirs:
        logger.warning("No example directories found")
        return 1
    
    logger.info(f"Found {len(example_dirs)} example directories")
    
    # Filter by specific example if requested
    if args.example:
        example_dirs = [d for d in example_dirs if d.name == args.example]
        if not example_dirs:
            logger.error(f"Example '{args.example}' not found")
            return 1
    
    # Collect example information
    examples = []
    successful_examples = 0
    
    for example_dir in example_dirs:
        example_name = example_dir.name
        
        # Get example information
        config_file = example_dir / "config.json"
        input_dir = example_dir / "input"
        expected_output_dir = example_dir / "expected_output"
        generated_output_dir = example_dir / "generated_output"
        
        input_files = len(list(input_dir.glob("*"))) if input_dir.exists() else 0
        output_files = len(list(generated_output_dir.glob("*.puml"))) if generated_output_dir.exists() else 0
        
        # Read README for description
        readme_file = example_dir / "README.md"
        description = "No description available"
        if readme_file.exists():
            with open(readme_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip().startswith('#') and not line.strip().startswith('##'):
                        description = line.strip('#').strip()
                        break
        
        # Run example if not just generating summary
        success = False
        if not args.summary:
            success = run_example(example_dir, args.verbose)
            if success:
                successful_examples += 1
        
        examples.append({
            "name": example_name,
            "description": description,
            "input_files": input_files,
            "output_files": output_files,
            "config": "config.json" if config_file.exists() else "None",
            "success": success
        })
    
    # Generate summary
    summary_content = create_example_summary(examples)
    summary_file = Path(__file__).parent / "SUMMARY.md"
    
    with open(summary_file, 'w') as f:
        f.write(summary_content)
    
    logger.info(f"Summary written to: {summary_file}")
    
    if not args.summary:
        logger.info(f"Examples completed: {successful_examples}/{len(examples)} successful")
        
        if successful_examples == len(examples):
            logger.info("All examples completed successfully!")
            return 0
        else:
            logger.warning(f"{len(examples) - successful_examples} examples failed")
            return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())