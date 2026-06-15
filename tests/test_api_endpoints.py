"""
Unit tests for Flask API endpoints.

Tests cover:
- GET / (dashboard page)
- GET /api/sessions (list sessions by date)
- POST /api/sessions (create new session)
- Status codes, response formats, and error handling
"""

import pytest
import json
from datetime import date, time
from app import app, db, Session


class TestDashboardRoute:
    """Tests for the GET / route."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize test database for each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_dashboard_returns_200_ok(self):
        """Test that dashboard route returns HTTP 200."""
        # Arrange
        client = app.test_client()

        # Act
        response = client.get('/')

        # Assert
        assert response.status_code == 200

    def test_dashboard_returns_html_content_type(self):
        """Test that dashboard returns HTML content type."""
        # Arrange
        client = app.test_client()

        # Act
        response = client.get('/')

        # Assert
        assert 'text/html' in response.content_type

    def test_dashboard_response_has_content(self):
        """Test that dashboard response contains HTML content."""
        # Arrange
        client = app.test_client()

        # Act
        response = client.get('/')

        # Assert
        assert response.data is not None
        assert len(response.data) > 0

    def test_invalid_route_returns_404(self):
        """Test that requesting non-existent route returns 404."""
        # Arrange
        client = app.test_client()

        # Act
        response = client.get('/nonexistent-route')

        # Assert
        assert response.status_code == 404


class TestGetSessionsEndpoint:
    """Tests for the GET /api/sessions endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize test database for each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_get_sessions_returns_200_ok(self):
        """Test that endpoint returns HTTP 200 on success."""
        # Arrange
        client = app.test_client()

        # Act
        response = client.get('/api/sessions?date=2026-06-12')

        # Assert
        assert response.status_code == 200

    def test_get_sessions_returns_json(self):
        """Test that endpoint returns JSON content type."""
        # Arrange
        client = app.test_client()

        # Act
        response = client.get('/api/sessions?date=2026-06-12')

        # Assert
        assert 'application/json' in response.content_type

    def test_get_sessions_empty_database_returns_empty_array(self):
        """Test fetching sessions from empty database returns empty array."""
        # Arrange
        client = app.test_client()

        # Act
        response = client.get('/api/sessions?date=2026-06-12')

        # Assert
        assert response.json == []

    def test_get_sessions_returns_single_session(self):
        """Test fetching single session for a date."""
        # Arrange
        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Team Meeting',
                type='event'
            )
            db.session.add(session)
            db.session.commit()

        client = app.test_client()

        # Act
        response = client.get('/api/sessions?date=2026-06-12')

        # Assert
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Team Meeting'
        assert response.json[0]['type'] == 'event'

    def test_get_sessions_returns_multiple_sessions(self):
        """Test fetching multiple sessions for same date."""
        # Arrange
        with app.app_context():
            for i in range(3):
                session = Session(
                    date=date(2026, 6, 12),
                    title=f'Session {i}',
                    type='event'
                )
                db.session.add(session)
            db.session.commit()

        client = app.test_client()

        # Act
        response = client.get('/api/sessions?date=2026-06-12')

        # Assert
        assert response.status_code == 200
        assert len(response.json) == 3

    def test_get_sessions_filters_by_date(self):
        """Test that sessions are correctly filtered by date."""
        # Arrange
        with app.app_context():
            session_12 = Session(
                date=date(2026, 6, 12),
                title='June 12th',
                type='event'
            )
            session_13 = Session(
                date=date(2026, 6, 13),
                title='June 13th',
                type='event'
            )
            db.session.add(session_12)
            db.session.add(session_13)
            db.session.commit()

        client = app.test_client()

        # Act
        response = client.get('/api/sessions?date=2026-06-12')

        # Assert
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'June 12th'

    def test_get_sessions_includes_all_response_fields(self):
        """Test that response includes all required fields."""
        # Arrange
        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Full Session',
                type='event',
                start_time=time(10, 0),
                end_time=time(11, 0),
                description='Test description'
            )
            db.session.add(session)
            db.session.commit()

        client = app.test_client()

        # Act
        response = client.get('/api/sessions?date=2026-06-12')
        assert len(response.json) > 0, "Expected at least one session in response"
        session_data = response.json[0]

        # Assert
        assert 'id' in session_data
        assert 'title' in session_data
        assert 'type' in session_data
        assert 'start_time' in session_data
        assert 'end_time' in session_data
        assert 'description' in session_data

    def test_get_sessions_optional_fields_are_none(self):
        """Test that optional fields are null when not provided."""
        # Arrange
        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Minimal',
                type='task'
            )
            db.session.add(session)
            db.session.commit()

        client = app.test_client()

        # Act
        response = client.get('/api/sessions?date=2026-06-12')

        # Assert
        assert response.json[0]['start_time'] is None
        assert response.json[0]['end_time'] is None
        assert response.json[0]['description'] is None

    def test_get_sessions_time_format_iso8601(self):
        """Test that times are returned in ISO 8601 format."""
        # Arrange
        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Timed',
                type='event',
                start_time=time(14, 30, 45),
                end_time=time(15, 45, 30)
            )
            db.session.add(session)
            db.session.commit()

        client = app.test_client()

        # Act
        response = client.get('/api/sessions?date=2026-06-12')

        # Assert
        assert response.json[0]['start_time'] == '14:30:45'
        assert response.json[0]['end_time'] == '15:45:30'

    def test_get_sessions_with_all_session_types(self):
        """Test fetching sessions of all three types."""
        # Arrange
        with app.app_context():
            for session_type in ['event', 'task', 'reminder']:
                session = Session(
                    date=date(2026, 6, 12),
                    title=session_type,
                    type=session_type
                )
                db.session.add(session)
            db.session.commit()

        client = app.test_client()

        # Act
        response = client.get('/api/sessions?date=2026-06-12')

        # Assert
        types = {s['type'] for s in response.json}
        assert types == {'event', 'task', 'reminder'}

    def test_get_sessions_with_special_characters_in_title(self):
        """Test fetching sessions with special characters."""
        # Arrange
        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Meeting & Review (Q2) <priority>',
                type='event'
            )
            db.session.add(session)
            db.session.commit()

        client = app.test_client()

        # Act
        response = client.get('/api/sessions?date=2026-06-12')

        # Assert
        assert response.json[0]['title'] == 'Meeting & Review (Q2) <priority>'

    def test_get_sessions_default_date_uses_today(self):
        """Test that missing date parameter defaults to today's date."""
        # Arrange
        from datetime import datetime
        today = datetime.today().date()

        with app.app_context():
            session = Session(
                date=today,
                title='Today Session',
                type='event'
            )
            db.session.add(session)
            db.session.commit()

        client = app.test_client()

        # Act - request without date parameter
        response = client.get('/api/sessions')

        # Assert
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Today Session'


class TestPostSessionsEndpoint:
    """Tests for the POST /api/sessions endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize test database for each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_create_session_returns_201_created(self):
        """Test that successful creation returns 201 Created."""
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

    def test_create_session_response_includes_id(self):
        """Test that response includes created session ID."""
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
        assert 'id' in response.json
        assert isinstance(response.json['id'], int)
        assert response.json['id'] > 0

    def test_create_session_with_required_fields_only(self):
        """Test creating session with only required fields."""
        # Arrange
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Minimal Event',
            'type': 'event'
        }

        # Act
        response = client.post('/api/sessions', json=data)

        # Assert
        assert response.status_code == 201
        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.title == 'Minimal Event'

    def test_create_session_with_all_fields(self):
        """Test creating session with all fields populated."""
        # Arrange
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Complete Event',
            'type': 'event',
            'start_time': '14:30',
            'end_time': '15:30',
            'description': 'Full details'
        }

        # Act
        response = client.post('/api/sessions', json=data)

        # Assert
        assert response.status_code == 201
        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.start_time == time(14, 30)
            assert session.end_time == time(15, 30)
            assert session.description == 'Full details'

    def test_create_session_persists_to_database(self):
        """Test that created session is saved to database."""
        # Arrange
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Persistent Event',
            'type': 'event'
        }

        # Act
        response = client.post('/api/sessions', json=data)
        session_id = response.json['id']

        # Assert
        with app.app_context():
            session = Session.query.filter_by(id=session_id).first()
            assert session is not None
            assert session.title == 'Persistent Event'

    def test_create_session_event_type(self):
        """Test creating session with type='event'."""
        # Arrange
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Event Type',
            'type': 'event'
        }

        # Act
        response = client.post('/api/sessions', json=data)

        # Assert
        assert response.status_code == 201
        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.type == 'event'

    def test_create_session_task_type(self):
        """Test creating session with type='task'."""
        # Arrange
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Task Type',
            'type': 'task'
        }

        # Act
        response = client.post('/api/sessions', json=data)

        # Assert
        assert response.status_code == 201
        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.type == 'task'

    def test_create_session_reminder_type(self):
        """Test creating session with type='reminder'."""
        # Arrange
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Reminder Type',
            'type': 'reminder'
        }

        # Act
        response = client.post('/api/sessions', json=data)

        # Assert
        assert response.status_code == 201
        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.type == 'reminder'

    def test_create_session_multiple_sessions(self):
        """Test creating multiple sessions in sequence."""
        # Arrange
        client = app.test_client()

        # Act
        for i in range(5):
            data = {
                'date': '2026-06-12',
                'title': f'Session {i}',
                'type': 'event'
            }
            response = client.post('/api/sessions', json=data)
            assert response.status_code == 201

        # Assert
        with app.app_context():
            sessions = Session.query.all()
            assert len(sessions) == 5

    def test_create_session_with_empty_optional_fields(self):
        """Test creating session with empty optional fields."""
        # Arrange
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'No Optional',
            'type': 'task',
            'description': ''
        }

        # Act
        response = client.post('/api/sessions', json=data)

        # Assert
        assert response.status_code == 201
        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.description == ''

    def test_create_session_with_special_characters(self):
        """Test creating session with special characters."""
        # Arrange
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': "Event & Review's (Q2) <urgent>",
            'type': 'event',
            'description': 'Details: "Important" & critical!'
        }

        # Act
        response = client.post('/api/sessions', json=data)

        # Assert
        assert response.status_code == 201
        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert "Event & Review's (Q2) <urgent>" in session.title

    def test_create_session_with_unicode_characters(self):
        """Test creating session with unicode characters."""
        # Arrange
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': '会议 Встреча ميتينج',
            'type': 'event'
        }

        # Act
        response = client.post('/api/sessions', json=data)

        # Assert
        assert response.status_code == 201
        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert '会议' in session.title

    def test_create_session_with_long_title(self):
        """Test creating session with maximum length title."""
        # Arrange
        client = app.test_client()
        long_title = 'A' * 255
        data = {
            'date': '2026-06-12',
            'title': long_title,
            'type': 'event'
        }

        # Act
        response = client.post('/api/sessions', json=data)

        # Assert
        assert response.status_code == 201

    def test_create_session_with_long_description(self):
        """Test creating session with large description."""
        # Arrange
        client = app.test_client()
        long_desc = 'B' * 5000
        data = {
            'date': '2026-06-12',
            'title': 'Long Desc',
            'type': 'event',
            'description': long_desc
        }

        # Act
        response = client.post('/api/sessions', json=data)

        # Assert
        assert response.status_code == 201
        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert len(session.description) == 5000

    def test_create_session_with_various_dates(self):
        """Test creating sessions across different dates."""
        # Arrange
        client = app.test_client()
        test_dates = ['2026-01-01', '2026-06-15', '2026-12-31']

        # Act
        for date_str in test_dates:
            data = {
                'date': date_str,
                'title': f'Event {date_str}',
                'type': 'event'
            }
            response = client.post('/api/sessions', json=data)
            assert response.status_code == 201

        # Assert
        with app.app_context():
            sessions = Session.query.all()
            assert len(sessions) == 3
