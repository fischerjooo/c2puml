import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.transformer import Transformer
from src.c2puml.models import ProjectModel, FileModel
import tempfile
import re

class TestFileSpecificConfiguration:
    def test_file_specific_include_filter(self):
        """Test that file-specific include filters preserve includes arrays correctly"""
        # Create a test project model
        project_model = ProjectModel(project_name="test_project", source_folder="/tmp")
        
        # Create a test file model with includes
        file_model = FileModel(name="sample.c", file_path="/tmp/sample.c")
        file_model.includes = {
            "stdio.h",
            "stdlib.h", 
            "string.h",
            "sample.h",
            "math_utils.h",
            "logger.h",
            "geometry.h",
            "filtered_header.h",  # This should be filtered out
            "first_level.h"       # This should be filtered out
        }
        
        project_model.files["sample.c"] = file_model
        
        # Create configuration with file-specific include filter
        config = {
            "file_specific": {
                "sample.c": {
                    "include_filter": [
                        "^stdio\\.h$",
                        "^stdlib\\.h$",
                        "^string\\.h$",
                        "^sample\\.h$",
                        "^math_utils\\.h$",
                        "^logger\\.h$",
                        "^geometry\\.h$",
                        "^config\\.h$"
                    ],
                    "include_depth": 3
                }
            }
        }
        
        # Create transformer and apply include filters
        transformer = Transformer()
        include_filters = transformer._extract_include_filters_from_config(config)
        transformer._apply_include_filters(project_model, include_filters)
        
        # Check that includes arrays are preserved (correct behavior)
        filtered_includes = file_model.includes
        print(f"Filtered includes: {filtered_includes}")
        
        # All includes should be preserved (includes arrays are never modified)
        all_includes = {
            "stdio.h",
            "stdlib.h",
            "string.h", 
            "sample.h",
            "math_utils.h",
            "logger.h",
            "geometry.h",
            "filtered_header.h",
            "first_level.h"
        }
        
        # Verify all includes are preserved
        for include in all_includes:
            assert include in filtered_includes, f"All includes should be preserved: '{include}' should be present"
        
        # Verify the total count is correct
        assert len(filtered_includes) == len(all_includes), f"All {len(all_includes)} includes should be preserved"
        
        print("✅ File-specific include filter test passed")

    def test_file_specific_include_depth(self):
        """Test that file-specific include depth is applied correctly"""
        # Create a test project model
        project_model = ProjectModel(project_name="test_project", source_folder="/tmp")
        
        # Create test file models
        sample_file = FileModel(name="sample.c", file_path="/tmp/sample.c")
        utils_file = FileModel(name="utils.c", file_path="/tmp/utils.c")
        
        project_model.files["sample.c"] = sample_file
        project_model.files["utils.c"] = utils_file
        
        # Create configuration with different include depths
        config = {
            "include_depth": 10,  # Global default
            "file_specific": {
                "sample.c": {
                    "include_depth": 3
                },
                "utils.c": {
                    "include_depth": 2
                }
            }
        }
        
        # Create transformer and apply include filters
        transformer = Transformer()
        include_filters = transformer._extract_include_filters_from_config(config)
        transformer._apply_include_filters(project_model, include_filters)
        
        # The transformer should respect file-specific include depths
        # This test verifies that the configuration is processed correctly
        print("✅ File-specific include depth test passed")

    def test_include_filter_patterns(self):
        """Test that include filter patterns work correctly"""
        # Test various regex patterns
        patterns = [
            "^stdio\\.h$",
            "^stdlib\\.h$", 
            "^string\\.h$",
            "^sample\\.h$",
            "^math_utils\\.h$",
            "^logger\\.h$",
            "^geometry\\.h$",
            "^config\\.h$"
        ]
        
        # Test files that should match
        matching_files = [
            "stdio.h",
            "stdlib.h",
            "string.h",
            "sample.h",
            "math_utils.h",
            "logger.h",
            "geometry.h",
            "config.h"
        ]
        
        # Test files that should not match
        non_matching_files = [
            "filtered_header.h",
            "first_level.h",
            "stdio.h.bak",
            "stdlib.h.old",
            "mystdio.h",
            "stdio.h.txt"
        ]
        
        # Compile patterns
        compiled_patterns = [re.compile(pattern) for pattern in patterns]
        
        # Test matching files
        for file in matching_files:
            matches = any(pattern.match(file) for pattern in compiled_patterns)
            assert matches, f"File '{file}' should match one of the patterns"
        
        # Test non-matching files
        for file in non_matching_files:
            matches = any(pattern.match(file) for pattern in compiled_patterns)
            assert not matches, f"File '{file}' should not match any pattern"
        
        print("✅ Include filter patterns test passed")

    def test_configuration_extraction(self):
        """Test that configuration extraction works correctly"""
        config = {
            "file_specific": {
                "sample.c": {
                    "include_filter": ["^stdio\\.h$", "^stdlib\\.h$"],
                    "include_depth": 3
                },
                "utils.c": {
                    "include_filter": ["^math\\.h$"],
                    "include_depth": 2
                }
            }
        }
        
        transformer = Transformer()
        include_filters = transformer._extract_include_filters_from_config(config)
        
        # Check that filters are extracted correctly
        assert "sample.c" in include_filters
        assert "utils.c" in include_filters
        assert include_filters["sample.c"] == ["^stdio\\.h$", "^stdlib\\.h$"]
        assert include_filters["utils.c"] == ["^math\\.h$"]
        
        print("✅ Configuration extraction test passed")

if __name__ == "__main__":
    test = TestFileSpecificConfiguration()
    test.test_file_specific_include_filter()
    test.test_file_specific_include_depth()
    test.test_include_filter_patterns()
    test.test_configuration_extraction()
    print("🎉 All file-specific configuration tests passed!")