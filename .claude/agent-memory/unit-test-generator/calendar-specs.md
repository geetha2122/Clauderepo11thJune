---
name: Session Model & API Specs
description: Calendar dashboard Session model fields, validation rules, and API endpoint specifications
type: reference
---

## Session Model Fields
- `id`: Integer, primary key, auto-incremented
- `date`: Date (required), ISO format YYYY-MM-DD
- `title`: String(255), required
- `type`: String(50), required, must be one of: 'event', 'task', 'reminder'
- `start_time`: Time, optional, ISO format HH:MM
- `end_time`: Time, optional, ISO format HH:MM
- `description`: Text, optional

## API Endpoints

### GET /api/sessions?date=YYYY-MM-DD
- Returns: JSON array of sessions for the specified date
- Query params: `date` (optional, defaults to today)
- Status: 200 on success
- Response: `[{id, title, type, start_time, end_time, description}, ...]`
- Times serialized to ISO8601 (HH:MM:SS format)

### POST /api/sessions
- Request body: JSON with date, title, type, and optional start_time, end_time, description
- Required: date (YYYY-MM-DD), title, type
- Optional: start_time (HH:MM), end_time (HH:MM), description
- Status: 201 Created on success
- Response: `{id: <integer>}`

### GET /
- Returns: HTML dashboard template
- Status: 200

## Validation Rules
- Date format: YYYY-MM-DD (strptime '%Y-%m-%d')
- Time format: HH:MM (strptime '%H:%M')
- Type must be one of: 'event', 'task', 'reminder'
- Title cannot be empty (required)
- Currently NO error handling for:
  - Invalid date formats → causes 500 ValueError
  - Invalid time formats → causes 500 ValueError
  - Invalid session types → accepted but should validate

## Known Issues
- Missing error handling for malformed date/time inputs (returns 500 instead of 400)
- No validation of session type enum values
- No validation that end_time > start_time
- No truncation of overly long titles (max 255 allowed)
