from app.db.base import Base
from app.db.session import engine
from app.models.ticket import Ticket  # noqa: F401: register table
from app.models.history import TicketHistory  # noqa: F401: register table

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
