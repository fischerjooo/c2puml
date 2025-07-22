# PlantUML Formatting Template

This template defines the structure for generating PlantUML diagrams from C source and header files, with strict separation of typedefs and clear relationship groupings.

## UML_ID Naming Conventions
- **C files**: No prefix, based on filename in capital letters (e.g., `main.c` → `MAIN`)
- **H files**: `HEADER_` prefix, based on filename in capital letters (e.g., `utils.h` → `HEADER_UTILS`)
- **Typedefs**: `TYPEDEF_` prefix, based on typedef name in capital letters (e.g., `MyStruct` → `TYPEDEF_MYSTRUCT`)

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
    {return_type} {function_name}()
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
    + {return_type} {function_name}()
}

' Typedef classes (all typedefs, including function typedefs, are in separate classes)
class "{typedef_name}" as {TYPEDEF_UML_ID} <<typedef>> #LightYellow
{
    + {typedef_content} ' (fields for struct/union, values for enum, signature for function typedef, type for primitive)
}

' Relationships: the following 3 groupings should be done:
' 1. Include relationships: C or H files including other H files
{UML_ID} --> {HEADER_UML_ID} : <<include>>
{HEADER_UML_ID} --> {OTHER_HEADER_UML_ID} : <<include>>
' 2. Declaration relationships: C or H files declaring typedef with declares relation
{UML_ID} ..> {TYPEDEF_UML_ID} : <<declares>>
{HEADER_UML_ID} ..> {TYPEDEF_UML_ID} : <<declares>>
' 3. Uses relationships: typedefs using other typedefs relations via 'uses' linkage
{TYPEDEF_UML_ID} ..> {OTHER_TYPEDEF_UML_ID} : <<uses>>

@enduml
```

## Notes
- All typedefs (including function typedefs) are represented as separate classes and never listed in C or header classes.
- Enums, unions, and structs are not listed in C or header classes; they are only shown in their own typedef classes.
- UML_ID naming follows specific conventions:
  - C files: No prefix, filename in capital letters
  - H files: `HEADER_` prefix, filename in capital letters  
  - Typedefs: `TYPEDEF_` prefix, typedef name in capital letters
- Relationships are grouped as: Include, Declaration, and Uses.