# Test Coverage Workflow Documentation

## 🚀 Overview

The `test-coverage.yml` GitHub Actions workflow provides comprehensive automated testing and coverage reporting for the C to PlantUML Converter project.

## 🔄 Automatic Triggers

The workflow runs automatically in these scenarios:

### 1. Push to Main Branch
```bash
git push origin main
```
- Runs full test suite with coverage
- Commits coverage reports back to repository
- Updates `tests/reports/` directory

### 2. Pull Request Closure
- Triggers when a PR is merged into main/master
- Generates coverage reports for the merged code
- Useful for tracking coverage changes from PRs

## 🎯 Manual Execution

### Via GitHub UI
1. Go to **Actions** tab in your repository
2. Select **"Test Suite with Coverage Reports"** workflow  
3. Click **"Run workflow"** button
4. Configure options:
   - **Coverage format**: `all`, `html`, `xml`, or `json`
   - **Test verbosity**: `0` (quiet), `1` (normal), `2` (verbose)

### Via GitHub CLI
```bash
# Run with default settings
gh workflow run test-coverage.yml

# Run with custom options
gh workflow run test-coverage.yml \
  -f coverage_format=html \
  -f test_verbosity=2
```

## 📊 Generated Reports

### Report Locations
All reports are saved in `tests/reports/`:

```
tests/reports/
├── test-results.txt          # Complete test output
├── test-summary.md           # Formatted summary with metadata
├── coverage-summary.txt      # Coverage overview
├── coverage-detailed.txt     # Line-by-line coverage details
├── coverage.xml              # XML format (CI/CD compatible)
├── coverage.json             # JSON format (programmatic access)
└── coverage-html/            # Interactive HTML reports
    ├── index.html            # Main coverage dashboard
    └── ...                   # Detailed file reports
```

### Report Contents

#### Test Summary (`test-summary.md`)
- Execution timestamp and metadata
- Git branch and commit information
- Python version details
- Test execution results
- Coverage overview
- Workflow run information

#### Coverage Reports
- **HTML**: Interactive web interface with file-by-file coverage
- **XML**: Standard format for CI/CD integration (Codecov, etc.)
- **JSON**: Machine-readable format for custom analysis
- **Text**: Human-readable summaries for quick review

## 🐍 Multi-Python Testing

The workflow tests against multiple Python versions:
- Python 3.9 (primary - used for coverage commits)
- Python 3.10
- Python 3.11

Only Python 3.9 results are committed to avoid conflicts.

## 📈 Coverage Configuration

Coverage analysis is configured via `.coveragerc`:

### Source Analysis
- **Target**: `c_to_plantuml/` directory
- **Excludes**: Tests, virtual environments, cache files

### Report Options
- **Missing lines**: Shown in detailed reports
- **Precision**: 2 decimal places
- **Skip covered**: Disabled (shows all files)

### Output Formats
- **HTML**: `tests/reports/coverage-html/`
- **XML**: `tests/reports/coverage.xml`
- **JSON**: `tests/reports/coverage.json`

## 🔧 Customization

### Coverage Format Options
- `all`: Generate HTML, XML, and JSON reports
- `html`: Only HTML interactive reports
- `xml`: Only XML reports (CI/CD integration)
- `json`: Only JSON reports (programmatic use)

### Verbosity Levels
- `0`: Minimal output (errors only)
- `1`: Normal output (default)
- `2`: Verbose output (detailed information)

## 📋 Workflow Features

### ✅ Capabilities
- **Sequential execution**: No parallel test conflicts
- **Comprehensive reporting**: Multiple formats and detailed analysis
- **Automatic commits**: Reports pushed to repository on main branch
- **Artifact uploads**: 30-day retention for all reports
- **Codecov integration**: Optional external coverage service
- **Multi-platform**: Tested on Ubuntu latest
- **Caching**: pip dependencies cached for faster execution

### 🎯 Benefits
- **Automated coverage tracking**: No manual intervention required
- **Historical analysis**: Reports stored in repository for trend analysis
- **CI/CD integration**: Multiple output formats for different tools
- **Developer friendly**: Clear, actionable coverage information
- **Quality assurance**: Ensures all code changes are properly tested

## 🚨 Troubleshooting

### Common Issues

#### 1. Coverage Not Generated
```bash
# Check if coverage tools are installed
pip install coverage pytest-cov

# Verify run_all_tests.py supports coverage
python run_all_tests.py --coverage --help
```

#### 2. Workflow Permissions
Ensure the repository has write permissions for GitHub Actions to commit reports.

#### 3. Missing Dependencies
The workflow installs all required dependencies, but local testing may need:
```bash
pip install -r requirements-dev.txt
pip install coverage[toml] pytest-cov
```

### Debug Steps
1. Check workflow logs in GitHub Actions tab
2. Review artifact downloads for generated reports
3. Verify `.coveragerc` configuration
4. Test coverage locally: `python run_all_tests.py --coverage`

## 🔗 Integration

### Codecov Setup (Optional)
1. Add `CODECOV_TOKEN` to repository secrets
2. Coverage XML reports automatically uploaded
3. Configure coverage thresholds in `codecov.yml`

### Badge Integration
Add coverage badge to README:
```markdown
[![Coverage](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/username/repo)
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Pytest Coverage Plugin](https://pytest-cov.readthedocs.io/)
- [Codecov Documentation](https://docs.codecov.io/)

---

*For questions or issues, please create an issue in the repository.*