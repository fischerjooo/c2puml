# Test Naming Convention Migration Plan

## Goal
Adopt the new test naming scheme and keep Python/YAML pairs consistent:
- Python tests: `test_<3-digit>_<short-name>.py`
- YAML tests: `test_<3-digit>_<short-name>.yml`
- Optional: multiple YAMLs for a single Python test use suffixes:
  - `test_<3-digit>_<short-name>_<suffix>.yml`
- Requirement: the `test_<3-digit>_` prefix must be identical between a `.py` and all `.yml` files it uses.

## Scope
- Update documentation (`tests/README.md`, `tests/framework/README.md`) to reflect new conventions.
- Migrate existing tests incrementally, ensuring each migrated Python test’s `run_test`/`load_test_data` calls match the new base id (`<3-digit>_<short-name>` and optional suffix).
- Keep directory categories (`tests/unit`, `tests/feature`, `tests/integration`, `tests/example`).

## Rules
- 3-digit id: choose unique values across the whole test suite to avoid cross-category ambiguity.
- Short name: 1–2 words max, concise and meaningful.
- For multi-YAML scenarios driven by a single `.py`, use suffix only in YAML and the `test_id` passed from Python:
  - Python file: `test_202_include_proc.py`
  - YAML files: `test_202_include_proc.yml`, `test_202_include_proc_error.yml`
  - Python calls: `self.run_test("202_include_proc")`, `self.run_test("202_include_proc_error")`

## Migration Steps
1. Update documentation to describe the new convention and examples.
2. Convert tests in small batches, updating both file names and internal `test_id` references.
3. Run test suite after each batch.
4. Track progress here.

## Batch 1 (initial conversions)
- tests/unit:
  - [x] `test_generator_basic_plantuml` → id 101, short `gen_basic`
    - [x] Rename `.py` to `test_101_gen_basic.py`
    - [x] Rename `.yml` to `test_101_gen_basic.yml`
    - [x] Update `run_test("101_gen_basic")`
  - [x] `test_transformer_basic` → id 102, short `trans_basic`
    - [x] Rename `.py` to `test_102_trans_basic.py`
    - [x] Rename `.yml` to `test_102_trans_basic.yml`
    - [x] Update `run_test("102_trans_basic")`
- tests/feature:
  - [x] `test_cli_modes_comprehensive` → id 201, short `cli_modes`
    - [x] Rename `.py` to `test_201_cli_modes.py`
    - [x] Rename `.yml` to `test_201_cli_modes.yml`
    - [x] Update `run_test("201_cli_modes")`
  - [x] `test_include_processing` (multi-YAML) → id 202, short `include_proc`
    - [x] Rename `.py` to `test_202_include_proc.py`
    - [x] Rename YAMLs:
      - `test_include_processing_comprehensive.yml` → `test_202_include_proc.yml`
      - `test_include_processing_error_handling_comprehensive.yml` → `test_202_include_proc_error.yml`
    - [x] Update Python calls to `"202_include_proc"` and `"202_include_proc_error"`
- tests/example:
  - [x] `test_basic_example` → id 901, short `basic_example`
    - [x] Rename `.py` to `test_901_basic_example.py`
    - [x] Rename `.yml` to `test_901_basic_example.yml`
    - [x] Update `load_test_data("901_basic_example")`

## Batch 2 (planned)
- tests/feature:
  - `test_error_handling_comprehensive` (3 YAMLs) → propose id 203, short `errors`
    - YAML suffixes: `_invalid_source`, `_invalid_config`, `_partial`
- tests/integration:
  - `test_comprehensive.py` (2 YAMLs) → propose id 301, short `integr`
    - YAML suffixes: `_relationships_formatting`, `_complete_system`
  - `test_new_formatting_comprehensive.py` → consider folding into the above (single scenario)

## Batch 3 (unit consolidations)
- Migrate remaining unit tests progressively (tokenizer, parser, generator, typedefs, includes), assigning unique ids and short names.

## Post-Migration
- Verify all docs reflect the new scheme.
- Ensure `tests/framework/data_loader.py` continues to resolve `test_id` by filename pattern `tests/<category>/test_<id>.yml`.
- Confirm CI green.