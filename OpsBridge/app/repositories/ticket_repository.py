from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.history import TicketHistory
from app.models.ticket import Ticket

def get_ticket_by_id(db: Session, ticket_id: int) -> Ticket | None:
    return db.get(Ticket, ticket_id)

def list_tickets(
    db: Session, *, status: str | None = None, priority: str | None = None,
    category: str | None = None, assigned_to: str | None = None,
    q: str | None = None, limit: int = 100, offset: int = 0,
) -> list[Ticket]:
    stmt = select(Ticket)
    if status:
        stmt = stmt.where(Ticket.status == status)
    if priority:
        stmt = stmt.where(Ticket.priority == priority)
    if category:
        stmt = stmt.where(Ticket.category == category)
    if assigned_to:
        stmt = stmt.where(Ticket.assigned_to.ilike(f"%{assigned_to}%"))
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(Ticket.title.ilike(pattern) | Ticket.description.ilike(pattern) | Ticket.requester.ilike(pattern))
    stmt = stmt.order_by(Ticket.created_at.desc(), Ticket.id.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())

def save(db: Session, ticket: Ticket) -> Ticket:
    db.add(ticket)
    db.flush()
    return ticket

def record_history(db: Session, *, ticket_id: int, field: str, old: str | None, new: str | None) -> None:
    db.add(TicketHistory(ticket_id=ticket_id, field=field, old_value=old, new_value=new))

def list_history(db: Session, ticket_id: int) -> list[TicketHistory]:
    return list(db.scalars(
        select(TicketHistory).where(TicketHistory.ticket_id == ticket_id)
        .order_by(TicketHistory.changed_at.desc(), TicketHistory.id.desc())
    ).all())

def count_by_status(db: Session) -> dict[str, int]:
    result = db.execute(select(Ticket.status, func.count()).group_by(Ticket.status)).all()
    return {status: count for status, count in result}

def count_critical_open(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Ticket).where(
        Ticket.priority == "critical", Ticket.status.notin_(["closed", "cancelled"])
    )) or 0
