---
name: Error Handling Coverage Gaps
description: Missing error handling for invalid date/time formats causes 500 errors instead of 400
type: feedback
---

## Failing Tests Identified
1. **test_get_sessions_handles_invalid_date_format**: Invalid date in query param causes unhandled ValueError (expects 400 or 500, gets 500 with traceback)
2. **test_create_session_time_with_seconds**: Seconds in time field cause unhandled ValueError

## Root Causes
Both failures stem from missing try/catch around datetime parsing in app.py:
- Line 26: `datetime.strptime(date_str, '%Y-%m-%d')` – no error handling
- Line 43: `datetime.strptime(data.get('start_time'), '%H:%M')` – no error handling

## Missing Validation Handlers
The API should return 400 Bad Request for:
- Invalid date format in GET query params
- Invalid time format in POST request fields
- Invalid/unsupported session type values
- Missing required fields (date, title, type)
- Malformed JSON in POST request body

## Recommendations for Enhanced Tests
1. Add error handling tests expecting 400 status
2. Mock datetime.strptime to simulate ValueError scenarios
3. Add JSONDecodeError tests for malformed request bodies
4. Test all required field validation
5. Validate that error responses include meaningful error messages
