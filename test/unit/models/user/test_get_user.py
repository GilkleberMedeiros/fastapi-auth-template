from sqlmodel import select

from test.unit.base import TestWithInMemoryDB
from app.models.user import get_user, User, UserCreate
from app.db import get_session


class TestGetUser(TestWithInMemoryDB):
    def setUp(self):
        """Populate the database with a user for testing."""
        super().setUp()

        # Create a user to test retrieval
        UserCreate(username="testuser", password="testpassword").save()

        session = next(get_session())
        statetement = select(User).where(User.username == "testuser")
        self.user1 = session.exec(statetement).first()

    def test_donot_raises_exception_when_getting_user_by_id(self):
        try:
            get_user(id=self.user1.id)
        except Exception as e:
            self.fail(f"get_user() raised an exception: {e}")

    def test_donot_raises_exception_when_getting_user_by_username(self):
        try:
            get_user(username="testuser")
        except Exception as e:
            self.fail(f"get_user() raised an exception: {e}")

    def test_raises_exception_if_no_user_found_by_username(self):

        with self.assertRaises(Exception) as _:
            _ = get_user(username="nonexistent")

    def test_raises_exception_if_no_user_found_by_id(self):
        with self.assertRaises(Exception) as _:
            _ = get_user(id="nonexistent-id")

    def test_returns_user_by_username(self):
        result = get_user(username="testuser")
        self.assertIsNotNone(result)
        self.assertEqual(result.username, "testuser")

    def test_returns_user_by_id(self):
        result = get_user(id=self.user1.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.user1.id)
