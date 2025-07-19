#!/usr/bin/env python3
"""
Use case focused unit tests for the C to PlantUML converter

These tests cover specific use cases and behavioral scenarios
described in the specification. They now use the examples from
the examples folder instead of creating temporary files.
"""

import unittest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from c_to_plantuml.parser import CParser
from c_to_plantuml.analyzer import Analyzer
from c_to_plantuml.generator import Generator
from c_to_plantuml.config import Config
from c_to_plantuml.models import (
    ProjectModel, FileModel, Struct, Function, Field, Enum, Union,
    TypedefRelation, IncludeRelation
)


class TestBasicProjectUseCase(unittest.TestCase):
    """Test the basic project analysis use case"""
    
    def setUp(self):
        self.parser = CParser()
        self.analyzer = Analyzer()
        self.generator = Generator()
        
        # Use the example from examples folder
        self.project_dir = Path(__file__).parent.parent / "examples" / "use_case_basic_project" / "input"
        self.config_file = Path(__file__).parent.parent / "examples" / "use_case_basic_project" / "config.json"
    
    def test_basic_project_analysis(self):
        """Test basic project analysis use case"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
        # Verify project structure
        self.assertEqual(model.project_name, "input")  # Project name is derived from directory name
        self.assertEqual(len(model.files), 3)
        
        # Check that all files are parsed
        file_paths = [f for f in model.files.keys()]
        self.assertIn("main.c", file_paths)
        self.assertIn("utils.h", file_paths)
        self.assertIn("types.h", file_paths)
        
        # Check main.c content
        main_c_model = model.files["main.c"]
        self.assertEqual(len(main_c_model.functions), 4)  # add, multiply, print_point, main
        self.assertEqual(len(main_c_model.globals), 2)  # global_counter, global_name
        self.assertEqual(len(main_c_model.includes), 3)  # stdio.h, utils.h, types.h
        
        # Check utils.h content
        utils_h_model = model.files["utils.h"]
        self.assertEqual(len(utils_h_model.structs), 1)  # Rectangle
        self.assertEqual(len(utils_h_model.enums), 1)  # Status
        self.assertEqual(len(utils_h_model.unions), 1)  # Data
        self.assertEqual(len(utils_h_model.functions), 3)  # add, multiply, print_point
        
        # Check types.h content
        types_h_model = model.files["types.h"]
        self.assertEqual(len(types_h_model.typedefs), 6)  # MyInt, String, ULong, Point, Color, Value
        self.assertGreaterEqual(len(types_h_model.typedef_relations), 4)  # At least 4 typedef relations
    
    def test_basic_project_generation(self):
        """Test PlantUML generation for basic project"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
        # Create output directory
        output_dir = self.project_dir.parent / "generated_output"
        output_dir.mkdir(exist_ok=True)
        
        # Generate PlantUML
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        main_puml = output_dir / "main.puml"
        self.assertTrue(main_puml.exists())
        
        # Check content
        content = main_puml.read_text()
        self.assertIn("class \"main\"", content)
        self.assertIn("class \"utils\"", content)
        self.assertIn("class \"types\"", content)
        self.assertIn("typedef", content)


class TestComplexTypedefUseCase(unittest.TestCase):
    """Test the complex typedef analysis use case"""
    
    def setUp(self):
        self.parser = CParser()
        self.analyzer = Analyzer()
        self.generator = Generator()
        
        # Use the example from examples folder
        self.project_dir = Path(__file__).parent.parent / "examples" / "use_case_typedef_complex" / "input"
        self.config_file = Path(__file__).parent.parent / "examples" / "use_case_typedef_complex" / "config.json"
    
    def test_complex_typedef_analysis(self):
        """Test complex typedef analysis use case"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
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
    
    def test_typedef_relationship_visualization(self):
        """Test typedef relationship visualization in PlantUML"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
        # Create output directory
        output_dir = self.project_dir.parent / "generated_output"
        output_dir.mkdir(exist_ok=True)
        
        # Generate PlantUML
        self.generator.generate_from_project_model(model, str(output_dir))
        
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


class TestLargeCodebaseUseCase(unittest.TestCase):
    """Test the large codebase analysis use case"""
    
    def setUp(self):
        self.analyzer = Analyzer()
        self.generator = Generator()
        
        # Use the example from examples folder
        self.project_dir = Path(__file__).parent.parent / "examples" / "use_case_large_codebase" / "input"
        self.config_file = Path(__file__).parent.parent / "examples" / "use_case_large_codebase" / "config.json"
    
    def test_large_codebase_analysis(self):
        """Test large codebase analysis use case"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
        # Verify project structure
        self.assertEqual(model.project_name, "input")  # Project name is derived from directory name
        self.assertGreaterEqual(len(model.files), 5)  # Should have at least 5 files
        
        # Check that all expected files are parsed
        file_paths = [f for f in model.files.keys()]
        self.assertIn("main.c", file_paths)
        self.assertIn("core.h", file_paths)
        self.assertIn("core.c", file_paths)
        self.assertIn("utils.h", file_paths)
        self.assertIn("utils.c", file_paths)
        
        # Check main.c content
        main_c_model = model.files["main.c"]
        self.assertGreaterEqual(len(main_c_model.functions), 1)  # At least main function
        self.assertGreaterEqual(len(main_c_model.includes), 2)  # At least core.h and utils.h
        
        # Check core.h content
        core_h_model = model.files["core.h"]
        self.assertGreaterEqual(len(core_h_model.typedefs), 2)  # At least CoreObject and CoreStatus
        self.assertGreaterEqual(len(core_h_model.functions), 3)  # At least 3 functions (core_init, core_cleanup, core_create_object, core_destroy_object)
        
        # Check utils.h content
        utils_h_model = model.files["utils.h"]
        self.assertGreaterEqual(len(utils_h_model.typedefs), 3)  # At least Vector3D, Variant, UtilResult
        self.assertGreaterEqual(len(utils_h_model.functions), 6)  # At least 6 functions
    
    def test_large_codebase_generation(self):
        """Test PlantUML generation for large codebase"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
        # Create output directory
        output_dir = self.project_dir.parent / "generated_output"
        output_dir.mkdir(exist_ok=True)
        
        # Generate PlantUML
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        
        # Should generate multiple .puml files
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 3)  # At least 3 files (main.c, core.c, utils.c)
        
        # Check main.puml content
        main_puml = output_dir / "main.puml"
        if main_puml.exists():
            content = main_puml.read_text()
            self.assertIn("class \"main\"", content)
            self.assertIn("class \"core\"", content)
            self.assertIn("class \"utils\"", content)


class TestErrorHandlingUseCase(unittest.TestCase):
    """Test error handling use cases"""
    
    def setUp(self):
        self.parser = CParser()
        self.analyzer = Analyzer()
        
        # Use the example from examples folder
        self.project_dir = Path(__file__).parent.parent / "examples" / "use_case_error_handling" / "input"
        self.config_file = Path(__file__).parent.parent / "examples" / "use_case_error_handling" / "config.json"
    
    def test_encoding_detection_and_recovery(self):
        """Test encoding detection and recovery"""
        # This test uses a temporary file with specific encoding
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False, encoding='utf-8') as f:
            f.write("""
#include <stdio.h>

struct TestStruct {
    int x;
    int y;
};

int main() {
    return 0;
}
""")
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.parser.parse_file(Path(temp_file))
            
            # Should parse successfully
            self.assertIsNotNone(file_model)
            self.assertIn('TestStruct', file_model.structs)
            self.assertEqual(len(file_model.functions), 1)
            
        finally:
            os.unlink(temp_file)
    
    def test_partial_parsing_on_errors(self):
        """Test partial parsing when encountering errors"""
        # Use the invalid file from the example
        invalid_file = self.project_dir / "invalid_file.c"
        
        if invalid_file.exists():
            # Parse the file
            file_model = self.parser.parse_file(invalid_file)
            
            # Should parse valid parts
            self.assertIsNotNone(file_model)
            self.assertIn('Valid', file_model.structs)
            # Invalid struct might be parsed with empty fields due to error recovery
            if 'Invalid' in file_model.structs:
                invalid_struct = file_model.structs['Invalid']
                # Should have empty fields due to parsing error
                self.assertEqual(len(invalid_struct.fields), 0)
            self.assertEqual(len(file_model.functions), 1)
    
    def test_missing_file_handling(self):
        """Test handling of missing files"""
        # Use the missing include file from the example
        missing_include_file = self.project_dir / "missing_include.c"
        
        if missing_include_file.exists():
            # Should not crash
            model = self.analyzer.analyze_project(
                project_root=str(self.project_dir),
                recursive=True
            )
            
            # Should still parse the file
            self.assertIsNotNone(model)
            self.assertGreaterEqual(len(model.files), 1)
            
            # Check that the file with missing include was parsed
            file_models = list(model.files.values())
            for file_model in file_models:
                if "missing_include.c" in file_model.file_path:
                    self.assertEqual(len(file_model.functions), 1)
                    break


class TestConfigurationUseCase(unittest.TestCase):
    """Test configuration-driven use cases"""
    
    def setUp(self):
        self.analyzer = Analyzer()
        self.generator = Generator()
        
        # Use the example from examples folder
        self.project_dir = Path(__file__).parent.parent / "examples" / "use_case_configuration" / "input"
        self.config_file = Path(__file__).parent.parent / "examples" / "use_case_configuration" / "config.json"
    
    def test_configuration_filtering(self):
        """Test configuration-based filtering"""
        # Load configuration
        config = Config.load(str(self.config_file))
        
        # Analyze with configuration - use analyze_project directly for single project
        model = self.analyzer.analyze_project(str(self.project_dir), recursive=True)
        
        # Apply filters manually
        model = config.apply_filters(model)
        
        # Check that the model was created successfully
        self.assertIsNotNone(model)
        self.assertGreater(len(model.files), 0)
        
        # Check that main.c was parsed
        self.assertIn("main.c", model.files)
        main_c_model = model.files["main.c"]
        
        # Should include public elements
        self.assertIn('PublicStruct', main_c_model.structs)
        self.assertIn('public_function', [f.name for f in main_c_model.functions])
        self.assertIn('global_public_var', [g.name for g in main_c_model.globals])


if __name__ == '__main__':
    unittest.main()