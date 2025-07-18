# Typedef and Include Relationship Features

## Overview

The C to PlantUML converter now supports:

1. **Typedef Relationships**: Shows typedef relationships with proper UML stereotypes
2. **Include Depth Processing**: Processes include relationships up to configurable depth
3. **Configurable Include Depth**: Control how deep include relationships are processed
4. **C-File Only Generation**: Only C files (.c) generate PlantUML diagrams
5. **Enhanced Header Relationships**: C files show header relationships as separate classes

## Features Implemented

### 1. Typedef Relationships

The system now parses typedef statements and generates proper PlantUML relationships:

- **«alias» relationship**: For basic type aliases (e.g., `typedef uint32_t MyLen`)
- **«defines» relationship**: For complex type definitions (e.g., `typedef struct MyBuffer`)

Example PlantUML output:
```plantuml
class "MyLen" as MYLEN <<typedef>> #LightYellow
{
    + uint32_t
}

MYLEN -|> UINT32_T : «alias»
```

### 2. Include Depth Processing

The system processes include relationships recursively up to a configurable depth:

- **Depth tracking**: Each include relationship shows its depth level
- **Configurable depth**: Set via `include_depth` in configuration
- **Prevents infinite loops**: Uses visited set to avoid circular includes

Example PlantUML output:
```plantuml
TYPEDEF_TEST --> SAMPLE : <<include>> (depth 1)
TYPEDEF_TEST --> SAMPLE : <<include>> (depth 2)
```

### 3. C-File Only Generation

**Only C files (.c) generate PlantUML diagrams**:
- Header files (.h) are NOT generated as separate PlantUML files
- This reduces clutter and focuses on the main source files
- Header relationships are shown within the C file diagrams

### 4. Enhanced Header Relationships

C files now show header relationships as separate classes:

```plantuml
class "stdio" as STDIO <<header>> #LightGreen
{
    + #include <stdio.h>
}

MAIN --> STDIO : <<include>>
```

This provides a clear visual representation of:
- Which headers are included
- The relationship between source files and headers
- Header dependencies

### 5. Configuration

Add `include_depth` to your configuration file:

```json
{
  "project_roots": ["./src"],
  "project_name": "My_Project",
  "output_dir": "./output",
  "include_depth": 3,
  "file_filters": {
    "include": [".*\\.c$", ".*\\.h$"],
    "exclude": []
  }
}
```

## Usage

1. **Create configuration file** with `include_depth` setting
2. **Run the converter**: `python3 main.py config config.json`
3. **View generated PlantUML files** in the output directory (only .c files)

## Example Output

The generated PlantUML files now show:

- **Source file classes** with `<<source>>` stereotype (only for .c files)
- **Header classes** with `<<header>>` stereotype (shown within .c files)
- **Typedef classes** with `<<typedef>>` stereotype
- **Type classes** with `<<type>>` stereotype for complex types
- **Proper relationships** with `«defines»` and `«alias»` stereotypes
- **Include relationships** with depth information

## File Naming

Files are now generated with their full extension to avoid conflicts:
- `typedef_test.c.puml`
- `complex_example.c.puml`
- `sample.c.puml`

**Note**: Header files (.h) do not generate separate PlantUML files but are shown as classes within the C file diagrams.

## Benefits

1. **Cleaner output**: Only source files generate diagrams
2. **Better focus**: Concentrates on the main implementation files
3. **Enhanced relationships**: Shows header dependencies clearly
4. **Reduced clutter**: Avoids duplicate information from header files
5. **Better organization**: Headers are shown as dependencies rather than separate files