"""
    Base Test Classes with common utilities for testing the application.
"""
from unittest import TestCase
from unittest.mock import patch
from sqlmodel import SQLModel

from app.db import test_engine, get_session
from app.models import *



class TestWithInMemoryDB(TestCase):
    """
    Base Test Class for tests that need an in-memory SQLite database.  
    Auto manage the test DB lifecycle, creating the schema before all tests and clearing data before each test.
    """

    @classmethod
    def setUpClass(cls):
        """Set up the in-memory database before all tests."""
        # Import models to register them
        from app.models import user
        # Create all tables on test_engine
        SQLModel.metadata.create_all(test_engine)
        # Patch the engine globally for all tests in this class
        cls.patcher = patch("app.db.engine", test_engine)
        cls.patcher.start()
        cls.engine = test_engine
    
    @classmethod
    def tearDownClass(cls):
        """Stop patching after all tests."""
        cls.patcher.stop()

        from app.models import user

        # Drop all tables to clean up the in-memory database
        SQLModel.metadata.drop_all(cls.engine)
        cls.engine = None
    
    def setUp(self):
        """Clear database before each test."""
        session = next(get_session())

        for table in reversed(SQLModel.metadata.sorted_tables):
            try:
                session.exec(table.delete())
            except Exception:
                pass
        session.commit()
