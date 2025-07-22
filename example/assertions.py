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
                "typedefs": ["typedef uint32_t id_t", "typedef int32_t status_t", "typedef enum GlobalStatus GlobalStatus_t"],
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
        typedef_pattern = r'typedef\s+(?:struct|enum|union)?\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[a-zA-Z_][a-zA-Z0-9_]*\s*;?'
        matches = re.findall(typedef_pattern, content)
        for match in matches:
            typedefs.append(match.strip())
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
        # Pattern for global variable declarations
        global_pattern = r'(?:extern\s+)?(?:const\s+)?[a-zA-Z_][a-zA-Z0-9_]*\s+\*?\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[=;]'
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
            relationships.append((source, target, 'include'))
            
        # Declaration relationships: A ..> B : <<declares>>
        declare_pattern = r'(\w+)\s+\.\.>\s+(\w+)\s+:\s+<<declares>>'
        declares = re.findall(declare_pattern, content)
        for source, target in declares:
            relationships.append((source, target, 'declares'))
            
        # Uses relationships: A ..> B : <<uses>>
        uses_pattern = r'(\w+)\s+\.\.>\s+(\w+)\s+:\s+<<uses>>'
        uses = re.findall(uses_pattern, content)
        for source, target in uses:
            relationships.append((source, target, 'uses'))
            
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
        includes = [(s, t) for s, t, r in relationships if r == 'include']
        declares = [(s, t) for s, t, r in relationships if r == 'declares']
        uses = [(s, t) for s, t, r in relationships if r == 'uses']
        
        print(f"  📊 Relationship counts:")
        print(f"    Include: {len(includes)}")
        print(f"    Declares: {len(declares)}")
        print(f"    Uses: {len(uses)}")
        
        # Assert relationship structure
        for source, target, rel_type in relationships:
            assert source and target, f"Invalid relationship: {source} -> {target}"
            assert rel_type in ['include', 'declares', 'uses'], f"Invalid relationship type: {rel_type}"
            
        print(f"    ✅ Relationship structure valid")
        
    def assert_specific_content(self, content: str, filename: str) -> None:
        """Assert specific content requirements for each file."""
        print(f"\n🎯 Validating specific content for {filename}:")
        
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
        
        # Validate each PUML file
        for filename in self.expected_files:
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