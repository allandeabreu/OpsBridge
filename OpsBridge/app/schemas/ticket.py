from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

TicketCategory = Literal["hardware", "software", "network", "access"]
TicketPriority = Literal["low", "medium", "high", "critical"]
TicketStatus = Literal["new", "in_progress", "waiting", "resolved", "closed", "cancelled"]

class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=3, max_length=5000)
    category: TicketCategory
    priority: TicketPriority = "medium"
    requester: str = Field(min_length=2, max_length=100)

class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, min_length=3, max_length=5000)
    category: TicketCategory | None = None
    priority: TicketPriority | None = None
    status: TicketStatus | None = None
    assigned_to: str | None = Field(default=None, max_length=100)

class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    requester: str
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime

class TicketHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_id: int
    field: str
    old_value: str | None
    new_value: str | None
    changed_at: datetime

class TicketStats(BaseModel):
    total: int
    open: int
    critical: int
    new: int
    in_progress: int
    waiting: int
    resolved: int
    closed: int
    cancelled: int
