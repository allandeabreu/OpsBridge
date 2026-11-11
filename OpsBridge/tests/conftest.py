import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.deps import DatabaseSession  # noqa: F401 (documented dependency)
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.history import TicketHistory  # noqa: F401
from app.models.ticket import Ticket  # noqa: F401

@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)

    def db_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    engine.dispose()
