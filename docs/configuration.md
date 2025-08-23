# Configuration Guide

This guide explains how to configure c2puml via `config.json`. It covers every parameter with defaults, types, behavior, and examples, with extra detail for transformer configuration.

## Quick Start

Minimal example:
```json
{
  "project_name": "my_project",
  "source_folders": ["./src"],
  "output_dir": "./output"
}
```

Run:
```bash
c2puml --config config.json
```

## Core Parameters

- **project_name** (string, default: "Unknown_Project")
  - Human-readable project name used in metadata.

- **source_folders** (string[], required)
  - One or more folders to scan for C/C++ files.
  - Relative paths are resolved from the working directory; absolute paths supported.

- **output_dir** (string, default: "./output")
  - Directory where `model.json`, `model_transformed.json`, and `.puml` files are written.

- **model_output_path** (string, default: "model.json")
  - Filename for the parser’s model output inside `output_dir`.

- **recursive_search** (boolean, default: true)
  - Recursively discover files in `source_folders`.

- **include_depth** (integer, default: 1)
  - Controls include relationship processing depth. Applied by the transformer; results stored as `include_relations` on root `.c` files and consumed by the generator.
  - 1: only direct includes. 2+: transitive includes and header-to-header arrows.

- **include_filter_local_only** (boolean, default: false)
  - When true, automatically adds a filter to prefer the local header matching each root C file name (e.g., `main.c` → `^main\\.h$`).

- **always_show_includes** (boolean, default: false)
  - When filtering excludes a header, still render it as an empty placeholder class and draw the include arrow. Its content and further includes are not processed.

- **convert_empty_class_to_artifact** (boolean, default: false)
  - PlantUML generation option: convert empty classes to artifacts for cleaner diagrams.

### Formatting Options (Generator)

- **max_function_signature_chars** (integer, default: 0)
  - 0 or less disables truncation. If > 0, long function signatures are truncated with `...` for readability.

- **hide_macro_values** (boolean, default: false)
  - Controls simple macro value display.
  - Function-like macros always hide definitions and show only the signature (`#define MIN(a, b)`).

## File and Element Filtering

- **file_filters** (object, default: `{}`)
  - `include`: string[] of regex patterns to include file paths.
  - `exclude`: string[] of regex patterns to exclude file paths.
  - Applied by the transformer to filter entire files in the model.

- **file_specific** (object, default: `{}`)
  - Per-root C-file settings by basename (e.g., `"main.c"`).
  - Keys:
    - `include_filter` (string[]): regex patterns controlling which headers are considered for this root.
    - `include_depth` (integer): overrides global `include_depth` for this root.

Behavior:
- Transformer processes include relations per root C file using a breadth-first, depth-limited traversal.
- If `always_show_includes` is true, filtered-out headers appear as placeholders and are not expanded further.

## Transformer Configuration (Step 2)

The transformer supports a multi-stage, containerized configuration. Containers are discovered by keys that start with `transformations` and are applied in alphabetical order. Use numeric prefixes to make the order explicit.

### Container structure

```json
{
  "transformations_01_rename": {
    "file_selection": [".*main\\.c$"],
    "rename": { /* ... */ }
  },
  "transformations_02_cleanup": {
    "file_selection": [],
    "remove": { /* ... */ }
  }
}
```

- **file_selection** (string[] of regex) – optional
  - Patterns are matched against file paths in the model. Empty or omitted applies to all files.
  - If an invalid type is provided (e.g., object), the transformer will ignore it and apply to all files.

- **rename** (object)
  - Keys and behaviors (regex-based; deduplicates by final name):
    - `typedef`: `{ pattern: replacement }`
      - Also updates all type references (functions, globals, struct fields, union fields) to the new typedef name.
    - `functions`: `{ pattern: replacement }`
    - `macros`: `{ pattern: replacement }` (renames macro identifiers while preserving parameters and values)
    - `globals`: `{ pattern: replacement }`
    - `includes`: `{ pattern: replacement }` (propagates to `include_relations`)
    - `files`: `{ pattern: replacement }` (renames file paths; propagates to `includes` and `include_relations` across the model)
    - `structs`, `enums`, `unions`: `{ pattern: replacement }`

- **remove** (object)
  - Keys and behaviors (regex arrays):
    - `typedef`: `[pattern, ...]` (removes typedefs; transformer cleans up any references to removed typedefs by replacing occurrences in types with `void` and normalizing spacing)
    - `functions`, `macros`, `globals`: `[pattern, ...]`
    - `includes`: `[pattern, ...]` (also removes matching `include_relations`)
    - `structs`, `enums`, `unions`: `[pattern, ...]`

- **add** (object)
  - Reserved for future use (no-ops in the current implementation).

### Include-depth processing in the transformer

- Global `include_depth` is honored; per-file overrides via `file_specific["<root.c>"]`. Include relations are recomputed and stored as a flat list on the root C file.
- `include_filter_local_only`: augments per-file include filters to prefer the matching local header (e.g., `^main\\.h$`).
- `always_show_includes`: when true, headers excluded by filters are still rendered as placeholders with arrows, without content expansion.

### Legacy compatibility

- If a single `transformations` object is provided, it is wrapped as `transformations_00_default` automatically.
- Prefer `file_selection` as a list of patterns. The legacy nested `file_selection.selected_files` object is deprecated.

## Backward Compatibility (Input)

- `project_roots` → `source_folders` is supported automatically when loading configuration.

## Examples

### Full configuration example
```json
{
  "project_name": "Example",
  "source_folders": ["tests/example/source"],
  "output_dir": "./output",
  "model_output_path": "model.json",
  "recursive_search": true,
  "include_depth": 2,
  "include_filter_local_only": false,
  "always_show_includes": true,
  "convert_empty_class_to_artifact": false,
  "max_function_signature_chars": 0,
  "hide_macro_values": false,
  "file_filters": {
    "include": [".*\\.(c|h)$"],
    "exclude": [".*test.*"]
  },
  "file_specific": {
    "main.c": {
      "include_filter": ["^stdio\\.h$", "^stdlib\\.h$", "^string\\.h$"],
      "include_depth": 3
    }
  },
  "transformations_01_rename": {
    "file_selection": [".*main\\.c$"],
    "rename": {
      "typedef": {"^old_config_t$": "config_t"},
      "functions": {"^calculate$": "compute"},
      "files": {"^legacy\\.c$": "modern\\.c"}
    }
  },
  "transformations_02_cleanup": {
    "file_selection": [],
    "remove": {
      "typedef": ["^legacy_.*"],
      "functions": ["^debug_.*"],
      "macros": ["^DEBUG_.*"],
      "includes": ["^deprecated\\.h$"]
    }
  }
}
```

### File-specific include filtering and depth override
```json
{
  "file_specific": {
    "network.c": {
      "include_filter": ["^sys/socket\\.h$", "^netinet/", "^arpa/"],
      "include_depth": 2
    }
  }
}
```

## See also
- Specification: `docs/specification.md`
- PlantUML Template: `docs/puml_template.md`