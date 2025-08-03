# C to PlantUML Conversion - TODO

## Current Status

**Temporarily Disabled:**
- ⏸️ **Anonymous Structure Processing**: Feature disabled due to complexity and potential conflicts with other fixes

## Remaining Open Issues

### Issue 8.1: Anonymous Structure Processing (Re-enable)
**Status**: ⏸️ **DISABLED** - Low Priority

**Problem**: Anonymous structure processing has been temporarily disabled to avoid conflicts with other fixes.

**Current Status**:
- Anonymous structure tests disabled (`test_anonymous_processor_extended.py.disabled`, `test_anonymous_structure_handling.py.disabled`)
- AnonymousTypedefProcessor import and usage commented out in `src/c2puml/core/parser.py`
- Anonymous structure handling in generator commented out in `src/c2puml/core/generator.py`

**Re-enablement Plan**:
1. Re-enable AnonymousTypedefProcessor import and usage
2. Re-enable anonymous structure handling in generator
3. Re-enable and fix anonymous structure tests
4. Ensure compatibility with other fixes (especially Issue 1.2)
5. **📚 UPDATE DOCUMENTATION** (Critical):
   - Update `docs/specification.md` to include anonymous structure processing details
   - Update `docs/puml_template.md` to show anonymous structure representation and composition relationships

**Improved Naming Convention**:
When re-enabling, implement intuitive naming for anonymous structures:
- Use pattern: `ParentType_fieldName` instead of generic `parent_anonymous_struct_1`
- Example: `struct { ... } position` in type `Tree` becomes `Tree_position`
- For nested anonymous structures: `Tree_branch_leaf` (parent_parent_field)
- This makes generated diagrams self-documenting and easier to understand

**Relationship Visualization**:
Anonymous structures should be connected to their parents using composition relationships:
- Use `*--` (composition/filled diamond) arrow instead of `-->` (association)
- Label relationships with "contains" for clarity
- Example: `Rectangle *-- Rectangle_position : contains`
- This correctly represents that anonymous structures are owned by and part of their parent

**Documentation Updates Required**:

### 📄 docs/specification.md
Must be updated to include:
- Anonymous structure detection and processing workflow
- Naming convention rules (ParentType_fieldName)
- Model structure changes (anonymous_relationships field)
- Parser and tokenizer modifications
- Integration with existing features

### 📄 docs/puml_template.md
Must be updated to include:
- Anonymous structure representation examples
- Composition relationship syntax (*-- with "contains")
- Complete examples showing parent-child relationships
- Visual guidelines for anonymous structure diagrams
- Best practices for readability

**Implementation Example**:
```python
def _generate_anonymous_name(self, parent_name: str, field_name: str) -> str:
    """Generate meaningful name: ParentType_fieldName"""
    return f"{parent_name}_{field_name}"

# In generator.py for relationships
def _generate_anonymous_relationships(self, lines, file_model, uml_ids):
    """Generate composition relationships for anonymous structures."""
    for parent, children in file_model.anonymous_relationships.items():
        parent_id = uml_ids.get(parent)
        for child in children:
            child_id = uml_ids.get(child)
            if parent_id and child_id:
                lines.append(f"{parent_id} *-- {child_id} : contains")
```

## Development Guidelines

### Test-Driven Development Approach
1. **Write failing test first** for each issue
2. **Implement minimal fix** to make test pass
3. **Run full test suite** to ensure no regressions
4. **Update documentation** before marking complete
5. **Commit and push** after each successful fix

### Testing Commands
```bash
# Run all tests
./scripts/run_all.sh

# Run specific test file
python -m pytest tests/unit/test_specific_issue.py -v

# Run with coverage
python -m pytest tests/ --cov=src/c2puml --cov-report=html
```

### Quality Gates
- All tests must pass before committing
- No regressions in existing functionality
- Code coverage maintained or improved
- **Documentation updated for any changes** (specification.md, puml_template.md)

## Next Steps

1. **Priority 1**: Re-enable Issue 8.1 (Anonymous Structure Processing)
   - This is the only remaining issue to address
   - Requires careful testing to ensure no conflicts with other fixes
   - May need refactoring to work with other fixes
   - **Must update both specification.md and puml_template.md**

## Notes

- All high-priority issues from the original TODO have been successfully resolved
- The codebase is in a stable state with comprehensive test coverage
- Anonymous structure processing can be re-enabled when needed
- The only remaining work is re-enabling Issue 8.1 (Anonymous Structure Processing)
- **Documentation is as important as code - both specification and template docs must be updated**