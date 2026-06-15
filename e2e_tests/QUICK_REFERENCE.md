# E2E Testing Suite - Quick Reference Card

## Installation

```bash
cd e2e_tests
pip install -r requirements.txt
```

## Start Flask App

```bash
# In separate terminal from project root
python app.py
```

## Running Tests

### All Tests
```bash
pytest
pytest -v                    # With details
pytest -v --tb=short        # With error details
```

### Specific Tests
```bash
pytest test_dashboard_ui.py
pytest test_session_creation.py
pytest test_api_integration.py
pytest test_edge_cases.py

# Single test class
pytest test_dashboard_ui.py::TestDashboardUI

# Single test
pytest test_dashboard_ui.py::TestDashboardUI::test_dashboard_page_loads
```

### Advanced
```bash
pytest -n 4 -v              # Parallel (4 workers)
pytest -x -v                # Stop on first failure
pytest -s -v                # Show print statements
pytest --lf                 # Run last failed tests
```

## Reporting

```bash
# HTML Report
pytest --html=report.html --self-contained-html
open report.html

# Coverage Report
pytest --cov=. --cov-report=html --cov-report=term
open htmlcov/index.html
```

## Markers

```bash
pytest -m ui                # UI tests only
pytest -m api               # API tests only
pytest -m smoke             # Smoke tests
pytest -m regression        # Regression tests
```

## Debugging

```bash
# Verbose output
pytest -vv

# Show print statements
pytest -s

# Full traceback
pytest --tb=long

# Non-headless (edit conftest.py first)
# Remove or comment out: options.add_argument('--headless')
pytest test_dashboard_ui.py
```

## Directory Structure

```
e2e_tests/
├── conftest.py                  # Test configuration & fixtures
├── page_objects.py              # Page Object Model
├── test_dashboard_ui.py         # 13 UI tests
├── test_session_creation.py     # 13 session tests
├── test_api_integration.py      # 18 API tests
├── test_edge_cases.py           # 22 edge case tests
├── requirements.txt             # Dependencies
├── pytest.ini                   # Pytest config
├── .env                         # Environment variables
├── README.md                    # Full documentation
├── OVERVIEW.md                  # Project overview
├── setup_guide.md               # Setup instructions
├── TEST_EXECUTION.md            # Execution guide
└── QUICK_REFERENCE.md           # This file
```

## Test Counts & Duration

| File | Tests | Markers | Duration |
|------|-------|---------|----------|
| test_dashboard_ui.py | 13 | ui, smoke | 30-40s |
| test_session_creation.py | 13 | - | 40-50s |
| test_api_integration.py | 18 | api, smoke | 20-30s |
| test_edge_cases.py | 22 | regression | 50-60s |
| **TOTAL** | **66** | - | **140-180s** |

## Key Concepts

### Page Object Model
```python
page = CalendarDashboardPage(driver)
page.navigate_to(base_url)
page.set_date('2026-06-20')
count = page.get_session_count()
details = page.get_session_details(0)
```

### Creating Sessions
```python
import requests
response = requests.post(
    f'{base_url}/api/sessions',
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

### Test Structure
```python
class TestFeature:
    @pytest.fixture(autouse=True)
    def setup(self, driver, flask_app_server):
        self.page = CalendarDashboardPage(driver)
        self.page.navigate_to(flask_app_server)

    def test_something(self):
        # Arrange, Act, Assert
        pass
```

## Fixtures (in conftest.py)

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `flask_app_server` | session | Manage Flask app lifecycle |
| `driver` | function | Selenium WebDriver |
| `driver_wait` | function | WebDriverWait helper |
| `clear_database` | function | Auto-clear database |

## Page Object Methods

```python
page.navigate_to(url)           # Go to dashboard
page.is_page_loaded()           # Check if loaded
page.get_date_header_text()     # Get displayed date
page.set_date(date_str)         # Change date
page.click_today_button()       # Click Today button
page.get_session_count()        # Count sessions
page.has_no_events_message()    # Check empty state
page.get_session_titles()       # Get all titles
page.get_session_types()        # Get all type badges
page.get_session_details(i)     # Get details of session i
page.get_all_session_details()  # Get all sessions
```

## Test Categories

### Dashboard UI (13 tests)
- Page load, date picker, Today button
- Ordinal formatting (1st, 2nd, 3rd)
- Navigation, empty state, layout

### Session Creation (13 tests)
- Create events, tasks, reminders
- Display verification, details, colors
- Multiple dates, special characters

### API Integration (18 tests)
- GET/POST endpoints, responses
- Validation, consistency, headers
- Date formats, session types

### Edge Cases (22 tests)
- Long strings, Unicode, special chars
- Boundary times, leap years
- HTML/SQL injection, large data

## Troubleshooting

### Tests Won't Start
```bash
# Check Flask is running
curl http://localhost:5000

# Check .env file
cat .env

# Verify dependencies
pip install -r requirements.txt
```

### Timeout Errors
- Increase wait time in `conftest.py`
- Ensure Flask app is fully started
- Run without headless mode to debug

### Connection Refused
- Start Flask: `python app.py`
- Check `BASE_URL` in `.env`
- Wait 5 seconds after starting Flask

### Element Not Found
- Run in non-headless mode
- Check page locators in `page_objects.py`
- Verify Flask UI structure

## Common Commands Chain

```bash
# Full test cycle
cd e2e_tests && \
pip install -r requirements.txt && \
pytest -v --tb=short --html=report.html && \
open report.html

# Quick smoke test
pytest test_dashboard_ui.py::TestDashboardUI::test_dashboard_page_loads -v

# Run with coverage
pytest --cov=. --cov-report=term --cov-report=html
```

## Configuration Files

### .env
```env
BASE_URL=http://localhost:5000
FLASK_ENV=testing
```

### pytest.ini
```ini
[pytest]
testpaths = .
addopts = -v --strict-markers --tb=short
markers = ui, api, smoke, regression
```

### requirements.txt
```
selenium==4.15.2
pytest==7.4.0
pytest-xdist==3.5.0
webdriver-manager==4.0.1
python-dotenv==1.0.0
requests==2.31.0
```

## Performance Tips

1. **Run in headless mode** (default): Faster browser
2. **Use parallel execution**: `pytest -n 4`
3. **Skip slow tests**: Add `@pytest.mark.slow`, then `pytest -m "not slow"`
4. **Run specific tests**: Focus on relevant tests only

## Output Examples

### Successful Run
```
test_dashboard_ui.py::TestDashboardUI::test_dashboard_page_loads PASSED [ 1%]
...
===== 66 passed in 3m 45s =====
```

### Failed Test
```
FAILED test_dashboard_ui.py::TestDashboardUI::test_today_button_functionality
AssertionError: assert '10th' in '15th June 2026'
```

### Parallel Run
```
pytest -n 4 -v
[gw0] [test_dashboard_ui.py::TestDashboardUI::test_dashboard_page_loads] PASSED
[gw1] [test_session_creation.py::TestSessionCreation::test_create_event_and_display] PASSED
```

## Links

- **Full Docs**: [README.md](README.md)
- **Setup Guide**: [setup_guide.md](setup_guide.md)
- **Execution Guide**: [TEST_EXECUTION.md](TEST_EXECUTION.md)
- **Project Overview**: [OVERVIEW.md](OVERVIEW.md)

---

**Version**: 1.0 | **Last Updated**: June 2026
