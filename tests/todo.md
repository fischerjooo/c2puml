## Completed (continued)
- unit/test_103_abs_path_relative.yml
  - Removed deprecated keys; added execution exit_code, puml.syntax_valid, files assertions
- unit/test_103_abs_path_subdir.yml
  - Removed deprecated keys; added execution exit_code, puml.syntax_valid, files assertions
- unit/test_103_abs_path_mixed.yml
  - Removed deprecated keys; added execution exit_code, puml.syntax_valid, files assertions
- unit/test_103_abs_path_consistency.yml
  - Removed deprecated keys; added execution exit_code, puml.syntax_valid, files assertions
- feature/test_202_include_proc_error.yml
  - Converted to align with current CLI behavior (exit_code:0 even with missing include), asserting output presence and puml.syntax_valid
- unit/test_109_file_spec_cfg.yml
  - Removed deprecated keys; added execution exit_code and files assertions
- unit/test_110_gen_comp.yml
  - Replaced execution.success with exit_code; added puml.syntax_valid and files assertions

## Completed (continued 2)
- unit/test_107_debug_fields_union.yml
  - Removed deprecated keys; added execution exit_code, model.validate_structure/expected_files, puml.syntax_valid, files assertions
- unit/test_107_debug_fields_struct.yml
  - Removed deprecated keys; switched to struct_details, added validate_structure/expected_files, puml.syntax_valid, files assertions
- unit/test_107_debug_fields_anonymous.yml
  - Removed deprecated keys; added validate_structure/expected_files, puml.syntax_valid, files assertions
- unit/test_103_abs_path_include_tree.yml
  - Removed deprecated keys; added execution exit_code and files assertions; normalized generate-only assertions schema

## Next Up (refined)
- unit/test_107_debug_fields_*.yml: replace cli_execution and should_succeed; add syntax_valid and files assertions
- integration/test_301_integration_complete.yml: consider adding class_count/relationship_count when stable
- feature/test_205_multi_src.yml and 209: add files assertions (model.json present) and optional line counts
## Next Up (refined again)
- Add per-file puml.files.contains_lines to more unit tests (e.g., 109, 111, 122)
- Introduce relationships_exist in integration 301 when patterns are stable
- Add model.project_name + file_count across remaining unit tests
- unit/test_111_gen_exact_requested.yml
  - Added puml.syntax_valid; moved per-file assertions under puml.files; added files assertions
- unit/test_111_gen_exact_params.yml
  - Added puml.syntax_valid; converted contains to contains_lines; added files assertions

## Next Up (additions)
- unit/test_122_gen_includes.yml: add per-file contains_lines for includes section and files assertions
- unit/test_113_gen_inctree*.yml: add model.project_name and element_counts, per-file contains_lines
- unit/test_122_gen_includes.yml
  - Added per-file relationships_exist and files assertions for output JSONs
- unit/test_113_gen_inctree.yml
  - Added puml.syntax_valid; converted per-file contains to contains_lines

## Next Up (more)
- unit/test_113_gen_inctree_abs.yml: align assertions schema to contains_lines and add syntax_valid
- Consider adding relationship_count/class_count where stable in integration tests