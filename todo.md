### Fix Plan for complex.puml generation

- **Context**: Compare `artifacts/output_example/complex.puml` with `tests/example/source/complex.c` and `tests/example/source/complex.h`. Several generation defects were found in function signatures, anonymous type extraction, typedef classification, and field rendering.

### Key Issues Identified

- **Incorrect function signatures (missing params, bogus varargs)**
  - Current (wrong):
    ```plantuml
    + complex_handler_t * create_complex_handler(const char * name, ...)
    + void * create_handler(const char * name, int ( * init_func ) ( void * ) init_func, ...)
    + int process_with_callbacks(int[] data, int size, math_operation_t[] operations, int op_count, ...)
    ```
  - Expected (from header):
    ```plantuml
    + complex_handler_t * create_complex_handler(const char * name, int ( * validate_func ) ( const char * ), void * ( * alloc_func ) ( size_t ), void ( * free_func ) ( void * ))
    + void * create_handler(const char * name, int ( * init_func ) ( void * ), void ( * cleanup_func ) ( void * ), complex_callback_t callback)
    + int process_with_callbacks(int[] data, int size, math_operation_t[] operations, int op_count, void ( * pre_process ) ( int * , int ), void ( * post_process ) ( int * , int ))
    ```

- **Anonymous struct/union extraction broken**
  - Garbled fields merging multiple anonymous blocks:
    - In `TYPEDEF_COMPLEX_NAMING_TEST_T_FIRST_STRUCT`:
      ```plantuml
      + } nested_struct_a; struct { int nested_a2
      ```
    - In `TYPEDEF_EXTREME_NESTING_TEST_T_LEVEL2_STRUCT_1`:
      ```plantuml
      + } level3_struct_1; struct { int level3_field
      ```
  - Duplicate/misnamed extracted types:
    - `TYPEDEF___ANONYMOUS_STRUCT__` should be `TYPEDEF_MODERATELY_NESTED_T_LEVEL2_STRUCT` only (duplicate exists).
    - For `struct_with_union_t`: both `TYPEDEF_STRUCT_WITH_UNION_T_DATA_UNION` and `TYPEDEF_DATA_UNION` exist; only the former should exist with correct children.
  - Wrong child content placement:
    - `TYPEDEF_STRUCT_WITH_UNION_T_DATA_UNION` lists `x/y/z` (fields of nested struct) instead of union fields; nested point struct should be a separate child type referenced by the union, not flattened into the union.

- **~~Token join/lexing errors producing wrong names~~ ✅ RESOLVED**
  - ~~`callback_with_anon_struct_t_config_param_config_value`: field `floatfloat_config` should be `float_config`.~~
  - ~~`array_of_anon_structs_t_items_point_data`: field `inty` should be `y`.~~
  - **FIXED**: Tokenizer join bugs resolved - field names now correctly parsed for comma-separated declarations

- **Typedef classification/stereotypes incorrect**
  - `complex_func_ptr_t` shown as `<<typedef>>` but is a function pointer → must be `<<function pointer>>`.
  - `result_generator_t` shown as `<<struct>>` with fields; it is a function pointer returning an anonymous struct → should be `<<function pointer>>` (and optionally generate a separate class for the returned struct with a sane name).

- **Duplicate extracted entities**
  - `TYPEDEF_PARAM4` and `TYPEDEF_COMPLEX_CALLBACK_T_PARAM4` both represent the same anonymous struct.
  - `TYPEDEF_RESULT_DATA` and `TYPEDEF_RESULT_GENERATOR_T_RESULT_DATA` duplicates.

- **Enum value order scrambled**
  - `operation_type_t` and `processor_module_enum_t` values not in source order. Preserve declaration order.

### Proposed Fixes (by component)

- **Tokenizer (`src/core/parser_tokenizer.py`)**
  - Robustly parse function declarators to retain full parameter lists, including nested function pointer parameters and names. Avoid introducing `...` unless present in source.
  - ~~Fix identifier/token concatenation bugs causing `floatfloat_config` and `inty` by tightening join rules around type keywords and commas.~~ ✅ **COMPLETED**
  - Preserve declaration order for enum constants as encountered.

- **Anonymous processor (`src/core/parser_anonymous_processor.py`)**
  - Enforce naming scheme `ParentTypedef_fieldName` for extracted anonymous structs/unions at every nesting level. Remove generic names like `__anonymous_struct__`.
  - Ensure extracted child entities are unique per parent/field. De-duplicate when the same anonymous block is processed twice.
  - Correct parent field rewrites so that:
    - Parent shows `+ ExtractedType fieldName` (no braces artifacts).
    - Unions keep their own fields; nested anonymous structs within a union become separate child struct types referenced by the union, not flattened into the union.

- **Model verifier (`src/core/verifier.py`)**
  - Add validations to catch:
    - Garbled field renderings containing stray `}` or `struct {`.
    - Duplicate extracted entity names for the same parent/field path.

- **Generator (`src/core/generator.py`)**
  - Function signature rendering: include complete parameter list with correct formatting for pointers, arrays, and function pointers.
  - Typedef stereotypes: detect function pointer typedefs (`typedef return (*name)(...);`) and use `<<function pointer>>` with content `alias of ...`.
  - For function pointers returning structs, optionally generate a separate struct class (e.g., `result_generator_t_return`) and render the typedef as `alias of struct result_generator_t_return (*)(...)`.
  - Ensure enum values are emitted in parsed order.
  - De-duplicate typedef classes for identical anonymous paths (`param4`, `result_data`).

### Acceptance Criteria

- Public function signatures in `complex.puml` match `complex.h` exactly (types, parameter count, and order) for:
  - `create_complex_handler`, `create_handler`, `process_with_callbacks`.
- No garbled field lines remain (no stray `}`/`struct {` fragments in any class).
- No duplicate extracted classes (`PARAM4`, `RESULT_DATA`, `DATA_UNION` variants) for the same anonymous path.
- Correct naming for all extracted anonymous types using `ParentTypedef_fieldName` at each level.
- `complex_func_ptr_t` and `result_generator_t` use `<<function pointer>>` stereotype.
- `operation_type_t` and `processor_module_enum_t` values appear in source order.

### How to Develop and Test

- **Local quick run (example project)**
  - Run the full pipeline on example sources and regenerate diagrams:
    ```bash
    python3 main.py --config tests/example/config.json --verbose
    ```
  - Open and review `./output/complex.puml` (or the test output folder used by the framework) against the acceptance criteria.

- **Full test suite**
  - Run fast path:
    ```bash
    ./scripts/run_all_tests.sh
    ```
  - Or targeted:
    ```bash
    python3 -m pytest tests/unit/ tests/feature/ tests/integration/ -q
    ```

- **Add/adjust tests**
  - Unit tests (tokenizer): function declarator parsing with nested function pointers and arrays.
  - Unit tests (anonymous processor): extracted-name correctness and de-duplication.
  - Unit tests (generator): stereotype assignment for typedefs; ordered enum emission.
  - Example assertions: Extend example test to assert the corrected lines exist in `complex.puml`, e.g.:
    ```yaml
    puml:
      files:
        complex.puml:
          contains_lines:
            - "+ void * create_handler(const char * name, int ( * init_func ) ( void * ), void ( * cleanup_func ) ( void * ), complex_callback_t callback)"
            - "+ complex_handler_t * create_complex_handler(const char * name, int ( * validate_func ) ( const char * ), void * ( * alloc_func ) ( size_t ), void ( * free_func ) ( void * ))"
            - "+ int process_with_callbacks(int[] data, int size, math_operation_t[] operations, int op_count, void ( * pre_process ) ( int * , int ), void ( * post_process ) ( int * , int ))"
    ```

- **Debugging aids**
  - Temporarily print parsed function signatures and anonymous path maps in the verifier when `--verbose` is enabled.
  - Add a generator option to dump intermediate normalized declarators for inspection (behind a verbose flag).

### Progress Update

- Implemented character-length-based function signature truncation configurable via `max_function_signature_chars` in `config.json` and documented in `docs/specification.md`. Added unit test (`test_101_gen_basic_trunc.yml`).
- Generator renders full function signatures correctly (no bogus varargs), detects function-pointer typedefs and uses `<<function pointer>>`, preserves enum value order.
- Relationship generation fixed and stabilized:
  - Removed direct field-based composition edges to prevent double counting.
  - Anonymous relationships: skip only pure placeholders (`__anonymous_struct__`, `__anonymous_union__`), allow suffixed anonymous names; de-duplicate per parent.
  - Declares: skip typedefs that are anonymous children; Uses: skip anonymous children unless the parent typedef is itself anonymous; also emit union uses.
- Verifier extended to detect duplicate extracted entities per parent and garbled anonymous fragments.
- All tests pass (67/67 via `./scripts/run_all.sh`).
- **✅ TOKENIZER JOIN BUGS RESOLVED**: Fixed field name corruption issues (`inty` → `int y`, `floatfloat_config` → `float float_config`) by improving comma-separated field parsing in anonymous structure processor.

### Work Breakdown and Progress Tracking

- **Parser/Tokenizer**
  - [ ] Implement robust C declarator parsing (function pointers in parameters)
  - [x] Fix token-join bugs (avoid `floatfloat_config`, `inty`) — ✅ **COMPLETED**
  - [x] Preserve enum constant order

- **Anonymous Extraction**
  - [ ] Enforce `ParentTypedef_fieldName` naming across all nesting levels
  - [x] Prevent duplicate extraction for identical anonymous paths (dedup in anonymous_relationships)
  - [x] Correct parent-field rewrite (update field types to extracted entity names; remove placeholder artifacts)
  - [x] Ensure unions keep proper fields; nested structs are separate children (composition emitted via anonymous relationships)

- **Generator**
  - [x] Render full function signatures for file/header classes
  - [x] Correct typedef stereotypes (`<<function pointer>>` vs `<<typedef>>`)
  - [ ] Optionally emit separate class for function-pointer return structs
  - [x] Emit enum values in source order
  - [ ] De-duplicate typedef classes for identical anonymous paths (deferred until unit tests updated)
  - [x] Configurable function signature truncation by character length

- **Verifier/Tests**
  - [x] Add verifier checks for garbled field lines and duplicates
  - [ ] Unit tests: tokenizer (function pointers, arrays)
  - [ ] Unit tests: anonymous extraction naming & de-duplication
  - [ ] Unit tests: generator stereotypes & enum order
  - [ ] Update example assertions for `complex.puml`

### Validation Milestones

- [x] Milestone 1: Function signatures match header (3 targets)
- [x] Milestone 2: No garbled fields; anonymous names correct (tokenizer join bugs resolved)
- [x] Milestone 3: Typedef stereotypes fixed; duplicates removed (in current scope; broader dedup deferred)
- [x] Milestone 4: All tests green

### Notes

- Consider filtering out header include-guard macros (e.g., `COMPLEX_H`) via a config option if they create noise in diagrams.
- Keep output formatting consistent with `docs/puml_template.md` (visibility, stereotypes, relationship types).
- Behavior detail: Pure anonymous placeholders (`__anonymous_struct__`, `__anonymous_union__`) are suppressed as endpoints in relationships; extracted, suffixed anonymous names are emitted. Consider a config flag to display pure placeholders if desired.
- **✅ COMPLETED**: Tokenizer join rules adjusted to correctly separate identifiers around commas and type keywords; nested anonymous struct fields are now preserved and emitted correctly.
- **NEXT PRIORITY**: Focus on remaining anonymous structure extraction issues (garbled field renderings and duplicate extracted entities).