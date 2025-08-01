# Simplified Include Processing Architecture

## Overview

The include handling and filtering system has been simplified to follow a structured, depth-based approach that is more predictable and easier to understand. This document describes the new simplified architecture.

## Key Principles

### 1. Single Root C File per Include Structure
- Each C file acts as an independent root for its own include structure
- Only C files (`.c` extensions) can be root files
- Each root C file maintains its own list of `include_relations`
- Header files (`.h`) never have `include_relations` - they are always targets, not sources

### 2. Layer-by-Layer Processing
The processing follows a breadth-first approach:
- **Depth 1**: Direct includes from the root C file
- **Depth 2**: Includes from files included at depth 1
- **Depth 3**: Includes from files included at depth 2
- And so on, up to the configured `include_depth`

### 3. Filter Application
- Include filters are applied **only at depth 1** (direct includes from root C files)
- Once a file passes the filter and is included, its own includes are processed without filtering
- This ensures that if you include a library header, you get all its transitive dependencies

### 4. Cycle Prevention
- Files are tracked as "processed" to prevent infinite loops
- If a file has already been processed in the current root's include tree, it won't be processed again
- This prevents circular dependencies from causing infinite recursion

## Implementation Details

### Main Method: `_process_include_relations_simplified()`

This is the new unified method that replaces the previous complex include processing logic.

```python
def _process_include_relations_simplified(self, model: ProjectModel, config: Dict[str, Any]) -> ProjectModel:
    """
    Simplified include processing following a structured depth-based approach:
    1. Each include structure has a single root C file
    2. Process C file's direct includes through filters first  
    3. Then recursively process header files' includes with filtering
    4. Continue until include_depth is reached
    """
```

### Key Features

1. **Clear Separation of Concerns**:
   - File discovery and mapping
   - Per-root-file processing 
   - Depth-controlled iteration
   - Filter application
   - Cycle detection

2. **Breadth-First Search (BFS) Approach**:
   - Process all files at the current depth before moving to the next depth
   - Maintains clear depth boundaries
   - Ensures predictable processing order

3. **Robust Cycle Detection**:
   - Tracks processed files per root to prevent cycles
   - Prevents duplicate relations
   - Handles complex circular dependencies gracefully

## Configuration Support

### File-Specific Settings
The simplified approach fully supports file-specific configuration:

```json
{
    "include_depth": 2,
    "file_specific": {
        "main.c": {
            "include_depth": 3,
            "include_filter": ["local.*", "utils.*"]
        },
        "test.c": {
            "include_depth": 1
        }
    }
}
```

### Filter Behavior
- Filters apply only to **direct includes** from the root C file
- Pattern matching uses regex
- Once a file is included, its transitive includes are processed without filtering

## Examples

### Basic Depth Processing
```
main.c -> utils.h, math.h          (depth 1)
utils.h -> config.h                (depth 2)  
math.h -> constants.h              (depth 2)
config.h -> types.h                (depth 3)
```

With `include_depth: 3`, this generates 5 include relations, all stored in `main.c.include_relations`.

### Filter Example
```
main.c includes: ["system.h", "local.h"]
local.h includes: ["app.h"]
```

With filter `["local.*"]`:
- `local.h` matches the filter → included at depth 1
- `app.h` doesn't match but is included at depth 2 (transitive)
- `system.h` doesn't match → filtered out

Result: 2 relations (`main.c -> local.h`, `local.h -> app.h`)

### Cycle Prevention
```
main.c -> a.h -> b.h -> a.h (cycle)
```

Result: 2 relations (`main.c -> a.h`, `a.h -> b.h`)
The `b.h -> a.h` relation is prevented because `a.h` was already processed.

## Benefits

1. **Predictable Behavior**: Clear depth-based processing with well-defined rules
2. **Better Performance**: Single-pass processing with efficient cycle detection
3. **Simplified Logic**: One unified method instead of multiple complex approaches
4. **Maintainable Code**: Clear separation of concerns and well-documented behavior
5. **Flexible Configuration**: Supports both global and file-specific settings

## Migration

The new simplified approach is a drop-in replacement for the previous include processing methods. All existing configuration formats are supported, and the behavior is backward-compatible for most use cases.

The main change is that include filters now only apply at depth 1, which provides more intuitive behavior for most users while still supporting advanced filtering scenarios.

## Testing

Comprehensive test coverage includes:
- Depth-based processing validation
- Filter application at different depths
- Cycle prevention scenarios
- Multiple root C files with independent processing
- File-specific configuration handling

All tests pass and validate the correct implementation of the simplified approach.