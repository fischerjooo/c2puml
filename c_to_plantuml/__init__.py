"""
C to PlantUML Converter

A high-performance Python package for converting C/C++ code to PlantUML diagrams.
Features optimized parsing, JSON model generation, and comprehensive PlantUML output.
"""

__version__ = "1.1.0"
__author__ = "C to PlantUML Team"

# Import main functionality
from .parsers.c_parser import CParser
from .project_analyzer import ProjectAnalyzer
from .generators.plantuml_generator import PlantUMLGenerator
from .models.project_model import ProjectModel, FileModel

# Main classes and functions for public API
__all__ = [
    'CParser',
    'ProjectAnalyzer', 
    'PlantUMLGenerator',
    'ProjectModel',
    'FileModel'
] 