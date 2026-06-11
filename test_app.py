import unittest
import json
from datetime import datetime, date, time
from app import app, db, Session


class CalendarTestCase(unittest.TestCase):
    """Unit tests for calendar dashboard API"""

    def setUp(self):
        """Set up test client and database before each test"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app = app

        with app.app_context():
            db.create_all()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up database after each test"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Dashboard tests
    def test_dashboard_page_loads(self):
        """Test that dashboard page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Calendar Dashboard', response.data)

    def test_dashboard_contains_html(self):
        """Test that dashboard returns valid HTML"""
        response = self.client.get('/')
        self.assertTrue(response.data.startswith(b'<!DOCTYPE'))

    # GET /api/sessions tests
    def test_get_sessions_empty_database(self):
        """Test getting sessions when database is empty"""
        response = self.client.get('/api/sessions')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

    def test_get_sessions_with_date_parameter(self):
        """Test getting sessions for a specific date"""
        with app.app_context():
            test_date = date(2026, 6, 11)
            session = Session(
                date=test_date,
                title='Test Event',
                type='event',
                description='Test Description'
            )
            db.session.add(session)
            db.session.commit()

        response = self.client.get('/api/sessions?date=2026-06-11')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Test Event')
        self.assertEqual(data[0]['type'], 'event')

    def test_get_sessions_default_to_today(self):
        """Test that sessions default to today's date when no date parameter"""
        response = self.client.get('/api/sessions')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_sessions_filters_by_date(self):
        """Test that only sessions for the specified date are returned"""
        with app.app_context():
            session1 = Session(
                date=date(2026, 6, 11),
                title='Event 1',
                type='event'
            )
            session2 = Session(
                date=date(2026, 6, 12),
                title='Event 2',
                type='task'
            )
            db.session.add_all([session1, session2])
            db.session.commit()

        response = self.client.get('/api/sessions?date=2026-06-11')
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Event 1')

    def test_get_sessions_includes_all_fields(self):
        """Test that session response includes all required fields"""
        with app.app_context():
            session = Session(
                date=date(2026, 6, 11),
                title='Test Event',
                type='event',
                start_time=time(10, 0),
                end_time=time(11, 0),
                description='Test Description'
            )
            db.session.add(session)
            db.session.commit()

        response = self.client.get('/api/sessions?date=2026-06-11')
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        session_data = data[0]

        self.assertIn('id', session_data)
        self.assertIn('title', session_data)
        self.assertIn('type', session_data)
        self.assertIn('start_time', session_data)
        self.assertIn('end_time', session_data)
        self.assertIn('description', session_data)

    def test_get_sessions_time_format(self):
        """Test that times are returned in ISO format"""
        with app.app_context():
            session = Session(
                date=date(2026, 6, 11),
                title='Test Event',
                type='event',
                start_time=time(14, 30),
                end_time=time(15, 45)
            )
            db.session.add(session)
            db.session.commit()

        response = self.client.get('/api/sessions?date=2026-06-11')
        data = json.loads(response.data)
        self.assertEqual(data[0]['start_time'], '14:30:00')
        self.assertEqual(data[0]['end_time'], '15:45:00')

    def test_get_sessions_null_times(self):
        """Test that null times are handled correctly"""
        with app.app_context():
            session = Session(
                date=date(2026, 6, 11),
                title='All Day Event',
                type='event'
            )
            db.session.add(session)
            db.session.commit()

        response = self.client.get('/api/sessions?date=2026-06-11')
        data = json.loads(response.data)
        self.assertIsNone(data[0]['start_time'])
        self.assertIsNone(data[0]['end_time'])

    # POST /api/sessions tests
    def test_create_session_basic(self):
        """Test creating a basic session"""
        payload = {
            'date': '2026-06-11',
            'title': 'Team Meeting',
            'type': 'event'
        }
        response = self.client.post('/api/sessions',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('id', data)

    def test_create_session_with_all_fields(self):
        """Test creating a session with all fields"""
        payload = {
            'date': '2026-06-11',
            'title': 'Team Meeting',
            'type': 'event',
            'start_time': '10:00',
            'end_time': '11:00',
            'description': 'Discuss project updates'
        }
        response = self.client.post('/api/sessions',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)

        with app.app_context():
            session = Session.query.first()
            self.assertEqual(session.title, 'Team Meeting')
            self.assertEqual(session.type, 'event')
            self.assertEqual(session.start_time, time(10, 0))
            self.assertEqual(session.end_time, time(11, 0))
            self.assertEqual(session.description, 'Discuss project updates')

    def test_create_task_type(self):
        """Test creating a task type session"""
        payload = {
            'date': '2026-06-11',
            'title': 'Complete Report',
            'type': 'task'
        }
        response = self.client.post('/api/sessions',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)

        with app.app_context():
            session = Session.query.first()
            self.assertEqual(session.type, 'task')

    def test_create_reminder_type(self):
        """Test creating a reminder type session"""
        payload = {
            'date': '2026-06-11',
            'title': 'Doctor Appointment',
            'type': 'reminder'
        }
        response = self.client.post('/api/sessions',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)

        with app.app_context():
            session = Session.query.first()
            self.assertEqual(session.type, 'reminder')

    def test_create_session_persists_to_database(self):
        """Test that created session is saved to database"""
        payload = {
            'date': '2026-06-11',
            'title': 'Team Meeting',
            'type': 'event'
        }
        self.client.post('/api/sessions',
                        data=json.dumps(payload),
                        content_type='application/json')

        with app.app_context():
            sessions = Session.query.all()
            self.assertEqual(len(sessions), 1)
            self.assertEqual(sessions[0].title, 'Team Meeting')

    def test_create_session_returns_id(self):
        """Test that created session returns the correct ID"""
        payload = {
            'date': '2026-06-11',
            'title': 'Team Meeting',
            'type': 'event'
        }
        response = self.client.post('/api/sessions',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        data = json.loads(response.data)

        with app.app_context():
            session = Session.query.first()
            self.assertEqual(data['id'], session.id)

    def test_create_session_with_optional_description(self):
        """Test creating session with optional description"""
        payload = {
            'date': '2026-06-11',
            'title': 'Meeting',
            'type': 'event',
            'description': 'Quarterly review'
        }
        response = self.client.post('/api/sessions',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)

        with app.app_context():
            session = Session.query.first()
            self.assertEqual(session.description, 'Quarterly review')

    def test_create_multiple_sessions(self):
        """Test creating multiple sessions"""
        payloads = [
            {'date': '2026-06-11', 'title': 'Event 1', 'type': 'event'},
            {'date': '2026-06-11', 'title': 'Task 1', 'type': 'task'},
            {'date': '2026-06-12', 'title': 'Reminder 1', 'type': 'reminder'}
        ]

        for payload in payloads:
            self.client.post('/api/sessions',
                            data=json.dumps(payload),
                            content_type='application/json')

        with app.app_context():
            all_sessions = Session.query.all()
            self.assertEqual(len(all_sessions), 3)

    def test_create_and_retrieve_session(self):
        """Test creating a session and then retrieving it"""
        create_payload = {
            'date': '2026-06-11',
            'title': 'Team Meeting',
            'type': 'event',
            'start_time': '10:00',
            'end_time': '11:00',
            'description': 'Planning session'
        }
        self.client.post('/api/sessions',
                        data=json.dumps(create_payload),
                        content_type='application/json')

        response = self.client.get('/api/sessions?date=2026-06-11')
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Team Meeting')
        self.assertEqual(data[0]['type'], 'event')

    def test_date_parsing_valid_format(self):
        """Test that valid date format is accepted"""
        payload = {
            'date': '2026-12-25',
            'title': 'Christmas',
            'type': 'event'
        }
        response = self.client.post('/api/sessions',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_time_parsing_valid_format(self):
        """Test that valid time format is accepted"""
        payload = {
            'date': '2026-06-11',
            'title': 'Meeting',
            'type': 'event',
            'start_time': '23:59',
            'end_time': '23:59'
        }
        response = self.client.post('/api/sessions',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)


class SessionModelTestCase(unittest.TestCase):
    """Unit tests for Session model"""

    def setUp(self):
        """Set up test database"""
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up database"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_session_creation(self):
        """Test creating a Session object"""
        with app.app_context():
            session = Session(
                date=date(2026, 6, 11),
                title='Test Event',
                type='event'
            )
            self.assertIsNotNone(session)
            self.assertEqual(session.title, 'Test Event')

    def test_session_with_times(self):
        """Test Session with start and end times"""
        with app.app_context():
            session = Session(
                date=date(2026, 6, 11),
                title='Meeting',
                type='event',
                start_time=time(10, 30),
                end_time=time(11, 30)
            )
            self.assertEqual(session.start_time, time(10, 30))
            self.assertEqual(session.end_time, time(11, 30))

    def test_session_nullable_fields(self):
        """Test that optional fields can be null"""
        with app.app_context():
            session = Session(
                date=date(2026, 6, 11),
                title='All Day Event',
                type='event'
            )
            self.assertIsNone(session.start_time)
            self.assertIsNone(session.end_time)
            self.assertIsNone(session.description)


if __name__ == '__main__':
    unittest.main()
