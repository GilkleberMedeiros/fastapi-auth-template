from sqlmodel import select

from test.unit.base import TestWithInMemoryDB
from app.models.user import UserCreate, User
from app.db import get_session


class TestUserCreate_Save(TestWithInMemoryDB):

    def test_donot_raises_exception(self):
        user_create = UserCreate(username="testuser", password="testpassword")
        try:
            user_create.save()
        except Exception as e:
            self.fail(f"UserCreate.save() raised an exception: {e}")

    def test_saves_user_to_db(self):
        user_create = UserCreate(username="testuser", password="testpassword")
        user_create.save()

        session = next(get_session())
        result = session.exec(select(User).where(User.username == "testuser"))
        user = result.first()

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")

    def test_password_is_hashed(self):
        user_create = UserCreate(username="testuser", password="testpassword")
        user_create.save()

        session = next(get_session())
        result = session.exec(select(User).where(User.username == "testuser"))
        user = result.first()

        self.assertIsNotNone(user)
        self.assertNotEqual(user.hashed_password, "testpassword")

    def test_created_at_and_updated_at_are_set(self):
        user_create = UserCreate(username="testuser", password="testpassword")
        user_create.save()

        session = next(get_session())
        result = session.exec(select(User).where(User.username == "testuser"))
        user = result.first()

        self.assertIsNotNone(user)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

    def test_username_uniqueness(self):
        user_create1 = UserCreate(username="testuser", password="testpassword")
        user_create1.save()

        user_create2 = UserCreate(username="testuser", password="anotherpassword")
        with self.assertRaises(Exception):
            user_create2.save()

    def test_username_min_length(self): 
        with self.assertRaises(Exception):
            user_create =  UserCreate(username="ab", password="testpassword")
            user_create.save()

    def test_username_max_length(self):
        with self.assertRaises(Exception):
            user_create = UserCreate(username="a" * 129, password="testpassword")
            user_create.save()

    def test_password_min_length(self):
        with self.assertRaises(Exception):
            user_create = UserCreate(username="testuser", password="short")
            user_create.save()
