import pytest
from datetime import datetime, timedelta
from page_objects import CalendarDashboardPage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import json


class TestDashboardUI:
    """Test suite for Calendar Dashboard UI."""

    @pytest.fixture(autouse=True)
    def setup(self, driver, flask_app_server):
        """Setup before each test."""
        self.page = CalendarDashboardPage(driver)
        self.page.navigate_to(flask_app_server)
        self.base_url = flask_app_server

    def test_dashboard_page_loads(self):
        """Test that dashboard page loads successfully."""
        assert self.page.is_page_loaded()

    def test_today_button_functionality(self):
        """Test Today button sets date to today."""
        # Set to a different date first
        self.page.set_date('2026-06-10')
        assert '10th' in self.page.get_date_header_text()

        # Click Today button
        self.page.click_today_button()
        today_text = datetime.now().strftime('%d').lstrip('0')
        assert today_text in self.page.get_date_header_text()

    def test_date_picker_navigation(self):
        """Test date picker changes the displayed date."""
        test_date = '2026-06-20'
        self.page.set_date(test_date)
        assert '20th' in self.page.get_date_header_text()
        assert 'June' in self.page.get_date_header_text()
        assert '2026' in self.page.get_date_header_text()

    def test_no_events_message_displayed(self):
        """Test that 'no events' message appears when no sessions exist."""
        assert self.page.has_no_events_message()
        assert self.page.get_session_count() == 0

    def test_ordinal_date_format(self):
        """Test that date is displayed with ordinal suffix."""
        test_dates = {
            '2026-06-01': '1st',
            '2026-06-02': '2nd',
            '2026-06-03': '3rd',
            '2026-06-04': '4th',
            '2026-06-21': '21st',
            '2026-06-22': '22nd',
            '2026-06-23': '23rd'
        }

        for date, expected_ordinal in test_dates.items():
            self.page.set_date(date)
            date_header = self.page.get_date_header_text()
            assert expected_ordinal in date_header, f"Expected {expected_ordinal} in {date_header}"

    def test_date_picker_input_value(self):
        """Test that date picker input reflects selected date."""
        test_date = '2026-06-25'
        self.page.set_date(test_date)

        date_input = self.page.driver.find_element(*self.page.DATE_PICKER)
        assert date_input.get_attribute('value') == test_date

    def test_dashboard_title_visible(self):
        """Test that dashboard title is visible."""
        title = self.page.driver.find_element(*self.page.DASHBOARD_TITLE)
        assert title.is_displayed()
        assert 'Calendar Dashboard' in title.text

    def test_today_button_styling(self):
        """Test that Today button has correct classes."""
        today_btn = self.page.driver.find_element(*self.page.TODAY_BUTTON)
        class_attr = today_btn.get_attribute('class')
        assert 'bg-blue-600' in class_attr
        assert 'text-white' in class_attr

    def test_date_navigation_updates_header(self):
        """Test that navigating dates updates the date header."""
        dates_and_months = {
            '2026-05-15': 'May',
            '2026-06-15': 'June',
            '2026-12-25': 'December'
        }

        for date, expected_month in dates_and_months.items():
            self.page.set_date(date)
            header = self.page.get_date_header_text()
            assert expected_month in header

    def test_page_layout_structure(self):
        """Test that page has correct layout structure."""
        # Main container
        assert self.page.driver.find_element(By.XPATH, "//div[@class='max-w-4xl mx-auto p-6']")
        # White card container
        assert self.page.driver.find_element(By.XPATH, "//div[@class='bg-white rounded-lg shadow-sm p-6 mb-6']")

    def test_multiple_date_selections(self):
        """Test multiple consecutive date selections."""
        dates = ['2026-06-01', '2026-06-10', '2026-06-20', '2026-06-30']

        for date in dates:
            self.page.set_date(date)
            date_input = self.page.driver.find_element(*self.page.DATE_PICKER)
            assert date_input.get_attribute('value') == date
