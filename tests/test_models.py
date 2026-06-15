"""
Unit tests for the Session database model.

Tests cover:
- Model creation and field types
- Primary key auto-increment behavior
- Optional field handling
- Field constraints and validation
- Query operations by date, type, and other criteria
"""

import pytest
from datetime import date, time
from app import app, db, Session


class TestSessionModelCreation:
    """Tests for creating Session model instances."""

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

    def test_create_session_with_required_fields_only(self):
        """Test creating Session with only required fields (date, title, type)."""
        # Arrange
        test_date = date(2026, 6, 12)
        test_title = 'Team Meeting'
        test_type = 'event'

        with app.app_context():
            # Act
            session = Session(
                date=test_date,
                title=test_title,
                type=test_type
            )
            db.session.add(session)
            db.session.commit()

            # Assert
            fetched = Session.query.first()
            assert fetched is not None
            assert fetched.date == test_date
            assert fetched.title == test_title
            assert fetched.type == test_type

    def test_create_session_with_all_fields(self):
        """Test creating Session with all fields populated."""
        # Arrange
        test_date = date(2026, 6, 12)
        test_title = 'Complete Meeting'
        test_type = 'event'
        test_start = time(14, 30)
        test_end = time(15, 30)
        test_desc = 'This is a detailed meeting description'

        with app.app_context():
            # Act
            session = Session(
                date=test_date,
                title=test_title,
                type=test_type,
                start_time=test_start,
                end_time=test_end,
                description=test_desc
            )
            db.session.add(session)
            db.session.commit()

            # Assert
            fetched = Session.query.first()
            assert fetched.date == test_date
            assert fetched.title == test_title
            assert fetched.type == test_type
            assert fetched.start_time == test_start
            assert fetched.end_time == test_end
            assert fetched.description == test_desc

    def test_session_optional_fields_are_none_by_default(self):
        """Test that optional fields default to None when not provided."""
        with app.app_context():
            # Act
            session = Session(
                date=date(2026, 6, 12),
                title='Minimal',
                type='task'
            )
            db.session.add(session)
            db.session.commit()

            # Assert
            fetched = Session.query.first()
            assert fetched.start_time is None
            assert fetched.end_time is None
            assert fetched.description is None

    def test_session_id_auto_increment(self):
        """Test that Session ID auto-increments starting from 1."""
        with app.app_context():
            # Act
            ids = []
            for i in range(5):
                session = Session(
                    date=date(2026, 6, 12),
                    title=f'Session {i}',
                    type='event'
                )
                db.session.add(session)
                db.session.commit()
                ids.append(session.id)

            # Assert
            assert ids == [1, 2, 3, 4, 5]

    def test_session_with_unicode_characters(self):
        """Test creating Session with unicode characters in title and description."""
        with app.app_context():
            # Act
            session = Session(
                date=date(2026, 6, 12),
                title='Встреча 会議 ミーティング',
                type='event',
                description='Notes: 你好 こんにちは مرحبا'
            )
            db.session.add(session)
            db.session.commit()

            # Assert
            fetched = Session.query.first()
            assert 'Встреча' in fetched.title
            assert '你好' in fetched.description


class TestSessionModelFields:
    """Tests for Session model field types and constraints."""

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

    def test_session_date_field_is_date_type(self):
        """Test that date field correctly stores date objects."""
        with app.app_context():
            # Act
            test_date = date(2026, 12, 31)
            session = Session(
                date=test_date,
                title='Year End',
                type='event'
            )
            db.session.add(session)
            db.session.commit()

            # Assert
            fetched = Session.query.first()
            assert isinstance(fetched.date, date)
            assert fetched.date == test_date

    def test_session_time_fields_are_time_type(self):
        """Test that start_time and end_time fields correctly store time objects."""
        with app.app_context():
            # Act
            test_start = time(9, 30, 45)
            test_end = time(17, 15, 30)
            session = Session(
                date=date(2026, 6, 12),
                title='Precise Times',
                type='event',
                start_time=test_start,
                end_time=test_end
            )
            db.session.add(session)
            db.session.commit()

            # Assert
            fetched = Session.query.first()
            assert isinstance(fetched.start_time, time)
            assert isinstance(fetched.end_time, time)
            assert fetched.start_time == test_start
            assert fetched.end_time == test_end

    def test_session_title_stored_as_string(self):
        """Test that title field is stored and retrieved as string."""
        with app.app_context():
            # Act
            long_title = 'A' * 255  # Max length
            session = Session(
                date=date(2026, 6, 12),
                title=long_title,
                type='event'
            )
            db.session.add(session)
            db.session.commit()

            # Assert
            fetched = Session.query.first()
            assert isinstance(fetched.title, str)
            assert len(fetched.title) == 255

    def test_session_type_field_stores_string_values(self):
        """Test that type field correctly stores string values."""
        with app.app_context():
            # Act
            for session_type in ['event', 'task', 'reminder']:
                session = Session(
                    date=date(2026, 6, 12),
                    title=session_type,
                    type=session_type
                )
                db.session.add(session)
            db.session.commit()

            # Assert
            events = Session.query.filter_by(type='event').all()
            tasks = Session.query.filter_by(type='task').all()
            reminders = Session.query.filter_by(type='reminder').all()
            assert len(events) == 1
            assert len(tasks) == 1
            assert len(reminders) == 1

    def test_session_description_field_stores_long_text(self):
        """Test that description field can store large text content."""
        with app.app_context():
            # Act
            long_desc = 'X' * 10000
            session = Session(
                date=date(2026, 6, 12),
                title='Long Description',
                type='event',
                description=long_desc
            )
            db.session.add(session)
            db.session.commit()

            # Assert
            fetched = Session.query.first()
            assert len(fetched.description) == 10000


class TestSessionModelQueries:
    """Tests for Session model query operations."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize test database with sample data for each test."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()

            # Populate with test data
            for day in range(10, 15):
                for session_type in ['event', 'task']:
                    session = Session(
                        date=date(2026, 6, day),
                        title=f'{session_type} on {day}th',
                        type=session_type
                    )
                    db.session.add(session)
            db.session.commit()
            yield
            db.session.remove()
            db.drop_all()

    def test_query_sessions_by_date(self):
        """Test querying sessions filtered by specific date."""
        with app.app_context():
            # Act
            sessions = Session.query.filter_by(date=date(2026, 6, 12)).all()

            # Assert
            assert len(sessions) == 2  # event and task on 12th
            assert all(s.date == date(2026, 6, 12) for s in sessions)

    def test_query_sessions_by_type(self):
        """Test querying sessions filtered by type."""
        with app.app_context():
            # Act
            events = Session.query.filter_by(type='event').all()

            # Assert
            assert len(events) == 5  # One event for each day (10-14)
            assert all(s.type == 'event' for s in events)

    def test_query_sessions_by_date_and_type(self):
        """Test querying sessions with multiple filter criteria."""
        with app.app_context():
            # Act
            sessions = Session.query.filter_by(
                date=date(2026, 6, 12),
                type='task'
            ).all()

            # Assert
            assert len(sessions) == 1
            assert sessions[0].title == 'task on 12th'

    def test_query_all_sessions(self):
        """Test querying all sessions without filters."""
        with app.app_context():
            # Act
            sessions = Session.query.all()

            # Assert
            assert len(sessions) == 10  # 5 days * 2 types

    def test_query_sessions_returns_empty_for_nonexistent_date(self):
        """Test that querying non-existent date returns empty list."""
        with app.app_context():
            # Act
            sessions = Session.query.filter_by(date=date(2026, 7, 1)).all()

            # Assert
            assert sessions == []

    def test_query_sessions_returns_empty_for_invalid_type(self):
        """Test that querying invalid type returns empty list."""
        with app.app_context():
            # Act
            sessions = Session.query.filter_by(type='invalid_type').all()

            # Assert
            assert sessions == []

    def test_query_session_by_id(self):
        """Test querying session by primary key."""
        with app.app_context():
            # Arrange - get first session's ID
            first_session = Session.query.first()
            session_id = first_session.id

            # Act
            fetched = Session.query.filter_by(id=session_id).first()

            # Assert
            assert fetched is not None
            assert fetched.id == session_id


class TestSessionModelUpdates:
    """Tests for updating Session model instances."""

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

    def test_update_session_title(self):
        """Test updating a session's title."""
        with app.app_context():
            # Arrange
            session = Session(
                date=date(2026, 6, 12),
                title='Original Title',
                type='event'
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id

            # Act
            session.title = 'Updated Title'
            db.session.commit()

            # Assert
            fetched = Session.query.filter_by(id=session_id).first()
            assert fetched.title == 'Updated Title'

    def test_update_session_optional_fields(self):
        """Test updating optional fields on existing session."""
        with app.app_context():
            # Arrange
            session = Session(
                date=date(2026, 6, 12),
                title='Partial',
                type='task'
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id

            # Act
            session.start_time = time(10, 0)
            session.end_time = time(11, 0)
            session.description = 'Now with times and description'
            db.session.commit()

            # Assert
            fetched = Session.query.filter_by(id=session_id).first()
            assert fetched.start_time == time(10, 0)
            assert fetched.end_time == time(11, 0)
            assert fetched.description == 'Now with times and description'

    def test_update_session_type(self):
        """Test updating session type field."""
        with app.app_context():
            # Arrange
            session = Session(
                date=date(2026, 6, 12),
                title='Changeable',
                type='event'
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id

            # Act
            session.type = 'task'
            db.session.commit()

            # Assert
            fetched = Session.query.filter_by(id=session_id).first()
            assert fetched.type == 'task'


class TestSessionModelDeletion:
    """Tests for deleting Session model instances."""

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

    def test_delete_single_session(self):
        """Test deleting a single session from database."""
        with app.app_context():
            # Arrange
            session = Session(
                date=date(2026, 6, 12),
                title='To Delete',
                type='event'
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id

            # Act
            session_to_delete = Session.query.filter_by(id=session_id).first()
            db.session.delete(session_to_delete)
            db.session.commit()

            # Assert
            fetched = Session.query.filter_by(id=session_id).first()
            assert fetched is None

    def test_delete_preserves_other_sessions(self):
        """Test that deleting one session doesn't affect others."""
        with app.app_context():
            # Arrange
            sessions = [
                Session(date=date(2026, 6, 12), title='Keep 1', type='event'),
                Session(date=date(2026, 6, 12), title='Delete', type='task'),
                Session(date=date(2026, 6, 12), title='Keep 2', type='reminder')
            ]
            for s in sessions:
                db.session.add(s)
            db.session.commit()
            delete_id = sessions[1].id

            # Act
            session_to_delete = Session.query.filter_by(id=delete_id).first()
            db.session.delete(session_to_delete)
            db.session.commit()

            # Assert
            remaining = Session.query.all()
            assert len(remaining) == 2
            assert all(s.id != delete_id for s in remaining)
