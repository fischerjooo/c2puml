#!/usr/bin/env python3
"""
Comprehensive PUML Validation Suite

This module provides detailed validation of generated PlantUML files against C source code.
It validates the structural integrity, content accuracy, and relationship correctness
of generated PUML diagrams.

Validation Categories:
1. Structural Validation - @startuml/@enduml, class definitions, syntax
2. Content Validation - class content, naming conventions, stereotypes  
3. Relationship Validation - connections between classes, duplicate detection
4. Pattern Validation - function signatures, typedefs, macros
5. File-specific Validation - expected content for each file type
6. Enum/Struct Validation - proper formatting of typedef content

Usage:
    python3 assertions.py

Returns:
    0 if all validations pass
    1 if validation errors are found
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


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
            return Path("../output")
        return Path("output")

    def _add_result(self, level: ValidationLevel, message: str, file: str, 
                   line_number: Optional[int] = None, context: Optional[str] = None):
        """Add a validation result."""
        self.results.append(ValidationResult(level, message, file, line_number, context))

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
            self._add_result(ValidationLevel.ERROR, f"Failed to read file: {e}", filename)
            return {}

        return {
            "content": content,
            "classes": self._extract_classes(content, filename),
            "relationships": self._extract_relationships(content, filename),
            "startuml": self._validate_startuml_structure(content, filename)
        }

    def _extract_classes(self, content: str, filename: str) -> Dict[str, PUMLClass]:
        """Extract and parse all class definitions from PUML content."""
        classes = {}
        
        # Pattern for class definitions
        class_pattern = r'class\s+"([^"]+)"\s+as\s+(\w+)\s+<<(\w+)>>\s+#(\w+)\s*\n\s*\{([^}]+)\}'
        matches = re.finditer(class_pattern, content, re.DOTALL)
        
        for match in matches:
            name = match.group(1)
            uml_id = match.group(2)
            stereotype = match.group(3)
            color = match.group(4)
            body = match.group(5).strip()
            
            # Parse body content
            macros, functions, variables, fields = self._parse_class_body(body, stereotype)
            
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
                values=[]
            )

        # Pattern for enum definitions
        enum_pattern = r'enum\s+"([^"]+)"\s+as\s+(\w+)\s+<<(\w+)>>\s+#(\w+)\s*\n\s*\{([^}]+)\}'
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
                values=values
            )
            
        return classes

    def _parse_class_body(self, body: str, stereotype: str) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Parse class body and categorize content."""
        lines = [line.strip() for line in body.split('\n') if line.strip()]
        
        macros = []
        functions = []
        variables = []
        fields = []
        
        current_section = None
        
        for line in lines:
            # Section headers
            if line.startswith('--') and line.endswith('--'):
                current_section = line.lower()
                continue
                
            # Skip comments and empty lines
            if line.startswith("'") or not line:
                continue
                
            # Categorize based on current section and content
            if 'macro' in str(current_section):
                if line.startswith(('+', '-')) and '#define' in line:
                    macros.append(line)
            elif 'function' in str(current_section):
                if line.startswith(('+', '-')) and '(' in line and ')' in line:
                    functions.append(line)
            elif 'variable' in str(current_section) or 'global' in str(current_section):
                if line.startswith(('+', '-')) and '(' not in line:
                    variables.append(line)
            else:
                # For typedef classes, everything is a field
                if stereotype == "typedef" and line.startswith('+'):
                    fields.append(line)
                elif line.startswith(('+', '-')):
                    # Auto-categorize based on content
                    if '#define' in line:
                        macros.append(line)
                    elif '(' in line and ')' in line:
                        functions.append(line)
                    else:
                        variables.append(line)
        
        return macros, functions, variables, fields

    def _parse_enum_values(self, body: str) -> List[str]:
        """Parse enum values from body."""
        lines = [line.strip() for line in body.split('\n') if line.strip()]
        values = []
        
        for line in lines:
            if line.startswith('+') and not line.startswith('--'):
                values.append(line)
                
        return values

    def _extract_relationships(self, content: str, filename: str) -> List[PUMLRelationship]:
        """Extract all relationships from PUML content."""
        relationships = []
        
        # Pattern for relationships with labels
        patterns = [
            (r'(\w+)\s+-->\s+(\w+)\s+:\s+(<<[^>]+>>)', '-->'),  # Include relationships
            (r'(\w+)\s+\.\.>\s+(\w+)\s+:\s+(<<[^>]+>>)', '..>'),  # Declares/Uses relationships
            (r'(\w+)\s+-->\s+(\w+)\s+:\s+([^<][^\n]*)', '-->'),   # Non-bracketed includes
            (r'(\w+)\s+\.\.>\s+(\w+)\s+:\s+([^<][^\n]*)', '..>')   # Non-bracketed declares/uses
        ]
        
        for pattern, arrow_type in patterns:
            matches = re.findall(pattern, content)
            for source, target, label in matches:
                relationships.append(PUMLRelationship(
                    source=source.strip(),
                    target=target.strip(),
                    type=arrow_type,
                    label=label.strip()
                ))
        
        return relationships

    def _validate_startuml_structure(self, content: str, filename: str) -> bool:
        """Validate basic PlantUML structure."""
        lines = content.split('\n')
        
        # Check for @startuml and @enduml
        has_start = any('@startuml' in line for line in lines)
        has_end = any('@enduml' in line for line in lines)
        
        if not has_start:
            self._add_result(ValidationLevel.ERROR, "Missing @startuml directive", filename)
            return False
            
        if not has_end:
            self._add_result(ValidationLevel.ERROR, "Missing @enduml directive", filename)
            return False
            
        # Check for proper diagram name
        start_line = next((line for line in lines if '@startuml' in line), None)
        if start_line and '@startuml' in start_line:
            expected_name = filename.replace('.puml', '')
            if expected_name not in start_line:
                self._add_result(ValidationLevel.WARNING, 
                               f"Diagram name should match filename: expected '{expected_name}'", 
                               filename)
        
        return True

    def validate_class_structure(self, classes: Dict[str, PUMLClass], filename: str):
        """Validate class definitions and structure."""
        for uml_id, cls in classes.items():
            # Validate stereotype
            if cls.stereotype not in self.expected_stereotypes:
                self._add_result(ValidationLevel.ERROR, 
                               f"Invalid stereotype '{cls.stereotype}' for class {uml_id}", 
                               filename)
            
            # Validate color
            if cls.color not in self.expected_colors:
                self._add_result(ValidationLevel.ERROR, 
                               f"Invalid color '{cls.color}' for class {uml_id}", 
                               filename)
            
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
                self._add_result(ValidationLevel.WARNING, 
                               f"Source class {cls.uml_id} should be named {expected_name}", 
                               filename)
        
        elif cls.stereotype == "header":
            if not cls.uml_id.startswith("HEADER_"):
                self._add_result(ValidationLevel.ERROR, 
                               f"Header class {cls.uml_id} should have HEADER_ prefix", 
                               filename)
        
        elif cls.stereotype == "typedef":
            if not cls.uml_id.startswith("TYPEDEF_"):
                self._add_result(ValidationLevel.ERROR, 
                               f"Typedef class {cls.uml_id} should have TYPEDEF_ prefix", 
                               filename)

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
            if item.startswith('+'):
                self._add_result(ValidationLevel.ERROR, 
                               f"Source class {cls.uml_id} should not have + prefix: {item}", 
                               filename)
        
        # Macros in source files should have - prefix
        for macro in cls.macros:
            if not macro.startswith('-'):
                self._add_result(ValidationLevel.WARNING, 
                               f"Source class macro should have - prefix: {macro}", 
                               filename)

    def _validate_header_content(self, cls: PUMLClass, filename: str):
        """Validate header file class content."""
        # Header files should have + prefix for all elements
        all_items = cls.macros + cls.functions + cls.variables
        for item in all_items:
            line = item.strip()
            if line and not line.startswith("'") and not line.startswith("--"):
                if not line.startswith("+"):
                    self._add_result(ValidationLevel.ERROR, 
                                   f"Header class item should have + prefix: {item}", 
                                   filename)

    def _validate_typedef_content(self, cls: PUMLClass, filename: str):
        """Validate typedef class content."""
        # Typedef classes should have + prefix for all elements
        all_items = cls.fields + cls.values
        for item in all_items:
            line = item.strip()
            if line and not line.startswith("'") and not line.startswith("--"):
                if not line.startswith("+"):
                    self._add_result(ValidationLevel.ERROR, 
                                   f"Typedef class item should have + prefix: {item}", 
                                   filename)

    def validate_relationships(self, relationships: List[PUMLRelationship], 
                             classes: Dict[str, PUMLClass], filename: str):
        """Validate relationships between classes."""
        # Check for duplicate relationships
        seen = set()
        for rel in relationships:
            key = (rel.source, rel.target, rel.label)
            if key in seen:
                self._add_result(ValidationLevel.WARNING, 
                               f"Duplicate relationship: {rel.source} -> {rel.target} ({rel.label})", 
                               filename)
            seen.add(key)
        
        # Validate relationship targets exist
        class_ids = set(classes.keys())
        for rel in relationships:
            if rel.source not in class_ids:
                self._add_result(ValidationLevel.ERROR, 
                               f"Relationship source '{rel.source}' not found in classes", 
                               filename)
            if rel.target not in class_ids:
                self._add_result(ValidationLevel.ERROR, 
                               f"Relationship target '{rel.target}' not found in classes", 
                               filename)
        
        # Validate relationship label format
        for rel in relationships:
            if rel.label and not (rel.label.startswith('<<') and rel.label.endswith('>>')):
                if rel.label not in ['include', 'declares', 'uses']:  # Allow some non-bracketed forms
                    self._add_result(ValidationLevel.WARNING, 
                                   f"Relationship label should use <<>> format: {rel.label}", 
                                   filename)

    def validate_content_patterns(self, content: str, filename: str):
        """Validate specific content patterns and detect issues."""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for malformed function signatures
            if '(' in line and ')' in line:
                self._validate_function_signature(line, filename, i)
            
            # Check for malformed typedefs
            if 'typedef' in line:
                self._validate_typedef_line(line, filename, i)
            
            # Check for macro definitions
            if '#define' in line:
                self._validate_macro_definition(line, filename, i)
            
            # Check for PlantUML syntax issues
            self._validate_plantuml_syntax(line, filename, i)

    def _validate_plantuml_syntax(self, line: str, filename: str, line_num: int):
        """Validate PlantUML-specific syntax patterns."""
        line_stripped = line.strip()
        
        # Check for proper class definition syntax
        if line_stripped.startswith('class "') and ' as ' in line:
            if not re.match(r'class\s+"[^"]+"\s+as\s+\w+\s+<<\w+>>\s+#\w+', line_stripped):
                self._add_result(ValidationLevel.WARNING, 
                               f"Class definition syntax may be malformed: {line_stripped}", 
                               filename, line_num)
        
        # Check for proper enum definition syntax  
        if line_stripped.startswith('enum "') and ' as ' in line:
            if not re.match(r'enum\s+"[^"]+"\s+as\s+\w+\s+<<\w+>>\s+#\w+', line_stripped):
                self._add_result(ValidationLevel.WARNING, 
                               f"Enum definition syntax may be malformed: {line_stripped}", 
                               filename, line_num)
        
        # Check for proper relationship syntax
        if ('-->' in line or '..>' in line) and ':' in line:
            if not re.match(r'\w+\s+(-->|\.\.>)\s+\w+\s+:', line_stripped):
                self._add_result(ValidationLevel.WARNING, 
                               f"Relationship syntax may be malformed: {line_stripped}", 
                               filename, line_num)

    def _validate_function_signature(self, line: str, filename: str, line_num: int):
        """Validate function signature formatting."""
        # Check for malformed function pointers with specific patterns
        if '* *' in line and not ('void * *' in line or 'char * *' in line):
            self._add_result(ValidationLevel.WARNING, 
                           f"Possible malformed function pointer: {line.strip()}", 
                           filename, line_num)
        
        # Check for incomplete parameter lists - but allow for function pointers with complex syntax
        open_parens = line.count('(')
        close_parens = line.count(')')
        if open_parens != close_parens:
            # Special case for function pointers that might be truncated
            if 'unknown unnamed' in line or line.strip().endswith('('):
                self._add_result(ValidationLevel.WARNING, 
                               f"Function signature appears truncated: {line.strip()}", 
                               filename, line_num)
            else:
                self._add_result(ValidationLevel.ERROR, 
                               f"Unbalanced parentheses in function: {line.strip()}", 
                               filename, line_num)

    def _validate_typedef_line(self, line: str, filename: str, line_num: int):
        """Validate typedef formatting."""
        # Check for repeated typedef keyword
        if line.count('typedef') > 1:
            self._add_result(ValidationLevel.WARNING, 
                           f"Multiple 'typedef' keywords in line: {line.strip()}", 
                           filename, line_num)
        
        # Check for incomplete struct/enum definitions
        if 'typedef struct' in line and '{' not in line and '}' not in line:
            self._add_result(ValidationLevel.INFO, 
                           f"Simple typedef struct: {line.strip()}", 
                           filename, line_num)

    def _validate_macro_definition(self, line: str, filename: str, line_num: int):
        """Validate macro definition formatting."""
        # Check for proper #define format
        if not re.match(r'^\s*[+\-]?\s*#define\s+\w+', line):
            self._add_result(ValidationLevel.WARNING, 
                           f"Possibly malformed macro definition: {line.strip()}", 
                           filename, line_num)

    def validate_file_specific_requirements(self, parsed_data: Dict[str, Any], filename: str):
        """Validate file-specific requirements."""
        base_name = filename.replace('.puml', '')
        classes = parsed_data.get('classes', {})
        content = parsed_data.get('content', '')
        
        # Validate expected classes exist
        expected_classes = self._get_expected_classes(base_name)
        for expected_class in expected_classes:
            if expected_class not in classes:
                self._add_result(ValidationLevel.ERROR, 
                               f"Expected class '{expected_class}' not found", 
                               filename)
        
        # Validate file-specific content patterns
        self._validate_file_specific_content(base_name, content, classes, filename)

    def _validate_file_specific_content(self, base_name: str, content: str, classes: Dict[str, PUMLClass], filename: str):
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

    def _validate_complex_file_content(self, content: str, classes: Dict[str, PUMLClass], filename: str):
        """Validate complex.puml specific content."""
        # Check for essential macros
        essential_macros = [
            "COMPLEX_MACRO_FUNC", "PROCESS_ARRAY", "CREATE_FUNC_NAME", 
            "STRINGIFY", "TOSTRING", "UTILS_U16_TO_U8ARR_BIG_ENDIAN",
            "UTILS_U32_TO_U8ARR_BIG_ENDIAN", "HANDLE_OPERATION"
        ]
        
        for macro in essential_macros:
            if macro not in content:
                self._add_result(ValidationLevel.ERROR, 
                               f"Missing essential macro: {macro}", 
                               filename)
        
        # Check for essential functions
        essential_functions = [
            "test_complex_macro", "test_process_array", "test_handle_operation",
            "test_processor_job_processing", "run_complex_tests", "process_with_callbacks"
        ]
        
        for func in essential_functions:
            if func not in content:
                self._add_result(ValidationLevel.WARNING, 
                               f"Missing expected function: {func}", 
                               filename)
        
        # Check for essential typedefs
        essential_typedefs = [
            "TYPEDEF_PROCESS_T", "TYPEDEF_MATH_OPERATION_T", "TYPEDEF_COMPLEX_HANDLER_T"
        ]
        
        for typedef in essential_typedefs:
            if typedef not in classes:
                self._add_result(ValidationLevel.ERROR, 
                               f"Missing essential typedef: {typedef}", 
                               filename)

    def _validate_typedef_test_content(self, content: str, classes: Dict[str, PUMLClass], filename: str):
        """Validate typedef_test.puml specific content."""
        essential_typedefs = [
            "TYPEDEF_MYLEN", "TYPEDEF_MYINT", "TYPEDEF_MYSTRING", 
            "TYPEDEF_MYBUFFER", "TYPEDEF_MYCOMPLEX", "TYPEDEF_COLOR_T"
        ]
        
        for typedef in essential_typedefs:
            if typedef not in classes:
                self._add_result(ValidationLevel.ERROR, 
                               f"Missing essential typedef: {typedef}", 
                               filename)
        
        # Check for enum values
        essential_enum_values = ["COLOR_RED", "COLOR_GREEN", "COLOR_BLUE"]
        for enum_val in essential_enum_values:
            if enum_val not in content:
                self._add_result(ValidationLevel.WARNING, 
                               f"Missing enum value: {enum_val}", 
                               filename)

    def _validate_sample_file_content(self, content: str, classes: Dict[str, PUMLClass], filename: str):
        """Validate sample.puml specific content."""
        essential_functions = ["calculate_sum", "create_point", "process_point", "main"]
        for func in essential_functions:
            if func not in content:
                self._add_result(ValidationLevel.WARNING, 
                               f"Missing expected function: {func}", 
                               filename)
        
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
            "filtered_global_string"
        ]
        
        for indicator in filtered_content_indicators:
            if indicator in content:
                self._add_result(ValidationLevel.ERROR,
                               f"Filtered content '{indicator}' from filtered_header.h should not appear in PUML file",
                               filename)

    def _validate_geometry_file_content(self, content: str, classes: Dict[str, PUMLClass], filename: str):
        """Validate geometry.puml specific content."""
        essential_functions = ["create_triangle", "triangle_area"]
        for func in essential_functions:
            if func not in content:
                self._add_result(ValidationLevel.WARNING, 
                               f"Missing expected function: {func}", 
                               filename)

    def _validate_logger_file_content(self, content: str, classes: Dict[str, PUMLClass], filename: str):
        """Validate logger.puml specific content."""
        essential_functions = ["log_message", "set_log_callback"]
        for func in essential_functions:
            if func not in content:
                self._add_result(ValidationLevel.WARNING, 
                               f"Missing expected function: {func}", 
                               filename)

    def _validate_math_utils_content(self, content: str, classes: Dict[str, PUMLClass], filename: str):
        """Validate math_utils.puml specific content."""
        essential_functions = ["add", "subtract", "average"]
        for func in essential_functions:
            if func not in content:
                self._add_result(ValidationLevel.WARNING, 
                               f"Missing expected function: {func}", 
                               filename)

    def _validate_preprocessed_content(self, content: str, classes: Dict[str, PUMLClass], filename: str):
        """Validate preprocessed.puml specific content."""
        # Check for preprocessing artifacts
        preprocessing_indicators = ["#if", "#ifdef", "#define"]
        has_preprocessing = any(indicator in content for indicator in preprocessing_indicators)
        if not has_preprocessing:
            self._add_result(ValidationLevel.INFO, 
                           "No preprocessing directives found", 
                           filename)

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
            if not value.startswith('+'):
                self._add_result(ValidationLevel.ERROR, 
                               f"Enum value should start with +: {value}", 
                               filename)
            
            # Check for enum value naming conventions
            value_name = value.replace('+', '').strip()
            if '=' in value_name:
                name_part = value_name.split('=')[0].strip()
                if not name_part.isupper():
                    self._add_result(ValidationLevel.WARNING, 
                                   f"Enum value should be uppercase: {name_part}", 
                                   filename)

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
            if not field.startswith('+'):
                self._add_result(ValidationLevel.ERROR, 
                               f"Struct field should start with +: {field}", 
                               filename)
            
            # Check for common field patterns
            field_content = field.replace('+', '').strip()
            
            # Validate array syntax
            if '[' in field_content and ']' in field_content:
                self._validate_array_field(field_content, filename)

    def _validate_array_field(self, field_content: str, filename: str):
        """Validate array field syntax."""
        # Check for proper array format: type[size] name or type name[size]
        if ' [ ' in field_content or ' ] ' in field_content:
            self._add_result(ValidationLevel.WARNING, 
                           f"Array field has spaces around brackets: {field_content}", 
                           filename)

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
            "preprocessed": ["PREPROCESSED", "HEADER_PREPROCESSED"]
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
        classes = parsed_data.get('classes', {})
        relationships = parsed_data.get('relationships', [])
        content = parsed_data.get('content', '')
        
        # Print validation summary for this file
        source_classes = [c for c in classes.values() if c.stereotype == "source"]
        header_classes = [c for c in classes.values() if c.stereotype == "header"] 
        typedef_classes = [c for c in classes.values() if c.stereotype == "typedef"]
        
        print(f"  Found: {len(source_classes)} source, {len(header_classes)} header, {len(typedef_classes)} typedef classes, {len(relationships)} relationships")
        
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
        
        return all_valid and len([r for r in self.results if r.level == ValidationLevel.ERROR]) == 0

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


def main():
    """Main function to run the validation."""
    try:
        validator = PUMLValidator()
        success = validator.run_all_validations()
        
        if not success:
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
