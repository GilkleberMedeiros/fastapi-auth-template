from unittest import TestCase
from httpx import patch
from sqlmodel import Session
from sqlalchemy import inspect

from test.unit.base import TestWithInMemoryDB, test_engine
from app.db import get_session, init_db


class TestGetSession(TestWithInMemoryDB):
    
    def test_donot_returns_none(self):
        session = next(get_session())
        self.assertIsNotNone(session)

    def test_returns_sqlmodel_session_instance(self):
        session = next(get_session())
        self.assertIsInstance(session, Session)

@patch("app.db.engine", test_engine)
class TestInitDB(TestCase):

    def test_donot_raises_exception(self):
        try:
            init_db()
        except Exception as e:
            self.fail(f"init_db() raised an exception: {e}")

    def test_create_user_table(self):
        init_db()

        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        self.assertIn("user", tables)


    


    