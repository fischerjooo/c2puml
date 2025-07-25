# Coverage Testing and Report Generation

This document explains how to run tests and generate coverage reports both locally and in CI/CD.

## 🏠 Local Development

### Quick Start

For basic testing without coverage (fastest):
```bash
bash run_all_tests.sh
```

For basic testing with HTML coverage reports:
```bash
./run_tests_with_coverage.sh
```

For comprehensive coverage analysis with multiple formats:
```bash
./generate_coverage_reports.sh
```

For two-step approach (run tests, then generate reports separately):
```bash
# Step 1: Run tests with coverage
./run_tests_coverage.sh

# Step 2: Generate reports from coverage data
./generate_coverage_reports_only.sh
```

### Script Options

#### `./generate_coverage_reports.sh [format] [verbosity]`

**Parameters:**
- `format`: Coverage report format - `all`, `html`, `xml`, `json` (default: `all`)
- `verbosity`: Test output verbosity - `0`, `1`, `2` (default: `1`)

**Examples:**
```bash
# Generate all report formats with default verbosity
./generate_coverage_reports.sh

# Generate only HTML reports with high verbosity
./generate_coverage_reports.sh html 2

# Generate XML and JSON reports with minimal output
./generate_coverage_reports.sh xml 0

# Two-step approach examples
./run_tests_coverage.sh 2          # Run tests with high verbosity
./generate_coverage_reports_only.sh html  # Generate only HTML reports

# Or run with different parameters
./run_tests_coverage.sh 0          # Run tests with minimal output
./generate_coverage_reports_only.sh all   # Generate all report formats
```

#### `./run_tests_with_coverage.sh`

Simple script that:
- Runs all tests with coverage
- Generates HTML coverage reports
- Creates a coverage dashboard
- Displays summary information

#### `./run_tests_coverage.sh [verbosity]`

Test execution only script:
- Runs tests with coverage collection
- Saves test execution logs
- Does NOT generate reports
- verbosity: `0`, `1`, `2` (default: `1`)

#### `./generate_coverage_reports_only.sh [format]`

Report generation only script:
- Generates reports from existing coverage data
- Requires coverage data to exist (run tests first)
- format: `all`, `html`, `xml`, `json` (default: `all`)
- Creates comprehensive coverage dashboard

## 📊 Generated Reports

All reports are generated in the `tests/reports/` directory:

```
tests/reports/
├── coverage-index.html          # Main dashboard linking all reports
├── coverage-html/               # Interactive HTML coverage reports
│   ├── index.html              # Main HTML coverage report
│   └── [source files].html    # Individual file coverage
├── coverage-annotated/         # Source files with coverage annotations
├── coverage-summary.txt        # Text summary
├── coverage-detailed.txt       # Detailed missing lines
├── coverage.xml               # XML format (for CI tools)
├── coverage.json              # JSON format (for programmatic access)
└── test-results.txt           # Test execution logs
```

## 🌐 Viewing Reports

After running either script, open the coverage dashboard in your browser:

```bash
# The script will display the file URL, or you can open directly:
open tests/reports/coverage-index.html

# Or for Linux:
xdg-open tests/reports/coverage-index.html

# Or manually navigate to:
file:///path/to/your/project/tests/reports/coverage-index.html
```

## 🔧 Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install coverage[toml] pytest-cov
```

Or install all development dependencies:

```bash
pip install -r requirements-dev.txt
```

## 🚀 CI/CD Integration

### GitHub Actions Workflows

The project includes two GitHub Actions workflows:

1. **`test.yml`** - Basic testing without coverage (runs on every push/PR)
2. **`test-coverage.yml`** - Two-step coverage analysis: runs tests with coverage, then generates reports (manual trigger or PR merge)

The coverage workflow uses a two-step approach:
- **Step 1**: `./run_tests_coverage.sh` - Executes tests and collects coverage data
- **Step 2**: `./generate_coverage_reports_only.sh` - Generates comprehensive reports from coverage data

This separation allows for better error handling and more granular control over the coverage process.

### Workflow Inputs

The `test-coverage.yml` workflow accepts manual inputs:

- **Coverage Format**: `all`, `html`, `xml`, `json`
- **Test Verbosity**: `0`, `1`, `2`

## 📈 Coverage Analysis

### Understanding Coverage Reports

- **Green lines**: Code that was executed during testing
- **Red lines**: Code that was not executed during testing
- **Excluded lines**: Code explicitly excluded from coverage analysis

### Improving Coverage

1. **Identify uncovered code**: Use the HTML report to see exactly which lines need tests
2. **Write targeted tests**: Focus on uncovered branches and edge cases
3. **Review exclusions**: Ensure coverage exclusions in `.coveragerc` are appropriate
4. **Monitor trends**: Track coverage percentage over time

### Coverage Thresholds

Current coverage configuration is defined in `.coveragerc`. Consider setting minimum thresholds for:
- Overall project coverage
- Individual file coverage
- New code coverage (for PRs)

## 🛠️ Customization

### Modifying Report Generation

To customize the coverage reports:

1. **Edit the shell scripts** directly for immediate changes
2. **Update `.coveragerc`** for coverage tool configuration
3. **Modify the HTML templates** in the scripts for custom styling

### Adding New Report Formats

To add new report formats:

1. Add the new format logic to `generate_coverage_reports.sh`
2. Update the coverage dashboard HTML template
3. Add corresponding links in the existing reports

## 🐛 Troubleshooting

### Common Issues

**No coverage data found:**
```bash
# Ensure tests are run with coverage
coverage erase
coverage run -m unittest discover tests -v
```

**Permission denied:**
```bash
# Make scripts executable
chmod +x *.sh
```

**Missing dependencies:**
```bash
# Install coverage tools
pip install coverage[toml] pytest-cov
```

**HTML reports not displaying:**
- Check that `tests/reports/coverage-html/index.html` exists
- Verify file permissions
- Try opening the file directly in a browser

### Debug Mode

For debugging test execution:

```bash
# Run with maximum verbosity
./generate_coverage_reports.sh all 2

# Run coverage commands manually
coverage erase
coverage run -m unittest discover tests -v -v
coverage report -m
```