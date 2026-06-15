import pytest
import requests
from datetime import datetime, timedelta
from page_objects import CalendarDashboardPage


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    @pytest.fixture(autouse=True)
    def setup(self, driver, flask_app_server):
        """Setup before each test."""
        self.page = CalendarDashboardPage(driver)
        self.page.navigate_to(flask_app_server)
        self.base_url = flask_app_server
        self.api_url = f'{flask_app_server}/api/sessions'

    def test_very_long_title(self):
        """Test session with very long title."""
        long_title = 'A' * 500  # Very long title
        payload = {
            'date': '2026-06-15',
            'title': long_title,
            'type': 'event'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2026-06-15')
        titles = self.page.get_session_titles()
        assert long_title in titles

    def test_very_long_description(self):
        """Test session with very long description."""
        long_desc = 'Lorem ipsum ' * 100
        payload = {
            'date': '2026-06-16',
            'title': 'Long Description Test',
            'type': 'event',
            'description': long_desc
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2026-06-16')
        session = self.page.get_session_details(0)
        assert session['description'] == long_desc

    def test_unicode_characters_in_title(self):
        """Test session with unicode characters."""
        unicode_title = '日本語 Русский العربية Emoji: 🎉🚀💡'
        payload = {
            'date': '2026-06-17',
            'title': unicode_title,
            'type': 'event'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2026-06-17')
        titles = self.page.get_session_titles()
        assert unicode_title in titles

    def test_unicode_in_description(self):
        """Test session with unicode in description."""
        unicode_desc = 'Meeting notes: 你好 мир مرحبا 🌍'
        payload = {
            'date': '2026-06-18',
            'title': 'Unicode Description',
            'type': 'task',
            'description': unicode_desc
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2026-06-18')
        session = self.page.get_session_details(0)
        assert unicode_desc in session['description']

    def test_session_with_all_special_characters(self):
        """Test session title with special characters."""
        special_title = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        payload = {
            'date': '2026-06-19',
            'title': special_title,
            'type': 'event'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2026-06-19')
        titles = self.page.get_session_titles()
        assert special_title in titles

    def test_midnight_time_boundary(self):
        """Test session at midnight (00:00)."""
        payload = {
            'date': '2026-06-20',
            'title': 'Midnight Event',
            'type': 'event',
            'start_time': '00:00',
            'end_time': '01:00'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2026-06-20')
        session = self.page.get_session_details(0)
        assert '00:00' in session['time']

    def test_end_of_day_time_boundary(self):
        """Test session at end of day (23:59)."""
        payload = {
            'date': '2026-06-21',
            'title': 'Late Evening Event',
            'type': 'event',
            'start_time': '23:00',
            'end_time': '23:59'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2026-06-21')
        session = self.page.get_session_details(0)
        assert '23:59' in session['time']

    def test_leap_year_date(self):
        """Test with leap year date."""
        # 2026 is not a leap year, but 2024 is
        payload = {
            'date': '2024-02-29',
            'title': 'Leap Day Event',
            'type': 'event'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2024-02-29')
        assert self.page.get_session_count() == 1

    def test_very_far_future_date(self):
        """Test with far future date."""
        payload = {
            'date': '2099-12-31',
            'title': 'Far Future Event',
            'type': 'event'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2099-12-31')
        assert self.page.get_session_count() == 1

    def test_historical_date(self):
        """Test with historical date."""
        payload = {
            'date': '2000-01-01',
            'title': 'Y2K Event',
            'type': 'event'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2000-01-01')
        assert self.page.get_session_count() == 1

    def test_fifty_sessions_same_date(self):
        """Test with many sessions on same date."""
        test_date = '2026-06-22'

        for i in range(50):
            payload = {
                'date': test_date,
                'title': f'Event {i+1}',
                'type': 'event'
            }
            requests.post(self.api_url, json=payload)

        self.page.set_date(test_date)
        assert self.page.get_session_count() == 50

    def test_empty_string_title_handling(self):
        """Test handling of empty title (should fail)."""
        payload = {
            'date': '2026-06-23',
            'title': '',
            'type': 'event'
        }
        response = requests.post(self.api_url, json=payload)
        # Should fail as title is required
        assert response.status_code != 201

    def test_null_title_handling(self):
        """Test handling of null title (should fail)."""
        payload = {
            'date': '2026-06-24',
            'title': None,
            'type': 'event'
        }
        response = requests.post(self.api_url, json=payload)
        # Should fail as title is required
        assert response.status_code != 201

    def test_whitespace_only_title(self):
        """Test title with only whitespace."""
        payload = {
            'date': '2026-06-25',
            'title': '   ',
            'type': 'event'
        }
        response = requests.post(self.api_url, json=payload)
        # Should succeed as it's technically not empty
        if response.status_code == 201:
            self.page.set_date('2026-06-25')
            titles = self.page.get_session_titles()
            assert '   ' in titles

    def test_consecutive_date_navigation(self):
        """Test rapid consecutive date navigation."""
        dates = [f'2026-06-{i:02d}' for i in range(1, 31)]

        for date in dates:
            self.page.set_date(date)
            # Should always succeed without errors
            assert self.page.is_page_loaded()

    def test_invalid_time_format(self):
        """Test invalid time format rejection."""
        payload = {
            'date': '2026-06-26',
            'title': 'Bad Time Event',
            'type': 'event',
            'start_time': '25:00',  # Invalid hour
            'end_time': 'not-a-time'
        }
        response = requests.post(self.api_url, json=payload)
        # API should handle gracefully
        if response.status_code == 201:
            self.page.set_date('2026-06-26')

    def test_zero_duration_event(self):
        """Test event with same start and end time."""
        payload = {
            'date': '2026-06-27',
            'title': 'Zero Duration Event',
            'type': 'event',
            'start_time': '14:30',
            'end_time': '14:30'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2026-06-27')
        session = self.page.get_session_details(0)
        assert session['title'] == 'Zero Duration Event'

    def test_reversed_time_event(self):
        """Test event with end time before start time."""
        payload = {
            'date': '2026-06-28',
            'title': 'Reversed Time Event',
            'type': 'event',
            'start_time': '15:00',
            'end_time': '14:00'  # Before start time
        }
        response = requests.post(self.api_url, json=payload)
        # API should still accept it (business logic decision)
        if response.status_code == 201:
            self.page.set_date('2026-06-28')
            assert self.page.get_session_count() == 1

    def test_rapid_session_creation(self):
        """Test creating many sessions rapidly."""
        test_date = '2026-06-29'

        for i in range(10):
            payload = {
                'date': test_date,
                'title': f'Quick Event {i+1}',
                'type': 'event'
            }
            requests.post(self.api_url, json=payload)

        self.page.set_date(test_date)
        assert self.page.get_session_count() == 10

    def test_session_type_case_sensitivity(self):
        """Test session type validation."""
        test_date = '2026-06-30'

        # Valid types
        for session_type in ['event', 'task', 'reminder']:
            payload = {
                'date': test_date,
                'title': f'{session_type.capitalize()} Type',
                'type': session_type
            }
            response = requests.post(self.api_url, json=payload)
            assert response.status_code == 201

    def test_html_injection_in_title(self):
        """Test HTML injection attempt in title."""
        html_title = '<script>alert("XSS")</script>'
        payload = {
            'date': '2026-07-01',
            'title': html_title,
            'type': 'event'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2026-07-01')
        # HTML should be displayed as text, not executed
        titles = self.page.get_session_titles()
        assert html_title in titles

    def test_html_injection_in_description(self):
        """Test HTML injection attempt in description."""
        html_desc = '<img src=x onerror="alert(\'XSS\')">'
        payload = {
            'date': '2026-07-02',
            'title': 'HTML Test',
            'type': 'event',
            'description': html_desc
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        self.page.set_date('2026-07-02')
        session = self.page.get_session_details(0)
        # Should be displayed as text
        assert html_desc in session['description']

    def test_sql_injection_attempt(self):
        """Test SQL injection attempt."""
        sql_title = "'; DROP TABLE sessions; --"
        payload = {
            'date': '2026-07-03',
            'title': sql_title,
            'type': 'event'
        }
        response = requests.post(self.api_url, json=payload)
        assert response.status_code == 201

        # Database should still be functional
        response = requests.get(f'{self.api_url}?date=2026-07-03')
        assert response.status_code == 200
        assert len(response.json()) > 0
