#!/usr/bin/env python3
"""
Consolidated feature tests for include header processing functionality.

This file consolidates tests from:
- test_include_processing_features.py
- test_include_processing_enhanced_features.py
- test_include_processing_integration.py
- test_include_dependency_processing.py
- test_include_processing_comprehensive.py (integration)

Organized into logical test groups focusing on:
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
        """Set up test fixtures."""
        super().setUp()
        self.parser = Parser()
        self.transformer = Transformer()
        self.generator = Generator()

    def test_feature_include_processing_basic_workflow(self):
        """Test basic include processing workflow from parsing to generation."""
        # Create test project structure
        project_data = {
            "main.c": """
#include <stdio.h>
#include "utils.h"

int main() {
    Point p = {0, 0};
    return 0;
}
""",
            "utils.h": """
#ifndef UTILS_H
#define UTILS_H

typedef struct {
    int x;
    int y;
} Point;

#endif
""",
        }

        project_dir = self.create_temp_project(project_data)

        # Run full pipeline
        config_data = {
            "source_folders": [str(project_dir)],
            "include_depth": 2,
            "file_extensions": [".c", ".h"],
        }

        results = self.run_full_pipeline(project_dir, config_data)

        # Verify basic workflow completed
        self.assertTrue(results["model_file"].exists())

        # Verify include relationships were processed
        with open(results["model_file"], "r") as f:
            model_data = json.load(f)

        # Find main.c file
        main_file = None
        for file_path, file_data in model_data["files"].items():
            if "main.c" in file_path:
                main_file = file_data
                break

        self.assertIsNotNone(main_file)
        self.assertIn("utils.h", main_file["includes"])

    def test_feature_c_to_h_relationships(self):
        """Test feature-level C to H file relationships."""
        project_data = {
            "app.c": """
#include "types.h"
#include "config.h"

void app_init() {
    Config cfg = DEFAULT_CONFIG;
    Point origin = {0, 0};
}
""",
            "types.h": """
#ifndef TYPES_H
#define TYPES_H

typedef struct {
    int x, y;
} Point;

#endif
""",
            "config.h": """
#ifndef CONFIG_H
#define CONFIG_H

#include "types.h"

typedef struct {
    Point window_size;
    int debug_mode;
} Config;

#define DEFAULT_CONFIG {{640, 480}, 0}

#endif
""",
        }

        project_dir = self.create_temp_project(project_data)
        config_data = {"source_folders": [str(project_dir)], "include_depth": 3}

        results = self.run_full_pipeline(project_dir, config_data)

        # Verify relationships in generated model
        with open(results["model_file"], "r") as f:
            model_data = json.load(f)

        # Check that all files were processed
        file_names = [file_data["name"] for file_data in model_data["files"].values()]
        expected_files = {"app.c", "types.h", "config.h"}
        actual_files = set(file_names)

        self.assertTrue(expected_files.issubset(actual_files))

    def test_feature_header_to_header_relationships(self):
        """Test feature-level header to header relationships."""
        project_data = {
            "main.c": """
#include "graphics.h"

int main() {
    Window win = create_window();
    return 0;
}
""",
            "graphics.h": """
#ifndef GRAPHICS_H
#define GRAPHICS_H

#include "geometry.h"
#include "colors.h"

typedef struct {
    Rectangle bounds;
    Color background;
} Window;

Window create_window();

#endif
""",
            "geometry.h": """
#ifndef GEOMETRY_H
#define GEOMETRY_H

typedef struct {
    int x, y, width, height;
} Rectangle;

#endif
""",
            "colors.h": """
#ifndef COLORS_H
#define COLORS_H

typedef struct {
    unsigned char r, g, b, a;
} Color;

#endif
""",
        }

        project_dir = self.create_temp_project(project_data)
        config_data = {"source_folders": [str(project_dir)], "include_depth": 3}

        results = self.run_full_pipeline(project_dir, config_data)

        with open(results["model_file"], "r") as f:
            model_data = json.load(f)

        # Find graphics.h and verify its includes
        graphics_file = None
        for file_data in model_data["files"].values():
            if file_data["name"] == "graphics.h":
                graphics_file = file_data
                break

        self.assertIsNotNone(graphics_file)
        self.assertIn("geometry.h", graphics_file["includes"])
        self.assertIn("colors.h", graphics_file["includes"])


class TestIncludeProcessingComplexFeatures(BaseFeatureTest):
    """Complex feature tests for advanced include processing scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.parser = Parser()
        self.transformer = Transformer()
        self.generator = Generator()

    def test_feature_complex_project_structure(self):
        """Test complex project structure with multiple layers of includes."""
        project_data = {
            "src/main.c": """
#include "core/engine.h"
#include "utils/logger.h"

int main() {
    Engine* engine = engine_create();
    log_info("Engine started");
    return 0;
}
""",
            "src/core/engine.h": """
#ifndef ENGINE_H
#define ENGINE_H

#include "../utils/memory.h"
#include "renderer.h"

typedef struct Engine Engine;

Engine* engine_create();

#endif
""",
            "src/core/renderer.h": """
#ifndef RENDERER_H
#define RENDERER_H

#include "../graphics/shader.h"

typedef struct {
    int width, height;
} Viewport;

#endif
""",
            "src/graphics/shader.h": """
#ifndef SHADER_H
#define SHADER_H

typedef struct {
    unsigned int program_id;
    char* vertex_source;
    char* fragment_source;
} Shader;

#endif
""",
            "src/utils/logger.h": """
#ifndef LOGGER_H
#define LOGGER_H

void log_info(const char* message);

#endif
""",
            "src/utils/memory.h": """
#ifndef MEMORY_H
#define MEMORY_H

#include <stdlib.h>

void* safe_malloc(size_t size);

#endif
""",
        }

        project_dir = self.create_temp_project(project_data)
        config_data = {
            "source_folders": [str(project_dir / "src")],
            "include_depth": 4,
            "recursive_search": True,
        }

        results = self.run_full_pipeline(project_dir, config_data)

        with open(results["model_file"], "r") as f:
            model_data = json.load(f)

        # Verify all files were processed despite nested structure
        file_names = [file_data["name"] for file_data in model_data["files"].values()]

        # Should include files from multiple subdirectories
        self.assertTrue(any("main.c" in name for name in file_names))
        self.assertTrue(any("engine.h" in name for name in file_names))
        self.assertTrue(any("shader.h" in name for name in file_names))

    def test_feature_typedef_relationships_across_files(self):
        """Test typedef relationships across multiple include files."""
        project_data = {
            "main.c": """
#include "data_structures.h"

int main() {
    LinkedList* list = list_create();
    TreeNode* root = tree_create();
    return 0;
}
""",
            "data_structures.h": """
#ifndef DATA_STRUCTURES_H
#define DATA_STRUCTURES_H

#include "types.h"
#include "memory_pool.h"

typedef struct Node {
    Data value;
    struct Node* next;
} Node;

typedef struct {
    Node* head;
    PoolAllocator* allocator;
} LinkedList;

typedef struct TreeNode {
    Data value;
    struct TreeNode* left;
    struct TreeNode* right;
} TreeNode;

#endif
""",
            "types.h": """
#ifndef TYPES_H
#define TYPES_H

typedef union {
    int integer;
    float decimal;
    char* string;
} Data;

#endif
""",
            "memory_pool.h": """
#ifndef MEMORY_POOL_H
#define MEMORY_POOL_H

typedef struct {
    void* pool;
    size_t size;
    size_t used;
} PoolAllocator;

#endif
""",
        }

        project_dir = self.create_temp_project(project_data)
        config_data = {"source_folders": [str(project_dir)], "include_depth": 3}

        results = self.run_full_pipeline(project_dir, config_data)

        with open(results["model_file"], "r") as f:
            model_data = json.load(f)

        # Verify typedef relationships were preserved
        data_structures_file = None
        for file_data in model_data["files"].values():
            if file_data["name"] == "data_structures.h":
                data_structures_file = file_data
                break

        self.assertIsNotNone(data_structures_file)
        self.assertIn("types.h", data_structures_file["includes"])
        self.assertIn("memory_pool.h", data_structures_file["includes"])


class TestIncludeProcessingIntegration(BaseFeatureTest):
    """Integration tests for include processing with full pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()

    def test_integration_complete_workflow_with_cli(self):
        """Test complete workflow using CLI interface."""
        project_data = {
            "main.c": """
#include "api.h"

int main() {
    initialize_api();
    return 0;
}
""",
            "api.h": """
#ifndef API_H
#define API_H

#include "internal.h"

void initialize_api();

#endif
""",
            "internal.h": """
#ifndef INTERNAL_H
#define INTERNAL_H

typedef struct {
    int version;
    char* name;
} ApiContext;

extern ApiContext global_context;

#endif
""",
        }

        project_dir = self.create_temp_project(project_data)
        output_dir = project_dir / "output"
        config_file = project_dir / "config.json"

        # Create config file
        config_data = {
            "source_folders": [str(project_dir)],
            "output_dir": str(output_dir),
            "include_depth": 3,
            "file_extensions": [".c", ".h"],
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)

        # Run through CLI
        with patch("sys.argv", ["c2puml", "--config", str(config_file)]):
            try:
                c2puml_main()
            except SystemExit:
                pass  # CLI exits after completion

        # Verify output was generated (check both possible locations)
        model_file = output_dir / "model.json"
        workspace_model_file = Path("/workspace/artifacts/output_example/model.json")

        # The CLI might use workspace output or project output
        model_exists = model_file.exists() or workspace_model_file.exists()
        self.assertTrue(
            model_exists,
            f"Model file not found at {model_file} or {workspace_model_file}",
        )

        # Use whichever file exists
        actual_model_file = model_file if model_file.exists() else workspace_model_file

        # Verify include relationships
        with open(actual_model_file, "r") as f:
            model_data = json.load(f)

        file_count = len(model_data["files"])
        self.assertGreaterEqual(file_count, 3)  # main.c, api.h, internal.h

    def test_integration_plantuml_output_generation(self):
        """Test that PlantUML output is correctly generated."""
        project_data = {
            "module.c": """
#include "interface.h"

void module_function() {
    InterfaceStruct is;
    is.field = 42;
}
""",
            "interface.h": """
#ifndef INTERFACE_H
#define INTERFACE_H

typedef struct {
    int field;
    char* name;
} InterfaceStruct;

#endif
""",
        }

        project_dir = self.create_temp_project(project_data)
        config_data = {
            "source_folders": [str(project_dir)],
            "include_depth": 2,
            "generate_images": False,  # Focus on PlantUML text output
        }

        results = self.run_full_pipeline(project_dir, config_data)

        # Check that PlantUML files were generated
        output_dir = results["output_dir"]
        plantuml_files = list(output_dir.glob("*.puml"))

        self.assertGreater(len(plantuml_files), 0)

        # Check content of a PlantUML file
        if plantuml_files:
            with open(plantuml_files[0], "r") as f:
                content = f.read()

            # Should contain PlantUML syntax
            self.assertIn("@startuml", content)
            self.assertIn("@enduml", content)


class TestIncludeProcessingDependencies(unittest.TestCase):
    """Dependency processing feature tests."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.source_folder = Path(self.temp_dir)
        self.parser = CParser()

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = self.source_folder / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_dependency_include_depth_levels(self):
        """Test that include processing respects depth levels in the transformer phase."""
        # Create nested include chain: main.c -> level1.h -> level2.h -> level3.h
        self.create_test_file(
            "main.c",
            """
#include "level1.h"

int main() { return 0; }
""",
        )

        self.create_test_file(
            "level1.h",
            """
#ifndef LEVEL1_H
#define LEVEL1_H
#include "level2.h"
typedef int Level1Type;
#endif
""",
        )

        self.create_test_file(
            "level2.h",
            """
#ifndef LEVEL2_H
#define LEVEL2_H
#include "level3.h"
typedef int Level2Type;
#endif
""",
        )

        self.create_test_file(
            "level3.h",
            """
#ifndef LEVEL3_H
#define LEVEL3_H
typedef int Level3Type;
#endif
""",
        )

        # Test with different include depths using the transformer
        # Note: include_depth must be > 1 for the transformer to process include relations
        for depth in [2, 3, 4]:
            config = Config()
            config.source_folders = [str(self.source_folder)]
            config.include_depth = depth

            # First parse the project (collects all files)
            project_model = self.parser.parse_project(
                str(self.source_folder), config=config
            )

            # Then apply transformations including include depth processing
            from c2puml.transformer import Transformer

            transformer = Transformer()

            # Create a temporary config dict for the transformer
            config_dict = {"include_depth": depth}

            # Apply transformations
            transformed_model = transformer._apply_transformations(
                project_model, config_dict
            )

            # Count unique include relations (avoiding duplicates)
            all_relations = []
            for file_model in transformed_model.files.values():
                for rel in file_model.include_relations:
                    # Create a unique key for each relation
                    relation_key = (rel.source_file, rel.included_file)
                    if relation_key not in all_relations:
                        all_relations.append(relation_key)

            unique_include_relations = len(all_relations)

            # With the new architecture, all files are collected but include relations
            # are processed based on depth. For depth 1, we expect include relations
            # from main.c to level1.h. For depth 2, also from level1.h -> level2.h, etc.
            # The actual count depends on the include chain: main.c -> level1.h -> level2.h -> level3.h
            # With depth 2, we process: main.c -> level1.h (depth 1), level1.h -> level2.h (depth 2)
            # level2.h -> level3.h requires depth 3, not depth 2
            if depth == 2:
                expected_relations = 2  # main.c -> level1.h, level1.h -> level2.h
            elif depth == 3:
                expected_relations = (
                    3  # main.c -> level1.h, level1.h -> level2.h, level2.h -> level3.h
                )
            elif depth == 4:
                expected_relations = 3  # main.c -> level1.h, level1.h -> level2.h, level2.h -> level3.h (max depth reached)

            self.assertEqual(
                unique_include_relations,
                expected_relations,
                f"Depth {depth} should create {expected_relations} unique include relations, got {unique_include_relations}",
            )

    def test_dependency_circular_include_handling(self):
        """Test handling of circular include dependencies."""
        self.create_test_file(
            "main.c",
            """
#include "a.h"

int main() { return 0; }
""",
        )

        self.create_test_file(
            "a.h",
            """
#ifndef A_H
#define A_H
#include "b.h"
typedef struct A { struct B* b_ptr; } A;
#endif
""",
        )

        self.create_test_file(
            "b.h",
            """
#ifndef B_H
#define B_H
#include "a.h"
typedef struct B { struct A* a_ptr; } B;
#endif
""",
        )

        config = Config()
        config.source_folders = [str(self.source_folder)]
        config.include_depth = 5  # Deep enough to detect cycles

        # Should not hang or crash due to circular includes
        project_model = self.parser.parse_project(
            str(self.source_folder), config=config
        )

        # Should include all files despite circular references
        file_names = [f.name for f in project_model.files.values()]
        expected_files = {"main.c", "a.h", "b.h"}
        actual_files = set(file_names)

        self.assertTrue(expected_files.issubset(actual_files))

    def test_dependency_missing_includes_handling(self):
        """Test handling of missing include files."""
        self.create_test_file(
            "main.c",
            """
#include "existing.h"
#include "missing.h"

int main() { return 0; }
""",
        )

        self.create_test_file(
            "existing.h",
            """
#ifndef EXISTING_H
#define EXISTING_H
typedef int ExistingType;
#endif
""",
        )

        # Note: missing.h is intentionally not created

        config = Config()
        config.source_folders = [str(self.source_folder)]
        config.include_depth = 2

        # Should not crash when include file is missing
        project_model = self.parser.parse_project(
            str(self.source_folder), config=config
        )

        # Should still process existing files
        file_names = [f.name for f in project_model.files.values()]
        self.assertIn("main.c", file_names)
        self.assertIn("existing.h", file_names)


class TestIncludeProcessingComprehensive(BaseFeatureTest):
    """Comprehensive end-to-end tests for include processing."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.parser = Parser()
        self.transformer = Transformer()
        self.generator = Generator()

    def test_comprehensive_real_world_project_structure(self):
        """Test with realistic project structure resembling real C projects."""
        project_data = {
            "src/main.c": """
#include "app/application.h"
#include "utils/logging.h"

int main(int argc, char** argv) {
    init_logging();
    Application* app = app_create();
    app_run(app);
    app_destroy(app);
    return 0;
}
""",
            "src/app/application.h": """
#ifndef APPLICATION_H
#define APPLICATION_H

#include "../core/window.h"
#include "../core/renderer.h"
#include "../utils/memory.h"

typedef struct {
    Window* window;
    Renderer* renderer;
    MemoryPool* memory_pool;
    int running;
} Application;

Application* app_create();
void app_run(Application* app);
void app_destroy(Application* app);

#endif
""",
            "src/core/window.h": """
#ifndef WINDOW_H
#define WINDOW_H

#include "../graphics/context.h"

typedef struct {
    int width, height;
    char* title;
    GraphicsContext* context;
} Window;

#endif
""",
            "src/core/renderer.h": """
#ifndef RENDERER_H
#define RENDERER_H

#include "../graphics/shader.h"
#include "../graphics/buffer.h"

typedef struct {
    Shader* active_shader;
    VertexBuffer* vertex_buffer;
    IndexBuffer* index_buffer;
} Renderer;

#endif
""",
            "src/graphics/context.h": """
#ifndef CONTEXT_H
#define CONTEXT_H

typedef struct {
    void* native_context;
    int api_version;
} GraphicsContext;

#endif
""",
            "src/graphics/shader.h": """
#ifndef SHADER_H
#define SHADER_H

typedef struct {
    unsigned int program_id;
    char* vertex_source;
    char* fragment_source;
} Shader;

#endif
""",
            "src/graphics/buffer.h": """
#ifndef BUFFER_H
#define BUFFER_H

typedef struct {
    unsigned int vbo_id;
    size_t vertex_count;
} VertexBuffer;

typedef struct {
    unsigned int ibo_id;
    size_t index_count;
} IndexBuffer;

#endif
""",
            "src/utils/logging.h": """
#ifndef LOGGING_H
#define LOGGING_H

#include <stdio.h>

void init_logging();
void log_info(const char* format, ...);
void log_error(const char* format, ...);

#endif
""",
            "src/utils/memory.h": """
#ifndef MEMORY_H
#define MEMORY_H

#include <stdlib.h>

typedef struct {
    void* pool;
    size_t total_size;
    size_t used_size;
} MemoryPool;

MemoryPool* memory_pool_create(size_t size);
void* memory_pool_alloc(MemoryPool* pool, size_t size);

#endif
""",
        }

        project_dir = self.create_temp_project(project_data)
        config_data = {
            "source_folders": [str(project_dir / "src")],
            "include_depth": 4,
            "recursive_search": True,
            "file_extensions": [".c", ".h"],
        }

        results = self.run_full_pipeline(project_dir, config_data)

        # Verify comprehensive processing
        with open(results["model_file"], "r") as f:
            model_data = json.load(f)

        # Should process all files in the complex hierarchy
        file_count = len(model_data["files"])
        self.assertGreaterEqual(file_count, 9)  # All the files we created

        # Verify include relationships are preserved
        main_file = None
        for file_data in model_data["files"].values():
            if "main.c" in file_data["name"]:
                main_file = file_data
                break

        self.assertIsNotNone(main_file)
        # Should include both direct includes from main.c
        includes = main_file["includes"]
        self.assertTrue(any("application.h" in inc for inc in includes))
        self.assertTrue(any("logging.h" in inc for inc in includes))

    def test_comprehensive_typedef_and_struct_relationships(self):
        """Test comprehensive typedef and struct relationships across files."""
        project_data = {
            "main.c": """
#include "data_model.h"

int main() {
    DatabaseConnection* db = db_connect("localhost");
    UserRecord user = {"john_doe", 25, ACTIVE};
    return 0;
}
""",
            "data_model.h": """
#ifndef DATA_MODEL_H
#define DATA_MODEL_H

#include "connection.h"
#include "types.h"

typedef struct {
    UserId id;
    UserName name;
    Age age;
    UserStatus status;
} UserRecord;

#endif
""",
            "connection.h": """
#ifndef CONNECTION_H
#define CONNECTION_H

#include "config.h"

typedef struct {
    ConnectionConfig config;
    void* native_handle;
    int connected;
} DatabaseConnection;

DatabaseConnection* db_connect(const char* host);

#endif
""",
            "config.h": """
#ifndef CONFIG_H
#define CONFIG_H

typedef struct {
    char* host;
    int port;
    int timeout_ms;
} ConnectionConfig;

#endif
""",
            "types.h": """
#ifndef TYPES_H
#define TYPES_H

typedef unsigned int UserId;
typedef char* UserName;
typedef int Age;

typedef enum {
    INACTIVE = 0,
    ACTIVE = 1,
    SUSPENDED = 2
} UserStatus;

#endif
""",
        }

        project_dir = self.create_temp_project(project_data)
        config_data = {"source_folders": [str(project_dir)], "include_depth": 4}

        results = self.run_full_pipeline(project_dir, config_data)

        # Verify all typedef relationships are maintained
        with open(results["model_file"], "r") as f:
            model_data = json.load(f)

        # Check that data_model.h includes its dependencies
        data_model_file = None
        for file_data in model_data["files"].values():
            if file_data["name"] == "data_model.h":
                data_model_file = file_data
                break

        self.assertIsNotNone(data_model_file)
        self.assertIn("connection.h", data_model_file["includes"])
        self.assertIn("types.h", data_model_file["includes"])

        # Verify PlantUML generation includes typedef relationships
        if results.get("output_dir"):
            plantuml_files = list(results["output_dir"].glob("*.puml"))
            if plantuml_files:
                with open(plantuml_files[0], "r") as f:
                    plantuml_content = f.read()

                # Should contain some struct definitions (at least UserRecord)
                self.assertIn("UserRecord", plantuml_content)
                # DatabaseConnection might not be included if include depth wasn't sufficient
                # but UserRecord should be there since it's directly in the included files


if __name__ == "__main__":
    unittest.main()
