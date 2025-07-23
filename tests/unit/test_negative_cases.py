#!/usr/bin/env python3
"""
Negative and edge case tests for C to PlantUML converter.

These tests ensure the system fails gracefully and with helpful diagnostics
for various failure modes, malformed files, and unusual C constructs.
"""

import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.exceptions import (
    ParserError,
    ConfigError,
    ErrorCode,
    create_error_context,
)
from c_to_plantuml.parser import CParser
from c_to_plantuml.config import Config
from c_to_plantuml.transformer import Transformer
from c_to_plantuml.generator import Generator
from c_to_plantuml.verifier import Verifier
from tests.test_utils import TestCaseWithCleanup, TestProjectBuilder


class TestNegativeCases(TestCaseWithCleanup):
    """Test negative cases and edge cases for robust error handling."""

    def setUp(self):
        super().setUp()
        self.parser = CParser()
        self.transformer = Transformer()
        self.generator = Generator()
        self.verifier = Verifier()

    def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        nonexistent_path = Path("/nonexistent/path/file.c")
        
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_file(
                nonexistent_path, "nonexistent.c", "/nonexistent/path"
            )
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.PARSER_FILE_NOT_FOUND)
        self.assertIn("nonexistent", error.message.lower())

    def test_nonexistent_project_root(self):
        """Test handling of nonexistent project root."""
        nonexistent_root = Path("/nonexistent/project/root")
        
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_project(str(nonexistent_root))
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.PARSER_FILE_NOT_FOUND)
        self.assertIn("project root not found", error.message.lower())

    def test_file_as_project_root(self):
        """Test handling when a file is passed as project root."""
        with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as f:
            f.write(b"int main() { return 0; }")
            temp_file = Path(f.name)
        
        self.add_temp_file(temp_file)
        
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_project(str(temp_file))
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.PARSER_FILE_NOT_FOUND)
        self.assertIn("must be a directory", error.message.lower())

    def test_malformed_struct_missing_semicolon(self):
        """Test handling of struct missing semicolon."""
        content = """
struct TestStruct {
    int field1
    char field2;
};
"""
        temp_file = self._create_temp_file(content)
        
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_file(temp_file, "malformed.c", str(temp_file.parent))
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.PARSER_MALFORMED_STRUCT)

    def test_malformed_struct_missing_brace(self):
        """Test handling of struct missing closing brace."""
        content = """
struct TestStruct {
    int field1;
    char field2;
"""
        temp_file = self._create_temp_file(content)
        
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_file(temp_file, "malformed.c", str(temp_file.parent))
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.PARSER_MALFORMED_STRUCT)

    def test_malformed_enum_missing_brace(self):
        """Test handling of enum missing closing brace."""
        content = """
enum TestEnum {
    VALUE1,
    VALUE2
"""
        temp_file = self._create_temp_file(content)
        
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_file(temp_file, "malformed.c", str(temp_file.parent))
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.PARSER_MALFORMED_ENUM)

    def test_malformed_function_missing_brace(self):
        """Test handling of function missing opening brace."""
        content = """
int test_function(int param)
    return param * 2;
}
"""
        temp_file = self._create_temp_file(content)
        
        with self.assertRaises(ParserError) as cm:
            self.parser.parse_file(temp_file, "malformed.c", str(temp_file.parent))
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.PARSER_MALFORMED_FUNCTION)

    def test_deeply_nested_structures(self):
        """Test handling of deeply nested structures."""
        content = """
struct Level1 {
    int data1;
    struct Level2 {
        int data2;
        struct Level3 {
            int data3;
            struct Level4 {
                int data4;
                struct Level5 {
                    int data5;
                    struct Level6 {
                        int data6;
                        struct Level7 {
                            int data7;
                            struct Level8 {
                                int data8;
                                struct Level9 {
                                    int data9;
                                    struct Level10 {
                                        int data10;
                                    } level10;
                                } level9;
                            } level8;
                        } level7;
                    } level6;
                } level5;
            } level4;
        } level3;
    } level2;
};
"""
        temp_file = self._create_temp_file(content)
        
        # This should not raise an exception but should handle deep nesting
        file_model = self.parser.parse_file(temp_file, "nested.c", str(temp_file.parent))
        
        self.assertIn("Level1", file_model.structs)
        level1 = file_model.structs["Level1"]
        self.assertEqual(len(level1.fields), 2)  # data1 and level2

    def test_anonymous_structs(self):
        """Test handling of anonymous structs."""
        content = """
struct {
    int x;
    int y;
} point;

struct Container {
    struct {
        int a;
        int b;
    } inner;
};
"""
        temp_file = self._create_temp_file(content)
        
        # This should handle anonymous structs gracefully
        file_model = self.parser.parse_file(temp_file, "anonymous.c", str(temp_file.parent))
        
        # Should find the Container struct
        self.assertIn("Container", file_model.structs)
        container = file_model.structs["Container"]
        self.assertEqual(len(container.fields), 1)  # inner field

    def test_preprocessor_trickery(self):
        """Test handling of preprocessor trickery."""
        content = """
#define STRUCT_DEF(name, field1, field2) \\
    struct name { \\
        field1; \\
        field2; \\
    };

STRUCT_DEF(GeneratedStruct, int x;, char y;)

#define ENUM_DEF(name, ...) \\
    enum name { __VA_ARGS__ };

ENUM_DEF(GeneratedEnum, VALUE1, VALUE2, VALUE3)
"""
        temp_file = self._create_temp_file(content)
        
        # This should handle macro-generated structures
        file_model = self.parser.parse_file(temp_file, "preprocessor.c", str(temp_file.parent))
        
        # Should find the generated struct and enum
        self.assertIn("GeneratedStruct", file_model.structs)
        self.assertIn("GeneratedEnum", file_model.enums)

    def test_macro_generated_typedefs(self):
        """Test handling of macro-generated typedefs."""
        content = """
#define TYPEDEF_INT(name) typedef int name;
#define TYPEDEF_STRUCT(name, field1, field2) \\
    typedef struct { \\
        field1; \\
        field2; \\
    } name;

TYPEDEF_INT(MyInt)
TYPEDEF_STRUCT(MyStruct, int x;, char y;)
"""
        temp_file = self._create_temp_file(content)
        
        # This should handle macro-generated typedefs
        file_model = self.parser.parse_file(temp_file, "typedefs.c", str(temp_file.parent))
        
        # Should find the generated typedefs
        self.assertIn("MyInt", file_model.aliases)
        self.assertIn("MyStruct", file_model.aliases)

    def test_invalid_encoding(self):
        """Test handling of files with invalid encoding."""
        # Create a file with invalid UTF-8 bytes
        with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as f:
            f.write(b"int main() { return 0; }\xff\xfe")  # Invalid UTF-8
            temp_file = Path(f.name)
        
        self.add_temp_file(temp_file)
        
        # This should handle encoding issues gracefully
        try:
            file_model = self.parser.parse_file(temp_file, "encoding.c", str(temp_file.parent))
            # Should still parse successfully despite encoding issues
            self.assertIsNotNone(file_model)
        except ParserError as e:
            # If it fails, should be with a proper error code
            self.assertEqual(e.error_code, ErrorCode.PARSER_INVALID_ENCODING)

    def test_empty_file(self):
        """Test handling of empty files."""
        temp_file = self._create_temp_file("")
        
        # Empty files should be handled gracefully
        file_model = self.parser.parse_file(temp_file, "empty.c", str(temp_file.parent))
        
        self.assertEqual(len(file_model.structs), 0)
        self.assertEqual(len(file_model.enums), 0)
        self.assertEqual(len(file_model.functions), 0)

    def test_file_with_only_comments(self):
        """Test handling of files with only comments."""
        content = """
/* This is a comment */
// Another comment
/*
 * Multi-line comment
 */
"""
        temp_file = self._create_temp_file(content)
        
        # Files with only comments should be handled gracefully
        file_model = self.parser.parse_file(temp_file, "comments.c", str(temp_file.parent))
        
        self.assertEqual(len(file_model.structs), 0)
        self.assertEqual(len(file_model.enums), 0)
        self.assertEqual(len(file_model.functions), 0)

    def test_invalid_config_file(self):
        """Test handling of invalid configuration files."""
        invalid_config = """
{
    "invalid_key": "invalid_value",
    "filters": {
        "invalid_filter": "invalid_value"
    }
}
"""
        temp_file = self._create_temp_file(invalid_config, suffix=".json")
        
        with self.assertRaises(ConfigError) as cm:
            Config.from_file(temp_file)
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.CONFIG_INVALID_SCHEMA)

    def test_missing_config_file(self):
        """Test handling of missing configuration file."""
        nonexistent_config = Path("/nonexistent/config.json")
        
        with self.assertRaises(ConfigError) as cm:
            Config.from_file(nonexistent_config)
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.CONFIG_INVALID_FILE)

    def test_invalid_json_config(self):
        """Test handling of invalid JSON in config file."""
        invalid_json = """
{
    "filters": {
        "include_patterns": ["*.c"],
        "exclude_patterns": ["*.h"
    }
}
"""
        temp_file = self._create_temp_file(invalid_json, suffix=".json")
        
        with self.assertRaises(ConfigError) as cm:
            Config.from_file(temp_file)
        
        error = cm.exception
        self.assertEqual(error.error_code, ErrorCode.CONFIG_INVALID_FILE)

    def test_circular_includes(self):
        """Test handling of circular include dependencies."""
        # Create header1.h that includes header2.h
        header1_content = """
#ifndef HEADER1_H
#define HEADER1_H

#include "header2.h"

struct Struct1 {
    int field1;
};

#endif
"""
        header1_file = self._create_temp_file(header1_content, suffix=".h")
        
        # Create header2.h that includes header1.h
        header2_content = """
#ifndef HEADER2_H
#define HEADER2_H

#include "header1.h"

struct Struct2 {
    int field2;
};

#endif
"""
        header2_file = self._create_temp_file(header2_content, suffix=".h")
        
        # Create main.c that includes header1.h
        main_content = """
#include "header1.h"

int main() {
    return 0;
}
"""
        main_file = self._create_temp_file(main_content)
        
        # This should handle circular includes gracefully
        try:
            file_model = self.parser.parse_file(main_file, "main.c", str(main_file.parent))
            # Should parse successfully despite circular includes
            self.assertIsNotNone(file_model)
        except ParserError as e:
            # If it fails, should be with a proper error code
            self.assertEqual(e.error_code, ErrorCode.PARSER_INCLUDE_NOT_FOUND)

    def test_very_large_file(self):
        """Test handling of very large files."""
        # Create a large file with many structs
        content = []
        for i in range(1000):
            content.append(f"""
struct LargeStruct{i} {{
    int field1_{i};
    char field2_{i}[50];
    float field3_{i};
}};
""")
        
        temp_file = self._create_temp_file("".join(content))
        
        # This should handle large files without memory issues
        file_model = self.parser.parse_file(temp_file, "large.c", str(temp_file.parent))
        
        # Should parse all structs
        self.assertEqual(len(file_model.structs), 1000)

    def test_unicode_in_identifiers(self):
        """Test handling of Unicode characters in identifiers."""
        content = """
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
        temp_file = self._create_temp_file(content)
        
        # This should handle Unicode in identifiers
        file_model = self.parser.parse_file(temp_file, "unicode.c", str(temp_file.parent))
        
        self.assertIn("UnicodeStruct", file_model.structs)
        self.assertIn("UnicodeEnum", file_model.enums)

    def test_mixed_line_endings(self):
        """Test handling of files with mixed line endings."""
        content = "struct TestStruct {\r\n    int field1;\n    char field2;\r};\n"
        temp_file = self._create_temp_file(content)
        
        # This should handle mixed line endings
        file_model = self.parser.parse_file(temp_file, "mixed_endings.c", str(temp_file.parent))
        
        self.assertIn("TestStruct", file_model.structs)

    def test_nested_preprocessor_directives(self):
        """Test handling of deeply nested preprocessor directives."""
        content = """
#define LEVEL1 1
#define LEVEL2 1

#if LEVEL1
    #if LEVEL2
        struct NestedStruct {
            int data;
        };
    #else
        struct AlternativeStruct {
            int data;
        };
    #endif
#else
    #if LEVEL2
        struct OtherStruct {
            int data;
        };
    #endif
#endif
"""
        temp_file = self._create_temp_file(content)
        
        # This should handle nested preprocessor directives
        file_model = self.parser.parse_file(temp_file, "nested_preprocessor.c", str(temp_file.parent))
        
        # Should find the appropriate struct based on preprocessor evaluation
        self.assertIn("NestedStruct", file_model.structs)

    def test_complex_typedef_chains(self):
        """Test handling of complex typedef chains."""
        content = """
typedef int BaseType;
typedef BaseType DerivedType1;
typedef DerivedType1 DerivedType2;
typedef DerivedType2 FinalType;

struct ComplexStruct {
    FinalType field1;
    DerivedType1 field2;
    BaseType field3;
};
"""
        temp_file = self._create_temp_file(content)
        
        # This should handle complex typedef chains
        file_model = self.parser.parse_file(temp_file, "typedef_chains.c", str(temp_file.parent))
        
        self.assertIn("ComplexStruct", file_model.structs)
        self.assertIn("BaseType", file_model.aliases)
        self.assertIn("FinalType", file_model.aliases)

    def _create_temp_file(self, content: str, suffix: str = ".c") -> Path:
        """Helper method to create a temporary file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_file = Path(f.name)
        
        self.add_temp_file(temp_file)
        return temp_file


class TestEdgeCases(TestCaseWithCleanup):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        super().setUp()
        self.parser = CParser()

    def test_struct_with_maximum_fields(self):
        """Test handling of struct with maximum number of fields."""
        # Create a struct with many fields
        fields = []
        for i in range(1000):
            fields.append(f"    int field_{i};")
        
        content = f"""
struct LargeStruct {{
{chr(10).join(fields)}
}};
"""
        temp_file = self._create_temp_file(content)
        
        # This should handle large structs
        file_model = self.parser.parse_file(temp_file, "large_struct.c", str(temp_file.parent))
        
        self.assertIn("LargeStruct", file_model.structs)
        large_struct = file_model.structs["LargeStruct"]
        self.assertEqual(len(large_struct.fields), 1000)

    def test_very_long_identifier_names(self):
        """Test handling of very long identifier names."""
        long_name = "a" * 1000  # 1000 character name
        
        content = f"""
struct {long_name} {{
    int field1;
    char field2;
}};
"""
        temp_file = self._create_temp_file(content)
        
        # This should handle long identifiers
        file_model = self.parser.parse_file(temp_file, "long_names.c", str(temp_file.parent))
        
        self.assertIn(long_name, file_model.structs)

    def test_nested_comments(self):
        """Test handling of nested comments."""
        content = """
/* Outer comment
   /* Inner comment */
   Still in outer comment */

struct TestStruct {
    int field1; /* Field comment */
    char field2; // Another comment
};
"""
        temp_file = self._create_temp_file(content)
        
        # This should handle nested comments
        file_model = self.parser.parse_file(temp_file, "nested_comments.c", str(temp_file.parent))
        
        self.assertIn("TestStruct", file_model.structs)

    def test_string_literals_with_quotes(self):
        """Test handling of string literals with quotes."""
        content = """
struct StringStruct {
    char* field1; // "quoted string"
    char field2[50]; // 'single quoted'
};

#define STRING_MACRO "Hello \"World\""
"""
        temp_file = self._create_temp_file(content)
        
        # This should handle string literals with quotes
        file_model = self.parser.parse_file(temp_file, "string_literals.c", str(temp_file.parent))
        
        self.assertIn("StringStruct", file_model.structs)

    def test_character_literals(self):
        """Test handling of character literals."""
        content = """
struct CharStruct {
    char field1; // 'a'
    char field2; // '\n'
    char field3; // '\t'
    char field4; // '\\'
    char field5; // '\''
};
"""
        temp_file = self._create_temp_file(content)
        
        # This should handle character literals
        file_model = self.parser.parse_file(temp_file, "char_literals.c", str(temp_file.parent))
        
        self.assertIn("CharStruct", file_model.structs)

    def _create_temp_file(self, content: str, suffix: str = ".c") -> Path:
        """Helper method to create a temporary file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_file = Path(f.name)
        
        self.add_temp_file(temp_file)
        return temp_file


if __name__ == "__main__":
    unittest.main()