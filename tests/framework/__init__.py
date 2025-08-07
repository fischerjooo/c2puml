"""
Unified Testing Framework for c2puml

This package provides a unified testing framework that enforces CLI-only access
to c2puml functionality, ensuring tests validate the actual user interface.
"""

from .executor import TestExecutor, CLIResult
from .input_factory import TestInputFactory
from .validators import ModelValidator, PlantUMLValidator, OutputValidator, FileValidator
from .base import UnifiedTestCase
from .assertion_processor import AssertionProcessor
from .data_loader import TestDataLoader

__all__ = [
    'TestExecutor',
    'CLIResult', 
    'TestInputFactory',
    'ModelValidator',
    'PlantUMLValidator',
    'OutputValidator',
    'FileValidator',
    'UnifiedTestCase',
    'AssertionProcessor',
    'TestDataLoader'
]