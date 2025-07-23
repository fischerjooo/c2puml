#!/usr/bin/env python3
"""
Test utilities for C to PlantUML converter tests.

This module provides common test project creation logic, fixtures,
and parameterized test helpers to reduce duplication and improve
test maintainability.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List, Optional, Union

from c_to_plantuml.models import (
    Alias,
    Enum,
    Field,
    FileModel,
    Function,
    ProjectModel,
    Struct,
    Union,
)


class TestProjectBuilder:
    """Builder class for creating test projects with common structures."""
    
    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir or Path(tempfile.mkdtemp())
        self.files: Dict[str, str] = {}
        self.project_name = "test_project"
    
    def add_file(self, relative_path: str, content: str) -> "TestProjectBuilder":
        """Add a file to the test project."""
        self.files[relative_path] = content
        return self
    
    def add_simple_struct_file(self, filename: str = "simple_struct.c") -> "TestProjectBuilder":
        """Add a file with simple struct definitions."""
        content = """
#include <stdio.h>

struct Person {
    char name[50];
    int age;
    float height;
};

struct Address {
    char street[100];
    char city[50];
    int zip_code;
};

int main() {
    return 0;
}
"""
        return self.add_file(filename, content)
    
    def add_simple_enum_file(self, filename: str = "simple_enum.c") -> "TestProjectBuilder":
        """Add a file with simple enum definitions."""
        content = """
enum Status {
    OK,
    ERROR,
    PENDING
};

enum Color {
    RED = 1,
    GREEN = 2,
    BLUE = 3
};

int global_var;
"""
        return self.add_file(filename, content)
    
    def add_simple_union_file(self, filename: str = "simple_union.c") -> "TestProjectBuilder":
        """Add a file with simple union definitions."""
        content = """
union Data {
    int i;
    float f;
    char str[20];
};

union Variant {
    int int_val;
    double double_val;
    char* string_val;
};
"""
        return self.add_file(filename, content)
    
    def add_function_file(self, filename: str = "functions.c") -> "TestProjectBuilder":
        """Add a file with function definitions."""
        content = """
#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

void print_hello(const char* name) {
    printf("Hello, %s!\\n", name);
}

float calculate_area(float width, float height) {
    return width * height;
}
"""
        return self.add_file(filename, content)
    
    def add_typedef_file(self, filename: str = "typedefs.c") -> "TestProjectBuilder":
        """Add a file with typedef definitions."""
        content = """
typedef int Integer;
typedef char* String;
typedef struct Point Point;

struct Point {
    int x;
    int y;
};

typedef enum { FALSE, TRUE } Boolean;
"""
        return self.add_file(filename, content)
    
    def add_include_file(self, filename: str = "includes.c") -> "TestProjectBuilder":
        """Add a file with include directives."""
        content = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "local_header.h"

int main() {
    return 0;
}
"""
        return self.add_file(filename, content)
    
    def add_macro_file(self, filename: str = "macros.c") -> "TestProjectBuilder":
        """Add a file with macro definitions."""
        content = """
#define MAX_SIZE 100
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define SQUARE(x) ((x) * (x))

#define DEBUG_PRINT(msg) printf("DEBUG: %s\\n", msg)

int main() {
    int value = MAX_SIZE;
    int result = MIN(5, 10);
    return 0;
}
"""
        return self.add_file(filename, content)
    
    def add_preprocessor_file(self, filename: str = "preprocessor.c") -> "TestProjectBuilder":
        """Add a file with preprocessor directives."""
        content = """
#define FEATURE_ENABLED 1

#if FEATURE_ENABLED
struct EnabledFeature {
    int data;
};
#else
struct DisabledFeature {
    int data;
};
#endif

#ifdef DEBUG
#define LOG(msg) printf("DEBUG: %s\\n", msg)
#else
#define LOG(msg)
#endif
"""
        return self.add_file(filename, content)
    
    def add_malformed_file(self, filename: str = "malformed.c") -> "TestProjectBuilder":
        """Add a file with malformed C code for negative testing."""
        content = """
struct IncompleteStruct {
    int field1
    char field2

enum IncompleteEnum {
    VALUE1,
    VALUE2

int function_without_brace(int param1, int param2
    return param1 + param2;
}
"""
        return self.add_file(filename, content)
    
    def add_deeply_nested_file(self, filename: str = "nested.c") -> "TestProjectBuilder":
        """Add a file with deeply nested structures."""
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
                } level5;
            } level4;
        } level3;
    } level2;
};
"""
        return self.add_file(filename, content)
    
    def add_anonymous_struct_file(self, filename: str = "anonymous.c") -> "TestProjectBuilder":
        """Add a file with anonymous structs and unions."""
        content = """
struct {
    int x;
    int y;
} point;

union {
    int i;
    float f;
} data;

struct Container {
    struct {
        int a;
        int b;
    } inner;
};
"""
        return self.add_file(filename, content)
    
    def build(self) -> Path:
        """Build the test project and return the project root path."""
        project_root = self.temp_dir / self.project_name
        project_root.mkdir(exist_ok=True)
        
        for relative_path, content in self.files.items():
            file_path = project_root / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        
        return project_root
    
    def cleanup(self) -> None:
        """Clean up the temporary directory."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


class TestModelBuilder:
    """Builder class for creating test model objects."""
    
    @staticmethod
    def create_simple_struct(name: str = "TestStruct") -> Struct:
        """Create a simple struct for testing."""
        return Struct(
            name=name,
            fields=[
                Field(name="field1", type="int", is_pointer=False, is_array=False),
                Field(name="field2", type="char", is_pointer=True, is_array=False),
                Field(name="field3", type="float", is_pointer=False, is_array=True, array_size="10"),
            ],
            line_number=1,
            column_number=1,
        )
    
    @staticmethod
    def create_simple_enum(name: str = "TestEnum") -> Enum:
        """Create a simple enum for testing."""
        return Enum(
            name=name,
            values=["VALUE1", "VALUE2", "VALUE3"],
            line_number=1,
            column_number=1,
        )
    
    @staticmethod
    def create_simple_union(name: str = "TestUnion") -> Union:
        """Create a simple union for testing."""
        return Union(
            name=name,
            fields=[
                Field(name="int_val", type="int", is_pointer=False, is_array=False),
                Field(name="float_val", type="float", is_pointer=False, is_array=False),
                Field(name="char_val", type="char", is_pointer=False, is_array=True, array_size="20"),
            ],
            line_number=1,
            column_number=1,
        )
    
    @staticmethod
    def create_simple_function(name: str = "test_function") -> Function:
        """Create a simple function for testing."""
        return Function(
            name=name,
            return_type="int",
            parameters=[
                Field(name="param1", type="int", is_pointer=False, is_array=False),
                Field(name="param2", type="char", is_pointer=True, is_array=False),
            ],
            line_number=1,
            column_number=1,
        )
    
    @staticmethod
    def create_simple_file_model(filename: str = "test.c") -> FileModel:
        """Create a simple file model for testing."""
        return FileModel(
            filename=filename,
            structs={"TestStruct": TestModelBuilder.create_simple_struct()},
            enums={"TestEnum": TestModelBuilder.create_simple_enum()},
            unions={"TestUnion": TestModelBuilder.create_simple_union()},
            functions=[TestModelBuilder.create_simple_function()],
            globals=[],
            includes=[],
            macros=[],
            aliases={},
        )
    
    @staticmethod
    def create_simple_project_model(project_name: str = "test_project") -> ProjectModel:
        """Create a simple project model for testing."""
        return ProjectModel(
            project_name=project_name,
            project_root="/tmp/test_project",
            files={"test.c": TestModelBuilder.create_simple_file_model()},
        )


class TestFileTemplates:
    """Templates for common test file contents."""
    
    @staticmethod
    def get_header_template(guard_name: str = "TEST_HEADER_H") -> str:
        """Get a standard header file template."""
        return f"""#ifndef {guard_name}
#define {guard_name}

#include <stdio.h>
#include <stdlib.h>

// Function declarations
int test_function(int param);
void print_message(const char* message);

// Global variables
extern int global_counter;

#endif // {guard_name}
"""
    
    @staticmethod
    def get_source_template() -> str:
        """Get a standard source file template."""
        return """#include "test_header.h"

int global_counter = 0;

int test_function(int param) {
    return param * 2;
}

void print_message(const char* message) {
    printf("%s\\n", message);
}
"""
    
    @staticmethod
    def get_main_template() -> str:
        """Get a standard main function template."""
        return """#include <stdio.h>

int main(int argc, char* argv[]) {
    printf("Hello, World!\\n");
    return 0;
}
"""
    
    @staticmethod
    def get_makefile_template() -> str:
        """Get a standard Makefile template."""
        return """CC = gcc
CFLAGS = -Wall -Wextra -std=c99

TARGET = test_program
SOURCES = main.c test.c
OBJECTS = $(SOURCES:.c=.o)

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(TARGET)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)

.PHONY: clean
"""


def create_temp_file(
    content: str,
    suffix: str = ".c",
    prefix: str = "test_",
    encoding: str = "utf-8"
) -> Path:
    """Create a temporary file with the given content."""
    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=suffix,
        prefix=prefix,
        delete=False,
        encoding=encoding
    )
    
    with temp_file:
        temp_file.write(content)
    
    return Path(temp_file.name)


def create_temp_directory(prefix: str = "test_project_") -> Path:
    """Create a temporary directory."""
    return Path(tempfile.mkdtemp(prefix=prefix))


def cleanup_temp_file(file_path: Union[str, Path]) -> None:
    """Clean up a temporary file."""
    try:
        os.unlink(file_path)
    except (OSError, FileNotFoundError):
        pass


def cleanup_temp_directory(dir_path: Union[str, Path]) -> None:
    """Clean up a temporary directory."""
    import shutil
    try:
        shutil.rmtree(dir_path)
    except (OSError, FileNotFoundError):
        pass


class TestCaseWithCleanup(unittest.TestCase):
    """Base test case class with automatic cleanup."""
    
    def setUp(self):
        self.temp_files: List[Path] = []
        self.temp_dirs: List[Path] = []
    
    def tearDown(self):
        # Clean up temporary files
        for file_path in self.temp_files:
            cleanup_temp_file(file_path)
        
        # Clean up temporary directories
        for dir_path in self.temp_dirs:
            cleanup_temp_directory(dir_path)
    
    def add_temp_file(self, file_path: Path) -> None:
        """Add a temporary file for cleanup."""
        self.temp_files.append(file_path)
    
    def add_temp_directory(self, dir_path: Path) -> None:
        """Add a temporary directory for cleanup."""
        self.temp_dirs.append(dir_path)


def parameterized_test_cases(*test_cases):
    """Decorator for parameterized test cases."""
    def decorator(test_method):
        def wrapper(self):
            for test_case in test_cases:
                with self.subTest(**test_case):
                    test_method(self, **test_case)
        return wrapper
    return decorator


def assert_model_contains_struct(model: FileModel, struct_name: str) -> None:
    """Assert that a model contains a struct with the given name."""
    unittest.TestCase().assertIn(
        struct_name,
        model.structs,
        f"Model should contain struct '{struct_name}'"
    )


def assert_model_contains_enum(model: FileModel, enum_name: str) -> None:
    """Assert that a model contains an enum with the given name."""
    unittest.TestCase().assertIn(
        enum_name,
        model.enums,
        f"Model should contain enum '{enum_name}'"
    )


def assert_model_contains_function(model: FileModel, function_name: str) -> None:
    """Assert that a model contains a function with the given name."""
    function_names = [f.name for f in model.functions]
    unittest.TestCase().assertIn(
        function_name,
        function_names,
        f"Model should contain function '{function_name}'"
    )


def assert_struct_has_field(struct: Struct, field_name: str, field_type: str) -> None:
    """Assert that a struct has a field with the given name and type."""
    field_names = [f.name for f in struct.fields]
    unittest.TestCase().assertIn(
        field_name,
        field_names,
        f"Struct '{struct.name}' should have field '{field_name}'"
    )
    
    field = next(f for f in struct.fields if f.name == field_name)
    unittest.TestCase().assertEqual(
        field.type,
        field_type,
        f"Field '{field_name}' should have type '{field_type}', got '{field.type}'"
    )


def save_test_model(model: ProjectModel, output_path: Union[str, Path]) -> None:
    """Save a test model to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(model.to_dict(), f, indent=2)


def load_test_model(input_path: Union[str, Path]) -> ProjectModel:
    """Load a test model from a JSON file."""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ProjectModel.from_dict(data)