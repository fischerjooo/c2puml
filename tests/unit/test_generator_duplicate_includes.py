#!/usr/bin/env python3

import unittest

from c2puml.generator import Generator
from c2puml.models import FileModel, IncludeRelation, ProjectModel


class TestGeneratorDuplicateIncludes(unittest.TestCase):
    """Test for duplicate include relationships bug in PlantUML generation"""

    def setUp(self):
        self.generator = Generator()

    def test_duplicate_include_relationships_bug(self):
        """Test that reproduces the duplicate include relationships bug"""

        # Create a simple project structure: main.c -> utils.h -> config.h
        files = {
            "main.c": FileModel(
                name="main.c",
                file_path="/test/main.c",
                includes={"utils.h"},  # Direct include
                include_relations=[
                    # Complete dependency tree from transformation
                    IncludeRelation(
                        source_file="main.c", included_file="utils.h", depth=1
                    ),
                    IncludeRelation(
                        source_file="utils.h", included_file="config.h", depth=2
                    ),
                ],
                structs={},
                enums={},
                functions=[],
                globals=[],
                aliases={},
                unions={},
                macros=[],
            ),
            "utils.h": FileModel(
                name="utils.h",
                file_path="/test/utils.h",
                includes={"config.h"},  # Direct include (causes duplicate)
                include_relations=[],  # Empty for .h files (correct after fix)
                structs={},
                enums={},
                functions=[],
                globals=[],
                aliases={},
                unions={},
                macros=[],
            ),
            "config.h": FileModel(
                name="config.h",
                file_path="/test/config.h",
                includes=set(),  # No includes
                include_relations=[],  # Empty for .h files
                structs={},
                enums={},
                functions=[],
                globals=[],
                aliases={},
                unions={},
                macros=[],
            ),
        }

        project_model = ProjectModel(
            project_name="test_project", source_folder="/test", files=files
        )

        # Generate PlantUML
        main_c_file = files["main.c"]
        plantuml_content = self.generator.generate_diagram(
            main_c_file, project_model, include_depth=3
        )
        lines = plantuml_content.split("\n")

        # Find include relationships section
        include_lines = []
        in_include_section = False
        for line in lines:
            if line.strip() == "' Include relationships":
                in_include_section = True
                continue
            elif in_include_section and line.strip() == "' Declaration relationships":
                break
            elif in_include_section and line.strip() and not line.startswith("'"):
                include_lines.append(line.strip())

        print(f"Generated include relationships:")
        for line in include_lines:
            print(f"  {line}")

        # Count occurrences of each relationship
        relationship_counts = {}
        for line in include_lines:
            if " --> " in line and "<<include>>" in line:
                relationship_counts[line] = relationship_counts.get(line, 0) + 1

        print(f"\nRelationship counts:")
        for rel, count in relationship_counts.items():
            print(f"  {count}x: {rel}")

        # Check for duplicates
        duplicates = {
            rel: count for rel, count in relationship_counts.items() if count > 1
        }

        # This test SHOULD FAIL before the fix, showing the bug
        self.assertEqual(
            len(duplicates), 0, f"Found duplicate include relationships: {duplicates}"
        )

        # Verify expected relationships (should appear exactly once each)
        expected_relationships = [
            "MAIN --> HEADER_UTILS : <<include>>",
            "HEADER_UTILS --> HEADER_CONFIG : <<include>>",
        ]

        for expected in expected_relationships:
            # Check that each expected relationship appears exactly once
            count = relationship_counts.get(expected, 0)
            self.assertEqual(
                count,
                1,
                f"Expected '{expected}' to appear exactly once, but found {count} times",
            )

    def test_include_relationships_with_multiple_c_files(self):
        """Test that multiple .c files don't create conflicts"""

        # Create structure: app.c -> utils.h, test.c -> utils.h -> config.h
        files = {
            "app.c": FileModel(
                name="app.c",
                file_path="/test/app.c",
                includes={"utils.h"},
                include_relations=[
                    IncludeRelation(
                        source_file="app.c", included_file="utils.h", depth=1
                    ),
                    IncludeRelation(
                        source_file="utils.h", included_file="config.h", depth=2
                    ),
                ],
                structs={},
                enums={},
                functions=[],
                globals=[],
                aliases={},
                unions={},
                macros=[],
            ),
            "test.c": FileModel(
                name="test.c",
                file_path="/test/test.c",
                includes={"utils.h"},
                include_relations=[
                    IncludeRelation(
                        source_file="test.c", included_file="utils.h", depth=1
                    ),
                    IncludeRelation(
                        source_file="utils.h", included_file="config.h", depth=2
                    ),
                ],
                structs={},
                enums={},
                functions=[],
                globals=[],
                aliases={},
                unions={},
                macros=[],
            ),
            "utils.h": FileModel(
                name="utils.h",
                file_path="/test/utils.h",
                includes={"config.h"},  # This should NOT be duplicated
                include_relations=[],  # Empty for .h files
                structs={},
                enums={},
                functions=[],
                globals=[],
                aliases={},
                unions={},
                macros=[],
            ),
            "config.h": FileModel(
                name="config.h",
                file_path="/test/config.h",
                includes=set(),
                include_relations=[],
                structs={},
                enums={},
                functions=[],
                globals=[],
                aliases={},
                unions={},
                macros=[],
            ),
        }

        project_model = ProjectModel(
            project_name="test_project", source_folder="/test", files=files
        )

        # Generate PlantUML for both files
        for c_file in ["app.c", "test.c"]:
            with self.subTest(c_file=c_file):
                c_file_model = files[c_file]
                plantuml_content = self.generator.generate_diagram(
                    c_file_model, project_model, include_depth=3
                )
                lines = plantuml_content.split("\n")

                # Extract include relationships
                include_lines = []
                in_include_section = False
                for line in lines:
                    if line.strip() == "' Include relationships":
                        in_include_section = True
                        continue
                    elif (
                        in_include_section
                        and line.strip() == "' Declaration relationships"
                    ):
                        break
                    elif (
                        in_include_section and line.strip() and not line.startswith("'")
                    ):
                        include_lines.append(line.strip())

                # Count duplicates
                relationship_counts = {}
                for line in include_lines:
                    if " --> " in line and "<<include>>" in line:
                        relationship_counts[line] = relationship_counts.get(line, 0) + 1

                duplicates = {
                    rel: count
                    for rel, count in relationship_counts.items()
                    if count > 1
                }
                self.assertEqual(
                    len(duplicates),
                    0,
                    f"Found duplicate relationships in {c_file}: {duplicates}",
                )


if __name__ == "__main__":
    unittest.main()
