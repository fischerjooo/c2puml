# Development Workflow - Agent LLM Guidance

## Overview
This document provides high-level guidance for developing new features or making code changes to the C to PlantUML converter project. Always prioritize code cleanup and simplification while maintaining clean coding practices, human readability, and testability.

## Workflow Steps

### 1. Specification Analysis
- Review current specification and requirements
- Update specification if new requirements extend functionality
- Ensure requirements align with project architecture

### 2. Design and Planning
- Identify affected components and design changes
- Plan implementation approach and test strategy
- Consider backward compatibility and API changes

### 3. Implementation
- Implement feature following existing patterns
- Apply code cleanup and simplification throughout
- Focus on readability, maintainability, and testability
- Ensure proper error handling and validation

### 4. Testing
- Create comprehensive tests for new functionality
- Improve existing test quality and coverage
- Verify integration with existing workflows
- Validate output quality and performance

### 5. Validation
- Execute test suite and integration tests
- Verify PlantUML output correctness
- Test with real projects when possible
- Document any performance impacts

### 6. Documentation
- Update relevant documentation files
- Add usage examples for new features
- Update configuration examples if needed

### 7. Delivery
- Create feature branch and commit changes
- Submit pull request with complete change set
- Include test results and documentation updates

## Quality Gates

### Before Implementation
- [ ] Requirements understood and specification updated if needed
- [ ] Design approach planned
- [ ] Code cleanup opportunities identified

### Before Testing
- [ ] Code follows project patterns and style
- [ ] Error handling and validation implemented
- [ ] Code quality improved (cleaner, more readable, more testable)

### Before Delivery
- [ ] All tests pass and output validated
- [ ] Documentation updated
- [ ] Performance and compatibility verified

## Common Patterns

### Adding New Configuration Options
- Update configuration schema and transformer logic
- Add validation and test configurations
- Update documentation with examples

### Adding New Parser Capabilities
- Extend parser with new parsing methods
- Update data models and generators as needed
- Add tests with sample code containing new constructs

### Adding New Output Formats
- Create new generator following existing patterns
- Add CLI commands and validation
- Update documentation with format examples

## Code Quality Guidelines

### Clean Code Practices
- Follow single responsibility principle
- Eliminate code duplication
- Use meaningful names and clear structure
- Keep functions focused and readable

### Readability Improvements
- Break down complex logic into helper functions
- Extract constants and improve organization
- Reduce nesting and improve flow

### Testability Enhancements
- Extract pure functions where possible
- Separate concerns and reduce dependencies
- Create focused, maintainable tests

## Error Handling and Performance

- Validate inputs and provide clear error messages
- Handle edge cases gracefully
- Optimize performance for large codebases
- Use caching and efficient algorithms

## Continuous Improvement

Always look for opportunities to:
- Simplify complex code
- Remove duplication and improve structure
- Enhance readability and maintainability
- Improve test quality and coverage

This workflow ensures high-quality development with continuous focus on code improvement and maintainability.