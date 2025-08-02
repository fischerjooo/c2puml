# PlantUML Formatting Template

This template defines the structure for generating PlantUML diagrams from C source and header files, with comprehensive typedef handling and relationship visualization.

## UML_ID Naming Conventions
- **C files**: No prefix, based on filename in capital letters (e.g., `main.c` → `MAIN`)
- **H files**: `HEADER_` prefix, based on filename in capital letters (e.g., `utils.h` → `HEADER_UTILS`)
- **Typedefs**: `TYPEDEF_` prefix, based on typedef name in capital letters (e.g., `MyStruct` → `TYPEDEF_MYSTRUCT`)

## Content Formatting Rules

### Source Files (C files)
- **Macros**: `-` prefix for visibility (private)
- **Global Variables**: `+` prefix if declared in headers (public), `-` prefix if not (private)
- **Functions**: `+` prefix if declared in headers (public), `-` prefix if not (private)
- **Structs/Enums/Unions**: NOT shown in source file sections
- **Primitive Typedefs**: NOT shown in source file sections - all typedefs get their own separate classes

### Header Files (H files)
- **All elements**: `+` prefix for visibility
- **Structs/Enums/Unions**: NOT shown in header file sections
- **Primitive Typedefs**: NOT shown in header file sections - all typedefs get their own separate classes

### Typedef Classes
- **Enum typedefs**: Use `<<enumeration>>` stereotype, show enum value names without prefix (e.g., `LOG_DEBUG`, `LOG_INFO`)
- **Struct typedefs**: Use `<<struct>>` stereotype, show field names and types with `+` prefix (e.g., `+ int x`, `+ char* name`)
- **Union typedefs**: Use `<<union>>` stereotype, show union field names and types with `+` prefix (e.g., `+ int i`, `+ float f`)
- **Alias typedefs**: Use `<<typedef>>` stereotype, show as `alias of {original_type}` (e.g., `alias of int`, `alias of char*`)

### Macro Display
- **Simple defines**: Show only the macro name (e.g., `#define PI`, `#define VERSION`)
- **Function-like macros**: Show the macro name with parameters (e.g., `#define MIN(a, b)`, `#define CALC(x, y)`)
- **Macro values**: Not displayed

### Function Signatures
- Include full parameter lists and return types
- Function pointers show complete signature with parameter names

## Color Scheme
- **Source files**: `#LightBlue` background with `<<source>>` stereotype
- **Header files**: `#LightGreen` background with `<<header>>` stereotype  
- **Typedef classes**: `#LightYellow` background with specific stereotypes:
  - **Enums**: `<<enumeration>>` stereotype
  - **Structs**: `<<struct>>` stereotype
  - **Unions**: `<<union>>` stereotype
  - **Aliases**: `<<typedef>>` stereotype

## Relationship Types

### Include Relationships
- **C files including headers**: `{C_FILE} --> {HEADER_FILE} : <<include>>`
- **Header-to-header includes**: `{HEADER_FILE} --> {OTHER_HEADER_FILE} : <<include>>`

### Declaration Relationships
- **Files declaring typedefs**: `{FILE} ..> {TYPEDEF} : <<declares>>`
- Shows which files declare which typedefs

### Uses Relationships
- **Typedefs using other typedefs**: `{TYPEDEF} ..> {OTHER_TYPEDEF} : <<uses>>`
- Shows dependencies between typedefs

## Template Structure

```plantuml
@startuml {basename}

' Source file class (C file)
class "{basename}" as {UML_ID} <<source>> #LightBlue
{
    -- Macros --
    - #define {macro_name}
    - #define {macro_name}({parameters})
    -- Global Variables --
    + {type} {variable_name}    // if declared in header (public)
    - {type} {variable_name}    // if not in header (private)
    -- Functions --
    + {return_type} {function_name}({parameters})    // if declared in header (public)
    + {return_type} {function_name}({parameters})    // other public functions

    - {return_type} {function_name}({parameters})    // if not in header (private)
    - {return_type} {function_name}({parameters})    // other private functions

}

' Header file class (H file)
class "{header_name}" as {HEADER_UML_ID} <<header>> #LightGreen
{
    -- Macros --
    + #define {macro_name}
    + #define {macro_name}({parameters})
    -- Global Variables --
    + {type} {variable_name}
    -- Functions --
    + {return_type} {function_name}({parameters})

}

' Typedef classes (all typedefs in separate classes)
' Enum typedefs
class "{enum_name}" as {ENUM_UML_ID} <<enumeration>> #LightYellow
{
    {enum_value}
    {enum_value} = {value}
}

' Struct typedefs  
class "{struct_name}" as {STRUCT_UML_ID} <<struct>> #LightYellow
{
    + {type} {field_name}
}

' Union typedefs
class "{union_name}" as {UNION_UML_ID} <<union>> #LightYellow
{
    + {type} {field_name}
}

' Alias typedefs
class "{alias_name}" as {TYPEDEF_UML_ID} <<typedef>> #LightYellow
{
    alias of {original_type}
}

' Include relationships
{UML_ID} --> {HEADER_UML_ID} : <<include>>
{HEADER_UML_ID} --> {OTHER_HEADER_UML_ID} : <<include>>

' Declaration relationships
{UML_ID} ..> {TYPEDEF_UML_ID} : <<declares>>
{HEADER_UML_ID} ..> {TYPEDEF_UML_ID} : <<declares>>

' Uses relationships
{TYPEDEF_UML_ID} ..> {OTHER_TYPEDEF_UML_ID} : <<uses>>

@enduml
```

## Key Features

### Typedef Handling
- **All typedefs**: All typedefs (primitive and complex) are shown in separate typedef classes only
- **No typedefs in file/header classes**: Typedefs are never shown in source or header file sections to avoid duplication
- **Declaration relationships**: Files that declare typedefs are connected via `<<declares>>` relationships to their typedef classes

### Relationship Visualization
- **Include relationships**: Arrows showing file dependencies
- **Declaration relationships**: Dotted lines showing which files declare which typedefs
- **Uses relationships**: Dotted lines showing typedef dependencies

### Content Organization
- **Source files**: Macros, Global Variables, Functions
- **Header files**: Macros, Global Variables, Functions  
- **Visibility in source files**: 
  - `+` prefix for globals/functions that are declared in headers (public)
  - `-` prefix for globals/functions that are not in headers (private)
  - `-` prefix for all macros (private)
  - **Grouping**: Public elements are listed first, followed by an empty line, then private elements
- **Visibility in header files**: `+` prefix for all elements (public)
- **No #include lines**: All include relationships are visualized with arrows only
- **No typedefs in files**: All typedefs are shown in separate typedef classes only

### Advanced Features
- **Function pointers**: Complete signature display with parameter names
- **Complex types**: Array types, pointer types, and nested structures properly displayed
- **Enum values**: All enum values shown with their assigned values
- **Union fields**: All union fields displayed with their types
- **Anonymous structs**: Handled with descriptive names like `__anonymous_struct__`

## Notes
- Standard library headers are displayed without angle brackets
- Macro definitions show only names and parameters, not values
- Function signatures include complete parameter lists and return types
- All typedefs are represented as separate classes for clarity
- Relationships are grouped as: Include, Declaration, and Uses
- The system supports complex C constructs including function pointers, arrays, and nested structures

## New Formatting Features

### Enhanced Typedef Stereotypes
The system now uses specific UML stereotypes for different typedef types:
- **Enums**: `<<enumeration>>` with enum values shown without prefix
- **Structs**: `<<struct>>` with fields shown with `+` prefix
- **Unions**: `<<union>>` with fields shown with `+` prefix  
- **Aliases**: `<<typedef>>` with content shown as `alias of {original_type}`

### Dynamic Visibility Detection
For source files, the system automatically determines visibility based on header presence:
- **Public elements** (`+` prefix): Functions and globals that are declared in at least one header file
- **Private elements** (`-` prefix): Functions and globals that are not declared in any header file

This provides a more accurate representation of the actual API surface and internal implementation details.

### Improved Readability with Grouping
Elements in source files are now grouped by visibility for better readability:
- **Public elements** (functions and globals declared in headers) are listed first with `+` prefix
- **Empty line separator** clearly divides public and private sections  
- **Private elements** (functions and globals not in headers) are listed after with `-` prefix

This grouping makes it easy to distinguish between the public API and internal implementation at a glance.