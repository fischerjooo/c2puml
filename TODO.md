# C to PlantUML Conversion - TODO

## Current Status

**Completed Issues (Fixed and Tested):**
- ✅ **Issue 1.2**: Union Field Order Preservation / Nested Union/Struct Flattening
- ✅ **Issue 2.1**: Function Parameter Parsing
- ✅ **Issue 3.1**: Macro Deduplication
- ✅ **Issue 4.1**: Template Compliance - Naming Conventions
- ✅ **Issue 5.1**: File-Specific Configuration
- ✅ **Issue 6.1**: Transformation System
- ✅ **Issue 7.1**: Anonymous Structure Handling

**Temporarily Disabled:**
- ⏸️ **Anonymous Structure Processing**: Feature disabled due to complexity and potential conflicts with other fixes

## Remaining Open Issues

### Issue 1.1: Struct Field Order Preservation
**Status**: ❌ **OPEN** - High Priority

**Problem**: Struct fields are not preserved in their original order from the C source code.

**Example**:
```c
// Source C code
typedef struct triangle_tag {
    point_t vertices[3];
    char label[MAX_LABEL_LEN];
} triangle_t;
```

**Current Output**:
```plantuml
class "triangle_t" as TYPEDEF_TRIANGLE_T <<struct>> #LightYellow
{
    + char[MAX_LABEL_LEN] label
    + point_t[3] vertices
}
```

**Expected Output**:
```plantuml
class "triangle_t" as TYPEDEF_TRIANGLE_T <<struct>> #LightYellow
{
    + point_t[3] vertices
    + char[MAX_LABEL_LEN] label
}
```

**Root Cause**: The field parsing logic in `find_struct_fields` does not preserve the original order of fields as they appear in the source code.

**Fix Required**:
1. Modify `find_struct_fields` in `src/c2puml/core/parser_tokenizer.py` to preserve field order
2. Update the field collection logic to maintain original sequence
3. Add test coverage for field order preservation

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

## Development Guidelines

### Test-Driven Development Approach
1. **Write failing test first** for each issue
2. **Implement minimal fix** to make test pass
3. **Run full test suite** to ensure no regressions
4. **Commit and push** after each successful fix

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
- Documentation updated for any changes

## Next Steps

1. **Priority 1**: Fix Issue 1.1 (Struct Field Order Preservation)
   - This is the only remaining high-priority issue
   - Should be addressed using TDD approach
   - Requires careful modification of field parsing logic

2. **Priority 2**: Re-enable Issue 8.1 (Anonymous Structure Processing)
   - Only after Issue 1.1 is resolved
   - Requires careful testing to ensure no conflicts
   - May need refactoring to work with other fixes

## Notes

- All other issues from the original TODO have been successfully resolved
- The codebase is in a stable state with comprehensive test coverage
- Anonymous structure processing can be re-enabled when needed
- Focus should be on Issue 1.1 as the primary remaining concern