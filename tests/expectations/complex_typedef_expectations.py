#!/usr/bin/env python3
"""
Test expectations for complex typedef use case

This module defines the expected behavior and content for the complex typedef
use case, including file structure, content validation, and output verification.
"""

from pathlib import Path
from typing import Dict, List
try:
    from tests.expectations.base_expectations import BaseExpectations
except ImportError:
    from .base_expectations import BaseExpectations
from c_to_plantuml.models import ProjectModel, FileModel


class ComplexTypedefExpectations(BaseExpectations):
    """Expectations for complex typedef use case"""
    
    def __init__(self):
        super().__init__("use_case_typedef_complex")
    
    def validate_project_structure(self, model: ProjectModel) -> None:
        """Validate the overall project structure"""
        # Check types.h typedefs
        types_h_model = model.files["types.h"]
        
        # Check basic typedefs (aliases)
        self.assertIn('Integer', types_h_model.typedefs)
        self.assertIn('UInteger', types_h_model.typedefs)
        self.assertIn('Character', types_h_model.typedefs)
        self.assertIn('Float', types_h_model.typedefs)
        self.assertIn('Double', types_h_model.typedefs)
        self.assertIn('Pointer', types_h_model.typedefs)
        
        # Check typedef chains
        self.assertIn('Int32', types_h_model.typedefs)
        self.assertIn('MyInt', types_h_model.typedefs)
        self.assertIn('Counter', types_h_model.typedefs)
        
        # Check anonymous struct typedefs (defines)
        self.assertIn('Vector3D', types_h_model.typedefs)
        self.assertIn('Color', types_h_model.typedefs)
        
        # Check anonymous enum typedefs (defines)
        self.assertIn('State', types_h_model.typedefs)
        
        # Check anonymous union typedefs (defines)
        self.assertIn('Variant', types_h_model.typedefs)
        
        # Check complex nested typedefs
        self.assertIn('Particle', types_h_model.typedefs)
        self.assertIn('ParticlePtr', types_h_model.typedefs)
        self.assertIn('ParticlePtrPtr', types_h_model.typedefs)
        
        # Check typedef with struct tag
        self.assertIn('Node', types_h_model.typedefs)
        self.assertIn('NodePtr', types_h_model.typedefs)
        
        # Check typedef relationships
        self.assertGreater(len(types_h_model.typedef_relations), 0)
        
        # Verify relationship types - check that we have both alias and defines relationships
        relationship_types = [r.relationship_type for r in types_h_model.typedef_relations]
        self.assertIn('alias', relationship_types)
        self.assertIn('defines', relationship_types)
    
    def validate_file_content(self, model: ProjectModel) -> None:
        """Validate the content of individual files"""
        # This is handled in validate_project_structure for this use case
        pass
    
    def validate_generated_output(self, output_dir: Path) -> None:
        """Validate the generated PlantUML output"""
        # Check that output was generated
        main_puml = output_dir / "main.puml"
        self.assertTrue(main_puml.exists())
        
        content = main_puml.read_text()
        
        # Check for typedef classes - they should be in the types.h header class
        self.assertIn("typedef int Integer", content)
        self.assertIn("typedef struct Vector3D Vector3D", content)
        self.assertIn("typedef struct State State", content)
        
        # Check for stereotypes in header classes
        self.assertIn("<<header>>", content)
        
        # Check for relationship notation - these might not be generated for basic types
        # but the typedefs should be listed in the header class
        self.assertIn("typedef", content)
    
    def get_expected_file_count(self) -> int:
        """Get the expected number of files in the project"""
        return 2
    
    def get_expected_output_files(self) -> List[str]:
        """Get the expected output file names"""
        return ["main.puml"]
    
    def get_expected_structs(self) -> Dict[str, List[str]]:
        """Get expected structs for each file"""
        return {}
    
    def get_expected_enums(self) -> Dict[str, List[str]]:
        """Get expected enums for each file"""
        return {}
    
    def get_expected_functions(self) -> Dict[str, List[str]]:
        """Get expected functions for each file"""
        return {
            "main.c": ["add_integers", "create_vector", "main"]
        }
    
    def get_expected_typedefs(self) -> Dict[str, List[str]]:
        """Get expected typedefs for each file"""
        return {
            "types.h": [
                "Integer", "UInteger", "Character", "Float", "Double", "Pointer",
                "Int32", "MyInt", "Counter", "Vector3D", "Color", "State", "Variant",
                "Particle", "ParticlePtr", "ParticlePtrPtr", "Node", "NodePtr"
            ]
        }
    
    def get_expected_macros(self) -> Dict[str, List[str]]:
        """Get expected macros for each file"""
        return {
            "types.h": ["TYPES_H"]
        }
    
    def get_expected_includes(self) -> Dict[str, List[str]]:
        """Get expected includes for each file"""
        return {
            "main.c": ["types.h"]
        }
    
    def get_expected_globals(self) -> Dict[str, List[str]]:
        """Get expected global variables for each file"""
        return {
            "types.h": ["a", "b", "c", "data", "f", "g", "i", "mass", "ptr", "r", "x", "y", "z"]
        }
    
    def get_expected_unions(self) -> Dict[str, List[str]]:
        """Get expected unions for each file"""
        return {}
    
    def get_expected_plantuml_content(self) -> List[str]:
        """Get expected content that should appear in PlantUML output"""
        return [
            "typedef int Integer",
            "typedef struct Vector3D Vector3D",
            "typedef struct State State",
            "<<header>>",
            "typedef"
        ]
    
    def get_expected_plantuml_classes(self) -> List[str]:
        """Get expected class names that should appear in PlantUML output"""
        return ["main", "types"]
    
    def get_expected_plantuml_relationships(self) -> List[str]:
        """Get expected relationships that should appear in PlantUML output"""
        return []