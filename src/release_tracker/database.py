from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from .config import get_settings


@lru_cache  # guarantees the engine you get is always the same engine
def get_engine() -> Engine:
    # first call builds the engine, calls after returns same engine
    return create_engine(get_settings().database_url)


# get db engine, and get me back a session
def get_session() -> Generator[Session]:
    with Session(get_engine()) as session:
        yield session
