"""
Pytest configuration and shared fixtures for calendar dashboard tests.

This module provides reusable fixtures for Flask app setup, database initialization,
and test client creation to reduce duplication across test modules.
"""

import pytest
from app import app, db


@pytest.fixture
def app_instance():
    """
    Create and configure Flask application instance for testing.

    Uses in-memory SQLite database to ensure isolation between tests.
    Yields app with active context, then cleans up database and context.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_instance):
    """
    Provide Flask test client for making HTTP requests in tests.

    Depends on app_instance fixture to ensure database is initialized.
    """
    return app_instance.test_client()


@pytest.fixture
def db_session(app_instance):
    """
    Provide direct access to SQLAlchemy session for unit tests.

    Useful for model tests that don't go through HTTP endpoints.
    """
    return db.session
