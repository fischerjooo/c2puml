#!/usr/bin/env python3
"""
Unified Testing Framework for C2PUML

This package provides a comprehensive testing framework for C2PUML tests,
including CLI execution, YAML-based test data, and validation components.
"""

from .base import UnifiedTestCase, TestResult
from .data_loader import TestDataLoader
from .executor import TestExecutor, CLIResult
from .validators_processor import ValidatorsProcessor
from .validators import (
    ModelValidator, 
    PlantUMLValidator, 
    OutputValidator, 
    FileValidator, 
    CLIValidator,
    TestError
)

__all__ = [
    'UnifiedTestCase',
    'TestResult', 
    'TestDataLoader',
    'TestExecutor',
    'CLIResult',
    'ValidatorsProcessor',
    'ModelValidator',
    'PlantUMLValidator', 
    'OutputValidator',
    'FileValidator',
    'CLIValidator',
    'TestError'
]