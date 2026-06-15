---
name: Calendar Dashboard Test Structure
description: Pytest fixtures, in-memory DB setup, and test patterns for Flask calendar app
type: reference
---

## Test Organization
- Tests in: `tests/` directory (following Flask conventions)
- File naming: `test_<module>.py` (e.g., `test_api.py`, `test_models.py`)
- Function naming: `test_<behavior>_<expected>()`
- Framework: pytest exclusively

## Fixture Pattern Used
The existing test_app.py uses class-based fixtures with `@pytest.fixture(autouse=True)` and `setup_teardown` pattern:

```python
@pytest.fixture(autouse=True)
def setup_teardown(self):
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()
```

Each test class repeats this fixture. Recommended: extract to conftest.py and use module-level fixtures.

## Database Setup
- In-memory SQLite: `sqlite:///:memory:`
- Automatically created and destroyed for each test
- Flask app context must be active for all database operations

## Test Patterns Established
1. **Dashboard tests**: Use `client.get('/')` and assert status code 200, HTML content type
2. **GET API tests**: Create test data in app context, then fetch via client
3. **POST API tests**: Send JSON, assert 201 status, verify DB persistence
4. **Model tests**: Direct SQLAlchemy operations within app context
5. **Integration tests**: Full request/response cycle mimicking real usage

## Coverage Summary
- 43 passing tests, 2 failing (error handling gaps)
- Covers: CRUD, validation, optional fields, date handling, all session types
- Missing: Better error handling, edge cases with malformed requests
