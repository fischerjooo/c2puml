# Complex Typedef Example

A C project demonstrating complex typedef relationships and patterns.

## Description

This example shows complex typedef usage including:
- Typedefs for basic types (aliases)
- Typedefs for structs, enums, and unions (defines)
- Anonymous struct/enum/union typedefs
- Nested typedef relationships
- Typedef chains and complex patterns

## Input Files

- `types.h` - Complex typedef definitions
- `structures.h` - Struct definitions with typedefs
- `main.c` - Usage of typedefs

## Expected Output

The tool should generate a PlantUML diagram showing:
- Separate typedef classes with proper stereotypes («defines», «alias»)
- Typedef content display for struct/enum/union typedefs
- Relationship arrows between typedefs and their underlying types
- Complex typedef chains and nested relationships

## Configuration

Uses include depth 2 to show typedef relationships clearly.