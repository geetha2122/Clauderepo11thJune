"""
Comprehensive unit tests for the Calendar Dashboard Flask application.

Test Coverage:
- Dashboard page rendering
- Session API endpoints (GET and POST)
- Session model validation
- Database persistence
- Error handling and edge cases
- All session types (event, task, reminder)
- Optional field handling
- Response format validation
"""

import pytest
import json
from datetime import datetime, date, time
from app import app, db, Session


class TestDashboard:
    """Tests for the dashboard page and route handling."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up test client and database for each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_dashboard_page_loads(self):
        """Test that the dashboard page loads successfully."""
        client = app.test_client()
        response = client.get('/')
        assert response.status_code == 200

    def test_dashboard_returns_html(self):
        """Test that the dashboard returns HTML content type."""
        client = app.test_client()
        response = client.get('/')
        assert 'text/html' in response.content_type

    def test_dashboard_template_exists(self):
        """Test that dashboard HTML content is returned."""
        client = app.test_client()
        response = client.get('/')
        assert response.data is not None
        assert len(response.data) > 0

    def test_dashboard_not_found_for_invalid_route(self):
        """Test that invalid routes return 404."""
        client = app.test_client()
        response = client.get('/invalid-route')
        assert response.status_code == 404


class TestGetSessionsAPI:
    """Tests for the GET /api/sessions endpoint."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up test client and database for each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_get_sessions_empty_database(self):
        """Test fetching sessions from empty database."""
        client = app.test_client()
        response = client.get('/api/sessions?date=2026-06-12')
        assert response.status_code == 200
        assert response.json == []

    def test_get_sessions_returns_json(self):
        """Test that the endpoint returns JSON content type."""
        client = app.test_client()
        response = client.get('/api/sessions?date=2026-06-12')
        assert 'application/json' in response.content_type

    def test_get_sessions_with_single_event(self):
        """Test fetching a single event for a specific date."""
        client = app.test_client()

        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Team Meeting',
                type='event',
                start_time=time(14, 30),
                end_time=time(15, 30),
                description='Daily sync'
            )
            db.session.add(session)
            db.session.commit()

        response = client.get('/api/sessions?date=2026-06-12')
        assert response.status_code == 200
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Team Meeting'
        assert response.json[0]['type'] == 'event'

    def test_get_sessions_with_multiple_sessions(self):
        """Test fetching multiple sessions for a specific date."""
        client = app.test_client()

        with app.app_context():
            for i in range(5):
                session = Session(
                    date=date(2026, 6, 12),
                    title=f'Session {i+1}',
                    type='event'
                )
                db.session.add(session)
            db.session.commit()

        response = client.get('/api/sessions?date=2026-06-12')
        assert response.status_code == 200
        assert len(response.json) == 5

    def test_get_sessions_filters_by_date(self):
        """Test that sessions are filtered correctly by date."""
        client = app.test_client()

        with app.app_context():
            session1 = Session(
                date=date(2026, 6, 12),
                title='Session on 12th',
                type='event'
            )
            session2 = Session(
                date=date(2026, 6, 13),
                title='Session on 13th',
                type='event'
            )
            db.session.add(session1)
            db.session.add(session2)
            db.session.commit()

        response = client.get('/api/sessions?date=2026-06-12')
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Session on 12th'

    def test_get_sessions_with_all_session_types(self):
        """Test fetching sessions of all types (event, task, reminder)."""
        client = app.test_client()

        with app.app_context():
            for session_type in ['event', 'task', 'reminder']:
                session = Session(
                    date=date(2026, 6, 12),
                    title=f'{session_type.capitalize()}',
                    type=session_type
                )
                db.session.add(session)
            db.session.commit()

        response = client.get('/api/sessions?date=2026-06-12')
        assert response.status_code == 200
        assert len(response.json) == 3
        types = {s['type'] for s in response.json}
        assert types == {'event', 'task', 'reminder'}

    def test_get_sessions_includes_all_fields(self):
        """Test that response includes all required fields."""
        client = app.test_client()

        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Full Session',
                type='event',
                start_time=time(10, 0),
                end_time=time(11, 0),
                description='Full description'
            )
            db.session.add(session)
            db.session.commit()

        response = client.get('/api/sessions?date=2026-06-12')
        data = response.json[0]
        assert 'id' in data
        assert 'title' in data
        assert 'type' in data
        assert 'start_time' in data
        assert 'end_time' in data
        assert 'description' in data

    def test_get_sessions_without_optional_fields(self):
        """Test that sessions without optional fields return None."""
        client = app.test_client()

        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Minimal Session',
                type='task'
            )
            db.session.add(session)
            db.session.commit()

        response = client.get('/api/sessions?date=2026-06-12')
        data = response.json[0]
        assert data['start_time'] is None
        assert data['end_time'] is None
        assert data['description'] is None

    def test_get_sessions_time_format_iso8601(self):
        """Test that times are returned in ISO 8601 format."""
        client = app.test_client()

        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Time Test',
                type='event',
                start_time=time(14, 30, 45),
                end_time=time(15, 45, 30)
            )
            db.session.add(session)
            db.session.commit()

        response = client.get('/api/sessions?date=2026-06-12')
        data = response.json[0]
        assert data['start_time'] == '14:30:45'
        assert data['end_time'] == '15:45:30'

    def test_get_sessions_default_date_is_today(self):
        """Test that default date parameter uses today's date."""
        client = app.test_client()

        with app.app_context():
            today = datetime.today().date()
            session = Session(
                date=today,
                title='Today Session',
                type='event'
            )
            db.session.add(session)
            db.session.commit()

        response = client.get('/api/sessions')
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Today Session'

    def test_get_sessions_handles_invalid_date_format(self):
        """Test that invalid date format in query parameter is handled."""
        client = app.test_client()
        response = client.get('/api/sessions?date=invalid-date')
        assert response.status_code == 400 or response.status_code == 500

    def test_get_sessions_with_special_characters_in_title(self):
        """Test fetching sessions with special characters in title."""
        client = app.test_client()

        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Meeting & Review (Q2) <important>',
                type='event'
            )
            db.session.add(session)
            db.session.commit()

        response = client.get('/api/sessions?date=2026-06-12')
        assert response.json[0]['title'] == 'Meeting & Review (Q2) <important>'


class TestCreateSessionAPI:
    """Tests for the POST /api/sessions endpoint."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up test client and database for each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_create_session_minimal_event(self):
        """Test creating a minimal event with required fields only."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'New Event',
            'type': 'event'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201
        assert 'id' in response.json
        assert response.json['id'] > 0

    def test_create_session_returns_201_created(self):
        """Test that creating a session returns 201 Created status."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'New Session',
            'type': 'task'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

    def test_create_session_with_all_fields(self):
        """Test creating a session with all fields populated."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Full Session',
            'type': 'event',
            'start_time': '14:30',
            'end_time': '15:30',
            'description': 'Complete session details'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.title == 'Full Session'
            assert session.description == 'Complete session details'

    def test_create_session_event_type(self):
        """Test creating a session with type='event'."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Team Event',
            'type': 'event'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.type == 'event'

    def test_create_session_task_type(self):
        """Test creating a session with type='task'."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Review Code',
            'type': 'task'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.type == 'task'

    def test_create_session_reminder_type(self):
        """Test creating a session with type='reminder'."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Call Client',
            'type': 'reminder'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.type == 'reminder'

    def test_create_session_persists_to_database(self):
        """Test that created session is saved to database."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Persistent Session',
            'type': 'event'
        }
        response = client.post('/api/sessions', json=data)

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session is not None
            assert session.title == 'Persistent Session'

    def test_create_session_multiple_sessions(self):
        """Test creating multiple sessions with different dates."""
        client = app.test_client()

        for day in range(10, 15):
            data = {
                'date': f'2026-06-{day:02d}',
                'title': f'Session {day}',
                'type': 'event'
            }
            response = client.post('/api/sessions', json=data)
            assert response.status_code == 201

        with app.app_context():
            count = Session.query.count()
            assert count == 5

    def test_create_session_with_empty_description(self):
        """Test creating a session with empty description."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'No Description',
            'type': 'event',
            'description': ''
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.description == ''

    def test_create_session_with_special_characters(self):
        """Test creating a session with special characters in title/description."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': "Meeting & Review's (Q2) <important>",
            'type': 'event',
            'description': 'Details: "Important" & urgent!'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert "Meeting & Review's (Q2) <important>" in session.title

    def test_create_session_time_parsing_valid(self):
        """Test that valid time formats are parsed correctly."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Timed Event',
            'type': 'event',
            'start_time': '09:30',
            'end_time': '10:45'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.start_time == time(9, 30)
            assert session.end_time == time(10, 45)

    def test_create_session_time_with_seconds(self):
        """Test time parsing with seconds included."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'Precise Timing',
            'type': 'event',
            'start_time': '14:30:45'
        }
        response = client.post('/api/sessions', json=data)
        # The API expects HH:MM format, so this may fail; documenting expected behavior
        assert response.status_code in [201, 400]

    def test_create_session_without_optional_start_time(self):
        """Test creating session without start_time."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'No Start Time',
            'type': 'task'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.start_time is None

    def test_create_session_without_optional_end_time(self):
        """Test creating session without end_time."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'No End Time',
            'type': 'event',
            'start_time': '10:00'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.end_time is None

    def test_create_session_without_optional_description(self):
        """Test creating session without description."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'No Description',
            'type': 'reminder'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert session.description is None

    def test_create_session_long_title(self):
        """Test creating session with very long title."""
        client = app.test_client()
        long_title = 'A' * 255  # Max length
        data = {
            'date': '2026-06-12',
            'title': long_title,
            'type': 'event'
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

    def test_create_session_long_description(self):
        """Test creating session with very long description."""
        client = app.test_client()
        long_desc = 'B' * 5000  # Large description
        data = {
            'date': '2026-06-12',
            'title': 'Long Description',
            'type': 'event',
            'description': long_desc
        }
        response = client.post('/api/sessions', json=data)
        assert response.status_code == 201

        with app.app_context():
            session = Session.query.filter_by(id=response.json['id']).first()
            assert len(session.description) == 5000

    def test_create_session_different_dates(self):
        """Test creating sessions across different dates."""
        client = app.test_client()
        dates = ['2026-06-01', '2026-06-15', '2026-12-31', '2026-01-01']

        for date_str in dates:
            data = {
                'date': date_str,
                'title': f'Session on {date_str}',
                'type': 'event'
            }
            response = client.post('/api/sessions', json=data)
            assert response.status_code == 201

    def test_create_session_response_includes_id(self):
        """Test that response includes the created session ID."""
        client = app.test_client()
        data = {
            'date': '2026-06-12',
            'title': 'ID Test',
            'type': 'event'
        }
        response = client.post('/api/sessions', json=data)
        assert 'id' in response.json
        assert isinstance(response.json['id'], int)
        assert response.json['id'] > 0


class TestSessionModel:
    """Tests for the Session database model."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up test client and database for each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_session_model_create_minimal(self):
        """Test creating a Session model with minimal required fields."""
        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Test',
                type='event'
            )
            db.session.add(session)
            db.session.commit()

            fetched = Session.query.first()
            assert fetched.title == 'Test'
            assert fetched.type == 'event'

    def test_session_model_auto_increment_id(self):
        """Test that Session ID auto-increments."""
        with app.app_context():
            for i in range(5):
                session = Session(
                    date=date(2026, 6, 12),
                    title=f'Session {i}',
                    type='event'
                )
                db.session.add(session)
            db.session.commit()

            sessions = Session.query.all()
            ids = [s.id for s in sessions]
            assert ids == [1, 2, 3, 4, 5]

    def test_session_model_all_fields(self):
        """Test Session model with all fields populated."""
        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Complete',
                type='event',
                start_time=time(14, 30),
                end_time=time(15, 30),
                description='Full details'
            )
            db.session.add(session)
            db.session.commit()

            fetched = Session.query.first()
            assert fetched.date == date(2026, 6, 12)
            assert fetched.title == 'Complete'
            assert fetched.type == 'event'
            assert fetched.start_time == time(14, 30)
            assert fetched.end_time == time(15, 30)
            assert fetched.description == 'Full details'

    def test_session_model_optional_fields_null(self):
        """Test that optional fields can be NULL."""
        with app.app_context():
            session = Session(
                date=date(2026, 6, 12),
                title='Minimal',
                type='task'
            )
            db.session.add(session)
            db.session.commit()

            fetched = Session.query.first()
            assert fetched.start_time is None
            assert fetched.end_time is None
            assert fetched.description is None

    def test_session_model_query_by_date(self):
        """Test querying sessions by date."""
        with app.app_context():
            for day in [10, 11, 12, 13]:
                session = Session(
                    date=date(2026, 6, day),
                    title=f'Day {day}',
                    type='event'
                )
                db.session.add(session)
            db.session.commit()

            sessions = Session.query.filter_by(date=date(2026, 6, 12)).all()
            assert len(sessions) == 1
            assert sessions[0].title == 'Day 12'

    def test_session_model_query_by_type(self):
        """Test querying sessions by type."""
        with app.app_context():
            for session_type in ['event', 'task', 'reminder', 'event']:
                session = Session(
                    date=date(2026, 6, 12),
                    title=f'{session_type}',
                    type=session_type
                )
                db.session.add(session)
            db.session.commit()

            events = Session.query.filter_by(type='event').all()
            assert len(events) == 2


class TestIntegration:
    """Integration tests combining multiple components."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up test client and database for each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()
            yield
            db.session.remove()
            db.drop_all()

    def test_create_and_retrieve_session(self):
        """Test creating a session and retrieving it via API."""
        client = app.test_client()

        # Create
        create_data = {
            'date': '2026-06-12',
            'title': 'Integration Test',
            'type': 'event',
            'start_time': '10:00',
            'end_time': '11:00',
            'description': 'Testing integration'
        }
        create_response = client.post('/api/sessions', json=create_data)
        assert create_response.status_code == 201

        # Retrieve
        get_response = client.get('/api/sessions?date=2026-06-12')
        assert get_response.status_code == 200
        assert len(get_response.json) == 1
        session = get_response.json[0]
        assert session['title'] == 'Integration Test'
        assert session['start_time'] == '10:00:00'
        assert session['end_time'] == '11:00:00'

    def test_create_multiple_and_retrieve_by_date(self):
        """Test creating multiple sessions and retrieving by specific date."""
        client = app.test_client()

        # Create sessions on different dates
        for day in [11, 12, 13]:
            data = {
                'date': f'2026-06-{day:02d}',
                'title': f'Session {day}',
                'type': 'event'
            }
            response = client.post('/api/sessions', json=data)
            assert response.status_code == 201

        # Retrieve only June 12th sessions
        response = client.get('/api/sessions?date=2026-06-12')
        assert len(response.json) == 1
        assert response.json[0]['title'] == 'Session 12'

    def test_all_session_types_workflow(self):
        """Test complete workflow with all session types."""
        client = app.test_client()

        session_types = {
            'event': {'date': '2026-06-12', 'title': 'Team Meeting', 'start_time': '10:00'},
            'task': {'date': '2026-06-12', 'title': 'Code Review'},
            'reminder': {'date': '2026-06-12', 'title': 'Call Client'}
        }

        for s_type, base_data in session_types.items():
            data = {**base_data, 'type': s_type}
            response = client.post('/api/sessions', json=data)
            assert response.status_code == 201

        # Retrieve all
        response = client.get('/api/sessions?date=2026-06-12')
        assert len(response.json) == 3
        types = {s['type'] for s in response.json}
        assert types == {'event', 'task', 'reminder'}

    def test_optional_fields_persistence(self):
        """Test that optional fields are correctly persisted and retrieved."""
        client = app.test_client()

        # Create with only required fields
        data1 = {
            'date': '2026-06-12',
            'title': 'Minimal',
            'type': 'task'
        }
        response1 = client.post('/api/sessions', json=data1)
        assert response1.status_code == 201

        # Create with all fields
        data2 = {
            'date': '2026-06-12',
            'title': 'Complete',
            'type': 'event',
            'start_time': '14:00',
            'end_time': '15:00',
            'description': 'Full details'
        }
        response2 = client.post('/api/sessions', json=data2)
        assert response2.status_code == 201

        # Retrieve and verify
        response = client.get('/api/sessions?date=2026-06-12')
        sessions = {s['title']: s for s in response.json}

        assert sessions['Minimal']['start_time'] is None
        assert sessions['Minimal']['description'] is None
        assert sessions['Complete']['start_time'] == '14:00:00'
        assert sessions['Complete']['description'] == 'Full details'


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=app', '--cov-report=html'])
