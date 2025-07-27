# Coverage Report Generation

This project uses a simplified approach to generate coverage reports using the standard `coverage` tool.

## Overview

The `generate_combined_coverage.py` script has been greatly simplified to:

1. **Run tests with coverage** (optional, using `--run-tests` flag)
2. **Generate standard coverage reports** including:
   - Terminal summary
   - XML report (`coverage.xml`)
   - JSON report (`coverage.json`)
   - **HTML report in `htmlcov/` directory** (the main output)

## Usage

### Generate reports from existing coverage data:
```bash
python3 generate_combined_coverage.py
```

### Run tests and generate reports:
```bash
python3 generate_combined_coverage.py --run-tests
```

### Use custom output directory:
```bash
python3 generate_combined_coverage.py --output-dir custom/path
```

## Output

The script generates the following files in the output directory (default: `tests/reports/coverage/`):

- `htmlcov/` - **Standard coverage HTML report** (main output)
  - `index.html` - Main coverage report page
  - Individual HTML files for each source file
  - CSS, JavaScript, and image assets
- `coverage.xml` - XML format report
- `coverage.json` - JSON format report
- Terminal output with coverage summary

## Key Changes

### Before (Complex):
- Custom HTML generation for each Python file
- Complex index.html with custom styling
- Test result parsing and custom test summary
- 1,284 lines of code

### After (Simplified):
- Uses standard `coverage html` command
- Leverages the excellent built-in HTML report
- Clean, maintainable code
- ~100 lines of code

## Benefits

1. **Maintainability**: Much simpler codebase
2. **Reliability**: Uses battle-tested coverage tool output
3. **Features**: Standard HTML report includes:
   - Interactive file browser
   - Line-by-line coverage highlighting
   - Missing lines identification
   - Branch coverage (if enabled)
   - Search functionality
4. **Git Integration**: The `htmlcov/` directory is tracked in git for easy sharing

## Viewing Reports

Open `tests/reports/coverage/htmlcov/index.html` in your web browser to view the coverage report.

The standard coverage HTML report provides:
- Overall project coverage statistics
- Per-file coverage breakdown
- Interactive file browser
- Line-by-line coverage details
- Missing lines highlighting
- Search and filter capabilities