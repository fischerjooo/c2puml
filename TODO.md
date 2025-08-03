# TODO: Multi-Pass Anonymous Structure Processing

## Status: 📋 **PLANNED FOR FUTURE IMPLEMENTATION**

**Date**: August 2025  
**Priority**: Medium  
**Complexity**: Medium-High  

## Current Limitation

The anonymous structure processing currently **stops at level 2** and doesn't recursively extract deeper nested anonymous structures (level 3+).

### Example Problem
```c
typedef struct {
    int level1_id;
    struct {                        // Level 1 → Level 2: ✅ Extracted as separate structure
        int level2_id;
        union {                     // Level 2 → Level 3: ❌ Remains flat in PlantUML
            int level3_int;
            float level3_float;
        } level3_union;
    } level2_struct;
} moderately_nested_t;
```

**Current Output (Stops at Level 2):**
```plantuml
class "moderately_nested_t_level2_struct" {
    + int level2_id
    + union { int level3_int      // ❌ Should be extracted to separate entity
    + float level3_float
    + } level3_union
}
```

**Desired Output (Continues to Level 3+):**
```plantuml
class "moderately_nested_t_level2_struct" {
    + int level2_id
    + moderately_nested_t_level2_struct_level3_union level3_union  // ✅ Reference to extracted entity
}

class "moderately_nested_t_level2_struct_level3_union" {
    + int level3_int
    + float level3_float
}
```

## Root Cause Analysis

1. **Single-Pass Processing**: Current anonymous processor runs once on the original parsed structures
2. **No Recursive Content Analysis**: After creating anonymous structures from preserved content, the system doesn't re-analyze the newly created structures for nested anonymous patterns
3. **Field Reference Updating**: Created structures maintain original field content instead of updating references to point to newly extracted entities

## Proposed Solution: Multi-Pass Processing Architecture

### Phase 1: Iterative Processing Loop
```python
def process_file_model(self, file_model: FileModel) -> None:
    max_iterations = 5  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        initial_count = len(file_model.structs) + len(file_model.unions)
        
        # Process all structures/unions/aliases
        self._process_all_entities(file_model)
        
        final_count = len(file_model.structs) + len(file_model.unions)
        
        # Stop if no new entities were created
        if final_count == initial_count:
            break
```

### Phase 2: Recursive Content Processing
```python
def _process_preserved_content(self, anon_name: str, content: str, file_model: FileModel):
    # 1. Create anonymous structure from content
    anon_struct = self._create_anonymous_struct(anon_name, content)
    file_model.structs[anon_name] = anon_struct
    
    # 2. Recursively process the content for nested anonymous patterns
    nested_patterns = self._extract_anonymous_structs_from_text(content)
    for pattern_content, pattern_type in nested_patterns:
        # Create nested anonymous structure with proper naming
        nested_name = self._generate_nested_anonymous_name(anon_name, pattern_type, field_name)
        # ... recursive processing
    
    # 3. Update field references to point to extracted nested entities
    self._update_field_references(anon_struct, file_model)
```

### Phase 3: Field Reference Resolution
```python
def _update_field_references(self, struct: Struct, file_model: FileModel):
    for field in struct.fields:
        # Check if field contains anonymous pattern that was extracted
        if self._has_anonymous_pattern(field.type):
            # Find corresponding extracted entity
            extracted_entity = self._find_extracted_entity(field, file_model)
            if extracted_entity:
                # Update field type to reference the entity
                field.type = extracted_entity.name
```

## Implementation Plan

### Step 1: Multi-Pass Loop Framework ⏳
- [ ] Modify `process_file_model()` to use iterative processing
- [ ] Add convergence detection (stop when no new entities created)
- [ ] Add maximum iteration limit for safety
- [ ] Test with simple 2-level structures to ensure no regression

### Step 2: Enhanced Content Analysis ⏳
- [ ] Extend preserved content processing to detect nested patterns
- [ ] Implement recursive pattern extraction within decoded content
- [ ] Add proper naming convention for nested entities (e.g., `Parent_Child_GrandChild`)
- [ ] Test with 3-level nested structures

### Step 3: Field Reference Resolution ⏳  
- [ ] Implement field type updating after entity extraction
- [ ] Add pattern matching to identify which fields should reference extracted entities
- [ ] Ensure circular reference prevention
- [ ] Test with complex nested structures (4+ levels)

### Step 4: Integration & Validation ⏳
- [ ] Integrate with existing anonymous relationship tracking
- [ ] Ensure composition relationships (`*-- : contains`) are created correctly
- [ ] Update PlantUML generation to handle deeper nesting
- [ ] Add comprehensive test cases for deep nesting scenarios

## Test Cases to Implement

### Test Case 1: 3-Level Nesting
```c
typedef struct {
    struct {
        union {
            int deep_value;
        } deep_union;
    } middle_struct;
} outer_struct_t;
```

### Test Case 2: Mixed Structure Types
```c
typedef struct {
    union {
        struct {
            enum { A, B } inner_enum;
        } inner_struct;
    } mixed_union;
} complex_nested_t;
```

### Test Case 3: Multiple Siblings
```c
typedef struct {
    struct { int a; } first;
    struct { int b; } second;
    union { float c; } third;
} sibling_test_t;
```

## Success Criteria

✅ **Functional Requirements:**
- [ ] Extract anonymous structures up to 5 levels deep
- [ ] Generate correct PlantUML composition relationships for all levels
- [ ] Maintain proper naming convention throughout nesting hierarchy
- [ ] Preserve all field types and relationships accurately

✅ **Performance Requirements:**
- [ ] Complete processing within 5 iterations for most real-world code
- [ ] No significant performance regression on existing codebase
- [ ] Memory usage remains reasonable for deep nesting

✅ **Quality Requirements:**
- [ ] All existing tests continue to pass
- [ ] New test coverage for 3+ level nesting scenarios
- [ ] Documentation updated to reflect new capabilities
- [ ] No circular references or infinite loops

## Technical Considerations

### Naming Convention
- **Level 1**: `ParentType_fieldName`
- **Level 2**: `ParentType_fieldName_nestedFieldName`  
- **Level 3**: `ParentType_fieldName_nestedFieldName_deepFieldName`

### Relationship Tracking
- Each level maintains `*-- : contains` relationships to its immediate children
- Deep relationships are transitive through the hierarchy

### Edge Cases
- **Circular References**: Prevent infinite loops in recursive processing
- **Naming Conflicts**: Handle cases where auto-generated names collide
- **Memory Management**: Ensure efficient processing of very deep structures
- **Malformed Code**: Graceful handling of invalid or incomplete C code

## Dependencies

- ✅ **Current Anonymous Processing**: Already implemented and working for 2 levels
- ✅ **Content Preservation**: Tokenizer properly preserves anonymous structure content  
- ✅ **Relationship Tracking**: Anonymous relationship system in place
- ✅ **PlantUML Generation**: Composition relationship generation working

## Estimated Effort

**Development Time**: 2-3 days  
**Testing Time**: 1-2 days  
**Documentation**: 0.5 days  
**Total**: 3.5-5.5 days

## Future Enhancements

After basic multi-pass processing is implemented:

1. **Performance Optimization**: Optimize for large codebases with many nested structures
2. **Advanced Naming**: User-configurable naming patterns for nested entities  
3. **Circular Reference Detection**: Enhanced detection and handling of complex circular patterns
4. **IDE Integration**: Support for IDE plugins to visualize nested structure hierarchies
5. **Interactive Diagrams**: Generate clickable PlantUML diagrams with drill-down capability

---

**Note**: This feature will significantly enhance the tool's ability to handle complex C/C++ codebases with deeply nested anonymous structures, providing complete and accurate UML representations of intricate data relationships.