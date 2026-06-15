import pytest
import requests
import json
from datetime import datetime, timedelta


class TestAPIIntegration:
    """Test suite for API endpoints integration with UI."""

    @pytest.fixture(autouse=True)
    def setup(self, flask_app_server):
        """Setup before each test."""
        self.base_url = flask_app_server
        self.api_url = f'{flask_app_server}/api/sessions'

    def test_api_get_sessions_empty(self):
        """Test GET /api/sessions returns empty list for date with no sessions."""
        response = requests.get(f'{self.api_url}?date=2026-06-01')
        assert response.status_code == 200
        assert response.json() == []

    def test_api_create_event_success(self):
        """Test POST /api/sessions creates event successfully."""
        payload = {
            'date': '2026-06-15',
            'title': 'Team Standup',
            'type': 'event',
            'start_time': '09:00',
            'end_time': '09:30',
            'description': 'Daily team sync'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201
        data = response.json()
        assert 'id' in data

    def test_api_create_task_success(self):
        """Test POST /api/sessions creates task successfully."""
        payload = {
            'date': '2026-06-16',
            'title': 'Code review',
            'type': 'task',
            'description': 'Review PR #123'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201
        data = response.json()
        assert 'id' in data

    def test_api_create_reminder_success(self):
        """Test POST /api/sessions creates reminder successfully."""
        payload = {
            'date': '2026-06-17',
            'title': 'Client call',
            'type': 'reminder',
            'start_time': '15:00'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201
        data = response.json()
        assert 'id' in data

    def test_api_create_without_optional_fields(self):
        """Test creating session with only required fields."""
        payload = {
            'date': '2026-06-18',
            'title': 'Minimal Event',
            'type': 'task'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

    def test_api_get_sessions_single(self):
        """Test GET returns the created session."""
        # Create a session
        payload = {
            'date': '2026-06-19',
            'title': 'Test Event',
            'type': 'event',
            'start_time': '10:00',
            'end_time': '11:00'
        }
        create_response = requests.post(self.api_url, json=payload)
        assert create_response.status_code == 201

        # Get sessions for that date
        get_response = requests.get(f'{self.api_url}?date=2026-06-19')
        assert get_response.status_code == 200
        sessions = get_response.json()
        assert len(sessions) == 1
        assert sessions[0]['title'] == 'Test Event'

    def test_api_get_sessions_multiple(self):
        """Test GET returns multiple sessions."""
        test_date = '2026-06-20'

        # Create multiple sessions
        for i in range(3):
            payload = {
                'date': test_date,
                'title': f'Event {i+1}',
                'type': 'event'
            }
            requests.post(self.api_url, json=payload)

        # Get sessions
        response = requests.get(f'{self.api_url}?date={test_date}')
        sessions = response.json()
        assert len(sessions) == 3

    def test_api_session_response_format(self):
        """Test that session response has correct format."""
        payload = {
            'date': '2026-06-21',
            'title': 'Format Test',
            'type': 'event',
            'start_time': '13:00',
            'end_time': '14:00',
            'description': 'Test description'
        }
        requests.post(self.api_url, json=payload)

        response = requests.get(f'{self.api_url}?date=2026-06-21')
        session = response.json()[0]

        assert 'id' in session
        assert session['title'] == 'Format Test'
        assert session['type'] == 'event'
        assert session['start_time'] == '13:00:00'
        assert session['end_time'] == '14:00:00'
        assert session['description'] == 'Test description'

    def test_api_invalid_date_format(self):
        """Test API with invalid date format."""
        response = requests.get(f'{self.api_url}?date=invalid-date')
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data

    def test_api_default_date_parameter(self):
        """Test GET uses today's date when date parameter not provided."""
        # Create session for today
        today = datetime.now().strftime('%Y-%m-%d')
        payload = {
            'date': today,
            'title': 'Today Event',
            'type': 'event'
        }
        requests.post(self.api_url, json=payload)

        # Get without date parameter
        response = requests.get(self.api_url)
        assert response.status_code == 200
        sessions = response.json()
        assert len(sessions) >= 1

    def test_api_date_format_consistency(self):
        """Test that dates in responses are in consistent format."""
        payload = {
            'date': '2026-06-22',
            'title': 'Consistency Test',
            'type': 'event',
            'start_time': '09:30',
            'end_time': '10:30'
        }
        requests.post(self.api_url, json=payload)

        response = requests.get(f'{self.api_url}?date=2026-06-22')
        session = response.json()[0]

        # Verify ISO format for times
        assert ':' in session['start_time']
        assert ':' in session['end_time']

    def test_api_special_characters_in_title(self):
        """Test handling special characters in title and description."""
        payload = {
            'date': '2026-06-23',
            'title': 'Meeting: Q3 Review & Planning (40%)',
            'type': 'event',
            'description': 'Topics: Goals, timelines, <issues>'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        # Verify retrieval
        get_response = requests.get(f'{self.api_url}?date=2026-06-23')
        session = get_response.json()[0]
        assert session['title'] == 'Meeting: Q3 Review & Planning (40%)'

    def test_api_empty_description_optional(self):
        """Test that description is optional and can be empty."""
        payload = {
            'date': '2026-06-24',
            'title': 'No Description',
            'type': 'task',
            'description': None
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        # Verify
        get_response = requests.get(f'{self.api_url}?date=2026-06-24')
        session = get_response.json()[0]
        assert session['description'] is None

    def test_api_time_format_handling(self):
        """Test proper handling of different time formats."""
        payload = {
            'date': '2026-06-25',
            'title': 'Time Format Test',
            'type': 'event',
            'start_time': '08:00',
            'end_time': '17:30'
        }
        requests.post(self.api_url, json=payload)

        response = requests.get(f'{self.api_url}?date=2026-06-25')
        session = response.json()[0]
        assert '08:00' in session['start_time']
        assert '17:30' in session['end_time']

    def test_api_session_types_validation(self):
        """Test that all session types are accepted."""
        test_date = '2026-06-26'
        types = ['event', 'task', 'reminder']

        for session_type in types:
            payload = {
                'date': test_date,
                'title': f'{session_type.capitalize()} Type',
                'type': session_type
            }
            response = requests.post(self.api_url, json=payload)
            assert response.status_code == 201

        # Verify all were created
        response = requests.get(f'{self.api_url}?date={test_date}')
        sessions = response.json()
        assert len(sessions) == 3
        retrieved_types = [s['type'] for s in sessions]
        for session_type in types:
            assert session_type in retrieved_types

    def test_api_response_headers(self):
        """Test API response headers."""
        response = requests.get(self.api_url)
        assert 'Content-Type' in response.headers
        assert 'application/json' in response.headers['Content-Type']

    def test_api_multiple_requests_consistency(self):
        """Test consistency across multiple requests."""
        payload = {
            'date': '2026-06-27',
            'title': 'Consistency Check',
            'type': 'event'
        }
        requests.post(self.api_url, json=payload)

        # Make multiple requests
        response1 = requests.get(f'{self.api_url}?date=2026-06-27')
        response2 = requests.get(f'{self.api_url}?date=2026-06-27')

        assert response1.json() == response2.json()
