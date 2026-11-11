from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.repositories import ticket_repository as repo
from app.schemas.ticket import TicketCreate, TicketUpdate

ALLOWED_TRANSITIONS = {
    "new": {"in_progress", "waiting", "resolved", "cancelled"},
    "in_progress": {"waiting", "resolved", "cancelled"},
    "waiting": {"in_progress", "resolved", "cancelled"},
    "resolved": {"in_progress", "closed"},
    "closed": set(),
    "cancelled": set(),
}

class TicketNotFound(Exception):
    pass

class TicketConflict(Exception):
    pass

def require_ticket(db: Session, ticket_id: int) -> Ticket:
    ticket = repo.get_ticket_by_id(db, ticket_id)
    if ticket is None:
        raise TicketNotFound(f"Ticket {ticket_id} não encontrado")
    return ticket

def create_ticket(db: Session, data: TicketCreate) -> Ticket:
    ticket = Ticket(**data.model_dump(), status="new")
    try:
        repo.save(db, ticket)
        repo.record_history(db, ticket_id=ticket.id, field="created", old=None, new="new")
        db.commit()
        db.refresh(ticket)
        return ticket
    except Exception:
        db.rollback()
        raise

def update_ticket(db: Session, ticket_id: int, data: TicketUpdate) -> Ticket:
    ticket = require_ticket(db, ticket_id)
    changes = data.model_dump(exclude_unset=True)
    if ticket.status in {"closed", "cancelled"} and any(
        value != getattr(ticket, name) for name, value in changes.items()
    ):
        raise TicketConflict("Tickets fechados ou cancelados não podem ser alterados")
    new_status = changes.get("status")
    if new_status is not None and new_status != ticket.status:
        if new_status not in ALLOWED_TRANSITIONS[ticket.status]:
            raise TicketConflict(f"Transição inválida: {ticket.status} → {new_status}")
    # None is allowed only to clear technician assignment, not required fields.
    for field, value in changes.items():
        if field != "assigned_to" and value is None:
            raise TicketConflict(f"O campo {field} não pode ser nulo")
    try:
        for field, value in changes.items():
            old = getattr(ticket, field)
            if old != value:
                repo.record_history(db, ticket_id=ticket.id, field=field,
                                    old=str(old) if old is not None else None,
                                    new=str(value) if value is not None else None)
                setattr(ticket, field, value)
        db.commit()
        db.refresh(ticket)
        return ticket
    except Exception:
        db.rollback()
        raise

def cancel_ticket(db: Session, ticket_id: int) -> Ticket:
    ticket = require_ticket(db, ticket_id)
    if ticket.status == "cancelled":
        return ticket
    if ticket.status == "closed" or "cancelled" not in ALLOWED_TRANSITIONS[ticket.status]:
        raise TicketConflict("Este ticket já não pode ser cancelado")
    return update_ticket(db, ticket_id, TicketUpdate(status="cancelled"))

def ticket_stats(db: Session) -> dict[str, int]:
    counts = repo.count_by_status(db)
    result = {status: counts.get(status, 0) for status in ALLOWED_TRANSITIONS}
    result["total"] = sum(counts.values())
    result["open"] = sum(counts.get(s, 0) for s in ["new", "in_progress", "waiting", "resolved"])
    result["critical"] = repo.count_critical_open(db)
    return result
