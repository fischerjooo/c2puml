#!/usr/bin/env python3
"""
Unified Test Case Base Class

This module provides the UnifiedTestCase base class that all c2puml tests
should inherit from, providing common setup, teardown, and component initialization.
"""

import os
import sys
import unittest
import tempfile
import json
import shutil
from typing import Dict, Any, List

from .executor import TestExecutor, CLIResult
from .data_loader import TestDataLoader
from .assertion_processor import AssertionProcessor
from .validators import ModelValidator, PlantUMLValidator, OutputValidator, FileValidator, CLIValidator


class UnifiedTestCase(unittest.TestCase):
    """
    Base class for all tests using the unified testing framework.
    
    This class provides:
    - Automatic setup of TestExecutor, TestDataLoader, and validators
    - Component initialization for all framework components
    - Standardized test output management
    - Integration with the unified testing framework components
    """
    
    def setUp(self):
        """Set up test environment"""
        # Initialize framework components
        self.executor = TestExecutor()
        self.data_loader = TestDataLoader()
        self.assertion_processor = AssertionProcessor()
        
        # Initialize validators
        self.model_validator = ModelValidator()
        self.puml_validator = PlantUMLValidator()
        self.output_validator = OutputValidator()
        self.file_validator = FileValidator()
        self.cli_validator = CLIValidator()
        
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Test metadata
        self.test_name = self.__class__.__name__
        self.test_method = self._testMethodName
    
    def tearDown(self):
        """Clean up after each test"""
        # Note: temp_dir is NOT automatically cleaned to preserve output for debugging
        pass