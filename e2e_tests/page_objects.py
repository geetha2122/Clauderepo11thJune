from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta


class CalendarDashboardPage:
    """Page Object Model for Calendar Dashboard."""

    # Locators
    DATE_PICKER = (By.ID, 'datePicker')
    TODAY_BUTTON = (By.ID, 'todayBtn')
    DASHBOARD_TITLE = (By.XPATH, "//h1[contains(text(), 'Calendar Dashboard')]")
    DATE_HEADER = (By.XPATH, "//h2[@class='text-xl font-semibold text-gray-800 mb-4']")
    SESSION_CARDS = (By.XPATH, "//div[@class='p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow']")
    NO_EVENTS_MESSAGE = (By.XPATH, "//p[contains(text(), 'No events, tasks or reminders')]")
    SESSION_TITLE = (By.XPATH, "//h3[@class='font-semibold text-gray-900']")
    SESSION_TYPE_BADGE = (By.XPATH, "//span[@class='inline-block mt-1 px-2 py-1 text-xs font-medium rounded']")
    SESSION_TIME = (By.XPATH, "//p[@class='mt-2 text-sm text-gray-600']")
    SESSION_DESCRIPTION = (By.XPATH, "//p[@class='mt-2 text-sm text-gray-700']")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def navigate_to(self, url='http://localhost:5000'):
        """Navigate to the dashboard."""
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located(self.DASHBOARD_TITLE))

    def is_page_loaded(self):
        """Check if the dashboard page is loaded."""
        try:
            self.wait.until(EC.presence_of_element_located(self.DASHBOARD_TITLE))
            return True
        except:
            return False

    def get_date_header_text(self):
        """Get the current date header text."""
        return self.driver.find_element(*self.DATE_HEADER).text

    def set_date(self, date_str):
        """Set the date picker to a specific date (format: YYYY-MM-DD)."""
        date_input = self.driver.find_element(*self.DATE_PICKER)
        date_input.clear()
        date_input.send_keys(date_str)
        date_input.send_keys('\n')
        self.wait.until(EC.presence_of_element_located(self.DATE_HEADER))

    def click_today_button(self):
        """Click the Today button."""
        today_btn = self.driver.find_element(*self.TODAY_BUTTON)
        today_btn.click()
        self.wait.until(EC.presence_of_element_located(self.DATE_HEADER))

    def get_session_count(self):
        """Get the number of session cards displayed."""
        try:
            return len(self.driver.find_elements(*self.SESSION_CARDS))
        except:
            return 0

    def has_no_events_message(self):
        """Check if 'no events' message is displayed."""
        try:
            self.driver.find_element(*self.NO_EVENTS_MESSAGE)
            return True
        except:
            return False

    def get_session_titles(self):
        """Get all session titles."""
        titles = []
        session_elements = self.driver.find_elements(*self.SESSION_TITLE)
        for element in session_elements:
            titles.append(element.text)
        return titles

    def get_session_types(self):
        """Get all session type badges."""
        types = []
        type_elements = self.driver.find_elements(*self.SESSION_TYPE_BADGE)
        for element in type_elements:
            types.append(element.text)
        return types

    def get_session_details(self, index=0):
        """Get details of a specific session (by index)."""
        cards = self.driver.find_elements(*self.SESSION_CARDS)
        if index >= len(cards):
            return None

        card = cards[index]
        title = card.find_element(By.XPATH, ".//h3[@class='font-semibold text-gray-900']").text
        type_badge = card.find_element(By.XPATH, ".//span[@class='inline-block mt-1 px-2 py-1 text-xs font-medium rounded']").text

        time_text = None
        description = None

        try:
            time_elem = card.find_element(By.XPATH, ".//p[@class='mt-2 text-sm text-gray-600']")
            time_text = time_elem.text
        except:
            pass

        try:
            desc_elem = card.find_element(By.XPATH, ".//p[@class='mt-2 text-sm text-gray-700']")
            description = desc_elem.text
        except:
            pass

        return {
            'title': title,
            'type': type_badge,
            'time': time_text,
            'description': description
        }

    def get_all_session_details(self):
        """Get details of all sessions."""
        sessions = []
        count = self.get_session_count()
        for i in range(count):
            session = self.get_session_details(i)
            if session:
                sessions.append(session)
        return sessions

    def verify_session_badge_color(self, session_type):
        """Verify the color class of a session type badge."""
        type_colors = {
            'event': 'bg-blue-100 text-blue-800',
            'task': 'bg-yellow-100 text-yellow-800',
            'reminder': 'bg-red-100 text-red-800'
        }
        return type_colors.get(session_type)
