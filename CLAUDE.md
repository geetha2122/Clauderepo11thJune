# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Calendar Dashboard** application with a Python Flask backend and JavaScript frontend. It manages events, tasks, and reminders on a calendar with a database backend.

- **Backend**: Flask with SQLAlchemy ORM, SQLite database
- **Frontend**: Vanilla JavaScript with Tailwind CSS (no build step)
- **Database**: SQLite with a `Session` model representing calendar entries (events, tasks, reminders)

## Architecture

### Backend (Python Flask)

The Flask application (`app.py`) provides a REST API:
- **Main Route**: `GET /` returns the dashboard HTML template
- **API Endpoints**:
  - `GET /api/sessions?date=YYYY-MM-DD` - Fetch all sessions for a specific date
  - `POST /api/sessions` - Create a new session (event, task, or reminder)

### Database Model

The `Session` model (`app.py`) represents all calendar entries with:
- `id`: Primary key
- `date`: Date of the session
- `title`: Session title
- `type`: One of `'event'`, `'task'`, or `'reminder'`
- `start_time`, `end_time`: Optional time fields
- `description`: Optional text description

### Frontend

- **Template**: `templates/dashboard.html` - Minimal HTML with Tailwind CDN and date-fns CDN
- **Client Code**: `static/dashboard.js` - Vanilla JavaScript that renders the UI and communicates with the Flask API
- Uses **Tailwind CSS** (via CDN) for styling
- Uses **date-fns** (via CDN) for date utilities
- **IMPORTANT**: See `docs/ui.md` - only use shadcn UI components, no custom components, no custom CSS

## Development Commands

### Backend Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start Flask development server (runs on http://localhost:5000)
python app.py

# The dashboard is accessible at http://localhost:5000/
```

### Testing
```bash
# Run all tests with coverage report
pytest test_app.py --cov=. --cov-report=html

# Run a specific test
pytest test_app.py::CalendarTestCase::test_dashboard_page_loads

# Run tests with verbose output
pytest test_app.py -v
```

## Key Files

- `app.py` - Flask application, database models, and API endpoints
- `test_app.py` - Comprehensive unit tests for the API
- `static/dashboard.js` - Frontend JavaScript implementation
- `templates/dashboard.html` - HTML template
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies (for future React migration)
- `docs/ui.md` - UI component standards and styling rules

## UI/Frontend Standards

As per `docs/ui.md`:
- **Component Library**: Use only shadcn UI components (no custom components)
- **Styling**: Use Tailwind CSS utility classes only (no custom CSS files)
- **Date Formatting**: Use date-fns with ordinal suffixes (e.g., "1st Sept 2026")
- Dependencies: `@shadcn/ui`, `date-fns`, React 18+, Tailwind CSS

## Database

- SQLite database file: `calendar.db` (created in the instance directory)
- Database is initialized automatically when the app runs
- For testing, an in-memory SQLite database is used (see `test_app.py` setup)

## Git Workflow

The repo is initialized with a clean main branch. Recent commits:
- `f81541e` - Add comprehensive unit tests for calendar dashboard API
- `fb5ede1` - Implement calendar dashboard with events, tasks and reminders
- `f6fdb11` - Initial commit

## Common Patterns

### Querying Sessions
```python
# Get sessions for a specific date
date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
sessions = Session.query.filter_by(date=date_obj).all()

# Convert to JSON format
sessions_json = [{
    'id': s.id,
    'title': s.title,
    'type': s.type,
    'start_time': s.start_time.isoformat() if s.start_time else None,
    'end_time': s.end_time.isoformat() if s.end_time else None,
    'description': s.description
} for s in sessions]
```

### API Request Format
POST requests to `/api/sessions` expect JSON:
```json
{
  "date": "2026-06-12",
  "title": "Meeting",
  "type": "event",
  "start_time": "14:30",
  "end_time": "15:30",
  "description": "Team sync"
}
```

## Dependencies

**Python**: Flask 3.0.0, Flask-SQLAlchemy 3.1.1, pytest 7.4.0, pytest-cov 4.1.0
**JavaScript**: React 18.2.0, shadcn/ui, date-fns 3.0.0, Vite 5.0.0 (dev)
