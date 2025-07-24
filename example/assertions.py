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

    def _find_output_directory(self) -> str:
        """Return the output directory path."""
        # Check if we're in the example directory
        if Path.cwd().name == "example":
            return "../output"
        return "output"

    def __init__(self):
        # Set paths
        self.output_dir = Path(self._find_output_directory())

        # Expected PUML files
        self.expected_files = [
            "typedef_test.puml",
            "geometry.puml",
            "logger.puml",
            "math_utils.puml",
            "sample.puml",
            "preprocessed.puml",
            "complex.puml",
        ]

    def assert_file_exists(self, filename: str) -> None:
        """Assert that a PUML file exists."""
        filepath = self.output_dir / filename
        assert filepath.exists(), f"File {filename} does not exist at {filepath}"
        # {filename} exists

    def read_puml_file(self, filename: str) -> str:
        """Read and return the content of a PUML file."""
        filepath = self.output_dir / filename
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def extract_classes(self, content: str) -> Dict[str, Dict]:
        """Extract all class definitions from PUML content."""
        classes = {}

        # Extract class definitions
        class_pattern = (
            r'class\s+"([^"]+)"\s+as\s+(\w+)\s+<<(\w+)>>\s+#(\w+)\s*\n\s*\{([^}]+)\}'
        )
        matches = re.finditer(class_pattern, content, re.DOTALL)

        for match in matches:
            class_name = match.group(1)
            uml_id = match.group(2)
            stereotype = match.group(3)
            color = match.group(4)
            body = match.group(5).strip()

            classes[uml_id] = {
                "name": class_name,
                "stereotype": stereotype,
                "color": color,
                "body": body,
            }

        # Extract enum definitions (typedef enums)
        enum_pattern = (
            r'enum\s+"([^"]+)"\s+as\s+(\w+)\s+<<(\w+)>>\s+#(\w+)\s*\n\s*\{([^}]+)\}'
        )
        enum_matches = re.finditer(enum_pattern, content, re.DOTALL)

        for match in enum_matches:
            enum_name = match.group(1)
            uml_id = match.group(2)
            stereotype = match.group(3)
            color = match.group(4)
            body = match.group(5).strip()

            classes[uml_id] = {
                "name": enum_name,
                "stereotype": stereotype,
                "color": color,
                "body": body,
            }

        return classes

    def extract_relationships(self, content: str) -> List[Tuple[str, str, str]]:
        """Extract all relationships from PUML content."""
        relationships = []
        # Include relationships: A --> B : <<include>>
        include_pattern = r"(\w+)\s+-->\s+(\w+)\s+:\s+<<include>>"
        includes = re.findall(include_pattern, content)
        for source, target in includes:
            relationships.append((source, target, "<<include>>"))

        # Declaration relationships: A ..> B : <<declares>>
        declare_pattern = r"(\w+)\s+\.\.>\s+(\w+)\s+:\s+<<declares>>"
        declares = re.findall(declare_pattern, content)
        for source, target in declares:
            relationships.append((source, target, "<<declares>>"))

        # Uses relationships: A ..> B : <<uses>>
        uses_pattern = r"(\w+)\s+\.\.>\s+(\w+)\s+:\s+<<uses>>"
        uses = re.findall(uses_pattern, content)
        for source, target in uses:
            relationships.append((source, target, "<<uses>>"))

        # Also check for relationships without angle brackets (to detect violations)
        # Include relationships without brackets: A --> B : include
        include_no_brackets_pattern = r"(\w+)\s+-->\s+(\w+)\s+:\s+(?!<<)(\w+)(?!>>)"
        includes_no_brackets = re.findall(include_no_brackets_pattern, content)
        for source, target, rel_type in includes_no_brackets:
            if rel_type == "include":
                relationships.append((source, target, rel_type))

        # Declaration relationships without brackets: A ..> B : declares
        declare_no_brackets_pattern = r"(\w+)\s+\.\.>\s+(\w+)\s+:\s+(?!<<)(\w+)(?!>>)"
        declares_no_brackets = re.findall(declare_no_brackets_pattern, content)
        for source, target, rel_type in declares_no_brackets:
            if rel_type == "declares":
                relationships.append((source, target, rel_type))

        # Uses relationships without brackets: A ..> B : uses
        uses_no_brackets_pattern = r"(\w+)\s+\.\.>\s+(\w+)\s+:\s+(?!<<)(\w+)(?!>>)"
        uses_no_brackets = re.findall(uses_no_brackets_pattern, content)
        for source, target, rel_type in uses_no_brackets:
            if rel_type == "uses":
                relationships.append((source, target, rel_type))

        return relationships

    def assert_class_structure(self, classes: Dict[str, Dict], filename: str) -> None:
        """Assert that classes have the correct structure and content."""
        try:
            for uml_id, class_info in classes.items():
                # Assert stereotype
                assert class_info["stereotype"] in [
                    "source",
                    "header",
                    "typedef",
                ], f"Invalid stereotype '{class_info['stereotype']}' for class {uml_id} in {filename}"

                # Assert color
                assert class_info["color"] in [
                    "LightBlue",
                    "LightGreen",
                    "LightYellow",
                    "LightGray",
                ], f"Invalid color '{class_info['color']}' for class {uml_id} in {filename}"

                # Assert UML_ID naming convention
                if class_info["stereotype"] == "source":
                    # Source files should be named after the filename in uppercase
                    expected_name = (
                        class_info["name"].upper().replace("-", "_").replace(".", "_")
                    )
                    assert (
                        uml_id == expected_name
                    ), f"Source class {uml_id} should be named {expected_name} (filename in uppercase) in {filename}"
                elif class_info["stereotype"] == "header":
                    assert uml_id.startswith(
                        "HEADER_"
                    ), f"Header class {uml_id} should have HEADER_ prefix in {filename}"
                elif class_info["stereotype"] == "typedef":
                    assert uml_id.startswith(
                        "TYPEDEF_"
                    ), f"Typedef class {uml_id} should have TYPEDEF_ prefix in {filename}"
        except Exception as e:
            # Fail the test for unexpected exceptions in class structure validation
            assert False, f"Unexpected exception in assert_class_structure for {filename}: {e}"

    def assert_class_content(self, classes: Dict[str, Dict], filename: str) -> None:
        """Assert that class content matches expected patterns."""
        try:
            for uml_id, class_info in classes.items():
                body = class_info["body"]
                stereotype = class_info["stereotype"]

                if stereotype == "source":
                    # Source files should not have + prefix for global variables and functions
                    assert not re.search(
                        r"^\s*\+\s+[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*$",
                        body,
                        re.MULTILINE,
                    ), f"Source class {uml_id} should not have + prefix for global variables in {filename}"
                    assert not re.search(
                        r"^\s*\+\s+[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\(",
                        body,
                        re.MULTILINE,
                    ), f"Source class {uml_id} should not have + prefix for functions in {filename}"

                elif stereotype == "header":
                    # Header files should have + prefix for all elements
                    lines = body.strip().split("\n")
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith("'") and not line.startswith("--"):
                            assert line.startswith("+") or line.startswith("--"), f"Header line '{line}' should have + prefix in {uml_id} in {filename}"

                elif stereotype == "typedef":
                    # Typedef classes should have + prefix for all elements
                    lines = body.strip().split("\n")
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith("'") and not line.startswith("--"):
                            assert line.startswith("+"), f"Typedef line '{line}' should have + prefix in {uml_id} in {filename}"
        except Exception as e:
            # Fail the test for unexpected exceptions in class content validation
            assert False, f"Unexpected exception in assert_class_content for {filename}: {e}"

    def assert_relationships(
        self,
        relationships: List[Tuple[str, str, str]],
        classes: Dict[str, Dict],
        filename: str,
    ) -> None:
        """Assert that relationships are properly structured."""
        try:
            # Group relationships by type
            includes = [(s, t) for s, t, r in relationships if r == "<<include>>"]
            declares = [(s, t) for s, t, r in relationships if r == "<<declares>>"]
            uses = [(s, t) for s, t, r in relationships if r == "<<uses>>"]

            # Check for duplicate relationships
            self._validate_no_duplicate_relationships(relationships, filename)

            # Check for consistent relationship formatting
            self._validate_relationship_formatting(relationships, filename)

            # Check that all typedef objects have at least one relation
            self._validate_all_typedefs_have_relations(relationships, filename)

            # Check that all relations have corresponding classes
            self._validate_all_relations_have_classes(relationships, filename)

            # Check that all header classes have a path to the main C class
            self._validate_all_headers_connected_to_main_class(
                relationships, classes, filename
            )

            # Assert relationship structure
            for source, target, rel_type in relationships:
                assert source and target, f"Invalid relationship: {source} -> {target} in {filename}"
                assert rel_type in [
                    "<<include>>",
                    "<<declares>>",
                    "<<uses>>",
                ], f"Invalid relationship type: {rel_type} in {filename}"
        except Exception as e:
            # Fail the test for unexpected exceptions in relationship validation
            assert False, f"Unexpected exception in assert_relationships for {filename}: {e}"

    def assert_specific_content(self, content: str, filename: str) -> None:
        """Assert specific content requirements for each file."""
        try:
            # Validating specific content for {filename}

            # Check for macro formatting issues
            self._validate_macro_formatting(content, filename)

            # Check for typedef content issues
            self._validate_typedef_content(content, filename)

            # Check for global variable formatting issues
            self._validate_global_variable_formatting(content, filename)

            # Check for array formatting issues
            self._validate_array_formatting(content, filename)

            # Check that no "-- Typedefs --" sections exist in header or source classes
            self._validate_no_typedefs_sections_in_header_or_source_classes(
                content, filename
            )

            # Check that PlantUML files are only generated for C files, not header files
            self._validate_only_c_files_have_puml_diagrams(filename)

            # Check for preprocessing directive issues
            self._validate_preprocessing_directives(content, filename)

            # Check for complex parsing edge cases
            self._validate_complex_parsing_edge_cases(content, filename)

            # Check for complex.puml specific content issues
            self._validate_complex_specific_content(content, filename)

            if filename == "typedef_test.puml":
                # Should have specific typedef classes
                assert "TYPEDEF_MYLEN" in content, "Missing TYPEDEF_MYLEN class"
                assert "TYPEDEF_MYINT" in content, "Missing TYPEDEF_MYINT class"
                assert "TYPEDEF_MYSTRING" in content, "Missing TYPEDEF_MYSTRING class"
                assert "TYPEDEF_MYBUFFER" in content, "Missing TYPEDEF_MYBUFFER class"
                assert "TYPEDEF_MYCALLBACK" in content, "Missing TYPEDEF_MYCALLBACK class"
                assert "TYPEDEF_MYCOMPLEX" in content, "Missing TYPEDEF_MYCOMPLEX class"
                assert (
                    "TYPEDEF_MYCOMPLEXPTR" in content
                ), "Missing TYPEDEF_MYCOMPLEXPTR class"
                assert "TYPEDEF_COLOR_T" in content, "Missing TYPEDEF_COLOR_T enum class"
                assert "TYPEDEF_STATUS_T" in content, "Missing TYPEDEF_STATUS_T enum class"
                assert "TYPEDEF_POINT_T" in content, "Missing TYPEDEF_POINT_T class"
                assert (
                    "TYPEDEF_NAMEDSTRUCT_T" in content
                ), "Missing TYPEDEF_NAMEDSTRUCT_T class"
                assert "TYPEDEF_NUMBER_T" in content, "Missing TYPEDEF_NUMBER_T class"
                assert (
                    "TYPEDEF_NAMEDUNION_T" in content
                ), "Missing TYPEDEF_NAMEDUNION_T class"
                assert (
                    "TYPEDEF_MYCOMPLEXARRAY" in content
                ), "Missing TYPEDEF_MYCOMPLEXARRAY class"
                assert (
                    "TYPEDEF_SYSTEM_STATE_T" in content
                ), "Missing TYPEDEF_SYSTEM_STATE_T enum class"
                assert "TYPEDEF_TRIANGLE_T" in content, "Missing TYPEDEF_TRIANGLE_T class"
                assert (
                    "TYPEDEF_LOG_LEVEL_T" in content
                ), "Missing TYPEDEF_LOG_LEVEL_T enum class"
                assert (
                    "TYPEDEF_LOG_CALLBACK_T" in content
                ), "Missing TYPEDEF_LOG_CALLBACK_T class"
                assert (
                    "TYPEDEF_NESTEDINFO_T" in content
                ), "Missing TYPEDEF_NESTEDINFO_T class"
                assert (
                    "TYPEDEF_CE_STATUS_T" in content
                ), "Missing TYPEDEF_CE_STATUS_T enum class"
                assert (
                    "TYPEDEF_COMPLEXEXAMPLE_T" in content
                ), "Missing TYPEDEF_COMPLEXEXAMPLE_T class"

                # Should have enum values in enum typedefs
                assert "COLOR_RED" in content, "Missing COLOR_RED enum value"
                assert "COLOR_GREEN" in content, "Missing COLOR_GREEN enum value"
                assert "COLOR_BLUE" in content, "Missing COLOR_BLUE enum value"
                assert "STATUS_OK" in content, "Missing STATUS_OK enum value"
                assert "STATUS_FAIL" in content, "Missing STATUS_FAIL enum value"
                assert "LOG_DEBUG" in content, "Missing LOG_DEBUG enum value"
                assert "LOG_INFO" in content, "Missing LOG_INFO enum value"
                assert "LOG_WARN" in content, "Missing LOG_WARN enum value"
                assert "LOG_ERROR" in content, "Missing LOG_ERROR enum value"

                # Should have specific relationships
                assert (
                    "TYPEDEF_MYBUFFER ..> TYPEDEF_MYLEN : <<uses>>" in content
                ), "Missing MyBuffer uses MyLen relationship"
                assert (
                    "TYPEDEF_MYBUFFER ..> TYPEDEF_MYSTRING : <<uses>>" in content
                ), "Missing MyBuffer uses MyString relationship"
                assert (
                    "TYPEDEF_MYCALLBACK ..> TYPEDEF_MYBUFFER : <<uses>>" in content
                ), "Missing MyCallback uses MyBuffer relationship"
                assert (
                    "TYPEDEF_MYCOMPLEX ..> TYPEDEF_MYLEN : <<uses>>" in content
                ), "Missing MyComplex uses MyLen relationship"
                assert (
                    "TYPEDEF_MYCOMPLEX ..> TYPEDEF_MYSTRING : <<uses>>" in content
                ), "Missing MyComplex uses MyString relationship"
                assert (
                    "TYPEDEF_MYCOMPLEX ..> TYPEDEF_MYCALLBACK : <<uses>>" in content
                ), "Missing MyComplex uses MyCallback relationship"
                assert (
                    "TYPEDEF_MYCOMPLEX ..> TYPEDEF_LOG_LEVEL_T : <<uses>>" in content
                ), "Missing MyComplex uses log_level_t relationship"
                assert (
                    "TYPEDEF_MYCOMPLEXPTR ..> TYPEDEF_MYCOMPLEX : <<uses>>" in content
                ), "Missing MyComplexPtr uses MyComplex relationship"
                assert (
                    "TYPEDEF_MYCOMPLEXARRAY ..> TYPEDEF_MYCOMPLEXPTR : <<uses>>" in content
                ), "Missing MyComplexArray uses MyComplexPtr relationship"
                assert (
                    "TYPEDEF_TRIANGLE_T ..> TYPEDEF_POINT_T : <<uses>>" in content
                ), "Missing triangle_t uses point_t relationship"
                assert (
                    "TYPEDEF_LOG_CALLBACK_T ..> TYPEDEF_LOG_LEVEL_T : <<uses>>" in content
                ), "Missing log_callback_t uses log_level_t relationship"
                assert (
                    "TYPEDEF_NESTEDINFO_T ..> TYPEDEF_LOG_LEVEL_T : <<uses>>" in content
                ), "Missing NestedInfo_t uses log_level_t relationship"
                assert (
                    "TYPEDEF_COMPLEXEXAMPLE_T ..> TYPEDEF_NESTEDINFO_T : <<uses>>"
                    in content
                ), "Missing ComplexExample_t uses NestedInfo_t relationship"
                assert (
                    "TYPEDEF_COMPLEXEXAMPLE_T ..> TYPEDEF_CE_STATUS_T : <<uses>>" in content
                ), "Missing ComplexExample_t uses CE_Status_t relationship"

            elif filename == "geometry.puml":
                assert "TYPEDEF_TRIANGLE_T" in content, "Missing TYPEDEF_TRIANGLE_T class"
                assert "TYPEDEF_POINT_T" in content, "Missing TYPEDEF_POINT_T class"
                assert (
                    "TYPEDEF_SYSTEM_STATE_T" in content
                ), "Missing TYPEDEF_SYSTEM_STATE_T enum class"
                assert (
                    "TYPEDEF_LOG_LEVEL_T" in content
                ), "Missing TYPEDEF_LOG_LEVEL_T enum class"
                assert (
                    "TYPEDEF_TRIANGLE_T ..> TYPEDEF_POINT_T : <<uses>>" in content
                ), "Missing triangle_t uses point_t relationship"

            elif filename == "logger.puml":
                assert (
                    "TYPEDEF_LOG_LEVEL_T" in content
                ), "Missing TYPEDEF_LOG_LEVEL_T enum class"
                assert (
                    "TYPEDEF_LOG_CALLBACK_T" in content
                ), "Missing TYPEDEF_LOG_CALLBACK_T class"
                assert (
                    "TYPEDEF_LOG_CALLBACK_T ..> TYPEDEF_LOG_LEVEL_T : <<uses>>" in content
                ), "Missing log_callback_t uses log_level_t relationship"

            elif filename == "sample.puml":
                assert "TYPEDEF_POINT_T" in content, "Missing TYPEDEF_POINT_T class"
                assert (
                    "TYPEDEF_SYSTEM_STATE_T" in content
                ), "Missing TYPEDEF_SYSTEM_STATE_T enum class"
                assert "TYPEDEF_TRIANGLE_T" in content, "Missing TYPEDEF_TRIANGLE_T class"
                assert (
                    "TYPEDEF_LOG_LEVEL_T" in content
                ), "Missing TYPEDEF_LOG_LEVEL_T enum class"
                assert (
                    "TYPEDEF_TRIANGLE_T ..> TYPEDEF_POINT_T : <<uses>>" in content
                ), "Missing triangle_t uses point_t relationship"

            elif filename == "math_utils.puml":
                # math_utils.puml should have separate typedef classes
                assert "TYPEDEF_REAL_T" in content, "Missing TYPEDEF_REAL_T class"
                assert "TYPEDEF_MATH_OP_T" in content, "Missing TYPEDEF_MATH_OP_T class"

            elif filename == "complex.puml":
                # complex.puml should have specific complex typedef classes
                assert (
                    "TYPEDEF_MATH_OPERATION_T" in content
                ), "Missing TYPEDEF_MATH_OPERATION_T class"
                assert (
                    "TYPEDEF_MATH_OPS_ARRAY_T" in content
                ), "Missing TYPEDEF_MATH_OPS_ARRAY_T class"
                assert (
                    "TYPEDEF_COMPLEX_FUNC_PTR_T" in content
                ), "Missing TYPEDEF_COMPLEX_FUNC_PTR_T class"
                assert (
                    "TYPEDEF_DATA_PROCESSOR_T" in content
                ), "Missing TYPEDEF_DATA_PROCESSOR_T class"
                assert (
                    "TYPEDEF_DATA_PROCESSOR_ARRAY_T" in content
                ), "Missing TYPEDEF_DATA_PROCESSOR_ARRAY_T class"
                assert (
                    "TYPEDEF_MIXED_UNION_T" in content
                ), "Missing TYPEDEF_MIXED_UNION_T class"
                assert (
                    "TYPEDEF_OPERATION_SET_T" in content
                ), "Missing TYPEDEF_OPERATION_SET_T class"
                assert (
                    "TYPEDEF_COMPLEX_HANDLER_T" in content
                ), "Missing TYPEDEF_COMPLEX_HANDLER_T class"
                assert (
                    "TYPEDEF_OPERATION_TYPE_T" in content
                ), "Missing TYPEDEF_OPERATION_TYPE_T class"
                assert (
                    "TYPEDEF_COMPLEX_CALLBACK_T" in content
                ), "Missing TYPEDEF_COMPLEX_CALLBACK_T class"
                assert (
                    "TYPEDEF_HANDLER_ENTRY_T" in content
                ), "Missing TYPEDEF_HANDLER_ENTRY_T class"
                assert (
                    "TYPEDEF_HANDLER_TABLE_T" in content
                ), "Missing TYPEDEF_HANDLER_TABLE_T class"
                assert (
                    "TYPEDEF_DEBUG_CALLBACK_T" in content
                ), "Missing TYPEDEF_DEBUG_CALLBACK_T class"
                assert (
                    "TYPEDEF_RELEASE_CALLBACK_T" in content
                ), "Missing TYPEDEF_RELEASE_CALLBACK_T class"
                assert (
                    "TYPEDEF_PROCESSOR_MODULE_ENUM_T" in content
                ), "Missing TYPEDEF_PROCESSOR_MODULE_ENUM_T class"
                assert "TYPEDEF_PROCESS_T" in content, "Missing TYPEDEF_PROCESS_T class"
                assert (
                    "TYPEDEF_STD_RETURNTYPE" in content
                ), "Missing TYPEDEF_STD_RETURNTYPE class"
                assert (
                    "TYPEDEF_PROCESS_CFG_PROCESS_FCT" in content
                ), "Missing TYPEDEF_PROCESS_CFG_PROCESS_FCT class"
                assert (
                    "TYPEDEF_PROCESS_CFG_PROCESS_ACPFCT_T" in content
                ), "Missing TYPEDEF_PROCESS_CFG_PROCESS_ACPFCT_T class"
                assert "TYPEDEF_UINT8" in content, "Missing TYPEDEF_UINT8 class"
                assert "TYPEDEF_UINT32" in content, "Missing TYPEDEF_UINT32 class"

                # Should have specific complex macro definitions
                assert "COMPLEX_MACRO_FUNC" in content, "Missing COMPLEX_MACRO_FUNC macro"
                assert "PROCESS_ARRAY" in content, "Missing PROCESS_ARRAY macro"
                assert "HANDLE_OPERATION" in content, "Missing HANDLE_OPERATION macro"
                assert (
                    "UTILS_U16_TO_U8ARR_BIG_ENDIAN" in content
                ), "Missing UTILS_U16_TO_U8ARR_BIG_ENDIAN macro"
                assert (
                    "UTILS_U32_TO_U8ARR_BIG_ENDIAN" in content
                ), "Missing UTILS_U32_TO_U8ARR_BIG_ENDIAN macro"
                assert (
                    "UTILS_U8ARR_TO_U16_BIG_ENDIAN" in content
                ), "Missing UTILS_U8ARR_TO_U16_BIG_ENDIAN macro"
                assert (
                    "UTILS_U8ARR_TO_U32_BIG_ENDIAN" in content
                ), "Missing UTILS_U8ARR_TO_U32_BIG_ENDIAN macro"

                # Should have specific complex function patterns
                assert (
                    "test_processor_job_processing" in content
                ), "Missing test_processor_job_processing function"
                assert (
                    "test_processor_utility_macros" in content
                ), "Missing test_processor_utility_macros function"
                assert (
                    "test_complex_macro" in content
                ), "Missing test_complex_macro function"
                assert (
                    "test_process_array" in content
                ), "Missing test_process_array function"
                assert (
                    "test_handle_operation" in content
                ), "Missing test_handle_operation function"
                assert "test_mixed_union" in content, "Missing test_mixed_union function"
                assert (
                    "test_operation_set" in content
                ), "Missing test_operation_set function"
                assert (
                    "test_handler_table" in content
                ), "Missing test_handler_table function"
                assert "run_complex_tests" in content, "Missing run_complex_tests function"

                # Should have specific relationships for complex types
                assert (
                    "TYPEDEF_MATH_OPS_ARRAY_T ..> TYPEDEF_MATH_OPERATION_T : <<uses>>"
                    in content
                ), "Missing math_ops_array_t uses math_operation_t relationship"
                assert (
                    "TYPEDEF_DATA_PROCESSOR_ARRAY_T ..> TYPEDEF_DATA_PROCESSOR_T : <<uses>>"
                    in content
                ), "Missing data_processor_array_t uses data_processor_t relationship"
                assert (
                    "TYPEDEF_DATA_PROCESSOR_T ..> TYPEDEF_DATA_ITEM_T : <<uses>>" in content
                ), "Missing data_processor_t uses data_item_t relationship"
                assert (
                    "TYPEDEF_HANDLER_TABLE_T ..> TYPEDEF_HANDLER_ENTRY_T : <<uses>>"
                    in content
                ), "Missing handler_table_t uses handler_entry_t relationship"
                assert (
                    "TYPEDEF_PROCESS_CFG_PROCESS_ACPFCT_T ..> TYPEDEF_PROCESS_CFG_PROCESS_FCT : <<uses>>"
                    in content
                ), "Missing Process_Cfg_Process_acpfct_t uses Process_Cfg_Process_fct relationship"
                assert (
                    "TYPEDEF_PROCESS_CFG_PROCESS_FCT ..> TYPEDEF_PROCESS_T : <<uses>>"
                    in content
                ), "Missing Process_Cfg_Process_fct uses Process_T relationship"
                assert (
                    "TYPEDEF_PROCESS_CFG_PROCESS_FCT ..> TYPEDEF_STD_RETURNTYPE : <<uses>>"
                    in content
                ), "Missing Process_Cfg_Process_fct uses Std_ReturnType relationship"

                # Should have specific enum values
                assert "OP_ADD" in content, "Missing OP_ADD enum value"
                assert "OP_SUB" in content, "Missing OP_SUB enum value"
                assert "OP_MUL" in content, "Missing OP_MUL enum value"
                assert "OP_DIV" in content, "Missing OP_DIV enum value"
                assert (
                    "PROCESSOR_CFG_MODULE_COUNT" in content
                ), "Missing PROCESSOR_CFG_MODULE_COUNT enum value"
                assert (
                    "PROCESSOR_CFG_MODULE_ADAPTER" in content
                ), "Missing PROCESSOR_CFG_MODULE_ADAPTER enum value"
                assert (
                    "PROCESSOR_CFG_MODULE_SERVICE" in content
                ), "Missing PROCESSOR_CFG_MODULE_SERVICE enum value"
                assert (
                    "PROCESSOR_CFG_MODULE_HARDWARE" in content
                ), "Missing PROCESSOR_CFG_MODULE_HARDWARE enum value"

            elif filename == "preprocessed.puml":
                # preprocessed.puml should have preprocessing-related typedef classes
                assert (
                    "TYPEDEF_ENABLED_FEATURE_T" in content
                ), "Missing TYPEDEF_ENABLED_FEATURE_T class"
                assert "TYPEDEF_STATUS_T" in content, "Missing TYPEDEF_STATUS_T enum class"
                assert (
                    "TYPEDEF_FEATURE_CALLBACK_T" in content
                ), "Missing TYPEDEF_FEATURE_CALLBACK_T class"
                assert (
                    "TYPEDEF_LARGE_BUFFER_T" in content
                ), "Missing TYPEDEF_LARGE_BUFFER_T class"
                assert (
                    "TYPEDEF_FEATURE_STRUCT_T" in content
                ), "Missing TYPEDEF_FEATURE_STRUCT_T class"
                assert (
                    "TYPEDEF_FEATURE_UNION_T" in content
                ), "Missing TYPEDEF_FEATURE_UNION_T class"

                # Should have enum values from preprocessing
                assert "STATUS_ENABLED" in content, "Missing STATUS_ENABLED enum value"
                assert "STATUS_DISABLED" in content, "Missing STATUS_DISABLED enum value"
                assert "STATUS_UNKNOWN" in content, "Missing STATUS_UNKNOWN enum value"

                # Should have preprocessing-related relationships
                assert (
                    "TYPEDEF_FEATURE_CALLBACK_T ..> TYPEDEF_ENABLED_FEATURE_T : <<uses>>"
                    in content
                ), "Missing feature_callback_t uses enabled_feature_t relationship"

            # Specific content validation completed successfully
        except Exception as e:
            # Fail the test for unexpected exceptions in specific content validation
            assert False, f"Unexpected exception in assert_specific_content for {filename}: {e}"

    def _validate_macro_formatting(self, content: str, filename: str) -> None:
        """Validate that macros show only name/parameters, not full values."""
        # Look for function-like macros that are missing parameters
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("#define"):
                # Check if this is a function-like macro that should have parameters
                # Look for common function-like macro names
                macro_name = line.split()[1] if len(line.split()) > 1 else ""

                # Check if this macro should have parameters based on common patterns
                if macro_name in ["MIN", "MAX", "CALC"] and "(" not in line:
                    raise AssertionError(
                        f"Function-like macro {macro_name} missing parameters in {filename}"
                    )

                # Check for macros that show full values instead of just name/parameters
                if macro_name in ["MIN", "MAX", "CALC"] and "(" in line and ")" in line:
                    # Check if the macro shows the full value after the parameters
                    parts = line.split(")")
                    if (
                        len(parts) > 1
                        and parts[1].strip()
                        and not parts[1].strip().startswith(";")
                    ):
                        raise AssertionError(
                            f"Macro {macro_name} showing full value instead of just name/parameters in {filename}"
                        )

                # Check for simple defines that show values instead of just names
                if macro_name in ["PI", "MAX_SIZE", "DEFAULT_VALUE"] and "=" in line:
                    raise AssertionError(
                        f"Simple define {macro_name} showing value instead of just name in {filename}"
                    )

                # Check for variadic function issues
                if "... ..." in line:
                    raise AssertionError(
                        f"Malformed variadic function with '... ...' in {filename}"
                    )

        # Macro formatting validation completed successfully

    def _validate_typedef_content(self, content: str, filename: str) -> None:
        """Validate that typedef content is properly displayed."""
        # Check for typedef content issues
        lines = content.split("\n")

        for line in lines:
            line = line.strip()

            # Check for struct typedefs that only show "typedef struct Name" without fields
            if (
                "typedef struct" in line
                and "typedef struct" in line
                and "{" not in line
            ):
                # This might be a struct typedef without fields - check if it should have fields
                if any(
                    keyword in line
                    for keyword in ["MyBuffer", "MyComplex", "Point_t", "triangle_t"]
                ):
                    # These structs should have fields displayed
                    if "Field(" not in content and "field" not in content.lower():
                        raise AssertionError(
                            f"Struct typedef missing fields in {filename}"
                        )

            # Check for enum typedefs that show EnumValue objects instead of clean values
            if "EnumValue(" in line:
                raise AssertionError(
                    f"Enum typedef showing EnumValue objects instead of clean values in {filename}"
                )

            # Check for function pointer typedefs with raw tokenized format
            if "typedef" in line and "(*" in line and ")" in line and "typedef" in line:
                # Check for malformed function pointer typedefs
                if line.count("typedef") > 1 or "... ..." in line:
                    raise AssertionError(
                        f"Malformed function pointer typedef in {filename}"
                    )

            # Check for simple typedefs that repeat the typedef name
            if line.startswith("+ typedef") and "typedef" in line:
                # Check if the typedef name is repeated at the end
                parts = line.split()
                if len(parts) >= 3:
                    typedef_name = parts[2]  # e.g., "uint32_t" or "void"
                    if len(parts) > 3 and parts[-1] == typedef_name:
                        raise AssertionError(
                            f"Simple typedef repeating name '{typedef_name}' in {filename}"
                        )

            # Check for enum/struct typedefs that show only the type instead of values/fields
            if line.strip() in ["+ enum", "+ struct"]:
                raise AssertionError(
                    f"Enum/struct typedef showing only type '{line.strip()}' instead of values/fields in {filename}"
                )

        # Typedef content validation completed successfully

    def _validate_global_variable_formatting(self, content: str, filename: str) -> None:
        """Validate that global variables are properly formatted."""
        # Check for global variable formatting issues
        lines = content.split("\n")

        for line in lines:
            line = line.strip()

            # Check for global variables that show Field objects instead of clean format
            if "Field(" in line and "name=" in line and "type=" in line:
                raise AssertionError(
                    f"Global variable showing Field object instead of clean format in {filename}"
                )

            # Check for malformed variadic functions
            if "... ..." in line:
                raise AssertionError(
                    f"Malformed variadic function with '... ...' in {filename}"
                )

        # Global variable formatting validation completed successfully

    def _validate_array_formatting(self, content: str, filename: str) -> None:
        """Validate that array declarations are properly formatted with size inside brackets."""
        # Check for array formatting issues
        lines = content.split("\n")

        for line in lines:
            line = line.strip()

            # Check for incorrect array format: type size[ ] name instead of type[size] name
            # Pattern: + type size[ ] name
            if line.startswith("+ ") and "[" in line and "]" in line:
                # Look for the pattern where size comes before [ ]
                # Examples of incorrect format:
                # + char MAX_LABEL_LEN[ ] description
                # + int 5[ ] values
                # + point_t 3[ ] vertices
                # + char 32[ ] label

                # Split the line to analyze the parts
                parts = line.split()
                if len(parts) >= 4:  # + type size[ ] name
                    # Check if we have the pattern: type size[ ] name
                    for i in range(1, len(parts) - 2):
                        if (
                            parts[i + 1] == "["
                            and parts[i + 2] == "]"
                            and parts[i] not in ["[", "]", ";", "}"]
                            and not parts[i].startswith("[")
                            and not parts[i].endswith("]")
                        ):
                            # This looks like an array with size before brackets
                            # Check if the size part looks like a number or identifier
                            size_part = parts[i]
                            if (
                                size_part.isdigit()
                                or size_part.isidentifier()
                                or size_part in ["MAX_LABEL_LEN", "5", "3", "32"]
                            ):
                                raise AssertionError(
                                    f"Incorrect array format in {filename}: '{line}'. "
                                    f"Expected format: 'type[size] name', got: 'type size[ ] name'"
                                )

        # Array formatting validation completed successfully

    def _validate_preprocessing_directives(self, content: str, filename: str) -> None:
        """Validate that preprocessing directives are properly processed and not left as raw text."""
        # Validating preprocessing directives in {filename}

        # Check for raw preprocessing directives that should have been processed
        raw_directives = [
            "#if FEATURE_ENABLED",
            "#if DEBUG_MODE",
            "#if MAX_SIZE > 50",
            "#if MIN_SIZE < 20",
            "#elif defined(DEBUG_MODE)",
            "#else",
            "#endif",
            "#ifdef FEATURE_ENABLED",
            "#ifdef DEBUG_MODE",
        ]

        found_raw_directives = []
        for directive in raw_directives:
            if directive in content:
                found_raw_directives.append(directive)

        if found_raw_directives:
            directive_list = ", ".join(found_raw_directives)
            raise AssertionError(
                f"Raw preprocessing directives found in {filename}: {directive_list}. "
                f"These should be processed and not appear as raw text in the PlantUML output."
            )

        # Check for malformed preprocessing results
        # Look for incomplete conditional compilation blocks
        lines = content.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()

            # Check for incomplete #if blocks (missing #endif)
            if line.startswith("#if") and not line.endswith(";"):
                # Look ahead to see if there's a corresponding #endif
                has_endif = False
                for j in range(
                    i + 1, min(i + 50, len(lines))
                ):  # Look ahead up to 50 lines
                    if lines[j].strip() == "#endif":
                        has_endif = True
                        break
                if not has_endif:
                    raise AssertionError(
                        f"Incomplete preprocessing block in {filename}: {line} (missing #endif)"
                    )

            # Check for malformed preprocessing expressions
            if "#if" in line and "defined(" in line and not line.endswith(")"):
                raise AssertionError(
                    f"Malformed preprocessing expression in {filename}: {line}"
                )

        # Preprocessing directives properly processed

    def _validate_complex_parsing_edge_cases(self, content: str, filename: str) -> None:
        """Validate complex parsing edge cases specific to complex.c and complex.h."""
        if "complex" not in filename.lower():
            return

        # Validating complex parsing edge cases in {filename}

        # Validate nasty function pointer array patterns
        if "complex.c" in filename:
            self._validate_function_pointer_arrays(content, filename)
            self._validate_complex_macros(content, filename)
            self._validate_crypto_utility_macros(content, filename)
            self._validate_nasty_edge_case_functions(content, filename)

        # Validate nasty typedef patterns
        if "complex.h" in filename:
            self._validate_complex_typedefs(content, filename)
            self._validate_complex_macro_definitions(content, filename)
            self._validate_const_array_of_function_pointers(content, filename)
            self._validate_complex_documentation_patterns(content, filename)
            self._validate_bit_shift_and_type_casting(content, filename)

        # Complex parsing edge cases properly processed

    def _validate_function_pointer_arrays(self, content: str, filename: str) -> None:
        """Validate array of function pointers parsing."""
        patterns = [
            r"math_operation_t\s+global_math_ops\s*\[\s*10\s*\]",
            r"Process_Cfg_ProcessJobLite_acpfct\s*\[\s*PROCESSOR_CFG_MODULE_COUNT\s*\]",
            r"handler_table_t\s+table\s*\[\s*8\s*\]",
            r"math_ops_array_t\s+local_ops",
        ]

        for pattern in patterns:
            assert re.search(pattern, content), f"Missing function pointer array pattern: {pattern} in {filename}"

    def _validate_complex_macros(self, content: str, filename: str) -> None:
        """Validate complex macro usage patterns."""
        patterns = [
            r"COMPLEX_MACRO_FUNC\s*\(",
            r"PROCESS_ARRAY\s*\(",
            r"HANDLE_OPERATION\s*\(",
            r"TOSTRING\s*\(",
            r"CREATE_FUNC_NAME\s*\(",
        ]

        for pattern in patterns:
            assert re.search(pattern, content), f"Missing complex macro usage: {pattern} in {filename}"

    def _validate_processor_utility_macros(self, content: str, filename: str) -> None:
        """Validate processor utility macro usage patterns."""
        patterns = [
            r"UTILS_U16_TO_U8ARR_BIG_ENDIAN\s*\(",
            r"UTILS_U32_TO_U8ARR_BIG_ENDIAN\s*\(",
            r"UTILS_U8ARR_TO_U16_BIG_ENDIAN\s*\(",
            r"UTILS_U8ARR_TO_U32_BIG_ENDIAN\s*\(",
        ]

        for pattern in patterns:
            assert re.search(pattern, content), f"Missing processor utility macro: {pattern} in {filename}"

    def _validate_complex_typedefs(self, content: str, filename: str) -> None:
        """Validate complex typedef patterns."""
        patterns = [
            r"typedef\s+int\s*\(\s*\*\s*math_operation_t\s*\)\s*\(\s*int\s*,\s*int\s*\)",
            r"typedef\s+math_operation_t\s+math_ops_array_t\s*\[\s*10\s*\]",
            r"typedef\s+int\s*\(\s*\*\s*\(\s*\*complex_func_ptr_t\s*\)\s*\(\s*int\s*,\s*char\*\s*\)\s*\)\s*\(\s*double\s*,\s*void\*\s*\)",
            r"typedef\s+Std_ReturnType\s*\(\s*\*Process_Cfg_ProcessJobLite_fct\s*\)\s*\(\s*const\s+Process_JobType\s*\*job_pst\s*\)",
            r"typedef\s+Process_Cfg_ProcessJobLite_fct\s*\(\s*\*const\s+Process_Cfg_ProcessJobLite_acpfct\s*\[\s*PROCESSOR_CFG_MODULE_COUNT\s*\]\s*\)\s*\(\s*const\s+Process_JobType\s*\*job_pst\s*\)",
        ]

        for pattern in patterns:
            assert re.search(pattern, content), f"Missing complex typedef: {pattern} in {filename}"

    def _validate_complex_macro_definitions(self, content: str, filename: str) -> None:
        """Validate complex macro definition patterns."""
        patterns = [
            r"#define\s+COMPLEX_MACRO_FUNC\s*\([^)]+\)\s*\\",
            r"#define\s+PROCESS_ARRAY\s*\([^)]+\)\s*\\",
            r"#define\s+HANDLE_OPERATION\s*\([^)]+\)\s*\\",
            r"#define\s+CRYPTO_PRV_UTILS_U16_TO_U8ARR_BIG_ENDIAN\s*\([^)]+\)\s*\\",
            r"#define\s+CRYPTO_PRV_UTILS_U32_TO_U8ARR_BIG_ENDIAN\s*\([^)]+\)\s*\\",
        ]

        for pattern in patterns:
            assert re.search(pattern, content), f"Missing complex macro definition: {pattern} in {filename}"

    def _validate_const_array_of_function_pointers(
        self, content: str, filename: str
    ) -> None:
        """Validate const array of function pointers pattern."""
        pattern = r"Std_ReturnType\s*\(\s*\*const\s+Crypto_Cfg_ProcessJobLite_acpfct\s*\[\s*CRYPTO_CFG_MODULE_COUNT\s*\]\s*\)\s*\(\s*const\s+Crypto_JobType\s*\*job_pst\s*\)"

        assert re.search(pattern, content), f"Missing const array of function pointers: {pattern} in {filename}"

    def _validate_nasty_edge_case_functions(self, content: str, filename: str) -> None:
        """Validate nasty edge case function patterns."""
        if "complex.c" not in filename:
            return

        patterns = [
            r"test_crypto_job_processing\s*\(\s*\)",
            r"test_crypto_utility_macros\s*\(\s*\)",
            r"test_complex_macro\s*\(\s*int\s*\*\s*x\s*,\s*int\s*y\s*,\s*int\s*z\s*\)",
            r"test_process_array\s*\(\s*int\s*\*\s*arr\s*,\s*int\s*size\s*\)",
            r"test_handle_operation\s*\(\s*operation_type_t\s+op_type\s*,\s*int\s*\*\s*data\s*,\s*int\s*size\s*\)",
        ]

        for pattern in patterns:
            assert re.search(pattern, content), f"Missing nasty edge case function: {pattern} in {filename}"

    def _validate_complex_documentation_patterns(
        self, content: str, filename: str
    ) -> None:
        """Validate complex documentation patterns in macros."""
        if "complex.h" not in filename:
            return

        # Check for Doxygen-style documentation in macros
        doc_pattern = r"/\*\*\s*\*+\s*\*\\brief\s+[^*]+\*+\s*\*/"
        assert re.search(doc_pattern, content), f"Missing complex documentation pattern in macro in {filename}"

    def _validate_bit_shift_and_type_casting(self, content: str, filename: str) -> None:
        """Validate bit shift and type casting patterns."""
        patterns = [
            r"\(\s*uint8\s*\)\s*\(\s*\(\s*[^)]+\s*\)\s*\)",
            r"\(\s*uint8\s*\)\s*\(\s*\(\s*[^)]+\s*\)\s*>>\s*8U\s*\)",
            r"\(\s*uint16\s*\)\s*\(\s*\(\s*[^)]+\s*\)\s*<<\s*8U\s*\)",
            r"\(\s*uint32\s*\)\s*\(\s*\(\s*[^)]+\s*\)\s*<<\s*24U\s*\)",
        ]

        for pattern in patterns:
            assert re.search(pattern, content), f"Missing bit shift/type casting pattern: {pattern} in {filename}"

    def _validate_complex_specific_content(self, content: str, filename: str) -> None:
        """Validate specific content issues in complex.puml."""
        if "complex.puml" not in filename.lower():
            return

        # Validating complex.puml specific content issues
        issues_found = []

        # Check for corrupted macro content
        if re.search(r"} \\ \n \( x \)", content):
            issues_found.append("Corrupted macro content detected")

        if re.search(r"} \\ \n \n \n #define UTILS_U32_TO_U8ARR_BIG_ENDIAN", content):
            issues_found.append("Broken macro definitions detected")

        # Check for other corrupted content patterns
        if re.search(r"} \\ \n \n \n #define", content):
            issues_found.append("Additional broken macro definitions detected")

        if re.search(r"\\ \n } \n \( x \)", content):
            issues_found.append("Corrupted macro content with broken syntax")

        # Check for corrupted global variables
        if re.search(r"    \\+ char name$", content, re.MULTILINE):
            issues_found.append(
                "Corrupted global variable: 'char name' (should be struct field)"
            )
            # Found corrupted global 'char name'

        if re.search(r"    \\+ } processor_t$", content, re.MULTILINE):
            issues_found.append(
                "Corrupted global variable: '} processor_t' (should be struct field)"
            )
            # Found corrupted global '} processor_t'

        # Check for malformed struct fields
        if re.search(r"    \\+ struct \\{ \\\\n char\\[32\\] name", content):
            issues_found.append("Malformed nested struct field in complex_handler_t")

        # Check for missing proper struct field formatting
        if re.search(r"    \\+ char\\[32\\] name$", content, re.MULTILINE):
            issues_found.append(
                "Missing proper struct field formatting for nested struct"
            )

        # Check for missing typedefs
        missing_typedefs = [
            "processor_t",
            "complex_func_ptr_t",
            "data_item_t",
            "data_processor_array_t",
            "mixed_union_t",
            "operation_set_t",
            "complex_handler_t",
            "operation_type_t",
            "complex_callback_t",
            "handler_entry_t",
            "processor_module_enum_t",
            "Process_T",
        ]

        for typedef in missing_typedefs:
            if f'class "{typedef}" as TYPEDEF_{typedef.upper()}' not in content:
                issues_found.append(f"Missing typedef: {typedef}")

        # Check for missing functions
        missing_functions = [
            "init_math_operations",
            "test_complex_macro",
            "test_callback",
            "test_process_array",
            "test_stringify_macro",
            "test_processor_utility_macros",
            "test_handle_operation",
            "process_with_callbacks",
            "create_handler",
            "test_mixed_union",
            "test_operation_set",
            "test_handler_table",
            "test_processor_job_processing",
            "run_complex_tests",
            "ProcessorAdapter_Process",
            "ProcessorService_Process",
            "ProcessorHardware_Process",
        ]

        for func in missing_functions:
            if func not in content:
                issues_found.append(f"Missing function: {func}")

        # Check for missing global variables
        missing_globals = ["global_math_ops", "Process_Cfg_Process_acpfct"]

        for global_var in missing_globals:
            if global_var not in content:
                issues_found.append(f"Missing global variable: {global_var}")

        # Check for proper macro content
        expected_macros = [
            "COMPLEX_MACRO_FUNC",
            "PROCESS_ARRAY",
            "CREATE_FUNC_NAME",
            "STRINGIFY",
            "TOSTRING",
            "UTILS_U16_TO_U8ARR_BIG_ENDIAN",
            "UTILS_U32_TO_U8ARR_BIG_ENDIAN",
            "UTILS_U8ARR_TO_U16_BIG_ENDIAN",
            "UTILS_U8ARR_TO_U32_BIG_ENDIAN",
            "DEPRECATED",
            "HANDLE_OPERATION",
        ]

        for macro in expected_macros:
            if f"#define {macro}" not in content:
                issues_found.append(f"Missing or corrupted macro: {macro}")

        if issues_found:
            raise AssertionError(f"Complex.puml has {len(issues_found)} content issues: {', '.join(issues_found)}")
        # Complex.puml content validation passed

    def _validate_no_typedefs_in_header_or_source_classes(self, puml_lines, filename):
        """Assert that no typedefs (e.g., '+ struct', '+ enum', or any typedef) are generated in header or source class blocks (HEADER_xxx or main class blocks)."""
        in_header_or_main_class = False
        class_name = None
        for line in puml_lines:
            # Detect start of a header or main class
            if line.strip().startswith('class "') and (
                "as HEADER_" in line
                or "as " in line
                and "<<header>>" in line
                or "<<main>>" in line
            ):
                in_header_or_main_class = True
                class_name = line.strip()
                continue
            if in_header_or_main_class:
                if line.strip() == "}":
                    in_header_or_main_class = False
                    class_name = None
                    continue
                # Detect typedefs in header or main class
                if (
                    line.strip().startswith("+ struct")
                    or line.strip().startswith("+ enum")
                    or line.strip().startswith("+ typedef")
                ):
                    raise AssertionError(
                        f"Typedef found in header or source class block {class_name} in {filename}: {line.strip()}"
                    )

    def _validate_no_typedefs_sections_in_header_or_source_classes(
        self, content: str, filename: str
    ) -> None:
        """Assert that no '-- Typedefs --' sections exist in header or source class blocks."""
        lines = content.split("\n")
        in_header_or_source_class = False
        class_name = None

        for i, line in enumerate(lines):
            line = line.strip()

            # Detect start of a header or source class
            if line.startswith('class "') and (
                "as HEADER_" in line
                or ("as " in line and "<<header>>" in line)
                or ("as " in line and "<<main>>" in line)
                or (
                    "as " in line
                    and not "<<typedef>>" in line
                    and not "<<enum>>" in line
                )
            ):
                in_header_or_source_class = True
                class_name = line
                continue

            if in_header_or_source_class:
                if line == "}":
                    in_header_or_source_class = False
                    class_name = None
                    continue

                # Check for "-- Typedefs --" section in header or source class
                if line == "-- Typedefs --":
                    raise AssertionError(
                        f"'-- Typedefs --' section found in header or source class block in {filename}: {class_name}"
                    )

                # Also check for typedef values that might appear after the section
                if line.startswith("+ ") and (
                    "struct" in line or "enum" in line or "typedef" in line
                ):
                    # Look back a few lines to see if we're in a typedefs section
                    for j in range(max(0, i - 5), i):
                        if lines[j].strip() == "-- Typedefs --":
                            raise AssertionError(
                                f"Typedef value found in '-- Typedefs --' section of header or source class block in {filename}: {class_name} - {line}"
                            )

    def _validate_only_c_files_have_puml_diagrams(self, filename: str) -> None:
        """Assert that PlantUML files are only generated for C files, not header files."""
        # Extract the base name from the PlantUML filename
        puml_basename = filename.replace(".puml", "")

        # Check if this corresponds to a header file by looking for .h extension
        # The expected C files that should have PlantUML diagrams
        expected_c_files = [
            "typedef_test",  # typedef_test.c
            "geometry",  # geometry.c
            "logger",  # logger.c
            "math_utils",  # math_utils.c
            "sample",  # sample.c
            "preprocessed",  # preprocessed.c
            "complex",  # complex.c
        ]

        # Check if this is a header file by looking for common header patterns
        header_patterns = [
            "complex_example",  # complex_example.h
            "config",  # config.h
            "sample_h",  # sample.h (if generated separately)
            "logger_h",  # logger.h (if generated separately)
            "math_utils_h",  # math_utils.h (if generated separately)
            "geometry_h",  # geometry.h (if generated separately)
            "typedef_test_h",  # typedef_test.h (if generated separately)
            "preprocessed_h",  # preprocessed.h (if generated separately)
        ]

        # If the basename matches a header pattern, throw an error
        if puml_basename in header_patterns:
            raise AssertionError(
                f"PlantUML diagram generated for header file: {filename}. Only C files should have PlantUML diagrams generated."
            )

        # If the basename is not in expected C files, it might be a header file
        if puml_basename not in expected_c_files:
            # Check if there's a corresponding .h file in the source directory
            header_file_path = self.source_dir / f"{puml_basename}.h"
            if header_file_path.exists():
                raise AssertionError(
                    f"PlantUML diagram generated for header file: {filename} (corresponds to {puml_basename}.h). Only C files should have PlantUML diagrams generated."
                )

    def _validate_no_duplicate_relationships(
        self, relationships: List[Tuple[str, str, str]], filename: str
    ) -> None:
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
            raise AssertionError(
                f"Duplicate relationships found in {filename}: {duplicate_list}"
            )

    def _validate_relationship_formatting(
        self, relationships: List[Tuple[str, str, str]], filename: str
    ) -> None:
        """Assert that all relationships use consistent <<>> formatting."""
        invalid_relationships = []

        for source, target, rel_type in relationships:
            # Check if the relationship type has angle brackets
            if not rel_type.startswith("<<") or not rel_type.endswith(">>"):
                invalid_relationships.append(f"{source} -> {target} ({rel_type})")

        if invalid_relationships:
            invalid_list = ", ".join(invalid_relationships)
            raise AssertionError(
                f"Relationships without <<>> formatting found in {filename}: {invalid_list}"
            )

    def _validate_all_typedefs_have_relations(
        self, relationships: List[Tuple[str, str, str]], filename: str
    ) -> None:
        """Assert that all typedef objects have at least one relation (either <<declares>> or <<uses>>)."""
        # Read the PUML file to extract all typedef objects
        content = self.read_puml_file(filename)
        classes = self.extract_classes(content)

        # Find all typedef objects
        typedef_objects = []
        for uml_id, class_info in classes.items():
            if class_info["stereotype"] == "typedef":
                typedef_objects.append(uml_id)

        # Find all objects that have relations (either as source or target)
        objects_with_relations = set()
        for source, target, rel_type in relationships:
            objects_with_relations.add(source)
            objects_with_relations.add(target)

        # Check which typedef objects don't have any relations
        typedefs_without_relations = []
        for typedef_id in typedef_objects:
            if typedef_id not in objects_with_relations:
                typedefs_without_relations.append(typedef_id)

        if typedefs_without_relations:
            missing_list = ", ".join(typedefs_without_relations)
            raise AssertionError(
                f"Typedef objects without any relations found in {filename}: {missing_list}"
            )

        # All typedef objects have relations

    def _validate_all_relations_have_classes(
        self, relationships: List[Tuple[str, str, str]], filename: str
    ) -> None:
        """Assert that for every relation, both source and target classes exist in the diagram."""
        # Read the PUML file to extract all classes
        content = self.read_puml_file(filename)
        classes = self.extract_classes(content)

        # Get all class IDs that exist in the diagram
        existing_classes = set(classes.keys())

        # Check each relationship
        missing_classes = []
        for source, target, rel_type in relationships:
            if source not in existing_classes:
                missing_classes.append(
                    f"Source class '{source}' in relation '{source} -> {target} ({rel_type})'"
                )
            if target not in existing_classes:
                missing_classes.append(
                    f"Target class '{target}' in relation '{source} -> {target} ({rel_type})'"
                )

        if missing_classes:
            missing_list = "\n      ".join(missing_classes)
            raise AssertionError(
                f"Relations with missing classes found in {filename}:\n      {missing_list}"
            )

        # All relations have corresponding classes

    def _validate_all_headers_connected_to_main_class(
        self,
        relationships: List[Tuple[str, str, str]],
        classes: Dict[str, Dict],
        filename: str,
    ) -> None:
        """Assert that all header classes have a direct or indirect relationship to the main C class."""
        # Checking that all header classes are connected to main C class

        # Find the main C class (source class)
        main_class = None
        for uml_id, class_info in classes.items():
            if class_info["stereotype"] == "source":
                main_class = uml_id
                break

        if not main_class:
            assert False, f"No main C class found in {filename}"

        # Find all header classes
        header_classes = set()
        for uml_id, class_info in classes.items():
            if class_info["stereotype"] == "header":
                header_classes.add(uml_id)

        if not header_classes:
            # No header classes to validate
            return

        # Build a graph of relationships for path finding
        graph = {}
        for source, target, rel_type in relationships:
            if source not in graph:
                graph[source] = []
            if target not in graph:
                graph[target] = []
            graph[source].append(target)
            # For include relationships, also add reverse direction for path finding
            if rel_type == "<<include>>":
                graph[target].append(source)

        # Check each header class for connectivity to main class
        orphan_headers = []
        for header_class in header_classes:
            if not self._has_path_to_main_class(header_class, main_class, graph, set()):
                orphan_headers.append(header_class)

        if orphan_headers:
            raise AssertionError(
                f"Orphan header classes found in {filename}: {', '.join(orphan_headers)}"
            )

        # All header classes are connected to main C class

    def _has_path_to_main_class(
        self,
        current_class: str,
        main_class: str,
        graph: Dict[str, List[str]],
        visited: Set[str],
    ) -> bool:
        """Check if there's a path from current_class to main_class using DFS."""
        if current_class == main_class:
            return True

        if current_class in visited:
            return False

        visited.add(current_class)

        if current_class not in graph:
            return False

        for neighbor in graph[current_class]:
            if self._has_path_to_main_class(neighbor, main_class, graph, visited):
                return True

        return False

    def validate_file(self, filename: str) -> None:
        """Validate a single PUML file."""
        try:
            # Validating {filename}

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
            self.assert_relationships(relationships, classes, filename)

            # Validate specific content requirements
            self.assert_specific_content(content, filename)

            # {filename} validation completed successfully
        except Exception as e:
            # Fail the test for unexpected exceptions in PUML file validation
            assert False, f"Unexpected exception in validate_file for {filename}: {e}"

    def run_all_validations(self) -> None:
        """Run validation for all expected PUML files."""
        # Starting comprehensive validation
        # Output directory: {self.output_dir.absolute()}

        # Check if output directory exists
        assert (
            self.output_dir.exists()
        ), f"Output directory {self.output_dir} does not exist"

        # Validate PUML files
        # Validating generated PUML files

        # Find all PlantUML files in the output directory
        all_puml_files = list(self.output_dir.glob("*.puml"))
        puml_filenames = [f.name for f in all_puml_files]

        # Found {len(puml_filenames)} PlantUML files: {puml_filenames}

        # Validate each PUML file
        for filename in puml_filenames:
            try:
                self.validate_file(filename)
            except AssertionError as e:
                print(f"\n❌ Validation failed for {filename}: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"\n💥 Unexpected error validating {filename}: {e}")
                # Fail the test for unexpected exceptions
                assert False, f"Unexpected exception in PUML file validation for {filename}: {e}"

        # All validations completed successfully


def main():
    """Main function to run the validation."""
    try:
        validator = PUMLValidator()
        validator.run_all_validations()
    except AssertionError as e:
        print(f"\n❌ Validation failed: {e}")
        print(f"Current working directory: {Path.cwd().absolute()}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error in validation: {e}")
        print(f"Current working directory: {Path.cwd().absolute()}")
        # Fail the test for unexpected exceptions
        assert False, f"Unexpected exception in main validation: {e}"


if __name__ == "__main__":
    main()
