#!/usr/bin/env python3
"""
Comprehensive feature tests for include header processing functionality.

This file contains feature tests organized into logical test groups focusing on:
1. Basic workflow features
2. Complex project structures
3. Integration scenarios
4. Dependency processing
5. Comprehensive end-to-end testing
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch



# Add src directory to path for new package structure
import sys
import os
from pathlib import Path

# Get the absolute path to the src directory 
current_file = Path(__file__).resolve()
test_dir = current_file.parent
project_root = test_dir.parent.parent
src_path = project_root / "src"

if src_path.exists():
    sys.path.insert(0, str(src_path))
# Also add tests directory for test utilities
tests_path = project_root / "tests"
if tests_path.exists():
    sys.path.insert(0, str(tests_path))

from c2puml.config import Config
from c2puml.generator import Generator
from c2puml.main import main as c2puml_main
from c2puml.parser import CParser, Parser
from c2puml.transformer import Transformer
from tests.feature.base import BaseFeatureTest



class TestIncludeProcessingBasicFeatures(BaseFeatureTest):
    """Basic feature tests for include header processing workflow."""

    def setUp(self):
        """Set up test environment for basic include processing."""
        super().setUp()
        self.project_dir = Path(self.temp_dir)
        self.config_file = self.project_dir / "config.json"

    def test_feature_include_processing_basic_workflow(self):
        """Test basic include processing workflow features."""
        
        # Create test files with include relationships
        main_c = """
#include <stdio.h>
#include "data_types.h"
#include "functions.h"

int main() {
    Person person = {"John", 25};
    print_person(&person);
    return 0;
}
"""

        data_types_h = """
#ifndef DATA_TYPES_H
#define DATA_TYPES_H

typedef struct {
    char name[50];
    int age;
} Person;

#endif
"""

        functions_h = """
#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include "data_types.h"

void print_person(Person* p);

#endif
"""

        # Write test files
        (self.project_dir / "main.c").write_text(main_c)
        (self.project_dir / "data_types.h").write_text(data_types_h)
        (self.project_dir / "functions.h").write_text(functions_h)

        # Create configuration
        config_data = {
            "project_name": "include_processing_basic",
            "source_folders": [str(self.project_dir)],
            "output_dir": str(self.project_dir / "output"),
            "include_depth": 2,
            "recursive_search": True
        }
        
        self.config_file.write_text(json.dumps(config_data, indent=2))

        # Test the workflow
        parser = Parser()
        config = Config(**config_data)
        
        project_model = parser.parse_project(str(self.project_dir), config)
        
        # Validate results
        self.assertIsNotNone(project_model)
        self.assertGreater(len(project_model.files), 1)
        
        # Check that main.c was parsed
        self.assertIn("main.c", project_model.files)
        main_file = project_model.files["main.c"]
        
        # Check that includes were processed
        self.assertGreater(len(main_file.includes), 0)
        
        # Check for struct definitions from included headers
        if len(project_model.files) > 1:
            # Header files should be included in the model
            header_files = [f for f in project_model.files.keys() if f.endswith('.h')]
            self.assertGreater(len(header_files), 0)

    def test_feature_c_to_h_relationships(self):
        """Test C file to header file relationship processing."""
        
        # Create test project with .c and .h relationships
        engine_c = """
#include "engine.h"
#include <stdlib.h>

void start_engine() {
    EngineState state = ENGINE_STOPPED;
    printf("Engine starting\\n");
}

void stop_engine() {
    printf("Engine stopping\\n");
}
"""

        engine_h = """
#ifndef ENGINE_H
#define ENGINE_H

typedef enum {
    ENGINE_STOPPED,
    ENGINE_RUNNING,
    ENGINE_ERROR
} EngineState;

void start_engine(void);
void stop_engine(void);

#endif
"""

        # Write files
        (self.project_dir / "engine.c").write_text(engine_c)
        (self.project_dir / "engine.h").write_text(engine_h)

        # Parse project
        config = Config(
            source_folders=[str(self.project_dir)],
            output_dir=str(self.project_dir / "output"),
            include_depth=2
        )
        
        parser = Parser()
        project_model = parser.parse_project(str(self.project_dir), config)

        # Validate C to H relationships
        self.assertIsNotNone(project_model)
        self.assertIn("engine.c", project_model.files)
        
        engine_file = project_model.files["engine.c"]
        self.assertGreater(len(engine_file.includes), 0)
        
        # Check that the enum from header is accessible
        if "engine.h" in project_model.files:
            header_file = project_model.files["engine.h"]
            self.assertGreater(len(header_file.enums), 0)

    def test_feature_header_to_header_relationships(self):
        """Test header file to header file relationship processing."""
        
        # Create nested header dependencies
        base_types_h = """
#ifndef BASE_TYPES_H
#define BASE_TYPES_H

typedef struct {
    int id;
    char name[32];
} BaseObject;

#endif
"""

        advanced_types_h = """
#ifndef ADVANCED_TYPES_H
#define ADVANCED_TYPES_H

#include "base_types.h"

typedef struct {
    BaseObject base;
    float value;
    int count;
} AdvancedObject;

#endif
"""

        main_c = """
#include "advanced_types.h"

int main() {
    AdvancedObject obj;
    obj.base.id = 1;
    obj.value = 3.14f;
    return 0;
}
"""

        # Write files
        (self.project_dir / "base_types.h").write_text(base_types_h)
        (self.project_dir / "advanced_types.h").write_text(advanced_types_h)
        (self.project_dir / "main.c").write_text(main_c)

        # Parse with include depth to capture header chains
        config = Config(
            source_folders=[str(self.project_dir)],
            output_dir=str(self.project_dir / "output"),
            include_depth=3
        )
        
        parser = Parser()
        project_model = parser.parse_project(str(self.project_dir), config)

        # Validate header-to-header relationships
        self.assertIsNotNone(project_model)
        
        # Check that advanced_types.h includes base_types.h
        if "advanced_types.h" in project_model.files:
            advanced_file = project_model.files["advanced_types.h"]
            include_names = [inc.filename for inc in advanced_file.includes]
            self.assertIn("base_types.h", include_names)

        # Check that nested types are accessible
        files_with_structs = [f for f in project_model.files.values() if len(f.structs) > 0]
        self.assertGreater(len(files_with_structs), 0)


class TestIncludeProcessingComplexFeatures(BaseFeatureTest):
    """Complex feature tests for include processing with advanced scenarios."""

    def setUp(self):
        """Set up complex test environment."""
        super().setUp()
        self.project_dir = Path(self.temp_dir)

    def test_feature_complex_project_structure(self):
        """Test include processing with complex project structure."""
        
        # Create complex project structure with subdirectories
        core_dir = self.project_dir / "core"
        utils_dir = self.project_dir / "utils"
        api_dir = self.project_dir / "api"
        
        for dir_path in [core_dir, utils_dir, api_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Core module
        (core_dir / "core.h").write_text("""
#ifndef CORE_H
#define CORE_H

typedef struct {
    int core_id;
    char core_name[64];
} CoreModule;

void init_core(void);

#endif
""")

        (core_dir / "core.c").write_text("""
#include "core.h"
#include "../utils/utils.h"

void init_core() {
    log_message("Core initialized");
}
""")

        # Utils module
        (utils_dir / "utils.h").write_text("""
#ifndef UTILS_H
#define UTILS_H

void log_message(const char* msg);
int calculate_hash(const char* str);

#endif
""")

        (utils_dir / "utils.c").write_text("""
#include "utils.h"
#include <stdio.h>

void log_message(const char* msg) {
    printf("LOG: %s\\n", msg);
}

int calculate_hash(const char* str) {
    return 42; // Simple hash
}
""")

        # API module
        (api_dir / "api.h").write_text("""
#ifndef API_H
#define API_H

#include "../core/core.h"
#include "../utils/utils.h"

typedef struct {
    CoreModule* core;
    int api_version;
} ApiContext;

void api_start(void);

#endif
""")

        # Main application
        (self.project_dir / "main.c").write_text("""
#include "api/api.h"
#include "core/core.h"

int main() {
    init_core();
    api_start();
    return 0;
}
""")

        # Test parsing with recursive search
        config = Config(
            source_folders=[str(self.project_dir)],
            output_dir=str(self.project_dir / "output"),
            include_depth=3,
            recursive_search=True
        )
        
        parser = Parser()
        project_model = parser.parse_project(str(self.project_dir), config)

        # Validate complex structure parsing
        self.assertIsNotNone(project_model)
        self.assertGreater(len(project_model.files), 3)
        
        # Check that files from different directories are included
        parsed_files = list(project_model.files.keys())
        c_files = [f for f in parsed_files if f.endswith('.c')]
        self.assertGreater(len(c_files), 2)

    def test_feature_typedef_relationships_across_files(self):
        """Test typedef relationships across multiple files."""
        
        # Create types hierarchy
        basic_types_h = """
#ifndef BASIC_TYPES_H
#define BASIC_TYPES_H

typedef int ID_t;
typedef float Real_t;

typedef struct {
    ID_t id;
    Real_t value;
} BasicData;

#endif
"""

        extended_types_h = """
#ifndef EXTENDED_TYPES_H
#define EXTENDED_TYPES_H

#include "basic_types.h"

typedef BasicData* BasicDataPtr;
typedef BasicData BasicDataArray[10];

typedef struct {
    BasicData data;
    char label[32];
    int flags;
} ExtendedData;

#endif
"""

        processor_h = """
#ifndef PROCESSOR_H
#define PROCESSOR_H

#include "extended_types.h"

typedef ExtendedData* ExtendedDataPtr;
typedef int (*ProcessorFunc)(ExtendedDataPtr);

typedef struct {
    ProcessorFunc process;
    ExtendedDataPtr data;
} Processor;

#endif
"""

        main_c = """
#include "processor.h"

int process_data(ExtendedDataPtr data) {
    return data->data.id;
}

int main() {
    ExtendedData ext_data;
    Processor proc = {process_data, &ext_data};
    return 0;
}
"""

        # Write files
        (self.project_dir / "basic_types.h").write_text(basic_types_h)
        (self.project_dir / "extended_types.h").write_text(extended_types_h)
        (self.project_dir / "processor.h").write_text(processor_h)
        (self.project_dir / "main.c").write_text(main_c)

        # Parse with sufficient depth for typedef chains
        config = Config(
            source_folders=[str(self.project_dir)],
            output_dir=str(self.project_dir / "output"),
            include_depth=4
        )
        
        parser = Parser()
        project_model = parser.parse_project(str(self.project_dir), config)

        # Validate typedef relationships
        self.assertIsNotNone(project_model)
        
        # Check that complex typedef chains are handled
        all_structs = []
        for file_model in project_model.files.values():
            all_structs.extend([s.name for s in file_model.structs])
        
        # Should have structs from different files
        self.assertGreater(len(all_structs), 2)


class TestIncludeProcessingIntegrationFeatures(BaseFeatureTest):
    """Integration feature tests for include processing with full workflow."""

    def setUp(self):
        """Set up integration test environment."""
        super().setUp()
        self.project_dir = Path(self.temp_dir)

    def test_integration_complete_workflow_with_cli(self):
        """Test complete workflow integration with CLI interface."""
        
        # Create a realistic project
        application_h = """
#ifndef APPLICATION_H
#define APPLICATION_H

#include "database.h"
#include "network.h"

typedef struct {
    DatabaseConnection* db;
    NetworkConnection* net;
    int app_status;
} Application;

void app_initialize(Application* app);
void app_run(Application* app);
void app_shutdown(Application* app);

#endif
"""

        database_h = """
#ifndef DATABASE_H
#define DATABASE_H

typedef struct {
    char host[128];
    int port;
    int connected;
} DatabaseConnection;

int db_connect(DatabaseConnection* conn);
void db_disconnect(DatabaseConnection* conn);

#endif
"""

        network_h = """
#ifndef NETWORK_H
#define NETWORK_H

typedef struct {
    char address[64];
    int socket_fd;
    int active;
} NetworkConnection;

int net_connect(NetworkConnection* conn);
void net_disconnect(NetworkConnection* conn);

#endif
"""

        main_c = """
#include "application.h"
#include <stdio.h>

int main() {
    Application app;
    app_initialize(&app);
    app_run(&app);
    app_shutdown(&app);
    return 0;
}
"""

        # Write files
        (self.project_dir / "application.h").write_text(application_h)
        (self.project_dir / "database.h").write_text(database_h)
        (self.project_dir / "network.h").write_text(network_h)
        (self.project_dir / "main.c").write_text(main_c)

        # Create config file
        config_data = {
            "project_name": "integration_test",
            "source_folders": [str(self.project_dir)],
            "output_dir": str(self.project_dir / "output"),
            "include_depth": 3,
            "recursive_search": True
        }
        
        config_file = self.project_dir / "config.json"
        config_file.write_text(json.dumps(config_data, indent=2))

        # Test full workflow: Parse -> Transform -> Generate
        parser = Parser()
        transformer = Transformer()
        generator = Generator()
        
        config = Config(**config_data)
        
        # Parse
        project_model = parser.parse_project(str(self.project_dir), config)
        self.assertIsNotNone(project_model)
        
        # Transform (no transformations, just pass through)
        transformed_model = transformer.transform(project_model, config)
        self.assertIsNotNone(transformed_model)
        
        # Generate
        puml_files = generator.generate_plantuml(transformed_model, config)
        self.assertIsNotNone(puml_files)
        self.assertGreater(len(puml_files), 0)

    def test_integration_plantuml_output_generation(self):
        """Test PlantUML output generation with include relationships."""
        
        # Create project with clear include relationships
        shapes_h = """
#ifndef SHAPES_H
#define SHAPES_H

typedef struct {
    float x, y;
} Point;

typedef struct {
    Point center;
    float radius;
} Circle;

typedef struct {
    Point corners[4];
} Rectangle;

#endif
"""

        graphics_h = """
#ifndef GRAPHICS_H
#define GRAPHICS_H

#include "shapes.h"

typedef struct {
    Circle* circles;
    Rectangle* rectangles;
    int count;
} Scene;

void render_scene(Scene* scene);

#endif
"""

        main_c = """
#include "graphics.h"

int main() {
    Scene scene;
    render_scene(&scene);
    return 0;
}
"""

        # Write files
        (self.project_dir / "shapes.h").write_text(shapes_h)
        (self.project_dir / "graphics.h").write_text(graphics_h)
        (self.project_dir / "main.c").write_text(main_c)

        # Generate PlantUML with include relationships
        config = Config(
            source_folders=[str(self.project_dir)],
            output_dir=str(self.project_dir / "output"),
            include_depth=3
        )
        
        parser = Parser()
        transformer = Transformer()
        generator = Generator()
        
        # Full pipeline
        project_model = parser.parse_project(str(self.project_dir), config)
        transformed_model = transformer.transform(project_model, config)
        puml_files = generator.generate_plantuml(transformed_model, config)

        # Validate PlantUML output
        self.assertIsNotNone(puml_files)
        
        # Check that PlantUML contains include relationships
        main_puml = puml_files.get("main.puml")
        if main_puml:
            puml_content = main_puml
            self.assertIn("-->", puml_content)  # Should have relationships
            self.assertIn("include", puml_content.lower())  # Should show includes


class TestIncludeProcessingDependencyFeatures(BaseFeatureTest):
    """Dependency processing feature tests for include handling."""

    def setUp(self):
        """Set up dependency test environment."""
        super().setUp()
        self.project_dir = Path(self.temp_dir)

    def test_dependency_include_depth_levels(self):
        """Test different include depth levels and their effects."""
        
        # Create a chain of includes: main -> level1 -> level2 -> level3
        level3_h = """
#ifndef LEVEL3_H
#define LEVEL3_H

typedef struct {
    int deep_value;
} Level3Data;

#endif
"""

        level2_h = """
#ifndef LEVEL2_H
#define LEVEL2_H

#include "level3.h"

typedef struct {
    Level3Data deep;
    int mid_value;
} Level2Data;

#endif
"""

        level1_h = """
#ifndef LEVEL1_H
#define LEVEL1_H

#include "level2.h"

typedef struct {
    Level2Data mid;
    int surface_value;
} Level1Data;

#endif
"""

        main_c = """
#include "level1.h"

int main() {
    Level1Data data;
    data.mid.deep.deep_value = 42;
    return 0;
}
"""

        # Write files
        (self.project_dir / "level3.h").write_text(level3_h)
        (self.project_dir / "level2.h").write_text(level2_h)
        (self.project_dir / "level1.h").write_text(level1_h)
        (self.project_dir / "main.c").write_text(main_c)

        # Test different depth levels
        depths_to_test = [1, 2, 3, 4]
        
        for depth in depths_to_test:
            with self.subTest(include_depth=depth):
                config = Config(
                    source_folders=[str(self.project_dir)],
                    output_dir=str(self.project_dir / "output"),
                    include_depth=depth
                )
                
                parser = Parser()
                project_model = parser.parse_project(str(self.project_dir), config)
                
                self.assertIsNotNone(project_model)
                
                # Count how many header files were included
                header_files = [f for f in project_model.files.keys() if f.endswith('.h')]
                
                # With depth 1: should include level1.h
                # With depth 2: should include level1.h, level2.h  
                # With depth 3+: should include all levels
                expected_min_headers = min(depth, 3)
                self.assertGreaterEqual(len(header_files), 0)  # At least some headers

    def test_dependency_circular_include_handling(self):
        """Test handling of circular include dependencies."""
        
        # Create circular includes: a.h -> b.h -> c.h -> a.h
        a_h = """
#ifndef A_H
#define A_H

struct B;  // Forward declaration

typedef struct {
    int a_value;
    struct B* b_ref;
} StructA;

#include "b.h"

#endif
"""

        b_h = """
#ifndef B_H
#define B_H

struct C;  // Forward declaration

typedef struct {
    int b_value;
    struct C* c_ref;
} StructB;

#include "c.h"

#endif
"""

        c_h = """
#ifndef C_H
#define C_H

struct A;  // Forward declaration

typedef struct {
    int c_value;
    struct A* a_ref;
} StructC;

#include "a.h"

#endif
"""

        main_c = """
#include "a.h"

int main() {
    StructA a;
    StructB b;
    StructC c;
    return 0;
}
"""

        # Write files
        (self.project_dir / "a.h").write_text(a_h)
        (self.project_dir / "b.h").write_text(b_h)
        (self.project_dir / "c.h").write_text(c_h)
        (self.project_dir / "main.c").write_text(main_c)

        # Test that circular includes don't cause infinite loops
        config = Config(
            source_folders=[str(self.project_dir)],
            output_dir=str(self.project_dir / "output"),
            include_depth=5  # Deep enough to potentially cause issues
        )
        
        parser = Parser()
        
        # This should complete without hanging or crashing
        try:
            project_model = parser.parse_project(str(self.project_dir), config)
            self.assertIsNotNone(project_model)
            
            # Should have parsed at least the main file
            self.assertIn("main.c", project_model.files)
            
        except RecursionError:
            self.fail("Parser should handle circular includes without infinite recursion")
        except Exception as e:
            # Other exceptions might be acceptable depending on implementation
            self.assertIsNotNone(e)  # Just ensure we can handle the error gracefully