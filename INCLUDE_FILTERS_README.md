# Include Filters Feature

## Overview

The `include_filters` feature allows you to filter includes and include relations for each root C file based on regex patterns. This enables you to create separate PlantUML models for different root files with different include filtering rules.

## Configuration

Add an `include_filters` section to your configuration JSON file:

```json
{
  "include_filters": {
    "the name of the root c file": ["regex filter A", "regex filter B"],
    "another_root_file.c": ["^stdio\\.h$", "^stdlib\\.h$"]
  }
}
```

## How It Works

1. **Root File Detection**: The system identifies the root C file for each file in the model. Currently, it uses the filename as the root file identifier.

2. **Pattern Matching**: For each root file, the system applies the corresponding regex patterns to filter:
   - `includes`: The list of included header files
   - `include_relations`: The relationships between files

3. **Filtering Logic**: Only includes and include relations that match **any** of the regex patterns for the root file are kept.

## Examples

### Basic Example

```json
{
  "include_filters": {
    "main.c": ["^stdio\\.h$", "^stdlib\\.h$", "^string\\.h$"]
  }
}
```

This configuration will:
- Keep only `stdio.h`, `stdlib.h`, and `string.h` includes for files associated with `main.c`
- Remove all other includes and include relations for `main.c`

### Multiple Root Files

```json
{
  "include_filters": {
    "main.c": ["^stdio\\.h$", "^stdlib\\.h$"],
    "utils.c": ["^math\\.h$", "^time\\.h$"],
    "network.c": ["^sys/socket\\.h$", "^netinet/", "^arpa/"]
  }
}
```

This configuration applies different filtering rules for different root files:
- `main.c`: Only keeps standard library includes
- `utils.c`: Only keeps math and time-related includes
- `network.c`: Only keeps networking-related includes

### Advanced Patterns

```json
{
  "include_filters": {
    "database.c": ["^sqlite3\\.h$", "^mysql\\.h$", "^postgresql/"],
    "gui.c": ["^gtk/", "^glib/", "^cairo\\.h$"],
    "crypto.c": ["^openssl/", "^crypto\\.h$", "^ssl\\.h$"]
  }
}
```

## Integration with PlantUML Generation

When you generate PlantUML diagrams, each root file will have its own filtered set of includes and include relations. This allows you to:

1. **Create focused diagrams**: Each PlantUML diagram will only show the relevant includes for that specific root file
2. **Reduce complexity**: Remove unnecessary include relationships that clutter the diagram
3. **Customize per module**: Apply different filtering rules for different parts of your codebase

## Error Handling

- **Invalid Regex Patterns**: If a regex pattern is invalid, it will be skipped with a warning, but valid patterns will still be applied
- **Missing Root Files**: If a file doesn't match any root file filters, it will not be affected by include filtering
- **Empty Configuration**: If `include_filters` is empty or not provided, no filtering will be applied

## Usage in Transformation Pipeline

The include filtering is applied during the transformation step (Step 2) of the C to PlantUML conversion process, after file and element filtering but before other transformations.

## Testing

The feature includes comprehensive unit tests that verify:
- Basic include filtering functionality
- Multiple root file support
- Error handling for invalid regex patterns
- Integration with the main transformation pipeline

Run the tests with:
```bash
python3 -m unittest tests.unit.test_transformer.TestTransformer.test_apply_include_filters_*
```