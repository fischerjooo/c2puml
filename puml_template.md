# PlantUML Formatting Template

This template defines the structure for generating PlantUML diagrams from C source and header files, with strict separation of typedefs and clear relationship groupings.

```plantuml
@startuml {basename}

' Source file class
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

' Header file class
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

' Original type classes for struct/enum/union
class "{original_type}" as {TYPE_UML_ID} <<type>> #LightGray
{
    + {field_type} {field_name}
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
- Enums and unions are not listed in C or header classes; they are only shown in their own typedef/type classes.
- Structs are not listed in C or header classes; they are only shown in their own typedef/type classes.
- Relationships are grouped as: Include, Declaration, and Uses.