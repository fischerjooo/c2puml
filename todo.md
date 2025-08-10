## Test Suite Consolidation Plan (YAML scenarios)

Goal: Reduce the number of YAML test scenarios while preserving full coverage. Each `.yml` remains a single scenario, but becomes more comprehensive by merging closely related cases.

Constraints
- Keep 1:1 base-name pairing (`test_*.py` ↔ `test_*.yml`).
- Each YAML contains a single scenario (one test case) with richer inputs/assertions.
- Preserve coverage for parser, tokenizer, preprocessor, transformer, generator, verifier, CLI, and integration features.
- De-duplicate overlapping tests and unify naming.

High-level approach
- Merge granular scenarios into comprehensive ones per area.
- Keep separate scenarios where negative/error flows are essential.
- Normalize naming: `*_comprehensive.yml` or `*_workflows.yml` for merged tests.

---

Planned merges by category (old → new)

Tokenizer and Preprocessor
- tests/unit/test_tokenizer_comprehensive_parsing.yml
- tests/unit/test_tokenizer_comprehensive_edge_cases.yml
- tests/unit/test_tokenizer_complex_mixed_structures.yml
- tests/unit/test_tokenizer_complex_function_parsing.yml
- tests/unit/test_tokenizer_keywords.yml
- tests/unit/test_tokenizer_validation_comprehensive.yml
→ tests/unit/test_tokenizer_comprehensive.yml

- tests/unit/test_preprocessor_handling_comprehensive.yml
- tests/unit/test_preprocessor_bug_comprehensive.yml
- tests/unit/test_macro_duplicates_simple.yml
- tests/unit/test_macro_duplicates_complex.yml
→ tests/unit/test_preprocessor_and_macros_comprehensive.yml

Parser (structures, typedefs, functions, includes, encoding)
- tests/unit/test_parser_simple_c_file.yml
- tests/unit/test_simple_c_file_parsing.yml
- tests/unit/test_parser_complete.yml
- tests/unit/test_parser_mixed_comprehensive.yml
- tests/unit/test_global_parsing_comprehensive.yml
→ tests/unit/test_parser_comprehensive_basics.yml

- tests/unit/test_parser_structs.yml
- tests/unit/test_parser_enums.yml
- tests/unit/test_parser_globals.yml
- tests/unit/test_parser_macros.yml
→ tests/unit/test_parser_elements_comprehensive.yml

- tests/unit/test_parser_typedefs.yml
- tests/unit/test_parser_typedef_struct.yml
- tests/unit/test_parser_enum_comprehensive_simple.yml
- tests/unit/test_parser_enum_comprehensive_typedef.yml
→ tests/unit/test_parser_typedefs_comprehensive.yml

- tests/unit/test_parser_nested_structures_comprehensive_struct.yml
- tests/unit/test_parser_nested_structures_comprehensive_union.yml
- tests/unit/test_parser_nested_structures_comprehensive_puml.yml
→ tests/unit/test_parser_nested_structures_comprehensive.yml

- tests/unit/test_struct_order_puml.yml
- tests/unit/test_struct_order_preservation.yml
- tests/unit/test_nested_structures_puml.yml
- tests/unit/test_struct_order_complex.yml
→ tests/unit/test_struct_and_nested_ordering_comprehensive.yml

- tests/unit/test_parser_functions.yml
- tests/unit/test_parser_function_comprehensive_declarations.yml
- tests/unit/test_parser_function_comprehensive_definitions.yml
- tests/unit/test_parser_function_comprehensive_modifiers.yml
- tests/unit/test_function_parameters_parsing.yml
- tests/unit/test_function_parameters_display.yml
- tests/unit/test_function_parameters_empty.yml
- tests/unit/test_function_params_parsing.yml
- tests/unit/test_function_params_complex.yml
- tests/unit/test_function_parameters_complex.yml
→ tests/unit/test_parser_functions_and_parameters_comprehensive.yml
  - Note: unify duplicate naming `function_params_*` vs `function_parameters_*`.

- tests/unit/test_parser_includes.yml
- tests/unit/test_include_processing_comprehensive.yml
→ tests/unit/test_parser_includes_comprehensive.yml

- tests/unit/test_parser_encoding.yml
→ Keep as is OR fold into `test_tokenizer_comprehensive.yml` if covered; prefer keep as standalone if encoding-specific edge cases are unique.

Typedef extraction
- tests/unit/test_typedef_extraction_comprehensive_simple.yml
- tests/unit/test_typedef_extraction_comprehensive_function_pointers.yml
- tests/unit/test_typedef_extraction_comprehensive_structs.yml
- tests/unit/test_typedef_extraction_comprehensive_enums.yml
- tests/unit/test_typedef_extraction_comprehensive_unions.yml
- tests/unit/test_typedef_extraction_comprehensive_mixed.yml
- tests/unit/test_typedef_extraction_comprehensive_edge_cases.yml
→ tests/unit/test_typedef_extraction_comprehensive.yml

Anonymous structures and debug variants
- tests/unit/test_anonymous_structure_comprehensive_typedef.yml
- tests/unit/test_anonymous_structure_comprehensive_nested.yml
- tests/unit/test_anonymous_structure_comprehensive_unions.yml
- tests/unit/test_anonymous_processing_comprehensive.yml
- tests/unit/test_debug_parsing_comprehensive_struct.yml
- tests/unit/test_debug_parsing_comprehensive_union.yml
- tests/unit/test_debug_parsing_comprehensive_anonymous.yml
- tests/unit/test_debug_field_parsing_comprehensive_struct.yml
- tests/unit/test_debug_field_parsing_comprehensive_union.yml
- tests/unit/test_debug_field_parsing_comprehensive_anonymous.yml
→ tests/unit/test_anonymous_structures_and_unions_comprehensive.yml

Path resolution and include tree
- tests/unit/test_absolute_path_bug_comprehensive_relative_path.yml
- tests/unit/test_absolute_path_bug_comprehensive_subdirectory.yml
- tests/unit/test_absolute_path_bug_comprehensive_mixed_paths.yml
- tests/unit/test_generator_include_tree_cli_absolute_paths.yml
- tests/unit/test_generator_include_tree_cli_comprehensive.yml
→ tests/unit/test_path_resolution_and_include_tree_comprehensive.yml

File-specific configuration
- tests/unit/test_file_specific_configuration_comprehensive_extraction.yml
- tests/unit/test_file_specific_configuration_comprehensive_depth.yml
- tests/unit/test_file_specific_configuration_comprehensive_filter.yml
- tests/unit/test_file_specific_configuration_comprehensive_patterns.yml
→ tests/unit/test_file_specific_configuration_comprehensive.yml

Transformer
- tests/unit/test_transformer_basic.yml
- tests/unit/test_transformer_comprehensive_operations.yml
- tests/unit/test_transformer_comprehensive_filtering.yml
- tests/unit/test_transformer_comprehensive_includes.yml
→ tests/unit/test_transformer_comprehensive.yml

Generator: formatting, naming, grouping, visibility, includes
- tests/unit/test_generator_basic_plantuml.yml
- tests/unit/test_generator_comprehensive.yml
- tests/unit/test_generator_new_formatting_cli_enum_stereotype.yml
- tests/unit/test_generator_new_formatting_cli_struct_stereotype.yml
- tests/unit/test_generator_new_formatting_cli_union_stereotype.yml
- tests/unit/test_generator_new_formatting_cli_function_pointer.yml
- tests/unit/test_generator_new_formatting_cli_alias_stereotype.yml
- tests/unit/test_generator_exact_format_cli_requested_format.yml
- tests/unit/test_generator_exact_format_cli_with_parameters.yml
→ tests/unit/test_generator_formatting_and_stereotypes_comprehensive.yml

- tests/unit/test_generator_naming_comprehensive_file_conventions.yml
- tests/unit/test_generator_naming_comprehensive_typedef_conventions.yml
- tests/unit/test_generator_naming_comprehensive_complex_names.yml
→ tests/unit/test_generator_naming_conventions_comprehensive.yml

- tests/unit/test_generator_grouping_cli_function_separation.yml
- tests/unit/test_generator_grouping_cli_global_separation.yml
- tests/unit/test_generator_grouping_cli_mixed_comprehensive.yml
→ tests/unit/test_generator_grouping_comprehensive.yml

- tests/unit/test_generator_visibility_logic_public_functions.yml
- tests/unit/test_generator_visibility_logic_private_functions.yml
- tests/unit/test_generator_visibility_logic_public_globals.yml
- tests/unit/test_generator_visibility_logic_no_headers.yml
- tests/unit/test_generator_visibility_logic_mixed_visibility.yml
→ tests/unit/test_generator_visibility_logic_comprehensive.yml

- tests/unit/test_generator_includes_comprehensive.yml
- tests/unit/test_include_filtering_comprehensive.yml
→ tests/unit/test_generator_includes_and_filtering_comprehensive.yml

Verifier
- tests/unit/test_verifier_valid_model.yml
- tests/unit/test_verifier_comprehensive.yml
→ tests/unit/test_verifier_comprehensive.yml (keep the comprehensive one and fold valid model checks into it)

Configuration
- tests/unit/test_config_comprehensive.yml → Keep (already comprehensive)

Feature: include processing workflows
- tests/feature/test_include_processing_basic_workflow.yml
- tests/feature/test_include_processing_comprehensive_scenario.yml
- tests/feature/test_include_processing_complex_project_structure.yml
- tests/feature/test_include_processing_c_to_h_relationships.yml
- tests/feature/test_include_processing_header_to_header_relationships.yml
- tests/feature/test_include_processing_transitive_dependencies.yml
- tests/feature/test_include_processing_include_depth_control.yml
- tests/feature/test_include_processing_nested_directory_structure.yml
- tests/feature/test_include_processing_dependency_ordering.yml
- tests/feature/test_include_processing_typedef_relationships.yml
- tests/feature/test_include_processing_macro_propagation.yml
- tests/feature/test_include_processing_missing_dependency_handling.yml
- tests/feature/test_include_processing_include_filtering.yml
- tests/feature/test_include_processing_full_pipeline_integration.yml
→ tests/feature/test_include_processing_comprehensive.yml
→ tests/feature/test_include_processing_error_handling_comprehensive.yml (collects negative/missing dependency and cycle/error cases)

Feature: component features
- tests/feature/test_component_features_comprehensive_generator_typedefs.yml
- tests/feature/test_component_features_comprehensive_unions.yml
- tests/feature/test_component_features_comprehensive_function_pointers.yml
- tests/feature/test_component_features_comprehensive_complex_typedefs.yml
- tests/feature/test_component_features_comprehensive_cross_file_dependencies.yml
- tests/feature/test_component_features_comprehensive_recursive_includes.yml
- tests/feature/test_component_features_comprehensive_project_structure.yml
- tests/feature/test_component_features_comprehensive_complex_relationships.yml
→ tests/feature/test_component_features_types_and_relationships_comprehensive.yml

Feature: CLI modes and features
- tests/feature/test_cli_modes_comprehensive_parse_mode.yml
- tests/feature/test_cli_modes_comprehensive_transform_mode.yml
- tests/feature/test_cli_modes_comprehensive_generate_prefers_transformed.yml
- tests/feature/test_cli_modes_comprehensive_generate_isolation.yml
- tests/feature/test_cli_modes_comprehensive_full_workflow.yml
- tests/feature/test_cli_modes_comprehensive_generate_fallback.yml
- tests/feature/test_cli_feature_comprehensive_parse_only.yml
- tests/feature/test_cli_feature_comprehensive_transform_only.yml
- tests/feature/test_cli_feature_comprehensive_generate_prefers_transformed.yml
- tests/feature/test_cli_feature_comprehensive_generate_isolation.yml
- tests/feature/test_cli_feature_comprehensive_generate_fallback.yml
→ tests/feature/test_cli_modes_and_features_comprehensive.yml

Integration
- tests/integration/test_comprehensive_parser_tokenizer_integration.yml
- tests/integration/test_comprehensive_header_to_header_relationships.yml
- tests/integration/test_comprehensive_c_to_h_relationships.yml
- tests/integration/test_comprehensive_typedef_relationships.yml
- tests/integration/test_new_formatting_comprehensive_complete_formatting_integration.yml
- tests/integration/test_new_formatting_comprehensive_mixed_project_comprehensive_formatting.yml
→ tests/integration/test_integration_relationships_and_formatting_comprehensive.yml

- tests/integration/test_comprehensive_complete_system_integration.yml → Keep (acts as the end-to-end golden path)

Example
- tests/example/test_basic_example.yml → Keep

---

Refactoring tasks per merged test (tracking)

Tokenizer/Preprocessor
- [x] tests/unit/test_tokenizer_comprehensive.yml
  - [x] Merge inputs/assertions from listed tokenizer YAMLs
  - [x] Remove old YAMLs and update `test_tokenizer*.py` callers
- [x] tests/unit/test_preprocessor_and_macros_comprehensive.yml
  - [x] Merge preprocessor + macro duplicate scenarios
  - [x] Remove old YAMLs and update Python tests

Parser
- [x] tests/unit/test_parser_functions_and_parameters_comprehensive.yml
- [x] tests/unit/test_struct_and_nested_ordering_comprehensive.yml
- [x] tests/unit/test_parser_includes_comprehensive.yml
- [ ] tests/unit/test_parser_elements_comprehensive.yml
- [ ] tests/unit/test_parser_typedefs_comprehensive.yml
- [ ] Confirm whether to keep `test_parser_encoding.yml` standalone or fold

Typedef extraction
- [x] tests/unit/test_typedef_extraction_comprehensive.yml

Anonymous structures
- [ ] tests/unit/test_anonymous_structures_and_unions_comprehensive.yml

Path/Include tree
- [ ] tests/unit/test_path_resolution_and_include_tree_comprehensive.yml

File-specific configuration
- [ ] tests/unit/test_file_specific_configuration_comprehensive.yml

Transformer
- [ ] tests/unit/test_transformer_comprehensive.yml

Generator
- [ ] tests/unit/test_generator_formatting_and_stereotypes_comprehensive.yml
- [ ] tests/unit/test_generator_naming_conventions_comprehensive.yml
- [ ] tests/unit/test_generator_grouping_comprehensive.yml
- [ ] tests/unit/test_generator_visibility_logic_comprehensive.yml
- [ ] tests/unit/test_generator_includes_and_filtering_comprehensive.yml

Verifier
- [ ] tests/unit/test_verifier_comprehensive.yml (fold valid model assertions)

Feature: include processing
- [ ] tests/feature/test_include_processing_comprehensive.yml
- [ ] tests/feature/test_include_processing_error_handling_comprehensive.yml

Feature: component features
- [ ] tests/feature/test_component_features_types_and_relationships_comprehensive.yml

Feature: CLI
- [ ] tests/feature/test_cli_modes_and_features_comprehensive.yml

Integration
- [ ] tests/integration/test_integration_relationships_and_formatting_comprehensive.yml
- [ ] Keep tests/integration/test_comprehensive_complete_system_integration.yml

De-duplication/renames
- [x] Unify `function_params_*` and `function_parameters_*` under the new functions/parameters comprehensive test
- [x] Remove overlapping unit vs feature duplicates (e.g., include filtering) by keeping the consolidated version in the most appropriate category (unit includes consolidated; feature workflows to be consolidated next)

Validation checklist
- [x] Run full suite after each merged YAML creation (update Python `self.run_test("<name>")` targets)
- [x] Ensure each merged YAML uses a single scenario with multi-assertions
- [x] Preserve IDs where feasible or reassign consistently per category ranges
- [ ] Update `tests/README.md` if naming or examples change
- [ ] Update CI if any path-based selection depends on old names

Notes
- Encoding-specific behaviors may warrant a dedicated YAML if not reliably covered by comprehensive tokenizer tests.
- Negative/error-path scenarios should remain separated where they materially change execution expectations (fail vs success).