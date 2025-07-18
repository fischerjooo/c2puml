#!/usr/bin/env python3
"""
Quick Test Runner for C to PlantUML Converter
Simplified version for fast local testing
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔧 {description}")
    print(f"Command: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.stdout:
            print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode != 0:
            print("❌ FAILED")
            return False
        else:
            print("✅ PASSED")
            return True
            
    except subprocess.TimeoutExpired:
        print("❌ FAILED (timeout)")
        return False
    except Exception as e:
        print(f"❌ FAILED (error: {e})")
        return False


def main():
    """Run quick test suite"""
    print("🚀 Quick Test Suite for C to PlantUML Converter")
    print("=" * 50)
    
    test_results = []
    
    # 1. Basic syntax check
    print("\n📝 Testing: Basic Syntax Check")
    success = run_command("python -m py_compile c_to_plantuml/main.py", "Main module syntax")
    test_results.append(("Syntax Check", success))
    
    # 2. Unit tests (core ones only)
    print("\n🧪 Testing: Core Unit Tests")
    success = run_command("python -m unittest tests.test_parser -v", "Parser tests")
    test_results.append(("Parser Unit Tests", success))
    
    success = run_command("python -m unittest tests.test_project_analyzer -v", "Project Analyzer tests")
    test_results.append(("Project Analyzer Unit Tests", success))
    
    # 3. Integration test
    print("\n🔄 Testing: Basic Integration")
    success = run_command("python -m c_to_plantuml.main config test_config.json", "Full workflow")
    test_results.append(("Integration Test", success))
    
    # 4. Output validation
    print("\n🔍 Testing: Output Validation")
    if os.path.exists("test_project_model.json"):
        print("✅ Model file created")
        file_size = os.path.getsize("test_project_model.json")
        print(f"📊 Model file size: {file_size} bytes")
        test_results.append(("Model Creation", True))
    else:
        print("❌ Model file not created")
        test_results.append(("Model Creation", False))
    
    if os.path.exists("test_plantuml_output"):
        puml_files = list(Path("test_plantuml_output").glob("*.puml"))
        if puml_files:
            print(f"✅ PlantUML files created: {len(puml_files)}")
            test_results.append(("PlantUML Generation", True))
        else:
            print("❌ No PlantUML files created")
            test_results.append(("PlantUML Generation", False))
    else:
        print("❌ PlantUML output directory not created")
        test_results.append(("PlantUML Generation", False))
    
    # 5. CLI test
    print("\n🛠️ Testing: CLI Tools")
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
        success = run_command(cmd, "CLI Analysis")
        test_results.append(("CLI Analysis", success))
    
    # Summary
    print("\n" + "=" * 50)
    print("QUICK TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nPassed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL QUICK TESTS PASSED!")
        return 0
    else:
        print("❌ SOME QUICK TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())