# Unified Type System: Concept and Design (Proposed)

## Objectives
- Simplify and unify parsing, modeling, and generation of all C types (named and anonymous) under one coherent model.
- Eliminate special-case handling for anonymous types by representing them identically to named types with metadata.
- Normalize typedefs via a single relation model (alias/defines) and a canonical type registry.
- Make relationships (declares, uses, contains) uniform and derivable from the model without ad-hoc lists.
- Enable deterministic unfolding of typedef-of-typedef chains and anonymous inlines.

## Core Ideas

### 1) Unified TypeEntity and TypeExpr
- TypeEntity: first-class model object for any type that can appear as a UML class.
  - id: canonical identifier (e.g., TYPEDEF_RECTANGLE, TYPEDEF_MY_INT)
  - name: display/original typedef name or synthesized name for anonymous
  - kind: enum [alias, struct, union, enum, function_pointer, primitive]
  - is_anonymous: bool
  - owner: optional OwnerRef (typedef/file/parent-type + field path) for anonymous or synthesized types
  - fields: for struct/union (ordered list of Field{name, type: TypeExpr})
  - enum_values: for enums (ordered)
  - function_signature: for function_pointer (return: TypeExpr, params: [Param{name?, type: TypeExpr}])
  - original_type: for alias (TypeExpr)

- TypeExpr: normalized type expression AST used everywhere (fields, params, typedefs, globals, returns).
  - Variants: NamedType{id}, Pointer{to}, Array{of, size?}, Function{return, params}, Qualified{base, const?, volatile?}
  - NamedType always refers to a TypeEntity by canonical id (never raw text) after resolution.

### 2) Type Registry and Canonical IDs
- Global TypeRegistry builds a bijection between names/synthesized names and TypeEntity ids.
- For anonymous types, synthesize deterministic names using context path:
  - Pattern: PARENT_TYPEDEF__fieldA__fieldB (double underscore as separator)
  - Collisions resolved with numeric suffixes, tracked in registry.
- Deduplication is handled by canonicalization of owner+field-path.

### 3) Typedef Relations as First-Class
- Every typedef becomes (or points to) a TypeEntity with:
  - kind = alias if it aliases a non-aggregate, or function_pointer if it aliases a function type, or struct/union/enum if it defines one.
  - relation: enum [defines, alias] between the typedef name and the canonical target represented by TypeExpr.
- typedef-of-typedef chains are represented directly via TypeExpr NamedType nodes pointing to other TypeEntity ids; a post-pass computes:
  - alias_chain: [typedef_a -> typedef_b -> primitive]
  - canonical_target_id: final concrete TypeEntity kind (struct/union/enum/function_pointer/primitive)

### 4) Anonymous Types as Normal Types
- Inline anonymous structs/unions/function-signature-return-structs are extracted as TypeEntity with is_anonymous = true and an owner reference.
- Parent fields are rewritten to refer to the NamedType of the extracted entity.
- No separate anonymous lists; composition relationships derive from owner links.

### 5) Unified Relationships
- declares: File → TypeEntity declared in the file (typedef or named aggregate)
- uses: TypeEntity → TypeEntity for all referenced NamedType ids present in its TypeExpr trees (fields, params, returns)
- contains: Parent TypeEntity (struct/union) → Child TypeEntity for extracted anonymous children, based on owner relationship
- alias/defines: Rendered as UML relationship style but stored only as `relation` on the typedef TypeEntity linking to canonical_target_id

All arrows in PlantUML are generated from these uniform sources; no special-case anonymous relationship lists.

## Parsing and Resolution Pipeline
1) Tokenize and parse declarations into raw declarators and raw type expressions.
2) Build initial TypeExpr trees (symbolic, may include unresolved names).
3) Register TypeEntities for:
   - All typedef names (as alias/defines depending on the declarator)
   - All named structs/unions/enums
   - All function pointer typedefs (as kind=function_pointer)
   - All anonymous inline aggregates encountered in fields/params/returns (synthesized name, owner reference)
4) Resolve TypeExpr NamedType nodes against the TypeRegistry; create primitives on demand as TypeEntity(kind=primitive) for builtin types (uint32_t etc.).
5) Compute typedef alias chains and canonical targets; fill `relation` and `canonical_target_id` on typedef entities.
6) Normalize parent fields/params to reference NamedType ids only (no raw inline blocks remain).
7) Build relationship views (declares, uses, contains) directly from the registry and entities.

## Data Model Changes (models.py)
- New dataclasses:
  - TypeEntity
  - TypeExpr variants (algebraic-like using tagged dicts or typed classes)
  - OwnerRef { parent_typedef_id, field_path: [str], source_file }
- ProjectModel additions:
  - type_index: Dict[id, TypeEntity]
  - files[].declares: List[id]
  - relationships are derived at generation time; stored optionally for debugging.
- Remove/replace:
  - file.typedefs (string map) → represented by TypeEntity of kind alias/struct/union/enum/function_pointer
  - typedef_relations list → folded into typedef TypeEntity fields `relation`, `canonical_target_id`
  - anonymous_relationships → replaced by contains derived from OwnerRef

## Generator Mapping
- Stereotype from TypeEntity.kind
- Content:
  - struct/union: fields from fields[] (TypeExpr rendered)
  - enum: enum_values
  - function_pointer: `alias of <rendered function signature>`
  - alias: `alias of <rendered TypeExpr>`
- Relationships:
  - declares: FILE ..> TYPEDEF
  - uses: TYPEDEF ..> TYPEDEF (from all NamedType references in TypeExpr trees)
  - contains: PARENT *-- CHILD (for OwnerRef children)
  - «alias» vs «defines» labels derived from typedef TypeEntity.relation when drawing alias/defines stylings

## Benefits
- One representation for all types; no special handling for anonymous blocks.
- Deterministic naming and dedup for anonymous types.
- Clean separation: TypeExpr for syntax; TypeEntity for things that become classes.
- Uniform relationship derivation removes ad-hoc collectors and duplicate logic.
- Easier future features: cycles, better function-pointer returns, arrays-of-function-pointers, qualifiers.

## Migration Plan
- Phase 1 (Docs & Tests):
  - Document design (this file) and add non-executed YAML fixtures for upcoming tests.
  - Add unit tests scaffolding (Python drivers later) for typedef unfolding, anonymous extraction, and uses/contains derivation.
- Phase 2 (Model Layer):
  - Introduce TypeExpr and TypeEntity alongside existing models; add adapters in generator to read from new structures without breaking old behavior.
- Phase 3 (Parser/Anonymous):
  - Switch anonymous extraction to create TypeEntities with OwnerRef and remove anonymous-specific lists.
- Phase 4 (Typedef Resolution):
  - Implement alias chain resolution and canonical target computation; update stereotypes and relationships in generator.
- Phase 5 (Cleanup):
  - Remove legacy typedef_relations and anonymous_relationships; update docs and tests.

## Testing Strategy (TDD)
- Unit: tokenizer → declarators → TypeExpr trees (function pointers, arrays, qualifiers).
- Unit: anonymous extraction → synthesized naming and OwnerRef; dedup by field path.
- Unit: typedef unfolding → alias chains; canonical target determination.
- Generator: stereotypes and relationships from unified model; no duplicates; correct composition and uses.
- Integration: example project parity with new model; order preserved; no garbled fields; no duplicate anonymous types.