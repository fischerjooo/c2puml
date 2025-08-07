"""
C2PUML Unified Testing Framework

This package provides a unified testing framework for c2puml that ensures
all tests use only the public CLI interface, maintaining clear boundaries
between test and application code.
"""

from .executor import TestExecutor, CLIResult, TimedCLIResult, MemoryCLIResult
from .input_factory import TestInputFactory
from .validators import ModelValidator, PlantUMLValidator, OutputValidator, FileValidator

__all__ = [
    'TestExecutor',
    'CLIResult',
    'TimedCLIResult',
    'MemoryCLIResult',
    'TestInputFactory',
    'ModelValidator',
    'PlantUMLValidator',
    'OutputValidator',
    'FileValidator'
]