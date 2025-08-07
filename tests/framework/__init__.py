#!/usr/bin/env python3
"""
Unified Testing Framework for C2PUML

This package provides a unified testing framework that enforces CLI-only access
to c2puml functionality, ensuring tests validate the actual user interface.
"""

from .executor import TestExecutor, CLIResult
from .validators import ModelValidator, PlantUMLValidator, OutputValidator, FileValidator, CLIValidator
from .base import UnifiedTestCase
from .data_loader import TestDataLoader
from .assertion_processor import AssertionProcessor

__all__ = [
    'TestExecutor',
    'CLIResult',
    'ModelValidator',
    'PlantUMLValidator',
    'OutputValidator',
    'FileValidator',
    'CLIValidator',
    'UnifiedTestCase',
    'TestDataLoader',
    'AssertionProcessor',
]