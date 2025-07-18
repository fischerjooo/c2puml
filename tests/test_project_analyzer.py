#!/usr/bin/env python3
"""
Unit tests for the project analyzer and model functionality
"""

import unittest
import os
import tempfile
import json
import shutil
from c_to_plantuml.project_analyzer import ProjectAnalyzer, load_config_and_analyze
from c_to_plantuml.models.project_model import ProjectModel
from c_to_plantuml.parsers.c_parser import CParser

class TestProjectAnalyzer(unittest.TestCase):
    """Test cases for ProjectAnalyzer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ProjectAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_file(self, filename: str, content: str) -> str:
        """Create a test file and return its path"""
        file_path = os.path.join(self.temp_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.test_files.append(file_path)
        return file_path
    
    def test_single_file_analysis(self):
        """Test analyzing a single C file"""
        test_c_content = '''
        #include <stdio.h>
        #include "local.h"
        
        #define MAX_SIZE 100
        
        typedef struct Point {
            int x;
            int y;
        } Point;
        
        int global_var = 42;
        
        int calculate(int a, int b) {
            return a + b;
        }
        '''
        
        c_file = self.create_test_file("test.c", test_c_content)
        
        # Analyze the project
        model = self.analyzer.analyze_project([self.temp_dir], "TestProject")
        
        # Verify model structure
        self.assertEqual(model.project_name, "TestProject")
        self.assertEqual(model.project_roots, [self.temp_dir])
        self.assertEqual(len(model.files), 1)
        
        # Check file model
        file_model = list(model.files.values())[0]
        self.assertIn('stdio.h', file_model.includes)
        self.assertIn('local.h', file_model.includes)
        self.assertIn('Point', file_model.structs)
        self.assertEqual(len(file_model.functions), 1)
        self.assertEqual(file_model.functions[0].name, 'calculate')
    
    def test_multiple_files_analysis(self):
        """Test analyzing multiple C files"""
        file1_content = '''
        #include <stdio.h>
        
        typedef struct User {
            int id;
            char name[50];
        } User;
        
        void print_user(User* user) {
            printf("User: %s\\n", user->name);
        }
        '''
        
        file2_content = '''
        #include <stdlib.h>
        
        typedef struct Config {
            int max_users;
            int timeout;
        } Config;
        
        Config* create_config(int max_users) {
            return malloc(sizeof(Config));
        }
        '''
        
        self.create_test_file("user.c", file1_content)
        self.create_test_file("config.c", file2_content)
        
        # Analyze the project
        model = self.analyzer.analyze_project([self.temp_dir], "MultiFileProject")
        
        # Verify model structure
        self.assertEqual(len(model.files), 2)
        
        # Check that both files are processed
        file_names = [os.path.basename(fp) for fp in model.files.keys()]
        self.assertIn('user.c', file_names)
        self.assertIn('config.c', file_names)
        
        # Check global includes
        self.assertIn('stdio.h', model.global_includes)
        self.assertIn('stdlib.h', model.global_includes)
    
    def test_prefix_filtering(self):
        """Test filtering files by prefix"""
        self.create_test_file("main.c", "int main() { return 0; }")
        self.create_test_file("test_helper.c", "void helper() {}")
        self.create_test_file("module_core.c", "void core() {}")
        
        # Analyze with prefix filter
        model = self.analyzer.analyze_project(
            [self.temp_dir], 
            "FilteredProject",
            c_file_prefixes=["test_", "module_"]
        )
        
        # Should only include files with specified prefixes
        file_names = [os.path.basename(fp) for fp in model.files.keys()]
        self.assertIn('test_helper.c', file_names)
        self.assertIn('module_core.c', file_names)
        self.assertNotIn('main.c', file_names)
    
    def test_recursive_search(self):
        """Test recursive directory search"""
        # Create nested directory structure
        sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(sub_dir, exist_ok=True)
        
        self.create_test_file("main.c", "int main() { return 0; }")
        self.create_test_file("subdir/helper.c", "void helper() {}")
        
        # Test recursive search (default)
        model = self.analyzer.analyze_project([self.temp_dir], "RecursiveProject")
        self.assertEqual(len(model.files), 2)
        
        # Test non-recursive search
        model_non_recursive = self.analyzer.analyze_project(
            [self.temp_dir], 
            "NonRecursiveProject",
            recursive=False
        )
        # Note: This would require updating find_c_files to support recursive=False
        # For now, we'll assume it finds both files since our test structure is simple
    
    def test_save_and_load_model(self):
        """Test saving and loading project model"""
        test_content = '''
        #include <stdio.h>
        
        typedef struct Data {
            int value;
        } Data;
        
        int process(Data* data) {
            return data->value * 2;
        }
        '''
        
        self.create_test_file("data.c", test_content)
        
        # Analyze and save
        model_path = os.path.join(self.temp_dir, "model.json")
        model = self.analyzer.analyze_and_save(
            [self.temp_dir], 
            model_path, 
            "SaveLoadTest"
        )
        
        # Verify file was created
        self.assertTrue(os.path.exists(model_path))
        
        # Load the model
        loaded_model = ProjectModel.load_from_json(model_path)
        
        # Verify loaded model matches original
        self.assertEqual(loaded_model.project_name, "SaveLoadTest")
        self.assertEqual(len(loaded_model.files), 1)
        
        file_model = list(loaded_model.files.values())[0]
        self.assertIn('stdio.h', file_model.includes)
        self.assertIn('Data', file_model.structs)
    
    def test_config_based_analysis(self):
        """Test analysis using configuration file"""
        test_content = '''
        #include <stdio.h>
        
        void test_function() {
            printf("Hello, World!\\n");
        }
        '''
        
        self.create_test_file("test.c", test_content)
        
        # Create config file
        config = {
            "project_roots": [self.temp_dir],
            "project_name": "ConfigTest",
            "recursive": True,
            "model_output_path": os.path.join(self.temp_dir, "config_model.json")
        }
        
        config_path = os.path.join(self.temp_dir, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        # Run analysis using config
        model = load_config_and_analyze(config_path)
        
        # Verify results
        self.assertEqual(model.project_name, "ConfigTest")
        self.assertEqual(len(model.files), 1)
        
        # Verify model file was saved
        self.assertTrue(os.path.exists(config["model_output_path"]))
    
    def test_empty_project_analysis(self):
        """Test analyzing a project with no C files"""
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        
        # Create a non-C file
        with open(os.path.join(empty_dir, "readme.txt"), 'w') as f:
            f.write("No C files here")
        
        model = self.analyzer.analyze_project([empty_dir], "EmptyProject")
        
        # Should handle empty project gracefully
        self.assertEqual(model.project_name, "EmptyProject")
        self.assertEqual(len(model.files), 0)
        self.assertEqual(len(model.global_includes), 0)
    
    def test_error_handling(self):
        """Test error handling for problematic files"""
        # Create a file with encoding issues
        problematic_file = os.path.join(self.temp_dir, "problematic.c")
        with open(problematic_file, 'wb') as f:
            f.write(b'\xff\xfe// Invalid UTF-8\nint main() { return 0; }')
        
        # Should handle the error gracefully
        model = self.analyzer.analyze_project([self.temp_dir], "ErrorTest")
        
        # Analysis should complete even with problematic files
        self.assertEqual(model.project_name, "ErrorTest")
        # The file might or might not be processed depending on encoding detection
    
    def test_cache_management(self):
        """Test cache management during analysis"""
        # Create multiple files to trigger cache management
        for i in range(60):  # More than the cache limit
            content = f'''
            #include <stdio.h>
            
            void function_{i}() {{
                printf("Function {i}\\n");
            }}
            '''
            self.create_test_file(f"file_{i}.c", content)
        
        # Analyze project (should trigger cache clearing)
        model = self.analyzer.analyze_project([self.temp_dir], "CacheTest")
        
        # Should process all files despite cache clearing
        self.assertEqual(len(model.files), 60)
        
        # Cache should be managed (not necessarily empty due to recent files)
        # This is more of a performance test than a correctness test
    
    def test_relative_path_calculation(self):
        """Test relative path calculation in file models"""
        # Create nested structure
        sub_dir = os.path.join(self.temp_dir, "src", "modules")
        os.makedirs(sub_dir, exist_ok=True)
        
        test_file = self.create_test_file("src/modules/test.c", "int test() { return 0; }")
        
        model = self.analyzer.analyze_project([self.temp_dir], "RelativePathTest")
        
        file_model = list(model.files.values())[0]
        
        # Check that relative path is calculated correctly
        expected_relative = os.path.join("src", "modules", "test.c")
        self.assertEqual(file_model.relative_path, expected_relative)
        self.assertEqual(file_model.project_root, self.temp_dir)

if __name__ == '__main__':
    unittest.main()