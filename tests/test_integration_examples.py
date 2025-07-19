#!/usr/bin/env python3
"""
Integration tests for complete C to PlantUML workflow using examples

These tests use the examples from the examples folder instead of creating
temporary files, making them more reliable and maintainable.
"""

import unittest
import os
import json
import shutil
from pathlib import Path
from c_to_plantuml.analyzer import Analyzer
from c_to_plantuml.generator import Generator
from c_to_plantuml.config import Config
from c_to_plantuml.models import ProjectModel


class TestIntegrationExamples(unittest.TestCase):
    """Integration tests for complete workflow using examples"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = Analyzer()
        self.generator = Generator()
        
        # Use examples from the examples folder
        self.examples_dir = Path(__file__).parent.parent / "examples"
    
    def test_integration_workflow_example(self):
        """Test complete workflow using the integration workflow example"""
        example_dir = self.examples_dir / "use_case_integration_workflow"
        project_dir = example_dir / "input"
        config_file = example_dir / "config.json"
        
        # Load configuration
        config = Config.load(str(config_file))
        
        # Step 1: Analyze project and generate model
        model = self.analyzer.analyze_with_config(config)
        
        # Verify model structure
        self.assertEqual(model.project_name, "use_case_integration_workflow")
        self.assertEqual(len(model.files), 3)  # main.c, config.h, utils.c
        
        # Check that all files are present
        file_names = list(model.files.keys())
        self.assertIn("main.c", file_names)
        self.assertIn("config.h", file_names)
        self.assertIn("utils.c", file_names)
        
        # Check main.c content
        main_file = model.files["main.c"]
        self.assertIn("Person", main_file.structs)
        self.assertIn("Config", main_file.structs)
        self.assertIn("Status", main_file.enums)
        self.assertIn("main", [f.name for f in main_file.functions])
        self.assertIn("process_data", [f.name for f in main_file.functions])
        self.assertIn("calculate", [f.name for f in main_file.functions])
        self.assertIn("stdio.h", main_file.includes)
        self.assertIn("stdlib.h", main_file.includes)
        self.assertIn("config.h", main_file.includes)
        self.assertIn("MAX_SIZE", main_file.macros)
        self.assertIn("DEBUG_MODE", main_file.macros)
        self.assertIn("Integer", main_file.typedefs)
        self.assertIn("String", main_file.typedefs)
        
        # Check config.h content
        config_file_model = model.files["config.h"]
        self.assertIn("User", config_file_model.typedefs)  # This should be parsed as a typedef struct
        self.assertIn("Color", config_file_model.enums)
        self.assertIn("init_config", [f.name for f in config_file_model.functions])
        self.assertIn("validate_config", [f.name for f in config_file_model.functions])
        self.assertIn("CONFIG_VERSION", config_file_model.macros)
        self.assertIn("DEFAULT_TIMEOUT", config_file_model.macros)
        
        # Check utils.c content
        utils_file = model.files["utils.c"]
        self.assertIn("init_config", [f.name for f in utils_file.functions])
        self.assertIn("validate_config", [f.name for f in utils_file.functions])
        self.assertIn("helper_function", [f.name for f in utils_file.functions])
        self.assertIn("debug_log", [f.name for f in utils_file.functions])
        
        # Save model
        model_path = example_dir / "test_model.json"
        model.save(str(model_path))
        self.assertTrue(model_path.exists())
        
        # Step 3: Generate PlantUML diagrams
        output_dir = example_dir / "test_output"
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)
        
        # Check main.puml content
        main_puml = output_dir / "main.puml"
        self.assertTrue(main_puml.exists())
        
        content = main_puml.read_text()
        self.assertIn("@startuml main", content)
        self.assertIn("class \"main\"", content)
        self.assertIn("class \"config\"", content)
        # utils.c is not included by main.c, so it won't appear in the diagram
        
        # Cleanup
        if model_path.exists():
            model_path.unlink()
        if output_dir.exists():
            shutil.rmtree(output_dir)
    
    def test_complex_example_workflow(self):
        """Test complete workflow using the complex example"""
        example_dir = self.examples_dir / "use_case_complex_example"
        project_dir = example_dir / "input"
        config_file = example_dir / "config.json"
        
        # Load configuration
        config = Config.load(str(config_file))
        
        # Analyze project
        model = self.analyzer.analyze_with_config(config)
        
        # Verify model structure
        self.assertEqual(model.project_name, "use_case_complex_example")
        self.assertEqual(len(model.files), 2)  # complex_example.c, complex_example.h
        
        # Check complex_example.c content
        c_file = model.files["complex_example.c"]
        self.assertIn("event_handler_t", c_file.typedefs)
        self.assertIn("data_value_t", c_file.typedefs)
        self.assertIn("event_type_t", c_file.typedefs)
        self.assertIn("create_entity", [f.name for f in c_file.functions])
        self.assertIn("update_entity_position", [f.name for f in c_file.functions])
        self.assertIn("set_entity_color", [f.name for f in c_file.functions])
        self.assertIn("register_event_handler", [f.name for f in c_file.functions])
        self.assertIn("trigger_event", [f.name for f in c_file.functions])
        self.assertIn("BUFFER_SIZE", c_file.macros)
        self.assertIn("LOG_LEVEL_ERROR", c_file.macros)
        self.assertIn("LOG_LEVEL_INFO", c_file.macros)
        
        # Check complex_example.h content
        h_file = model.files["complex_example.h"]
        self.assertIn("MAX_ENTITIES", h_file.macros)
        self.assertIn("ENTITY_NAME_LENGTH", h_file.macros)
        self.assertIn("create_entity", [f.name for f in h_file.functions])
        self.assertIn("update_entity_position", [f.name for f in h_file.functions])
        self.assertIn("set_entity_color", [f.name for f in h_file.functions])
        self.assertIn("register_event_handler", [f.name for f in h_file.functions])
        self.assertIn("trigger_event", [f.name for f in h_file.functions])
        
        # Generate diagrams
        output_dir = example_dir / "test_output"
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)
        
        # Cleanup
        if output_dir.exists():
            shutil.rmtree(output_dir)
    
    def test_typedef_test_workflow(self):
        """Test complete workflow using the typedef test example"""
        example_dir = self.examples_dir / "use_case_typedef_test"
        project_dir = example_dir / "input"
        config_file = example_dir / "config.json"
        
        # Load configuration
        config = Config.load(str(config_file))
        
        # Analyze project
        model = self.analyzer.analyze_with_config(config)
        
        # Verify model structure
        self.assertEqual(model.project_name, "use_case_typedef_test")
        self.assertGreaterEqual(len(model.files), 3)  # typedef_test.c, typedef_test.h, sample.h
        
        # Check typedef_test.c content
        c_file = model.files["typedef_test.c"]
        self.assertIn("process_buffer", [f.name for f in c_file.functions])
        self.assertIn("my_callback", [f.name for f in c_file.functions])
        self.assertIn("main", [f.name for f in c_file.functions])
        
        # Check typedef_test.h content
        h_file = model.files["typedef_test.h"]
        self.assertIn("MyLen", h_file.typedefs)
        self.assertIn("MyInt", h_file.typedefs)
        self.assertIn("MyString", h_file.typedefs)
        self.assertIn("MyBuffer", h_file.typedefs)
        self.assertIn("MyCallback", h_file.typedefs)
        self.assertIn("MyComplex", h_file.typedefs)
        self.assertIn("MyComplexPtr", h_file.typedefs)
        self.assertIn("Color_t", h_file.typedefs)
        self.assertIn("Status_t", h_file.typedefs)
        self.assertIn("Point_t", h_file.typedefs)
        self.assertIn("NamedStruct_t", h_file.typedefs)
        self.assertIn("Number_t", h_file.typedefs)
        self.assertIn("NamedUnion_t", h_file.typedefs)
        
        # Generate diagrams
        output_dir = example_dir / "test_output"
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)
        
        # Cleanup
        if output_dir.exists():
            shutil.rmtree(output_dir)
    
    def test_sample_workflow(self):
        """Test complete workflow using the sample example"""
        example_dir = self.examples_dir / "use_case_sample"
        project_dir = example_dir / "input"
        config_file = example_dir / "config.json"
        
        # Load configuration
        config = Config.load(str(config_file))
        
        # Analyze project
        model = self.analyzer.analyze_with_config(config)
        
        # Verify model structure
        self.assertEqual(model.project_name, "use_case_sample")
        self.assertEqual(len(model.files), 2)  # sample.c, sample.h
        
        # Check sample.c content
        c_file = model.files["sample.c"]
        self.assertIn("point_t", c_file.typedefs)
        self.assertIn("system_state_t", c_file.typedefs)
        self.assertIn("calculate_sum", [f.name for f in c_file.functions])
        self.assertIn("process_point", [f.name for f in c_file.functions])
        self.assertIn("main", [f.name for f in c_file.functions])
        self.assertIn("internal_helper", [f.name for f in c_file.functions])
        self.assertIn("MAX_SIZE", c_file.macros)
        self.assertIn("DEBUG_MODE", c_file.macros)
        self.assertIn("CALC", c_file.macros)
        
        # Check sample.h content
        h_file = model.files["sample.h"]
        self.assertIn("PI", h_file.macros)
        self.assertIn("VERSION", h_file.macros)
        self.assertIn("MIN", h_file.macros)
        self.assertIn("MAX", h_file.macros)
        self.assertIn("calculate_sum", [f.name for f in h_file.functions])
        self.assertIn("process_point", [f.name for f in h_file.functions])
        
        # Generate diagrams
        output_dir = example_dir / "test_output"
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)
        
        # Cleanup
        if output_dir.exists():
            shutil.rmtree(output_dir)
    
    def test_workflow_with_filtering_example(self):
        """Test workflow with filtering using the configuration example"""
        example_dir = self.examples_dir / "use_case_configuration"
        project_dir = example_dir / "input"
        config_file = example_dir / "config.json"
        
        # Load configuration
        config = Config.load(str(config_file))
        
        # Analyze project
        model = self.analyzer.analyze_with_config(config)
        
        # Verify that filtering worked
        self.assertEqual(model.project_name, "use_case_configuration")
        
        # Check main.c content after filtering
        main_file = model.files["main.c"]
        
        # Should include public elements
        self.assertIn("PublicStruct", main_file.structs)
        self.assertIn("public_function", [f.name for f in main_file.functions])
        self.assertIn("global_public_var", [g.name for g in main_file.globals])
        
        # Should exclude internal elements
        self.assertNotIn("InternalStruct", main_file.structs)
        self.assertNotIn("internal_function", [f.name for f in main_file.functions])
        self.assertNotIn("global_internal_var", [g.name for g in main_file.globals])
        
        # Generate diagrams
        output_dir = example_dir / "test_output"
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)
        
        # Cleanup
        if output_dir.exists():
            shutil.rmtree(output_dir)


if __name__ == '__main__':
    unittest.main()