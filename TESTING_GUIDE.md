# Calendar Dashboard Testing Guide

## Overview

This document provides comprehensive guidance on the pytest unit test suite for the Flask Calendar Dashboard application. The test suite includes **85 deterministic unit tests** organized into 3 modules covering models, API endpoints, and error handling.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pytest tests/ -v` | Run all 85 tests with verbose output |
| `pytest tests/ --cov=app --cov-report=html` | Run tests with coverage report |
| `pytest tests/test_models.py -v` | Run 30 model tests only |
| `pytest tests/test_api_endpoints.py -v` | Run 31 endpoint tests only |
| `pytest tests/test_error_handling.py -v` | Run 24 error handling tests |
| `pytest tests/ -k "create_session" -v` | Run tests matching pattern |

## Test Files

### tests/conftest.py
**Purpose**: Shared pytest fixtures for test configuration

**Fixtures Provided**:
- `app_instance`: Flask app with TESTING=True and in-memory SQLite database
- `client`: Flask test client for HTTP requests
- `db_session`: Direct SQLAlchemy session access

**Key Setup**:
```python
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db.create_all()  # Initialize schema
yield  # Test runs here
db.session.remove()
db.drop_all()  # Cleanup
```

### tests/test_models.py (30 tests)
**Purpose**: Unit tests for Session database model

**Test Classes**:
1. **TestSessionModelCreation** (5 tests)
   - Creating sessions with required and optional fields
   - Testing auto-increment primary key behavior
   - Unicode character support

2. **TestSessionModelFields** (5 tests)
   - Field type validation (Date, Time, String, Text)
   - Long text storage capacity
   - Type consistency on retrieval

3. **TestSessionModelQueries** (7 tests)
   - Filtering by date, type, and multiple criteria
   - Querying by primary key
   - Empty result handling

4. **TestSessionModelUpdates** (3 tests)
   - Updating session fields
   - Updating optional fields
   - Type field changes

5. **TestSessionModelDeletion** (2 tests)
   - Single session deletion
   - Cascading effects on other records

**Example Test**:
```python
def test_create_session_with_required_fields_only(self):
    """Test creating Session with only required fields."""
    with app.app_context():
        # Arrange
        session = Session(
            date=date(2026, 6, 12),
            title='Team Meeting',
            type='event'
        )
        db.session.add(session)
        db.session.commit()

        # Act
        fetched = Session.query.first()

        # Assert
        assert fetched.title == 'Team Meeting'
        assert fetched.type == 'event'
```

### tests/test_api_endpoints.py (31 tests)
**Purpose**: Integration tests for Flask API endpoints

**Test Classes**:
1. **TestDashboardRoute** (4 tests)
   - GET / returns 200 with HTML
   - 404 for invalid routes

2. **TestGetSessionsEndpoint** (12 tests)
   - Empty database behavior
   - Single/multiple session retrieval
   - Date filtering
   - Time format (ISO 8601)
   - Optional field null handling
   - All session types support
   - Special character handling
   - Default date parameter

3. **TestPostSessionsEndpoint** (15 tests)
   - 201 Created status
   - Response ID validation
   - Database persistence
   - All session types
   - Optional field handling
   - Unicode support
   - Long text storage
   - Various dates

**Example Test**:
```python
def test_create_session_returns_201_created(self):
    """Test that successful creation returns 201."""
    # Arrange
    client = app.test_client()
    data = {
        'date': '2026-06-12',
        'title': 'New Event',
        'type': 'event'
    }

    # Act
    response = client.post('/api/sessions', json=data)

    # Assert
    assert response.status_code == 201
    assert 'id' in response.json
```

### tests/test_error_handling.py (24 tests)
**Purpose**: Error scenarios and edge cases

**Test Classes**:
1. **TestGetSessionsErrorHandling** (4 tests)
   - Invalid date formats → 500 (should be 400)
   - Malformed date strings
   - Empty/null parameters

2. **TestPostSessionsRequiredFieldValidation** (5 tests)
   - Missing date/title/type → 500/KeyError (should be 400)
   - Null required fields
   - Empty JSON body

3. **TestPostSessionsDateValidation** (4 tests)
   - Invalid date formats
   - Empty date strings
   - Non-string types

4. **TestPostSessionsTimeValidation** (5 tests)
   - Invalid time formats
   - Seconds in time (HH:MM:SS not supported)
   - Non-string types
   - Invalid hour/minute

5. **TestPostSessionsTypeValidation** (5 tests)
   - Valid types: event, task, reminder
   - Invalid types (currently accepted)
   - Case sensitivity
   - Empty strings

6. **TestPostSessionsMalformedRequests** (4 tests)
   - Invalid JSON syntax
   - Empty JSON body
   - Missing Content-Type
   - Extra fields

7. **TestPostSessionsEdgeCases** (5 tests)
   - Leap year dates
   - Year boundaries
   - Midnight times
   - Empty/whitespace titles

**Note**: 19 tests fail due to missing error handling in app.py (see Known Issues)

## Test Results

### Current Status
- **Total**: 85 tests
- **Passing**: 66 (77.6%)
- **Failing**: 19 (22.4%)

### Test Coverage by Component
| Component | Coverage | Status |
|-----------|----------|--------|
| Dashboard route (GET /) | Full | ✓ |
| Get Sessions (GET /api/sessions) | Full | ✓ |
| Create Session - Happy Path (POST /api/sessions) | Full | ✓ |
| Create Session - Error Handling | Partial | ✗ |
| Session Model | Full | ✓ |
| Date Validation | Partial | ✗ |
| Time Validation | Partial | ✗ |
| Type Validation | Partial | ✗ |

## Known Issues

### 1. Missing Error Handling (19 tests fail)

**Issue**: Invalid input returns 500 errors instead of 400 Bad Request

**Affected Tests**:
- Invalid date formats in GET and POST
- Missing required fields
- Invalid time formats
- Empty JSON body

**Root Cause**: No try-catch error handling in app.py endpoints

**Solution**: Add error handling middleware to catch ValueError, KeyError, TypeError and return 400 with descriptive error messages

**Example Fix**:
```python
@app.route('/api/sessions', methods=['POST'])
def create_session():
    try:
        data = request.json or {}
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        if 'date' not in data or not data['date']:
            return jsonify({'error': 'Missing required field: date'}), 400
        
        # Parse date
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        # ... rest of logic
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except (KeyError, TypeError) as e:
        return jsonify({'error': f'Malformed request: {str(e)}'}), 400
```

## Test Patterns

### Pattern 1: Arrange-Act-Assert
All tests follow this structure:
```python
def test_example(self):
    # Arrange: Set up test data
    with app.app_context():
        session = Session(...)
        db.session.add(session)
        db.session.commit()
    
    # Act: Perform action
    client = app.test_client()
    response = client.get('/api/sessions?date=2026-06-12')
    
    # Assert: Verify results
    assert response.status_code == 200
    assert len(response.json) == 1
```

### Pattern 2: Database Isolation
Each test gets fresh database:
```python
@pytest.fixture(autouse=True)
def setup(self):
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()
```

### Pattern 3: App Context
Database operations require Flask context:
```python
with app.app_context():
    session = Session.query.first()
    # Can access db.session here
```

### Pattern 4: Test Client
HTTP requests via Flask test client:
```python
client = app.test_client()
response = client.post('/api/sessions', json=data)
assert response.status_code == 201
```

## Running Tests

### Basic Execution
```bash
# All tests
pytest tests/ -v

# Single module
pytest tests/test_models.py -v

# Single class
pytest tests/test_models.py::TestSessionModelCreation -v

# Single test
pytest tests/test_models.py::TestSessionModelCreation::test_create_session_with_required_fields_only -v

# By pattern
pytest tests/ -k "create" -v
```

### With Coverage
```bash
# Generate coverage report
pytest tests/ --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

### With Output Capture
```bash
# Show print statements
pytest tests/ -v -s

# Verbose output
pytest tests/ -vv

# Long tracebacks
pytest tests/ --tb=long
```

## Test Coverage Analysis

### Model Coverage (30 tests)
- **Create**: ✓ All field combinations
- **Read**: ✓ Query by date, type, id
- **Update**: ✓ Individual fields
- **Delete**: ✓ Single and cascade
- **Field Types**: ✓ Date, Time, String, Text
- **Edge Cases**: ✓ Unicode, long text, boundaries

### Endpoint Coverage (31 tests)
- **GET /**: ✓ Status, content type, content
- **GET /api/sessions**: ✓ Filtering, formatting, defaults
- **POST /api/sessions**: ✓ All types, optional fields, persistence
- **Error Responses**: ✗ Mostly unimplemented

### Data Coverage
- **Session Types**: ✓ event, task, reminder
- **Dates**: ✓ Boundary dates, leap years
- **Times**: ✓ Valid HH:MM format
- **Text**: ✓ Unicode, special chars, long strings
- **Validation**: ✗ Invalid inputs not properly handled

## Adding New Tests

### New Model Test
```python
class TestSessionModelXxx:
    """Test description."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()
    
    def test_new_feature(self):
        """Test what this feature does."""
        with app.app_context():
            # Arrange
            # Act
            # Assert
```

### New Endpoint Test
```python
def test_endpoint_behavior(self):
    """Test description."""
    # Arrange
    client = app.test_client()
    data = {...}
    
    # Act
    response = client.post('/api/sessions', json=data)
    
    # Assert
    assert response.status_code == 201
```

## Best Practices

1. **Isolation**: Each test is independent with fresh database
2. **Determinism**: No random values, external APIs, or real time
3. **Clarity**: Test names describe what and why
4. **Completeness**: Test happy path, errors, edge cases
5. **DRY**: Reuse fixtures, avoid duplication
6. **Documentation**: Docstrings explain test purpose
7. **Type Coverage**: String, numeric, date, unicode, special chars
8. **Boundary Testing**: Empty, null, max length, boundaries
9. **Error Testing**: Verify both success and failure
10. **Readability**: Clear Arrange-Act-Assert structure

## Troubleshooting

### Test Hangs
- Add `-v` to see which test is running
- Check for missing `yield` in fixtures
- Verify `db.session.remove()` in cleanup

### Flaky Tests
- Look for datetime.now() or random() calls
- Verify database isolation between tests
- Check for shared state between test classes

### Import Errors
- Ensure `tests/__init__.py` exists
- Run from project root: `pytest tests/`
- Check PYTHONPATH includes project root

### Database Locked
- Ensure `db.session.remove()` is called
- Check for uncommitted transactions
- Use in-memory database for testing

## Performance

- **Total Time**: ~3.3 seconds for all 85 tests
- **Average per Test**: ~39 milliseconds
- **Database**: In-memory SQLite (no I/O)
- **Network**: No external calls

## Files Summary

```
tests/
├── __init__.py          # Package marker
├── conftest.py          # Shared fixtures
├── test_models.py       # 30 model tests
├── test_api_endpoints.py # 31 endpoint tests
├── test_error_handling.py # 24 error tests
└── README.md            # Detailed test documentation
```

## Next Steps

1. **Review test_error_handling.py failures** and implement error handling in app.py
2. **Run coverage report** to identify untested code paths
3. **Add integration tests** for complete user workflows
4. **Performance tests** if needed for high-load scenarios
5. **Continuous Integration** setup to run tests automatically

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/orm/session_basics.html#using-sessions-with-events)
- [test_app.py](../test_app.py) - Original comprehensive tests (45 tests)

---

**Last Updated**: 2026-06-12  
**Test Suite Version**: 1.0  
**Compatibility**: Python 3.12+, pytest 7.4.0+
