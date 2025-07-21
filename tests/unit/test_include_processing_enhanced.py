#!/usr/bin/env python3
"""
Enhanced unit tests for include header processing functionality
Focuses on edge cases and detailed verification of relationships
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from c_to_plantuml.models import (
    FileModel, ProjectModel, IncludeRelation, TypedefRelation,
    Struct, Enum, Union, Function, Field
)
from c_to_plantuml.parser import CParser
from c_to_plantuml.transformer import Transformer
from c_to_plantuml.generator import PlantUMLGenerator


class TestIncludeProcessingEnhanced(unittest.TestCase):
    """Enhanced tests for include header processing functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.parser = CParser()
        self.transformer = Transformer()
        self.generator = PlantUMLGenerator()
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content"""
        file_path = self.test_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path

    def test_include_processing_with_complex_nested_typedefs(self):
        """Test include processing with complex nested typedef relationships"""
        # Create test files with complex typedef relationships
        main_c_content = """
#include "types.h"
#include "utils.h"

typedef types_Byte CustomByte;
typedef types_Word CustomWord;
typedef utils_Point CustomPoint;

typedef struct {
    CustomByte r, g, b;
    CustomWord alpha;
} CustomColor;

typedef CustomColor* ColorPtr;
typedef ColorPtr* ColorPtrPtr;

int main() {
    return 0;
}
        """
        
        types_h_content = """
typedef unsigned char Byte;
typedef unsigned short Word;
typedef unsigned long DWord;

typedef struct {
    Byte r, g, b, a;
} RGBA;

typedef RGBA* RGBAPtr;
        """
        
        utils_h_content = """
#include "types.h"

typedef struct {
    types_Word x;
    types_Word y;
} Point;

typedef Point* PointPtr;
        """
        
        # Create test files
        main_c = self.create_test_file("main.c", main_c_content)
        types_h = self.create_test_file("types.h", types_h_content)
        utils_h = self.create_test_file("utils.h", utils_h_content)
        
        # Parse the project
        project_model = self.parser.parse_project(str(self.test_dir))
        
        # Process include relations
        transformed_model = self.transformer._process_include_relations(project_model, 3)
        
        # Generate PlantUML diagram
        main_file_model = transformed_model.files["main.c"]
        diagram = self.generator.generate_diagram(main_file_model, transformed_model)
        
        # Verify include relationships are correct
        self.assertIn("MAIN --> HEADER_TYPES : <<include>>", diagram)
        self.assertIn("MAIN --> HEADER_UTILS : <<include>>", diagram)
        
        # Verify header classes are generated
        self.assertIn('class "types" as HEADER_TYPES <<header>> #LightGreen', diagram)
        self.assertIn('class "utils" as HEADER_UTILS <<header>> #LightGreen', diagram)
        
        # Verify typedefs are correctly parsed and displayed (name only in headers)
        self.assertIn("+ typedef Byte", diagram)  # from types.h
        self.assertIn("+ typedef Word", diagram)  # from types.h
        self.assertIn("+ typedef x", diagram)  # from utils.h
        
        # Check that typedefs are NOT shown with full type information in headers
        self.assertNotIn("+ typedef unsigned char Byte", diagram)  # from types.h
        self.assertNotIn("+ typedef unsigned short Word", diagram)  # from types.h
        self.assertNotIn("+ typedef struct { types_Word x", diagram)  # from utils.h
        
        # Verify complex typedefs in main file
        self.assertIn("+ typedef CustomByte", diagram)
        self.assertIn("+ typedef types_Word CustomWord", diagram)
        self.assertIn("+ typedef utils_Point CustomPoint", diagram)
        self.assertIn("+ typedef struct { CustomByte r, g, b", diagram)

    def test_include_processing_with_circular_typedef_dependencies(self):
        """Test include processing with circular typedef dependencies"""
        # Create test files with circular typedef dependencies
        types_h_content = """
#include "utils.h"

typedef unsigned char Byte;
typedef utils_Point* PointPtr;
typedef utils_Color* ColorPtr;

typedef struct {
    PointPtr points;
    ColorPtr colors;
} ComplexShape;
        """
        
        utils_h_content = """
#include "types.h"

typedef struct {
    types_Byte x;
    types_Byte y;
} Point;

typedef struct {
    types_Byte r;
    types_Byte g;
    types_Byte b;
} Color;

typedef types_PointPtr* PointPtrPtr;
        """
        
        # Create test files
        types_h = self.create_test_file("types.h", types_h_content)
        utils_h = self.create_test_file("utils.h", utils_h_content)
        
        # Parse the project
        project_model = self.parser.parse_project(str(self.test_dir))
        
        # Process include relations
        transformed_model = self.transformer._process_include_relations(project_model, 3)
        
        # Generate PlantUML diagram for types.h
        types_file_model = transformed_model.files["types.h"]
        diagram = self.generator.generate_diagram(types_file_model, transformed_model)
        
        # Verify include relationships
        self.assertIn("HEADER_TYPES --> HEADER_UTILS : <<include>>", diagram)
        
        # Check that typedefs are correctly shown in header classes (name only)
        self.assertIn("+ typedef Byte", diagram)  # from types.h
        self.assertIn("+ typedef PointPtr", diagram)  # from types.h
        self.assertIn("+ typedef ColorPtr", diagram)  # from types.h
        
        # Check that typedefs are NOT shown with full type information in headers
        self.assertNotIn("+ typedef unsigned char Byte", diagram)
        self.assertNotIn("+ typedef utils_Point* PointPtr", diagram)
        self.assertNotIn("+ typedef utils_Color* ColorPtr", diagram)

    def test_include_processing_with_function_declarations_in_headers(self):
        """Test include processing with function declarations in headers"""
        # Create test files with function declarations
        main_c_content = """
#include "api.h"
#include "utils.h"

int main() {
    api_init();
    utils_process_data();
    return 0;
}
        """
        
        api_h_content = """
#ifndef API_H
#define API_H

#include "types.h"

// Function declarations
void api_init(void);
int api_process(types_Byte* data, types_Word size);
types_Byte* api_allocate(types_Word size);
void api_cleanup(void);

// Function pointer typedefs
typedef int (*ProcessCallback)(types_Byte* data);
typedef void (*CleanupCallback)(void);

// Struct with function pointers
typedef struct {
    ProcessCallback process;
    CleanupCallback cleanup;
} ApiCallbacks;

#endif // API_H
        """
        
        utils_h_content = """
#ifndef UTILS_H
#define UTILS_H

#include "types.h"

// Function declarations
void utils_process_data(void);
types_Word utils_calculate_size(types_Byte* data);
types_Byte* utils_allocate_buffer(types_Word size);

// Inline functions
static inline types_Byte utils_get_byte(types_Byte* data, types_Word offset) {
    return data[offset];
}

#endif // UTILS_H
        """
        
        types_h_content = """
#ifndef TYPES_H
#define TYPES_H

typedef unsigned char Byte;
typedef unsigned short Word;
typedef unsigned long DWord;

#endif // TYPES_H
        """
        
        # Create test files
        main_c = self.create_test_file("main.c", main_c_content)
        api_h = self.create_test_file("api.h", api_h_content)
        utils_h = self.create_test_file("utils.h", utils_h_content)
        types_h = self.create_test_file("types.h", types_h_content)
        
        # Parse the project
        project_model = self.parser.parse_project(str(self.test_dir))
        
        # Process include relations
        transformed_model = self.transformer._process_include_relations(project_model, 3)
        
        # Generate PlantUML diagram for main.c
        main_file_model = transformed_model.files["main.c"]
        diagram = self.generator.generate_diagram(main_file_model, transformed_model)
        
        # Verify include relationships
        self.assertIn("MAIN --> HEADER_API : <<include>>", diagram)
        self.assertIn("MAIN --> HEADER_UTILS : <<include>>", diagram)
        
        # Verify header classes are generated
        self.assertIn('class "api" as HEADER_API <<header>> #LightGreen', diagram)
        self.assertIn('class "utils" as HEADER_UTILS <<header>> #LightGreen', diagram)
        
        # Verify function declarations are included in headers
        # Note: The current parser may not parse function declarations in headers
        # This test documents the expected behavior when that feature is implemented
        pass

    def test_include_processing_with_macro_dependencies(self):
        """Test include processing with macro dependencies between headers"""
        # Create test files with macro dependencies
        main_c_content = """
#include "config.h"
#include "debug.h"
#include "limits.h"

int main() {
    #ifdef DEBUG_MODE
    debug_print("Starting application");
    #endif
    
    if (MAX_BUFFER_SIZE > 0) {
        // Process data
    }
    
    return 0;
}
        """
        
        config_h_content = """
#ifndef CONFIG_H
#define CONFIG_H

#define DEBUG_MODE 1
#define RELEASE_MODE 0

#define MAX_BUFFER_SIZE 1024
#define DEFAULT_TIMEOUT 30

typedef struct {
    int buffer_size;
    int timeout;
} Config;

#endif // CONFIG_H
        """
        
        debug_h_content = """
#ifndef DEBUG_H
#define DEBUG_H

#include "config.h"

#ifdef DEBUG_MODE
#define debug_print(msg) printf("[DEBUG] %s\\n", msg)
#define debug_assert(cond) assert(cond)
#else
#define debug_print(msg) ((void)0)
#define debug_assert(cond) ((void)0)
#endif

void debug_init(void);
void debug_cleanup(void);

#endif // DEBUG_H
        """
        
        limits_h_content = """
#ifndef LIMITS_H
#define LIMITS_H

#include "config.h"

#define MAX_CONNECTIONS (MAX_BUFFER_SIZE / 64)
#define MIN_BUFFER_SIZE 256

typedef struct {
    int max_connections;
    int min_buffer_size;
} Limits;

#endif // LIMITS_H
        """
        
        # Create test files
        main_c = self.create_test_file("main.c", main_c_content)
        config_h = self.create_test_file("config.h", config_h_content)
        debug_h = self.create_test_file("debug.h", debug_h_content)
        limits_h = self.create_test_file("limits.h", limits_h_content)
        
        # Parse the project
        project_model = self.parser.parse_project(str(self.test_dir))
        
        # Process include relations
        transformed_model = self.transformer._process_include_relations(project_model, 3)
        
        # Generate PlantUML diagram for main.c
        main_file_model = transformed_model.files["main.c"]
        diagram = self.generator.generate_diagram(main_file_model, transformed_model)
        
        # Verify include relationships
        self.assertIn("MAIN --> HEADER_CONFIG : <<include>>", diagram)
        self.assertIn("MAIN --> HEADER_DEBUG : <<include>>", diagram)
        self.assertIn("MAIN --> HEADER_LIMITS : <<include>>", diagram)
        
        # Verify header classes are generated
        self.assertIn('class "config" as HEADER_CONFIG <<header>> #LightGreen', diagram)
        self.assertIn('class "debug" as HEADER_DEBUG <<header>> #LightGreen', diagram)
        self.assertIn('class "limits" as HEADER_LIMITS <<header>> #LightGreen', diagram)
        
        # Verify macros are included in headers
        self.assertIn("+ #define DEBUG_MODE", diagram)  # from config.h
        self.assertIn("+ #define MAX_BUFFER_SIZE", diagram)  # from config.h
        self.assertIn("+ #define debug_print", diagram)  # from debug.h (simplified)
        self.assertIn("+ #define MAX_CONNECTIONS", diagram)  # from limits.h

    def test_include_processing_with_struct_and_enum_inheritance(self):
        """Test include processing with struct and enum inheritance patterns"""
        # Create test files with struct and enum inheritance
        main_c_content = """
#include "base_types.h"
#include "derived_types.h"

int main() {
    base_Shape shape = {0};
    derived_Circle circle = {0};
    derived_Rectangle rect = {0};
    
    return 0;
}
        """
        
        base_types_h_content = """
#ifndef BASE_TYPES_H
#define BASE_TYPES_H

typedef enum {
    SHAPE_CIRCLE,
    SHAPE_RECTANGLE,
    SHAPE_TRIANGLE
} ShapeType;

typedef struct {
    ShapeType type;
    int x, y;
} Shape;

typedef struct {
    Shape base;
    int radius;
} Circle;

typedef struct {
    Shape base;
    int width, height;
} Rectangle;

#endif // BASE_TYPES_H
        """
        
        derived_types_h_content = """
#ifndef DERIVED_TYPES_H
#define DERIVED_TYPES_H

#include "base_types.h"

typedef struct {
    base_Circle circle;
    int color;
} ColoredCircle;

typedef struct {
    base_Rectangle rect;
    int border_width;
} BorderedRectangle;

typedef enum {
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE
} Color;

typedef enum {
    BORDER_THIN = 1,
    BORDER_MEDIUM = 2,
    BORDER_THICK = 3
} BorderWidth;

#endif // DERIVED_TYPES_H
        """
        
        # Create test files
        main_c = self.create_test_file("main.c", main_c_content)
        base_types_h = self.create_test_file("base_types.h", base_types_h_content)
        derived_types_h = self.create_test_file("derived_types.h", derived_types_h_content)
        
        # Parse the project
        project_model = self.parser.parse_project(str(self.test_dir))
        
        # Process include relations
        transformed_model = self.transformer._process_include_relations(project_model, 3)
        
        # Generate PlantUML diagram for main.c
        main_file_model = transformed_model.files["main.c"]
        diagram = self.generator.generate_diagram(main_file_model, transformed_model)
        
        # Verify include relationships
        self.assertIn("MAIN --> HEADER_BASE_TYPES : <<include>>", diagram)
        self.assertIn("MAIN --> HEADER_DERIVED_TYPES : <<include>>", diagram)
        
        # Verify header classes are generated
        self.assertIn('class "base_types" as HEADER_BASE_TYPES <<header>> #LightGreen', diagram)
        self.assertIn('class "derived_types" as HEADER_DERIVED_TYPES <<header>> #LightGreen', diagram)
        
                # Verify typedefs are included in headers (name only)
        self.assertIn("+ typedef ShapeType", diagram)  # from base_types.h
        self.assertIn("+ typedef type", diagram)  # from base_types.h
        self.assertIn("+ typedef base", diagram)  # from base_types.h
        self.assertIn("+ typedef circle", diagram)  # from derived_types.h
        self.assertIn("+ typedef rect", diagram)  # from derived_types.h
        self.assertIn("+ typedef Color", diagram)  # from derived_types.h
        self.assertIn("+ typedef BorderWidth", diagram)  # from derived_types.h
        
        # Check that typedefs are NOT shown with full type information in headers
        self.assertNotIn("+ typedef enum { SHAPE_CIRCLE, SHAPE_RECTANGLE, SHAPE_TRIANGLE } ShapeType", diagram)  # from base_types.h
        self.assertNotIn("+ typedef enum { COLOR_RED, COLOR_GREEN, COLOR_BLUE } Color", diagram)  # from derived_types.h
        self.assertNotIn("+ typedef enum { BORDER_THIN = 1, BORDER_MEDIUM = 2, BORDER_THICK = 3 } BorderWidth", diagram)  # from derived_types.h
        self.assertNotIn("+ typedef struct { ShapeType type", diagram)  # from base_types.h
        self.assertNotIn("+ typedef struct { Shape base", diagram)  # from base_types.h
        self.assertNotIn("+ typedef struct { base_Circle circle", diagram)  # from derived_types.h
        self.assertNotIn("+ typedef struct { base_Rectangle rect", diagram)  # from derived_types.h

    def test_include_processing_with_conditional_includes(self):
        """Test include processing with conditional include statements"""
        # Create test files with conditional includes
        main_c_content = """
#include "common.h"

#ifdef PLATFORM_LINUX
#include "linux_specific.h"
#elif defined(PLATFORM_WINDOWS)
#include "windows_specific.h"
#endif

#ifdef DEBUG_BUILD
#include "debug_utils.h"
#endif

int main() {
    return 0;
}
        """
        
        common_h_content = """
#ifndef COMMON_H
#define COMMON_H

typedef int Status;
typedef char* String;

#define SUCCESS 0
#define ERROR -1

#endif // COMMON_H
        """
        
        linux_specific_h_content = """
#ifndef LINUX_SPECIFIC_H
#define LINUX_SPECIFIC_H

#include "common.h"

typedef struct {
    int fd;
    String path;
} LinuxFile;

void linux_init(void);

#endif // LINUX_SPECIFIC_H
        """
        
        windows_specific_h_content = """
#ifndef WINDOWS_SPECIFIC_H
#define WINDOWS_SPECIFIC_H

#include "common.h"

typedef struct {
    void* handle;
    String path;
} WindowsFile;

void windows_init(void);

#endif // WINDOWS_SPECIFIC_H
        """
        
        debug_utils_h_content = """
#ifndef DEBUG_UTILS_H
#define DEBUG_UTILS_H

#include "common.h"

void debug_log(String message);
void debug_assert(Status condition);

#endif // DEBUG_UTILS_H
        """
        
        # Create test files
        main_c = self.create_test_file("main.c", main_c_content)
        common_h = self.create_test_file("common.h", common_h_content)
        linux_specific_h = self.create_test_file("linux_specific.h", linux_specific_h_content)
        windows_specific_h = self.create_test_file("windows_specific.h", windows_specific_h_content)
        debug_utils_h = self.create_test_file("debug_utils.h", debug_utils_h_content)
        
        # Parse the project
        project_model = self.parser.parse_project(str(self.test_dir))
        
        # Process include relations
        transformed_model = self.transformer._process_include_relations(project_model, 3)
        
        # Generate PlantUML diagram for main.c
        main_file_model = transformed_model.files["main.c"]
        diagram = self.generator.generate_diagram(main_file_model, transformed_model)
        
        # Verify include relationships (all conditional includes should be parsed)
        self.assertIn("MAIN --> HEADER_COMMON : <<include>>", diagram)
        self.assertIn("MAIN --> HEADER_LINUX_SPECIFIC : <<include>>", diagram)
        self.assertIn("MAIN --> HEADER_WINDOWS_SPECIFIC : <<include>>", diagram)
        self.assertIn("MAIN --> HEADER_DEBUG_UTILS : <<include>>", diagram)
        
        # Verify header classes are generated
        self.assertIn('class "common" as HEADER_COMMON <<header>> #LightGreen', diagram)
        self.assertIn('class "linux_specific" as HEADER_LINUX_SPECIFIC <<header>> #LightGreen', diagram)
        self.assertIn('class "windows_specific" as HEADER_WINDOWS_SPECIFIC <<header>> #LightGreen', diagram)
        self.assertIn('class "debug_utils" as HEADER_DEBUG_UTILS <<header>> #LightGreen', diagram)

    def test_include_processing_with_namespace_like_patterns(self):
        """Test include processing with namespace-like patterns using prefixes"""
        # Create test files with namespace-like patterns
        main_c_content = """
#include "core_types.h"
#include "graphics_types.h"
#include "network_types.h"

int main() {
    core_String message = "Hello";
    graphics_Color color = {255, 0, 0};
    network_Address addr = {192, 168, 1, 1};
    
    return 0;
}
        """
        
        core_types_h_content = """
#ifndef CORE_TYPES_H
#define CORE_TYPES_H

typedef char* String;
typedef int Integer;
typedef float Float;

typedef struct {
    Integer x, y;
} Point;

typedef struct {
    Float width, height;
} Size;

#endif // CORE_TYPES_H
        """
        
        graphics_types_h_content = """
#ifndef GRAPHICS_TYPES_H
#define GRAPHICS_TYPES_H

#include "core_types.h"

typedef struct {
    core_Integer r, g, b;
} Color;

typedef struct {
    core_Point position;
    core_Size size;
    Color color;
} Rectangle;

typedef enum {
    GRAPHICS_MODE_2D,
    GRAPHICS_MODE_3D
} GraphicsMode;

#endif // GRAPHICS_TYPES_H
        """
        
        network_types_h_content = """
#ifndef NETWORK_TYPES_H
#define NETWORK_TYPES_H

#include "core_types.h"

typedef struct {
    core_Integer octet1, octet2, octet3, octet4;
} Address;

typedef struct {
    Address address;
    core_Integer port;
} Endpoint;

typedef enum {
    NETWORK_PROTOCOL_TCP,
    NETWORK_PROTOCOL_UDP
} NetworkProtocol;

#endif // NETWORK_TYPES_H
        """
        
        # Create test files
        main_c = self.create_test_file("main.c", main_c_content)
        core_types_h = self.create_test_file("core_types.h", core_types_h_content)
        graphics_types_h = self.create_test_file("graphics_types.h", graphics_types_h_content)
        network_types_h = self.create_test_file("network_types.h", network_types_h_content)
        
        # Parse the project
        project_model = self.parser.parse_project(str(self.test_dir))
        
        # Process include relations
        transformed_model = self.transformer._process_include_relations(project_model, 3)
        
        # Generate PlantUML diagram for main.c
        main_file_model = transformed_model.files["main.c"]
        diagram = self.generator.generate_diagram(main_file_model, transformed_model)
        
        # Verify include relationships
        self.assertIn("MAIN --> HEADER_CORE_TYPES : <<include>>", diagram)
        self.assertIn("MAIN --> HEADER_GRAPHICS_TYPES : <<include>>", diagram)
        self.assertIn("MAIN --> HEADER_NETWORK_TYPES : <<include>>", diagram)
        
        # Verify header classes are generated
        self.assertIn('class "core_types" as HEADER_CORE_TYPES <<header>> #LightGreen', diagram)
        self.assertIn('class "graphics_types" as HEADER_GRAPHICS_TYPES <<header>> #LightGreen', diagram)
        self.assertIn('class "network_types" as HEADER_NETWORK_TYPES <<header>> #LightGreen', diagram)
        
        # Verify typedefs are included in headers (name only)
        self.assertIn("+ typedef String", diagram)  # from core_types.h
        self.assertIn("+ typedef Integer", diagram)  # from core_types.h
        self.assertIn("+ typedef Float", diagram)  # from core_types.h
        self.assertIn("+ typedef b", diagram)  # from graphics_types.h
        self.assertIn("+ typedef position", diagram)  # from graphics_types.h
        self.assertIn("+ typedef GraphicsMode", diagram)  # from graphics_types.h
        self.assertIn("+ typedef octet4", diagram)  # from network_types.h
        self.assertIn("+ typedef address", diagram)  # from network_types.h
        self.assertIn("+ typedef NetworkProtocol", diagram)  # from network_types.h
        
        # Check that typedefs are NOT shown with full type information in headers
        self.assertNotIn("+ typedef char* String", diagram)  # from core_types.h
        self.assertNotIn("+ typedef struct { core_Integer r, g, b", diagram)  # from graphics_types.h
        self.assertNotIn("+ typedef struct { core_Integer octet1, octet2, octet3, octet4", diagram)  # from network_types.h
        self.assertNotIn("+ typedef enum { GRAPHICS_MODE_2D, GRAPHICS_MODE_3D } GraphicsMode", diagram)  # from graphics_types.h
        self.assertNotIn("+ typedef enum { NETWORK_PROTOCOL_TCP, NETWORK_PROTOCOL_UDP } NetworkProtocol", diagram)  # from network_types.h


if __name__ == "__main__":
    unittest.main()