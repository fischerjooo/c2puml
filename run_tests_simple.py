#!/usr/bin/env python3
"""
Simple Test Runner for C to PlantUML Converter
Alternative runner using unittest.main() for maximum compatibility
"""

import sys
import os
import unittest

# Get the script directory and change to it
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the current directory to the path
sys.path.insert(0, script_dir)

if __name__ == "__main__":
    print("🧪 Running C to PlantUML Converter Tests (Simple Mode)")
    print("=" * 60)
    print(f"Working directory: {os.getcwd()}")
    
    # Use unittest.main() to discover and run tests
    # This automatically discovers tests in the current directory and subdirectories
    unittest.main(
        module=None,
        argv=['run_tests_simple.py', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v'],
        exit=False
    )