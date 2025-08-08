#!/usr/bin/env python3
"""
Fix orphan YAML files by creating corresponding Python test files
"""

import os
import glob

# List of orphan YAML files that need corresponding Python files
ORPHAN_YAMLS = [
    "test_absolute_vs_relative_path_consistency",
    "test_anonymous_struct_in_typedef", 
    "test_anonymous_unions_in_structs",
    "test_configuration_extraction",
    "test_debug_anonymous_structure_parsing",
    "test_debug_complex_struct_field_processing", 
    "test_debug_complex_union_parsing",
    "test_debug_nested_anonymous_structure_fields",
    "test_debug_nested_struct_parsing",
    "test_debug_nested_union_field_parsing",
    "test_file_specific_include_depth",
    "test_file_specific_include_filter",
    "test_generator_basic_plantuml",
    "test_generator_duplicate_include_handling",
    "test_include_filter_patterns",
    "test_include_processing_basic",
    "test_mixed_path_styles_handling",
    "test_nested_anonymous_structures",
    "test_nested_structures_in_generated_puml", 
    "test_parser_enum_simple",
    "test_parser_enum_typedef",
    "test_parser_function_declarations",
    "test_parser_function_definitions",
    "test_parser_function_modifiers",
    "test_parser_mixed_content",
    "test_relative_path_handling_in_include_tree",
    "test_subdirectory_includes_path_resolution",
    "test_tokenizer_complex_function_parsing",
    "test_tokenizer_complex_mixed_structures",
    "test_tokenizer_complex_nested_union",
    "test_tokenizer_complex_parsing",
    "test_tokenizer_edge_cases",
    "test_tokenizer_preprocessor_handling",
    "test_transformer_comprehensive_operations",
    "test_transformer_file_filtering", 
    "test_transformer_include_processing",
    "test_verifier_valid_model"
]

def create_python_test_file(yaml_basename):
    """Create a Python test file for the given YAML basename"""
    
    # Convert basename to class name
    class_name_parts = []
    for part in yaml_basename.split('_')[1:]:  # Skip 'test' prefix
        class_name_parts.append(part.capitalize())
    class_name = f"Test{''.join(class_name_parts)}"
    
    # Convert basename to method name 
    method_name = yaml_basename  # Keep as is
    
    # Create Python file content
    content = f'''#!/usr/bin/env python3
"""
Individual test file for {yaml_basename}.yml
Auto-generated to maintain 1:1 pairing between .py and .yml files
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class {class_name}(UnifiedTestCase):
    """Test class for {yaml_basename}"""

    def {method_name}(self):
        """Run the {yaml_basename} test through CLI interface."""
        result = self.run_test("{yaml_basename}")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
'''
    
    # Write the Python file
    python_file = f"tests/unit/{yaml_basename}.py"
    with open(python_file, 'w') as f:
        f.write(content)
    
    print(f"Created: {python_file}")

def main():
    """Create Python test files for all orphan YAML files"""
    print("Creating Python test files for orphan YAML files...")
    print()
    
    for yaml_basename in ORPHAN_YAMLS:
        create_python_test_file(yaml_basename)
    
    print()
    print(f"Created {len(ORPHAN_YAMLS)} Python test files.")
    print("All YAML files now have corresponding Python test files!")

if __name__ == "__main__":
    main()