# End-to-End Testing Suite - Calendar Dashboard

This directory contains comprehensive end-to-end tests for the Calendar Dashboard application using Selenium and Python.

## Project Structure

```
e2e_tests/
├── conftest.py              # Pytest configuration and fixtures
├── page_objects.py          # Page Object Model for dashboard UI
├── test_dashboard_ui.py     # UI interaction tests
├── test_session_creation.py # Session creation and display tests
├── test_api_integration.py  # API endpoint integration tests
├── requirements.txt         # Python dependencies
├── pytest.ini              # Pytest configuration
├── .env                    # Environment variables
└── README.md              # This file
```

## Features

### Test Coverage

1. **Dashboard UI Tests** (`test_dashboard_ui.py`)
   - Dashboard page load verification
   - Date picker functionality
   - Today button functionality
   - Ordinal date format validation (1st, 2nd, 3rd, etc.)
   - Navigation between dates
   - Empty state handling
   - Page layout structure

2. **Session Creation Tests** (`test_session_creation.py`)
   - Create events, tasks, and reminders via API
   - Verify sessions display on the dashboard
   - Session detail verification (title, type, time, description)
   - Multiple sessions on same date
   - Session badge color validation
   - Sessions on different dates
   - Special characters handling
   - Mixed session type display

3. **API Integration Tests** (`test_api_integration.py`)
   - GET /api/sessions endpoint
   - POST /api/sessions endpoint
   - Response format validation
   - Invalid date handling
   - Default date parameter behavior
   - Session type validation (event, task, reminder)
   - Time format consistency
   - Special character handling
   - Multiple requests consistency

### Page Object Model

The `page_objects.py` file implements the Page Object Model pattern:

- `CalendarDashboardPage` class encapsulates all dashboard UI interactions
- Centralized locators for easy maintenance
- Helper methods for common operations
- Wait strategies for element visibility

## Installation

### Prerequisites
- Python 3.8+
- Firefox browser (WebDriver Manager handles the driver)
- Flask app running on http://localhost:5000

### Setup Steps

1. **Install dependencies:**
   ```bash
   cd e2e_tests
   pip install -r requirements.txt
   ```

2. **Configure environment (optional):**
   - Edit `.env` if your Flask app runs on a different URL
   - Default: `BASE_URL=http://localhost:5000`

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest test_dashboard_ui.py
```

### Run Specific Test Class
```bash
pytest test_session_creation.py::TestSessionCreation
```

### Run Specific Test
```bash
pytest test_dashboard_ui.py::TestDashboardUI::test_dashboard_page_loads
```

### Run Tests with Markers
```bash
pytest -m ui          # Run only UI tests
pytest -m api         # Run only API tests
pytest -m smoke       # Run smoke tests
```

### Verbose Output
```bash
pytest -v
```

### With Coverage Report
```bash
pytest --cov=. --cov-report=html
```

### Run Tests in Parallel
```bash
pytest -n 4  # Run with 4 workers
```

### Run Tests in Headless Mode
Edit `conftest.py` and uncomment the headless option in the `driver` fixture:
```python
options.add_argument('--headless')
```

Note: Firefox headless mode uses `--headless` (without value)

## Test Configuration

### conftest.py

Provides pytest fixtures:

- **`flask_app_server`**: Session-scoped fixture that starts/manages Flask app
- **`driver`**: Function-scoped fixture providing Selenium WebDriver
- **`driver_wait`**: WebDriverWait helper for explicit waits
- **`clear_database`**: Auto-clears database before each test

### Environment Variables

Available in `.env`:
- `BASE_URL`: URL of Flask application (default: http://localhost:5000)
- `FLASK_ENV`: Environment for Flask (default: testing)

## Writing New Tests

### Example Test Structure

```python
class TestNewFeature:
    @pytest.fixture(autouse=True)
    def setup(self, driver, flask_app_server):
        self.page = CalendarDashboardPage(driver)
        self.page.navigate_to(flask_app_server)
        self.base_url = flask_app_server

    def test_feature_functionality(self):
        # Arrange
        self.page.set_date('2026-06-15')
        
        # Act
        result = self.page.get_session_count()
        
        # Assert
        assert result == 0
```

### Using Page Objects

```python
# Navigate to dashboard
page.navigate_to('http://localhost:5000')

# Set date
page.set_date('2026-06-20')

# Get session details
sessions = page.get_all_session_details()

# Verify session count
assert page.get_session_count() == 3
```

### Creating Sessions via API

```python
import requests

response = requests.post(
    'http://localhost:5000/api/sessions',
    json={
        'date': '2026-06-20',
        'title': 'Meeting',
        'type': 'event',
        'start_time': '14:00',
        'end_time': '15:00',
        'description': 'Team sync'
    }
)
```

## Browser Automation Details

### WebDriver Configuration

- **Browser**: Mozilla Firefox
- **Wait Timeout**: 10 seconds
- **Window Size**: 1920x1080
- **Implicit Wait**: 10 seconds

### Locator Strategy

Uses a combination of:
- XPath: For complex element selection
- ID: For direct element access
- CSS selectors via Tailwind classes

## Troubleshooting

### "Chrome driver not found" Error
```bash
# WebDriver Manager should handle this, but you can pre-install:
python -m webdriver_manager chrome
```

### "Connection refused" Error
- Ensure Flask app is running on http://localhost:5000
- Or set `BASE_URL` environment variable to correct URL

### Tests Timing Out
- Increase `TIMEOUT` in conftest.py
- Check if elements load slowly in your environment
- Run in non-headless mode to debug

### Database Issues
- `conftest.py` auto-clears database before each test
- Ensure `calendar.db` has proper write permissions

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r e2e_tests/requirements.txt
      - name: Run E2E tests
        run: pytest e2e_tests/ -v
```

## Best Practices

1. **Use Page Objects**: Keep tests clean and maintainable
2. **Isolate Tests**: Each test should be independent
3. **Clear Test Names**: Test names should describe what is being tested
4. **Wait Strategies**: Use explicit waits instead of sleep()
5. **Element Locators**: Keep locators centralized in page objects
6. **Database Cleanup**: Tests auto-clear database via `conftest.py`
7. **Assertions**: Use meaningful assertions with context

## Test Maintenance

### Adding New Locators

Edit `page_objects.py`:
```python
# Add locator
NEW_ELEMENT = (By.ID, 'element-id')

# Add helper method
def interact_with_element(self):
    element = self.driver.find_element(*self.NEW_ELEMENT)
    # Interact with element
```

### Updating Tests After UI Changes

1. Update locators in `page_objects.py`
2. Update helper methods if behavior changed
3. Update assertions if expected output changed

## Dependencies

- **selenium**: WebDriver and browser automation
- **pytest**: Test framework
- **pytest-xdist**: Parallel test execution
- **webdriver-manager**: Automatic WebDriver management
- **python-dotenv**: Environment variable management
- **requests**: HTTP requests (API testing)

## Related Documentation

- [Calendar Dashboard CLAUDE.md](../CLAUDE.md)
- [API Documentation](../TESTING_GUIDE.md)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Pytest Documentation](https://docs.pytest.org/)

## Contributing

When adding new tests:
1. Follow the existing test structure
2. Add appropriate markers (@pytest.mark)
3. Update documentation with new test scenarios
4. Ensure tests are isolated and don't depend on execution order
5. Test with multiple browsers/resolutions if applicable

## Support

For issues or questions:
1. Check test output and logs
2. Run in non-headless mode to see browser automation
3. Verify Flask app is running correctly
4. Check browser console for JavaScript errors
5. Review Selenium WebDriver logs

---

**Last Updated**: June 2026
