import pytest
import requests
import json
from datetime import datetime, timedelta
from page_objects import CalendarDashboardPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class TestSessionCreation:
    """Test suite for creating sessions via API and verifying in UI."""

    @pytest.fixture(autouse=True)
    def setup(self, driver, flask_app_server):
        """Setup before each test."""
        self.page = CalendarDashboardPage(driver)
        self.page.navigate_to(flask_app_server)
        self.base_url = flask_app_server

    def create_session_via_api(self, date, title, session_type, start_time=None, end_time=None, description=None):
        """Helper to create a session via API."""
        payload = {
            'date': date,
            'title': title,
            'type': session_type,
            'start_time': start_time,
            'end_time': end_time,
            'description': description
        }
        response = requests.post(f'{self.base_url}/api/sessions', json=payload)
        assert response.status_code == 201
        return response.json()

    def test_create_event_and_display(self):
        """Test creating an event and verifying it displays on dashboard."""
        test_date = '2026-06-15'
        self.create_session_via_api(
            test_date,
            'Team Meeting',
            'event',
            '14:00',
            '15:00',
            'Weekly sync with team'
        )

        # Refresh the page to load the new session
        self.page.set_date(test_date)

        assert self.page.get_session_count() == 1
        assert not self.page.has_no_events_message()

        titles = self.page.get_session_titles()
        assert 'Team Meeting' in titles

    def test_create_task_and_display(self):
        """Test creating a task and verifying it displays on dashboard."""
        test_date = '2026-06-18'
        self.create_session_via_api(
            test_date,
            'Complete project report',
            'task',
            description='Finish the quarterly report'
        )

        self.page.set_date(test_date)

        assert self.page.get_session_count() == 1
        types = self.page.get_session_types()
        assert 'task' in types

    def test_create_reminder_and_display(self):
        """Test creating a reminder and verifying it displays on dashboard."""
        test_date = '2026-06-20'
        self.create_session_via_api(
            test_date,
            'Call dentist',
            'reminder',
            description='Schedule appointment'
        )

        self.page.set_date(test_date)

        assert self.page.get_session_count() == 1
        types = self.page.get_session_types()
        assert 'reminder' in types

    def test_multiple_sessions_same_date(self):
        """Test creating multiple sessions on the same date."""
        test_date = '2026-06-22'

        self.create_session_via_api(test_date, 'Morning standup', 'event', '09:00', '09:30')
        self.create_session_via_api(test_date, 'Code review', 'event', '10:00', '11:00')
        self.create_session_via_api(test_date, 'Buy groceries', 'task')
        self.create_session_via_api(test_date, 'Client call follow-up', 'reminder')

        self.page.set_date(test_date)

        assert self.page.get_session_count() == 4

    def test_session_details_display(self):
        """Test that session details are correctly displayed."""
        test_date = '2026-06-25'
        self.create_session_via_api(
            test_date,
            'Project kickoff',
            'event',
            '13:30',
            '14:30',
            'Starting new client project'
        )

        self.page.set_date(test_date)

        session = self.page.get_session_details(0)
        assert session['title'] == 'Project kickoff'
        assert session['type'] == 'event'
        assert '13:30' in session['time']
        assert '14:30' in session['time']
        assert session['description'] == 'Starting new client project'

    def test_event_badge_color(self):
        """Test that event badge has correct color."""
        test_date = '2026-06-26'
        self.create_session_via_api(test_date, 'Planning', 'event', '10:00', '11:00')

        self.page.set_date(test_date)

        session = self.page.get_session_details(0)
        assert session['type'] == 'event'

    def test_task_badge_color(self):
        """Test that task badge has correct color."""
        test_date = '2026-06-27'
        self.create_session_via_api(test_date, 'Review proposal', 'task')

        self.page.set_date(test_date)

        session = self.page.get_session_details(0)
        assert session['type'] == 'task'

    def test_reminder_badge_color(self):
        """Test that reminder badge has correct color."""
        test_date = '2026-06-28'
        self.create_session_via_api(test_date, 'Pay bills', 'reminder')

        self.page.set_date(test_date)

        session = self.page.get_session_details(0)
        assert session['type'] == 'reminder'

    def test_session_without_time(self):
        """Test session created without start/end times."""
        test_date = '2026-06-29'
        self.create_session_via_api(
            test_date,
            'All day event',
            'task',
            description='No specific time'
        )

        self.page.set_date(test_date)

        session = self.page.get_session_details(0)
        assert session['title'] == 'All day event'
        assert session['time'] is None

    def test_session_with_time_display_format(self):
        """Test that session times are displayed in correct format."""
        test_date = '2026-06-30'
        self.create_session_via_api(
            test_date,
            'Afternoon meeting',
            'event',
            '14:30',
            '15:45'
        )

        self.page.set_date(test_date)

        session = self.page.get_session_details(0)
        assert '14:30' in session['time']
        assert '15:45' in session['time']

    def test_sessions_different_dates(self):
        """Test sessions on different dates don't appear together."""
        self.create_session_via_api('2026-06-10', 'Event A', 'event')
        self.create_session_via_api('2026-06-15', 'Event B', 'event')

        # Check date 1
        self.page.set_date('2026-06-10')
        assert self.page.get_session_count() == 1
        titles = self.page.get_session_titles()
        assert 'Event A' in titles
        assert 'Event B' not in titles

        # Check date 2
        self.page.set_date('2026-06-15')
        assert self.page.get_session_count() == 1
        titles = self.page.get_session_titles()
        assert 'Event B' in titles
        assert 'Event A' not in titles

    def test_session_with_special_characters(self):
        """Test session with special characters in title."""
        test_date = '2026-07-01'
        self.create_session_via_api(
            test_date,
            'Q3 Planning: Goals & Objectives',
            'event',
            description='Review 2026 Q3 targets - 50% done!'
        )

        self.page.set_date(test_date)

        session = self.page.get_session_details(0)
        assert session['title'] == 'Q3 Planning: Goals & Objectives'
        assert 'Q3 targets - 50% done!' in session['description']

    def test_mixed_session_types_display(self):
        """Test that mixed session types display with correct styling."""
        test_date = '2026-07-05'

        self.create_session_via_api(test_date, 'Event 1', 'event', '09:00', '10:00')
        self.create_session_via_api(test_date, 'Task 1', 'task')
        self.create_session_via_api(test_date, 'Reminder 1', 'reminder')
        self.create_session_via_api(test_date, 'Event 2', 'event', '14:00', '15:00')

        self.page.set_date(test_date)

        assert self.page.get_session_count() == 4
        types = self.page.get_session_types()
        assert types.count('event') == 2
        assert types.count('task') == 1
        assert types.count('reminder') == 1
