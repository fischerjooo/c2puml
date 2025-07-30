#!/usr/bin/env python3
"""
Unit tests for generator include_relations filtering behavior
Tests that PlantUML generation only includes header files mentioned in include_relations
"""

import os
import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.generator import Generator
from c_to_plantuml.models import (
    FileModel,
    ProjectModel,
    IncludeRelation,
)


class TestGeneratorIncludeRelationsFilter(unittest.TestCase):
    """Test that PlantUML generation only includes headers mentioned in include_relations"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = Generator()
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_include_relations_filters_header_files(self):
        """Test that only header files mentioned in include_relations are included"""
        
        # Create a main.c file that has include_relations for only specific headers
        main_file_model = FileModel(
            file_path="main.c",
            includes={"header1.h", "header2.h", "header3.h"},  # All headers in includes
            include_relations=[
                # Only include_relations for header1.h and header2.h
                IncludeRelation(source_file="main.c", included_file="header1.h", depth=1),
                IncludeRelation(source_file="main.c", included_file="header2.h", depth=1),
                # Note: header3.h is NOT in include_relations but is in includes
            ]
        )

        # Create header file models
        header1_model = FileModel(file_path="header1.h", includes=set())
        header2_model = FileModel(file_path="header2.h", includes=set())
        header3_model = FileModel(file_path="header3.h", includes=set())  # This should NOT be included

        # Create ProjectModel
        project_model = ProjectModel(
            project_name="test_project",
            source_folder=str(self.test_dir),
            files={
                "main.c": main_file_model,
                "header1.h": header1_model,
                "header2.h": header2_model,
                "header3.h": header3_model,  # Present in project but not in include_relations
            },
        )

        # Generate PlantUML content
        puml_content = self.generator.generate_diagram(
            main_file_model, project_model, include_depth=1
        )

        print("Generated PlantUML content:")
        print(puml_content)

        # Assertions - only header1.h and header2.h should be included
        # header3.h should NOT be included even though it's in the includes list
        self.assertIn('class "header1" as HEADER_HEADER1', puml_content)
        self.assertIn('class "header2" as HEADER_HEADER2', puml_content)
        self.assertNotIn('class "header3" as HEADER_HEADER3', puml_content)

        # Verify include relationships are generated correctly
        self.assertIn('MAIN --> HEADER_HEADER1 : <<include>>', puml_content)
        self.assertIn('MAIN --> HEADER_HEADER2 : <<include>>', puml_content)
        self.assertNotIn('MAIN --> HEADER_HEADER3 : <<include>>', puml_content)

    def test_include_relations_includes_all_mentioned_files(self):
        """Test that all files mentioned in include_relations are included (even transitive)"""
        
        # Create main.c that directly includes header1.h
        # header1.h includes header2.h (transitive)
        # Since both are in include_relations, both should be included
        main_file_model = FileModel(
            file_path="main.c",
            includes={"header1.h"},
            include_relations=[
                # Direct include of header1.h from main.c
                IncludeRelation(source_file="main.c", included_file="header1.h", depth=1),
                # Transitive include mentioned in include_relations
                IncludeRelation(source_file="header1.h", included_file="header2.h", depth=2),
            ]
        )

        header1_model = FileModel(
            file_path="header1.h", 
            includes={"header2.h"},  # header1.h includes header2.h
            include_relations=[]  # No include_relations for header files
        )
        header2_model = FileModel(
            file_path="header2.h", 
            includes=set()
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder=str(self.test_dir),
            files={
                "main.c": main_file_model,
                "header1.h": header1_model,
                "header2.h": header2_model,
            },
        )

        # Generate PlantUML content
        puml_content = self.generator.generate_diagram(
            main_file_model, project_model, include_depth=2
        )

        print("Generated PlantUML content (includes all mentioned files):")
        print(puml_content)

        # Both headers should be included because they're both mentioned in include_relations
        self.assertIn('class "header1" as HEADER_HEADER1', puml_content)
        self.assertIn('class "header2" as HEADER_HEADER2', puml_content)

    def test_include_relations_excludes_files_not_in_relations(self):
        """Test that files NOT mentioned in include_relations are excluded"""
        
        # Create main.c that has header3.h in includes but NOT in include_relations
        main_file_model = FileModel(
            file_path="main.c",
            includes={"header1.h", "header2.h", "header3.h"},  # header3.h in includes
            include_relations=[
                # Only header1.h and header2.h in include_relations
                IncludeRelation(source_file="main.c", included_file="header1.h", depth=1),
                IncludeRelation(source_file="main.c", included_file="header2.h", depth=1),
                # header3.h is NOT in include_relations
            ]
        )

        header1_model = FileModel(file_path="header1.h", includes=set())
        header2_model = FileModel(file_path="header2.h", includes=set())
        header3_model = FileModel(file_path="header3.h", includes=set())

        project_model = ProjectModel(
            project_name="test_project",
            source_folder=str(self.test_dir),
            files={
                "main.c": main_file_model,
                "header1.h": header1_model,
                "header2.h": header2_model,
                "header3.h": header3_model,
            },
        )

        # Generate PlantUML content
        puml_content = self.generator.generate_diagram(
            main_file_model, project_model, include_depth=1
        )

        print("Generated PlantUML content (excludes files not in relations):")
        print(puml_content)

        # Only header1.h and header2.h should be included
        # header3.h should NOT be included even though it's in the includes list
        self.assertIn('class "header1" as HEADER_HEADER1', puml_content)
        self.assertIn('class "header2" as HEADER_HEADER2', puml_content)
        self.assertNotIn('class "header3" as HEADER_HEADER3', puml_content)

    def test_include_relations_excludes_transitive_includes(self):
        """Test that transitive includes are NOT included when include_relations is available"""
        
        # Create main.c that directly includes header1.h
        # header1.h includes header2.h (transitive)
        # But only direct includes should be in PlantUML when include_relations exists
        main_file_model = FileModel(
            file_path="main.c",
            includes={"header1.h"},
            include_relations=[
                # Only direct include of header1.h from main.c
                IncludeRelation(source_file="main.c", included_file="header1.h", depth=1),
                # This should NOT cause header2.h to be included in PlantUML
                IncludeRelation(source_file="header1.h", included_file="header2.h", depth=2),
            ]
        )

        header1_model = FileModel(
            file_path="header1.h", 
            includes={"header2.h"},  # header1.h includes header2.h
            include_relations=[]  # No include_relations for header files
        )
        header2_model = FileModel(
            file_path="header2.h", 
            includes=set()
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder=str(self.test_dir),
            files={
                "main.c": main_file_model,
                "header1.h": header1_model,
                "header2.h": header2_model,
            },
        )

        # Generate PlantUML content
        puml_content = self.generator.generate_diagram(
            main_file_model, project_model, include_depth=2
        )

        print("Generated PlantUML content (should exclude transitive):")
        print(puml_content)

        # Only header1.h should be included (directly mentioned in include_relations)
        # header2.h should NOT be included even though it's transitively included
        self.assertIn('class "header1" as HEADER_HEADER1', puml_content)
        self.assertNotIn('class "header2" as HEADER_HEADER2', puml_content)
        
        # Only the direct include relationship should exist
        self.assertIn('MAIN --> HEADER_HEADER1 : <<include>>', puml_content)
        self.assertNotIn('HEADER_HEADER1 --> HEADER_HEADER2 : <<include>>', puml_content)

    def test_include_relations_respects_transitive_includes(self):
        """Test that transitive includes are respected when mentioned in include_relations"""
        
        # Create main.c that includes header1.h, which includes header2.h transitively
        main_file_model = FileModel(
            file_path="main.c",
            includes={"header1.h"},
            include_relations=[
                IncludeRelation(source_file="main.c", included_file="header1.h", depth=1),
                IncludeRelation(source_file="header1.h", included_file="header2.h", depth=2),
                # Note: main.c never directly includes header2.h, but it's included transitively
            ]
        )

        header1_model = FileModel(
            file_path="header1.h", 
            includes={"header2.h"},
            include_relations=[]  # include_relations are only on .c files
        )
        header2_model = FileModel(file_path="header2.h", includes=set())

        project_model = ProjectModel(
            project_name="test_project",
            source_folder=str(self.test_dir),
            files={
                "main.c": main_file_model,
                "header1.h": header1_model,
                "header2.h": header2_model,
            },
        )

        # Generate PlantUML content
        puml_content = self.generator.generate_diagram(
            main_file_model, project_model, include_depth=2
        )

        print("Generated PlantUML content (transitive):")
        print(puml_content)

        # Both headers should be included because they're in include_relations
        self.assertIn('class "header1" as HEADER_HEADER1', puml_content)
        self.assertIn('class "header2" as HEADER_HEADER2', puml_content)

    def test_fallback_to_includes_when_no_include_relations(self):
        """Test that it falls back to includes when include_relations is empty"""
        
        # Create main.c with no include_relations (empty list)
        main_file_model = FileModel(
            file_path="main.c",
            includes={"header1.h", "header2.h"},
            include_relations=[]  # Empty - should fallback to includes
        )

        header1_model = FileModel(file_path="header1.h", includes=set())
        header2_model = FileModel(file_path="header2.h", includes=set())

        project_model = ProjectModel(
            project_name="test_project",
            source_folder=str(self.test_dir),
            files={
                "main.c": main_file_model,
                "header1.h": header1_model,
                "header2.h": header2_model,
            },
        )

        # Generate PlantUML content
        puml_content = self.generator.generate_diagram(
            main_file_model, project_model, include_depth=1
        )

        print("Generated PlantUML content (fallback):")
        print(puml_content)

        # Both headers should be included when falling back to includes
        self.assertIn('class "header1" as HEADER_HEADER1', puml_content)
        self.assertIn('class "header2" as HEADER_HEADER2', puml_content)


if __name__ == "__main__":
    unittest.main()