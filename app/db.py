from sqlmodel import Session, create_engine, SQLModel 
from typing import Generator

from app.env import DB_HOST, DEBUG


# Create database engine once and reuse it! Echo set to True for SQL query logging
engine = create_engine(DB_HOST, echo=DEBUG)

def get_session() -> Generator[Session, any, None]: 
    """Create DB Session Automanaging it.""" 
    with Session(engine) as session:
        yield session

def init_db():
    """Init Database Structure! Import models to register them."""
    from app.models import user

    SQLModel.metadata.create_all(engine)

# For testing purposes, we can create an in-memory SQLite database engine
test_engine = create_engine("sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False})