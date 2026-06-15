# E2E Testing Setup Guide

Complete step-by-step guide to set up and run the Selenium end-to-end tests.

## Quick Start

```bash
# 1. Navigate to e2e_tests directory
cd e2e_tests

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run tests
pytest
```

## Detailed Setup

### Step 1: Install Python Dependencies

```bash
cd e2e_tests
pip install -r requirements.txt
```

This installs:
- `selenium`: Browser automation
- `pytest`: Test framework
- `pytest-xdist`: Parallel execution
- `webdriver-manager`: Automatic WebDriver handling
- `python-dotenv`: Environment configuration
- `requests`: HTTP client for API testing

### Step 2: Verify Firefox Installation

Selenium tests require Mozilla Firefox. WebDriver Manager handles the driver automatically.

```bash
# Check Firefox is installed
firefox --version  # Linux
# or
/Applications/Firefox.app/Contents/MacOS/firefox --version  # macOS
# or
"C:\Program Files\Mozilla Firefox\firefox.exe" --version  # Windows
```

### Step 3: Prepare Flask Application

Ensure the Flask app is properly configured:

```bash
# From project root
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Step 4: Configure Environment

The `.env` file contains test configuration:

```env
BASE_URL=http://localhost:5000
FLASK_ENV=testing
```

Modify if your Flask app runs on a different URL/port.

### Step 5: Start Flask Application

In a separate terminal:

```bash
# From project root
source venv/bin/activate
python app.py
```

The Flask server should start on http://localhost:5000

### Step 6: Run Tests

In another terminal, navigate to e2e_tests and run tests:

```bash
cd e2e_tests
pytest
```

## Running Different Test Scenarios

### 1. Run All Tests

```bash
pytest
```

### 2. Run Specific Test File

```bash
# Dashboard UI tests
pytest test_dashboard_ui.py

# Session creation tests
pytest test_session_creation.py

# API integration tests
pytest test_api_integration.py
```

### 3. Run Specific Test Class

```bash
pytest test_dashboard_ui.py::TestDashboardUI
pytest test_session_creation.py::TestSessionCreation
pytest test_api_integration.py::TestAPIIntegration
```

### 4. Run Specific Test

```bash
pytest test_dashboard_ui.py::TestDashboardUI::test_dashboard_page_loads
```

### 5. Run with Verbose Output

```bash
pytest -v
```

### 6. Run with Coverage

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

Coverage reports will be generated in `htmlcov/` directory.

### 7. Run in Parallel

```bash
# Install pytest-xdist if not already installed
pip install pytest-xdist

# Run with 4 workers
pytest -n 4
```

### 8. Run in Headless Mode

Edit `conftest.py` and uncomment:

```python
# In driver fixture
options.add_argument('--headless')
```

Then run:

```bash
pytest
```

### 9. Run with Custom Markers

```bash
# Only UI tests
pytest -m ui

# Only API tests
pytest -m api

# Smoke tests
pytest -m smoke
```

## Test Structure

### conftest.py

Provides reusable fixtures:

- **`flask_app_server`**: Manages Flask application lifecycle
- **`driver`**: Selenium WebDriver instance
- **`driver_wait`**: WebDriverWait for explicit waits
- **`clear_database`**: Auto-clears database before/after tests

### page_objects.py

Implements Page Object Model:

```python
page = CalendarDashboardPage(driver)
page.navigate_to(base_url)
page.set_date('2026-06-20')
count = page.get_session_count()
details = page.get_session_details(0)
```

### Test Files

1. **test_dashboard_ui.py**: UI interactions and display
2. **test_session_creation.py**: Creating and viewing sessions
3. **test_api_integration.py**: API endpoint validation

## Common Issues and Solutions

### Issue: Chrome Driver Not Found

**Solution**: WebDriver Manager should handle this automatically. If not:

```bash
python -m webdriver_manager chrome
```

### Issue: Connection Refused

**Error**: `ConnectionRefusedError` when connecting to Flask app

**Solution**:
1. Ensure Flask app is running on correct port
2. Check `BASE_URL` in `.env` matches Flask URL
3. Wait a few seconds before running tests

```bash
# Start Flask
python app.py &
sleep 5

# Then run tests
pytest
```

### Issue: Database Lock

**Error**: `database is locked`

**Solution**: The fixture `clear_database` handles this. If you still get this error:

```bash
# Remove the database and let it recreate
rm instance/calendar.db
pytest
```

### Issue: Element Not Found

**Solution**: 
1. Verify Flask app is running
2. Check if element locators changed in dashboard.html
3. Update locators in `page_objects.py`
4. Run in non-headless mode to debug:

```python
# In conftest.py, comment out or remove:
# options.add_argument('--headless')
```

### Issue: Timeout Errors

**Solution**: Increase wait timeout in `conftest.py`:

```python
self.wait = WebDriverWait(driver, 15)  # Increased from 10
```

## Debugging Tests

### Run in Non-Headless Mode

```python
# In conftest.py driver fixture, remove or comment out:
# options.add_argument('--headless')
```

This allows you to see the browser during test execution.

### Add Debug Output

```python
def test_example(self):
    print(f"Current URL: {self.driver.current_url}")
    print(f"Page title: {self.driver.title}")
    sessions = self.page.get_all_session_details()
    print(f"Sessions: {sessions}")
```

Run with:

```bash
pytest -s  # -s shows print statements
```

### Capture Screenshots

```python
def test_example(self):
    self.driver.save_screenshot('debug_screenshot.png')
```

### Check Browser Console

In non-headless mode, open Chrome DevTools (F12) to see console errors.

## Advanced Configuration

### Custom Timeouts

Edit `conftest.py`:

```python
@pytest.fixture(scope='function')
def driver(flask_app_server):
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(15)  # Increase implicit wait
    yield driver
    driver.quit()
```

### Multiple Browsers

```python
# Install additional drivers
pip install webdriver-manager

# Use Edge
from webdriver_manager.microsoft import EdgeChromiumDriverManager
driver = webdriver.Edge(EdgeChromiumDriverManager().install())
```

### Proxy Configuration

```python
options.add_argument('--proxy-server=http://proxy.example.com:8080')
```

## Integration with CI/CD

### GitHub Actions

Create `.github/workflows/e2e-tests.yml`:

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r e2e_tests/requirements.txt
      - name: Run E2E tests
        run: |
          cd e2e_tests
          pytest -v --tb=short
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
e2e_tests:
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - pip install -r e2e_tests/requirements.txt
    - cd e2e_tests
    - pytest -v
```

## Performance Testing Tips

1. **Run in Parallel**:
   ```bash
   pytest -n 4
   ```

2. **Use Markers for Quick Smoke Tests**:
   ```bash
   pytest -m smoke
   ```

3. **Skip Slow Tests**:
   ```bash
   pytest -m "not slow"
   ```

## Best Practices

1. **Keep Tests Independent**: Each test should work standalone
2. **Use Page Objects**: Centralize UI interactions
3. **Clear Test Data**: Database is auto-cleared per test
4. **Meaningful Assertions**: Clear failure messages
5. **Explicit Waits**: Avoid `sleep()`, use WebDriverWait
6. **Test Organization**: Group related tests in classes

## Next Steps

1. Review [README.md](README.md) for detailed test documentation
2. Examine test files to understand test structure
3. Modify `page_objects.py` for new UI elements
4. Add new test cases as features are developed

## Support and Troubleshooting

For help:
1. Run with `-v` for verbose output
2. Use `-s` to see print statements
3. Check `conftest.py` for fixture issues
4. Review Selenium documentation: https://www.selenium.dev/documentation/
5. Check Pytest documentation: https://docs.pytest.org/

---

**Version**: 1.0
**Last Updated**: June 2026
