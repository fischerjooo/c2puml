#!/usr/bin/env python3
"""
Comprehensive PUML Validation Suite

This module provides detailed validation of generated PlantUML files against C source code.
It validates the structural integrity, content accuracy, and relationship correctness
of generated PUML diagrams, including include filtering functionality.

Validation Categories:
1. Structural Validation - @startuml/@enduml, class definitions, syntax
2. Content Validation - class content, naming conventions, stereotypes
3. Relationship Validation - connections between classes, duplicate detection
4. Pattern Validation - function signatures, typedefs, macros
5. File-specific Validation - expected content for each file type
6. Enum/Struct Validation - proper formatting of typedef content
7. Include Filtering Validation - validate include filter behavior and configurations

Usage:
    python3 test-example.py [--test-include-filtering]

Arguments:
    --test-include-filtering  Run include filtering validation tests with example configurations

Returns:
    0 if all validations pass
    1 if validation errors are found
"""

import os
import re
import sys
import json
import subprocess
import argparse
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class ValidationLevel(Enum):
    """Validation severity levels."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    level: ValidationLevel
    message: str
    file: str
    line_number: Optional[int] = None
    context: Optional[str] = None


@dataclass
class PUMLClass:
    """Represents a PlantUML class/enum definition."""

    name: str
    uml_id: str
    stereotype: str
    color: str
    body: str
    macros: List[str]
    functions: List[str]
    variables: List[str]
    fields: List[str]
    values: List[str]  # For enums


@dataclass
class PUMLRelationship:
    """Represents a PlantUML relationship."""

    source: str
    target: str
    type: str
    label: str


class PUMLValidator:
    """
    Comprehensive PlantUML file validator.

    This validator provides multi-level validation of PlantUML files generated
    from C source code, ensuring structural integrity, content accuracy, and
    adherence to PlantUML best practices.
    """

    def __init__(self):
        """Initialize the validator with expected values and patterns."""
        self.output_dir = self._find_output_directory()
        self.results: List[ValidationResult] = []
        self.expected_stereotypes = {"source", "header", "typedef"}
        self.expected_colors = {"LightBlue", "LightGreen", "LightYellow", "LightGray"}
        self.expected_relationships = {"<<include>>", "<<declares>>", "<<uses>>"}

    def _find_output_directory(self) -> Path:
        """Find the output directory path."""
        if Path.cwd().name == "example":
            return Path("../../artifacts/output_example")
        return Path("artifacts/output_example")

    def _add_result(
        self,
        level: ValidationLevel,
        message: str,
        file: str,
        line_number: Optional[int] = None,
        context: Optional[str] = None,
    ):
        """Add a validation result."""
        self.results.append(
            ValidationResult(level, message, file, line_number, context)
        )

    def parse_puml_file(self, filename: str) -> Dict[str, Any]:
        """Parse a PUML file and extract all components."""
        filepath = self.output_dir / filename

        if not filepath.exists():
            self._add_result(ValidationLevel.ERROR, f"File does not exist", filename)
            return {}

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self._add_result(
                ValidationLevel.ERROR, f"Failed to read file: {e}", filename
            )
            return {}

        return {
            "content": content,
            "classes": self._extract_classes(content, filename),
            "relationships": self._extract_relationships(content, filename),
            "startuml": self._validate_startuml_structure(content, filename),
        }

    def _extract_classes(self, content: str, filename: str) -> Dict[str, PUMLClass]:
        """Extract and parse all class definitions from PUML content."""
        classes = {}

        # Pattern for class definitions
        class_pattern = (
            r'class\s+"([^"]+)"\s+as\s+(\w+)\s+<<(\w+)>>\s+#(\w+)\s*\n\s*\{([^}]+)\}'
        )
        matches = re.finditer(class_pattern, content, re.DOTALL)

        for match in matches:
            name = match.group(1)
            uml_id = match.group(2)
            stereotype = match.group(3)
            color = match.group(4)
            body = match.group(5).strip()

            # Parse body content
            macros, functions, variables, fields = self._parse_class_body(
                body, stereotype
            )

            classes[uml_id] = PUMLClass(
                name=name,
                uml_id=uml_id,
                stereotype=stereotype,
                color=color,
                body=body,
                macros=macros,
                functions=functions,
                variables=variables,
                fields=fields,
                values=[],
            )

        # Pattern for enum definitions
        enum_pattern = (
            r'enum\s+"([^"]+)"\s+as\s+(\w+)\s+<<(\w+)>>\s+#(\w+)\s*\n\s*\{([^}]+)\}'
        )
        enum_matches = re.finditer(enum_pattern, content, re.DOTALL)

        for match in enum_matches:
            name = match.group(1)
            uml_id = match.group(2)
            stereotype = match.group(3)
            color = match.group(4)
            body = match.group(5).strip()

            # Parse enum values
            values = self._parse_enum_values(body)

            classes[uml_id] = PUMLClass(
                name=name,
                uml_id=uml_id,
                stereotype=stereotype,
                color=color,
                body=body,
                macros=[],
                functions=[],
                variables=[],
                fields=[],
                values=values,
            )

        return classes

    def _parse_class_body(
        self, body: str, stereotype: str
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Parse class body and categorize content."""
        lines = [line.strip() for line in body.split("\n") if line.strip()]

        macros = []
        functions = []
        variables = []
        fields = []

        current_section = None

        for line in lines:
            # Section headers
            if line.startswith("--") and line.endswith("--"):
                current_section = line.lower()
                continue

            # Skip comments and empty lines
            if line.startswith("'") or not line:
                continue

            # Categorize based on current section and content
            if "macro" in str(current_section):
                if line.startswith(("+", "-")) and "#define" in line:
                    macros.append(line)
            elif "function" in str(current_section):
                if line.startswith(("+", "-")) and "(" in line and ")" in line:
                    functions.append(line)
            elif "variable" in str(current_section) or "global" in str(current_section):
                if line.startswith(("+", "-")) and "(" not in line:
                    variables.append(line)
            else:
                # For typedef classes, everything is a field
                if stereotype == "typedef" and line.startswith("+"):
                    fields.append(line)
                elif line.startswith(("+", "-")):
                    # Auto-categorize based on content
                    if "#define" in line:
                        macros.append(line)
                    elif "(" in line and ")" in line:
                        functions.append(line)
                    else:
                        variables.append(line)

        return macros, functions, variables, fields

    def _parse_enum_values(self, body: str) -> List[str]:
        """Parse enum values from body."""
        lines = [line.strip() for line in body.split("\n") if line.strip()]
        values = []

        for line in lines:
            if line.startswith("+") and not line.startswith("--"):
                values.append(line)

        return values

    def _extract_relationships(
        self, content: str, filename: str
    ) -> List[PUMLRelationship]:
        """Extract all relationships from PUML content."""
        relationships = []

        # Pattern for relationships with labels
        patterns = [
            (r"(\w+)\s+-->\s+(\w+)\s+:\s+(<<[^>]+>>)", "-->"),  # Include relationships
            (
                r"(\w+)\s+\.\.>\s+(\w+)\s+:\s+(<<[^>]+>>)",
                "..>",
            ),  # Declares/Uses relationships
            (
                r"(\w+)\s+-->\s+(\w+)\s+:\s+([^<][^\n]*)",
                "-->",
            ),  # Non-bracketed includes
            (
                r"(\w+)\s+\.\.>\s+(\w+)\s+:\s+([^<][^\n]*)",
                "..>",
            ),  # Non-bracketed declares/uses
        ]

        for pattern, arrow_type in patterns:
            matches = re.findall(pattern, content)
            for source, target, label in matches:
                relationships.append(
                    PUMLRelationship(
                        source=source.strip(),
                        target=target.strip(),
                        type=arrow_type,
                        label=label.strip(),
                    )
                )

        return relationships

    def _validate_startuml_structure(self, content: str, filename: str) -> bool:
        """Validate basic PlantUML structure."""
        lines = content.split("\n")

        # Check for @startuml and @enduml
        has_start = any("@startuml" in line for line in lines)
        has_end = any("@enduml" in line for line in lines)

        if not has_start:
            self._add_result(
                ValidationLevel.ERROR, "Missing @startuml directive", filename
            )
            return False

        if not has_end:
            self._add_result(
                ValidationLevel.ERROR, "Missing @enduml directive", filename
            )
            return False

        # Check for proper diagram name
        start_line = next((line for line in lines if "@startuml" in line), None)
        if start_line and "@startuml" in start_line:
            expected_name = filename.replace(".puml", "")
            if expected_name not in start_line:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Diagram name should match filename: expected '{expected_name}'",
                    filename,
                )

        return True

    def validate_class_structure(self, classes: Dict[str, PUMLClass], filename: str):
        """Validate class definitions and structure."""
        for uml_id, cls in classes.items():
            # Validate stereotype
            if cls.stereotype not in self.expected_stereotypes:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Invalid stereotype '{cls.stereotype}' for class {uml_id}",
                    filename,
                )

            # Validate color
            if cls.color not in self.expected_colors:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Invalid color '{cls.color}' for class {uml_id}",
                    filename,
                )

            # Validate naming conventions
            self._validate_naming_conventions(cls, filename)

            # Validate content based on stereotype
            self._validate_class_content(cls, filename)

    def _validate_naming_conventions(self, cls: PUMLClass, filename: str):
        """Validate class naming conventions."""
        if cls.stereotype == "source":
            # Source files should be named after the filename in uppercase
            expected_name = cls.name.upper().replace("-", "_").replace(".", "_")
            if cls.uml_id != expected_name:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Source class {cls.uml_id} should be named {expected_name}",
                    filename,
                )

        elif cls.stereotype == "header":
            if not cls.uml_id.startswith("HEADER_"):
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Header class {cls.uml_id} should have HEADER_ prefix",
                    filename,
                )

        elif cls.stereotype == "typedef":
            if not cls.uml_id.startswith("TYPEDEF_"):
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Typedef class {cls.uml_id} should have TYPEDEF_ prefix",
                    filename,
                )

    def _validate_class_content(self, cls: PUMLClass, filename: str):
        """Validate class content based on stereotype."""
        if cls.stereotype == "source":
            self._validate_source_content(cls, filename)
        elif cls.stereotype == "header":
            self._validate_header_content(cls, filename)
        elif cls.stereotype == "typedef":
            self._validate_typedef_content(cls, filename)

    def _validate_source_content(self, cls: PUMLClass, filename: str):
        """Validate source file class content."""
        # Source files should not have + prefix for global elements
        for item in cls.variables + cls.functions:
            if item.startswith("+"):
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Source class {cls.uml_id} should not have + prefix: {item}",
                    filename,
                )

        # Macros in source files should have - prefix
        for macro in cls.macros:
            if not macro.startswith("-"):
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Source class macro should have - prefix: {macro}",
                    filename,
                )

    def _validate_header_content(self, cls: PUMLClass, filename: str):
        """Validate header file class content."""
        # Header files should have + prefix for all elements
        all_items = cls.macros + cls.functions + cls.variables
        for item in all_items:
            line = item.strip()
            if line and not line.startswith("'") and not line.startswith("--"):
                if not line.startswith("+"):
                    self._add_result(
                        ValidationLevel.ERROR,
                        f"Header class item should have + prefix: {item}",
                        filename,
                    )

    def _validate_typedef_content(self, cls: PUMLClass, filename: str):
        """Validate typedef class content."""
        # Typedef classes should have + prefix for all elements
        all_items = cls.fields + cls.values
        for item in all_items:
            line = item.strip()
            if line and not line.startswith("'") and not line.startswith("--"):
                if not line.startswith("+"):
                    self._add_result(
                        ValidationLevel.ERROR,
                        f"Typedef class item should have + prefix: {item}",
                        filename,
                    )

    def validate_relationships(
        self,
        relationships: List[PUMLRelationship],
        classes: Dict[str, PUMLClass],
        filename: str,
    ):
        """Validate relationships between classes."""
        # Check for duplicate relationships
        seen = set()
        for rel in relationships:
            key = (rel.source, rel.target, rel.label)
            if key in seen:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Duplicate relationship: {rel.source} -> {rel.target} ({rel.label})",
                    filename,
                )
            seen.add(key)

        # Validate relationship targets exist
        class_ids = set(classes.keys())
        for rel in relationships:
            if rel.source not in class_ids:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Relationship source '{rel.source}' not found in classes",
                    filename,
                )
            if rel.target not in class_ids:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Relationship target '{rel.target}' not found in classes",
                    filename,
                )

        # Validate relationship label format
        for rel in relationships:
            if rel.label and not (
                rel.label.startswith("<<") and rel.label.endswith(">>")
            ):
                if rel.label not in [
                    "include",
                    "declares",
                    "uses",
                ]:  # Allow some non-bracketed forms
                    self._add_result(
                        ValidationLevel.WARNING,
                        f"Relationship label should use <<>> format: {rel.label}",
                        filename,
                    )

    def validate_content_patterns(self, content: str, filename: str):
        """Validate specific content patterns and detect issues."""
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for malformed function signatures
            if "(" in line and ")" in line:
                self._validate_function_signature(line, filename, i)

            # Check for malformed typedefs
            if "typedef" in line:
                self._validate_typedef_line(line, filename, i)

            # Check for macro definitions
            if "#define" in line:
                self._validate_macro_definition(line, filename, i)

            # Check for PlantUML syntax issues
            self._validate_plantuml_syntax(line, filename, i)

    def _validate_plantuml_syntax(self, line: str, filename: str, line_num: int):
        """Validate PlantUML-specific syntax patterns."""
        line_stripped = line.strip()

        # Check for proper class definition syntax
        if line_stripped.startswith('class "') and " as " in line:
            if not re.match(
                r'class\s+"[^"]+"\s+as\s+\w+\s+<<\w+>>\s+#\w+', line_stripped
            ):
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Class definition syntax may be malformed: {line_stripped}",
                    filename,
                    line_num,
                )

        # Check for proper enum definition syntax
        if line_stripped.startswith('enum "') and " as " in line:
            if not re.match(
                r'enum\s+"[^"]+"\s+as\s+\w+\s+<<\w+>>\s+#\w+', line_stripped
            ):
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Enum definition syntax may be malformed: {line_stripped}",
                    filename,
                    line_num,
                )

        # Check for proper relationship syntax
        if ("-->" in line or "..>" in line) and ":" in line:
            if not re.match(r"\w+\s+(-->|\.\.>)\s+\w+\s+:", line_stripped):
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Relationship syntax may be malformed: {line_stripped}",
                    filename,
                    line_num,
                )

    def _validate_function_signature(self, line: str, filename: str, line_num: int):
        """Validate function signature formatting."""
        # Check for malformed function pointers with specific patterns
        if "* *" in line and not ("void * *" in line or "char * *" in line):
            self._add_result(
                ValidationLevel.WARNING,
                f"Possible malformed function pointer: {line.strip()}",
                filename,
                line_num,
            )

        # Check for incomplete parameter lists - but allow for function pointers with complex syntax
        open_parens = line.count("(")
        close_parens = line.count(")")
        if open_parens != close_parens:
            # Special case for function pointers that might be truncated
            if "unknown unnamed" in line or line.strip().endswith("("):
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Function signature appears truncated: {line.strip()}",
                    filename,
                    line_num,
                )
            else:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Unbalanced parentheses in function: {line.strip()}",
                    filename,
                    line_num,
                )

    def _validate_typedef_line(self, line: str, filename: str, line_num: int):
        """Validate typedef formatting."""
        # Check for repeated typedef keyword
        if line.count("typedef") > 1:
            self._add_result(
                ValidationLevel.WARNING,
                f"Multiple 'typedef' keywords in line: {line.strip()}",
                filename,
                line_num,
            )

        # Check for incomplete struct/enum definitions
        if "typedef struct" in line and "{" not in line and "}" not in line:
            self._add_result(
                ValidationLevel.INFO,
                f"Simple typedef struct: {line.strip()}",
                filename,
                line_num,
            )

    def _validate_macro_definition(self, line: str, filename: str, line_num: int):
        """Validate macro definition formatting."""
        # Check for proper #define format
        if not re.match(r"^\s*[+\-]?\s*#define\s+\w+", line):
            self._add_result(
                ValidationLevel.WARNING,
                f"Possibly malformed macro definition: {line.strip()}",
                filename,
                line_num,
            )

    def validate_file_specific_requirements(
        self, parsed_data: Dict[str, Any], filename: str
    ):
        """Validate file-specific requirements."""
        base_name = filename.replace(".puml", "")
        classes = parsed_data.get("classes", {})
        content = parsed_data.get("content", "")

        # Validate expected classes exist
        expected_classes = self._get_expected_classes(base_name)
        for expected_class in expected_classes:
            if expected_class not in classes:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Expected class '{expected_class}' not found",
                    filename,
                )

        # Validate file-specific content patterns
        self._validate_file_specific_content(base_name, content, classes, filename)

    def _validate_file_specific_content(
        self, base_name: str, content: str, classes: Dict[str, PUMLClass], filename: str
    ):
        """Validate specific content requirements for each file type."""
        if base_name == "complex":
            self._validate_complex_file_content(content, classes, filename)
        elif base_name == "typedef_test":
            self._validate_typedef_test_content(content, classes, filename)
        elif base_name == "sample":
            self._validate_sample_file_content(content, classes, filename)
        elif base_name == "geometry":
            self._validate_geometry_file_content(content, classes, filename)
        elif base_name == "logger":
            self._validate_logger_file_content(content, classes, filename)
        elif base_name == "math_utils":
            self._validate_math_utils_content(content, classes, filename)
        elif base_name == "preprocessed":
            self._validate_preprocessed_content(content, classes, filename)
        elif base_name == "sample2":
            self._validate_sample2_file_content(content, classes, filename)
        elif base_name == "transformed":
            self._validate_transformed_file_content(content, classes, filename)

    def _validate_complex_file_content(
        self, content: str, classes: Dict[str, PUMLClass], filename: str
    ):
        """Validate complex.puml specific content."""
        # Check for essential macros
        essential_macros = [
            "COMPLEX_MACRO_FUNC",
            "PROCESS_ARRAY",
            "CREATE_FUNC_NAME",
            "STRINGIFY",
            "TOSTRING",
            "UTILS_U16_TO_U8ARR_BIG_ENDIAN",
            "UTILS_U32_TO_U8ARR_BIG_ENDIAN",
            "HANDLE_OPERATION",
        ]

        for macro in essential_macros:
            if macro not in content:
                self._add_result(
                    ValidationLevel.ERROR, f"Missing essential macro: {macro}", filename
                )

        # Check for essential functions
        essential_functions = [
            "test_complex_macro",
            "test_process_array",
            "test_handle_operation",
            "test_processor_job_processing",
            "run_complex_tests",
            "process_with_callbacks",
        ]

        for func in essential_functions:
            if func not in content:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Missing expected function: {func}",
                    filename,
                )

        # Check for essential typedefs
        essential_typedefs = [
            "TYPEDEF_PROCESS_T",
            "TYPEDEF_MATH_OPERATION_T",
            "TYPEDEF_COMPLEX_HANDLER_T",
        ]

        for typedef in essential_typedefs:
            if typedef not in classes:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Missing essential typedef: {typedef}",
                    filename,
                )

    def _validate_typedef_test_content(
        self, content: str, classes: Dict[str, PUMLClass], filename: str
    ):
        """Validate typedef_test.puml specific content."""
        essential_typedefs = [
            "TYPEDEF_MYLEN",
            "TYPEDEF_MYINT",
            "TYPEDEF_MYSTRING",
            "TYPEDEF_MYBUFFER",
            "TYPEDEF_MYCOMPLEX",
            "TYPEDEF_COLOR_T",
        ]

        for typedef in essential_typedefs:
            if typedef not in classes:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Missing essential typedef: {typedef}",
                    filename,
                )

        # Check for enum values
        essential_enum_values = ["COLOR_RED", "COLOR_GREEN", "COLOR_BLUE"]
        for enum_val in essential_enum_values:
            if enum_val not in content:
                self._add_result(
                    ValidationLevel.WARNING, f"Missing enum value: {enum_val}", filename
                )

    def _validate_sample_file_content(
        self, content: str, classes: Dict[str, PUMLClass], filename: str
    ):
        """Validate sample.puml specific content."""
        essential_functions = ["calculate_sum", "create_point", "process_point", "main"]
        for func in essential_functions:
            if func not in content:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Missing expected function: {func}",
                    filename,
                )

        # Check that filtered_header.h content is not present in the PUML file
        filtered_content_indicators = [
            "filtered_header",
            "FILTERED_CONSTANT",
            "FILTERED_MACRO",
            "filtered_struct_t",
            "filtered_enum_t",
            "filtered_function1",
            "filtered_function2",
            "filtered_function3",
            "filtered_global_var",
            "filtered_global_string",
        ]

        for indicator in filtered_content_indicators:
            if indicator in content:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Filtered content '{indicator}' from filtered_header.h should not appear in PUML file",
                    filename,
                )

    def _validate_sample2_file_content(
        self, content: str, classes: Dict[str, PUMLClass], filename: str
    ):
        """Validate sample2.puml specific content."""
        essential_functions = ["calculate_sum", "create_point", "process_point", "main"]
        for func in essential_functions:
            if func not in content:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Missing expected function: {func}",
                    filename,
                )

        # Check that filtered_header.h content IS present in the PUML file (opposite of sample.puml)
        filtered_content_indicators = [
            "filtered_header",
            "FILTERED_CONSTANT",
            "FILTERED_MACRO",
            "filtered_struct_t",
            "filtered_enum_t",
            "filtered_function1",
            "filtered_function2",
            "filtered_function3",
            "filtered_global_var",
            "filtered_global_string",
        ]

        found_indicators = []
        for indicator in filtered_content_indicators:
            if indicator in content:
                found_indicators.append(indicator)

        if not found_indicators:
            self._add_result(
                ValidationLevel.ERROR,
                f"Filtered content from filtered_header.h should appear in sample2.puml but none found. Expected: {filtered_content_indicators}",
                filename,
            )

    def _validate_geometry_file_content(
        self, content: str, classes: Dict[str, PUMLClass], filename: str
    ):
        """Validate geometry.puml specific content."""
        essential_functions = ["create_triangle", "triangle_area"]
        for func in essential_functions:
            if func not in content:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Missing expected function: {func}",
                    filename,
                )

    def _validate_logger_file_content(
        self, content: str, classes: Dict[str, PUMLClass], filename: str
    ):
        """Validate logger.puml specific content."""
        essential_functions = ["log_message", "set_log_callback"]
        for func in essential_functions:
            if func not in content:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Missing expected function: {func}",
                    filename,
                )

    def _validate_math_utils_content(
        self, content: str, classes: Dict[str, PUMLClass], filename: str
    ):
        """Validate math_utils.puml specific content."""
        essential_functions = ["add", "subtract", "average"]
        for func in essential_functions:
            if func not in content:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Missing expected function: {func}",
                    filename,
                )

    def _validate_preprocessed_content(
        self, content: str, classes: Dict[str, PUMLClass], filename: str
    ):
        """Validate preprocessed.puml specific content."""
        # Check for preprocessing artifacts
        preprocessing_indicators = ["#if", "#ifdef", "#define"]
        has_preprocessing = any(
            indicator in content for indicator in preprocessing_indicators
        )
        if not has_preprocessing:
            self._add_result(
                ValidationLevel.INFO, "No preprocessing directives found", filename
            )

    def validate_enum_content(self, classes: Dict[str, PUMLClass], filename: str):
        """Validate enum content and structure."""
        for uml_id, cls in classes.items():
            if cls.stereotype == "typedef" and cls.values:
                # This is an enum typedef
                self._validate_enum_values(cls, filename)

    def _validate_enum_values(self, enum_class: PUMLClass, filename: str):
        """Validate individual enum values."""
        for value in enum_class.values:
            # Check for proper enum value format
            if not value.startswith("+"):
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Enum value should start with +: {value}",
                    filename,
                )

            # Check for enum value naming conventions
            value_name = value.replace("+", "").strip()
            if "=" in value_name:
                name_part = value_name.split("=")[0].strip()
                if not name_part.isupper():
                    self._add_result(
                        ValidationLevel.WARNING,
                        f"Enum value should be uppercase: {name_part}",
                        filename,
                    )

    def validate_struct_content(self, classes: Dict[str, PUMLClass], filename: str):
        """Validate struct content and fields."""
        for uml_id, cls in classes.items():
            if cls.stereotype == "typedef" and cls.fields and not cls.values:
                # This is a struct typedef
                self._validate_struct_fields(cls, filename)

    def _validate_struct_fields(self, struct_class: PUMLClass, filename: str):
        """Validate individual struct fields."""
        for field in struct_class.fields:
            # Check for proper struct field format
            if not field.startswith("+"):
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Struct field should start with +: {field}",
                    filename,
                )

            # Check for common field patterns
            field_content = field.replace("+", "").strip()

            # Validate array syntax
            if "[" in field_content and "]" in field_content:
                self._validate_array_field(field_content, filename)

    def _validate_array_field(self, field_content: str, filename: str):
        """Validate array field syntax."""
        # Check for proper array format: type[size] name or type name[size]
        if " [ " in field_content or " ] " in field_content:
            self._add_result(
                ValidationLevel.WARNING,
                f"Array field has spaces around brackets: {field_content}",
                filename,
            )

    def _get_expected_classes(self, base_name: str) -> List[str]:
        """Get expected classes for a specific file."""
        # This could be loaded from a configuration file or database
        expected_classes_map = {
            "typedef_test": ["TYPEDEF_TEST", "TYPEDEF_MYLEN", "TYPEDEF_MYINT"],
            "complex": ["COMPLEX", "HEADER_COMPLEX", "TYPEDEF_PROCESS_T"],
            "sample": ["SAMPLE", "HEADER_CONFIG", "TYPEDEF_POINT_T"],
            "geometry": ["GEOMETRY", "HEADER_GEOMETRY", "TYPEDEF_TRIANGLE_T"],
            "logger": ["LOGGER", "HEADER_LOGGER", "TYPEDEF_LOG_LEVEL_T"],
            "math_utils": ["MATH_UTILS", "HEADER_MATH_UTILS", "TYPEDEF_REAL_T"],
            "preprocessed": ["PREPROCESSED", "HEADER_PREPROCESSED"],
        }
        return expected_classes_map.get(base_name, [])

    def validate_file(self, filename: str) -> bool:
        """Validate a single PUML file comprehensively."""
        print(f"Validating {filename}...")

        # Parse the file
        parsed_data = self.parse_puml_file(filename)
        if not parsed_data:
            return False

        # Run all validations
        classes = parsed_data.get("classes", {})
        relationships = parsed_data.get("relationships", [])
        content = parsed_data.get("content", "")

        # Print validation summary for this file
        source_classes = [c for c in classes.values() if c.stereotype == "source"]
        header_classes = [c for c in classes.values() if c.stereotype == "header"]
        typedef_classes = [c for c in classes.values() if c.stereotype == "typedef"]

        print(
            f"  Found: {len(source_classes)} source, {len(header_classes)} header, {len(typedef_classes)} typedef classes, {len(relationships)} relationships"
        )

        self.validate_class_structure(classes, filename)
        self.validate_relationships(relationships, classes, filename)
        self.validate_content_patterns(content, filename)
        self.validate_enum_content(classes, filename)
        self.validate_struct_content(classes, filename)
        self.validate_file_specific_requirements(parsed_data, filename)

        return True

    def run_all_validations(self) -> bool:
        """Run validation for all PUML files."""
        print(f"Starting comprehensive PUML validation...")
        print(f"Output directory: {self.output_dir.absolute()}")

        if not self.output_dir.exists():
            print(f"❌ Output directory {self.output_dir} does not exist")
            return False

        # Find all PlantUML files
        puml_files = list(self.output_dir.glob("*.puml"))
        if not puml_files:
            print("❌ No PlantUML files found")
            return False

        print(f"Found {len(puml_files)} PlantUML files")

        # Validate each file
        all_valid = True
        for puml_file in puml_files:
            if not self.validate_file(puml_file.name):
                all_valid = False

        # Report results
        self._report_results()

        return (
            all_valid
            and len([r for r in self.results if r.level == ValidationLevel.ERROR]) == 0
        )

    def _validate_transformed_file_content(
        self, content: str, classes: Dict[str, PUMLClass], filename: str
    ):
        """Validate transformed.puml specific content to test transformation features."""
        # These elements should be REMOVED by transformations
        removed_elements = [
            # Legacy typedefs that should be removed
            "legacy_int_t", "legacy_string_t", "old_point_t", "legacy_uint_t", "legacy_handle_t",
            # Test functions that should be removed 
            "test_function_one", "test_function_two", "test_helper_function",
            # Debug functions that should be removed
            "debug_log", "debug_validate_config",
            # Deprecated macros that should be removed
            "DEPRECATED_MAX_SIZE", "OLD_VERSION", "LEGACY_DEBUG", "LEGACY_BUFFER_SIZE", 
            "OLD_API_VERSION", "DEPRECATED_FLAG",
            # Old global variables that should be removed
            "old_global_counter", "deprecated_message", "old_error_code", "legacy_path",
            # Legacy structures that should be removed
            "legacy_data", "legacy_node",
            # Old enums that should be removed  
            "old_status", "legacy_color", "old_error_type", "legacy_mode",
            # Old unions that should be removed
            "old_value", "old_variant",
            # Includes that should be removed
            "time.h", "unistd.h"
        ]
        
        for element in removed_elements:
            if element in content:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Element '{element}' should have been removed by transformations but is still present",
                    filename,
                )
        
        # These elements should be PRESENT (not removed)
        preserved_elements = [
            "main", "keep_this_function", "initialize_system", "process_data", 
            "cleanup_resources", "point3d_t", "status_t"
        ]
        
        for element in preserved_elements:
            if element not in content:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Element '{element}' should have been preserved but is missing",
                    filename,
                )
        
        # These elements should be RENAMED (check for new names)
        renamed_elements = {
            "old_config_t": "config_t",
            "deprecated_print_info": "legacy_print_info", 
            "OLD_API_VERSION": "LEGACY_API_VERSION",
            "legacy_path": "system_path",
            "old_config": "modern_config"
        }
        
        for old_name, new_name in renamed_elements.items():
            if old_name in content:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"Element '{old_name}' should have been renamed to '{new_name}' but old name is still present",
                    filename,
                )
            if new_name not in content:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"Renamed element '{new_name}' (from '{old_name}') should be present but is missing",
                    filename,
                )
        
        # Validate that file selection worked - transformations should only apply to transformed.c/h
        # This would be validated by checking that other files don't have these transformations applied

    def _report_results(self):
        """Report validation results."""
        errors = [r for r in self.results if r.level == ValidationLevel.ERROR]
        warnings = [r for r in self.results if r.level == ValidationLevel.WARNING]
        infos = [r for r in self.results if r.level == ValidationLevel.INFO]

        print(f"\n📊 Validation Summary:")
        print(f"   Errors: {len(errors)}")
        print(f"   Warnings: {len(warnings)}")
        print(f"   Info: {len(infos)}")

        if errors:
            print(f"\n❌ Errors:")
            for error in errors:
                location = f"{error.file}"
                if error.line_number:
                    location += f":{error.line_number}"
                print(f"   {location}: {error.message}")

        if warnings:
            print(f"\n⚠️  Warnings:")
            for warning in warnings:
                location = f"{warning.file}"
                if warning.line_number:
                    location += f":{warning.line_number}"
                print(f"   {location}: {warning.message}")

        if infos and len(infos) <= 5:  # Only show a few info messages to avoid clutter
            print(f"\nℹ️  Info:")
            for info in infos[:5]:
                location = f"{info.file}"
                if info.line_number:
                    location += f":{info.line_number}"
                print(f"   {location}: {info.message}")

        if not errors and not warnings:
            print("✅ All validations passed!")


class IncludeFilteringValidator:
    """Validator for include filtering functionality using example configurations."""
    
    def __init__(self):
        """Initialize the include filtering validator."""
        self.results: List[ValidationResult] = []
        self.example_dir = Path("tests/example")
        if not self.example_dir.exists():
            self.example_dir = Path(".")
            
    def _add_result(self, level: ValidationLevel, message: str, context: str = ""):
        """Add a validation result for include filtering."""
        self.results.append(ValidationResult(level, message, "include_filtering", context=context))
    
    def _run_c2puml_with_config(self, config_file: str, output_suffix: str = "") -> bool:
        """Run c2puml with a specific configuration file."""
        try:
            config_path = self.example_dir / config_file
            if not config_path.exists():
                self._add_result(ValidationLevel.ERROR, f"Configuration file not found: {config_file}")
                return False
                
            output_dir = Path("output") / f"include_filtering{output_suffix}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Run c2puml with the configuration
            cmd = [
                "python", "-m", "c2puml.main",
                "--config", str(config_path),
                "--output", str(output_dir)
            ]
            
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            
            if result.returncode != 0:
                self._add_result(
                    ValidationLevel.ERROR, 
                    f"c2puml failed with config {config_file}: {result.stderr}",
                    result.stdout
                )
                return False
                
            self._add_result(ValidationLevel.INFO, f"Successfully generated output with {config_file}")
            return True
            
        except Exception as e:
            self._add_result(ValidationLevel.ERROR, f"Failed to run c2puml with {config_file}: {e}")
            return False
    
    def _validate_include_filtering_output(self, output_dir: str, expected_includes: Dict[str, List[str]], 
                                         filtered_includes: Dict[str, List[str]]) -> bool:
        """Validate that include filtering worked as expected."""
        output_path = Path(output_dir)
        success = True
        
        for file_pattern, expected_list in expected_includes.items():
            puml_files = list(output_path.glob(f"*{file_pattern}*.puml"))
            if not puml_files:
                self._add_result(ValidationLevel.ERROR, f"No PUML files found matching {file_pattern}")
                success = False
                continue
                
            for puml_file in puml_files:
                with open(puml_file, 'r') as f:
                    content = f.read()
                    
                # Check that expected includes are present
                for expected_include in expected_list:
                    if expected_include not in content:
                        self._add_result(
                            ValidationLevel.ERROR,
                            f"Expected include '{expected_include}' not found in {puml_file.name}"
                        )
                        success = False
                        
                # Check that filtered includes are NOT present
                filtered_list = filtered_includes.get(file_pattern, [])
                for filtered_include in filtered_list:
                    if filtered_include in content:
                        self._add_result(
                            ValidationLevel.ERROR,
                            f"Filtered include '{filtered_include}' should not be present in {puml_file.name}"
                        )
                        success = False
                        
        return success
    
    def test_network_filtering(self) -> bool:
        """Test network-specific include filtering."""
        print("Testing network-specific include filtering...")
        
        if not self._run_c2puml_with_config("config_network_filtering.json", "_network"):
            return False
            
        # Define expected and filtered includes for network configuration
        expected_includes = {
            "network": ["sys/socket.h", "netinet/in.h", "arpa/inet.h", "common.h"],
            "application": ["network.h", "common.h", "stdio.h", "signal.h"]
        }
        
        filtered_includes = {
            "network": ["sqlite3.h", "mysql/mysql.h", "postgresql/libpq-fe.h"],
            "application": ["database.h", "unistd.h"]
        }
        
        return self._validate_include_filtering_output(
            "output/include_filtering_network", expected_includes, filtered_includes
        )
    
    def test_database_filtering(self) -> bool:
        """Test database-specific include filtering."""
        print("Testing database-specific include filtering...")
        
        if not self._run_c2puml_with_config("config_database_filtering.json", "_database"):
            return False
            
        expected_includes = {
            "database": ["sqlite3.h", "mysql/mysql.h", "postgresql/libpq-fe.h", "string.h"],
            "application": ["database.h", "common.h", "stdio.h"]
        }
        
        filtered_includes = {
            "database": ["sys/socket.h", "netinet/in.h", "arpa/inet.h"],
            "application": ["network.h", "signal.h", "unistd.h"]
        }
        
        return self._validate_include_filtering_output(
            "output/include_filtering_database", expected_includes, filtered_includes
        )
    
    def test_comprehensive_filtering(self) -> bool:
        """Test comprehensive include filtering with complex patterns."""
        print("Testing comprehensive include filtering...")
        
        if not self._run_c2puml_with_config("config_comprehensive_filtering.json", "_comprehensive"):
            return False
            
        expected_includes = {
            "network": ["sys/socket.h", "netinet/in.h", "arpa/inet.h"],
            "database": ["sqlite3.h", "mysql/mysql.h", "postgresql/libpq-fe.h"],
            "application": ["network.h", "database.h", "stdio.h", "stdlib.h"]
        }
        
        # In comprehensive mode, fewer items should be filtered
        filtered_includes = {
            "network": [],  # Most network includes should be allowed
            "database": [],  # Most database includes should be allowed
            "application": []  # Most application includes should be allowed
        }
        
        return self._validate_include_filtering_output(
            "output/include_filtering_comprehensive", expected_includes, filtered_includes
        )
    
    def validate_include_filter_patterns(self) -> bool:
        """Validate various include filter regex patterns."""
        print("Validating include filter regex patterns...")
        
        test_patterns = [
            (r"^sys/.*", ["sys/socket.h", "sys/types.h"], ["stdio.h", "stdlib.h"]),
            (r"^std.*\.h$", ["stdio.h", "stdlib.h", "string.h"], ["sys/socket.h", "unistd.h"]),
            (r"^.*sql.*\.h$", ["mysql.h", "postgresql.h"], ["stdio.h", "network.h"]),
            (r"^(stdio|stdlib|string)\.h$", ["stdio.h", "stdlib.h", "string.h"], ["math.h", "unistd.h"])
        ]
        
        success = True
        for pattern, should_match, should_not_match in test_patterns:
            try:
                import re
                compiled_pattern = re.compile(pattern)
                
                # Test positive matches
                for item in should_match:
                    if not compiled_pattern.search(item):
                        self._add_result(
                            ValidationLevel.ERROR,
                            f"Pattern '{pattern}' should match '{item}' but doesn't"
                        )
                        success = False
                        
                # Test negative matches
                for item in should_not_match:
                    if compiled_pattern.search(item):
                        self._add_result(
                            ValidationLevel.ERROR,
                            f"Pattern '{pattern}' should not match '{item}' but does"
                        )
                        success = False
                        
            except re.error as e:
                self._add_result(ValidationLevel.ERROR, f"Invalid regex pattern '{pattern}': {e}")
                success = False
                
        return success
    
    def run_include_filtering_tests(self) -> bool:
        """Run all include filtering validation tests."""
        print("🔍 Starting Include Filtering Validation Tests...")
        
        # Check if example source files exist
        source_dir = self.example_dir / "source"
        if not source_dir.exists():
            self._add_result(ValidationLevel.ERROR, "Example source directory not found")
            return False
            
        # Check if configuration files exist
        required_configs = [
            "config_network_filtering.json",
            "config_database_filtering.json", 
            "config_comprehensive_filtering.json"
        ]
        
        for config in required_configs:
            if not (self.example_dir / config).exists():
                self._add_result(ValidationLevel.ERROR, f"Required config file missing: {config}")
                return False
        
        # Run individual tests
        tests = [
            ("Pattern Validation", self.validate_include_filter_patterns),
            ("Network Filtering", self.test_network_filtering),
            ("Database Filtering", self.test_database_filtering),
            ("Comprehensive Filtering", self.test_comprehensive_filtering),
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name} test...")
            try:
                if not test_func():
                    all_passed = False
                    print(f"❌ {test_name} test failed")
                else:
                    print(f"✅ {test_name} test passed")
            except Exception as e:
                self._add_result(ValidationLevel.ERROR, f"{test_name} test crashed: {e}")
                all_passed = False
                print(f"💥 {test_name} test crashed: {e}")
        
        # Report results
        self._report_include_filtering_results()
        
        return all_passed and len([r for r in self.results if r.level == ValidationLevel.ERROR]) == 0
    
    def _report_include_filtering_results(self):
        """Report include filtering validation results."""
        errors = [r for r in self.results if r.level == ValidationLevel.ERROR]
        warnings = [r for r in self.results if r.level == ValidationLevel.WARNING]
        infos = [r for r in self.results if r.level == ValidationLevel.INFO]
        
        print(f"\n📊 Include Filtering Validation Summary:")
        print(f"   Errors: {len(errors)}")
        print(f"   Warnings: {len(warnings)}")  
        print(f"   Info: {len(infos)}")
        
        if errors:
            print(f"\n❌ Include Filtering Errors:")
            for error in errors:
                print(f"   {error.message}")
                if error.context:
                    print(f"      Context: {error.context}")
                    
        if warnings:
            print(f"\n⚠️  Include Filtering Warnings:")
            for warning in warnings:
                print(f"   {warning.message}")
                
        if not errors and not warnings:
            print("✅ All include filtering validations passed!")


def main():
    """Main function to run the validation."""
    parser = argparse.ArgumentParser(description="Comprehensive PUML validation suite")
    parser.add_argument("--test-include-filtering", action="store_true", 
                       help="Run include filtering validation tests")
    args = parser.parse_args()
    
    try:
        overall_success = True
        
        if args.test_include_filtering:
            print("🔍 Running Include Filtering Tests...")
            include_validator = IncludeFilteringValidator()
            include_success = include_validator.run_include_filtering_tests()
            overall_success = overall_success and include_success
        else:
            print("📋 Running Standard PUML Validation...")
            validator = PUMLValidator()
            standard_success = validator.run_all_validations()
            overall_success = overall_success and standard_success

        if not overall_success:
            print("\n❌ Validation failed")
            sys.exit(1)
        else:
            print("\n✅ All validations passed successfully!")

    except Exception as e:
        print(f"\n💥 Unexpected error in validation: {e}")
        print(f"Current working directory: {Path.cwd().absolute()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
