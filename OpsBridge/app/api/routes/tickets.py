from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import DatabaseSession
from app.repositories import ticket_repository as repo
from app.schemas.ticket import (
    TicketCategory, TicketCreate, TicketHistoryRead, TicketPriority,
    TicketRead, TicketStats, TicketStatus, TicketUpdate,
)
from app.services import ticket_service as service

router = APIRouter(prefix="/tickets", tags=["tickets"])

def not_found(exc: service.TicketNotFound) -> HTTPException:
    return HTTPException(status_code=404, detail=str(exc))

def conflict(exc: service.TicketConflict) -> HTTPException:
    return HTTPException(status_code=409, detail=str(exc))

@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(data: TicketCreate, db: DatabaseSession):
    return service.create_ticket(db, data)

@router.get("", response_model=list[TicketRead])
def list_tickets(
    db: DatabaseSession,
    status_filter: TicketStatus | None = Query(default=None, alias="status"),
    priority: TicketPriority | None = None,
    category: TicketCategory | None = None,
    assigned_to: str | None = None,
    q: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    return repo.list_tickets(db, status=status_filter, priority=priority,
                             category=category, assigned_to=assigned_to,
                             q=q, limit=limit, offset=offset)

@router.get("/stats", response_model=TicketStats)
def get_stats(db: DatabaseSession):
    return service.ticket_stats(db)

@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: int, db: DatabaseSession):
    try:
        return service.require_ticket(db, ticket_id)
    except service.TicketNotFound as exc:
        raise not_found(exc) from exc

@router.put("/{ticket_id}", response_model=TicketRead)
@router.patch("/{ticket_id}", response_model=TicketRead, include_in_schema=False)
def update_ticket(ticket_id: int, data: TicketUpdate, db: DatabaseSession):
    try:
        return service.update_ticket(db, ticket_id, data)
    except service.TicketNotFound as exc:
        raise not_found(exc) from exc
    except service.TicketConflict as exc:
        raise conflict(exc) from exc

@router.delete("/{ticket_id}", response_model=TicketRead)
def cancel_ticket(ticket_id: int, db: DatabaseSession):
    """Cancelamento lógico: preserva registo e histórico, não elimina a linha."""
    try:
        return service.cancel_ticket(db, ticket_id)
    except service.TicketNotFound as exc:
        raise not_found(exc) from exc
    except service.TicketConflict as exc:
        raise conflict(exc) from exc

@router.get("/{ticket_id}/history", response_model=list[TicketHistoryRead])
def ticket_history(ticket_id: int, db: DatabaseSession):
    try:
        service.require_ticket(db, ticket_id)
    except service.TicketNotFound as exc:
        raise not_found(exc) from exc
    return repo.list_history(db, ticket_id)
