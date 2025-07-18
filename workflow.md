# Development Workflow - Agent LLM Guidance

## Overview
This document provides high-level guidance for developing new features or making code changes to the C to PlantUML converter project. Always prioritize code cleanup and simplification while maintaining clean coding practices, human readability, and testability.

## Processing Flow
The application follows a clear 3-step processing flow:
1. **Parse C/C++ files and generate model** - Extract structural information from source code
2. **Apply configuration/transformers** - Filter and transform the model based on configuration
3. **Generate PlantUML files** - Convert the transformed model into PlantUML diagrams

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

## Testing Structure

### Test Organization
All tests are organized under the `tests/` directory with the following structure:
```
tests/
├── test_parser.py          # Parser functionality tests
├── test_project_analyzer.py # Project analysis tests
├── test_config.py          # Configuration functionality tests
├── test_generator.py       # PlantUML generation tests
├── test_integration.py     # Complete workflow tests
├── test_files/             # Test input files
│   ├── sample.c
│   ├── sample.h
│   ├── complex_example.c
│   └── complex_example.h
├── test_output/            # Expected output files
│   └── expected_main.puml
├── test_config.json        # Test configuration
└── run_tests.py           # Test runner script
```

### Test Categories
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows and component interactions
- **Configuration Tests**: Test configuration loading, validation, and filtering
- **Output Verification Tests**: Test PlantUML generation and output quality

### Running Tests
```bash
# Run all tests
python tests/run_tests.py

# Run specific test module
python tests/run_tests.py test_config

# Run with unittest directly
python -m unittest discover tests/
```

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