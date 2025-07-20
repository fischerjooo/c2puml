#!/usr/bin/env python3
"""
Unit tests for the project parser and model functionality
"""

import unittest
import os
import tempfile
import json
import shutil
from c_to_plantuml.parser import Parser
from c_to_plantuml.models import ProjectModel
from c_to_plantuml.parser import CParser

class TestProjectAnalyzer(unittest.TestCase):
    """Test cases for ProjectParser functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = Parser()
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
        model = self.parser.c_parser.parse_project(self.temp_dir, recursive=True)
        
        # Verify model structure
        self.assertEqual(model.project_name, os.path.basename(self.temp_dir))
        self.assertEqual(model.project_root, self.temp_dir)
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
        model = self.parser.c_parser.parse_project(self.temp_dir, recursive=True)
        
        # Verify model structure
        self.assertEqual(len(model.files), 2)
        
        # Check that both files are processed
        file_names = [os.path.basename(fp) for fp in model.files.keys()]
        self.assertIn('user.c', file_names)
        self.assertIn('config.c', file_names)
    
    def test_recursive_search(self):
        """Test recursive directory search"""
        # Create nested directory structure
        sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(sub_dir, exist_ok=True)
        
        self.create_test_file("main.c", "int main() { return 0; }")
        self.create_test_file("subdir/helper.c", "void helper() {}")
        
        # Test recursive search (default)
        model = self.parser.c_parser.parse_project(self.temp_dir, recursive=True)
        self.assertEqual(len(model.files), 2)
        
        # Test non-recursive search
        model_non_recursive = self.parser.c_parser.parse_project(self.temp_dir, recursive=False)
        # Should only find files in the root directory
        self.assertEqual(len(model_non_recursive.files), 1)
    
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
        model = self.parser.c_parser.parse_project(self.temp_dir, recursive=True)
        model.save(model_path)
        
        # Verify file was created
        self.assertTrue(os.path.exists(model_path))
        
        # Load the model
        with open(model_path, 'r') as f:
            loaded_model = ProjectModel.from_dict(json.load(f))
        
        # Verify loaded model matches original
        self.assertEqual(loaded_model.project_name, os.path.basename(self.temp_dir))
        self.assertEqual(len(loaded_model.files), 1)
        
        file_model = list(loaded_model.files.values())[0]
        self.assertIn('stdio.h', file_model.includes)
        self.assertIn('Data', file_model.structs)
    
    def test_empty_project_analysis(self):
        """Test analyzing an empty project directory"""
        # Create empty directory
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        
        # Analyze empty project
        model = self.parser.c_parser.parse_project(empty_dir, recursive=True)
        
        # Verify empty model
        self.assertEqual(len(model.files), 0)
        self.assertEqual(model.project_name, "empty")
        self.assertEqual(model.project_root, empty_dir)
    
    def test_error_handling(self):
        """Test error handling in project analysis"""
        # Test with non-existent directory
        with self.assertRaises(Exception):
            self.parser.c_parser.parse_project("/non/existent/path", recursive=True)
        
        # Test with file instead of directory
        test_file = self.create_test_file("test.txt", "not a directory")
        with self.assertRaises(Exception):
            self.parser.c_parser.parse_project(test_file, recursive=True)
    
    def test_file_filtering(self):
        """Test file filtering during analysis"""
        # Create files with different extensions
        self.create_test_file("main.c", "int main() { return 0; }")
        self.create_test_file("header.h", "#define MAX 100")
        self.create_test_file("test.txt", "not a C file")
        self.create_test_file("script.py", "print('not C')")
        
        # Analyze with default filters (should only include .c and .h files)
        model = self.parser.c_parser.parse_project(self.temp_dir, recursive=True)
        
        # Should only include C/C++ files
        file_names = [os.path.basename(fp) for fp in model.files.keys()]
        self.assertIn('main.c', file_names)
        self.assertIn('header.h', file_names)
        self.assertNotIn('test.txt', file_names)
        self.assertNotIn('script.py', file_names)
    
    def test_model_serialization(self):
        """Test model serialization and deserialization"""
        test_content = '''
        #include <stdio.h>
        
        struct Test {
            int value;
        };
        
        int main() {
            return 0;
        }
        '''
        
        self.create_test_file("test.c", test_content)
        
        # Create model
        model = self.parser.c_parser.parse_project(self.temp_dir, recursive=True)
        
        # Serialize to dict
        model_dict = model.__dict__.copy()
        model_dict['files'] = {k: v.__dict__.copy() for k, v in model.files.items()}
        
        # Verify serialization
        self.assertIn('project_name', model_dict)
        self.assertIn('project_root', model_dict)
        self.assertIn('files', model_dict)
        self.assertIn('created_at', model_dict)
        
        # Deserialize from dict
        loaded_model = ProjectModel.from_dict(model_dict)
        
        # Verify deserialization
        self.assertEqual(loaded_model.project_name, model.project_name)
        self.assertEqual(loaded_model.project_root, model.project_root)
        self.assertEqual(len(loaded_model.files), len(model.files))
    
    def test_relative_path_calculation(self):
        """Test relative path calculation in file models"""
        # Create nested structure
        sub_dir = os.path.join(self.temp_dir, "src")
        os.makedirs(sub_dir, exist_ok=True)
        
        self.create_test_file("src/main.c", "int main() { return 0; }")
        
        # Analyze project
        model = self.parser.c_parser.parse_project(self.temp_dir, recursive=True)
        
        # Check relative paths
        file_model = list(model.files.values())[0]
        self.assertEqual(file_model.relative_path, "src/main.c")
        self.assertEqual(file_model.project_root, self.temp_dir)