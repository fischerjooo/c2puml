# Development Workflow - Agent LLM Guidance

## Overview
This document provides step-by-step guidance for developing new features or making code changes to the C to PlantUML converter project. Follow this workflow to ensure consistent, high-quality development practices with a focus on clean code, readability, and testability.

**IMPORTANT**: Always prioritize code cleanup and simplification. When working on any feature or change, continuously look for opportunities to improve existing code quality, enhance readability, and increase testability.

## Workflow Steps

### 1. Specification Analysis and Update
**Objective**: Understand current requirements and update specification if needed

**Actions**:
- Read `specification.md` to understand current system capabilities
- Analyze user requirements against existing specification
- If new requirements extend current functionality:
  - Update `specification.md` with new requirements
  - Add new requirements to appropriate sections (Core/Advanced/Quality)
  - Update architecture diagrams if component changes are needed
- If requirements fit existing specification, proceed to design

**Deliverables**: Updated specification (if needed)

### 2. Design and Planning
**Objective**: Create detailed design for the feature/change

**Actions**:
- Identify affected components from the architecture
- Design new/modified data structures if needed
- Plan API changes and backward compatibility
- Create implementation plan with:
  - Component modifications required
  - New files to create
  - Configuration schema changes (if any)
  - Test strategy
- Document design decisions in comments or separate design file

**Deliverables**: Implementation plan, design documentation

### 3. Implementation
**Objective**: Implement the feature according to design

**Actions**:
- Follow existing code patterns and style
- Implement changes in appropriate modules:
  - `c_to_plantuml/` for core functionality
  - `packager/` for output packaging
  - Configuration files for new options
- Add proper error handling and validation
- Include comprehensive docstrings and comments
- Ensure backward compatibility unless breaking changes are required
- Update `__init__.py` files if new modules are added
- **Code Cleanup**: Refactor complex functions, remove duplication, improve variable names
- **Readability**: Break down large functions, add clear comments, improve code structure
- **Testability**: Extract pure functions, reduce side effects, add dependency injection where beneficial

**Deliverables**: Working code implementation with improved quality

### 4. Testing Strategy
**Objective**: Ensure feature works correctly and doesn't break existing functionality

**Actions**:
- **Unit Tests**: Create/modify tests in `tests/` directory
  - Test new functions and classes
  - Test edge cases and error conditions
  - Ensure existing tests still pass
  - **Improve Test Quality**: Refactor existing tests for better readability and maintainability
  - **Test Coverage**: Add tests for previously untested code paths
- **Integration Tests**: Test complete workflows
  - Use existing test configurations in `config/`
  - Test with sample C files in `tests/test_files/`
  - Verify PlantUML output format
- **Configuration Tests**: Test new configuration options
  - Create test config files
  - Verify parsing and application of new settings
- **Test Cleanup**: Simplify complex test setups, remove test duplication, improve test data organization

**Deliverables**: Test files, test configurations with improved quality

### 5. Verification and Validation
**Objective**: Execute tests and validate implementation

**Actions**:
- Run test suite: `python -m pytest tests/`
- Execute integration tests:
  ```bash
  python -m c_to_plantuml.main config test_config.json
  python -m c_to_plantuml.main filter model.json filter_config.json
  ```
- Verify PlantUML output quality:
  - Check generated `.puml` files
  - Validate syntax with PlantUML renderer
  - Ensure proper styling and formatting
- Test with real C projects if available
- Verify performance impact (if significant changes)

**Deliverables**: Test results, validation report

### 6. Documentation Update
**Objective**: Update project documentation

**Actions**:
- Update `README.md` if new features affect user interface
- Update configuration examples if new options added
- Update `IMPLEMENTATION_COMPLETE.md` for significant features
- Add usage examples for new functionality
- Update any relevant guides in project root

**Deliverables**: Updated documentation

### 7. Repository Integration
**Objective**: Deliver changes to repository

**Actions**:
- Create feature branch: `git checkout -b feature/description`
- Stage changes: `git add .`
- Commit with descriptive message:
  ```
  feat: add [feature description]
  
  - Brief description of changes
  - Any breaking changes noted
  - Related issue numbers
  ```
- Push branch: `git push origin feature/description`
- Create pull request with:
  - Description of changes
  - Test results summary
  - Any configuration changes needed
  - Screenshots of new PlantUML output (if visual changes)

**Deliverables**: Pull request with complete change set

## Quality Gates

### Before Implementation
- [ ] Specification updated (if needed)
- [ ] Design reviewed and approved
- [ ] Implementation plan complete
- [ ] Code cleanup opportunities identified

### Before Testing
- [ ] Code follows project style
- [ ] All functions documented
- [ ] Error handling implemented
- [ ] Backward compatibility maintained
- [ ] Complex functions refactored for readability
- [ ] Duplicate code eliminated
- [ ] Variable and function names are clear and descriptive

### Before Delivery
- [ ] All tests pass
- [ ] PlantUML output validated
- [ ] Documentation updated
- [ ] Performance acceptable
- [ ] No breaking changes (or documented)
- [ ] Code quality improved (cleaner, more readable, more testable)
- [ ] Test quality improved (simpler, more maintainable)

## Common Patterns

### Adding New Configuration Options
1. Update configuration schema in `enhanced_config.json`
2. Modify `ModelTransformer` to handle new options
3. Add validation in configuration loading
4. Create test configuration files
5. Update documentation with examples

### Adding New Parser Capabilities
1. Extend `CParser` class with new parsing methods
2. Update data models in `c_structures.py` if needed
3. Modify `PlantUMLGenerator` to output new elements
4. Add tests with sample C code containing new constructs
5. Update specification with new capabilities

### Adding New Output Formats
1. Create new generator in `generators/` directory
2. Follow existing `PlantUMLGenerator` patterns
3. Add CLI command in `main.py`
4. Create test outputs and validate format
5. Update documentation with new format examples

## Code Quality Guidelines

### Clean Code Practices
- **Single Responsibility**: Each function/class should have one clear purpose
- **DRY Principle**: Eliminate code duplication through extraction and reuse
- **Meaningful Names**: Use descriptive variable, function, and class names
- **Small Functions**: Keep functions under 20 lines when possible
- **Clear Comments**: Explain "why" not "what" in comments
- **Consistent Formatting**: Follow project style guidelines

### Readability Improvements
- Break down complex conditional logic into helper functions
- Extract magic numbers and strings into named constants
- Use early returns to reduce nesting
- Group related functionality into cohesive modules
- Add type hints where beneficial for clarity

### Testability Enhancements
- Extract pure functions that don't depend on external state
- Use dependency injection for external dependencies
- Separate business logic from I/O operations
- Create small, focused test functions
- Use descriptive test names that explain the scenario

## Error Handling Guidelines

- Always validate input parameters
- Provide meaningful error messages
- Log errors for debugging
- Gracefully handle malformed C code
- Continue processing when possible (don't fail fast on non-critical errors)

## Performance Considerations

- Use pre-compiled regex patterns for filtering
- Implement caching for expensive operations
- Profile large project analysis
- Consider memory usage for large codebases
- Optimize file I/O operations

## Continuous Improvement Checklist

During any development task, always ask:
- [ ] Can this code be simplified?
- [ ] Are there any code smells (long functions, duplication, unclear names)?
- [ ] Can I extract reusable components?
- [ ] Are the tests clear and maintainable?
- [ ] Is the code self-documenting?
- [ ] Can I improve error handling or validation?
- [ ] Are there opportunities to reduce complexity?

This workflow ensures consistent, high-quality development while maintaining the project's architecture and quality standards, with a continuous focus on code improvement and maintainability.