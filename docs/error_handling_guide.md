# Error Handling Guide

This guide documents the enhanced error handling in the C to PlantUML converter, particularly focusing on invalid source path handling and other common issues.

## Overview

The library has been enhanced with comprehensive error handling to prevent crashes and provide helpful error messages when invalid source paths are configured. Instead of crashing, the library now provides detailed error messages with suggestions for resolution.

## Enhanced Source Path Validation

### Invalid Source Path Scenarios

The library now handles the following invalid source path scenarios gracefully:

1. **Nonexistent paths**
2. **Files instead of directories**
3. **Empty or whitespace-only paths**
4. **Non-string values**
5. **Permission denied errors**
6. **Relative path resolution issues**

### Error Message Examples

#### Nonexistent Path
```bash
$ c2puml --config config.json
ValueError: Source folder not found: /nonexistent/path
Parent directory does not exist: /nonexistent
```

#### File Instead of Directory
```bash
$ c2puml --config config.json
ValueError: Source folder must be a directory, got: /path/to/file.txt (is_file: True)
```

#### Relative Path Issues
```bash
$ c2puml --config config.json
ValueError: Source folder not found: /workspace/nonexistent/relative/path
Current working directory: /workspace
Tried to resolve relative path: nonexistent/relative/path
Parent directory does not exist: /workspace/nonexistent/relative
```

#### Permission Denied
```bash
$ c2puml --config config.json
ValueError: Permission denied accessing source folder: /restricted/path
```

#### Empty or Invalid Configuration
```bash
$ c2puml --config config.json
ValueError: Source folder cannot be empty or whitespace
```

### Helpful Error Context

The enhanced error messages provide additional context to help users resolve issues:

- **Current working directory** when relative paths fail
- **Parent directory information** when paths don't exist
- **Available directories** in parent folders
- **File vs directory detection** with clear indicators
- **Permission information** for access issues

## Configuration Validation

### Source Folders Validation

The configuration system now validates source folders more thoroughly:

```python
# Valid configuration
{
    "source_folders": ["./src", "./include"],
    "project_name": "MyProject"
}

# Invalid configurations that will be caught:
{
    "source_folders": [],  # Empty list
    "source_folders": "not_a_list",  # Not a list
    "source_folders": ["", "valid_path"],  # Empty string
    "source_folders": [123, "valid_path"],  # Non-string
    # Missing source_folders field
}
```

### Error Messages for Configuration Issues

```bash
# Empty source_folders list
ValueError: 'source_folders' list cannot be empty

# Non-list source_folders
ValueError: 'source_folders' must be a list, got: <class 'str'>

# Missing source_folders field
ValueError: Configuration must contain 'source_folders' field

# Invalid JSON
ValueError: Invalid JSON in configuration file config.json: Expecting ',' delimiter
```

## Multiple Source Folders Handling

The library now handles multiple source folders more gracefully:

### Partial Failures
When some source folders fail but others succeed, the library:
- Continues processing valid folders
- Logs warnings for failed folders
- Returns a combined model from successful folders
- Provides detailed error information

### All Failures
When all source folders fail, the library provides a comprehensive error message:

```bash
RuntimeError: All source folders failed to parse:
  - /nonexistent/path1: Source folder not found: /nonexistent/path1
  - /nonexistent/path2: Source folder not found: /nonexistent/path2
```

## CLI Error Handling

The command-line interface provides additional context for common issues:

### Source Folder Not Found
```bash
Error in workflow: Source folder not found: /nonexistent/path
Please check that the source_folders in your configuration exist and are accessible.
You can use absolute paths or relative paths from the current working directory.
```

### Permission Issues
```bash
Error in workflow: Permission denied accessing source folder: /restricted/path
Please check file permissions for the source folders.
```

### Configuration Issues
```bash
Error in workflow: Invalid JSON in configuration file config.json
Please check that your configuration file contains valid JSON.
```

## File System Error Handling

### File Search Robustness
The file search process now handles various file system errors:

- **Permission errors** during directory traversal
- **Non-existent files** discovered during search
- **Non-file items** (directories, symlinks) in search results
- **Access errors** for individual files

### Graceful Degradation
When file system errors occur:
- Individual file errors are logged as warnings
- Processing continues with accessible files
- Comprehensive error reporting at the end
- No crashes due to file system issues

## Testing Error Handling

The library includes comprehensive tests for error handling:

```bash
# Run error handling tests
python3 -m pytest tests/feature/test_invalid_source_paths.py -v
```

### Test Coverage
The error handling tests cover:
- Nonexistent source folders
- Files as source folders
- Empty and whitespace paths
- Non-string values
- Permission denied scenarios
- Relative path resolution
- Configuration validation
- Multiple source folder scenarios

## Best Practices

### Configuration
1. **Use absolute paths** for critical projects
2. **Use relative paths** from project root for portability
3. **Validate paths** before running the tool
4. **Check permissions** for source directories

### Error Resolution
1. **Read error messages carefully** - they contain helpful information
2. **Check current working directory** for relative path issues
3. **Verify file permissions** for access issues
4. **Use absolute paths** if relative paths are problematic
5. **Check configuration syntax** for JSON errors

### Development
1. **Test with invalid paths** during development
2. **Use the error handling tests** as examples
3. **Add new error scenarios** to the test suite
4. **Update error messages** to be helpful and actionable

## Migration from Previous Versions

### Behavior Changes
- **No more crashes** on invalid source paths
- **Detailed error messages** instead of generic exceptions
- **Graceful handling** of partial failures
- **Better configuration validation**

### Backward Compatibility
- All existing valid configurations continue to work
- No changes to successful execution paths
- Enhanced error handling is additive only

## Troubleshooting

### Common Issues and Solutions

#### "Source folder not found"
**Cause**: The configured source folder doesn't exist
**Solution**: 
- Check the path spelling
- Use absolute paths if relative paths are unclear
- Verify the path exists and is accessible

#### "Source folder must be a directory"
**Cause**: The path points to a file instead of a directory
**Solution**: 
- Check if the path is correct
- Ensure you're pointing to a directory, not a file
- Use the parent directory if needed

#### "Permission denied"
**Cause**: Insufficient permissions to access the directory
**Solution**:
- Check file permissions
- Run with appropriate user privileges
- Use a different source directory

#### "Configuration must contain 'source_folders' field"
**Cause**: Missing or invalid configuration
**Solution**:
- Ensure your config.json has a "source_folders" field
- Check JSON syntax
- Use the example configuration as a template

### Getting Help

If you encounter issues not covered in this guide:

1. **Check the error message** for specific details
2. **Review your configuration** for syntax errors
3. **Test with a simple configuration** first
4. **Run the error handling tests** to see examples
5. **Check file permissions** and accessibility

## Conclusion

The enhanced error handling makes the C to PlantUML converter more robust and user-friendly. Instead of crashing on invalid source paths, the library now provides helpful error messages that guide users to resolution. This improves the overall user experience and makes the tool more reliable in production environments.