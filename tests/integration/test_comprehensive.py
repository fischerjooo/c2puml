#!/usr/bin/env python3
"""
Consolidated integration tests for the C to PlantUML converter.

This file consolidates tests from:
- test_include_processing_comprehensive.py
- test_parser_tokenizer_integration.py

Organized into logical test groups focusing on:
1. Comprehensive include processing integration
2. Parser-tokenizer integration scenarios
3. End-to-end system integration
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from c_to_plantuml.generator import Generator
from c_to_plantuml.parser import CParser, Parser
from c_to_plantuml.parser_tokenizer import CTokenizer
from c_to_plantuml.transformer import Transformer
from tests.feature.base import BaseFeatureTest


class TestIncludeProcessingIntegrationComprehensive(BaseFeatureTest):
    """Comprehensive integration tests for include processing."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.parser = Parser()
        self.transformer = Transformer()
        self.generator = Generator()

    def test_comprehensive_c_to_h_relationships_integration(self):
        """Test comprehensive C to H file relationships with full integration."""
        project_data = {
            "src/app.c": """
#include "core/engine.h"
#include "ui/window.h"
#include "utils/logger.h"

int main() {
    Engine* engine = engine_init();
    Window* window = window_create(800, 600, "App");

    log_info("Application started");

    while (engine_is_running(engine)) {
        window_update(window);
        engine_update(engine);
    }

    window_destroy(window);
    engine_cleanup(engine);
    return 0;
}
""",
            "src/core/engine.h": """
#ifndef ENGINE_H
#define ENGINE_H

#include "../graphics/renderer.h"
#include "../audio/sound.h"

typedef struct {
    Renderer* renderer;
    SoundSystem* audio;
    int running;
    double delta_time;
} Engine;

Engine* engine_init();
void engine_update(Engine* engine);
int engine_is_running(Engine* engine);
void engine_cleanup(Engine* engine);

#endif
""",
            "src/ui/window.h": """
#ifndef WINDOW_H
#define WINDOW_H

#include "../graphics/context.h"
#include "../input/keyboard.h"

typedef struct {
    GraphicsContext* context;
    KeyboardState* keyboard;
    int width, height;
    char* title;
} Window;

Window* window_create(int width, int height, const char* title);
void window_update(Window* window);
void window_destroy(Window* window);

#endif
""",
            "src/graphics/renderer.h": """
#ifndef RENDERER_H
#define RENDERER_H

#include "context.h"
#include "shader.h"

typedef struct {
    GraphicsContext* context;
    Shader* current_shader;
    int frame_count;
} Renderer;

#endif
""",
            "src/graphics/context.h": """
#ifndef CONTEXT_H
#define CONTEXT_H

typedef struct {
    void* native_handle;
    int api_version;
    int width, height;
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
            "src/audio/sound.h": """
#ifndef SOUND_H
#define SOUND_H

typedef struct {
    void* audio_device;
    float master_volume;
} SoundSystem;

#endif
""",
            "src/input/keyboard.h": """
#ifndef KEYBOARD_H
#define KEYBOARD_H

typedef struct {
    int keys[256];
    int key_count;
} KeyboardState;

#endif
""",
            "src/utils/logger.h": """
#ifndef LOGGER_H
#define LOGGER_H

#include <stdio.h>

void log_info(const char* message);
void log_error(const char* message);

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

        # Verify specific include relationships
        engine_file = None
        window_file = None

        for file_data in model_data["files"].values():
            if "engine.h" in file_data["name"]:
                engine_file = file_data
            elif "window.h" in file_data["name"]:
                window_file = file_data

        self.assertIsNotNone(engine_file)
        self.assertIsNotNone(window_file)

        # Check include relationships
        self.assertTrue(any("renderer.h" in inc for inc in engine_file["includes"]))
        self.assertTrue(any("sound.h" in inc for inc in engine_file["includes"]))
        self.assertTrue(any("context.h" in inc for inc in window_file["includes"]))
        self.assertTrue(any("keyboard.h" in inc for inc in window_file["includes"]))

    def test_comprehensive_header_to_header_relationships_integration(self):
        """Test comprehensive header to header relationships integration."""
        project_data = {
            "math/vector.h": """
#ifndef VECTOR_H
#define VECTOR_H

typedef struct {
    float x, y, z;
} Vector3;

Vector3 vector_add(Vector3 a, Vector3 b);

#endif
""",
            "math/matrix.h": """
#ifndef MATRIX_H
#define MATRIX_H

#include "vector.h"

typedef struct {
    float m[16];
} Matrix4;

Matrix4 matrix_translate(Vector3 translation);

#endif
""",
            "graphics/transform.h": """
#ifndef TRANSFORM_H
#define TRANSFORM_H

#include "../math/matrix.h"
#include "../math/vector.h"

typedef struct {
    Vector3 position;
    Vector3 rotation;
    Vector3 scale;
    Matrix4 world_matrix;
} Transform;

#endif
""",
            "graphics/camera.h": """
#ifndef CAMERA_H
#define CAMERA_H

#include "transform.h"

typedef struct {
    Transform transform;
    Matrix4 view_matrix;
    Matrix4 projection_matrix;
    float fov;
} Camera;

#endif
""",
            "main.c": """
#include "graphics/camera.h"

int main() {
    Camera camera;
    return 0;
}
""",
        }

        project_dir = self.create_temp_project(project_data)
        config_data = {
            "source_folders": [str(project_dir)],
            "include_depth": 4,
            "recursive_search": True,
        }

        results = self.run_full_pipeline(project_dir, config_data)

        with open(results["model_file"], "r") as f:
            model_data = json.load(f)

        # Verify all files were processed
        file_names = [file_data["name"] for file_data in model_data["files"].values()]
        # Since name field now contains just filenames, not paths, we expect just the basenames
        expected_files = {
            "main.c",
            "vector.h",
            "matrix.h",
            "transform.h",
            "camera.h",
        }
        actual_files = set(file_names)

        self.assertTrue(expected_files.issubset(actual_files))

        # Verify include chain: camera.h -> transform.h -> matrix.h -> vector.h
        camera_file = None
        transform_file = None
        matrix_file = None

        for file_data in model_data["files"].values():
            if "camera.h" in file_data["name"]:
                camera_file = file_data
            elif "transform.h" in file_data["name"]:
                transform_file = file_data
            elif "matrix.h" in file_data["name"]:
                matrix_file = file_data

        self.assertIsNotNone(camera_file)
        self.assertIsNotNone(transform_file)
        self.assertIsNotNone(matrix_file)

        # Verify include relationships
        self.assertIn("transform.h", camera_file["includes"])
        self.assertTrue(any("matrix.h" in inc for inc in transform_file["includes"]))
        self.assertTrue(any("vector.h" in inc for inc in transform_file["includes"]))
        self.assertIn("vector.h", matrix_file["includes"])

    def test_comprehensive_typedef_relationships_integration(self):
        """Test comprehensive typedef relationships across files integration."""
        project_data = {
            "main.c": """
#include "database/models.h"

int main() {
    User user = create_user("john", 25);
    Product product = create_product("laptop", 999.99);
    Order order = create_order(&user, &product);
    return 0;
}
""",
            "database/models.h": """
#ifndef MODELS_H
#define MODELS_H

#include "types.h"
#include "relationships.h"

typedef struct {
    UserId id;
    UserName name;
    Age age;
    Address address;
} User;

typedef struct {
    ProductId id;
    ProductName name;
    Price price;
    Category category;
} Product;

User create_user(const char* name, int age);
Product create_product(const char* name, double price);

#endif
""",
            "database/types.h": """
#ifndef TYPES_H
#define TYPES_H

typedef unsigned int UserId;
typedef unsigned int ProductId;
typedef unsigned int OrderId;
typedef char* UserName;
typedef char* ProductName;
typedef double Price;
typedef int Age;

typedef enum {
    ELECTRONICS,
    CLOTHING,
    BOOKS,
    OTHER
} Category;

typedef struct {
    char* street;
    char* city;
    char* zip_code;
} Address;

#endif
""",
            "database/relationships.h": """
#ifndef RELATIONSHIPS_H
#define RELATIONSHIPS_H

#include "types.h"

typedef struct {
    OrderId id;
    UserId user_id;
    ProductId product_id;
    int quantity;
    Price total_price;
} Order;

Order create_order(void* user, void* product);

#endif
""",
        }

        project_dir = self.create_temp_project(project_data)
        config_data = {"source_folders": [str(project_dir)], "include_depth": 3}

        results = self.run_full_pipeline(project_dir, config_data)

        with open(results["model_file"], "r") as f:
            model_data = json.load(f)

        # Verify typedef relationships are preserved
        models_file = None
        types_file = None
        relationships_file = None

        for file_data in model_data["files"].values():
            if "models.h" in file_data["name"]:
                models_file = file_data
            elif "types.h" in file_data["name"]:
                types_file = file_data
            elif "relationships.h" in file_data["name"]:
                relationships_file = file_data

        self.assertIsNotNone(models_file)
        self.assertIsNotNone(types_file)
        self.assertIsNotNone(relationships_file)

        # Verify include relationships
        self.assertIn("types.h", models_file["includes"])
        self.assertIn("relationships.h", models_file["includes"])
        self.assertIn("types.h", relationships_file["includes"])

        # Verify that structs were parsed
        self.assertTrue(len(models_file["structs"]) > 0)
        self.assertTrue(len(types_file["structs"]) > 0)
        self.assertTrue(len(relationships_file["structs"]) > 0)


class TestParserTokenizerIntegration(unittest.TestCase):
    """Integration tests for parser-tokenizer interaction."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.source_folder = Path(self.temp_dir)
        self.parser = CParser()
        self.tokenizer = CTokenizer()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = self.source_folder / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_parser_tokenizer_struct_parsing_integration(self):
        """Test that parser correctly uses tokenizer for struct parsing."""
        content = """
typedef struct ComplexStruct {
    int field1;
    char* field2;
    struct {
        float nested_field1;
        double nested_field2;
    } nested_struct;
    enum {
        OPTION_A,
        OPTION_B = 5,
        OPTION_C
    } options;
} ComplexStruct;
"""

        file_path = self.create_test_file("complex.h", content)
        file_model = self.parser.parse_file(file_path, "complex.h")

        # Verify struct was parsed correctly
        self.assertTrue(len(file_model.structs) > 0)

        # Check that complex struct was parsed
        struct_names = list(file_model.structs.keys())
        self.assertIn("ComplexStruct", struct_names)

        complex_struct = file_model.structs["ComplexStruct"]
        self.assertTrue(len(complex_struct.fields) > 0)

    def test_parser_tokenizer_function_parsing_integration(self):
        """Test that parser correctly uses tokenizer for function parsing."""
        content = """
int simple_function(void);

static inline double complex_function(
    const char* input,
    size_t input_length,
    void (*callback)(int, char*),
    struct {
        int option1;
        float option2;
    } config
) {
    return 0.0;
}

extern void* variadic_function(int count, ...);
"""

        file_path = self.create_test_file("functions.h", content)
        file_model = self.parser.parse_file(file_path, "functions.h")

        # Verify functions were parsed correctly
        self.assertTrue(len(file_model.functions) > 0)

        function_names = [func.name for func in file_model.functions]
        self.assertIn("simple_function", function_names)
        self.assertIn("complex_function", function_names)
        self.assertIn("variadic_function", function_names)

        # Check complex function parameters
        complex_func = None
        for func in file_model.functions:
            if func.name == "complex_function":
                complex_func = func
                break

        self.assertIsNotNone(complex_func)
        self.assertTrue(len(complex_func.parameters) > 0)

    def test_parser_tokenizer_preprocessor_integration(self):
        """Test that parser handles preprocessor directives through tokenizer."""
        content = """
#define MAX_SIZE 1024
#define STRINGIFY(x) #x
#define CONCAT(a, b) a ## b

#ifdef DEBUG
    #define LOG(msg) printf("DEBUG: %s\\n", msg)
#else
    #define LOG(msg)
#endif

typedef struct {
    char buffer[MAX_SIZE];
    int size;
} Buffer;

#if defined(WINDOWS)
    typedef void* Handle;
#elif defined(LINUX)
    typedef int Handle;
#else
    typedef void* Handle;
#endif
"""

        file_path = self.create_test_file("preprocessor.h", content)
        file_model = self.parser.parse_file(file_path, "preprocessor.h")

        # Verify that structs are still parsed despite preprocessor directives
        self.assertTrue(len(file_model.structs) > 0)
        struct_names = list(file_model.structs.keys())
        self.assertIn("Buffer", struct_names)

        # Verify macros were captured
        self.assertTrue(len(file_model.macros) > 0)

    def test_parser_tokenizer_complex_syntax_integration(self):
        """Test parser-tokenizer integration with complex C syntax."""
        content = """
// Complex typedef with function pointers and arrays
typedef struct {
    int (*compare_func)(const void* a, const void* b);
    void (*cleanup_func)(void* data);
    size_t (*size_func)(const void* data);
} VTable;

typedef struct Node {
    void* data;
    struct Node* next;
    struct Node* children[16];
    VTable* vtable;
} Node;

// Function with complex signature
Node* create_node(
    void* data,
    size_t data_size,
    int (*comparator)(const void*, const void*),
    void (*destructor)(void*)
);

// Enum with explicit values
typedef enum {
    STATE_INIT = 0x01,
    STATE_READY = 0x02,
    STATE_RUNNING = 0x04,
    STATE_PAUSED = 0x08,
    STATE_STOPPED = 0x10,
    STATE_ERROR = 0xFF
} NodeState;

// Union with bitfields
typedef union {
    struct {
        unsigned int state : 8;
        unsigned int flags : 8;
        unsigned int reserved : 16;
    } bits;
    uint32_t value;
} NodeStatus;
"""

        file_path = self.create_test_file("complex.h", content)
        file_model = self.parser.parse_file(file_path, "complex.h")

        # Verify complex structures were parsed
        self.assertTrue(len(file_model.structs) > 0)
        self.assertTrue(len(file_model.functions) > 0)
        self.assertTrue(len(file_model.enums) > 0)
        self.assertTrue(len(file_model.unions) > 0)

        # Check specific structures
        struct_names = list(file_model.structs.keys())
        self.assertIn("VTable", struct_names)
        self.assertIn("Node", struct_names)

        enum_names = list(file_model.enums.keys())
        self.assertIn("NodeState", enum_names)

        union_names = list(file_model.unions.keys())
        self.assertIn("NodeStatus", union_names)

    def test_parser_tokenizer_error_handling_integration(self):
        """Test that parser gracefully handles tokenizer errors."""
        # Content with syntax errors that tokenizer should handle
        content = """
// Valid content
typedef struct {
    int valid_field;
} ValidStruct;

// Malformed content that might cause tokenizer issues
typedef struct {
    int field1
    // Missing semicolon
    char* field2;
} MalformedStruct;

// Content that continues after error
typedef struct {
    float recovery_field;
} RecoveryStruct;
"""

        file_path = self.create_test_file("errors.h", content)

        # Should not crash despite syntax errors
        file_model = self.parser.parse_file(file_path, "complex.h")

        # Should still parse some valid structures
        self.assertIsNotNone(file_model)
        # May have parsed some structs despite errors
        # The exact behavior depends on error recovery implementation


class TestEndToEndSystemIntegration(BaseFeatureTest):
    """End-to-end system integration tests."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()

    def test_complete_system_integration_real_world_project(self):
        """Test complete system integration with realistic project."""
        project_data = {
            "src/main.c": """
#include "game/game.h"
#include "platform/platform.h"

int main(int argc, char** argv) {
    Platform platform;
    Game game;

    if (!platform_init(&platform)) {
        return -1;
    }

    if (!game_init(&game, &platform)) {
        platform_shutdown(&platform);
        return -1;
    }

    while (platform_is_running(&platform)) {
        platform_update(&platform);
        game_update(&game, platform_get_delta_time(&platform));
        game_render(&game);
    }

    game_shutdown(&game);
    platform_shutdown(&platform);

    return 0;
}
""",
            "src/game/game.h": """
#ifndef GAME_H
#define GAME_H

#include "../platform/platform.h"
#include "entities/player.h"
#include "world/level.h"
#include "rendering/renderer.h"

typedef struct {
    Platform* platform;
    Player player;
    Level current_level;
    Renderer renderer;
    double total_time;
} Game;

int game_init(Game* game, Platform* platform);
void game_update(Game* game, double delta_time);
void game_render(Game* game);
void game_shutdown(Game* game);

#endif
""",
            "src/game/entities/player.h": """
#ifndef PLAYER_H
#define PLAYER_H

#include "../../math/vector.h"
#include "../../physics/rigidbody.h"

typedef struct {
    Vector3 position;
    Vector3 velocity;
    RigidBody physics;
    float health;
    int score;
} Player;

#endif
""",
            "src/game/world/level.h": """
#ifndef LEVEL_H
#define LEVEL_H

#include "../entities/player.h"
#include "../../graphics/mesh.h"

typedef struct {
    Mesh* geometry;
    Player* players;
    int player_count;
    char* name;
} Level;

#endif
""",
            "src/game/rendering/renderer.h": """
#ifndef RENDERER_H
#define RENDERER_H

#include "../../graphics/context.h"
#include "../../graphics/shader.h"

typedef struct {
    GraphicsContext context;
    Shader* active_shader;
    int frame_count;
} Renderer;

#endif
""",
            "src/platform/platform.h": """
#ifndef PLATFORM_H
#define PLATFORM_H

typedef struct {
    void* window_handle;
    int window_width;
    int window_height;
    double last_frame_time;
} Platform;

int platform_init(Platform* platform);
void platform_update(Platform* platform);
int platform_is_running(Platform* platform);
double platform_get_delta_time(Platform* platform);
void platform_shutdown(Platform* platform);

#endif
""",
            "src/math/vector.h": """
#ifndef VECTOR_H
#define VECTOR_H

typedef struct {
    float x, y, z;
} Vector3;

Vector3 vector_add(Vector3 a, Vector3 b);
Vector3 vector_scale(Vector3 v, float scalar);

#endif
""",
            "src/physics/rigidbody.h": """
#ifndef RIGIDBODY_H
#define RIGIDBODY_H

#include "../math/vector.h"

typedef struct {
    Vector3 position;
    Vector3 velocity;
    Vector3 acceleration;
    float mass;
} RigidBody;

#endif
""",
            "src/graphics/context.h": """
#ifndef CONTEXT_H
#define CONTEXT_H

typedef struct {
    void* api_context;
    int api_version;
} GraphicsContext;

#endif
""",
            "src/graphics/shader.h": """
#ifndef SHADER_H
#define SHADER_H

typedef struct {
    unsigned int program_id;
    char* source_code;
} Shader;

#endif
""",
            "src/graphics/mesh.h": """
#ifndef MESH_H
#define MESH_H

typedef struct {
    float* vertices;
    unsigned int* indices;
    int vertex_count;
    int index_count;
} Mesh;

#endif
""",
        }

        project_dir = self.create_temp_project(project_data)
        config_data = {
            "source_folders": [str(project_dir / "src")],
            "include_depth": 5,
            "recursive_search": True,
            "file_extensions": [".c", ".h"],
            "generate_images": False,
        }

        # Run complete pipeline
        results = self.run_full_pipeline(project_dir, config_data)

        # Verify all stages completed
        self.assertTrue(results["model_file"].exists())
        self.assertTrue(results["transformed_model_file"].exists())

        # Load and verify model
        with open(results["model_file"], "r") as f:
            model_data = json.load(f)

        # Should process all files
        file_count = len(model_data["files"])
        self.assertGreaterEqual(file_count, 11)  # All files created

        # Verify include relationships are preserved across deep hierarchy
        game_file = None
        for file_data in model_data["files"].values():
            if "game.h" in file_data["name"]:
                game_file = file_data
                break

        self.assertIsNotNone(game_file)

        # game.h should include its dependencies
        includes = game_file["includes"]
        self.assertTrue(any("platform.h" in inc for inc in includes))
        self.assertTrue(any("player.h" in inc for inc in includes))
        self.assertTrue(any("level.h" in inc for inc in includes))
        self.assertTrue(any("renderer.h" in inc for inc in includes))

        # Verify PlantUML output was generated
        output_dir = results["output_dir"]
        plantuml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(plantuml_files), 0)

        # Verify PlantUML content
        if plantuml_files:
            with open(plantuml_files[0], "r") as f:
                content = f.read()

            self.assertIn("@startuml", content)
            self.assertIn("@enduml", content)
            # Should contain some of our defined structures
            self.assertTrue(
                any(
                    struct_name in content
                    for struct_name in ["Game", "Player", "Platform", "Vector3"]
                )
            )


if __name__ == "__main__":
    unittest.main()
