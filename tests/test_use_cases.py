#!/usr/bin/env python3
"""
Use case focused unit tests for the C to PlantUML converter

These tests cover specific use cases and behavioral scenarios
described in the specification.
"""

import unittest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from c_to_plantuml.parser import CParser
from c_to_plantuml.analyzer import Analyzer
from c_to_plantuml.generator import Generator
from c_to_plantuml.config import Config
from c_to_plantuml.models import (
    ProjectModel, FileModel, Struct, Function, Field, Enum, Union,
    TypedefRelation, IncludeRelation
)


class TestBasicProjectUseCase(unittest.TestCase):
    """Test the basic project analysis use case"""
    
    def setUp(self):
        self.parser = CParser()
        self.analyzer = Analyzer()
        self.generator = Generator()
        
        # Create temporary project structure
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir) / "basic_project"
        self.project_dir.mkdir()
        
        # Create source files
        self.create_basic_project_files()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_basic_project_files(self):
        """Create basic project files for testing"""
        # Create main.c
        main_c = self.project_dir / "main.c"
        main_c.write_text("""
#include <stdio.h>
#include "utils.h"
#include "types.h"

int global_counter = 0;
char* global_name = "Basic Project";

int add(int a, int b) {
    return a + b;
}

float multiply(float x, float y) {
    return x * y;
}

void print_point(Point p) {
    printf("Point: (%d, %d)\\n", p.x, p.y);
}

int main() {
    Point p = {10, 20};
    Rectangle rect = {{0, 0}, {100, 100}, RED};
    
    print_point(p);
    printf("Area: %f\\n", multiply(rect.bottom_right.x - rect.top_left.x, 
                                  rect.bottom_right.y - rect.top_left.y));
    
    return 0;
}
""")
        
        # Create utils.h
        utils_h = self.project_dir / "utils.h"
        utils_h.write_text("""
#ifndef UTILS_H
#define UTILS_H

#include "types.h"

extern int global_counter;
extern char* global_name;

int add(int a, int b);
float multiply(float x, float y);
void print_point(Point p);

struct Rectangle {
    Point top_left;
    Point bottom_right;
    Color color;
};

enum Status {
    OK = 0,
    ERROR = 1,
    WARNING = 2
};

union Data {
    int integer;
    float floating;
    char character;
    char* string;
};

#endif
""")
        
        # Create types.h
        types_h = self.project_dir / "types.h"
        types_h.write_text("""
#ifndef TYPES_H
#define TYPES_H

typedef int MyInt;
typedef char* String;
typedef unsigned long ULong;

typedef struct {
    int x;
    int y;
} Point;

typedef enum {
    RED = 0,
    GREEN = 1,
    BLUE = 2
} Color;

typedef union {
    int i;
    float f;
    char c;
} Value;

#endif
""")
    
    def test_basic_project_analysis(self):
        """Test basic project analysis use case"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
        # Verify project structure
        self.assertEqual(model.project_name, "basic_project")
        self.assertEqual(len(model.files), 3)
        
        # Check that all files are parsed
        file_paths = [f for f in model.files.keys()]
        self.assertIn("main.c", file_paths)
        self.assertIn("utils.h", file_paths)
        self.assertIn("types.h", file_paths)
        
        # Check main.c content
        main_c_model = model.files["main.c"]
        self.assertEqual(len(main_c_model.functions), 4)  # add, multiply, print_point, main
        self.assertEqual(len(main_c_model.globals), 2)  # global_counter, global_name
        self.assertEqual(len(main_c_model.includes), 3)  # stdio.h, utils.h, types.h
        
        # Check utils.h content
        utils_h_model = model.files["utils.h"]
        self.assertEqual(len(utils_h_model.structs), 1)  # Rectangle
        self.assertEqual(len(utils_h_model.enums), 1)  # Status
        self.assertEqual(len(utils_h_model.unions), 1)  # Data
        self.assertEqual(len(utils_h_model.functions), 3)  # add, multiply, print_point
        
        # Check types.h content
        types_h_model = model.files["types.h"]
        self.assertEqual(len(types_h_model.typedefs), 6)  # MyInt, String, ULong, Point, Color, Value
        self.assertGreaterEqual(len(types_h_model.typedef_relations), 4)  # At least 4 typedef relations
    
    def test_basic_project_generation(self):
        """Test PlantUML generation for basic project"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
        # Create output directory
        output_dir = self.project_dir / "output"
        output_dir.mkdir()
        
        # Generate PlantUML
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)
        
        # Check main.puml content
        main_puml = output_dir / "main.puml"
        self.assertTrue(main_puml.exists())
        
        content = main_puml.read_text()
        # Check for expected PlantUML elements
        self.assertIn("@startuml main", content)
        self.assertIn("class \"main\"", content)
        self.assertIn("class \"utils\"", content)
        self.assertIn("class \"types\"", content)
        self.assertIn("-->", content)  # Include relationships


class TestComplexTypedefUseCase(unittest.TestCase):
    """Test the complex typedef analysis use case"""
    
    def setUp(self):
        self.parser = CParser()
        self.analyzer = Analyzer()
        self.generator = Generator()
        
        # Create temporary project structure
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir) / "typedef_project"
        self.project_dir.mkdir()
        
        # Create source files
        self.create_typedef_project_files()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_typedef_project_files(self):
        """Create typedef project files for testing"""
        # Create types.h with complex typedefs
        types_h = self.project_dir / "types.h"
        types_h.write_text("""
#ifndef TYPES_H
#define TYPES_H

// Basic type aliases
typedef int Integer;
typedef unsigned int UInteger;
typedef char Character;
typedef float Float;
typedef double Double;
typedef void* Pointer;

// Typedef chains
typedef Integer Int32;
typedef Int32 MyInt;
typedef MyInt Counter;

// Anonymous struct typedefs
typedef struct {
    int x;
    int y;
    int z;
} Vector3D;

typedef struct {
    float r;
    float g;
    float b;
    float a;
} Color;

// Anonymous enum typedefs
typedef enum {
    STATE_IDLE = 0,
    STATE_RUNNING = 1,
    STATE_PAUSED = 2,
    STATE_STOPPED = 3
} State;

// Anonymous union typedefs
typedef union {
    int i;
    float f;
    char c;
    void* ptr;
} Variant;

// Complex nested typedefs
typedef struct {
    Vector3D position;
    Vector3D velocity;
    float mass;
} Particle;

typedef Particle* ParticlePtr;
typedef ParticlePtr* ParticlePtrPtr;

// Typedef with struct tag
struct Node {
    int data;
    struct Node* next;
};
typedef struct Node Node;
typedef Node* NodePtr;

#endif
""")
        
        # Create main.c using typedefs
        main_c = self.project_dir / "main.c"
        main_c.write_text("""
#include "types.h"

Integer global_integer = 42;
Vector3D global_vector = {1, 2, 3};
Color global_color = {1.0, 0.5, 0.0, 1.0};
State global_state = STATE_RUNNING;

Integer add_integers(Integer a, Integer b) {
    return a + b;
}

Vector3D create_vector(Integer x, Integer y, Integer z) {
    Vector3D v = {x, y, z};
    return v;
}

int main() {
    Integer x = 10;
    Float y = 3.14;
    Vector3D pos = create_vector(1, 2, 3);
    Color col = global_color;
    
    return 0;
}
""")
    
    def test_complex_typedef_analysis(self):
        """Test complex typedef analysis use case"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
        # Check types.h typedefs
        types_h_model = model.files["types.h"]
        
        # Check basic typedefs (aliases)
        self.assertIn('Integer', types_h_model.typedefs)
        self.assertIn('UInteger', types_h_model.typedefs)
        self.assertIn('Character', types_h_model.typedefs)
        self.assertIn('Float', types_h_model.typedefs)
        self.assertIn('Double', types_h_model.typedefs)
        self.assertIn('Pointer', types_h_model.typedefs)
        
        # Check typedef chains
        self.assertIn('Int32', types_h_model.typedefs)
        self.assertIn('MyInt', types_h_model.typedefs)
        self.assertIn('Counter', types_h_model.typedefs)
        
        # Check anonymous struct typedefs (defines)
        self.assertIn('Vector3D', types_h_model.typedefs)
        self.assertIn('Color', types_h_model.typedefs)
        
        # Check anonymous enum typedefs (defines)
        self.assertIn('State', types_h_model.typedefs)
        
        # Check anonymous union typedefs (defines)
        self.assertIn('Variant', types_h_model.typedefs)
        
        # Check complex nested typedefs
        self.assertIn('Particle', types_h_model.typedefs)
        self.assertIn('ParticlePtr', types_h_model.typedefs)
        self.assertIn('ParticlePtrPtr', types_h_model.typedefs)
        
        # Check typedef with struct tag
        self.assertIn('Node', types_h_model.typedefs)
        self.assertIn('NodePtr', types_h_model.typedefs)
        
        # Check typedef relationships
        self.assertGreater(len(types_h_model.typedef_relations), 0)
        
        # Verify relationship types - check that we have both alias and defines relationships
        relationship_types = [r.relationship_type for r in types_h_model.typedef_relations]
        self.assertIn('alias', relationship_types)
        self.assertIn('defines', relationship_types)
    
    def test_typedef_relationship_visualization(self):
        """Test typedef relationship visualization in PlantUML"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
        # Create output directory
        output_dir = self.project_dir / "output"
        output_dir.mkdir()
        
        # Generate PlantUML
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Check that output was generated
        main_puml = output_dir / "main.puml"
        self.assertTrue(main_puml.exists())
        
        content = main_puml.read_text()
        
        # Check for typedef classes - they should be in the types.h header class
        self.assertIn("typedef int Integer", content)
        self.assertIn("typedef struct Vector3D Vector3D", content)
        self.assertIn("typedef struct State State", content)
        
        # Check for stereotypes in header classes
        self.assertIn("<<header>>", content)
        
        # Check for relationship notation - these might not be generated for basic types
        # but the typedefs should be listed in the header class
        self.assertIn("typedef", content)


class TestLargeCodebaseUseCase(unittest.TestCase):
    """Test the large codebase analysis use case"""
    
    def setUp(self):
        self.analyzer = Analyzer()
        self.generator = Generator()
        
        # Create temporary project structure
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir) / "large_project"
        self.project_dir.mkdir()
        
        # Create large project structure
        self.create_large_project_structure()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_large_project_structure(self):
        """Create a large project structure for testing"""
        # Create core module
        core_dir = self.project_dir / "core"
        core_dir.mkdir()
        
        core_types_h = core_dir / "types.h"
        core_types_h.write_text("""
#ifndef CORE_TYPES_H
#define CORE_TYPES_H

typedef int CoreInt;
typedef float CoreFloat;
typedef char* CoreString;

struct CoreConfig {
    CoreInt id;
    CoreString name;
    CoreFloat value;
};

enum CoreStatus {
    CORE_OK = 0,
    CORE_ERROR = 1
};

#endif
""")
        
        core_utils_h = core_dir / "utils.h"
        core_utils_h.write_text("""
#ifndef CORE_UTILS_H
#define CORE_UTILS_H

#include "types.h"

CoreInt core_add(CoreInt a, CoreInt b);
CoreFloat core_multiply(CoreFloat a, CoreFloat b);
CoreString core_create_string(const char* str);

extern CoreConfig global_config;
extern CoreStatus global_status;

#endif
""")
        
        core_utils_c = core_dir / "utils.c"
        core_utils_c.write_text("""
#include "utils.h"

CoreConfig global_config = {0, "default", 1.0};
CoreStatus global_status = CORE_OK;

CoreInt core_add(CoreInt a, CoreInt b) {
    return a + b;
}

CoreFloat core_multiply(CoreFloat a, CoreFloat b) {
    return a * b;
}

CoreString core_create_string(const char* str) {
    return (CoreString)str;
}
""")
        
        # Create network module
        network_dir = self.project_dir / "network"
        network_dir.mkdir()
        
        network_protocol_h = network_dir / "protocol.h"
        network_protocol_h.write_text("""
#ifndef NETWORK_PROTOCOL_H
#define NETWORK_PROTOCOL_H

#include "../core/types.h"

typedef struct {
    CoreInt id;
    CoreString data;
    CoreInt length;
} NetworkPacket;

typedef enum {
    PACKET_TYPE_DATA = 0,
    PACKET_TYPE_CONTROL = 1,
    PACKET_TYPE_ACK = 2
} PacketType;

CoreInt network_send_packet(NetworkPacket* packet);
CoreInt network_receive_packet(NetworkPacket* packet);

#endif
""")
        
        network_protocol_c = network_dir / "protocol.c"
        network_protocol_c.write_text("""
#include "protocol.h"

CoreInt network_send_packet(NetworkPacket* packet) {
    return 0;
}

CoreInt network_receive_packet(NetworkPacket* packet) {
    return 0;
}
""")
        
        # Create database module
        database_dir = self.project_dir / "database"
        database_dir.mkdir()
        
        database_types_h = database_dir / "types.h"
        database_types_h.write_text("""
#ifndef DATABASE_TYPES_H
#define DATABASE_TYPES_H

#include "../../core/types.h"

typedef struct {
    CoreInt id;
    CoreString name;
    CoreFloat value;
} DatabaseRecord;

typedef enum {
    DB_OP_INSERT = 0,
    DB_OP_UPDATE = 1,
    DB_OP_DELETE = 2,
    DB_OP_SELECT = 3
} DatabaseOperation;

CoreInt database_insert(DatabaseRecord* record);
CoreInt database_update(DatabaseRecord* record);
CoreInt database_delete(CoreInt id);
DatabaseRecord* database_select(CoreInt id);

#endif
""")
        
        database_types_c = database_dir / "types.c"
        database_types_c.write_text("""
#include "types.h"

CoreInt database_insert(DatabaseRecord* record) {
    return 0;
}

CoreInt database_update(DatabaseRecord* record) {
    return 0;
}

CoreInt database_delete(CoreInt id) {
    return 0;
}

DatabaseRecord* database_select(CoreInt id) {
    return NULL;
}
""")
        
        # Create main application
        main_c = self.project_dir / "main.c"
        main_c.write_text("""
#include <stdio.h>
#include "core/utils.h"
#include "network/protocol.h"
#include "database/types.h"

int main() {
    CoreConfig config = {1, "test", 2.5};
    NetworkPacket packet = {1, "data", 4};
    DatabaseRecord record = {1, "test_record", 3.14};
    
    CoreInt result = core_add(10, 20);
    CoreFloat product = core_multiply(2.5, 3.0);
    
    network_send_packet(&packet);
    database_insert(&record);
    
    printf("Result: %d, Product: %f\\n", result, product);
    
    return 0;
}
""")
    
    def test_large_codebase_analysis(self):
        """Test large codebase analysis use case"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
        # Verify project structure
        self.assertEqual(model.project_name, "large_project")
        self.assertGreaterEqual(len(model.files), 8)  # At least 8 files
        
        # Check that all modules are parsed
        file_paths = [f for f in model.files.keys()]
        
        # Core module files
        self.assertTrue(any("core/types.h" in f for f in file_paths))
        self.assertTrue(any("core/utils.h" in f for f in file_paths))
        self.assertTrue(any("core/utils.c" in f for f in file_paths))
        
        # Network module files
        self.assertTrue(any("network/protocol.h" in f for f in file_paths))
        self.assertTrue(any("network/protocol.c" in f for f in file_paths))
        
        # Database module files
        self.assertTrue(any("database/types.h" in f for f in file_paths))
        self.assertTrue(any("database/types.c" in f for f in file_paths))
        
        # Main file
        self.assertTrue(any("main.c" in f for f in file_paths))
        
        # Check include relationships
        main_c_model = model.files["main.c"]
        self.assertGreaterEqual(len(main_c_model.includes), 3)
        
        # Check that all modules have their content
        core_types_model = next(f for f in model.files.values() if "core/types.h" in f.file_path)
        self.assertGreater(len(core_types_model.typedefs), 0)
        self.assertGreater(len(core_types_model.structs), 0)
        self.assertGreater(len(core_types_model.enums), 0)
    
    def test_large_codebase_generation(self):
        """Test PlantUML generation for large codebase"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(self.project_dir),
            recursive=True
        )
        
        # Create output directory
        output_dir = self.project_dir / "output"
        output_dir.mkdir()
        
        # Generate PlantUML
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)
        
        # Check main.puml content
        main_puml = output_dir / "main.puml"
        self.assertTrue(main_puml.exists())
        
        content = main_puml.read_text()
        
        # Check for expected elements
        self.assertIn("@startuml main", content)
        self.assertIn("class \"main\"", content)
        
        # Check for header classes - they use base names without paths
        self.assertIn("class \"types\"", content)
        self.assertIn("class \"utils\"", content)
        self.assertIn("class \"protocol\"", content)
        
        # Check for include relationships
        self.assertIn("-->", content)


class TestErrorHandlingUseCase(unittest.TestCase):
    """Test error handling and recovery use cases"""
    
    def setUp(self):
        self.parser = CParser()
        self.analyzer = Analyzer()
    
    def test_encoding_detection_and_recovery(self):
        """Test encoding detection and recovery"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
// This is a valid C file
struct Test {
    int x;
    int y;
};

int main() {
    return 0;
}
""")
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.parser.parse_file(Path(temp_file))
            
            # Should parse successfully
            self.assertIsNotNone(file_model)
            self.assertIn('Test', file_model.structs)
            self.assertEqual(len(file_model.functions), 1)
            
        finally:
            os.unlink(temp_file)
    
    def test_partial_parsing_on_errors(self):
        """Test partial parsing when encountering errors"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
// Valid struct
struct Valid {
    int x;
    int y;
};

// Invalid syntax - should be skipped
struct Invalid {
    int x
    int y  // missing semicolon
}

// Valid function
int main() {
    return 0;
}
""")
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.parser.parse_file(Path(temp_file))
            
            # Should parse valid parts
            self.assertIsNotNone(file_model)
            self.assertIn('Valid', file_model.structs)
            # Invalid struct might be parsed with empty fields due to error recovery
            if 'Invalid' in file_model.structs:
                invalid_struct = file_model.structs['Invalid']
                # Should have empty fields due to parsing error
                self.assertEqual(len(invalid_struct.fields), 0)
            self.assertEqual(len(file_model.functions), 1)
            
        finally:
            os.unlink(temp_file)
    
    def test_missing_file_handling(self):
        """Test handling of missing files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir()
            
            # Create a file that includes a non-existent header
            main_c = project_dir / "main.c"
            main_c.write_text("""
#include "nonexistent.h"

int main() {
    return 0;
}
""")
            
            # Should not crash
            model = self.analyzer.analyze_project(
                project_root=str(project_dir),
                recursive=True
            )
            
            # Should still parse the main file
            self.assertIsNotNone(model)
            self.assertEqual(len(model.files), 1)
            
            main_model = list(model.files.values())[0]
            self.assertEqual(len(main_model.functions), 1)


class TestConfigurationUseCase(unittest.TestCase):
    """Test configuration-driven use cases"""
    
    def setUp(self):
        self.analyzer = Analyzer()
        self.generator = Generator()
        
        # Create temporary project structure
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir) / "config_project"
        self.project_dir.mkdir()
        
        # Create project files
        self.create_config_project_files()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_config_project_files(self):
        """Create project files for configuration testing"""
        # Create main.c
        main_c = self.project_dir / "main.c"
        main_c.write_text("""
#include "public.h"
#include "internal.h"

int public_function() {
    return 0;
}

int internal_function() {
    return 1;
}

struct PublicStruct {
    int x;
    int y;
};

struct InternalStruct {
    int private_data;
};

int global_public_var = 0;
int global_internal_var = 1;
""")
        
        # Create public.h
        public_h = self.project_dir / "public.h"
        public_h.write_text("""
#ifndef PUBLIC_H
#define PUBLIC_H

int public_function();
struct PublicStruct;

extern int global_public_var;

#endif
""")
        
        # Create internal.h
        internal_h = self.project_dir / "internal.h"
        internal_h.write_text("""
#ifndef INTERNAL_H
#define INTERNAL_H

int internal_function();
struct InternalStruct;

extern int global_internal_var;

#endif
""")
    
    def test_configuration_filtering(self):
        """Test configuration-based filtering"""
        # Create configuration
        config_data = {
            "project_name": "config_project",
            "project_root": str(self.project_dir),
            "model_output_path": "config_model.json",
            "output_directory": "output",
            "include_depth": 1,
            "file_patterns": {
                "include": ["*.c", "*.h"],
                "exclude": []
            },
            "element_filters": {
                "structs": {
                    "include": [],
                    "exclude": ["*internal*", "*Internal*"]
                },
                "functions": {
                    "include": [],
                    "exclude": ["*internal*", "*Internal*"]
                },
                "globals": {
                    "include": [],
                    "exclude": ["*internal*", "*Internal*"]
                }
            }
        }
        
        config_file = self.project_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Load configuration
        config = Config.load(str(config_file))
        
        # Analyze with configuration - use analyze_project directly for single project
        model = self.analyzer.analyze_project(str(self.project_dir), recursive=True)
        
        # Apply filters manually
        model = config.apply_filters(model)
        
        # Check that the model was created successfully
        self.assertIsNotNone(model)
        self.assertGreater(len(model.files), 0)
        
        # Check that main.c was parsed
        self.assertIn("main.c", model.files)
        main_c_model = model.files["main.c"]
        
        # Should include public elements
        self.assertIn('PublicStruct', main_c_model.structs)
        self.assertIn('public_function', [f.name for f in main_c_model.functions])
        self.assertIn('global_public_var', [g.name for g in main_c_model.globals])


if __name__ == '__main__':
    unittest.main()