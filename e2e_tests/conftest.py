import pytest
import subprocess
import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')
PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope='session')
def flask_app_server():
    """Start the Flask app server before tests and stop after."""
    # Check if server is already running
    try:
        import requests
        requests.get(f'{BASE_URL}/', timeout=2)
        print(f"\nFlask server already running at {BASE_URL}")
        yield BASE_URL
    except requests.exceptions.RequestException:
        # Start the server
        print("\nStarting Flask server...")
        env = os.environ.copy()
        env['FLASK_ENV'] = 'testing'

        process = subprocess.Popen(
            ['python', 'app.py'],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )

        # Wait for server to start
        max_retries = 30
        for i in range(max_retries):
            try:
                import requests
                requests.get(f'{BASE_URL}/', timeout=2)
                print(f"Flask server started successfully")
                break
            except requests.exceptions.RequestException:
                if i == max_retries - 1:
                    process.terminate()
                    raise RuntimeError("Failed to start Flask server")
                time.sleep(1)

        yield BASE_URL

        # Clean up
        print("\nStopping Flask server...")
        process.terminate()
        process.wait(timeout=10)


@pytest.fixture(scope='function')
def driver(flask_app_server):
    """Create and configure Firefox WebDriver for each test."""
    options = webdriver.FirefoxOptions()
    # Uncomment for headless mode
    # options.add_argument('--headless')
    options.add_argument('--width=1920')
    options.add_argument('--height=1080')

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture(scope='function')
def driver_wait(driver):
    """Provide explicit wait helper."""
    return WebDriverWait(driver, 10)


@pytest.fixture(autouse=True)
def clear_database():
    """Clear the database before each test."""
    db_path = PROJECT_ROOT / 'instance' / 'calendar.db'
    if db_path.exists():
        db_path.unlink()
    yield
    # Cleanup after test
    if db_path.exists():
        db_path.unlink()
