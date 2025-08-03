# Proposed Changes to AnonymousTypedefProcessor

## Current Implementation vs Proposed Changes

### 1. Update `_generate_anonymous_name` Method

**Current Implementation:**
```python
def _generate_anonymous_name(self, parent_name: str, struct_type: str, counter: int) -> str:
    """Generate a name for an anonymous structure."""
    return f"{parent_name}_anonymous_{struct_type}_{counter}"
```

**Proposed Implementation:**
```python
def _generate_anonymous_name(self, parent_name: str, field_name: str, struct_type: str = None) -> str:
    """Generate a meaningful name for anonymous structure based on parent and field."""
    # Use parent_field pattern for clarity
    base_name = f"{parent_name}_{field_name}"
    
    # Handle edge cases
    if not field_name or field_name == "":
        # Fallback to counter-based naming for edge cases
        if not hasattr(self, '_fallback_counter'):
            self._fallback_counter = {}
        if parent_name not in self._fallback_counter:
            self._fallback_counter[parent_name] = 0
        self._fallback_counter[parent_name] += 1
        return f"{parent_name}_anonymous_{struct_type}_{self._fallback_counter[parent_name]}"
    
    return base_name
```

### 2. Update Method Calls

**In `_process_alias_for_anonymous_structs`:**
```python
# Current
anon_name = self._generate_anonymous_name(alias_name, struct_type, i)

# Proposed - need to extract field name from context
# For function pointers with anonymous parameters, use parameter position
anon_name = self._generate_anonymous_name(alias_name, f"param{i}", struct_type)
```

**In `_extract_anonymous_from_field`:**
```python
# Current
anon_name = self._generate_anonymous_name(parent_name, struct_type, 1)

# Proposed - use the actual field name
anon_name = self._generate_anonymous_name(parent_name, field.name, struct_type)
```

### 3. Handle Nested Anonymous Structures

**Add tracking for nested context:**
```python
def _extract_anonymous_from_field(self, file_model: FileModel, parent_name: str, field: Field, parent_context: str = "") -> None:
    """Extract anonymous structures with context tracking for nested structures."""
    
    # Build full context for nested structures
    if parent_context:
        full_parent_name = f"{parent_context}_{parent_name}"
    else:
        full_parent_name = parent_name
    
    if field.type in ["struct { ... }", "union { ... }"]:
        # Generate contextual name
        anon_name = self._generate_anonymous_name(full_parent_name, field.name)
        
        # ... rest of the implementation
        
        # For nested anonymous structures within this one, pass the context forward
        for nested_field in anon_struct.fields:
            if self._field_contains_anonymous_struct(nested_field):
                self._extract_anonymous_from_field(
                    file_model, 
                    field.name,  # This field becomes the parent
                    nested_field,
                    full_parent_name  # Pass the full context
                )
```

### 4. Special Cases Handling

**Array fields with anonymous structures:**
```python
# For: struct { ... } items[10];
# Generate: ParentType_items (not ParentType_items[10])
field_name_clean = re.sub(r'\[.*\]', '', field.name)
anon_name = self._generate_anonymous_name(parent_name, field_name_clean)
```

**Multiple anonymous fields of same type:**
```python
# Add uniqueness check
def _ensure_unique_name(self, file_model: FileModel, proposed_name: str) -> str:
    """Ensure the generated name is unique, append number if needed."""
    if proposed_name not in file_model.structs and proposed_name not in file_model.unions:
        return proposed_name
    
    # Add counter suffix for uniqueness
    counter = 2
    while True:
        unique_name = f"{proposed_name}_{counter}"
        if unique_name not in file_model.structs and unique_name not in file_model.unions:
            return unique_name
        counter += 1
```

### 5. Update Tests

**Test the new naming convention:**
```python
def test_meaningful_anonymous_names(self):
    """Test that anonymous structures get meaningful names."""
    test_code = """
    typedef struct {
        struct {
            int x, y;
        } position;
        struct {
            int width, height;
        } size;
    } Rectangle;
    """
    
    # Process the code
    file_model = self.parser.parse_file_content(test_code)
    processor = AnonymousTypedefProcessor()
    processor.process_file_model(file_model)
    
    # Verify names
    assert "Rectangle_position" in file_model.structs
    assert "Rectangle_size" in file_model.structs
    
    # Verify field updates
    rect = file_model.structs["Rectangle"]
    position_field = next(f for f in rect.fields if f.name == "position")
    assert position_field.type == "Rectangle_position"
```

## Benefits of This Approach

1. **Self-Documenting**: Names like `Rectangle_position` immediately tell you the relationship
2. **Debugging**: Easier to trace issues when names are meaningful
3. **PlantUML Clarity**: Generated diagrams are more readable
4. **Consistency**: Predictable naming pattern across the codebase
5. **Collision Avoidance**: Parent_field combination naturally avoids most name collisions

## Migration Strategy

1. Keep the old `_generate_anonymous_name` signature but add field_name parameter with default None
2. When field_name is None, fall back to old behavior (for compatibility)
3. Gradually update all call sites to pass field_name
4. Add configuration option to choose naming strategy:
   ```json
   {
     "anonymous_naming": "contextual"  // or "legacy" for old behavior
   }
   ```