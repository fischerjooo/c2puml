#!/usr/bin/env python3
"""
Comprehensive integration tests for the new PlantUML formatting rules.
Tests the complete workflow with all new formatting features.
"""

import tempfile
import unittest
from pathlib import Path

from c2puml.core.generator import Generator
from c2puml.models import (
    Alias,
    Enum,
    EnumValue,
    Field,
    FileModel,
    Function,
    ProjectModel,
    Struct,
    Union,
)


class TestNewFormattingIntegration(unittest.TestCase):
    """Integration tests for all new formatting rules working together"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = Generator()
        self.temp_dir = tempfile.mkdtemp()

    def test_complete_formatting_integration(self):
        """Test all new formatting rules working together in a realistic scenario"""
        
        # Create a comprehensive source file with all types of elements
        source_file = self._create_comprehensive_source_file()
        
        # Create a header file that exposes some of the source elements
        header_file = self._create_corresponding_header_file()
        
        # Create project model
        project_model = ProjectModel(
            project_name="comprehensive_test",
            source_folder="/test",
            files={"graphics.c": source_file, "graphics.h": header_file},
        )

        # Generate diagram
        diagram = self.generator.generate_diagram(source_file, project_model)

        # Validate all new formatting rules
        self._validate_enum_formatting(diagram)
        self._validate_struct_formatting(diagram)
        self._validate_union_formatting(diagram)
        self._validate_alias_formatting(diagram)
        self._validate_visibility_logic(diagram)
        self._validate_no_old_stereotypes(diagram)

    def _create_comprehensive_source_file(self) -> FileModel:
        """Create a comprehensive source file with all types of elements"""
        
        # Enums
        color_enum = Enum(
            name="Color",
            values=[
                EnumValue(name="RED", value="0xFF0000"),
                EnumValue(name="GREEN", value="0x00FF00"),
                EnumValue(name="BLUE", value="0x0000FF"),
                EnumValue(name="ALPHA"),  # No value
            ],
        )
        
        status_enum = Enum(
            name="RenderStatus",
            values=[
                EnumValue(name="RENDER_OK"),
                EnumValue(name="RENDER_ERROR"),
                EnumValue(name="RENDER_PENDING"),
            ],
        )

        # Structs
        point_struct = Struct(
            name="Point",
            fields=[
                Field(name="x", type="float"),
                Field(name="y", type="float"),
                Field(name="z", type="float"),
            ],
        )
        
        rect_struct = Struct(
            name="Rectangle",
            fields=[
                Field(name="top_left", type="Point"),
                Field(name="width", type="int"),
                Field(name="height", type="int"),
                Field(name="color", type="Color"),
            ],
        )

        # Unions
        pixel_union = Union(
            name="Pixel",
            fields=[
                Field(name="rgba", type="uint32_t"),
                Field(name="components", type="struct { uint8_t r, g, b, a; }"),
            ],
        )

        # Aliases
        coord_alias = Alias(name="Coordinate", original_type="float")
        callback_alias = Alias(name="RenderCallback", original_type="void (*)(Rectangle*)")
        buffer_alias = Alias(name="PixelBuffer", original_type="Pixel*")

        # Functions - mix of public and private
        public_function = Function(name="render_rectangle", return_type="RenderStatus", is_declaration=False)
        private_function = Function(name="calculate_pixel_offset", return_type="int", is_declaration=False)
        another_public = Function(name="set_pixel_color", return_type="void", is_declaration=False)
        internal_helper = Function(name="optimize_render_buffer", return_type="void", is_declaration=False)

        # Globals - mix of public and private
        public_global = Field(name="default_background", type="Color")
        private_global = Field(name="render_cache_size", type="static int")
        another_public_global = Field(name="max_texture_size", type="int")
        internal_state = Field(name="last_render_time", type="static uint64_t")

        # Macros
        macros = [
            "#define MAX_RENDER_WIDTH 1920",
            "#define MAX_RENDER_HEIGHT 1080",
            "#define DEBUG_RENDER",
        ]

        return FileModel(
            file_path="graphics.c",
            name="graphics.c",
            structs={
                "Point": point_struct,
                "Rectangle": rect_struct,
            },
            enums={
                "Color": color_enum,
                "RenderStatus": status_enum,
            },
            unions={
                "Pixel": pixel_union,
            },
            aliases={
                "Coordinate": coord_alias,
                "RenderCallback": callback_alias,
                "PixelBuffer": buffer_alias,
            },
            functions=[
                public_function,
                private_function,
                another_public,
                internal_helper,
            ],
            globals=[
                public_global,
                private_global,
                another_public_global,
                internal_state,
            ],
            macros=macros,
        )

    def _create_corresponding_header_file(self) -> FileModel:
        """Create a header file that declares some of the source elements as public"""
        
        # Public function declarations
        public_func_decl = Function(name="render_rectangle", return_type="RenderStatus", is_declaration=True)
        another_public_decl = Function(name="set_pixel_color", return_type="void", is_declaration=True)

        # Public global declarations
        public_global_decl = Field(name="default_background", type="extern Color")
        another_public_global_decl = Field(name="max_texture_size", type="extern int")

        return FileModel(
            file_path="graphics.h",
            name="graphics.h",
            functions=[public_func_decl, another_public_decl],
            globals=[public_global_decl, another_public_global_decl],
        )

    def _validate_enum_formatting(self, diagram: str):
        """Validate that enums use the new <<enumeration>> stereotype"""
        self.assertIn('<<enumeration>>', diagram)
        self.assertIn('class "Color" as TYPEDEF_COLOR <<enumeration>> #LightYellow', diagram)
        self.assertIn('class "RenderStatus" as TYPEDEF_RENDERSTATUS <<enumeration>> #LightYellow', diagram)
        
        # Enum values should not have + prefix
        self.assertIn('RED = 0xFF0000', diagram)
        self.assertIn('ALPHA', diagram)  # Value without assignment
        self.assertIn('RENDER_OK', diagram)

    def _validate_struct_formatting(self, diagram: str):
        """Validate that structs use the new <<struct>> stereotype with + prefix for fields"""
        self.assertIn('<<struct>>', diagram)
        self.assertIn('class "Point" as TYPEDEF_POINT <<struct>> #LightYellow', diagram)
        self.assertIn('class "Rectangle" as TYPEDEF_RECTANGLE <<struct>> #LightYellow', diagram)
        
        # Struct fields should have + prefix
        self.assertIn('+ float x', diagram)
        self.assertIn('+ float y', diagram)
        self.assertIn('+ int width', diagram)
        self.assertIn('+ Color color', diagram)

    def _validate_union_formatting(self, diagram: str):
        """Validate that unions use the new <<union>> stereotype with + prefix for fields"""
        self.assertIn('<<union>>', diagram)
        self.assertIn('class "Pixel" as TYPEDEF_PIXEL <<union>> #LightYellow', diagram)
        
        # Union fields should have + prefix
        self.assertIn('+ uint32_t rgba', diagram)

    def _validate_alias_formatting(self, diagram: str):
        """Validate that aliases use <<typedef>> stereotype with 'alias of' prefix"""
        self.assertIn('class "Coordinate" as TYPEDEF_COORDINATE <<typedef>> #LightYellow', diagram)
        self.assertIn('class "RenderCallback" as TYPEDEF_RENDERCALLBACK <<typedef>> #LightYellow', diagram)
        self.assertIn('class "PixelBuffer" as TYPEDEF_PIXELBUFFER <<typedef>> #LightYellow', diagram)
        
        # Alias content should show 'alias of'
        self.assertIn('alias of float', diagram)
        self.assertIn('alias of void (*)(Rectangle*)', diagram)
        self.assertIn('alias of Pixel*', diagram)

    def _validate_visibility_logic(self, diagram: str):
        """Validate that public/private visibility is correctly applied"""
        # Public functions (declared in header) should have + prefix
        self.assertIn('+ RenderStatus render_rectangle', diagram)
        self.assertIn('+ void set_pixel_color', diagram)
        
        # Private functions (not in header) should have - prefix
        self.assertIn('- int calculate_pixel_offset', diagram)
        self.assertIn('- void optimize_render_buffer', diagram)
        
        # Public globals (declared in header) should have + prefix
        self.assertIn('+ Color default_background', diagram)
        self.assertIn('+ int max_texture_size', diagram)
        
        # Private globals (not in header) should have - prefix
        self.assertIn('- static int render_cache_size', diagram)
        self.assertIn('- static uint64_t last_render_time', diagram)

    def _validate_no_old_stereotypes(self, diagram: str):
        """Validate that old stereotypes are not used for enums, structs, unions"""
        # Count occurrences to ensure enum/struct/union don't use <<typedef>>
        lines = diagram.split('\n')
        
        # Find lines with enums, structs, unions and ensure they don't use <<typedef>>
        for line in lines:
            if 'TYPEDEF_COLOR' in line or 'TYPEDEF_RENDERSTATUS' in line:
                self.assertNotIn('<<typedef>>', line, f"Enum should not use <<typedef>> stereotype: {line}")
            elif 'TYPEDEF_POINT' in line or 'TYPEDEF_RECTANGLE' in line:
                self.assertNotIn('<<typedef>>', line, f"Struct should not use <<typedef>> stereotype: {line}")
            elif 'TYPEDEF_PIXEL' in line and not any(alias in line for alias in ['PIXELBUFFER', 'COORDINATE', 'CALLBACK']):
                # Only check TYPEDEF_PIXEL for union, not aliases like TYPEDEF_PIXELBUFFER
                self.assertNotIn('<<typedef>>', line, f"Union should not use <<typedef>> stereotype: {line}")

    def test_mixed_project_comprehensive_formatting(self):
        """Test formatting in a project with multiple files and cross-references"""
        # Create multiple interconnected files
        main_c = self._create_main_source_file()
        utils_c = self._create_utils_source_file()
        main_h = self._create_main_header_file()
        utils_h = self._create_utils_header_file()

        project_model = ProjectModel(
            project_name="multi_file_test",
            source_folder="/test",
            files={
                "main.c": main_c,
                "utils.c": utils_c,
                "main.h": main_h,
                "utils.h": utils_h,
            },
        )

        # Generate diagrams for both source files
        main_diagram = self.generator.generate_diagram(main_c, project_model)
        utils_diagram = self.generator.generate_diagram(utils_c, project_model)

        # Verify cross-file visibility works correctly
        # main.c functions that are in main.h should be public
        self.assertIn('+ int main', main_diagram)
        
        # utils.c functions that are in utils.h should be public
        self.assertIn('+ void utility_function', utils_diagram)
        
        # Functions not declared in any header should be private
        self.assertIn('- void internal_main_helper', main_diagram)
        self.assertIn('- int internal_utils_helper', utils_diagram)

    def _create_main_source_file(self) -> FileModel:
        """Create main.c with mixed visibility"""
        return FileModel(
            file_path="main.c",
            name="main.c",
            functions=[
                Function(name="main", return_type="int", is_declaration=False),
                Function(name="internal_main_helper", return_type="void", is_declaration=False),
            ],
            globals=[
                Field(name="program_name", type="char*"),
                Field(name="debug_mode", type="static int"),
            ],
        )

    def _create_utils_source_file(self) -> FileModel:
        """Create utils.c with mixed visibility"""
        return FileModel(
            file_path="utils.c",
            name="utils.c",
            functions=[
                Function(name="utility_function", return_type="void", is_declaration=False),
                Function(name="internal_utils_helper", return_type="int", is_declaration=False),
            ],
            globals=[
                Field(name="utils_initialized", type="int"),
                Field(name="private_cache", type="static void*"),
            ],
        )

    def _create_main_header_file(self) -> FileModel:
        """Create main.h with public declarations"""
        return FileModel(
            file_path="main.h",
            name="main.h",
            functions=[
                Function(name="main", return_type="int", is_declaration=True),
            ],
            globals=[
                Field(name="program_name", type="extern char*"),
            ],
        )

    def _create_utils_header_file(self) -> FileModel:
        """Create utils.h with public declarations"""
        return FileModel(
            file_path="utils.h",
            name="utils.h",
            functions=[
                Function(name="utility_function", return_type="void", is_declaration=True),
            ],
            globals=[
                Field(name="utils_initialized", type="extern int"),
            ],
        )


if __name__ == "__main__":
    unittest.main()