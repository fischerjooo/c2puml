#!/usr/bin/env python3
"""
Comprehensive test runner for C to PlantUML converter
Runs unit tests, integration tests, and performance tests
"""

import os
import sys
import subprocess
import tempfile
import json
import time
from pathlib import Path


def run_command(cmd, description, check_returncode=True):
    """Run a command and return success status"""
    print(f"🔄 Running: {description}")
    print(f"📟 Command: {cmd}")
    print("=" * 80)
    
    try:
        start_time = time.perf_counter()
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        print(f"⏱️  Execution time: {duration:.3f} seconds")
        print(f"🔢 Return code: {result.returncode}")
        
        if result.stdout:
            print("📤 STDOUT:")
            print("-" * 40)
            print(result.stdout)
            print("-" * 40)
        if result.stderr:
            print("⚠️  STDERR:")
            print("-" * 40)
            print(result.stderr)
            print("-" * 40)
        
        if check_returncode and result.returncode != 0:
            print(f"❌ FAILED ({description})")
            return False
        else:
            print(f"✅ PASSED ({description})")
            return True
            
    except subprocess.TimeoutExpired:
        print(f"❌ FAILED (timeout after 120s) - {description}")
        return False
    except Exception as e:
        print(f"❌ FAILED (error: {e}) - {description}")
        return False


def main():
    """Run all tests"""
    print("🧪 C to PlantUML Converter - Comprehensive Test Suite")
    print("=" * 80)
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"⏰ Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    overall_start_time = time.perf_counter()
    
    test_results = []
    
    # Unit Tests
    print("=" * 60)
    print("Running: Parser Unit Tests")
    success = run_command(
        "python3 -m unittest tests.test_parser -v",
        "Parser Unit Tests"
    )
    test_results.append(("Parser Unit Tests", success))
    print()
    
    print("=" * 60)
    print("Running: Project Analyzer Unit Tests")
    success = run_command(
        "python3 -m unittest tests.test_project_analyzer -v",
        "Project Analyzer Unit Tests"
    )
    test_results.append(("Project Analyzer Unit Tests", success))
    print()
    
    print("=" * 60)
    print("Running: Configuration Manipulation Tests")
    success = run_command(
        "python3 -m unittest tests.test_config_manipulations -v",
        "Configuration Manipulation Tests"
    )
    test_results.append(("Configuration Manipulation Tests", success))
    print()
    
    print("=" * 60)
    print("Running: Configuration Integration Tests")
    success = run_command(
        "python3 -m unittest tests.test_config_integration -v",
        "Configuration Integration Tests"
    )
    test_results.append(("Configuration Integration Tests", success))
    print()
    
    print("=" * 60)
    print("Running: Configuration CLI Tests")
    success = run_command(
        "python3 -m unittest tests.test_config_cli -v",
        "Configuration CLI Tests"
    )
    test_results.append(("Configuration CLI Tests", success))
    print()
    
    # Integration Tests
    print("=" * 60)
    print("Integration Tests")
    print("=" * 60)
    print()
    
    # Test 1: Full workflow using config
    print("=" * 60)
    print("Running: Full Workflow Test")
    success = run_command(
        "python3 -m c_to_plantuml.main config test_config.json",
        "Full Workflow Test"
    )
    test_results.append(("Full Workflow Test", success))
    print()
    
    # Test 2: CLI analysis tool
    print("=" * 60)
    print("Running: CLI Analysis Tool Test")
    with tempfile.TemporaryDirectory() as tmp_dir:
        cmd = f"""python3 -c "
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
handle_analyze_command(args)"
"""
        success = run_command(cmd, "CLI Analysis Tool Test")
        test_results.append(("CLI Analysis Tool Test", success))
    print()
    
    # Test 3: PlantUML generation from JSON
    print("=" * 60)
    print("Running: PlantUML Generation Test")
    with tempfile.TemporaryDirectory() as tmp_dir:
        # First create a test model
        model_path = f"{tmp_dir}/test_model.json"
        cmd1 = f"""python3 -c "
import sys
sys.path.insert(0, '.')
from c_to_plantuml.project_analyzer import ProjectAnalyzer
analyzer = ProjectAnalyzer()
model = analyzer.analyze_and_save(['./tests/test_files'], '{model_path}', 'PlantUML_Test')
print('Model created successfully')
"
"""
        success1 = run_command(cmd1, "Create Test Model", check_returncode=False)
        
        if success1:
            # Then generate PlantUML
            cmd2 = f"""python3 -c "
import sys
sys.path.insert(0, '.')
from c_to_plantuml.main import handle_generate_command
import argparse
args = argparse.Namespace()
args.model_json = '{model_path}'
args.output_dir = '{tmp_dir}/plantuml_output'
handle_generate_command(args)"
"""
            success2 = run_command(cmd2, "Generate PlantUML")
            success = success1 and success2
        else:
            success = False
        
        test_results.append(("PlantUML Generation Test", success))
    print()
    
    # Performance Tests
    print("=" * 60)
    print("Performance Tests")
    print("=" * 60)
    try:
        import time
        from c_to_plantuml.parsers.c_parser import CParser
        
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
        
        print(f"Performance Test Results:")
        print(f"- Parsed file with 200+ functions in {parse_time:.3f} seconds")
        print(f"- Found {len(parser.functions)} functions")
        print(f"- Found {len(parser.structs)} structs")
        
        # Cleanup
        os.unlink(temp_file)
        
        perf_success = parse_time < 2.0  # Should parse in under 2 seconds
        test_results.append(("Performance Test", perf_success))
        
        if perf_success:
            print("✅ Performance test passed")
        else:
            print("❌ Performance test failed (too slow)")
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        test_results.append(("Performance Test", False))
    print()
    
    # Code Quality Tests
    print("=" * 60)
    print("Code Quality Tests")
    print("=" * 60)
    
    # Syntax checks
    code_files = [
        "c_to_plantuml/parsers/c_parser.py",
        "c_to_plantuml/project_analyzer.py",
        "c_to_plantuml/generators/plantuml_generator.py",
        "c_to_plantuml/models/project_model.py",
        "c_to_plantuml/main.py"
    ]
    
    syntax_success = True
    for file_path in code_files:
        print("=" * 60)
        print(f"Running: Syntax Check - {Path(file_path).stem}")
        success = run_command(f"python3 -m py_compile {file_path}", f"Syntax Check - {file_path}")
        syntax_success = syntax_success and success
        print()
    
    test_results.append(("Code Syntax Checks", syntax_success))
    
    # File structure tests
    print("=" * 60)
    print("File Structure Tests")
    print("=" * 60)
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
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        structure_success = False
    else:
        print("✅ All required files present")
        structure_success = True
    
    test_results.append(("File Structure", structure_success))
    print()
    
    overall_end_time = time.perf_counter()
    total_duration = overall_end_time - overall_start_time
    
    # Summary
    print("=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    
    print(f"⏰ Total execution time: {total_duration:.3f} seconds")
    print(f"🧪 Tests completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status} {test_name}")
    
    print()
    print(f"📈 Passed: {passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    print(f"⚡ Average time per test: {total_duration/total:.3f} seconds")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔍 Check the output above for details on failed tests")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())