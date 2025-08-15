# Naming Specification

## Anonymous Type Naming (Synthesized)
- Separator: single underscore `_` between path parts.
- Pattern: `PARENTTYPE_field1_field2_...`
  - Example (3 levels): `widget_t_meta_layout_pos`
- Path parts come from the field identifiers along the nesting path.
- Collisions: append numeric suffix `_2`, `_3`, ... deterministically.
- Casing: preserve original typedef and field casing as parsed (no extra transformations).

## Owner Reference
- For synthesized anonymous types, store an `OwnerRef` with:
  - `parent_typedef_id`: canonical id of the parent typedef entity
  - `field_path`: ordered list of field names, e.g., `["meta", "layout", "pos"]`
  - `source_file`: file where the parent typedef is declared

## Typedef Unfolding (Chains)
- Represent chains via `TypeExpr` NamedType references.
- Compute and store:
  - `alias_chain`: ordered list of typedef ids from alias to target
  - `canonical_target_id`: final non-alias entity id (struct/union/enum/function_pointer/primitive)

## Relationships (Derivation Rules)
- declares: File → TypeEntity declared in the file
- uses: TypeEntity → TypeEntity referenced by any `NamedType` found in its `TypeExpr` trees
- contains: Parent TypeEntity (struct/union) → Child synthesized TypeEntity with `OwnerRef` whose parent matches the parent entity

## Example
C source:
```c
typedef struct {
    struct {
        struct {
            int x; int y;
        } pos;
        int width;
    } layout;
    char name[16];
} widget_t;
```
Synthesized types:
- `widget_t_layout`
- `widget_t_layout_pos`

Field rewrites:
- `widget_t` fields: `widget_t_layout layout`, `char name[16]`
- `widget_t_layout` fields: `widget_t_layout_pos pos`, `int width`
- `widget_t_layout_pos` fields: `int x`, `int y`

Relationships:
- `widget_t *-- widget_t_layout : <<contains>>`
- `widget_t_layout *-- widget_t_layout_pos : <<contains>>`