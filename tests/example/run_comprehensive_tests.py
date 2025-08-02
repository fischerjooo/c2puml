#!/usr/bin/env python3
"""
Comprehensive Test Runner for C2PlantUML

This script demonstrates the refactored test-example.py with:
1. JSON-based configuration for test expectations
2. Extensive deep content analysis of generated puml files
3. Enhanced validation capabilities
4. Modular and maintainable test structure

Usage:
    python3 run_comprehensive_tests.py [--verbose] [--deep-only] [--standard-only]

Features:
- Standard PUML validation with JSON configuration
- Deep content analysis with extensive checks
- Include filtering validation tests
- Comprehensive reporting and error handling
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=False, text=True, cwd=Path.cwd())
        end_time = time.time()
        
        if result.returncode == 0:
            print(f"\n✅ {description} - PASSED ({end_time - start_time:.2f}s)")
            return True
        else:
            print(f"\n❌ {description} - FAILED ({end_time - start_time:.2f}s)")
            return False
            
    except Exception as e:
        print(f"\n💥 {description} - ERROR: {e}")
        return False


def main():
    """Main test runner function."""
    print("🚀 C2PlantUML Comprehensive Test Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("tests/example/test-example.py").exists():
        print("❌ Error: test-example.py not found. Please run from the project root.")
        sys.exit(1)
    
    if not Path("tests/example/test-example.json").exists():
        print("❌ Error: test-example.json not found. Please run from the project root.")
        sys.exit(1)
    
    # Parse command line arguments
    verbose = "--verbose" in sys.argv
    deep_only = "--deep-only" in sys.argv
    standard_only = "--standard-only" in sys.argv
    
    if verbose:
        print("📝 Verbose mode enabled")
    
    # Test results tracking
    test_results = []
    
    # 1. Standard PUML Validation (with JSON configuration)
    if not deep_only:
        success = run_command(
            ["python3", "tests/example/test-example.py"],
            "Standard PUML Validation with JSON Configuration"
        )
        test_results.append(("Standard Validation", success))
    
    # 2. Deep Content Analysis
    if not standard_only:
        success = run_command(
            ["python3", "tests/example/test-example.py", "--deep-analysis"],
            "Deep Content Analysis of Generated PUML Files"
        )
        test_results.append(("Deep Analysis", success))
    
    # 3. Include Filtering Tests (if configuration files exist)
    if Path("tests/example/config_network_filtering.json").exists():
        success = run_command(
            ["python3", "tests/example/test-example.py", "--test-include-filtering"],
            "Include Filtering Validation Tests"
        )
        test_results.append(("Include Filtering", success))
    else:
        print("\n⚠️  Skipping Include Filtering Tests (config files not found)")
        test_results.append(("Include Filtering", True))  # Skip, not fail
    
    # 4. Validate JSON Configuration Structure
    print(f"\n{'='*60}")
    print("🔍 Validating JSON Configuration Structure")
    print(f"{'='*60}")
    
    try:
        import json
        with open("tests/example/test-example.json", 'r') as f:
            config = json.load(f)
        
        # Check required sections
        required_sections = ["file_expectations", "validation_rules", "puml_content_validation"]
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            print(f"❌ Missing required JSON sections: {missing_sections}")
            test_results.append(("JSON Structure", False))
        else:
            print("✅ JSON configuration structure is valid")
            test_results.append(("JSON Structure", True))
            
            # Show configuration summary
            file_count = len(config.get("file_expectations", {}))
            deep_checks = len(config.get("puml_content_validation", {}).get("deep_content_analysis", {}))
            print(f"   📁 Configured files: {file_count}")
            print(f"   🔬 Deep analysis checks: {deep_checks}")
            
    except Exception as e:
        print(f"❌ JSON configuration validation failed: {e}")
        test_results.append(("JSON Structure", False))
    
    # 5. Check Generated PUML Files
    print(f"\n{'='*60}")
    print("📊 Generated PUML Files Analysis")
    print(f"{'='*60}")
    
    puml_dir = Path("artifacts/output_example")
    if puml_dir.exists():
        puml_files = list(puml_dir.glob("*.puml"))
        png_files = list(puml_dir.glob("*.png"))
        
        print(f"📄 PUML files: {len(puml_files)}")
        print(f"🖼️  PNG files: {len(png_files)}")
        
        if puml_files:
            print("\n📋 PUML Files:")
            for puml_file in sorted(puml_files):
                size = puml_file.stat().st_size
                print(f"   • {puml_file.name} ({size} bytes)")
        
        test_results.append(("PUML Files", len(puml_files) > 0))
    else:
        print("❌ No PUML files found")
        test_results.append(("PUML Files", False))
    
    # Final Results Summary
    print(f"\n{'='*60}")
    print("📊 COMPREHENSIVE TEST RESULTS")
    print(f"{'='*60}")
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n📈 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The refactored test suite is working correctly.")
        print("\n✨ Key Improvements:")
        print("   • JSON-based configuration for maintainable test expectations")
        print("   • Extensive deep content analysis of generated PUML files")
        print("   • Modular validation architecture")
        print("   • Enhanced error reporting and debugging")
        print("   • Comprehensive coverage of PUML model validation")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())