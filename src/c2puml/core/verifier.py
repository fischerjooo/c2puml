#!/usr/bin/env python3
"""
Verification module for C to PlantUML converter

Performs sanity checks on the parsed model to ensure values make sense for C code.
"""

import logging
import re
from typing import List, Tuple

from ..models import Alias, Enum, Field, FileModel, Function, ProjectModel, Struct, Union


class ModelVerifier:
    """Verifies the sanity of parsed C code model"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.issues = []

    def verify_model(self, model: ProjectModel) -> Tuple[bool, List[str]]:
        """
        Verify the sanity of the entire model

        Args:
            model: The ProjectModel to verify

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        self.issues = []

        # Verify project-level data
        self._verify_project_data(model)

        # New invariants: filenames as keys and include_relations ownership
        self._verify_filename_keys_and_relations(model)

        # Verify each file
        for file_path, file_model in model.files.items():
            self._verify_file(file_path, file_model)

        is_valid = not self.issues

        if self.issues:
            self.logger.warning("Model verification found %d issues:", len(self.issues))
            for issue in self.issues:
                self.logger.warning("  - %s", issue)
        else:
            self.logger.info("Model verification passed - all values look sane")

        return is_valid, self.issues

    def _verify_project_data(self, model: ProjectModel) -> None:
        """Verify project-level data"""
        if not model.project_name or not model.project_name.strip():
            self.issues.append("Project name is empty or whitespace")

        if not model.source_folder or not model.source_folder.strip():
            self.issues.append("Source folder is empty or whitespace")

        if not model.files:
            self.issues.append("No files found in project")

    def _verify_file(self, file_path: str, file_model: FileModel) -> None:
        """Verify a single file model"""
        # Verify file-level data
        if not file_model.file_path or not file_model.file_path.strip():
            self.issues.append(f"File path is empty in {file_model.name}")

        if not file_model.name or not file_model.name.strip():
            self.issues.append(f"File name is empty in {file_path}")

        # Anonymous extraction sanity: detect duplicates per parent and garbled content
        if file_model.anonymous_relationships:
            for parent, children in file_model.anonymous_relationships.items():
                # Duplicates under same parent
                seen = set()
                for child in children:
                    key = (parent, child)
                    if child in seen:
                        self.issues.append(
                            f"Duplicate extracted anonymous entity '{child}' for parent '{parent}' in {file_path}"
                        )
                    seen.add(child)

        # Verify structs
        for struct_name, struct in file_model.structs.items():
            self._verify_struct(file_path, struct_name, struct)

        # Verify enums
        for enum_name, enum in file_model.enums.items():
            self._verify_enum(file_path, enum_name, enum)

        # Verify unions
        for union_name, union in file_model.unions.items():
            self._verify_union(file_path, union_name, union)

        # Verify functions
        for function in file_model.functions:
            self._verify_function(file_path, function)

        # Verify globals
        for global_var in file_model.globals:
            self._verify_global(file_path, global_var)

        # Verify aliases
        for alias_name, alias in file_model.aliases.items():
            self._verify_alias(file_path, alias_name, alias)

    def _verify_struct(self, file_path: str, struct_name: str, struct: Struct) -> None:
        """Verify a struct definition"""
        if not self._is_valid_identifier(struct_name):
            self.issues.append(f"Invalid struct name '{struct_name}' in {file_path}")

        if not struct.name or not struct.name.strip():
            self.issues.append(f"Struct name is empty in {file_path}")

        # Verify fields
        for field in struct.fields:
            self._verify_field(file_path, f"struct {struct_name}", field)

    def _verify_enum(self, file_path: str, enum_name: str, enum: Enum) -> None:
        """Verify an enum definition"""
        if not self._is_valid_identifier(enum_name):
            self.issues.append(f"Invalid enum name '{enum_name}' in {file_path}")

        if not enum.name or not enum.name.strip():
            self.issues.append(f"Enum name is empty in {file_path}")

        # Verify enum values
        for enum_value in enum.values:
            if not enum_value.name or not enum_value.name.strip():
                self.issues.append(
                    f"Enum value name is empty in enum {enum_name} in {file_path}"
                )
            elif not self._is_valid_identifier(enum_value.name):
                self.issues.append(
                    f"Invalid enum value name '{enum_value.name}' in enum {enum_name} in {file_path}"
                )

    def _verify_union(self, file_path: str, union_name: str, union: Union) -> None:
        """Verify a union definition"""
        if not self._is_valid_identifier(union_name):
            self.issues.append(f"Invalid union name '{union_name}' in {file_path}")

        if not union.name or not union.name.strip():
            self.issues.append(f"Union name is empty in {file_path}")

        # Verify fields
        for field in union.fields:
            self._verify_field(file_path, f"union {union_name}", field)

    def _verify_function(self, file_path: str, function: Function) -> None:
        """Verify a function definition"""
        if not function.name or not function.name.strip():
            self.issues.append(f"Function name is empty in {file_path}")
        elif not self._is_valid_identifier(function.name):
            self.issues.append(
                f"Invalid function name '{function.name}' in {file_path}"
            )

        if not function.return_type or not function.return_type.strip():
            self.issues.append(
                f"Function return type is empty for '{function.name}' in {file_path}"
            )

        # Verify parameters (skip variadic parameter '...')
        for param in function.parameters:
            if param.name == "...":  # Skip variadic parameter
                continue
            self._verify_field(file_path, f"function {function.name}", param)

    def _verify_global(self, file_path: str, global_var: Field) -> None:
        """Verify a global variable"""
        self._verify_field(file_path, "global", global_var)

    def _verify_alias(self, file_path: str, alias_name: str, alias: Alias) -> None:
        """Verify a type alias (typedef)"""
        if not self._is_valid_identifier(alias_name):
            self.issues.append(f"Invalid alias name '{alias_name}' in {file_path}")

        if not alias.name or not alias.name.strip():
            self.issues.append(f"Alias name is empty in {file_path}")

        if not alias.original_type or not alias.original_type.strip():
            self.issues.append(
                f"Alias original type is empty for '{alias_name}' in {file_path}"
            )

    def _verify_filename_keys_and_relations(self, model: ProjectModel) -> None:
        """Check filename-key invariant and include_relations placement."""
        for key, fm in model.files.items():
            # Keys should be filenames (equal to FileModel.name)
            if key != fm.name:
                self.issues.append(
                    f"Model.files key '{key}' does not match FileModel.name '{fm.name}'"
                )
            # Only .c files should carry include_relations; others must be empty
            if not fm.name.endswith(".c") and fm.include_relations:
                self.issues.append(
                    f"Header/non-C file '{fm.name}' has include_relations; expected empty"
                )

    def _verify_field(self, file_path: str, context: str, field: Field) -> None:
        """Verify a field (struct field, function parameter, global variable)"""
        # Check for invalid names
        if not field.name or not field.name.strip():
            self.issues.append(f"Field name is empty in {context} in {file_path}")
        elif not self._is_valid_identifier(field.name):
            self.issues.append(
                f"Invalid field name '{field.name}' in {context} in {file_path}"
            )

        # Check for invalid types
        if not field.type or not field.type.strip():
            self.issues.append(
                f"Field type is empty for '{field.name}' in {context} in {file_path}"
            )
        elif self._is_suspicious_type(field.type):
            self.issues.append(
                f"Suspicious field type '{field.type}' for '{field.name}' in {context} in {file_path}"
            )

        # Check for suspicious values
        if field.value and self._is_suspicious_value(field.value):
            self.issues.append(
                f"Suspicious field value '{field.value}' for '{field.name}' in {context} in {file_path}"
            )

    def _is_valid_identifier(self, name: str) -> bool:
        """Check if a name is a valid C identifier"""
        if not name or not name.strip():
            return False

        # C identifier rules: start with letter or underscore, then letters, digits, or underscores
        return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name.strip()))

    def _is_suspicious_type(self, type_str: str) -> bool:
        """Check if a type string looks suspicious"""
        if not type_str or not type_str.strip():
            return True

        type_str = type_str.strip()

        # Check for obvious parsing errors
        suspicious_patterns = [
            r"^[\[\]\{\}\(\)\s\\\n]+$",  # Only brackets, spaces, backslashes, newlines
            r"^[\[\]\{\}\(\)\s\\\n]*[\[\]\{\}\(\)\s\\\n]+$",  # Mostly brackets and whitespace
            r"^[\[\]\{\}\(\)\s\\\n]*[\[\]\{\}\(\)\s\\\n]*$",  # All brackets and whitespace
            r"^[\[\]\{\}\(\)\s\\\n]*[\[\]\{\}\(\)\s\\\n]*[\[\]\{\}\(\)\s\\\n]*$",  # Excessive brackets/whitespace
            r"}\s+\w+;\s*struct\s*\{",  # Garbled anonymous extraction pattern like '} name; struct {'
        ]

        for pattern in suspicious_patterns:
            if re.match(pattern, type_str):
                return True

        # Check for unbalanced brackets
        if self._has_unbalanced_brackets(type_str):
            return True

        # Check for excessive newlines or backslashes
        if type_str.count("\n") > 5 or type_str.count("\\") > 10:
            return True

        return False

    def _is_suspicious_value(self, value: str) -> bool:
        """Check if a value string looks suspicious"""
        if not value or not value.strip():
            return True

        value = value.strip()

        # Check for obvious parsing errors
        suspicious_patterns = [
            r"^[\[\]\{\}\(\)\s\\\n]+$",  # Only brackets, spaces, backslashes, newlines
            r"^[\[\]\{\}\(\)\s\\\n]*[\[\]\{\}\(\)\s\\\n]+$",  # Mostly brackets and whitespace
        ]

        for pattern in suspicious_patterns:
            if re.match(pattern, value):
                return True

        # Check for unbalanced brackets
        if self._has_unbalanced_brackets(value):
            return True

        # Check for excessive newlines or backslashes
        if value.count("\n") > 3 or value.count("\\") > 5:
            return True

        return False

    def _has_unbalanced_brackets(self, text: str) -> bool:
        """Check if text has unbalanced brackets"""
        stack = []
        bracket_pairs = {")": "(", "]": "[", "}": "{"}

        for char in text:
            if char in "([{":
                stack.append(char)
            elif char in ")]}":
                if not stack or stack.pop() != bracket_pairs[char]:
                    return True

        return bool(stack)  # Unclosed brackets
