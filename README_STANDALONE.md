# c2puml Standalone Version

This directory contains a standalone version of the c2puml application that can be used directly without installation. This is useful for:

- Quick testing without installing the package
- Running c2puml in environments where you can't install packages
- Distributing c2puml as a single directory
- Development and debugging

## Files

- `c2puml_standalone.py` - The main standalone Python script
- `c2puml_standalone.sh` - Unix/Linux/macOS shell script wrapper
- `c2puml_standalone.bat` - Windows batch file wrapper
- `README_STANDALONE.md` - This documentation file

## Prerequisites

- Python 3.7 or later
- The complete c2puml source code (including the `src/` directory)

## Usage

### Method 1: Direct Python execution

```bash
# Full workflow: Parse → Transform → Generate diagrams
python3 c2puml_standalone.py --config tests/example/config.json

# Using current directory configuration (merges all .json files)
python3 c2puml_standalone.py

# Individual steps
python3 c2puml_standalone.py --config tests/example/config.json parse      # Step 1: Parse only
python3 c2puml_standalone.py --config tests/example/config.json transform  # Step 2: Transform only
python3 c2puml_standalone.py --config tests/example/config.json generate   # Step 3: Generate only

# With verbose output for debugging
python3 c2puml_standalone.py --config tests/example/config.json --verbose
```

### Method 2: Using shell scripts (Unix/Linux/macOS)

```bash
# Make sure the script is executable (should already be done)
chmod +x c2puml_standalone.sh

# Run the application
./c2puml_standalone.sh --config tests/example/config.json
./c2puml_standalone.sh --config tests/example/config.json --verbose
```

### Method 3: Using batch file (Windows)

```cmd
# Run the application
c2puml_standalone.bat --config tests/example/config.json
c2puml_standalone.bat --config tests/example/config.json --verbose
```

## How it works

The standalone version works by:

1. **Path manipulation**: It adds the `src/` directory to Python's module search path
2. **Direct imports**: It imports the c2puml modules directly from the source code
3. **Same functionality**: It provides exactly the same functionality as the installed version

The script automatically detects if it's in the correct location (root directory of the c2puml project) and provides helpful error messages if the required files are missing.

## Example Usage

Here's a complete example of using the standalone version:

```bash
# 1. Navigate to the c2puml project root directory
cd /path/to/c2puml

# 2. Run the standalone version on the example
python3 c2puml_standalone.py --config tests/example/config.json

# 3. Check the output
ls output/
```

## Troubleshooting

### Error: "src directory not found"
- Make sure you're running the script from the root directory of the c2puml project
- Ensure the `src/` directory exists and contains the `c2puml/` package

### Error: "Error importing c2puml modules"
- Check that all required Python files are present in the `src/c2puml/` directory
- Ensure you have Python 3.7 or later installed
- Try running with `--verbose` for more detailed error information

### Error: "Python is not installed"
- Install Python 3.7 or later
- Make sure Python is in your system PATH
- On Windows, you might need to use `python` instead of `python3`

## Advantages of the Standalone Version

1. **No installation required**: Just run the script directly
2. **Portable**: Can be easily copied to other systems
3. **Development friendly**: Easy to modify and test changes
4. **Environment isolation**: Doesn't interfere with system Python packages
5. **Quick testing**: Ideal for trying out c2puml without commitment

## Limitations

1. **Requires source code**: You need the complete c2puml source code
2. **No package management**: Dependencies must be installed manually if needed
3. **Path dependency**: Must be run from the correct directory

## Comparison with Installed Version

| Feature | Standalone | Installed |
|---------|------------|-----------|
| Installation | None required | `pip install -e .` |
| Command | `python3 c2puml_standalone.py` | `c2puml` |
| Portability | High (copy files) | Low (system dependent) |
| Updates | Manual (update source) | `pip install --upgrade` |
| Dependencies | Manual management | Automatic via pip |

## Integration with Existing Scripts

The standalone version can be easily integrated into existing build scripts or CI/CD pipelines:

```bash
# In a build script
python3 c2puml_standalone.py --config config.json --verbose

# In a CI/CD pipeline
- name: Generate PlantUML diagrams
  run: python3 c2puml_standalone.py --config config.json
```

## Support

For issues with the standalone version:

1. Check that you're running from the correct directory
2. Verify all source files are present
3. Try running with `--verbose` for detailed error messages
4. Compare with the installed version behavior
5. Check the main project documentation for configuration details