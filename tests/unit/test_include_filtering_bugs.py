#!/usr/bin/env python3
"""
Unit tests for include filtering bugs and edge cases.
These tests are designed to expose issues with the current include filtering implementation.
"""

import unittest
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from src.c2puml.core.transformer import Transformer
from src.c2puml.models import FileModel, ProjectModel, IncludeRelation


class TestIncludeFilteringBugs(unittest.TestCase):
    """Test class to expose bugs in include filtering functionality"""

    def setUp(self):
        """Setup for each test method"""
        self.transformer = Transformer()

    def test_include_filters_applied_at_all_depths_bug_fix(self):
        """
        Test that include filters are applied at all depths, not just depth 1.
        
        This test creates a hierarchical include structure to verify that include
        filters are properly applied at all depths, not just direct includes.
        
        Structure:
        - processor.c includes worker.h and api.h (depth 1)
        - api.h includes types.h, memory.h, platform.h (depth 2)
        - worker.h includes validation.h, errors.h (depth 2)
        - types.h includes constants.h (depth 3)
        
        The bug was that include filters were only applied at depth 1, allowing
        all transitive includes (depth 2+) to pass through even if they didn't
        match the filter patterns.
        
        Expected behavior: Only includes matching the filter patterns should be
        present in include_relations, regardless of depth.
        """
        # Create a project with hierarchical include structure
        project = ProjectModel(
            project_name="filter_test",
            source_folder="/test",
            files={}
        )
        
        # Main C file that includes two headers
        processor_c = FileModel(
            file_path="processor.c",
            includes={"worker.h", "api.h"},
            structs={}, enums={}, unions={}, functions=[], globals=[], 
            macros=[], aliases={}, include_relations=[]
        )
        
        # Private header that includes other private headers (should be filtered out at depth 2)
        worker_h = FileModel(
            file_path="worker.h",
            includes={"validation.h", "errors.h"},
            structs={}, enums={}, unions={}, functions=[], globals=[], 
            macros=[], aliases={}, include_relations=[]
        )
        
        # Main API header that includes types and other headers (should be filtered out at depth 2)
        api_h = FileModel(
            file_path="api.h",
            includes={"types.h", "memory.h", "platform.h"},
            structs={}, enums={}, unions={}, functions=[], globals=[], 
            macros=[], aliases={}, include_relations=[]
        )
        
        # Types header that includes defines (should be filtered out at depth 3)
        types_h = FileModel(
            file_path="types.h",
            includes={"constants.h"},
            structs={}, enums={}, unions={}, functions=[], globals=[], 
            macros=[], aliases={}, include_relations=[]
        )
        
        # Other headers that should be filtered out
        memory_h = FileModel(
            file_path="memory.h",
            includes={},
            structs={}, enums={}, unions={}, functions=[], globals=[], 
            macros=[], aliases={}, include_relations=[]
        )
        
        constants_h = FileModel(
            file_path="constants.h",
            includes={},
            structs={}, enums={}, unions={}, functions=[], globals=[], 
            macros=[], aliases={}, include_relations=[]
        )
        
        platform_h = FileModel(
            file_path="platform.h",
            includes={},
            structs={}, enums={}, unions={}, functions=[], globals=[], 
            macros=[], aliases={}, include_relations=[]
        )
        
        validation_h = FileModel(
            file_path="validation.h",
            includes={},
            structs={}, enums={}, unions={}, functions=[], globals=[], 
            macros=[], aliases={}, include_relations=[]
        )
        
        errors_h = FileModel(
            file_path="errors.h",
            includes={},
            structs={}, enums={}, unions={}, functions=[], globals=[], 
            macros=[], aliases={}, include_relations=[]
        )
        
        # Add all files to the project
        project.files = {
            "processor.c": processor_c,
            "worker.h": worker_h,
            "api.h": api_h,
            "types.h": types_h,
            "memory.h": memory_h,
            "constants.h": constants_h,
            "platform.h": platform_h,
            "validation.h": validation_h,
            "errors.h": errors_h
        }
        
        # Configure file-specific include filters to only allow specific patterns
        config = {
            "include_depth": 1,  # Global depth
            "file_specific": {
                "processor.c": {
                    "include_filter": [
                        "worker\\.h$",  # Only allow the worker header
                        "api\\.h$"     # Only allow the API header
                    ],
                    "include_depth": 3  # Allow deeper includes, but only matching the filter
                }
            }
        }
        
        # Process include relations using the simplified method
        result = self.transformer._process_include_relations_simplified(project, config)
        
        # Get the processed include relations for processor.c
        processor_relations = processor_c.include_relations
        
        print(f"\nFound {len(processor_relations)} include relations:")
        for rel in processor_relations:
            print(f"  {rel.source_file} -> {rel.included_file} (depth {rel.depth})")
        
        # CRITICAL TEST: With the bug, we would see 8 relations (including filtered ones)
        # With the fix, we should see only 2 relations (matching the filter)
        
        # Expected relations (only these should be present):
        # 1. processor.c -> api.h (depth 1) - matches "api\\.h$" 
        # 2. processor.c -> worker.h (depth 1) - matches "worker\\.h$"
        
        # With the bug, we would also see (these should NOT be present):
        # 3. api.h -> types.h (depth 2) - does NOT match filter
        # 4. api.h -> memory.h (depth 2) - does NOT match filter  
        # 5. api.h -> platform.h (depth 2) - does NOT match filter
        # 6. worker.h -> validation.h (depth 2) - does NOT match filter
        # 7. worker.h -> errors.h (depth 2) - does NOT match filter
        # 8. types.h -> constants.h (depth 3) - does NOT match filter
        
        # Verify we have exactly 2 relations (the fix)
        self.assertEqual(
            len(processor_relations), 2, 
            f"Expected exactly 2 include relations after filtering, but got {len(processor_relations)}. "
            f"If this is 8, the bug is present (filters only applied at depth 1). "
            f"Relations found: {[(r.source_file, r.included_file, r.depth) for r in processor_relations]}"
        )
        
        # Verify the specific relations that should be present
        relation_tuples = {(rel.source_file, rel.included_file, rel.depth) for rel in processor_relations}
        expected_relations = {
            ("processor.c", "api.h", 1),
            ("processor.c", "worker.h", 1)
        }
        
        self.assertEqual(
            relation_tuples, expected_relations,
            f"Expected relations {expected_relations}, but got {relation_tuples}. "
            f"Extra relations indicate the bug where filters are not applied at all depths."
        )
        
        # Verify no filtered relations are present (these would indicate the bug)
        unwanted_relations = {
            ("api.h", "types.h"),
            ("api.h", "memory.h"),
            ("api.h", "platform.h"),
            ("worker.h", "validation.h"),
            ("worker.h", "errors.h"),
            ("types.h", "constants.h")
        }
        
        actual_source_target_pairs = {(rel.source_file, rel.included_file) for rel in processor_relations}
        
        for unwanted_source, unwanted_target in unwanted_relations:
            self.assertNotIn(
                (unwanted_source, unwanted_target), actual_source_target_pairs,
                f"Found unwanted relation {unwanted_source} -> {unwanted_target}. "
                f"This indicates the bug where include filters are not applied at depth > 1."
            )

    def test_include_filters_depth_boundary_conditions(self):
        """
        Test include filters at various depth boundaries to ensure the fix works correctly.
        """
        project = ProjectModel(
            project_name="depth_test",
            source_folder="/test",
            files={}
        )
        
        # Create a chain: main.c -> a.h -> b.h -> c.h -> d.h
        main_c = FileModel(file_path="main.c", includes={"a.h"})
        a_h = FileModel(file_path="a.h", includes={"b.h"})
        b_h = FileModel(file_path="b.h", includes={"c.h"}) 
        c_h = FileModel(file_path="c.h", includes={"d.h"})
        d_h = FileModel(file_path="d.h", includes={})
        
        for fm in [main_c, a_h, b_h, c_h, d_h]:
            fm.structs = {}
            fm.enums = {}
            fm.unions = {}
            fm.functions = []
            fm.globals = []
            fm.macros = []
            fm.aliases = {}
            fm.include_relations = []
        
        project.files = {
            "main.c": main_c,
            "a.h": a_h,
            "b.h": b_h,
            "c.h": c_h,
            "d.h": d_h
        }
        
        # Test 1: Filter that only allows a.h (should block b.h, c.h, d.h at all depths)
        config_restrictive = {
            "include_depth": 1,
            "file_specific": {
                "main.c": {
                    "include_filter": ["a\\.h$"],  # Only a.h allowed
                    "include_depth": 4  # Allow deep processing but filter everything except a.h
                }
            }
        }
        
        self.transformer._process_include_relations_simplified(project, config_restrictive)
        
        # Should only have main.c -> a.h, no transitive includes
        self.assertEqual(len(main_c.include_relations), 1)
        self.assertEqual(main_c.include_relations[0].included_file, "a.h")
        self.assertEqual(main_c.include_relations[0].depth, 1)
        
        # Reset relations for next test
        main_c.include_relations = []
        
        # Test 2: Filter that allows a.h and c.h (should have main->a, a->b, b->c, but NOT c->d)
        config_selective = {
            "include_depth": 1,
            "file_specific": {
                "main.c": {
                    "include_filter": ["[ac]\\.h$"],  # Only a.h and c.h allowed
                    "include_depth": 4
                }
            }
        }
        
        self.transformer._process_include_relations_simplified(project, config_selective)
        
        # Should have: main->a (depth 1), but no others since b.h doesn't match filter
        self.assertEqual(len(main_c.include_relations), 1)
        relation_pairs = {(rel.source_file, rel.included_file) for rel in main_c.include_relations}
        self.assertEqual(relation_pairs, {("main.c", "a.h")})

    def test_multiple_files_with_different_include_filters(self):
        """
        Test that different C files can have different include filters applied correctly.
        """
        project = ProjectModel(
            project_name="multi_file_test",
            source_folder="/test",
            files={}
        )
        
        # Create two C files with different include patterns
        file1_c = FileModel(file_path="file1.c", includes={"common.h", "specific1.h"})
        file2_c = FileModel(file_path="file2.c", includes={"common.h", "specific2.h"})
        
        common_h = FileModel(file_path="common.h", includes={"base.h", "utils.h"})
        specific1_h = FileModel(file_path="specific1.h", includes={"private1.h"})
        specific2_h = FileModel(file_path="specific2.h", includes={"private2.h"})
        base_h = FileModel(file_path="base.h", includes={})
        utils_h = FileModel(file_path="utils.h", includes={})
        private1_h = FileModel(file_path="private1.h", includes={})
        private2_h = FileModel(file_path="private2.h", includes={})
        
        for fm in [file1_c, file2_c, common_h, specific1_h, specific2_h, base_h, utils_h, private1_h, private2_h]:
            fm.structs = {}
            fm.enums = {}
            fm.unions = {}
            fm.functions = []
            fm.globals = []
            fm.macros = []
            fm.aliases = {}
            fm.include_relations = []
        
        project.files = {
            "file1.c": file1_c,
            "file2.c": file2_c,
            "common.h": common_h,
            "specific1.h": specific1_h,
            "specific2.h": specific2_h,
            "base.h": base_h,
            "utils.h": utils_h,
            "private1.h": private1_h,
            "private2.h": private2_h
        }
        
        # Different filters for each file
        config = {
            "include_depth": 1,
            "file_specific": {
                "file1.c": {
                    "include_filter": ["common\\.h$", "base\\.h$"],  # Allow common.h and base.h
                    "include_depth": 3
                },
                "file2.c": {
                    "include_filter": ["common\\.h$", "utils\\.h$"],  # Allow common.h and utils.h
                    "include_depth": 3
                }
            }
        }
        
        self.transformer._process_include_relations_simplified(project, config)
        
        # file1.c should have: file1->common (depth 1), common->base (depth 2)
        # NOT: file1->specific1, common->utils, specific1->private1
        file1_relations = {(rel.source_file, rel.included_file) for rel in file1_c.include_relations}
        expected_file1 = {("file1.c", "common.h"), ("common.h", "base.h")}
        self.assertEqual(file1_relations, expected_file1)
        
        # file2.c should have: file2->common (depth 1), common->utils (depth 2)  
        # NOT: file2->specific2, common->base, specific2->private2
        file2_relations = {(rel.source_file, rel.included_file) for rel in file2_c.include_relations}
        expected_file2 = {("file2.c", "common.h"), ("common.h", "utils.h")}
        self.assertEqual(file2_relations, expected_file2)

    def test_duplicate_method_definition_bug(self):
        """Test that there are not multiple definitions of the same method"""
        # This test checks for the duplicate _apply_include_filters method bug
        import inspect
        import src.c2puml.core.transformer as transformer_module
        
        # Get all methods of the Transformer class
        transformer_methods = inspect.getmembers(Transformer, predicate=inspect.isfunction)
        method_names = [name for name, _ in transformer_methods]
        
        # Check for duplicate method names
        unique_methods = set(method_names)
        self.assertEqual(len(method_names), len(unique_methods), f"Duplicate methods found: {[name for name in method_names if method_names.count(name) > 1]}")
        
        # Specifically check that _apply_include_filters is not duplicated in source
        source_lines = inspect.getsource(transformer_module).split('\n')
        apply_include_filters_definitions = [
            line for line in source_lines 
            if line.strip().startswith('def _apply_include_filters(')
        ]
        
        self.assertLessEqual(len(apply_include_filters_definitions), 1, f"Found {len(apply_include_filters_definitions)} definitions of _apply_include_filters method")

    def test_header_mapping_with_multiple_c_files_bug(self):
        """Test that header mapping is incorrect when multiple C files exist"""
        # Create a project with multiple C files
        main_c = FileModel(
            file_path="/project/main.c",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"stdio.h", "stdlib.h"}, macros=[], aliases={}, include_relations=[]
        )
        
        utils_c = FileModel(
            file_path="/project/utils.c",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"string.h", "math.h"}, macros=[], aliases={}, include_relations=[]
        )
        
        project_model = ProjectModel(
            source_folder="/project",
            project_name="TestProject",
            files={"main.c": main_c, "utils.c": utils_c}
        )

        # Test configuration with filters for main.c only
        config = {
            "file_specific": {"main.c": {"include_filter": [r"stdio\.h"]}},
            "include_depth": 2
        }
        
        # Extract include filters
        include_filters = self.transformer._extract_include_filters_from_config(config)
        
        # Should only have filters for main.c
        self.assertEqual(len(include_filters), 1)
        self.assertIn("main.c", include_filters)
        self.assertEqual(include_filters["main.c"], [r"stdio\.h"])
        
        # Apply include filters
        result = self.transformer._apply_include_filters(project_model, include_filters)
        
        # main.c should still exist (has filters)
        self.assertIn("main.c", result.files)
        
        # utils.c should still exist (no filters, so not affected)
        self.assertIn("utils.c", result.files)

    def test_include_pipeline_vs_direct_filtering_behavior_difference(self):
        """Test the difference between pipeline and direct include filtering approaches"""
        # Create project using the full pipeline
        file_model_pipeline = FileModel(
            file_path="/test/main.c",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"stdio.h", "stdlib.h"}, macros=[], aliases={}, include_relations=[]
        )
        
        project_model_pipeline = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"main.c": file_model_pipeline}
        )
        
        # Create project for direct filtering test (deep copy)
        file_model_direct = FileModel(
            file_path="/test/main.c",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"stdio.h", "stdlib.h"}, macros=[], aliases={}, include_relations=[]
        )
        
        project_model_direct = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"main.c": file_model_direct}
        )

        # Test configuration
        config = {
            "file_specific": {"main.c": {"include_filter": [r"stdio\.h"]}},
            "include_depth": 2
        }
        
        # Apply transformations using the main pipeline (preserves includes)
        result_pipeline = self.transformer._apply_transformations(project_model_pipeline, config)
        
        # Apply include filters directly (comprehensive filtering)
        include_filters = self.transformer._extract_include_filters_from_config(config)
        result_direct = self.transformer._apply_include_filters(project_model_direct, include_filters)
        
        # Results should be different but predictable
        main_file_pipeline = result_pipeline.files["main.c"]
        main_file_direct = result_direct.files["main.c"]
        
        # Both pipeline and direct method should preserve includes arrays (correct behavior)
        self.assertEqual(len(main_file_pipeline.includes), 2, "Pipeline should preserve all includes")
        self.assertEqual(len(main_file_direct.includes), 2, "Direct method should preserve all includes")
        self.assertIn("stdio.h", main_file_direct.includes, "Direct method should preserve all includes")
        self.assertIn("stdlib.h", main_file_direct.includes, "Direct method should preserve all includes")

    def test_include_filter_with_no_matching_files(self):
        """Test include filtering when no files match the specified root file names"""
        file_model = FileModel(
            file_path="/test/actual_file.c",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"stdio.h", "stdlib.h"}, macros=[], aliases={}, include_relations=[]
        )
        
        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"actual_file.c": file_model}
        )

        # Configure filters for a file that doesn't exist
        include_filters = {"nonexistent_file.c": [r"stdio\.h"]}
        
        # Apply filters
        result = self.transformer._apply_include_filters(project_model, include_filters)
        
        # Since no files match the filter specification, no filtering should occur
        actual_file = result.files["actual_file.c"]
        self.assertEqual(len(actual_file.includes), 2, "No filtering should occur for unmatched files")
        self.assertIn("stdio.h", actual_file.includes)
        self.assertIn("stdlib.h", actual_file.includes)

    def test_include_filter_empty_patterns_handling(self):
        """Test include filtering with empty or invalid patterns"""
        file_model = FileModel(
            file_path="/test/main.c",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"stdio.h", "stdlib.h"}, macros=[], aliases={}, include_relations=[]
        )
        
        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"main.c": file_model}
        )

        # Test with empty patterns
        include_filters_empty = {"main.c": []}
        result_empty = self.transformer._apply_include_filters(project_model, include_filters_empty)
        
        # Empty patterns should preserve all includes
        main_file_empty = result_empty.files["main.c"]
        self.assertEqual(len(main_file_empty.includes), 2)

    def test_include_filter_regex_compilation_errors(self):
        """Test include filtering with invalid regex patterns"""
        file_model = FileModel(
            file_path="/test/main.c",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"stdio.h", "stdlib.h"}, macros=[], aliases={}, include_relations=[]
        )
        
        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"main.c": file_model}
        )

        # Test with invalid regex patterns
        include_filters_invalid = {"main.c": ["[invalid regex"]}
        
        # Should handle gracefully without crashing
        try:
            result = self.transformer._apply_include_filters(project_model, include_filters_invalid)
            # If it doesn't crash, the test passes
            self.assertTrue(True, "Invalid regex patterns handled gracefully")
        except Exception as e:
            self.fail(f"Invalid regex patterns should be handled gracefully, but got: {e}")

    def test_complex_include_hierarchy_filtering(self):
        """Test include filtering with complex hierarchical structures"""
        project = ProjectModel(
            project_name="complex_test",
            source_folder="/test",
            files={}
        )
        
        # Create complex hierarchy: main.c -> {system.h, local.h}
        # system.h -> kernel.h, local.h -> app.h
        main_c = FileModel(file_path="main.c", includes={"system.h", "local.h"})
        system_h = FileModel(file_path="system.h", includes={"kernel.h"})
        local_h = FileModel(file_path="local.h", includes={"app.h"})
        kernel_h = FileModel(file_path="kernel.h", includes={})
        app_h = FileModel(file_path="app.h", includes={})
        
        # Initialize all file models properly
        for fm in [main_c, system_h, local_h, kernel_h, app_h]:
            fm.structs = {}
            fm.enums = {}
            fm.unions = {}
            fm.functions = []
            fm.globals = []
            fm.macros = []
            fm.aliases = {}
            fm.include_relations = []
        
        project.files = {
            "main.c": main_c,
            "system.h": system_h, 
            "local.h": local_h,
            "kernel.h": kernel_h,
            "app.h": app_h
        }
        
        # Configure to only include "local*" and "app*" files (updated for new behavior)
        config = {
            "include_depth": 3,
            "file_specific": {
                "main.c": {
                    "include_filter": ["local.*", "app.*"]  # Include both local.h and app.h
                }
            }
        }
        
        result = self.transformer._process_include_relations_simplified(project, config)
        
        # Should only have relations for local.h and app.h
        self.assertEqual(len(main_c.include_relations), 2)
        
        included_files = {rel.included_file for rel in main_c.include_relations}
        self.assertEqual(included_files, {"local.h", "app.h"})
        
        # Verify no system.h or kernel.h
        self.assertNotIn("system.h", included_files)
        self.assertNotIn("kernel.h", included_files)

    def test_simplified_cycle_prevention(self):
        """Test that simplified processing prevents cycles correctly"""
        project = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={}
        )
        
        # Create circular dependency: main.c -> a.h -> b.h -> a.h
        main_c = FileModel(file_path="main.c", includes={"a.h"})
        a_h = FileModel(file_path="a.h", includes={"b.h"})
        b_h = FileModel(file_path="b.h", includes={"a.h"})  # Creates cycle
        
        project.files = {
            "main.c": main_c,
            "a.h": a_h,
            "b.h": b_h
        }
        
        config = {"include_depth": 5}  # High depth to expose cycles
        result = self.transformer._process_include_relations_simplified(project, config)
        
        # Should have exactly 2 relations without infinite loop
        self.assertEqual(len(main_c.include_relations), 2)
        
        # Relations should be main->a and a->b (b->a blocked by cycle prevention)
        relations = {(rel.source_file, rel.included_file) for rel in main_c.include_relations}
        expected = {("main.c", "a.h"), ("a.h", "b.h")}
        self.assertEqual(relations, expected)

    def test_case_sensitivity_in_include_filtering(self):
        """Test that include filtering properly handles case sensitivity"""
        project = ProjectModel(
            project_name="case_test",
            source_folder="/test",
            files={}
        )
        
        main_c = FileModel(file_path="main.c", includes={"Header.h", "header.h", "HEADER.H"})
        header1 = FileModel(file_path="Header.h", includes={})
        header2 = FileModel(file_path="header.h", includes={})
        header3 = FileModel(file_path="HEADER.H", includes={})
        
        for fm in [main_c, header1, header2, header3]:
            fm.structs = {}
            fm.enums = {}
            fm.unions = {}
            fm.functions = []
            fm.globals = []
            fm.macros = []
            fm.aliases = {}
            fm.include_relations = []
        
        project.files = {
            "main.c": main_c,
            "Header.h": header1,
            "header.h": header2,
            "HEADER.H": header3
        }
        
        # Case-sensitive filter
        config = {
            "include_depth": 2,
            "file_specific": {
                "main.c": {
                    "include_filter": ["Header\\.h$"]  # Only matches exact case
                }
            }
        }
        
        result = self.transformer._process_include_relations_simplified(project, config)
        
        # Should only match "Header.h", not "header.h" or "HEADER.H"
        self.assertEqual(len(main_c.include_relations), 1)
        self.assertEqual(main_c.include_relations[0].included_file, "Header.h")


if __name__ == '__main__':
    unittest.main()