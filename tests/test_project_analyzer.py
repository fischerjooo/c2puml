#!/usr/bin/env python3
"""
Unit tests for the project analyzer and model functionality
"""

import unittest
import os
import sys
import tempfile
import json
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from c_to_plantuml.project_analyzer import ProjectAnalyzer, load_config_and_analyze
from c_to_plantuml.models.project_model import ProjectModel, FileModel
from c_to_plantuml.generators.model_plantuml_generator import ModelPlantUMLGenerator, generate_plantuml_from_json

class TestProjectAnalyzer(unittest.TestCase):
    """Test cases for the ProjectAnalyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ProjectAnalyzer()
        self.test_files_dir = Path(__file__).parent / "test_files"
        
        # Create a temporary directory for outputs
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_analyze_single_file_project(self):
        """Test analyzing a project with a single file"""
        if not (self.test_files_dir / "sample.c").exists():
            self.skipTest("sample.c test file not found")
        
        project_roots = [str(self.test_files_dir)]
        model = self.analyzer.analyze_project(
            project_roots=project_roots,
            project_name="Test_Project",
            recursive=False
        )
        
        # Check model structure
        self.assertEqual(model.project_name, "Test_Project")
        self.assertEqual(model.project_roots, project_roots)
        self.assertGreater(len(model.files), 0)
        
        # Check that sample.c was analyzed
        sample_files = [f for f in model.files.keys() if "sample.c" in f]
        self.assertGreater(len(sample_files), 0)
        
        # Check file model content
        sample_file_path = sample_files[0]
        file_model = model.files[sample_file_path]
        self.assertIsInstance(file_model, FileModel)
        self.assertGreater(len(file_model.functions), 0)
        self.assertGreater(len(file_model.macros), 0)
    
    def test_model_json_serialization(self):
        """Test JSON serialization and deserialization of models"""
        if not (self.test_files_dir / "sample.c").exists():
            self.skipTest("sample.c test file not found")
        
        # Create a model
        project_roots = [str(self.test_files_dir)]
        original_model = self.analyzer.analyze_project(
            project_roots=project_roots,
            project_name="Serialization_Test"
        )
        
        # Save to JSON
        json_path = self.temp_dir / "test_model.json"
        self.analyzer.save_model_to_json(original_model, str(json_path))
        
        # Check that file was created
        self.assertTrue(json_path.exists())
        
        # Load from JSON
        loaded_model = ProjectModel.load_from_json(str(json_path))
        
        # Compare models
        self.assertEqual(original_model.project_name, loaded_model.project_name)
        self.assertEqual(original_model.project_roots, loaded_model.project_roots)
        self.assertEqual(len(original_model.files), len(loaded_model.files))
        
        # Check that file models are equivalent
        for file_path in original_model.files:
            self.assertIn(file_path, loaded_model.files)
            orig_file = original_model.files[file_path]
            loaded_file = loaded_model.files[file_path]
            self.assertEqual(orig_file.file_path, loaded_file.file_path)
            self.assertEqual(len(orig_file.functions), len(loaded_file.functions))
    
    def test_analyze_and_save(self):
        """Test the convenience method analyze_and_save"""
        if not (self.test_files_dir / "sample.c").exists():
            self.skipTest("sample.c test file not found")
        
        json_path = self.temp_dir / "analyze_and_save_test.json"
        
        model = self.analyzer.analyze_and_save(
            project_roots=[str(self.test_files_dir)],
            output_path=str(json_path),
            project_name="Convenience_Test"
        )
        
        # Check that file was created
        self.assertTrue(json_path.exists())
        
        # Check that model is returned
        self.assertIsInstance(model, ProjectModel)
        self.assertEqual(model.project_name, "Convenience_Test")
    
    def test_file_filtering(self):
        """Test C file prefix filtering"""
        if not (self.test_files_dir / "sample.c").exists():
            self.skipTest("test files not found")
        
        # Test with prefix filter that should match
        model = self.analyzer.analyze_project(
            project_roots=[str(self.test_files_dir)],
            project_name="Filter_Test",
            c_file_prefixes=["sample"]
        )
        
        # Should find sample.c
        sample_files = [f for f in model.files.keys() if "sample.c" in f]
        self.assertGreater(len(sample_files), 0)
        
        # Test with prefix filter that shouldn't match anything
        model_empty = self.analyzer.analyze_project(
            project_roots=[str(self.test_files_dir)],
            project_name="Empty_Filter_Test",
            c_file_prefixes=["nonexistent"]
        )
        
        # Should find no files
        self.assertEqual(len(model_empty.files), 0)
    
    def test_recursive_scanning(self):
        """Test recursive vs non-recursive scanning"""
        # Create a temporary nested structure
        nested_dir = self.temp_dir / "nested"
        nested_dir.mkdir()
        
        # Copy test file to nested directory
        if (self.test_files_dir / "sample.c").exists():
            shutil.copy2(self.test_files_dir / "sample.c", nested_dir / "nested_sample.c")
        else:
            # Create a simple test file
            with open(nested_dir / "nested_sample.c", 'w') as f:
                f.write("int nested_func() { return 42; }")
        
        # Test recursive scanning
        model_recursive = self.analyzer.analyze_project(
            project_roots=[str(self.temp_dir)],
            project_name="Recursive_Test",
            recursive=True
        )
        
        # Test non-recursive scanning
        model_non_recursive = self.analyzer.analyze_project(
            project_roots=[str(self.temp_dir)],
            project_name="NonRecursive_Test",
            recursive=False
        )
        
        # Recursive should find the nested file, non-recursive shouldn't
        nested_files_recursive = [f for f in model_recursive.files.keys() if "nested_sample.c" in f]
        nested_files_non_recursive = [f for f in model_non_recursive.files.keys() if "nested_sample.c" in f]
        
        self.assertGreater(len(nested_files_recursive), 0)
        self.assertEqual(len(nested_files_non_recursive), 0)

class TestModelPlantUMLGenerator(unittest.TestCase):
    """Test cases for the ModelPlantUMLGenerator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = ModelPlantUMLGenerator()
        self.test_files_dir = Path(__file__).parent / "test_files"
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_plantuml_generation_from_model(self):
        """Test PlantUML generation from a project model"""
        if not (self.test_files_dir / "sample.c").exists():
            self.skipTest("sample.c test file not found")
        
        # Create a model first
        analyzer = ProjectAnalyzer()
        model = analyzer.analyze_project(
            project_roots=[str(self.test_files_dir)],
            project_name="PlantUML_Test"
        )
        
        # Generate PlantUML diagrams
        output_dir = self.temp_dir / "plantuml_output"
        self.generator.generate_from_model(model, str(output_dir))
        
        # Check that output directory was created
        self.assertTrue(output_dir.exists())
        
        # Check that .puml files were generated
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)
        
        # Check content of generated files
        for puml_file in puml_files:
            content = puml_file.read_text()
            self.assertIn("@startuml", content)
            self.assertIn("@enduml", content)
            self.assertIn("class", content)
    
    def test_project_overview_generation(self):
        """Test project overview diagram generation"""
        if not (self.test_files_dir / "sample.c").exists():
            self.skipTest("sample.c test file not found")
        
        # Create a model first
        analyzer = ProjectAnalyzer()
        model = analyzer.analyze_project(
            project_roots=[str(self.test_files_dir)],
            project_name="Overview_Test"
        )
        
        # Generate project overview
        overview_path = self.temp_dir / "overview.puml"
        self.generator.generate_project_overview(model, str(overview_path))
        
        # Check that file was created
        self.assertTrue(overview_path.exists())
        
        # Check content
        content = overview_path.read_text()
        self.assertIn("@startuml", content)
        self.assertIn("Overview_Test", content)
        self.assertIn("component", content)
    
    def test_generate_plantuml_from_json_convenience(self):
        """Test the convenience function for generating PlantUML from JSON"""
        if not (self.test_files_dir / "sample.c").exists():
            self.skipTest("sample.c test file not found")
        
        # Create and save a model
        analyzer = ProjectAnalyzer()
        model = analyzer.analyze_project(
            project_roots=[str(self.test_files_dir)],
            project_name="JSON_Convenience_Test"
        )
        
        json_path = self.temp_dir / "model.json"
        analyzer.save_model_to_json(model, str(json_path))
        
        # Generate PlantUML using convenience function
        output_dir = self.temp_dir / "convenience_output"
        generate_plantuml_from_json(str(json_path), str(output_dir))
        
        # Check that files were generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)

class TestConfigBasedWorkflow(unittest.TestCase):
    """Test cases for config-based workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_files_dir = Path(__file__).parent / "test_files"
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_config_based_analysis(self):
        """Test analysis using a configuration file"""
        if not (self.test_files_dir / "sample.c").exists():
            self.skipTest("sample.c test file not found")
        
        # Create a test config file
        config = {
            "project_name": "Config_Test_Project",
            "project_roots": [str(self.test_files_dir)],
            "recursive": True,
            "c_file_prefixes": [],
            "model_output_path": str(self.temp_dir / "config_model.json")
        }
        
        config_path = self.temp_dir / "test_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Analyze using config
        model = load_config_and_analyze(str(config_path))
        
        # Check that model was created and saved
        self.assertIsInstance(model, ProjectModel)
        self.assertEqual(model.project_name, "Config_Test_Project")
        self.assertTrue((self.temp_dir / "config_model.json").exists())

class TestIntegrationWorkflow(unittest.TestCase):
    """Integration tests for the complete workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_files_dir = Path(__file__).parent / "test_files"
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test the complete workflow from C files to PlantUML"""
        if not (self.test_files_dir / "sample.c").exists():
            self.skipTest("sample.c test file not found")
        
        # Step 1: Analyze project
        analyzer = ProjectAnalyzer()
        model = analyzer.analyze_project(
            project_roots=[str(self.test_files_dir)],
            project_name="Complete_Workflow_Test"
        )
        
        # Step 2: Save model to JSON
        json_path = self.temp_dir / "workflow_model.json"
        analyzer.save_model_to_json(model, str(json_path))
        
        # Step 3: Generate PlantUML from JSON
        output_dir = self.temp_dir / "workflow_output"
        generate_plantuml_from_json(str(json_path), str(output_dir))
        
        # Verify all steps completed successfully
        self.assertTrue(json_path.exists())
        self.assertTrue(output_dir.exists())
        
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)
        
        # Check that both individual files and overview were generated
        overview_files = [f for f in puml_files if "overview" in f.name]
        individual_files = [f for f in puml_files if "overview" not in f.name]
        
        self.assertGreater(len(overview_files), 0)
        self.assertGreater(len(individual_files), 0)
        
        # Verify content quality
        for puml_file in puml_files:
            content = puml_file.read_text()
            self.assertIn("@startuml", content)
            self.assertIn("@enduml", content)
            # Should contain meaningful content, not just empty diagrams
            self.assertGreater(len(content.splitlines()), 5)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)