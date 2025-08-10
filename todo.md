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
  - Scenarios: `parse_only`, `transform_only`, `generate_only`, `generate_prefers_transformed`, `generate_fallback`, `full_workflow`
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

- **Unit: Parser Functions Comprehensive**
  - Merge into `tests/unit/test_parser_functions_comprehensive.yml` (TBD)

- **Unit: Typedef Extraction**
  - Merge into `tests/unit/test_typedef_extraction_comprehensive.yml` (TBD)

- **Unit: Absolute Path Bug**
  - Merge into `tests/unit/test_absolute_path_bug_comprehensive.yml` (TBD)

- **Unit: Tokenizer**
  - Merge into `tests/unit/test_tokenizer_comprehensive.yml` (DONE)

- **Unit: Debug and Anonymous Structures**
  - Merge into `tests/unit/test_anonymous_structures_and_debug.yml` (TBD)

- **Unit: Generator Naming & Grouping & New Formatting**
  - Merge naming into `tests/unit/test_generator_naming_comprehensive.yml` (DONE)
  - Merge grouping into `tests/unit/test_generator_grouping_cli.yml` (TBD)
  - Merge new formatting into `tests/unit/test_generator_new_formatting_cli.yml` (TBD)

- **Unit: Transformer**
  - Merge into `tests/unit/test_transformer_comprehensive.yml` (DONE)

- **Unit: File-specific Configuration**
  - Merge into `tests/unit/test_file_specific_configuration_comprehensive.yml` (DONE)

- **Integration: Comprehensive**
  - Merge into `tests/integration/test_comprehensive.yml` (TBD)


### Estimated Impact

- Reduce from ~156 YAML files to ~18–24 bundled YAML files.
- Maintain or increase coverage by collecting related assertions in one place per domain.
- Faster local development (fewer file hops), clearer ownership per domain, simpler reviews.


### Framework Changes Required (Phase 1)

- [x] Extend `tests/framework/data_loader.py` to support multi-scenario files:
  - [x] Accept a top-level `scenarios: []` array.
  - [x] Each scenario allows its own `test`, `source_files`, `config.json`, optional `model.json`, and `assertions` blocks.
  - [x] Backward compatibility: If `scenarios` is absent, treat file as single-scenario (current behavior).
  - [x] Expose loader entrypoint `load_test_data("<bundle>::<scenario>")` to return the selected scenario.
- [x] Update `tests/framework/base.py`:
  - [x] Add `run_test("<bundle>::<scenario>")` parsing and stable folder naming.
  - [x] Ensure validation loads the correct scenario assertions.
- [x] Update docs `tests/README.md` and `tests/framework/README.md`:
  - [x] Document new `scenarios` schema with examples.
  - [x] Document `bundle::scenario` naming in Python tests.


### Migration Plan (Phase 2)

- [x] Create bundled YAML for CLI modes and update Python.
- [x] Create bundled YAML for Include Processing and update Python.
- [x] Create bundled YAML for Tokenizer and update Python.
- [x] Create bundled YAML for Transformer and update Python.
- [x] Create bundled YAML for File-specific Configuration and update Python.
- [x] Create bundled YAML for Generator Visibility Logic and update Python.
- [x] Create bundled YAML for Generator Naming and update Python.
- [ ] Consolidate remaining unit bundles (parser functions, typedef extraction, absolute path bug, anonymous structures, grouping, new formatting) and integration comprehensive.
- [ ] Move old single-scenario YAMLs under `tests/_deprecated/` temporarily (final removal after CI green).


### Status

- All new bundles pass: `python3 -m unittest -q` → OK.
- Framework supports per-scenario execution modes and correct setup for parse/transform/generate/full.
- Documentation updated.
- Completed additional consolidations:
  - Parser functions → `tests/unit/test_parser_functions_comprehensive.yml` + refactor.
  - Kept suite green (now 157 tests executed via unittest discovery).


### Next Steps

- Complete remaining consolidations (typedef extraction, absolute path bug, anonymous structures, grouping, new formatting) and integration comprehensive.
- Deprecate and remove old single-scenario YAMLs after validating coverage parity.