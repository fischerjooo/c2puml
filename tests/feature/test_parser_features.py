"""
Feature tests for C parser functionality

Tests the basic C parsing capabilities including structs, enums, functions, etc.
"""

from pathlib import Path

from .base import BaseFeatureTest


class TestParserFeatures(BaseFeatureTest):
    """Test basic C parsing functionality"""

    def test_feature_parser_basic_parsing(self):
        """Test basic C parsing functionality"""
        from c_to_plantuml.parser import CParser

        test_content = """
#include <stdio.h>

struct Person {
    char name[50];
    int age;
};

enum Status {
    OK,
    ERROR
};

int main() {
    return 0;
}

int global_var;
        """

        c_file = self.create_test_file("test.c", test_content)
        parser = CParser()
        file_model = parser.parse_file(Path(c_file), "test.c", str(Path(c_file).parent))

        # Verify parsing results
        self.assertIn("Person", file_model.structs)
        self.assertIn("Status", file_model.enums)
        self.assertEqual(len(file_model.functions), 1)
        self.assertEqual(file_model.functions[0].name, "main")
        self.assertGreaterEqual(len(file_model.globals), 1)
        self.assertIn("stdio.h", file_model.includes)