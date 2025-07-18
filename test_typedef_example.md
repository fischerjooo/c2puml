# Typedef and Include Relationship Features

## Overview

The C to PlantUML converter now supports:

1. **Typedef Relationships**: Shows typedef relationships with proper UML stereotypes
2. **Include Depth Processing**: Processes include relationships up to configurable depth
3. **Configurable Include Depth**: Control how deep include relationships are processed
4. **C-File Only Generation**: Only C files (.c) generate PlantUML diagrams
5. **Enhanced Header Relationships**: C files show header relationships as separate classes with full content and arrows

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

C files now show header relationships as separate classes with **full content and arrows**:

```plantuml
class "stdio" as STDIO <<header>> #LightGreen
{
    -- Macros --
    + #define BUFFER_SIZE
    
    -- Functions --
    + int printf()
    + int scanf()
    
    -- Global Variables --
    - FILE* stdin
    - FILE* stdout
}

MAIN --> STDIO : <<include>>

' Header-to-header relationships:
STDIO --> STDLIB : <<include>>
```

**Key Features**:
- **Header files show their actual content**: Macros, typedefs, global variables, functions, structs, and enums from header files are displayed
- **Header classes shown separately**: Each included header becomes a separate class with `<<header>>` stereotype
- **Arrow relationships only**: Include relationships are shown with arrows between classes
- **Header-to-header relationships**: When headers include other headers, these relationships are shown with arrows
- **All referenced files shown**: Every include file is represented as a separate class with its content

This provides a clear visual representation of:
- Which headers are included
- The actual content of each header file
- The relationship between source files and headers
- Header dependencies and relationships between headers
- Clean separation between source content and include relationships

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
- **Header classes** with `<<header>>` stereotype and full content (macros, typedefs, globals, functions, structs, enums)
- **Typedef classes** with `<<typedef>>` stereotype
- **Type classes** with `<<type>>` stereotype for complex types
- **Proper relationships** with `«defines»` and `«alias»` stereotypes
- **Include relationships** with arrows only (no include statements in class content)
- **Header-to-header relationships** with arrows
- **Depth information** for include relationships

## File Naming

Files are now generated without the .c extension to avoid conflicts:
- `typedef_test.puml`
- `complex_example.puml`
- `sample.puml`

**Note**: Header files (.h) do not generate separate PlantUML files but are shown as classes with full content within the C file diagrams.

## Benefits

1. **Cleaner output**: Only source files generate diagrams
2. **Better focus**: Concentrates on the main implementation files
3. **Enhanced relationships**: Shows header dependencies clearly with arrows
4. **Full header content**: Displays actual macros, typedefs, globals, functions, structs, and enums from headers
5. **Header relationships**: Shows include relationships between headers
6. **Cleaner class content**: No include statements cluttering the main class content
7. **Visual clarity**: Clear separation between source content and include relationships
8. **Complete dependency view**: All header content and relationships are visible