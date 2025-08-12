# c2puml core refactoring and cleanup plan

This plan targets `src/c2puml/core` to simplify internals, fix concrete bugs, and remove duplication while keeping the current public behavior intact. Validate after each step with `./scripts/run_all.sh` and keep commits small.

## Quick wins (bug fixes)
- [ ] Generator: fix anonymous composition UML ID resolution
  - Current `_get_anonymous_uml_id` looks up keys like `typedef_{name.lower()}` or `struct_{name.lower()}` that are never populated; `uml_ids` uses `typedef_{OriginalCase}` keys.
  - Change lookup to try in order: `typedef_{name}`, `typedef_{name.capitalize/exact-case variants}` and finally normalize both sides consistently (e.g., store and look up with exact typedef name). Remove unused `struct_*/union_*` lookups.
- [ ] Transformer: preserve macro parameters when renaming macros
  - `_rename_macros` currently returns only the renamed macro name (drops `(args)`), breaking function-like macros. Keep the original parameter list when present.
- [ ] Transformer: update `include_relations` when files are renamed
  - `_rename_files` updates `file_model.name` and the `files` dict keys, but existing `include_relations` entries still carry old `source_file`/`included_file` names. Add a pass to rewrite both sides after file renaming.
- [ ] Transformer: convert `includes` to `set`
  - `_dict_to_file_model` passes a list to `FileModel.includes` which is a `Set[str]`. Convert via `set(data.get("includes", []))` for consistency and deterministic deduplication.
- [ ] Use `ProjectModel.from_dict`/`load` in transformer
  - Replace manual reconstruction in `_load_model` with `ProjectModel.load(model_file)` to reduce drift.

## Remove duplication and simplify control flow
- [ ] Consolidate include processing in transformer
  - Keep one BFS-style implementation (e.g., `_process_root_c_file_includes`) that:
    - Runs per-root `.c` file
    - Applies `include_filter` and `include_depth` (global + file-specific)
    - Populates `include_relations` only on root `.c` files
  - Remove older/duplicate flows: `_process_include_relations` (recursive variant), `_process_single_file_include_relations`, `_process_include_relations_with_file_specific_settings`, and helper `_find_included_file` if no longer used.
  - Ensure a single entry point (e.g., `_process_include_relations_simplified`).
- [ ] Unify include filtering helpers
  - Merge `_filter_file_includes` and `_filter_file_includes_comprehensive` into a single method with a boolean flag if needed; both preserve `includes` and only filter `include_relations`.
- [ ] Remove legacy transformation API
  - Drop `_apply_model_transformations` in favor of containerized `_apply_transformation_containers`. Keep a small adapter only for backward compatibility (`_ensure_backward_compatibility`) and delete dead code paths.
- [ ] Deduplicate class generation in generator
  - Merge `_generate_file_class_with_visibility` and `_generate_file_class` into a single method parameterized by: `class_type`, `color`, visibility strategy (static `+` for headers, dynamic lookup for `.c`).

## Consistency and API surface
- [ ] Normalize model file keys and names
  - Parser already uses filename (not path) as `ProjectModel.files` keys and `FileModel.name`. Ensure transformer/generator do not reintroduce path keys. Add a small validator in verifier for this invariant.
- [ ] Regex compilation and reuse
  - Centralize `_compile_patterns` and reuse precompiled patterns across rename/remove operations to avoid recompilation.
- [ ] Exceptions hygiene
  - Replace broad `except Exception` with specific exceptions; rethrow with context.

## Tests to add (before/along changes)
- [ ] Anonymous composition relationships render
  - Given `anonymous_relationships` in a model, verify generator produces `TYPEDEF_PARENT *-- TYPEDEF_PARENT_FIELD : <<contains>>` using the correct UML IDs.
- [ ] Macro renaming preserves parameters
  - Input macros include `MAX(a,b)`; apply rename; output keeps `(a,b)` intact.
- [ ] File rename propagates to include_relations
  - After renaming `old.c`→`new.c`, relations reference `new.c` on both ends where appropriate.
- [ ] Single include processing path
  - With `include_depth` > 1 and `file_specific.include_filter`, verify only one include path is used and results are stable.
- [ ] Includes type is a set
  - Ensure `includes` is serialized/deserialized as a set-equivalent (round-trips), and generation order is deterministic via sorting when emitting.

## Step-by-step refactor sequence (validate with ./scripts/run_all.sh)
1) Apply “quick wins” fixes (anonymous UML IDs, macro rename parameters, include_relations on file rename, includes as set, transformer `load` via ProjectModel).
2) Write tests for these behaviors; run `./scripts/run_all.sh`.
3) Consolidate include processing to a single BFS; remove duplicates; keep names stable. Tests green.
4) Unify include filtering helpers; tests green.
5) Remove legacy transformation entry, keep compatibility adapter; tests green.
6) Merge generator class emission methods into one; tests green.
7) Exceptions hygiene and small verifier invariant for filename keys; tests green.

## Follow-ups and housekeeping
- [ ] Document the simplified include processing and configuration behavior in `docs/specification.md` (mark legacy notes as deprecated).
- [ ] Add a short developer guide snippet in `README.md` about where include processing lives (transformer only) and how visibility is determined in generator.
- [ ] Consider a feature flag `"debug.verbose_include_processing"` for extra logs gated behind `--verbose`.

### Artifact verification (CI/runtime)
- [ ] After running the full workflow (`./scripts/run_all.sh` or `./run_runall.sh`), verify that `artifacts/output_example` contains all generated outputs:
  - Required PUML/PNG pairs: `application`, `complex`, `database`, `geometry`, `logger`, `math_utils`, `network`, `preprocessed`, `sample`, `sample2`, `transformed`, `typedef_test`
  - Required files: `model.json`, `model_transformed.json`, `diagram_index.html`
  - Exit with non-zero status if any are missing to fail CI early

## Notes
- Overall structure (parser → transformer → generator) remains; we reduce inner duplication and make behavior predictable.
- Always verify via:
  - Linux/macOS: `./scripts/run_all.sh`
  - Or tests only: `./scripts/run_all_tests.sh`

## Additional improvements and simplifications
- [ ] Generator: remove dead/unused code
  - Delete `_is_truncated_typedef`, `_handle_truncated_typedef`, `_handle_normal_alias` and the disabled anonymous flattening block; they are not invoked.
- [ ] Generator: align composition label with template
  - Use `: contains` (no guillemets) for anonymous composition to match `docs/puml_template.md`.
- [ ] Generator: simplify API and fallback
  - Drop `include_depth` parameter from public methods; rely on transformer-populated `include_relations`. Keep a minimal fallback that ignores depth and just links direct includes when no relations exist.
- [ ] Generator: precompute visibility maps
  - Build a set/map of header-declared function and global names once per diagram to avoid O(N^2) scans in `_get_visibility_prefix_for_*`.

- [ ] Transformer: unify type-reference cleanup
  - Keep a single cleanup path based on explicit removed typedef names and delete the pattern-based variant. Route both callers through one implementation.
- [ ] Transformer: standardize macro representation
  - Treat macros as names only (e.g., `PI`, `MIN(a,b)`), never strings starting with `#define`. Update rename logic to avoid injecting `#define` into the list.
- [ ] Transformer: remove unused include helpers
  - Delete `_find_included_file` and the older recursive include functions once the single BFS path is the only implementation.
- [ ] Transformer: add helpers for file type checks
  - Introduce `is_c_file(name: str)` and `is_header_file(name: str)` to replace repeated `.endswith(".c")` and `.endswith(".h")` checks.

- [ ] Parser: detect duplicate basenames across input
  - Since the model keys are filenames, detect duplicates during parsing and fail fast with a clear error listing colliding paths.

- [ ] Config: simplify initialization
  - Replace the custom `__init__` with dataclass defaults and a `from_dict()` constructor; trim the `hasattr` scaffolding and keep `_compile_patterns()` in `__post_init__`.

- [ ] Verifier: strengthen invariants
  - Add checks for unique filename keys, consistent `FileModel.name`, and that only root `.c` files carry `include_relations` (others empty), if we enforce that invariant after include consolidation.

- [ ] Logging hygiene
  - Demote noisy `info` logs in inner loops to `debug`. Keep high-level progress at `info`.

- [ ] Regex caching
  - Precompile and cache regex patterns per transformation container to avoid recompilation in each inner loop.

## More tests to add
- [ ] Duplicate filename detection
  - Two files named `util.c` in different folders should raise a clear error from parser.
- [ ] Macro representation standardization
  - After parsing and renaming, macros remain names (`PI`, `MAX(a,b)`), generator renders `#define` lines correctly.
- [ ] Composition label style
  - Generated PUML contains `*--` relations with `: contains` (no guillemets).
- [ ] Visibility precompute correctness
  - With headers declaring a subset of functions/globals, generator groups `+` and `-` correctly using the precomputed maps.
- [ ] Generator API change safety
  - Public `generate()` ignores/omits `include_depth` arg; tests still pass with transformer-provided `include_relations` and fallback when transform step is skipped.