# E2E Test Execution and Reporting Guide

This guide covers test execution, result analysis, and reporting for the Selenium E2E test suite.

## Quick Commands Reference

```bash
# Install and run all tests
pip install -r requirements.txt && pytest

# Run specific test suite
pytest test_dashboard_ui.py
pytest test_session_creation.py
pytest test_api_integration.py
pytest test_edge_cases.py

# Run with reporting
pytest -v --html=report.html --tb=short
pytest --cov=. --cov-report=html
pytest -v --tb=long

# Run in parallel
pytest -n 4 -v

# Run specific test class
pytest test_dashboard_ui.py::TestDashboardUI -v

# Run specific test method
pytest test_dashboard_ui.py::TestDashboardUI::test_dashboard_page_loads -v
```

## Test Execution Methods

### 1. Basic Execution

```bash
# Run all tests
pytest

# Expected output:
# test_dashboard_ui.py::TestDashboardUI::test_dashboard_page_loads PASSED
# test_dashboard_ui.py::TestDashboardUI::test_today_button_functionality PASSED
# ...
# ===== 50 passed in 123.45s =====
```

### 2. Verbose Execution

```bash
pytest -v

# Shows each test with full path and result
# test_dashboard_ui.py::TestDashboardUI::test_dashboard_page_loads PASSED [  1%]
# test_dashboard_ui.py::TestDashboardUI::test_today_button_functionality PASSED [  2%]
```

### 3. With Stop-on-First-Failure

```bash
pytest -x

# Stops execution on first test failure
```

### 4. With Full Traceback

```bash
pytest -v --tb=long

# Shows complete traceback for failures
```

### 5. With Print Statements

```bash
pytest -s

# Shows print() output from tests
pytest test_dashboard_ui.py -s
```

## Parallel Execution

For faster test runs across multiple cores:

```bash
# Install pytest-xdist if not already installed
pip install pytest-xdist

# Run with 4 workers
pytest -n 4 -v

# Run with 8 workers
pytest -n 8 -v

# Auto-detect number of CPUs
pytest -n auto
```

## Reporting

### HTML Report

```bash
# Install pytest-html
pip install pytest-html

# Generate HTML report
pytest --html=report.html --self-contained-html

# Open report
open report.html  # macOS
start report.html  # Windows
xdg-open report.html  # Linux
```

### Coverage Report

```bash
# Install pytest-cov
pip install pytest-cov

# Generate coverage report
pytest --cov=. --cov-report=html --cov-report=term

# Open coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Test Results Summary

```bash
pytest -v --tb=short 2>&1 | tee test_results.txt
```

## Test Organization by Category

### Dashboard UI Tests
Tests for user interface interactions and page navigation.

```bash
pytest test_dashboard_ui.py -v

# Individual tests:
pytest test_dashboard_ui.py::TestDashboardUI::test_dashboard_page_loads
pytest test_dashboard_ui.py::TestDashboardUI::test_date_picker_navigation
pytest test_dashboard_ui.py::TestDashboardUI::test_ordinal_date_format
```

**Expected**: 13 tests
**Duration**: ~30-40 seconds

### Session Creation Tests
Tests for creating sessions and displaying them on dashboard.

```bash
pytest test_session_creation.py -v

# Individual tests:
pytest test_session_creation.py::TestSessionCreation::test_create_event_and_display
pytest test_session_creation.py::TestSessionCreation::test_mixed_session_types_display
```

**Expected**: 13 tests
**Duration**: ~40-50 seconds

### API Integration Tests
Tests for REST API endpoints and data consistency.

```bash
pytest test_api_integration.py -v

# Individual tests:
pytest test_api_integration.py::TestAPIIntegration::test_api_create_event_success
pytest test_api_integration.py::TestAPIIntegration::test_api_get_sessions_multiple
```

**Expected**: 18 tests
**Duration**: ~20-30 seconds

### Edge Cases Tests
Tests for boundary conditions, special characters, and error scenarios.

```bash
pytest test_edge_cases.py -v

# Individual tests:
pytest test_edge_cases.py::TestEdgeCases::test_very_long_title
pytest test_edge_cases.py::TestEdgeCases::test_unicode_characters_in_title
```

**Expected**: 22 tests
**Duration**: ~50-60 seconds

## Full Test Suite Execution

```bash
# Run all tests with reporting
pytest -v --tb=short --html=report.html --cov=. --cov-report=html

# Expected output:
# test_dashboard_ui.py::... 13 tests PASSED
# test_session_creation.py::... 13 tests PASSED
# test_api_integration.py::... 18 tests PASSED
# test_edge_cases.py::... 22 tests PASSED
# ===== 66 passed in 200-250s =====
```

## Continuous Integration Execution

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r e2e_tests/requirements.txt
          pip install pytest-html pytest-cov
      
      - name: Run E2E tests
        run: |
          cd e2e_tests
          pytest -v --html=report.html --self-contained-html --cov=. --cov-report=html
      
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-test-report
          path: e2e_tests/report.html
      
      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: coverage-report
          path: e2e_tests/htmlcov/
```

## Analyzing Test Results

### Common Test Output Patterns

```
PASSED [100%] - Test passed successfully
FAILED [ 50%] - Test failed
SKIPPED [ 25%] - Test was skipped
ERROR [ 10%] - Error during test execution
```

### Reading Failure Reports

```
FAILED test_dashboard_ui.py::TestDashboardUI::test_today_button_functionality
______________________ test_today_button_functionality ______________________

self = <test_dashboard_ui.TestDashboardUI object at 0x...>

    def test_today_button_functionality(self):
>       assert '10th' in self.page.get_date_header_text()
E       AssertionError: assert '10th' in '15th June 2026'

test_dashboard_ui.py:45: AssertionError
```

**Analysis**:
- Test: `test_today_button_functionality`
- Failure: Expected date '10th' but got '15th'
- Line: 45 in test_dashboard_ui.py
- Likely cause: Date picker not updating properly

### Debugging Failed Tests

```bash
# Run failed test with verbose output
pytest test_dashboard_ui.py::TestDashboardUI::test_today_button_functionality -vv

# Run with print statements
pytest test_dashboard_ui.py::TestDashboardUI::test_today_button_functionality -s

# Run in non-headless mode to observe browser
# Edit conftest.py and comment out:
# options.add_argument('--headless')
pytest test_dashboard_ui.py::TestDashboardUI::test_today_button_functionality
```

## Test Metrics

### Success Metrics

Track these metrics over time:

1. **Pass Rate**: Percentage of tests that pass
   ```
   Pass Rate = (Passed Tests / Total Tests) × 100
   ```

2. **Test Duration**: How long tests take to run
   ```
   Average Duration = Total Time / Number of Tests
   ```

3. **Coverage**: Percentage of code covered by tests
   ```
   Coverage = (Lines Covered / Total Lines) × 100
   ```

### Example Metrics Report

```
Test Results Summary
====================
Total Tests: 66
Passed: 66
Failed: 0
Skipped: 0
Pass Rate: 100%

Execution Time: 215 seconds
Average Test Duration: 3.26 seconds

Coverage Report
===============
statements: 425 covered, 425 total (100%)
branches: 78 covered, 85 total (91.8%)
functions: 52 covered, 52 total (100%)
lines: 420 covered, 420 total (100%)
```

## Troubleshooting Test Failures

### Timeout Errors

```
TimeoutException: Message: chrome not reachable
```

**Solutions**:
1. Increase wait timeout in `conftest.py`
2. Check if Flask server is running
3. Check network connectivity

### Element Not Found Errors

```
NoSuchElementException: Message: no such element
```

**Solutions**:
1. Verify element locators in `page_objects.py`
2. Check if Flask app UI changed
3. Run in non-headless mode to debug

### Connection Refused

```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Solutions**:
1. Start Flask app: `python app.py`
2. Verify `BASE_URL` in `.env`
3. Wait for server to fully start

### Database Lock

```
sqlite3.OperationalError: database is locked
```

**Solutions**:
1. Restart Flask server
2. Delete `instance/calendar.db`
3. Run individual tests instead of full suite

## Performance Optimization

### Run Parallel Tests

```bash
# 4 workers
pytest -n 4 -v

# 8 workers
pytest -n 8 -v

# Auto-detect
pytest -n auto -v
```

### Skip Slow Tests

Add marker to slow tests:
```python
@pytest.mark.slow
def test_many_sessions():
    ...
```

Then run without slow tests:
```bash
pytest -m "not slow"
```

### Headless Mode (Faster)

```python
# In conftest.py
options.add_argument('--headless')
```

## Test Documentation

### Generate Test Report

```bash
# Create detailed test report
pytest -v --tb=short > test_report.txt 2>&1

# View report
cat test_report.txt
```

### Screenshot on Failure

```python
# Add to test fixture
@pytest.fixture
def screenshot_on_failure(driver):
    yield
    # Capture screenshot on failure
    driver.save_screenshot('failure.png')
```

## Best Practices

1. **Run tests before committing**:
   ```bash
   pytest -v
   ```

2. **Check coverage**:
   ```bash
   pytest --cov=. --cov-report=term-missing
   ```

3. **Keep tests isolated**: Each test independent
4. **Clear test names**: Describe what is tested
5. **Meaningful assertions**: Clear failure messages

## Scheduled Test Runs

### Nightly Test Execution

Create a cron job:
```bash
0 2 * * * cd /path/to/e2e_tests && pytest -v --html=report.html
```

### Weekly Regression Testing

```bash
# Run all tests weekly
0 3 * * 0 cd /path/to/e2e_tests && pytest -v --html=weekly_report.html
```

## Related Resources

- [README.md](README.md) - Test documentation
- [setup_guide.md](setup_guide.md) - Setup instructions
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Version**: 1.0
**Last Updated**: June 2026
