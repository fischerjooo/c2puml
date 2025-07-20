# Test Automation

This project uses GitHub Actions to automatically run tests on every push and pull request using a single simplified workflow.

## 🚀 Automated Testing

### GitHub Actions Workflow

The project includes a simple test workflow (`.github/workflows/test.yml`) that:

- **Triggers on**: Push to main/master, PRs, manual dispatch
- **Python version**: 3.9 only
- **Runs**: Comprehensive test suite using `run_all_tests.py`
- **Simple**: Single file execution for all tests

### Workflow Steps

1. **Checkout code** from the repository
2. **Setup Python** environment (3.9)
3. **Install dependencies** from requirements.txt
4. **Run all tests** using the single test script

### Local Testing

To run tests locally:

```bash
# Install dependencies
pip install -e .
pip install -r requirements.txt

# Run all tests
python run_all_tests.py
```

### Test Structure

- **Single Test Runner**: `run_all_tests.py` - Comprehensive test suite
- **Unit Tests**: `tests/unit/` - Individual component tests
- **Feature Tests**: `tests/feature/` - End-to-end feature tests

### Test Results

The workflow provides:

- ✅ **Pass/Fail Status**: Clear indication of test results
- 📊 **Test Summary**: Number of tests run, passed, failed
- 🔄 **Single Python**: Tests on Python 3.9 only

## 🎯 Best Practices

1. **Always run tests locally** before pushing
2. **Check GitHub Actions** for test results
3. **Fix failing tests** before merging PRs
4. **Use the single test script** for consistent results

## 📝 Contributing

When contributing:

1. Write tests for new features
2. Ensure all tests pass locally
3. Push your changes
4. Check GitHub Actions for automated test results
5. Address any test failures before merging

The automated testing ensures code quality and prevents regressions using a simple, reliable approach.