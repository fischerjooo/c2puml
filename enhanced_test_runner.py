#!/usr/bin/env python3
"""
Enhanced Test Runner for C to PlantUML Converter
Consolidates GitHub workflow test logic into Python scripts
"""

import os
import sys
import subprocess
import tempfile
import json
import time
import argparse
import shutil
from pathlib import Path


class EnhancedTestRunner:
    """Enhanced test runner that consolidates GitHub workflow logic"""
    
    def __init__(self, verbose=True, output_dir="test_output"):
        self.verbose = verbose
        self.output_dir = output_dir
        self.test_results = []
        self.setup_output_dir()
        
    def setup_output_dir(self):
        """Create output directory for test artifacts"""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)
        
    def log(self, message):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(message)
            
    def run_command(self, cmd, description, check_returncode=True):
        """Run a command and return success status"""
        self.log(f"🔧 {description}")
        self.log(f"Command: {cmd}")
        self.log("=" * 60)
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.stdout:
                self.log("STDOUT:")
                self.log(result.stdout)
            if result.stderr:
                self.log("STDERR:")
                self.log(result.stderr)
            
            if check_returncode and result.returncode != 0:
                self.log("❌ FAILED")
                return False
            else:
                self.log("✅ PASSED")
                return True
                
        except subprocess.TimeoutExpired:
            self.log("❌ FAILED (timeout)")
            return False
        except Exception as e:
            self.log(f"❌ FAILED (error: {e})")
            return False
    
    def setup_environment(self):
        """Setup Python environment similar to GitHub workflow"""
        self.log("🔧 Setting up Python environment...")
        
        # Install package in development mode
        success = self.run_command("pip install -e .", "Install package in development mode")
        if not success:
            return False
            
        # Install additional requirements
        if os.path.exists("requirements.txt"):
            success = self.run_command("pip install -r requirements.txt", "Install requirements")
            if not success:
                return False
                
        # Show Python environment
        self.log("🐍 Python Environment Information:")
        self.run_command("python --version", "Python version", check_returncode=False)
        self.run_command("pip --version", "Pip version", check_returncode=False)
        self.run_command("pip list", "Installed packages", check_returncode=False)
        
        return True
    
    def run_linting_tests(self):
        """Run linting tests from GitHub workflow"""
        self.log("🔍 Running linting tests...")
        
        # Install flake8
        self.run_command("pip install flake8", "Install flake8", check_returncode=False)
        
        # Syntax error check
        success1 = self.run_command(
            "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
            "Syntax error check"
        )
        
        # Style check
        success2 = self.run_command(
            "flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics",
            "Style check"
        )
        
        return success1 and success2
    
    def discover_test_files(self):
        """Discover and list test files"""
        self.log("🔍 Discovering test files...")
        
        test_files = list(Path("tests").glob("test_*.py"))
        self.log(f"📊 Test file count: {len(test_files)}")
        self.log("📋 Available test modules:")
        
        for test_file in test_files:
            module_name = f"tests.{test_file.stem}"
            self.log(f"  - {module_name}")
            
        return test_files
    
    def run_unit_tests(self):
        """Run unit tests from GitHub workflow"""
        self.log("🧪 Running unit tests...")
        
        unit_tests = [
            ("tests.test_parser", "Parser Unit Tests"),
            ("tests.test_project_analyzer", "Project Analyzer Unit Tests"),
            ("tests.test_config_manipulations", "Configuration Manipulation Tests"),
            ("tests.test_config_integration", "Configuration Integration Tests"),
            ("tests.test_config_cli", "Configuration CLI Tests"),
        ]
        
        all_success = True
        for test_module, description in unit_tests:
            success = self.run_command(
                f"python -m unittest {test_module} -v --buffer",
                description
            )
            all_success = all_success and success
            
        return all_success
    
    def run_comprehensive_test_suite(self):
        """Run comprehensive test suite using run_tests.py"""
        self.log("🧪 Running comprehensive test suite...")
        return self.run_command("python run_tests.py", "Comprehensive test suite")
    
    def test_complete_workflow(self):
        """Test complete workflow with detailed logging"""
        self.log("🔄 Testing complete workflow...")
        
        self.log("📁 Current directory:")
        self.run_command("pwd", "Current directory", check_returncode=False)
        
        self.log("📋 Available config files:")
        self.run_command("ls -la *.json", "List config files", check_returncode=False)
        
        return self.run_command(
            "python -m c_to_plantuml.main config test_config.json",
            "Main workflow"
        )
    
    def verify_output_files(self):
        """Verify output files with detailed checks"""
        self.log("🔍 Verifying output files...")
        
        # Check model file
        if not os.path.exists("test_project_model.json"):
            self.log("❌ Error: test_project_model.json not created")
            self.run_command("ls -la *.json", "List JSON files", check_returncode=False)
            return False
        else:
            self.log("✅ test_project_model.json created successfully")
            file_size = os.path.getsize("test_project_model.json")
            self.log(f"📊 Model file size: {file_size} bytes")
        
        # Check PlantUML output directory
        if not os.path.exists("test_plantuml_output"):
            self.log("❌ Error: test_plantuml_output directory not created")
            self.run_command("ls -la", "List directory contents", check_returncode=False)
            return False
        else:
            self.log("✅ test_plantuml_output directory created successfully")
        
        # Check for .puml files
        self.log("📋 Contents of test_plantuml_output:")
        self.run_command("find test_plantuml_output -type f", "List PlantUML files", check_returncode=False)
        
        puml_count = len(list(Path("test_plantuml_output").glob("*.puml")))
        if puml_count == 0:
            self.log("❌ Error: No .puml files generated")
            self.run_command("ls -la test_plantuml_output/", "PlantUML directory contents", check_returncode=False)
            return False
        
        self.log(f"✅ Success: Found {puml_count} PlantUML files")
        self.run_command("find test_plantuml_output -name '*.puml' -exec wc -l {} \\;", "PlantUML file line counts", check_returncode=False)
        
        return True
    
    def test_cli_tools(self):
        """Test CLI tools with verbose output"""
        self.log("🛠️ Testing CLI tools...")
        
        # Test analysis CLI
        self.log("🔍 Testing analysis CLI...")
        analysis_cmd = """python -c "
import sys
sys.path.insert(0, '.')
from c_to_plantuml.main import handle_analyze_command, handle_generate_command
import argparse
import os

print('Setting up analysis test...')
args = argparse.Namespace()
args.project_roots = ['./tests/test_files']
args.output = 'test_model.json'
args.name = 'CLI_Test'
args.prefixes = None
args.no_recursive = False

print(f'Project roots: {args.project_roots}')
print(f'Output file: {args.output}')
print(f'Project name: {args.name}')

exit_code = handle_analyze_command(args)
print(f'Analysis exit code: {exit_code}')

if exit_code != 0:
    print('❌ Analysis CLI test failed')
    sys.exit(1)

print('✅ Analysis CLI test passed')

# Check if model file was created
if not os.path.exists('test_model.json'):
    print('❌ Error: CLI analysis failed to create model file')
    print('Current directory contents:')
    for f in os.listdir('.'):
        if f.endswith('.json'):
            print(f'  {f}')
    sys.exit(1)
else:
    print('✅ Model file created successfully')
    print(f'Model file size: {os.path.getsize(\"test_model.json\")} bytes')

# Test generation
print('🔍 Testing generation CLI...')
args = argparse.Namespace()
args.model_json = 'test_model.json'
args.output_dir = 'cli_output'

print(f'Model JSON: {args.model_json}')
print(f'Output directory: {args.output_dir}')

exit_code = handle_generate_command(args)
print(f'Generation exit code: {exit_code}')

if exit_code != 0:
    print('❌ Generation CLI test failed')
    sys.exit(1)

print('✅ Generation CLI test passed')

# Check if output directory was created
if not os.path.exists('cli_output'):
    print('❌ Error: CLI PlantUML generation failed')
    sys.exit(1)
else:
    print('✅ CLI output directory created successfully')
    print('CLI output contents:')
    for root, dirs, files in os.walk('cli_output'):
        for file in files:
            print(f'  {os.path.join(root, file)}')
"
"""
        
        return self.run_command(analysis_cmd, "CLI tools test")
    
    def run_performance_benchmark(self):
        """Run performance benchmark with detailed metrics"""
        self.log("⚡ Running performance benchmark...")
        
        perf_cmd = """python -c "
import time
import sys
import os
sys.path.insert(0, '.')
from c_to_plantuml.project_analyzer import ProjectAnalyzer

print('🔍 Starting performance analysis...')
start_time = time.perf_counter()

analyzer = ProjectAnalyzer()
print('✅ ProjectAnalyzer initialized')

model = analyzer.analyze_project(['./tests/test_files'], 'Perf_Test')
end_time = time.perf_counter()

duration = end_time - start_time
print(f'⏱️ Analysis completed in {duration:.2f} seconds')
print(f'📁 Files processed: {len(model.files)}')
print(f'📊 Model size: {len(str(model))} characters')

# Additional metrics
if hasattr(model, 'functions'):
    print(f'🔧 Functions found: {len(model.functions)}')
if hasattr(model, 'structs'):
    print(f'🏗️ Structs found: {len(model.structs)}')
if hasattr(model, 'enums'):
    print(f'📋 Enums found: {len(model.enums)}')

if duration > 30:  # Fail if takes more than 30 seconds for test files
    print('❌ Error: Analysis took too long')
    sys.exit(1)
else:
    print('✅ Performance test passed')
"
"""
        
        return self.run_command(perf_cmd, "Performance benchmark")
    
    def run_complex_integration_test(self):
        """Run complex integration test"""
        self.log("🏗️ Running complex integration test...")
        
        # Create complex test project
        self.log("🏗️ Creating complex test project...")
        self.run_command("mkdir -p complex_test/src complex_test/include", "Create test directories", check_returncode=False)
        
        # Create main.c
        main_c_content = '''#include "../include/utils.h"
#include <stdio.h>

int main() {
    utils_init();
    return 0;
}'''
        
        with open("complex_test/src/main.c", 'w') as f:
            f.write(main_c_content)
        
        # Create utils.c
        utils_c_content = '''#include "../include/utils.h"

static int initialized = 0;

void utils_init(void) {
    initialized = 1;
}

int utils_is_initialized(void) {
    return initialized;
}'''
        
        with open("complex_test/src/utils.c", 'w') as f:
            f.write(utils_c_content)
        
        # Create utils.h
        utils_h_content = '''#ifndef UTILS_H
#define UTILS_H

void utils_init(void);
int utils_is_initialized(void);

#endif'''
        
        with open("complex_test/include/utils.h", 'w') as f:
            f.write(utils_h_content)
        
        self.log("📋 Complex test project structure:")
        self.run_command("find complex_test -type f", "List test files", check_returncode=False)
        
        # Create config for complex project
        complex_config = {
            "project_name": "Complex_Integration_Test",
            "project_roots": ["./complex_test"],
            "model_output_path": "./complex_model.json",
            "output_dir": "./complex_output",
            "recursive": True,
            "c_file_prefixes": []
        }
        
        with open("complex_config.json", 'w') as f:
            json.dump(complex_config, f, indent=2)
        
        self.log("📋 Configuration created:")
        self.run_command("cat complex_config.json", "Show config", check_returncode=False)
        
        # Run analysis
        self.log("🔄 Running analysis...")
        analysis_success = self.run_command(
            "python -m c_to_plantuml.main config complex_config.json",
            "Complex project analysis"
        )
        
        if not analysis_success:
            return False
        
        # Validate output
        self.log("🔍 Validating complex project output...")
        
        # Check model file
        if not os.path.exists("complex_model.json"):
            self.log("❌ Error: Complex model not created")
            self.run_command("ls -la *.json", "List JSON files", check_returncode=False)
            return False
        else:
            self.log("✅ Complex model file created")
            file_size = os.path.getsize("complex_model.json")
            self.log(f"📊 Model file size: {file_size} bytes")
        
        # Validate JSON structure
        self.log("🔍 Validating JSON structure...")
        validation_cmd = """python -c "
import json
with open('complex_model.json', 'r') as f:
    model = json.load(f)
    print(f'Project name: {model[\"project_name\"]}')
    print(f'Files count: {len(model[\"files\"])}')
    print(f'Files: {list(model[\"files\"].keys())}')
    assert model['project_name'] == 'Complex_Integration_Test'
    assert len(model['files']) >= 2  # Should have main.c and utils.c
    print('✅ Complex model validation passed')
"
"""
        
        validation_success = self.run_command(validation_cmd, "Complex model validation")
        
        # Check PlantUML output
        self.log("🔍 Checking PlantUML output...")
        if not os.path.exists("complex_output"):
            self.log("❌ Error: Complex output directory not created")
            self.run_command("ls -la", "List directory contents", check_returncode=False)
            return False
        
        self.log("📋 Complex output contents:")
        self.run_command("find complex_output -type f", "List complex output files", check_returncode=False)
        
        complex_puml_count = len(list(Path("complex_output").glob("*.puml")))
        if complex_puml_count < 2:
            self.log(f"❌ Error: Expected at least 2 PlantUML files, got {complex_puml_count}")
            return False
        
        self.log(f"✅ Integration test passed: {complex_puml_count} PlantUML files generated")
        self.run_command("find complex_output -name '*.puml' -exec wc -l {} \\;", "Complex PlantUML line counts", check_returncode=False)
        
        return validation_success
    
    def run_all_tests(self):
        """Run all tests from GitHub workflow"""
        self.log("🚀 Starting Enhanced Test Suite (GitHub Workflow Logic)")
        self.log("=" * 60)
        
        # Setup environment
        if not self.setup_environment():
            self.log("❌ Environment setup failed")
            return False
        
        # Run all test categories
        test_categories = [
            ("Linting Tests", self.run_linting_tests),
            ("Test Discovery", self.discover_test_files),
            ("Unit Tests", self.run_unit_tests),
            ("Comprehensive Test Suite", self.run_comprehensive_test_suite),
            ("Complete Workflow", self.test_complete_workflow),
            ("Output Verification", self.verify_output_files),
            ("CLI Tools", self.test_cli_tools),
            ("Performance Benchmark", self.run_performance_benchmark),
            ("Complex Integration", self.run_complex_integration_test),
        ]
        
        all_success = True
        for category_name, test_func in test_categories:
            self.log(f"\n{'='*60}")
            self.log(f"Running: {category_name}")
            self.log(f"{'='*60}")
            
            try:
                success = test_func()
                if not success:
                    all_success = False
                    self.log(f"❌ {category_name} failed")
                else:
                    self.log(f"✅ {category_name} passed")
            except Exception as e:
                self.log(f"❌ {category_name} error: {e}")
                all_success = False
        
        # Summary
        self.log(f"\n{'='*60}")
        self.log("TEST SUITE SUMMARY")
        self.log(f"{'='*60}")
        
        if all_success:
            self.log("🎉 ALL TESTS PASSED!")
            return True
        else:
            self.log("❌ SOME TESTS FAILED!")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced Test Runner for C to PlantUML Converter")
    parser.add_argument("--verbose", "-v", action="store_true", default=True, help="Enable verbose output")
    parser.add_argument("--output-dir", "-o", default="test_output", help="Output directory for test artifacts")
    parser.add_argument("--category", "-c", choices=["linting", "discovery", "unit", "comprehensive", "workflow", "verification", "cli", "performance", "complex", "all"], 
                       default="all", help="Run specific test category")
    
    args = parser.parse_args()
    
    runner = EnhancedTestRunner(verbose=args.verbose, output_dir=args.output_dir)
    
    if args.category == "all":
        success = runner.run_all_tests()
        return 0 if success else 1
    else:
        # Run specific category
        if args.category == "linting":
            success = runner.run_linting_tests()
        elif args.category == "discovery":
            runner.discover_test_files()
            success = True
        elif args.category == "unit":
            success = runner.run_unit_tests()
        elif args.category == "comprehensive":
            success = runner.run_comprehensive_test_suite()
        elif args.category == "workflow":
            success = runner.test_complete_workflow()
        elif args.category == "verification":
            success = runner.verify_output_files()
        elif args.category == "cli":
            success = runner.test_cli_tools()
        elif args.category == "performance":
            success = runner.run_performance_benchmark()
        elif args.category == "complex":
            success = runner.run_complex_integration_test()
            
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())