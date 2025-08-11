# Test Enhancement TODO

Purpose: Track progress while cleaning up, enriching, and standardizing YAML-based tests.

## Completed (this pass)
- feature/test_201_cli_modes.yml
  - Replaced unsupported keys (cli_execution, should_succeed) with supported execution/model/puml assertions
  - Clarified description; added model validations (expected_files, functions_exist, includes_exist)
- feature/test_202_include_proc.yml
  - Removed unsupported keys; added comprehensive model assertions (functions/globals/includes)
  - Ensured files assertions check for model artifacts; kept syntax validation
- feature/test_203_comp_features.yml
  - Removed unsupported keys; added aliases_exist, unions/structs/functions checks; improved description
- integration/test_301_integration_rel_fmt.yml
  - Removed unsupported keys; added model checks for structs/enums/functions/includes; syntax validation
- unit/test_106_config.yml
  - Fixed invalid nesting; replaced unsupported execution key; added element counts and per-file PUML checks
  - Adjusted element_counts.functions from 3 to 9 to match actual parsed functions across headers and C file
- unit/test_121_verifier.yml
  - Replaced unsupported execution key; added expected_files and counts; ensured output files asserted
- unit/test_124_gen_newfmt.yml
  - Corrected PUML per-file assertion schema; added syntax_valid and contains_lines
- feature/test_204_errors_invalid_config.yml
  - Standardized failure assertions using success_expected/exit_code; refined description

## Observations
- Several YAMLs still use deprecated keys: should_succeed, cli_execution, success
- Many tests lack model.element_counts and PUML-level per-file assertions
- Some feature/integration tests could benefit from relationships_exist and class/relationship counts once generator patterns are stabilized

## Proposed assertion keys to use more broadly (from validators_processor)
- Execution
  - exit_code, max_execution_time, success_expected (only for explicit failure cases), stdout_contains/stderr_contains sparingly
- Model
  - validate_structure, project_name, expected_files, file_count
  - functions_exist / functions_not_exist
  - structs_exist / structs_not_exist
  - enums_exist / enums_not_exist
  - typedefs_exist / aliases_exist
  - globals_exist, macros_exist, includes_exist
  - element_counts: { files, functions, structs, enums, globals, includes, macros, unions, aliases }
  - struct_details: per-struct fields; enum_details: per-enum values
  - files: { <file>: { structs/enums/functions/globals/includes with details } }
- PlantUML
  - syntax_valid (global and per-file)
  - file_count (when deterministic)
  - contains_elements / not_contains_elements (global and per-file)
  - contains_lines / not_contains_lines (prefer per-file)
  - classes_exist: [{ name, stereotype }] for typed class checks
  - relationships_exist: [{ source, target, type }]
  - line_count, class_count, relationship_count (when stable)

## Targets to enrich next
- Add project_name, expected_files, file_count, and element_counts across more unit and feature tests
- Add per-file puml.files contains_lines with stable identifiers (class headers, function signatures)
- Introduce relationships_exist where generator output is stable (include relationships, compositions)
- Expand negative assertions: functions_not_exist / structs_not_exist in example and feature tests

## Next Up
- Review and standardize remaining files with deprecated keys:
  - unit/test_103_abs_path_relative.yml
  - unit/test_103_abs_path_subdir.yml
  - unit/test_103_abs_path_mixed.yml
  - unit/test_103_abs_path_consistency.yml
  - unit/test_103_abs_path_include_tree.yml
  - unit/test_107_debug_fields_*.yml
  - feature/test_202_include_proc_error.yml (add negative assertions)
  - unit/test_109_file_spec_cfg.yml
  - unit/test_110_gen_comp.yml (replace execution.success)
  - unit/test_111_gen_exact*.yml
- Enrich integration/test_301_integration_complete.yml with class_count/relationship_count when safe
- Add plantuml files assertions (files_exist and minimal contains_lines) to more feature tests

## Notes
- Prefer execution.exit_code or success_expected with expected_error for failures
- Prefer model.validate_structure + expected_files + specific existence checks over only syntax validation
- Use puml.syntax_valid and per-file contains_lines for the most stable diagram assertions

Last updated: 2025-08-11