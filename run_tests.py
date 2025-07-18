#!/usr/bin/env python3
"""
Comprehensive test runner for the C to PlantUML converter
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
from pathlib import Path

def run_command(cmd, description, cwd=None):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        print("✅ PASSED")
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print("STDERR:", e.stderr)
        print("STDOUT:", e.stdout)
        return False

def main():
    """Run all tests"""
    print("C to PlantUML Converter - Comprehensive Test Suite")
    print("=" * 60)
    
    # Track test results
    passed_tests = 0
    total_tests = 0
    
    # 1. Unit Tests
    tests = [
        ("python3 -m unittest tests.test_enhanced_parser -v", "Enhanced Parser Unit Tests"),
        ("python3 -m unittest tests.test_project_analyzer -v", "Project Analyzer Unit Tests"),
    ]
    
    for cmd, desc in tests:
        total_tests += 1
        if run_command(cmd, desc):
            passed_tests += 1
    
    # 2. Integration Tests
    print(f"\n{'='*60}")
    print("Integration Tests")
    print(f"{'='*60}")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test with new configuration
        total_tests += 1
        if run_command(
            "python3 -m c_to_plantuml.main --config test_config.json --clean --verbose",
            "Full Workflow Test"
        ):
            # Verify outputs
            if (Path("project_model.json").exists() and 
                Path("output_uml").exists() and 
                len(list(Path("output_uml").glob("*.puml"))) > 0):
                print("✅ Output verification passed")
                passed_tests += 1
            else:
                print("❌ Output verification failed")
        
        # Test CLI tools
        total_tests += 1
        if run_command(
            f"python3 -c \"\nimport sys\nsys.path.insert(0, '.')\nfrom c_to_plantuml.main import analyze_project_cli\nimport os\nsys.argv = ['analyze_project_cli', './tests/test_files', '--output', '{temp_path}/cli_model.json', '--name', 'CLI_Test']\nanalyze_project_cli()\"",
            "CLI Analysis Tool Test"
        ):
            if (temp_path / "cli_model.json").exists():
                total_tests += 1
                if run_command(
                    f"python3 -c \"\nimport sys\nsys.path.insert(0, '.')\nfrom c_to_plantuml.main import generate_plantuml_cli\nimport os\nsys.argv = ['generate_plantuml_cli', '{temp_path}/cli_model.json', '--output', '{temp_path}/cli_output']\ngenerate_plantuml_cli()\"",
                    "CLI Generation Tool Test"
                ):
                    if (temp_path / "cli_output").exists():
                        print("✅ CLI tools verification passed")
                        passed_tests += 1
                    else:
                        print("❌ CLI generation failed")
            else:
                print("❌ CLI analysis failed")
    
    # 3. Performance Tests
    print(f"\n{'='*60}")
    print("Performance Tests")
    print(f"{'='*60}")
    
    try:
        from c_to_plantuml.project_analyzer import ProjectAnalyzer
        
        start_time = time.perf_counter()
        analyzer = ProjectAnalyzer()
        model = analyzer.analyze_project(['./tests/test_files'], 'Performance_Test')
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        total_tests += 1
        
        print(f"Analysis completed in {duration:.2f} seconds")
        print(f"Files processed: {len(model.files)}")
        
        if duration < 10:  # Should complete within 10 seconds for test files
            print("✅ Performance test passed")
            passed_tests += 1
        else:
            print("❌ Performance test failed - took too long")
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
    
    # 4. Code Quality Tests
    print(f"\n{'='*60}")
    print("Code Quality Tests")
    print(f"{'='*60}")
    
    # Check for Python syntax errors
    total_tests += 1
    if run_command(
        "python3 -m py_compile c_to_plantuml/parsers/c_parser_enhanced.py",
        "Syntax Check - Enhanced Parser"
    ):
        passed_tests += 1
    
    total_tests += 1
    if run_command(
        "python3 -m py_compile c_to_plantuml/project_analyzer.py",
        "Syntax Check - Project Analyzer"
    ):
        passed_tests += 1
    
    total_tests += 1
    if run_command(
        "python3 -m py_compile c_to_plantuml/generators/plantuml_generator.py",
        "Syntax Check - PlantUML Generator"
    ):
        passed_tests += 1
    
    # 5. File Structure Tests
    print(f"\n{'='*60}")
    print("File Structure Tests")
    print(f"{'='*60}")
    
    required_files = [
        "c_to_plantuml/parsers/c_parser_enhanced.py",
        "c_to_plantuml/models/project_model.py",
        "c_to_plantuml/generators/plantuml_generator.py",
        "c_to_plantuml/project_analyzer.py",
        "c_to_plantuml/main.py",
        "tests/test_files/sample.c",
        "tests/test_files/sample.h",
        "test_config.json",
        "setup.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    total_tests += 1
    if not missing_files:
        print("✅ All required files present")
        passed_tests += 1
    else:
        print(f"❌ Missing files: {missing_files}")
    
    # Final Results
    print(f"\n{'='*60}")
    print("TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())