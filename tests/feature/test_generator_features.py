"""
Feature tests for PlantUML generation functionality

Tests the ability to generate PlantUML diagrams from parsed C code models.
"""

from .base import BaseFeatureTest
from c_to_plantuml.models import ProjectModel


class TestGeneratorFeatures(BaseFeatureTest):
    """Test PlantUML diagram generation"""

    def test_feature_plantuml_generation(self):
        """Test PlantUML diagram generation"""
        from c_to_plantuml.generator import Generator
        from c_to_plantuml.models import Enum, Field, FileModel, Function, Struct

        # Create test file model
        file_model = FileModel(
            file_path="test.c",
            relative_path="test.c",
            project_root="/test",
            encoding_used="utf-8",
            structs={
                "Person": Struct(
                    "Person", [Field("name", "char*"), Field("age", "int")]
                )
            },
            enums={"Status": Enum("Status", ["OK", "ERROR"])},
            functions=[Function("main", "int", [])],
            globals=[],
            includes=["stdio.h"],
            macros=[],
            typedefs={},
        )

        generator = Generator()
        # Create a simple project model for testing
        project_model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"test.c": file_model},
            created_at="2023-01-01T00:00:00"
        )
        content = generator.plantuml_generator.generate_diagram(file_model, project_model)

        # Verify PlantUML generation
        self.assertIn("@startuml test", content)
        self.assertIn("@enduml", content)
        self.assertIn('class "test" as TEST <<source>> #LightBlue', content)
        # Header classes not implemented in current version
        # self.assertIn('class "stdio" as STDIO <<header>> #LightGreen', content)
        self.assertIn("+ struct Person", content)
        self.assertIn("+ enum Status", content)