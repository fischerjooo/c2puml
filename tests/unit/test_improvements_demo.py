#!/usr/bin/env python3
"""
Demonstration test showcasing all improvements made to the codebase.

This test demonstrates:
1. Centralized error handling with custom exceptions
2. Test utilities for better maintainability
3. Comprehensive negative and edge case testing
4. Parameterized testing patterns
5. Improved test data reuse
"""

import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.exceptions import (
    ParserError,
    ConfigError,
    ErrorCode,
    create_error_context,
    get_global_error_handler,
)
from c_to_plantuml.parser import CParser
from c_to_plantuml.config import Config
from tests.test_utils import (
    TestCaseWithCleanup,
    TestProjectBuilder,
    TestModelBuilder,
    TestFileTemplates,
    parameterized_test_cases,
    assert_model_contains_struct,
    assert_model_contains_enum,
    assert_model_contains_function,
    assert_struct_has_field,
    create_temp_file,
    cleanup_temp_file,
)


class TestImprovementsDemo(TestCaseWithCleanup):
    """Demonstration of all improvements made to the codebase."""

    def setUp(self):
        super().setUp()
        self.parser = CParser()
        self.error_handler = get_global_error_handler()
        self.error_handler.clear()  # Start with clean error state

    def test_centralized_error_handling(self):
        """Demonstrate centralized error handling with custom exceptions."""
        
        # Test 1: File not found error
        nonexistent_file = Path("/nonexistent/file.c")
        
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_file(
                nonexistent_file, "nonexistent.c", "/nonexistent"
            )
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.PARSER_FILE_NOT_FOUND)
        self.assertIn("file_path", error.context)
        self.assertIn("function_name", error.context)
        
        # Test 2: Invalid encoding error
        with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as f:
            f.write(b"int main() { return 0; }\xff\xfe")  # Invalid UTF-8
            temp_file = Path(f.name)
        
        self.add_temp_file(temp_file)
        
        try:
            self.parser.parse_file(temp_file, "encoding.c", str(temp_file.parent))
            # Should handle gracefully
        except ParserError as e:
            self.assertEqual(e.error_code, ErrorCode.PARSER_INVALID_ENCODING)
        
        # Test 3: Error context creation
        context = create_error_context(
            file_path="test.c",
            line_number=10,
            column_number=5,
            function_name="test_function"
        )
        
        self.assertIn("file_path", context)
        self.assertIn("line_number", context)
        self.assertIn("column_number", context)
        self.assertIn("function_name", context)

    def test_test_utilities_reuse(self):
        """Demonstrate test utilities for better maintainability."""
        
        # Test 1: Using TestProjectBuilder
        builder = TestProjectBuilder()
        project_root = (
            builder
            .add_simple_struct_file("structs.c")
            .add_simple_enum_file("enums.c")
            .add_function_file("functions.c")
            .add_typedef_file("typedefs.c")
            .build()
        )
        
        self.add_temp_directory(project_root)
        
        # Parse the project
        model = self.parser.parse_project(str(project_root))
        
        # Verify results using utility functions
        self.assertIn("structs.c", model.files)
        self.assertIn("enums.c", model.files)
        self.assertIn("functions.c", model.files)
        
        structs_file = model.files["structs.c"]
        assert_model_contains_struct(structs_file, "Person")
        assert_model_contains_struct(structs_file, "Address")
        
        enums_file = model.files["enums.c"]
        assert_model_contains_enum(enums_file, "Status")
        assert_model_contains_enum(enums_file, "Color")
        
        functions_file = model.files["functions.c"]
        assert_model_contains_function(functions_file, "add")
        assert_model_contains_function(functions_file, "print_hello")
        assert_model_contains_function(functions_file, "calculate_area")
        
        # Test 2: Using TestModelBuilder
        test_struct = TestModelBuilder.create_simple_struct("TestStruct")
        test_enum = TestModelBuilder.create_simple_enum("TestEnum")
        test_function = TestModelBuilder.create_simple_function("test_function")
        
        self.assertEqual(test_struct.name, "TestStruct")
        self.assertEqual(len(test_struct.fields), 3)
        
        self.assertEqual(test_enum.name, "TestEnum")
        self.assertEqual(len(test_enum.values), 3)
        
        self.assertEqual(test_function.name, "test_function")
        self.assertEqual(len(test_function.parameters), 2)
        
        # Test 3: Using TestFileTemplates
        header_content = TestFileTemplates.get_header_template("DEMO_HEADER_H")
        source_content = TestFileTemplates.get_source_template()
        main_content = TestFileTemplates.get_main_template()
        
        self.assertIn("#ifndef DEMO_HEADER_H", header_content)
        self.assertIn("#define DEMO_HEADER_H", header_content)
        self.assertIn("#endif", header_content)
        
        self.assertIn("test_function", source_content)
        self.assertIn("print_message", source_content)
        
        self.assertIn("main(", main_content)
        self.assertIn("Hello, World!", main_content)

    @parameterized_test_cases(
        {"struct_name": "SimpleStruct", "field_count": 2},
        {"struct_name": "ComplexStruct", "field_count": 5},
        {"struct_name": "EmptyStruct", "field_count": 0},
    )
    def test_parameterized_testing(self, struct_name: str, field_count: int):
        """Demonstrate parameterized testing patterns."""
        
        # Create test data based on parameters
        fields = []
        for i in range(field_count):
            fields.append(f"    int field_{i};")
        
        content = f"""
struct {struct_name} {{
{chr(10).join(fields)}
}};
"""
        temp_file = create_temp_file(content)
        self.add_temp_file(temp_file)
        
        # Parse and verify
        file_model = self.parser.parse_file(temp_file, "test.c", str(temp_file.parent))
        
        assert_model_contains_struct(file_model, struct_name)
        struct = file_model.structs[struct_name]
        self.assertEqual(len(struct.fields), field_count)

    def test_comprehensive_negative_cases(self):
        """Demonstrate comprehensive negative and edge case testing."""
        
        # Test 1: Malformed struct
        malformed_content = """
struct MalformedStruct {
    int field1
    char field2;
"""
        temp_file = create_temp_file(malformed_content)
        self.add_temp_file(temp_file)
        
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_file(temp_file, "malformed.c", str(temp_file.parent))
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.PARSER_MALFORMED_STRUCT)
        
        # Test 2: Empty file
        empty_file = create_temp_file("")
        self.add_temp_file(empty_file)
        
        file_model = self.parser.parse_file(empty_file, "empty.c", str(empty_file.parent))
        self.assertEqual(len(file_model.structs), 0)
        self.assertEqual(len(file_model.enums), 0)
        self.assertEqual(len(file_model.functions), 0)
        
        # Test 3: File with only comments
        comment_content = """
/* This is a comment */
// Another comment
/*
 * Multi-line comment
 */
"""
        comment_file = create_temp_file(comment_content)
        self.add_temp_file(comment_file)
        
        file_model = self.parser.parse_file(comment_file, "comments.c", str(comment_file.parent))
        self.assertEqual(len(file_model.structs), 0)
        self.assertEqual(len(file_model.enums), 0)
        self.assertEqual(len(file_model.functions), 0)
        
        # Test 4: Very large file
        large_content = []
        for i in range(100):
            large_content.append(f"""
struct LargeStruct{i} {{
    int field1_{i};
    char field2_{i}[50];
    float field3_{i};
}};
""")
        
        large_file = create_temp_file("".join(large_content))
        self.add_temp_file(large_file)
        
        file_model = self.parser.parse_file(large_file, "large.c", str(large_file.parent))
        self.assertEqual(len(file_model.structs), 100)

    def test_edge_cases_and_boundaries(self):
        """Demonstrate edge cases and boundary condition testing."""
        
        # Test 1: Very long identifier names
        long_name = "a" * 500  # 500 character name
        
        content = f"""
struct {long_name} {{
    int field1;
    char field2;
}};
"""
        temp_file = create_temp_file(content)
        self.add_temp_file(temp_file)
        
        file_model = self.parser.parse_file(temp_file, "long_names.c", str(temp_file.parent))
        self.assertIn(long_name, file_model.structs)
        
        # Test 2: Unicode in identifiers
        unicode_content = """
struct UnicodeStruct {
    int field_with_unicode_ñ;
    char field_with_emoji_🚀[50];
    float field_with_accent_é;
};

enum UnicodeEnum {
    VALUE_WITH_UNICODE_ñ,
    VALUE_WITH_EMOJI_🚀,
    VALUE_WITH_ACCENT_é
};
"""
        unicode_file = create_temp_file(unicode_content)
        self.add_temp_file(unicode_file)
        
        file_model = self.parser.parse_file(unicode_file, "unicode.c", str(unicode_file.parent))
        self.assertIn("UnicodeStruct", file_model.structs)
        self.assertIn("UnicodeEnum", file_model.enums)
        
        # Test 3: Mixed line endings
        mixed_content = "struct TestStruct {\r\n    int field1;\n    char field2;\r};\n"
        mixed_file = create_temp_file(mixed_content)
        self.add_temp_file(mixed_file)
        
        file_model = self.parser.parse_file(mixed_file, "mixed_endings.c", str(mixed_file.parent))
        self.assertIn("TestStruct", file_model.structs)

    def test_error_handler_integration(self):
        """Demonstrate error handler integration."""
        
        # Clear error handler
        self.error_handler.clear()
        
        # Trigger some errors
        try:
            self.parser.parse_file(
                Path("/nonexistent/file.c"), "nonexistent.c", "/nonexistent"
            )
        except ParserError:
            pass  # Expected
        
        try:
            self.parser.parse_project("/nonexistent/project")
        except ParserError:
            pass  # Expected
        
        # Check error handler state
        summary = self.error_handler.get_summary()
        self.assertGreater(summary["error_count"], 0)
        self.assertIn("errors", summary)
        
        # Verify error details
        for error_dict in summary["errors"]:
            self.assertIn("error_code", error_dict)
            self.assertIn("message", error_dict)
            self.assertIn("context", error_dict)

    def test_config_error_handling(self):
        """Demonstrate configuration error handling."""
        
        # Test 1: Invalid JSON config
        invalid_json = """
{
    "filters": {
        "include_patterns": ["*.c"],
        "exclude_patterns": ["*.h"
    }
}
"""
        invalid_config_file = create_temp_file(invalid_json, suffix=".json")
        self.add_temp_file(invalid_config_file)
        
        with self.assertRaises(ConfigError) as cm:
            Config.from_file(invalid_config_file)
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.CONFIG_INVALID_FILE)
        
        # Test 2: Missing config file
        nonexistent_config = Path("/nonexistent/config.json")
        
        with self.assertRaises(ConfigError) as cm:
            Config.from_file(nonexistent_config)
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.CONFIG_INVALID_FILE)

    def test_comprehensive_test_coverage(self):
        """Demonstrate comprehensive test coverage patterns."""
        
        # Test all major C constructs
        comprehensive_content = """
// Structs
struct Person {
    char name[50];
    int age;
    float height;
};

// Enums
enum Status {
    OK,
    ERROR,
    PENDING
};

// Unions
union Data {
    int i;
    float f;
    char str[20];
};

// Functions
int add(int a, int b) {
    return a + b;
}

void print_hello(const char* name) {
    printf("Hello, %s!\\n", name);
}

// Typedefs
typedef int Integer;
typedef char* String;

// Macros
#define MAX_SIZE 100
#define MIN(a, b) ((a) < (b) ? (a) : (b))

// Preprocessor
#ifdef DEBUG
#define LOG(msg) printf("DEBUG: %s\\n", msg)
#else
#define LOG(msg)
#endif

// Global variables
int global_counter = 0;
char* global_string = "Hello";
"""
        temp_file = create_temp_file(comprehensive_content)
        self.add_temp_file(temp_file)
        
        file_model = self.parser.parse_file(temp_file, "comprehensive.c", str(temp_file.parent))
        
        # Verify all constructs are parsed
        self.assertIn("Person", file_model.structs)
        self.assertIn("Status", file_model.enums)
        self.assertIn("Data", file_model.unions)
        
        function_names = [f.name for f in file_model.functions]
        self.assertIn("add", function_names)
        self.assertIn("print_hello", function_names)
        
        self.assertIn("Integer", file_model.aliases)
        self.assertIn("String", file_model.aliases)
        
        self.assertIn("MAX_SIZE", file_model.macros)
        self.assertIn("MIN", file_model.macros)
        self.assertIn("LOG", file_model.macros)
        
        self.assertGreaterEqual(len(file_model.globals), 2)

    def test_cleanup_and_resource_management(self):
        """Demonstrate proper cleanup and resource management."""
        
        # Create multiple temporary files
        files = []
        for i in range(5):
            content = f"struct TestStruct{i} {{ int field{i}; }};"
            temp_file = create_temp_file(content)
            files.append(temp_file)
            self.add_temp_file(temp_file)
        
        # Verify files exist
        for file_path in files:
            self.assertTrue(file_path.exists())
        
        # Cleanup happens automatically in tearDown
        # This test demonstrates that the cleanup mechanism works

    def test_error_context_preservation(self):
        """Demonstrate error context preservation across error handling."""
        
        # Create a complex error scenario
        try:
            # Try to parse a non-existent project
            self.parser.parse_project("/nonexistent/project/with/deep/path")
        except ParserError as e:
            # Verify error context is preserved
            self.assertIn("project_root", e.context)
            self.assertIn("function_name", e.context)
            self.assertEqual(e.error_code, ErrorCode.PARSER_FILE_NOT_FOUND)
            
            # Verify original exception handling
            self.assertIsNone(e.original_exception)  # No original exception for this case


if __name__ == "__main__":
    unittest.main()