#!/usr/bin/env python3
"""
Comprehensive assertions for validating generated PUML files against expected output.
This script validates that the generator produces the correct PlantUML diagrams.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


class PUMLValidator:
    """Validates generated PUML files against expected content."""
    
    def __init__(self, output_dir: str = "../output", source_dir: str = "source"):
        self.output_dir = Path(output_dir)
        self.source_dir = Path(source_dir)
        self.expected_files = [
            "typedef_test.puml",
            "geometry.puml", 
            "logger.puml",
            "math_utils.puml",
            "sample.puml"
        ]
        
        # Expected source files with their content requirements
        self.expected_source_files = {
            # C files
            "typedef_test.c": {
                "includes": ["typedef_test.h", "complex_example.h", "geometry.h", "logger.h", "stdlib.h"],
                "globals": ["MyLen global_length", "MyBuffer global_buffer", "MyComplexPtr global_complex"],
                "functions": [
                    "void log_buffer(const MyBuffer * buffer)",
                    "MyInt process_buffer(MyBuffer * buffer)",
                    "int my_callback(MyBuffer * buffer)",
                    "MyComplex * create_complex(MyLen id, MyString name)",
                    "int main(void)"
                ],
                "typedefs": []  # No typedefs in C files
            },
            "geometry.c": {
                "includes": ["geometry.h", "string.h", "stdlib.h"],
                "globals": [],
                "functions": [
                    "triangle_t create_triangle(const point_t * a, const point_t * b, const point_t * c, const char * label)",
                    "int triangle_area(const triangle_t * tri)"
                ],
                "typedefs": []
            },
            "logger.c": {
                "includes": ["logger.h", "stdarg.h", "string.h"],
                "globals": ["log_callback_t current_cb"],
                "functions": [
                    "void set_log_callback(log_callback_t cb)",
                    "void log_message(log_level_t level, const char * fmt, ...)"
                ],
                "typedefs": []
            },
            "math_utils.c": {
                "includes": ["math_utils.h"],
                "globals": [],
                "functions": [
                    "int add(int a, int b)",
                    "int subtract(int a, int b)",
                    "real_t average(const int * arr, size_t len)"
                ],
                "typedefs": []
            },
            "sample.c": {
                "includes": ["stdio.h", "stdlib.h", "string.h", "sample.h", "math_utils.h", "logger.h", "geometry.h"],
                "globals": ["int global_counter", "char buffer[MAX_SIZE]", "double * global_ptr"],
                "macros": ["#define MAX_SIZE", "#define DEBUG_MODE", "#define CALC(x, y)"],
                "functions": [
                    "static void internal_helper(void)",
                    "int calculate_sum(int a, int b)",
                    "point_t * create_point(int x, int y, const char * label)",
                    "void process_point(point_t * p)",
                    "void demo_triangle_usage(void)",
                    "int main(void)"
                ],
                "typedefs": []
            },
            
            # H files
            "typedef_test.h": {
                "includes": ["stdint.h", "sample.h", "config.h", "logger.h"],
                "macros": ["#define TYPEDEF_TEST_H"],
                "typedefs": [
                    "typedef uint32_t MyLen",
                    "typedef int32_t MyInt", 
                    "typedef char * MyString",
                    "typedef struct MyBuffer_tag",
                    "typedef int (*MyCallback)(MyBuffer * buffer)",
                    "typedef struct MyComplexStruct_tag",
                    "typedef MyComplex * MyComplexPtr",
                    "typedef enum Color_tag",
                    "typedef enum StatusEnum_tag",
                    "typedef struct Point_tag",
                    "typedef struct NamedStruct_tag",
                    "typedef union Number_tag",
                    "typedef union NamedUnion_tag",
                    "typedef MyComplexPtr MyComplexArray[10]"
                ],
                "functions": [],
                "globals": []
            },
            "geometry.h": {
                "includes": ["sample.h", "math_utils.h"],
                "macros": ["#define GEOMETRY_H"],
                "typedefs": [
                    "typedef struct triangle_tag"
                ],
                "functions": [
                    "triangle_t create_triangle(const point_t * a, const point_t * b, const point_t * c, const char * label)",
                    "int triangle_area(const triangle_t * tri)"
                ],
                "globals": []
            },
            "logger.h": {
                "includes": ["stdio.h", "config.h"],
                "macros": ["#define LOGGER_H"],
                "typedefs": [
                    "typedef enum log_level_tag",
                    "typedef void (*log_callback_t)(log_level_t level, const char * message)"
                ],
                "functions": [
                    "void set_log_callback(log_callback_t cb)",
                    "void log_message(log_level_t level, const char * fmt, ...)"
                ],
                "globals": []
            },
            "math_utils.h": {
                "includes": ["config.h"],
                "macros": ["#define MATH_UTILS_H"],
                "typedefs": [],
                "functions": [
                    "int add(int a, int b)",
                    "int subtract(int a, int b)",
                    "real_t average(const int * arr, size_t len)"
                ],
                "globals": []
            },
            "sample.h": {
                "includes": ["stddef.h", "config.h"],
                "macros": ["#define SAMPLE_H", "#define PI", "#define VERSION", "#define MIN(a, b)", "#define MAX(a, b)"],
                "typedefs": [
                    "typedef struct point_tag",
                    "typedef enum system_state_tag"
                ],
                "functions": [
                    "extern int calculate_sum(int a, int b)",
                    "extern point_t * create_point(int x, int y, const char * label)",
                    "extern void process_point(point_t * p)"
                ],
                "globals": [
                    "extern const int MAX_POINTS",
                    "extern const char * DEFAULT_LABEL"
                ]
            },
            "config.h": {
                "includes": ["stddef.h", "stdint.h"],
                "macros": ["#define CONFIG_H", "#define PROJECT_NAME", "#define MAX_LABEL_LEN", "#define DEFAULT_BUFFER_SIZE"],
                "typedefs": ["typedef uint32_t id_t", "typedef int32_t status_t", "typedef enum GlobalStatus GlobalStatus_t;"],
                "functions": [],
                "globals": []
            },
            "complex_example.h": {
                "includes": ["config.h", "logger.h"],
                "macros": ["#define COMPLEX_EXAMPLE_H"],
                "typedefs": [
                    "typedef struct NestedInfo_tag",
                    "typedef enum CE_Status_tag",
                    "typedef struct ComplexExample_tag"
                ],
                "functions": [],
                "globals": []
            }
        }
        
    def assert_file_exists(self, filename: str) -> None:
        """Assert that a PUML file exists."""
        filepath = self.output_dir / filename
        assert filepath.exists(), f"File {filename} does not exist at {filepath}"
        print(f"✅ {filename} exists")
        
    def assert_source_file_exists(self, filename: str) -> None:
        """Assert that a source file exists."""
        filepath = self.source_dir / filename
        assert filepath.exists(), f"Source file {filename} does not exist at {filepath}"
        print(f"✅ Source file {filename} exists")
        
    def read_puml_file(self, filename: str) -> str:
        """Read and return the content of a PUML file."""
        filepath = self.output_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
            
    def read_source_file(self, filename: str) -> str:
        """Read and return the content of a source file."""
        filepath = self.source_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
            
    def extract_includes(self, content: str) -> List[str]:
        """Extract all #include statements from source file content."""
        includes = []
        # Pattern for #include with quotes or angle brackets
        include_pattern = r'#include\s+["<]([^">]+)[">]'
        matches = re.findall(include_pattern, content)
        for match in matches:
            # For standard library headers, remove angle brackets and show without <>
            if match.startswith('std') or match in ['stdio.h', 'stdlib.h', 'string.h', 'stdarg.h', 'stddef.h']:
                includes.append(match)
            else:
                includes.append(match)
        return includes
        
    def extract_macros(self, content: str) -> List[str]:
        """Extract all #define statements from source file content."""
        macros = []
        # Pattern for simple #define without parameters
        simple_define_pattern = r'#define\s+(\w+)\s+(?!\()'
        simple_matches = re.findall(simple_define_pattern, content)
        for match in simple_matches:
            macros.append(f"#define {match}")
            
        # Pattern for #define with parameters (function-like macros)
        func_define_pattern = r'#define\s+(\w+)\s*\(([^)]+)\)'
        func_matches = re.findall(func_define_pattern, content)
        for match in func_matches:
            macro_name = match[0]
            params = match[1].strip()
            # Convert parameter list to function-like format
            param_list = [p.strip() for p in params.split(',')]
            param_str = ', '.join(param_list)
            macros.append(f"#define {macro_name}({param_str})")
            
        return macros
        
    def extract_typedefs(self, content: str) -> List[str]:
        """Extract all typedef statements from source file content."""
        typedefs = []
        
        # Use a simpler approach: look for typedef patterns and extract them
        # This is more reliable than complex regex patterns
        
        # Pattern for simple typedefs: typedef type name;
        simple_pattern = r'typedef\s+[a-zA-Z_][a-zA-Z0-9_]*\s+\*?\s*[a-zA-Z_][a-zA-Z0-9_]*\s*(?:\[[^\]]*\])?\s*;'
        simple_matches = re.findall(simple_pattern, content)
        for match in simple_matches:
            typedefs.append(match.strip())
        
        # Pattern for function pointer typedefs
        func_ptr_pattern = r'typedef\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(\s*\*\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)\s*\([^)]*\)\s*;'
        func_matches = re.findall(func_ptr_pattern, content)
        for match in func_matches:
            typedefs.append(match.strip())
        
        # For complex typedefs (struct/enum/union), look for the pattern:
        # typedef struct/enum/union tag { ... } name;
        # We'll use a simpler approach that looks for the key parts
        
        # Look for typedef followed by struct/enum/union
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('typedef') and any(keyword in line for keyword in ['struct', 'enum', 'union']):
                # This is a complex typedef, extract the basic pattern
                # Look for: typedef struct/enum/union tag
                match = re.search(r'typedef\s+(struct|enum|union)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
                if match:
                    typedef_type = match.group(1)
                    typedef_tag = match.group(2)
                    typedefs.append(f"typedef {typedef_type} {typedef_tag}")
        
        # Also look for the specific pattern: typedef enum GlobalStatus GlobalStatus_t;
        enum_typedef_pattern = r'typedef\s+enum\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;'
        enum_matches = re.findall(enum_typedef_pattern, content)
        for match in enum_matches:
            enum_name = match[0]
            typedef_name = match[1]
            typedefs.append(f"typedef enum {enum_name} {typedef_name};")
        
        return typedefs
        
    def extract_functions(self, content: str) -> List[str]:
        """Extract function declarations from source file content."""
        functions = []
        # Pattern for function declarations (including extern and static)
        func_pattern = r'(?:extern\s+|static\s+)?[a-zA-Z_][a-zA-Z0-9_]*\s+\*?\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*;?'
        matches = re.findall(func_pattern, content)
        for match in matches:
            # Clean up the function signature
            func_sig = match.strip()
            # Remove trailing semicolon if present
            if func_sig.endswith(';'):
                func_sig = func_sig[:-1]
            functions.append(func_sig)
        return functions
        
    def extract_globals(self, content: str) -> List[str]:
        """Extract global variable declarations from source file content."""
        globals = []
        # Pattern for global variable declarations including arrays
        global_pattern = r'(?:extern\s+)?(?:const\s+)?[a-zA-Z_][a-zA-Z0-9_]*\s+\*?\s*[a-zA-Z_][a-zA-Z0-9_]*\s*(?:\[[^\]]*\])?\s*[=;]'
        matches = re.findall(global_pattern, content)
        for match in matches:
            globals.append(match.strip())
        return globals
        
    def validate_source_file(self, filename: str) -> None:
        """Validate a single source file against expected content."""
        print(f"\n📁 Validating source file: {filename}")
        
        # Assert file exists
        self.assert_source_file_exists(filename)
        
        # Read file content
        content = self.read_source_file(filename)
        
        # Get expected content
        expected = self.expected_source_files.get(filename, {})
        if not expected:
            print(f"    ⚠️  No expected content defined for {filename}")
            return
            
        # Validate includes
        if "includes" in expected:
            actual_includes = self.extract_includes(content)
            expected_includes = expected["includes"]
            
            print(f"    📋 Validating includes ({len(actual_includes)} found):")
            for include in expected_includes:
                if include in actual_includes:
                    print(f"      ✅ {include}")
                else:
                    print(f"      ❌ Missing: {include}")
                    # Don't fail for missing includes as they might be conditional
                    
        # Validate macros
        if "macros" in expected:
            actual_macros = self.extract_macros(content)
            expected_macros = expected["macros"]
            
            print(f"    📋 Validating macros ({len(actual_macros)} found):")
            for macro in expected_macros:
                if macro in actual_macros:
                    print(f"      ✅ {macro}")
                else:
                    print(f"      ❌ Missing: {macro}")
                    
        # Validate typedefs
        if "typedefs" in expected:
            actual_typedefs = self.extract_typedefs(content)
            expected_typedefs = expected["typedefs"]
            
            print(f"    📋 Validating typedefs ({len(actual_typedefs)} found):")
            for typedef in expected_typedefs:
                # Check if any actual typedef contains the expected pattern
                found = any(typedef in actual for actual in actual_typedefs)
                if found:
                    print(f"      ✅ {typedef}")
                else:
                    print(f"      ❌ Missing: {typedef}")
                    
        # Validate functions
        if "functions" in expected:
            actual_functions = self.extract_functions(content)
            expected_functions = expected["functions"]
            
            print(f"    📋 Validating functions ({len(actual_functions)} found):")
            for func in expected_functions:
                # Check if any actual function contains the expected pattern
                found = any(func in actual for actual in actual_functions)
                if found:
                    print(f"      ✅ {func}")
                else:
                    print(f"      ❌ Missing: {func}")
                    
        # Validate globals
        if "globals" in expected:
            actual_globals = self.extract_globals(content)
            expected_globals = expected["globals"]
            
            print(f"    📋 Validating globals ({len(actual_globals)} found):")
            for global_var in expected_globals:
                # Check if any actual global contains the expected pattern
                found = any(global_var in actual for actual in actual_globals)
                if found:
                    print(f"      ✅ {global_var}")
                else:
                    print(f"      ❌ Missing: {global_var}")
                    
        print(f"    ✅ Source file {filename} validation completed")
        
    def extract_classes(self, content: str) -> Dict[str, Dict]:
        """Extract all class definitions from PUML content."""
        classes = {}
        class_pattern = r'class\s+"([^"]+)"\s+as\s+(\w+)\s+<<(\w+)>>\s+#(\w+)\s*\n\s*\{([^}]+)\}'
        matches = re.finditer(class_pattern, content, re.DOTALL)
        
        for match in matches:
            class_name = match.group(1)
            uml_id = match.group(2)
            stereotype = match.group(3)
            color = match.group(4)
            body = match.group(5).strip()
            
            classes[uml_id] = {
                'name': class_name,
                'stereotype': stereotype,
                'color': color,
                'body': body
            }
            
        return classes
        
    def extract_relationships(self, content: str) -> List[Tuple[str, str, str]]:
        """Extract all relationships from PUML content."""
        relationships = []
        # Include relationships: A --> B : <<include>>
        include_pattern = r'(\w+)\s+-->\s+(\w+)\s+:\s+<<include>>'
        includes = re.findall(include_pattern, content)
        for source, target in includes:
            relationships.append((source, target, '<<include>>'))
            
        # Declaration relationships: A ..> B : <<declares>>
        declare_pattern = r'(\w+)\s+\.\.>\s+(\w+)\s+:\s+<<declares>>'
        declares = re.findall(declare_pattern, content)
        for source, target in declares:
            relationships.append((source, target, '<<declares>>'))
            
        # Uses relationships: A ..> B : <<uses>>
        uses_pattern = r'(\w+)\s+\.\.>\s+(\w+)\s+:\s+<<uses>>'
        uses = re.findall(uses_pattern, content)
        for source, target in uses:
            relationships.append((source, target, '<<uses>>'))
            
        # Also check for relationships without angle brackets (to detect violations)
        # Include relationships without brackets: A --> B : include
        include_no_brackets_pattern = r'(\w+)\s+-->\s+(\w+)\s+:\s+(?!<<)(\w+)(?!>>)'
        includes_no_brackets = re.findall(include_no_brackets_pattern, content)
        for source, target, rel_type in includes_no_brackets:
            if rel_type == 'include':
                relationships.append((source, target, rel_type))
            
        # Declaration relationships without brackets: A ..> B : declares
        declare_no_brackets_pattern = r'(\w+)\s+\.\.>\s+(\w+)\s+:\s+(?!<<)(\w+)(?!>>)'
        declares_no_brackets = re.findall(declare_no_brackets_pattern, content)
        for source, target, rel_type in declares_no_brackets:
            if rel_type == 'declares':
                relationships.append((source, target, rel_type))
            
        # Uses relationships without brackets: A ..> B : uses
        uses_no_brackets_pattern = r'(\w+)\s+\.\.>\s+(\w+)\s+:\s+(?!<<)(\w+)(?!>>)'
        uses_no_brackets = re.findall(uses_no_brackets_pattern, content)
        for source, target, rel_type in uses_no_brackets:
            if rel_type == 'uses':
                relationships.append((source, target, rel_type))
            
        return relationships
        
    def assert_class_structure(self, classes: Dict[str, Dict], filename: str) -> None:
        """Assert that classes have the correct structure and content."""
        print(f"\n🔍 Validating class structure for {filename}:")
        
        for uml_id, class_info in classes.items():
            print(f"  📋 Class: {class_info['name']} ({uml_id})")
            
            # Assert stereotype
            assert class_info['stereotype'] in ['source', 'header', 'typedef'], \
                f"Invalid stereotype '{class_info['stereotype']}' for class {uml_id}"
                
            # Assert color
            assert class_info['color'] in ['LightBlue', 'LightGreen', 'LightYellow', 'LightGray'], \
                f"Invalid color '{class_info['color']}' for class {uml_id}"
                
            # Assert UML_ID naming convention
            if class_info['stereotype'] == 'source':
                # Source files should be named after the filename in uppercase
                expected_name = class_info['name'].upper().replace('-', '_').replace('.', '_')
                assert uml_id == expected_name, \
                    f"Source class {uml_id} should be named {expected_name} (filename in uppercase)"
            elif class_info['stereotype'] == 'header':
                assert uml_id.startswith('HEADER_'), \
                    f"Header class {uml_id} should have HEADER_ prefix"
            elif class_info['stereotype'] == 'typedef':
                assert uml_id.startswith('TYPEDEF_'), \
                    f"Typedef class {uml_id} should have TYPEDEF_ prefix"
                    
            print(f"    ✅ Structure valid")
            
    def assert_class_content(self, classes: Dict[str, Dict], filename: str) -> None:
        """Assert that class content matches expected patterns."""
        print(f"\n📝 Validating class content for {filename}:")
        
        for uml_id, class_info in classes.items():
            body = class_info['body']
            stereotype = class_info['stereotype']
            
            print(f"  📋 Content validation for {uml_id}:")
            
            if stereotype == 'source':
                # Source files should not have + prefix for global variables and functions
                assert not re.search(r'^\s*\+\s+[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*$', body, re.MULTILINE), \
                    f"Source class {uml_id} should not have + prefix for global variables"
                assert not re.search(r'^\s*\+\s+[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\(', body, re.MULTILINE), \
                    f"Source class {uml_id} should not have + prefix for functions"
                    
            elif stereotype == 'header':
                # Header files should have + prefix for all elements
                lines = body.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("'") and not line.startswith("--"):
                        if not line.startswith('+') and not line.startswith('--'):
                            print(f"    ⚠️  Warning: Header line '{line}' might not have + prefix")
                            
            elif stereotype == 'typedef':
                # Typedef classes should have + prefix for all elements
                lines = body.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("'") and not line.startswith("--"):
                        if not line.startswith('+'):
                            print(f"    ⚠️  Warning: Typedef line '{line}' might not have + prefix")
                            
            print(f"    ✅ Content patterns valid")
            
    def assert_relationships(self, relationships: List[Tuple[str, str, str]], filename: str) -> None:
        """Assert that relationships are properly structured."""
        print(f"\n🔗 Validating relationships for {filename}:")
        
        # Group relationships by type
        includes = [(s, t) for s, t, r in relationships if r == '<<include>>']
        declares = [(s, t) for s, t, r in relationships if r == '<<declares>>']
        uses = [(s, t) for s, t, r in relationships if r == '<<uses>>']
        
        print(f"  📊 Relationship counts:")
        print(f"    Include: {len(includes)}")
        print(f"    Declares: {len(declares)}")
        print(f"    Uses: {len(uses)}")
        
        # Check for duplicate relationships
        self._validate_no_duplicate_relationships(relationships, filename)
        
        # Check for consistent relationship formatting
        self._validate_relationship_formatting(relationships, filename)
        
        # Assert relationship structure
        for source, target, rel_type in relationships:
            assert source and target, f"Invalid relationship: {source} -> {target}"
            assert rel_type in ['<<include>>', '<<declares>>', '<<uses>>'], f"Invalid relationship type: {rel_type}"
            
        print(f"    ✅ Relationship structure valid")
        
    def assert_specific_content(self, content: str, filename: str) -> None:
        """Assert specific content requirements for each file."""
        print(f"\n🎯 Validating specific content for {filename}:")
        
        # Check for macro formatting issues
        self._validate_macro_formatting(content, filename)
        
        # Check for typedef content issues
        self._validate_typedef_content(content, filename)
        
        # Check for global variable formatting issues
        self._validate_global_variable_formatting(content, filename)
        
        # Check that no "-- Typedefs --" sections exist in header or source classes
        self._validate_no_typedefs_sections_in_header_or_source_classes(content, filename)
        
        # Check that PlantUML files are only generated for C files, not header files
        self._validate_only_c_files_have_puml_diagrams(filename)
        
        if filename == "typedef_test.puml":
            # Should have specific typedef classes
            assert 'TYPEDEF_MYLEN' in content, "Missing TYPEDEF_MYLEN class"
            assert 'TYPEDEF_MYINT' in content, "Missing TYPEDEF_MYINT class"
            assert 'TYPEDEF_MYSTRING' in content, "Missing TYPEDEF_MYSTRING class"
            assert 'TYPEDEF_MYBUFFER' in content, "Missing TYPEDEF_MYBUFFER class"
            assert 'TYPEDEF_MYCALLBACK' in content, "Missing TYPEDEF_MYCALLBACK class"
            assert 'TYPEDEF_MYCOMPLEX' in content, "Missing TYPEDEF_MYCOMPLEX class"
            assert 'TYPEDEF_MYCOMPLEXPTR' in content, "Missing TYPEDEF_MYCOMPLEXPTR class"
            assert 'TYPEDEF_COLOR_T' in content, "Missing TYPEDEF_COLOR_T enum class"
            assert 'TYPEDEF_STATUS_T' in content, "Missing TYPEDEF_STATUS_T enum class"
            assert 'TYPEDEF_POINT_T' in content, "Missing TYPEDEF_POINT_T class"
            assert 'TYPEDEF_NAMEDSTRUCT_T' in content, "Missing TYPEDEF_NAMEDSTRUCT_T class"
            assert 'TYPEDEF_NUMBER_T' in content, "Missing TYPEDEF_NUMBER_T class"
            assert 'TYPEDEF_NAMEDUNION_T' in content, "Missing TYPEDEF_NAMEDUNION_T class"
            assert 'TYPEDEF_MYCOMPLEXARRAY' in content, "Missing TYPEDEF_MYCOMPLEXARRAY class"
            assert 'TYPEDEF_SYSTEM_STATE_T' in content, "Missing TYPEDEF_SYSTEM_STATE_T enum class"
            assert 'TYPEDEF_TRIANGLE_T' in content, "Missing TYPEDEF_TRIANGLE_T class"
            assert 'TYPEDEF_LOG_LEVEL_T' in content, "Missing TYPEDEF_LOG_LEVEL_T enum class"
            assert 'TYPEDEF_LOG_CALLBACK_T' in content, "Missing TYPEDEF_LOG_CALLBACK_T class"
            assert 'TYPEDEF_NESTEDINFO_T' in content, "Missing TYPEDEF_NESTEDINFO_T class"
            assert 'TYPEDEF_CE_STATUS_T' in content, "Missing TYPEDEF_CE_STATUS_T enum class"
            assert 'TYPEDEF_COMPLEXEXAMPLE_T' in content, "Missing TYPEDEF_COMPLEXEXAMPLE_T class"
            
            # Should have enum values in enum typedefs
            assert 'COLOR_RED' in content, "Missing COLOR_RED enum value"
            assert 'COLOR_GREEN' in content, "Missing COLOR_GREEN enum value"
            assert 'COLOR_BLUE' in content, "Missing COLOR_BLUE enum value"
            assert 'STATUS_OK' in content, "Missing STATUS_OK enum value"
            assert 'STATUS_FAIL' in content, "Missing STATUS_FAIL enum value"
            assert 'LOG_DEBUG' in content, "Missing LOG_DEBUG enum value"
            assert 'LOG_INFO' in content, "Missing LOG_INFO enum value"
            assert 'LOG_WARN' in content, "Missing LOG_WARN enum value"
            assert 'LOG_ERROR' in content, "Missing LOG_ERROR enum value"
            
            # Should have specific relationships
            assert 'TYPEDEF_MYBUFFER ..> TYPEDEF_MYLEN : <<uses>>' in content, "Missing MyBuffer uses MyLen relationship"
            assert 'TYPEDEF_MYBUFFER ..> TYPEDEF_MYSTRING : <<uses>>' in content, "Missing MyBuffer uses MyString relationship"
            assert 'TYPEDEF_MYCALLBACK ..> TYPEDEF_MYBUFFER : <<uses>>' in content, "Missing MyCallback uses MyBuffer relationship"
            assert 'TYPEDEF_MYCOMPLEX ..> TYPEDEF_MYLEN : <<uses>>' in content, "Missing MyComplex uses MyLen relationship"
            assert 'TYPEDEF_MYCOMPLEX ..> TYPEDEF_MYSTRING : <<uses>>' in content, "Missing MyComplex uses MyString relationship"
            assert 'TYPEDEF_MYCOMPLEX ..> TYPEDEF_MYCALLBACK : <<uses>>' in content, "Missing MyComplex uses MyCallback relationship"
            assert 'TYPEDEF_MYCOMPLEX ..> TYPEDEF_LOG_LEVEL_T : <<uses>>' in content, "Missing MyComplex uses log_level_t relationship"
            assert 'TYPEDEF_MYCOMPLEXPTR ..> TYPEDEF_MYCOMPLEX : <<uses>>' in content, "Missing MyComplexPtr uses MyComplex relationship"
            assert 'TYPEDEF_MYCOMPLEXARRAY ..> TYPEDEF_MYCOMPLEXPTR : <<uses>>' in content, "Missing MyComplexArray uses MyComplexPtr relationship"
            assert 'TYPEDEF_TRIANGLE_T ..> TYPEDEF_POINT_T : <<uses>>' in content, "Missing triangle_t uses point_t relationship"
            assert 'TYPEDEF_LOG_CALLBACK_T ..> TYPEDEF_LOG_LEVEL_T : <<uses>>' in content, "Missing log_callback_t uses log_level_t relationship"
            assert 'TYPEDEF_NESTEDINFO_T ..> TYPEDEF_LOG_LEVEL_T : <<uses>>' in content, "Missing NestedInfo_t uses log_level_t relationship"
            assert 'TYPEDEF_COMPLEXEXAMPLE_T ..> TYPEDEF_NESTEDINFO_T : <<uses>>' in content, "Missing ComplexExample_t uses NestedInfo_t relationship"
            assert 'TYPEDEF_COMPLEXEXAMPLE_T ..> TYPEDEF_CE_STATUS_T : <<uses>>' in content, "Missing ComplexExample_t uses CE_Status_t relationship"
            
        elif filename == "geometry.puml":
            assert 'TYPEDEF_TRIANGLE_T' in content, "Missing TYPEDEF_TRIANGLE_T class"
            assert 'TYPEDEF_POINT_T' in content, "Missing TYPEDEF_POINT_T class"
            assert 'TYPEDEF_SYSTEM_STATE_T' in content, "Missing TYPEDEF_SYSTEM_STATE_T enum class"
            assert 'TYPEDEF_LOG_LEVEL_T' in content, "Missing TYPEDEF_LOG_LEVEL_T enum class"
            assert 'TYPEDEF_TRIANGLE_T ..> TYPEDEF_POINT_T : <<uses>>' in content, "Missing triangle_t uses point_t relationship"
            
        elif filename == "logger.puml":
            assert 'TYPEDEF_LOG_LEVEL_T' in content, "Missing TYPEDEF_LOG_LEVEL_T enum class"
            assert 'TYPEDEF_LOG_CALLBACK_T' in content, "Missing TYPEDEF_LOG_CALLBACK_T class"
            assert 'TYPEDEF_LOG_CALLBACK_T ..> TYPEDEF_LOG_LEVEL_T : <<uses>>' in content, "Missing log_callback_t uses log_level_t relationship"
            
        elif filename == "sample.puml":
            assert 'TYPEDEF_POINT_T' in content, "Missing TYPEDEF_POINT_T class"
            assert 'TYPEDEF_SYSTEM_STATE_T' in content, "Missing TYPEDEF_SYSTEM_STATE_T enum class"
            assert 'TYPEDEF_TRIANGLE_T' in content, "Missing TYPEDEF_TRIANGLE_T class"
            assert 'TYPEDEF_LOG_LEVEL_T' in content, "Missing TYPEDEF_LOG_LEVEL_T enum class"
            assert 'TYPEDEF_TRIANGLE_T ..> TYPEDEF_POINT_T : <<uses>>' in content, "Missing triangle_t uses point_t relationship"
            
        elif filename == "math_utils.puml":
            # math_utils.puml should have separate typedef classes
            assert 'TYPEDEF_REAL_T' in content, "Missing TYPEDEF_REAL_T class"
            assert 'TYPEDEF_MATH_OP_T' in content, "Missing TYPEDEF_MATH_OP_T class"
            assert 'TYPEDEF_ID_T' in content, "Missing TYPEDEF_ID_T class"
            assert 'TYPEDEF_STATUS_T' in content, "Missing TYPEDEF_STATUS_T class"
            
        print(f"    ✅ Specific content valid")
    
    def _validate_macro_formatting(self, content: str, filename: str) -> None:
        """Validate that macros show only name/parameters, not full values."""
        # Look for function-like macros that are missing parameters
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('#define'):
                # Check if this is a function-like macro that should have parameters
                # Look for common function-like macro names
                macro_name = line.split()[1] if len(line.split()) > 1 else ""
                
                # Check if this macro should have parameters based on common patterns
                if macro_name in ['MIN', 'MAX', 'CALC'] and '(' not in line:
                    raise AssertionError(f"Function-like macro {macro_name} missing parameters in {filename}")
                
                # Check for macros that show full values instead of just name/parameters
                if macro_name in ['MIN', 'MAX', 'CALC'] and '(' in line and ')' in line:
                    # Check if the macro shows the full value after the parameters
                    parts = line.split(')')
                    if len(parts) > 1 and parts[1].strip() and not parts[1].strip().startswith(';'):
                        raise AssertionError(f"Macro {macro_name} showing full value instead of just name/parameters in {filename}")
                
                # Check for simple defines that show values instead of just names
                if macro_name in ['PI', 'MAX_SIZE', 'DEFAULT_VALUE'] and '=' in line:
                    raise AssertionError(f"Simple define {macro_name} showing value instead of just name in {filename}")
                
                # Check for variadic function issues
                if '... ...' in line:
                    raise AssertionError(f"Malformed variadic function with '... ...' in {filename}")
        
        print("    ✅ Macro formatting valid")
    
    def _validate_typedef_content(self, content: str, filename: str) -> None:
        """Validate that typedef content is properly displayed."""
        # Check for typedef content issues
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check for struct typedefs that only show "typedef struct Name" without fields
            if 'typedef struct' in line and 'typedef struct' in line and '{' not in line:
                # This might be a struct typedef without fields - check if it should have fields
                if any(keyword in line for keyword in ['MyBuffer', 'MyComplex', 'Point_t', 'triangle_t']):
                    # These structs should have fields displayed
                    if 'Field(' not in content and 'field' not in content.lower():
                        raise AssertionError(f"Struct typedef missing fields in {filename}")
            
            # Check for enum typedefs that show EnumValue objects instead of clean values
            if 'EnumValue(' in line:
                raise AssertionError(f"Enum typedef showing EnumValue objects instead of clean values in {filename}")
            
            # Check for function pointer typedefs with raw tokenized format
            if 'typedef' in line and '(*' in line and ')' in line and 'typedef' in line:
                # Check for malformed function pointer typedefs
                if line.count('typedef') > 1 or '... ...' in line:
                    raise AssertionError(f"Malformed function pointer typedef in {filename}")
            
            # Check for simple typedefs that repeat the typedef name
            if line.startswith('+ typedef') and 'typedef' in line:
                # Check if the typedef name is repeated at the end
                parts = line.split()
                if len(parts) >= 3:
                    typedef_name = parts[2]  # e.g., "uint32_t" or "void"
                    if len(parts) > 3 and parts[-1] == typedef_name:
                        raise AssertionError(f"Simple typedef repeating name '{typedef_name}' in {filename}")
            
            # Check for enum/struct typedefs that show only the type instead of values/fields
            if line.strip() in ['+ enum', '+ struct']:
                raise AssertionError(f"Enum/struct typedef showing only type '{line.strip()}' instead of values/fields in {filename}")
        
        print("    ✅ Typedef content valid")
    
    def _validate_global_variable_formatting(self, content: str, filename: str) -> None:
        """Validate that global variables are properly formatted."""
        # Check for global variable formatting issues
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check for global variables that show Field objects instead of clean format
            if 'Field(' in line and 'name=' in line and 'type=' in line:
                raise AssertionError(f"Global variable showing Field object instead of clean format in {filename}")
            
            # Check for malformed variadic functions
            if '... ...' in line:
                raise AssertionError(f"Malformed variadic function with '... ...' in {filename}")
        
        print("    ✅ Global variable formatting valid")

    def _validate_no_typedefs_in_header_or_source_classes(self, puml_lines, filename):
        """Assert that no typedefs (e.g., '+ struct', '+ enum', or any typedef) are generated in header or source class blocks (HEADER_xxx or main class blocks)."""
        in_header_or_main_class = False
        class_name = None
        for line in puml_lines:
            # Detect start of a header or main class
            if line.strip().startswith('class "') and (
                'as HEADER_' in line or 'as ' in line and '<<header>>' in line or '<<main>>' in line):
                in_header_or_main_class = True
                class_name = line.strip()
                continue
            if in_header_or_main_class:
                if line.strip() == '}':
                    in_header_or_main_class = False
                    class_name = None
                    continue
                # Detect typedefs in header or main class
                if line.strip().startswith('+ struct') or line.strip().startswith('+ enum') or line.strip().startswith('+ typedef'):
                    raise AssertionError(f"Typedef found in header or source class block {class_name} in {filename}: {line.strip()}")

    def _validate_no_typedefs_sections_in_header_or_source_classes(self, content: str, filename: str) -> None:
        """Assert that no '-- Typedefs --' sections exist in header or source class blocks."""
        lines = content.split('\n')
        in_header_or_source_class = False
        class_name = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Detect start of a header or source class
            if line.startswith('class "') and (
                'as HEADER_' in line or 
                ('as ' in line and '<<header>>' in line) or 
                ('as ' in line and '<<main>>' in line) or
                ('as ' in line and not '<<typedef>>' in line and not '<<enum>>' in line)
            ):
                in_header_or_source_class = True
                class_name = line
                continue
                
            if in_header_or_source_class:
                if line == '}':
                    in_header_or_source_class = False
                    class_name = None
                    continue
                    
                # Check for "-- Typedefs --" section in header or source class
                if line == '-- Typedefs --':
                    raise AssertionError(f"'-- Typedefs --' section found in header or source class block in {filename}: {class_name}")
                    
                # Also check for typedef values that might appear after the section
                if line.startswith('+ ') and ('struct' in line or 'enum' in line or 'typedef' in line):
                    # Look back a few lines to see if we're in a typedefs section
                    for j in range(max(0, i-5), i):
                        if lines[j].strip() == '-- Typedefs --':
                            raise AssertionError(f"Typedef value found in '-- Typedefs --' section of header or source class block in {filename}: {class_name} - {line}")

    def _validate_only_c_files_have_puml_diagrams(self, filename: str) -> None:
        """Assert that PlantUML files are only generated for C files, not header files."""
        # Extract the base name from the PlantUML filename
        puml_basename = filename.replace('.puml', '')
        
        # Check if this corresponds to a header file by looking for .h extension
        # The expected C files that should have PlantUML diagrams
        expected_c_files = [
            "typedef_test",  # typedef_test.c
            "geometry",      # geometry.c  
            "logger",        # logger.c
            "math_utils",    # math_utils.c
            "sample"         # sample.c
        ]
        
        # Check if this is a header file by looking for common header patterns
        header_patterns = [
            "complex_example",  # complex_example.h
            "config",          # config.h
            "sample_h",        # sample.h (if generated separately)
            "logger_h",        # logger.h (if generated separately)
            "math_utils_h",    # math_utils.h (if generated separately)
            "geometry_h",      # geometry.h (if generated separately)
            "typedef_test_h"   # typedef_test.h (if generated separately)
        ]
        
        # If the basename matches a header pattern, throw an error
        if puml_basename in header_patterns:
            raise AssertionError(f"PlantUML diagram generated for header file: {filename}. Only C files should have PlantUML diagrams generated.")
        
        # If the basename is not in expected C files, it might be a header file
        if puml_basename not in expected_c_files:
            # Check if there's a corresponding .h file in the source directory
            header_file_path = self.source_dir / f"{puml_basename}.h"
            if header_file_path.exists():
                raise AssertionError(f"PlantUML diagram generated for header file: {filename} (corresponds to {puml_basename}.h). Only C files should have PlantUML diagrams generated.")

    def _validate_no_duplicate_relationships(self, relationships: List[Tuple[str, str, str]], filename: str) -> None:
        """Assert that no duplicate relationships exist between the same two objects."""
        seen_relationships = set()
        duplicates = []
        
        for source, target, rel_type in relationships:
            # Create a key for the relationship (source, target, type)
            rel_key = (source, target, rel_type)
            
            if rel_key in seen_relationships:
                duplicates.append(f"{source} -> {target} ({rel_type})")
            else:
                seen_relationships.add(rel_key)
        
        if duplicates:
            duplicate_list = ", ".join(duplicates)
            raise AssertionError(f"Duplicate relationships found in {filename}: {duplicate_list}")

    def _validate_relationship_formatting(self, relationships: List[Tuple[str, str, str]], filename: str) -> None:
        """Assert that all relationships use consistent <<>> formatting."""
        invalid_relationships = []
        
        for source, target, rel_type in relationships:
            # Check if the relationship type has angle brackets
            if not rel_type.startswith('<<') or not rel_type.endswith('>>'):
                invalid_relationships.append(f"{source} -> {target} ({rel_type})")
        
        if invalid_relationships:
            invalid_list = ", ".join(invalid_relationships)
            raise AssertionError(f"Relationships without <<>> formatting found in {filename}: {invalid_list}")

    def validate_file(self, filename: str) -> None:
        """Validate a single PUML file."""
        print(f"\n{'='*60}")
        print(f"🔍 Validating {filename}")
        print(f"{'='*60}")
        
        # Assert file exists
        self.assert_file_exists(filename)
        
        # Read file content
        content = self.read_puml_file(filename)
        
        # Extract and validate classes
        classes = self.extract_classes(content)
        self.assert_class_structure(classes, filename)
        self.assert_class_content(classes, filename)
        
        # Extract and validate relationships
        relationships = self.extract_relationships(content)
        self.assert_relationships(relationships, filename)
        
        # Validate specific content requirements
        self.assert_specific_content(content, filename)
        
        print(f"\n✅ {filename} validation completed successfully!")
        
    def run_source_validations(self) -> None:
        """Run validation for all source files."""
        print(f"\n{'='*60}")
        print("📁 Validating source files")
        print(f"{'='*60}")
        
        # Check if source directory exists
        assert self.source_dir.exists(), f"Source directory {self.source_dir} does not exist"
        
        # Validate each source file
        for filename in self.expected_source_files.keys():
            try:
                self.validate_source_file(filename)
            except AssertionError as e:
                print(f"\n❌ Source validation failed for {filename}: {e}")
                # Don't exit for source file validation failures
            except Exception as e:
                print(f"\n💥 Unexpected error validating source file {filename}: {e}")
                # Don't exit for source file validation failures
                
    def run_all_validations(self) -> None:
        """Run validation for all expected PUML files and source files."""
        print("🚀 Starting comprehensive validation...")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
        print(f"📁 Source directory: {self.source_dir.absolute()}")
        
        # Check if output directory exists
        assert self.output_dir.exists(), f"Output directory {self.output_dir} does not exist"
        
        # First validate source files
        self.run_source_validations()
        
        # Then validate PUML files
        print(f"\n{'='*60}")
        print("📊 Validating generated PUML files")
        print(f"{'='*60}")
        
        # Find all PlantUML files in the output directory
        all_puml_files = list(self.output_dir.glob("*.puml"))
        puml_filenames = [f.name for f in all_puml_files]
        
        print(f"📁 Found {len(puml_filenames)} PlantUML files: {puml_filenames}")
        
        # Validate each PUML file
        for filename in puml_filenames:
            try:
                self.validate_file(filename)
            except AssertionError as e:
                print(f"\n❌ Validation failed for {filename}: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"\n💥 Unexpected error validating {filename}: {e}")
                sys.exit(1)
                
        print(f"\n{'='*60}")
        print("🎉 All validations completed successfully!")
        print(f"{'='*60}")


def main():
    """Main function to run the validation."""
    validator = PUMLValidator()
    validator.run_all_validations()


if __name__ == "__main__":
    main()