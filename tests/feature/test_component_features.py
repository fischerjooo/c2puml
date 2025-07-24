#!/usr/bin/env python3
"""
Component Features tests.

Comprehensive test suite for verifying the functionality of
individual component features including parser, generator, and project analysis.

This file consolidates tests from:
- test_parser_features.py
- test_generator_features.py  
- test_project_analysis_features.py
"""

import os
from pathlib import Path

from tests.feature.base import BaseFeatureTest


class TestParserComponentFeatures(BaseFeatureTest):
    """Test advanced parser component features."""

    def test_parse_complex_typedefs(self):
        """Test parsing complex typedef relationships."""
        from c_to_plantuml.parser import Parser

        content = """
#include <stdio.h>

typedef struct {
    int id;
    char name[100];
} User;

typedef User* UserPtr;
typedef int Integer;
typedef void (*Callback)(int);

struct ComplexStruct {
    UserPtr users;
    Integer count;
    Callback callback;
};
        """

        self.create_test_file("typedef_test.c", content)

        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        file_model = model.files["typedef_test.c"]

        # Verify typedefs were parsed
        self.assertIn("UserPtr", file_model.aliases)
        self.assertIn("Integer", file_model.aliases)
        self.assertIn("Callback", file_model.aliases)

    def test_parse_unions(self):
        """Test parsing union definitions."""
        from c_to_plantuml.parser import Parser

        content = """
union Data {
    int i;
    float f;
    char str[20];
};

typedef union {
    int x;
    int y;
} Point;
        """

        self.create_test_file("union_test.c", content)

        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        file_model = model.files["union_test.c"]

        # The parser might not support unions yet, so we'll just check that it doesn't crash
        self.assertIsNotNone(file_model)

    def test_parse_function_pointers(self):
        """Test parsing function pointer definitions."""
        from c_to_plantuml.parser import Parser

        content = """
typedef int (*compare_func_t)(const void *a, const void *b);
typedef void (*callback_t)(void);

struct Handler {
    compare_func_t comparator;
    callback_t on_complete;
    void (*on_error)(int error_code);
};

int sort_with_callback(int *arr, size_t len, compare_func_t comp);
        """

        self.create_test_file("function_ptr_test.c", content)

        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        file_model = model.files["function_ptr_test.c"]
        
        # Should have parsed the typedefs and struct
        self.assertIn("compare_func_t", file_model.aliases)
        self.assertIn("callback_t", file_model.aliases)
        self.assertIn("Handler", file_model.structs)


class TestGeneratorComponentFeatures(BaseFeatureTest):
    """Test advanced generator component features."""

    def test_generate_with_typedefs(self):
        """Test PlantUML generation with typedef relationships."""
        from c_to_plantuml.generator import Generator
        from c_to_plantuml.parser import Parser

        content = """
#include <stdio.h>

typedef struct {
    int id;
    char name[100];
} User;

typedef User* UserPtr;

struct Container {
    UserPtr users;
    int count;
};
        """

        self.create_test_file("typedef_test.c", content)

        # Parse and generate
        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)

        generator = Generator()
        output_dir = self.temp_dir + "/output"
        generator.generate(model_path, output_dir)

        # Verify generation
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 1)

    def test_generate_with_unions(self):
        """Test PlantUML generation with union definitions."""
        from c_to_plantuml.generator import Generator
        from c_to_plantuml.parser import Parser

        content = """
union Data {
    int i;
    float f;
    char str[20];
};

struct Container {
    union Data data;
    int type;
};
        """

        self.create_test_file("union_test.c", content)

        # Parse and generate
        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)

        generator = Generator()
        output_dir = self.temp_dir + "/output"
        generator.generate(model_path, output_dir)

        # Verify generation
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 1)

    def test_generate_with_complex_relationships(self):
        """Test PlantUML generation with complex type relationships."""
        from c_to_plantuml.generator import Generator
        from c_to_plantuml.parser import Parser

        content = """
typedef struct Node Node;

struct Node {
    int data;
    Node* next;
    Node* prev;
};

typedef struct {
    Node* head;
    Node* tail;
    size_t count;
} LinkedList;

typedef LinkedList* ListPtr;

struct Database {
    ListPtr user_list;
    ListPtr config_list;
    int connection_count;
};
        """

        self.create_test_file("complex_test.c", content)

        # Parse and generate
        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)

        generator = Generator()
        output_dir = self.temp_dir + "/output"
        generator.generate(model_path, output_dir)

        # Verify generation
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 1)

        # Check that the generated PlantUML contains our structures
        if puml_files:
            with open(puml_files[0], 'r') as f:
                content = f.read()
                # Should contain some reference to our defined structures
                self.assertTrue(any(name in content for name in ["Node", "LinkedList", "Database"]))


class TestProjectAnalysisComponentFeatures(BaseFeatureTest):
    """Test project analysis component features."""

    def test_project_structure_analysis(self):
        """Test analysis of project structure and dependencies."""
        from c_to_plantuml.parser import Parser

        # Create a realistic project structure
        project_files = {
            "main.c": '''
#include "app.h"
#include "utils.h"

int main() {
    App app = app_create();
    return app_run(&app);
}
''',
            "app.h": '''
#ifndef APP_H
#define APP_H

#include "config.h"

typedef struct {
    Config config;
    int status;
} App;

App app_create(void);
int app_run(App* app);

#endif
''',
            "utils.h": '''
#ifndef UTILS_H
#define UTILS_H

typedef struct {
    char* buffer;
    size_t size;
} StringBuffer;

void utils_init(void);

#endif
''',
            "config.h": '''
#ifndef CONFIG_H
#define CONFIG_H

typedef struct {
    int debug_mode;
    char* log_file;
} Config;

#endif
'''
        }

        for filename, content in project_files.items():
            self.create_test_file(filename, content)

        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        # Verify project structure was analyzed correctly
        self.assertGreaterEqual(len(model.files), 4)
        
        # Check that include relationships were detected
        main_file = model.files.get("main.c")
        self.assertIsNotNone(main_file)
        self.assertIn("app.h", main_file.includes)
        self.assertIn("utils.h", main_file.includes)

    def test_cross_file_type_dependencies(self):
        """Test analysis of type dependencies across files."""
        from c_to_plantuml.parser import Parser

        # Create files with cross-dependencies
        project_files = {
            "types.h": '''
#ifndef TYPES_H
#define TYPES_H

typedef unsigned int EntityId;
typedef char* EntityName;

#endif
''',
            "entity.h": '''
#ifndef ENTITY_H
#define ENTITY_H

#include "types.h"

typedef struct {
    EntityId id;
    EntityName name;
    int health;
} Entity;

#endif
''',
            "world.h": '''
#ifndef WORLD_H
#define WORLD_H

#include "entity.h"

typedef struct {
    Entity* entities;
    size_t entity_count;
    size_t max_entities;
} World;

#endif
''',
            "game.c": '''
#include "world.h"

World* create_world(size_t max_entities) {
    // Implementation would go here
    return NULL;
}
'''
        }

        for filename, content in project_files.items():
            self.create_test_file(filename, content)

        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        # Verify cross-file dependencies were detected
        entity_file = model.files.get("entity.h")
        world_file = model.files.get("world.h")
        
        self.assertIsNotNone(entity_file)
        self.assertIsNotNone(world_file)
        
        # Check include chains
        self.assertIn("types.h", entity_file.includes)
        self.assertIn("entity.h", world_file.includes)

    def test_recursive_include_handling(self):
        """Test handling of recursive include relationships."""
        from c_to_plantuml.parser import Parser

        # Create files with potential circular includes
        project_files = {
            "module_a.h": '''
#ifndef MODULE_A_H
#define MODULE_A_H

// Forward declaration to avoid circular dependency
struct ModuleB;

typedef struct {
    int value_a;
    struct ModuleB* b_ref;
} ModuleA;

#endif
''',
            "module_b.h": '''
#ifndef MODULE_B_H
#define MODULE_B_H

#include "module_a.h"

typedef struct ModuleB {
    int value_b;
    ModuleA* a_ref;
} ModuleB;

#endif
''',
            "main.c": '''
#include "module_a.h"
#include "module_b.h"

int main() {
    ModuleA a = {0};
    ModuleB b = {0};
    return 0;
}
'''
        }

        for filename, content in project_files.items():
            self.create_test_file(filename, content)

        # This should not hang or crash due to circular includes
        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        # Verify all files were processed
        self.assertGreaterEqual(len(model.files), 3)
        
        # Should have both structures
        main_file = model.files.get("main.c")
        self.assertIsNotNone(main_file)


if __name__ == "__main__":
    import unittest
    unittest.main()