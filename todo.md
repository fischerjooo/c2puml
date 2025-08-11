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

Last updated: YYYY-MM-DD