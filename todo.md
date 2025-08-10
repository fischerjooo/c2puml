### Test Suite Consolidation Report and Plan


- **Goal**: Reduce test file count while keeping functional and scenario coverage intact. Improve maintainability and execution speed by consolidating closely related scenarios into fewer, structured scenario bundles.


### Current Test Inventory (YAML-driven tests)

- **Unit (`tests/unit/`)**: 105 YAML files
- **Feature (`tests/feature/`)**: 43 YAML files
- **Integration (`tests/integration/`)**: 7 YAML files
- **Example (`tests/example/`)**: 1 YAML file
- **Total**: 156 YAML scenario files (plus Python wrappers)


### Findings and Overlap Analysis

- **Include processing (feature)**: Many single-scenario YAMLs (`include_processing_*`) that collectively test workflow, depth, filtering, transitive deps, dependency ordering, circular detection, typedefs across files, macro propagation, and a comprehensive scenario. These can be bundled.
- **CLI modes (feature)**: Multiple mode-specific YAMLs (parse-only, transform-only, generate-only, isolation/prefers-transformed/fallback, full workflow) with identical structure differing only by assertions.
- **Generator visibility logic (unit)**: Separate YAMLs for public/private functions/globals, mixed visibility, and "no headers"; structurally similar, differing in model and expected UML lines.
- **Parser function comprehensive (unit)**: Declarations/definitions/modifiers split across separate YAMLs that can be combined.
- **Typedef extraction (unit)**: Multiple YAMLs for simple/structs/enums/unions/function pointers/mixed/edge cases; ideal for bundling.
- **Absolute path bug (unit)**: Relative path, subdirectory, mixed paths, consistency variations of the same concern.
- **Tokenizer comprehensive (unit)**: Complex parsing, edge cases, preprocessor cases, complex mixed structures; strong bundling candidates with scenario tags.
- **Debug/anonymous structures (unit)**: Anonymous structure/union processing and debug parsing appear across multiple focused YAMLs.
- **Generator naming/grouping/new-formatting (unit)**: Multiple narrowly focused YAMLs under the same concern (naming conventions; grouping; new formatting stereotypes) can be merged to reduce boilerplate.
- **Integration comprehensive (integration)**: Multiple comprehensive end-to-end tests with strong thematic overlap.


### Consolidation Strategy

- **Non-invasive Phase (recommended first)**: Introduce a "multi-scenario in one YAML" capability to the test framework, preserving backward compatibility. A single consolidated YAML file can contain multiple independent scenarios (each with its own `test`, `source_files`, `config.json`, optional `model.json`, and `assertions`).
  - Back-compat: Existing single-scenario YAMLs continue to work unchanged.
  - New capability: A new top-level `scenarios` array is supported. Or alternatively, support multiple scenarios via a schema like:
    - `tests/<category>/test_<bundle_name>.yml` with structure:
      - `scenarios:
        - id: "scenario_a"
          test: {...}
          source_files: {...}
          config.json: "..."
          assertions: {...}
        - id: "scenario_b"
          ...`
  - Runner ergonomics: Allow `run_test("<bundle_name>::scenario_a")` for targeted runs. Provide `run_all_scenarios("<bundle_name>")` helper if needed.

- **Migration Phase**: Merge thematically similar single-scenario YAMLs into bundled files using the new schema. Keep 1 Python test module per theme that calls each scenario by id.


### Target Bundles (Proposed)

- **Feature: Include Processing**
  - Merge into `tests/feature/test_include_processing.yml`
  - Scenarios: `basic_workflow`, `c_to_h_relationships`, `header_to_header_relationships`, `complex_project_structure`, `nested_directory_structure`, `circular_include_detection`, `full_pipeline_integration`, `include_depth_control`, `include_filtering`, `transitive_dependencies`, `dependency_ordering`, `missing_dependency_handling`, `comprehensive_scenario`, `typedef_relationships`, `macro_propagation`
  - Expected reduction: 15 → 1 file

- **Feature: CLI Modes**
  - Merge into `tests/feature/test_cli_modes_comprehensive.yml`
  - Scenarios: `parse_only`, `transform_only`, `generate_only`, `generate_isolation`, `generate_prefers_transformed`, `generate_fallback`, `parse_mode`, `transform_mode`, `full_workflow`
  - Expected reduction: 9 → 1 file

- **Feature: Component Features**
  - Merge into `tests/feature/test_component_features_comprehensive.yml`
  - Scenarios: `project_structure`, `cross_file_dependencies`, `recursive_includes`, `complex_typedefs`, `function_pointers`, `generator_typedefs`, `generator_unions`, `unions`
  - Expected reduction: 8 → 1 file

- **Feature: Crypto Filter**
  - Merge into `tests/feature/test_crypto_filter_comprehensive.yml`
  - Scenarios: `pattern_functionality`, `usecase_functionality`
  - Expected reduction: 2 → 1 file

- **Feature: Multiple Source Folders**
  - Merge `.py` and `.yml` into single bundle `tests/feature/test_multiple_source_folders.yml` with scenarios matching current coverage
  - Expected reduction: 2 → 1 file

- **Unit: Generator Visibility Logic**
  - Merge into `tests/unit/test_generator_visibility_logic.yml`
  - Scenarios: `public_functions`, `private_functions`, `public_globals`, `private_globals`, `mixed_visibility`, `no_headers`
  - Expected reduction: 6 → 1 file

- **Unit: Parser Functions Comprehensive**
  - Merge into `tests/unit/test_parser_functions_comprehensive.yml`
  - Scenarios: `declarations`, `definitions`, `modifiers`, and keep minimal `functions` coverage
  - Expected reduction: 4 → 1 file

- **Unit: Typedef Extraction**
  - Merge into `tests/unit/test_typedef_extraction_comprehensive.yml`
  - Scenarios: `simple`, `structs`, `enums`, `unions`, `function_pointers`, `mixed`, `edge_cases`
  - Expected reduction: 7 → 1 file

- **Unit: Absolute Path Bug**
  - Merge into `tests/unit/test_absolute_path_bug_comprehensive.yml`
  - Scenarios: `relative_path`, `subdirectory`, `mixed_paths`, `consistency`
  - Expected reduction: 4 → 1 file

- **Unit: Tokenizer**
  - Merge into `tests/unit/test_tokenizer_comprehensive.yml`
  - Scenarios: `complex_parsing`, `edge_cases`, `preprocessor`, `keywords`, `complex_function_parsing`, `complex_mixed_structures`, `comprehensive_parsing`
  - Expected reduction: 7+ → 1 file

- **Unit: Debug and Anonymous Structures**
  - Merge into `tests/unit/test_anonymous_structures_and_debug.yml`
  - Scenarios: `anonymous_processing`, `anonymous_struct`, `anonymous_union`, `nested_anonymous`, `debug_parsing_struct`, `debug_parsing_union`, `debug_parsing_anonymous`, `debug_field_parsing_struct`, `debug_field_parsing_union`, `debug_field_parsing_anonymous`
  - Expected reduction: 9+ → 1 file

- **Unit: Generator Naming & Grouping & New Formatting**
  - Merge naming into `tests/unit/test_generator_naming_comprehensive.yml` (scenarios: `typedef_conventions`, `file_conventions`, `complex_names`, `edge_cases`)
  - Merge grouping into `tests/unit/test_generator_grouping_cli.yml` (scenarios: `function_separation`, `global_separation`, `mixed_comprehensive`)
  - Merge new formatting into `tests/unit/test_generator_new_formatting_cli.yml` (scenarios: `enum_stereotype`, `struct_stereotype`, `union_stereotype`, `function_pointer`, `alias`, `complex_typedef`)
  - Expected reduction: 6+ → 3 files

- **Unit: Transformer**
  - Merge into `tests/unit/test_transformer_comprehensive.yml` (scenarios: `basic`, `operations`, `filtering`, `includes`)
  - Expected reduction: 4 → 1 file

- **Unit: File-specific Configuration**
  - Merge into `tests/unit/test_file_specific_configuration_comprehensive.yml` (scenarios: `patterns`, `filter`, `depth`, `extraction`)
  - Expected reduction: 4 → 1 file

- **Integration: Comprehensive**
  - Merge into `tests/integration/test_comprehensive.yml`
  - Scenarios: `c_to_h_relationships`, `header_to_header_relationships`, `typedef_relationships`, `parser_tokenizer_integration`, `complete_system_integration`, `new_formatting_complete`, `new_formatting_mixed_project`
  - Expected reduction: 7 → 1 file


### Estimated Impact

- Reduce from ~156 YAML files to ~18–24 bundled YAML files.
- Maintain or increase coverage by collecting related assertions in one place per domain.
- Faster local development (fewer file hops), clearer ownership per domain, simpler reviews.


### Framework Changes Required (Phase 1)

- [ ] Extend `tests/framework/data_loader.py` to support multi-scenario files:
  - [ ] Accept a top-level `scenarios: []` array.
  - [ ] Each scenario allows its own `test`, `source_files`, `config.json`, optional `model.json`, and `assertions` blocks.
  - [ ] Backward compatibility: If `scenarios` is absent, treat file as single-scenario (current behavior).
  - [ ] Expose loader entrypoint `load_test_data("<bundle>::<scenario>")` to return the selected scenario.
- [ ] Update `tests/framework/base.py`:
  - [ ] Add `run_test("<bundle>::<scenario>")` parsing.
  - [ ] Add helper `run_all_scenarios("<bundle>")` (optional) to iterate scenarios for smoke runs.
- [ ] Update `tests/framework/validators_processor.py` and `validators.py`:
  - [ ] No schema changes needed; ensure input is routed per scenario.
- [ ] Update docs `tests/README.md` and `tests/framework/README.md`:
  - [ ] Document new `scenarios` schema with examples.
  - [ ] Document `bundle::scenario` naming in Python tests.


### Migration Plan (Phase 2)

- [ ] Create new bundled YAMLs per the Target Bundles above (start with high-churn domains)
  - [ ] Include all existing assertions to preserve coverage.
  - [ ] Normalize IDs: use `id` per scenario (e.g., `1014_full_workflow`).
- [ ] Update Python test modules to call `run_test("<bundle>::<scenario>")` for each scenario.
- [ ] Mark old single-scenario YAMLs as deprecated in a `tests/_deprecated/` folder for one release cycle.
- [ ] Remove deprecated YAMLs once CI is green and coverage is stable.


### Risk Mitigation

- Keep a 1:1 mapping from old scenarios to new scenario IDs and maintain a temporary index mapping for quick lookup.
- Validate equivalence by running both old and new suites in CI during a transition branch; compare counts and key assertions.
- Ensure deterministic temp folder naming includes both bundle and scenario to avoid collisions.


### Quick Wins (No Framework Change, Optional)

If framework changes are postponed, we can still reduce noise by:
- [ ] Collapsing multiple Python test modules into one per domain (already done in many places like `tests/feature/test_include_processing.py`).
- [ ] Removing narrow tests fully covered by comprehensive scenarios (only if entirely redundant):
  - [ ] Example: feature include `basic_workflow`, `include_depth_control` potentially covered by `comprehensive_scenario` and `full_pipeline_integration`.
  - [ ] Keep at least one narrow sanity test per domain as a smoke check.


### Acceptance Criteria

- [ ] CI green after framework extension (no test regressions).
- [ ] 50% reduction in YAML file count in first pass; 80–90% after full migration.
- [ ] Documentation updated with clear examples for multi-scenario YAMLs.
- [ ] Developers can run a whole domain with a single bundled YAML, or target a specific scenario via `bundle::scenario`.


### Appendix: Example Multi-Scenario YAML Sketch

```yaml
# tests/feature/test_cli_modes_comprehensive.yml
scenarios:
  - id: "parse_only"
    test:
      name: "CLI parse-only"
      category: "feature"
      id: "1010"
    source_files:
      main.c: |
        int main(){return 0;}
    config.json: |
      { "project_name": "cli_parse", "source_folders": ["."], "output_dir": "./output" }
    assertions:
      execution:
        exit_code: 0
      puml:
        file_count: 1
  - id: "transform_only"
    test: {...}
    source_files: {...}
    config.json: |
      { "project_name": "cli_transform", ... }
    assertions: {...}
```