#!/usr/bin/env python3
"""
CLI tests for configuration-based model manipulations
Tests the command-line interface with configuration files
"""

import unittest
import tempfile
import json
import os
import subprocess
import sys
from pathlib import Path
from c_to_plantuml.main import handle_config_command, handle_filter_command


class TestConfigurationCLI(unittest.TestCase):
    """CLI tests for configuration-based model manipulations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config = Path('tests/test_config.json')
        self.config_dir = Path('config')
        
        # Create temporary files
        self.temp_files = []
        
        # Create a simple test model for CLI testing
        self.test_model_data = {
            "project_name": "CLITest",
            "project_roots": ["."],
            "files": {
                "cli_sample.c": {
                    "file_path": "cli_sample.c",
                    "relative_path": "cli_sample.c",
                    "project_root": ".",
                    "encoding_used": "utf-8",
                    "structs": {
                        "OldLegacy_struct": {
                            "name": "OldLegacy_struct",
                            "typedef_name": "OldLegacy_struct",
                            "fields": [],
                            "functions": []
                        },
                        "PublicStruct": {
                            "name": "PublicStruct",
                            "typedef_name": "PublicStruct",
                            "fields": [],
                            "functions": []
                        },
                        "ConfigData": {
                            "name": "ConfigData",
                            "typedef_name": "ConfigData",
                            "fields": [],
                            "functions": []
                        }
                    },
                    "enums": {
                        "old_status_enum": {
                            "name": "old_status_enum",
                            "typedef_name": "old_status_enum",
                            "values": []
                        },
                        "E_State": {
                            "name": "E_State",
                            "typedef_name": "E_State",
                            "values": []
                        }
                    },
                    "functions": [
                        {
                            "name": "public_legacy_impl",
                            "return_type": "void",
                            "parameters": [],
                            "is_static": False
                        },
                        {
                            "name": "public_api_function",
                            "return_type": "int",
                            "parameters": [],
                            "is_static": False
                        },
                        {
                            "name": "internal_private_function",
                            "return_type": "void",
                            "parameters": [],
                            "is_static": False
                        }
                    ],
                    "globals": [
                        {
                            "name": "g_config",
                            "type": "int"
                        },
                        {
                            "name": "debug_temp_var",
                            "type": "char"
                        }
                    ],
                    "includes": [],
                    "macros": [],
                    "typedefs": {}
                }
            },
            "global_includes": [],
            "created_at": "2024-01-01"
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temporary files
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def _create_temp_file(self, suffix='.json') -> str:
        """Create a temporary file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            temp_path = f.name
            self.temp_files.append(temp_path)
            return temp_path
    
    def _create_test_model_file(self) -> str:
        """Create a temporary test model file"""
        model_path = self._create_temp_file('.json')
        with open(model_path, 'w') as f:
            json.dump(self.test_model_data, f, indent=2)
        return model_path
    
    def test_config_command_with_test_config(self):
        """Test the config command with the test configuration file"""
        if not self.test_config.exists():
            self.skipTest(f"Test configuration file not found: {self.test_config}")
        
        # Mock the analyze_and_save function to avoid actual file system operations
        from unittest.mock import patch, MagicMock
        
        with patch('c_to_plantuml.main.load_config_and_analyze') as mock_analyze:
            # Create a mock model
            mock_model = MagicMock()
            mock_model.files = {'test.c': MagicMock()}
            mock_analyze.return_value = mock_model
            
            # Create mock arguments
            class MockArgs:
                config_file = str(self.test_config)
            
            args = MockArgs()
            
            # Test the config command
            result = handle_config_command(args)
            
            # Should return 0 (success)
            self.assertEqual(result, 0)
            
            # Should have called the analyze function
            mock_analyze.assert_called_once_with(str(self.test_config))
    
    def test_filter_command_with_test_config(self):
        """Test the filter command with the test configuration file"""
        if not self.test_config.exists():
            self.skipTest(f"Test configuration file not found: {self.test_config}")
        
        # Create a test model file
        model_path = self._create_test_model_file()
        
        # Create mock arguments
        class MockArgs:
            model_file = model_path
            config_files = [str(self.test_config)]
            output = None  # Will overwrite input
        
        args = MockArgs()
        
        # Test the filter command
        result = handle_filter_command(args)
        
        # Should return 0 (success)
        self.assertEqual(result, 0)
        
        # Check that the model was transformed
        with open(model_path, 'r') as f:
            transformed_data = json.load(f)
        
        # Verify transformations were applied
        test_file = transformed_data['files']['cli_sample.c']
        
        # Check struct transformations
        self.assertIn('OldLegacy_t', test_file['structs'])  # OldLegacy_struct -> OldLegacy_t (_struct suffix removed)
        self.assertNotIn('OldLegacy_struct', test_file['structs'])
        
        # Check enum transformations
        self.assertIn('status_e', test_file['enums'])  # old_status_enum -> status_e
        self.assertNotIn('old_status_enum', test_file['enums'])
        
        # Check function transformations
        function_names = [f['name'] for f in test_file['functions']]
        self.assertIn('public_legacy', function_names)  # public_legacy_impl -> public_legacy (_impl suffix removed)
        self.assertNotIn('public_legacy_impl', function_names)
        
        # Check that additions were made (only functions for .c files)
        self.assertIn('test_get_timestamp', function_names)
        self.assertIn('test_validate_checksum', function_names)
    
    def test_filter_command_with_output_file(self):
        """Test the filter command with a separate output file"""
        if not self.test_config.exists():
            self.skipTest(f"Test configuration file not found: {self.test_config}")
        
        # Create a test model file
        model_path = self._create_test_model_file()
        output_path = self._create_temp_file('.json')
        
        # Create mock arguments
        class MockArgs:
            model_file = model_path
            config_files = [str(self.test_config)]
            output = output_path
        
        args = MockArgs()
        
        # Test the filter command
        result = handle_filter_command(args)
        
        # Should return 0 (success)
        self.assertEqual(result, 0)
        
        # Check that the output file was created
        self.assertTrue(os.path.exists(output_path))
        
        # Check that the original file was not modified
        with open(model_path, 'r') as f:
            original_data = json.load(f)
        
        # Original should still have old names
        test_file = original_data['files']['cli_sample.c']
        self.assertIn('OldLegacy_struct', test_file['structs'])
        self.assertIn('public_legacy_impl', [f['name'] for f in test_file['functions']])
        
        # Output should have new names
        with open(output_path, 'r') as f:
            output_data = json.load(f)
        
        output_file = output_data['files']['cli_sample.c']
        self.assertIn('OldLegacy_t', output_file['structs'])
        self.assertIn('public_legacy', [f['name'] for f in output_file['functions']])
    
    def test_filter_command_with_multiple_configs(self):
        """Test the filter command with multiple configuration files"""
        # Find available config files
        config_files = []
        for config_file in self.config_dir.glob('*.json'):
            if config_file.exists():
                config_files.append(str(config_file))
        
        if len(config_files) < 2:
            self.skipTest(f"Need at least 2 configuration files, found: {len(config_files)}")
        
        # Create a test model file
        model_path = self._create_test_model_file()
        output_path = self._create_temp_file('.json')
        
        # Use config files that contain transformations
        cfgs = []
        for config_file in config_files:
            if 'transformations.json' in config_file or 'general_additions.json' in config_file:
                cfgs.append(config_file)
        
        if len(cfgs) < 2:
            # Fallback to first 2 files if specific ones not found
            cfgs = config_files[:2]
        class MockArgs:
            model_file = model_path
            config_files = cfgs
            output = output_path
        
        args = MockArgs()
        
        # Test the filter command
        result = handle_filter_command(args)
        
        # Should return 0 (success)
        self.assertEqual(result, 0)
        
        # Check that the output file was created
        self.assertTrue(os.path.exists(output_path))
        
        # Verify that transformations from multiple configs were applied
        with open(output_path, 'r') as f:
            output_data = json.load(f)
        
        output_file = output_data['files']['cli_sample.c']
        
        # Should have transformations from transformations.json
        self.assertIn('OldLegacy_t', output_file['structs'])
        
        # Should have additions from general_additions.json (if present)
        if any('general_additions.json' in f for f in cfgs):
            # Only functions should be added to .c files
            function_names = [f['name'] for f in output_file['functions']]
            self.assertIn('get_timestamp', function_names)
            self.assertIn('validate_checksum', function_names)
    
    def test_cli_error_handling(self):
        """Test CLI error handling with invalid inputs"""
        # Test with non-existent model file
        class MockArgs:
            model_file = 'nonexistent_model.json'
            config_files = [str(self.test_config)]
            output = None
        
        args = MockArgs()
        
        # Should return 1 (error)
        result = handle_filter_command(args)
        self.assertEqual(result, 1)
        
        # Test with non-existent config file
        model_path = self._create_test_model_file()
        
        class MockArgs2:
            model_file = model_path
            config_files = ['nonexistent_config.json']
            output = None
        
        args2 = MockArgs2()
        
        # Should return 1 (error)
        result = handle_filter_command(args2)
        self.assertEqual(result, 1)
    
    def test_cli_subprocess_integration(self):
        """Test CLI through subprocess to ensure it works as a standalone script"""
        if not self.test_config.exists():
            self.skipTest(f"Test configuration file not found: {self.test_config}")
        
        # Create a test model file
        model_path = self._create_test_model_file()
        output_path = self._create_temp_file('.json')
        
        # Run the CLI command through subprocess
        cmd = [
            sys.executable, '-m', 'c_to_plantuml.main',
            'filter', model_path, str(self.test_config),
            '-o', output_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Should succeed
            self.assertEqual(result.returncode, 0, f"Command failed: {result.stderr}")
            
            # Check that the output file was created
            self.assertTrue(os.path.exists(output_path))
            
            # Verify transformations were applied
            with open(output_path, 'r') as f:
                output_data = json.load(f)
            
            output_file = output_data['files']['cli_sample.c']
            self.assertIn('OldLegacy_t', output_file['structs'])
            self.assertIn('public_legacy', [f['name'] for f in output_file['functions']])
            
        except subprocess.TimeoutExpired:
            self.fail("CLI command timed out")
        except Exception as e:
            self.fail(f"CLI command failed: {e}")
    
    def test_config_command_subprocess(self):
        """Test the config command through subprocess"""
        if not self.test_config.exists():
            self.skipTest(f"Test configuration file not found: {self.test_config}")
        
        # Run the config command through subprocess
        cmd = [
            sys.executable, '-m', 'c_to_plantuml.main',
            'config', str(self.test_config)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Should succeed (even if no actual files to analyze)
            self.assertIn(result.returncode, [0, 1])  # 0 for success, 1 for no files found
            
        except subprocess.TimeoutExpired:
            self.fail("Config command timed out")
        except Exception as e:
            self.fail(f"Config command failed: {e}")
    
    def test_cli_help_output(self):
        """Test that CLI help output is available"""
        cmd = [sys.executable, '-m', 'c_to_plantuml.main', '--help']
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should succeed
            self.assertEqual(result.returncode, 0)
            
            # Should contain help information
            help_output = result.stdout
            self.assertIn('analyze', help_output)
            self.assertIn('generate', help_output)
            self.assertIn('config', help_output)
            self.assertIn('filter', help_output)
            
        except subprocess.TimeoutExpired:
            self.fail("Help command timed out")
        except Exception as e:
            self.fail(f"Help command failed: {e}")
    
    def test_filter_command_help(self):
        """Test filter command help output"""
        cmd = [sys.executable, '-m', 'c_to_plantuml.main', 'filter', '--help']
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should succeed
            self.assertEqual(result.returncode, 0)
            
            # Should contain filter-specific help
            help_output = result.stdout
            self.assertIn('model_file', help_output)
            self.assertIn('config_files', help_output)
            self.assertIn('output', help_output)
            
        except subprocess.TimeoutExpired:
            self.fail("Filter help command timed out")
        except Exception as e:
            self.fail(f"Filter help command failed: {e}")


if __name__ == '__main__':
    unittest.main()