#!/usr/bin/env python3

import logging
import sys
import os
sys.path.insert(0, '.')

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

from tests.feature.test_include_dependency_processing import TestIncludeDependencyProcessing

# Create test instance
test = TestIncludeDependencyProcessing()
test.setUp()

try:
    # Run the failing test
    test.test_basic_include_dependency_processing()
except Exception as e:
    print(f"Test failed: {e}")
finally:
    test.tearDown()