#!/usr/bin/env python3
"""
Test expectations for integration examples

This module defines the expected behavior and content for the integration
examples, including file structure, content validation, and output verification.
"""

from pathlib import Path
from typing import Dict, List
try:
    from tests.expectations.base_expectations import BaseExpectations
except ImportError:
    from .base_expectations import BaseExpectations
from c_to_plantuml.models import ProjectModel, FileModel


class IntegrationWorkflowExpectations(BaseExpectations):
    """Expectations for integration workflow example"""
    
    def __init__(self):
        super().__init__("use_case_integration_workflow")
    
    def validate_project_structure(self, model: ProjectModel) -> None:
        """Validate the overall project structure"""
        self.assertEqual(model.project_name, "use_case_integration_workflow")
        self.assertEqual(len(model.files), 3)  # main.c, config.h, utils.c
        
        # Check that all files are present
        file_names = list(model.files.keys())
        self.assertIn("main.c", file_names)
        self.assertIn("config.h", file_names)
        self.assertIn("utils.c", file_names)
    
    def validate_file_content(self, model: ProjectModel) -> None:
        """Validate the content of individual files"""
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
    
    def validate_generated_output(self, output_dir: Path) -> None:
        """Validate the generated PlantUML output"""
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


class ComplexExampleExpectations(BaseExpectations):
    """Expectations for complex example"""
    
    def __init__(self):
        super().__init__("use_case_complex_example")
    
    def validate_project_structure(self, model: ProjectModel) -> None:
        """Validate the overall project structure"""
        self.assertEqual(model.project_name, "use_case_complex_example")
        self.assertEqual(len(model.files), 2)  # complex_example.c, complex_example.h
    
    def validate_file_content(self, model: ProjectModel) -> None:
        """Validate the content of individual files"""
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
    
    def validate_generated_output(self, output_dir: Path) -> None:
        """Validate the generated PlantUML output"""
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)


class TypedefTestExpectations(BaseExpectations):
    """Expectations for typedef test example"""
    
    def __init__(self):
        super().__init__("use_case_typedef_test")
    
    def validate_project_structure(self, model: ProjectModel) -> None:
        """Validate the overall project structure"""
        self.assertEqual(model.project_name, "use_case_typedef_test")
        self.assertGreaterEqual(len(model.files), 3)  # typedef_test.c, typedef_test.h, sample.h
    
    def validate_file_content(self, model: ProjectModel) -> None:
        """Validate the content of individual files"""
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
    
    def validate_generated_output(self, output_dir: Path) -> None:
        """Validate the generated PlantUML output"""
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)


class SampleExpectations(BaseExpectations):
    """Expectations for sample example"""
    
    def __init__(self):
        super().__init__("use_case_sample")
    
    def validate_project_structure(self, model: ProjectModel) -> None:
        """Validate the overall project structure"""
        self.assertEqual(model.project_name, "use_case_sample")
        self.assertEqual(len(model.files), 2)  # sample.c, sample.h
    
    def validate_file_content(self, model: ProjectModel) -> None:
        """Validate the content of individual files"""
        # Check sample.c content
        c_file = model.files["sample.c"]
        self.assertIn("calculate_sum", [f.name for f in c_file.functions])
        self.assertIn("process_point", [f.name for f in c_file.functions])
        self.assertIn("main", [f.name for f in c_file.functions])
        self.assertIn("internal_helper", [f.name for f in c_file.functions])
        self.assertIn("point_t", c_file.typedefs)
        self.assertIn("system_state_t", c_file.typedefs)
        self.assertIn("MAX_SIZE", c_file.macros)
        self.assertIn("DEBUG_MODE", c_file.macros)
        self.assertIn("CALC", c_file.macros)
        
        # Check sample.h content
        h_file = model.files["sample.h"]
        self.assertIn("calculate_sum", [f.name for f in h_file.functions])
        self.assertIn("process_point", [f.name for f in h_file.functions])
        self.assertIn("PI", h_file.macros)
        self.assertIn("VERSION", h_file.macros)
        self.assertIn("MIN", h_file.macros)
        self.assertIn("MAX", h_file.macros)
    
    def validate_generated_output(self, output_dir: Path) -> None:
        """Validate the generated PlantUML output"""
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)