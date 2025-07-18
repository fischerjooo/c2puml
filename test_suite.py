#!/usr/bin/env python3
"""
Comprehensive Test Suite for C to PlantUML Converter
Consolidates all test logic from GitHub workflow into Python scripts
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
from typing import List, Tuple, Dict, Any
import unittest
import importlib.util


class TestSuite:
    """Main test suite class that consolidates all testing logic"""
    
    def __init__(self, verbose: bool = True, output_dir: str = "test_output"):
        self.verbose = verbose
        self.output_dir = output_dir
        self.test_results = []
        self.setup_output_dir()
        
    def setup_output_dir(self):
        """Create output directory for test artifacts"""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)
        
    def log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(message)
            
    def run_command(self, cmd: str, description: str, check_returncode: bool = True) -> bool:
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
            
    def run_unit_tests(self) -> List[Tuple[str, bool]]:
        """Run all unit tests"""
        self.log("🧪 Running Unit Tests")
        self.log("=" * 60)
        
        unit_tests = [
            ("tests.test_parser", "Parser Unit Tests"),
            ("tests.test_project_analyzer", "Project Analyzer Unit Tests"),
            ("tests.test_config_manipulations", "Configuration Manipulation Tests"),
            ("tests.test_config_integration", "Configuration Integration Tests"),
            ("tests.test_config_cli", "Configuration CLI Tests"),
        ]
        
        results = []
        for test_module, description in unit_tests:
            self.log(f"📝 Running: {description}")
            success = self.run_command(
                f"python -m unittest {test_module} -v --buffer",
                description
            )
            results.append((description, success))
            self.log()
            
        return results
        
    def run_linting_tests(self) -> List[Tuple[str, bool]]:
        """Run code quality and linting tests"""
        self.log("🔍 Running Code Quality Tests")
        self.log("=" * 60)
        
        results = []
        
        # Install flake8 if not available
        self.run_command("pip install flake8", "Installing flake8", check_returncode=False)
        
        # Syntax error check
        self.log("📝 Checking for Python syntax errors and undefined names...")
        syntax_success = self.run_command(
            "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
            "Syntax Error Check"
        )
        results.append(("Syntax Error Check", syntax_success))
        
        # Style check
        self.log("📊 Running comprehensive style check...")
        style_success = self.run_command(
            "flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics",
            "Style Check"
        )
        results.append(("Style Check", style_success))
        
        # Syntax compilation check
        code_files = [
            "c_to_plantuml/parsers/c_parser.py",
            "c_to_plantuml/project_analyzer.py",
            "c_to_plantuml/generators/plantuml_generator.py",
            "c_to_plantuml/models/project_model.py",
            "c_to_plantuml/main.py"
        ]
        
        syntax_compilation_success = True
        for file_path in code_files:
            if os.path.exists(file_path):
                success = self.run_command(
                    f"python -m py_compile {file_path}",
                    f"Syntax Compilation - {Path(file_path).stem}"
                )
                syntax_compilation_success = syntax_compilation_success and success
            else:
                self.log(f"⚠️ File not found: {file_path}")
                syntax_compilation_success = False
                
        results.append(("Syntax Compilation", syntax_compilation_success))
        
        return results
        
    def run_integration_tests(self) -> List[Tuple[str, bool]]:
        """Run integration tests"""
        self.log("🔄 Running Integration Tests")
        self.log("=" * 60)
        
        results = []
        
        # Test 1: Full workflow using config
        self.log("📝 Running: Full Workflow Test")
        workflow_success = self.run_command(
            "python -m c_to_plantuml.main config test_config.json",
            "Full Workflow Test"
        )
        results.append(("Full Workflow Test", workflow_success))
        
        # Test 2: CLI analysis tool
        self.log("📝 Running: CLI Analysis Tool Test")
        with tempfile.TemporaryDirectory() as tmp_dir:
            cmd = f"""python -c "
import sys
sys.path.insert(0, '.')
from c_to_plantuml.main import handle_analyze_command
import argparse
args = argparse.Namespace()
args.project_roots = ['./tests/test_files']
args.output = '{tmp_dir}/cli_model.json'
args.name = 'CLI_Test'
args.prefixes = None
args.no_recursive = False
exit_code = handle_analyze_command(args)
if exit_code != 0:
    sys.exit(1)
print('CLI analysis completed successfully')
"
"""
            cli_analysis_success = self.run_command(cmd, "CLI Analysis Tool Test")
            results.append(("CLI Analysis Tool Test", cli_analysis_success))
            
        # Test 3: PlantUML generation from JSON
        self.log("📝 Running: PlantUML Generation Test")
        with tempfile.TemporaryDirectory() as tmp_dir:
            # First create a test model
            model_path = f"{tmp_dir}/test_model.json"
            cmd1 = f"""python -c "
import sys
sys.path.insert(0, '.')
from c_to_plantuml.project_analyzer import ProjectAnalyzer
analyzer = ProjectAnalyzer()
model = analyzer.analyze_and_save(['./tests/test_files'], '{model_path}', 'PlantUML_Test')
print('Model created successfully')
"
"""
            success1 = self.run_command(cmd1, "Create Test Model", check_returncode=False)
            
            if success1:
                # Then generate PlantUML
                cmd2 = f"""python -c "
import sys
sys.path.insert(0, '.')
from c_to_plantuml.main import handle_generate_command
import argparse
args = argparse.Namespace()
args.model_json = '{model_path}'
args.output_dir = '{tmp_dir}/plantuml_output'
exit_code = handle_generate_command(args)
if exit_code != 0:
    sys.exit(1)
print('PlantUML generation completed successfully')
"
"""
                success2 = self.run_command(cmd2, "Generate PlantUML")
                plantuml_success = success1 and success2
            else:
                plantuml_success = False
            
            results.append(("PlantUML Generation Test", plantuml_success))
            
        return results
        
    def run_performance_tests(self) -> List[Tuple[str, bool]]:
        """Run performance tests"""
        self.log("⚡ Running Performance Tests")
        self.log("=" * 60)
        
        results = []
        
        try:
            # Import required modules
            sys.path.insert(0, '.')
            from c_to_plantuml.project_analyzer import ProjectAnalyzer
            from c_to_plantuml.parsers.c_parser import CParser
            
            # Performance test 1: Project analysis
            self.log("🔍 Testing project analysis performance...")
            start_time = time.perf_counter()
            
            analyzer = ProjectAnalyzer()
            model = analyzer.analyze_project(['./tests/test_files'], 'Perf_Test')
            
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            self.log(f"⏱️ Analysis completed in {duration:.2f} seconds")
            self.log(f"📁 Files processed: {len(model.files)}")
            self.log(f"📊 Model size: {len(str(model))} characters")
            
            # Additional metrics
            if hasattr(model, 'functions'):
                self.log(f"🔧 Functions found: {len(model.functions)}")
            if hasattr(model, 'structs'):
                self.log(f"🏗️ Structs found: {len(model.structs)}")
            if hasattr(model, 'enums'):
                self.log(f"📋 Enums found: {len(model.enums)}")
                
            perf_success = duration < 30  # Fail if takes more than 30 seconds
            results.append(("Project Analysis Performance", perf_success))
            
            # Performance test 2: Parser performance
            self.log("🔍 Testing parser performance...")
            
            # Create a large test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                large_content = '''
#include <stdio.h>
#include <stdlib.h>

#define BUFFER_SIZE 1024

typedef struct {
    int id;
    char name[50];
    double value;
} TestStruct;

''' + '\n'.join([f'int function_{i}(int param) {{ return param * {i}; }}' for i in range(200)])
                
                f.write(large_content)
                temp_file = f.name
            
            parser = CParser()
            
            # Measure parsing time
            start_time = time.time()
            parser.parse_file(temp_file)
            parse_time = time.time() - start_time
            
            self.log(f"Performance Test Results:")
            self.log(f"- Parsed file with 200+ functions in {parse_time:.3f} seconds")
            self.log(f"- Found {len(parser.functions)} functions")
            self.log(f"- Found {len(parser.structs)} structs")
            
            # Cleanup
            os.unlink(temp_file)
            
            parser_perf_success = parse_time < 2.0  # Should parse in under 2 seconds
            results.append(("Parser Performance", parser_perf_success))
            
        except Exception as e:
            self.log(f"❌ Performance test error: {e}")
            results.append(("Performance Tests", False))
            
        return results
        
    def run_file_structure_tests(self) -> List[Tuple[str, bool]]:
        """Run file structure validation tests"""
        self.log("📁 Running File Structure Tests")
        self.log("=" * 60)
        
        results = []
        
        required_files = [
            "c_to_plantuml/__init__.py",
            "c_to_plantuml/main.py",
            "c_to_plantuml/parsers/__init__.py",
            "c_to_plantuml/parsers/c_parser.py",
            "c_to_plantuml/models/__init__.py",
            "c_to_plantuml/models/c_structures.py",
            "c_to_plantuml/models/project_model.py",
            "c_to_plantuml/generators/__init__.py",
            "c_to_plantuml/generators/plantuml_generator.py",
            "c_to_plantuml/project_analyzer.py",
            "c_to_plantuml/utils/__init__.py",
            "c_to_plantuml/utils/file_utils.py",
            "tests/test_parser.py",
            "tests/test_project_analyzer.py",
            "setup.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
                self.log(f"❌ Missing: {file_path}")
            else:
                self.log(f"✅ Found: {file_path}")
        
        if missing_files:
            self.log(f"❌ Missing files: {missing_files}")
            structure_success = False
        else:
            self.log("✅ All required files present")
            structure_success = True
        
        results.append(("File Structure", structure_success))
        
        return results
        
    def run_output_validation_tests(self) -> List[Tuple[str, bool]]:
        """Run output validation tests"""
        self.log("🔍 Running Output Validation Tests")
        self.log("=" * 60)
        
        results = []
        
        # Check that expected files were created
        if not os.path.exists("test_project_model.json"):
            self.log("❌ Error: test_project_model.json not created")
            results.append(("Model File Creation", False))
        else:
            self.log("✅ test_project_model.json created successfully")
            file_size = os.path.getsize("test_project_model.json")
            self.log(f"📊 Model file size: {file_size} bytes")
            results.append(("Model File Creation", True))
        
        if not os.path.exists("test_plantuml_output"):
            self.log("❌ Error: test_plantuml_output directory not created")
            results.append(("PlantUML Output Directory", False))
        else:
            self.log("✅ test_plantuml_output directory created successfully")
            
            # Check for .puml files
            puml_files = list(Path("test_plantuml_output").glob("*.puml"))
            if not puml_files:
                self.log("❌ Error: No .puml files generated")
                results.append(("PlantUML File Generation", False))
            else:
                self.log(f"✅ Success: Found {len(puml_files)} PlantUML files")
                for puml_file in puml_files:
                    line_count = len(puml_file.read_text().splitlines())
                    self.log(f"📊 {puml_file.name}: {line_count} lines")
                results.append(("PlantUML File Generation", True))
        
        return results
        
    def run_complex_integration_test(self) -> List[Tuple[str, bool]]:
        """Run complex integration test with created test project"""
        self.log("🏗️ Running Complex Integration Test")
        self.log("=" * 60)
        
        results = []
        
        # Create complex test project
        complex_test_dir = os.path.join(self.output_dir, "complex_test")
        os.makedirs(complex_test_dir, exist_ok=True)
        
        # Create source files
        src_dir = os.path.join(complex_test_dir, "src")
        include_dir = os.path.join(complex_test_dir, "include")
        os.makedirs(src_dir, exist_ok=True)
        os.makedirs(include_dir, exist_ok=True)
        
        # Create main.c
        main_c_content = '''#include "../include/utils.h"
#include <stdio.h>

int main() {
    utils_init();
    return 0;
}'''
        
        with open(os.path.join(src_dir, "main.c"), 'w') as f:
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
        
        with open(os.path.join(src_dir, "utils.c"), 'w') as f:
            f.write(utils_c_content)
            
        # Create utils.h
        utils_h_content = '''#ifndef UTILS_H
#define UTILS_H

void utils_init(void);
int utils_is_initialized(void);

#endif'''
        
        with open(os.path.join(include_dir, "utils.h"), 'w') as f:
            f.write(utils_h_content)
            
        self.log("📋 Complex test project structure created:")
        for root, dirs, files in os.walk(complex_test_dir):
            for file in files:
                self.log(f"  {os.path.join(root, file)}")
        
        # Create config for complex project
        complex_config = {
            "project_name": "Complex_Integration_Test",
            "project_roots": [complex_test_dir],
            "model_output_path": os.path.join(self.output_dir, "complex_model.json"),
            "output_dir": os.path.join(self.output_dir, "complex_output"),
            "recursive": True,
            "c_file_prefixes": []
        }
        
        config_path = os.path.join(self.output_dir, "complex_config.json")
        with open(config_path, 'w') as f:
            json.dump(complex_config, f, indent=2)
            
        self.log("📋 Configuration created:")
        self.log(json.dumps(complex_config, indent=2))
        
        # Run analysis
        self.log("🔄 Running complex project analysis...")
        analysis_success = self.run_command(
            f"python -m c_to_plantuml.main config {config_path}",
            "Complex Project Analysis"
        )
        results.append(("Complex Project Analysis", analysis_success))
        
        # Validate output
        if analysis_success:
            # Check model file
            model_path = complex_config["model_output_path"]
            if not os.path.exists(model_path):
                self.log("❌ Error: Complex model not created")
                results.append(("Complex Model Creation", False))
            else:
                self.log("✅ Complex model file created")
                file_size = os.path.getsize(model_path)
                self.log(f"📊 Model file size: {file_size} bytes")
                
                # Validate JSON structure
                try:
                    with open(model_path, 'r') as f:
                        model = json.load(f)
                    self.log(f"Project name: {model['project_name']}")
                    self.log(f"Files count: {len(model['files'])}")
                    self.log(f"Files: {list(model['files'].keys())}")
                    
                    if model['project_name'] == 'Complex_Integration_Test' and len(model['files']) >= 2:
                        self.log("✅ Complex model validation passed")
                        results.append(("Complex Model Validation", True))
                    else:
                        self.log("❌ Complex model validation failed")
                        results.append(("Complex Model Validation", False))
                except Exception as e:
                    self.log(f"❌ Complex model validation error: {e}")
                    results.append(("Complex Model Validation", False))
                
                # Check PlantUML output
                output_dir = complex_config["output_dir"]
                if not os.path.exists(output_dir):
                    self.log("❌ Error: Complex output directory not created")
                    results.append(("Complex PlantUML Output", False))
                else:
                    self.log("✅ Complex output directory created")
                    
                    puml_files = list(Path(output_dir).glob("*.puml"))
                    if len(puml_files) < 2:
                        self.log(f"❌ Error: Expected at least 2 PlantUML files, got {len(puml_files)}")
                        results.append(("Complex PlantUML Output", False))
                    else:
                        self.log(f"✅ Integration test passed: {len(puml_files)} PlantUML files generated")
                        for puml_file in puml_files:
                            line_count = len(puml_file.read_text().splitlines())
                            self.log(f"📊 {puml_file.name}: {line_count} lines")
                        results.append(("Complex PlantUML Output", True))
        
        return results
        
    def run_all_tests(self) -> Dict[str, List[Tuple[str, bool]]]:
        """Run all test categories"""
        self.log("🚀 Starting Comprehensive Test Suite")
        self.log("=" * 60)
        
        all_results = {}
        
        # Run all test categories
        all_results["unit_tests"] = self.run_unit_tests()
        all_results["linting_tests"] = self.run_linting_tests()
        all_results["integration_tests"] = self.run_integration_tests()
        all_results["performance_tests"] = self.run_performance_tests()
        all_results["file_structure_tests"] = self.run_file_structure_tests()
        all_results["output_validation_tests"] = self.run_output_validation_tests()
        all_results["complex_integration_test"] = self.run_complex_integration_test()
        
        return all_results
        
    def generate_report(self, all_results: Dict[str, List[Tuple[str, bool]]]):
        """Generate comprehensive test report"""
        self.log("\n" + "=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        total_passed = 0
        total_tests = 0
        
        for category, results in all_results.items():
            self.log(f"\n📋 {category.replace('_', ' ').title()}:")
            category_passed = 0
            for test_name, success in results:
                status = "✅ PASSED" if success else "❌ FAILED"
                self.log(f"  {test_name}: {status}")
                if success:
                    category_passed += 1
                total_tests += 1
                total_passed += 1 if success else 0
                
            category_total = len(results)
            self.log(f"  Category: {category_passed}/{category_total} passed")
        
        self.log(f"\n📊 OVERALL RESULTS:")
        self.log(f"Total Tests: {total_tests}")
        self.log(f"Passed: {total_passed}")
        self.log(f"Failed: {total_tests - total_passed}")
        self.log(f"Success Rate: {total_passed/total_tests*100:.1f}%")
        
        if total_passed == total_tests:
            self.log("🎉 ALL TESTS PASSED!")
            return 0
        else:
            self.log("❌ SOME TESTS FAILED!")
            return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Comprehensive Test Suite for C to PlantUML Converter")
    parser.add_argument("--verbose", "-v", action="store_true", default=True, help="Enable verbose output")
    parser.add_argument("--output-dir", "-o", default="test_output", help="Output directory for test artifacts")
    parser.add_argument("--category", "-c", choices=["unit", "linting", "integration", "performance", "structure", "validation", "complex", "all"], 
                       default="all", help="Run specific test category")
    
    args = parser.parse_args()
    
    test_suite = TestSuite(verbose=args.verbose, output_dir=args.output_dir)
    
    if args.category == "all":
        all_results = test_suite.run_all_tests()
        return test_suite.generate_report(all_results)
    else:
        # Run specific category
        if args.category == "unit":
            results = test_suite.run_unit_tests()
        elif args.category == "linting":
            results = test_suite.run_linting_tests()
        elif args.category == "integration":
            results = test_suite.run_integration_tests()
        elif args.category == "performance":
            results = test_suite.run_performance_tests()
        elif args.category == "structure":
            results = test_suite.run_file_structure_tests()
        elif args.category == "validation":
            results = test_suite.run_output_validation_tests()
        elif args.category == "complex":
            results = test_suite.run_complex_integration_test()
            
        test_suite.generate_report({args.category: results})
        return 0 if all(success for _, success in results) else 1


if __name__ == "__main__":
    sys.exit(main())