from sqlmodel import SQLModel, Field, select
from uuid import uuid4
from datetime import datetime, timezone
from passlib.context import CryptContext

from app.db import get_session
from app.env import PASSWD_HASH_ALGO

pwd_context = CryptContext([PASSWD_HASH_ALGO], deprecated="auto")


class BaseUser(SQLModel):
    username: str = Field(min_length=3, max_length=128, unique=True, index=True)


class User(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True, default_factory=lambda: str(uuid4()))
    username: str = Field(min_length=3, max_length=128, unique=True, index=True)
    hashed_password: str = Field(min_length=6)
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseUser):
    password: str = Field(min_length=6, max_length=64)

    def save(self):
        """Create User on Database."""

        hashed_pwd = pwd_context.hash(self.password)
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

        try:
            user = User(
                username=self.username, 
                hashed_password=hashed_pwd, 
                created_at=created_at, 
                updated_at=updated_at
            )
        except Exception as e: 
            raise Exception(f"Error while creating User model!\nError: {e}")

        session = next(get_session())
        session.add(user)
        session.commit()


def get_user(id: str = "", username: str = "") -> User:
    statement = select(User)

    if id:
        statement = statement.where(User.id == id)
    elif username:
        statement = statement.where(User.username == username)
    else:
        raise Exception("This function should receive an id or username!")
    
    session = next(get_session())
    results = session.exec(statement)
    user = results.first()

    if not user:
        raise Exception("Couldn't find a User for the given id or username.")
    
    return user



