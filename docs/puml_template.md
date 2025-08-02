# PlantUML Formatting Template

This template defines the structure for generating PlantUML diagrams from C source and header files, with comprehensive typedef handling and relationship visualization.

## UML_ID Naming Conventions
- **C files**: No prefix, based on filename in capital letters (e.g., `main.c` → `MAIN`)
- **H files**: `HEADER_` prefix, based on filename in capital letters (e.g., `utils.h` → `HEADER_UTILS`)
- **Typedefs**: `TYPEDEF_` prefix, based on typedef name in capital letters (e.g., `MyStruct` → `TYPEDEF_MYSTRUCT`)

## Content Formatting Rules

### Source Files (C files)
- **Macros**: `-` prefix for visibility
- **Global Variables**: No prefix for visibility
- **Functions**: No prefix for visibility
- **Structs/Enums/Unions**: Only the name is shown (e.g., `struct MyStruct`, `enum MyEnum`)
- **Primitive Typedefs**: Only primitive typedefs with `relationship_type = "alias"` are shown with `-` prefix

### Header Files (H files)
- **All elements**: `+` prefix for visibility
- **Primitive Typedefs**: Only primitive typedefs with `relationship_type = "alias"` are shown with `+` prefix
- **Structs/Enums/Unions**: Only the name is shown (e.g., `+ struct MyStruct`, `+ enum MyEnum`)

### Typedef Classes
- **All typedefs**: Separate classes for all typedefs (structs, enums, unions, function pointers, primitives)
- **Struct typedefs**: Show field names and types (e.g., `+ int x`, `+ char* name`)
- **Enum typedefs**: Show enum value names (e.g., `+ LOG_DEBUG`, `+ LOG_INFO`)
- **Union typedefs**: Show union field names and types (e.g., `+ int i`, `+ float f`)
- **Function pointer typedefs**: Show complete signature (e.g., `+ int(* callback)(int, char*)`)
- **Primitive typedefs**: Show the original type name (e.g., `+ uint32_t`, `+ char*`)

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
- **Typedefs**: `#LightYellow` background with `<<typedef>>` stereotype

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
    {type} {variable_name}
    -- Functions --
    {return_type} {function_name}({parameters})
    -- Structs/Enums/Unions --
    struct {struct_name}
    enum {enum_name}
    union {union_name}
    -- Primitive Typedefs --
    - typedef {original_type} {typedef_name}
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
    -- Structs/Enums/Unions --
    + struct {struct_name}
    + enum {enum_name}
    + union {union_name}
    -- Primitive Typedefs --
    + typedef {original_type} {typedef_name}
}

' Typedef classes (all typedefs in separate classes)
class "{typedef_name}" as {TYPEDEF_UML_ID} <<typedef>> #LightYellow
{
    + {typedef_content}
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
- **Primitive typedefs**: Only shown in file/header classes if `relationship_type = "alias"` and not struct/enum/union
- **Complex typedefs**: Struct, enum, and union typedefs are NOT shown in file/header classes to avoid duplication
- **Typedef classes**: All typedefs (primitive and complex) are shown in separate typedef classes with their content and relationships

### Relationship Visualization
- **Include relationships**: Arrows showing file dependencies
- **Declaration relationships**: Dotted lines showing which files declare which typedefs
- **Uses relationships**: Dotted lines showing typedef dependencies

### Content Organization
- **Sections**: Macros, Global Variables, Functions, Structs/Enums/Unions, Primitive Typedefs
- **Visibility**: Consistent use of `+` for headers, `-` for source files
- **No #include lines**: All include relationships are visualized with arrows only

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