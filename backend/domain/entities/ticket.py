
from pydantic import BaseModel


class TicketCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"
    created_by: str = "system"


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None


class CommentCreate(BaseModel):
    content: str
    author: str = "system"


class TicketResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    created_by: str
    created_at: str
    updated_at: str


class CommentResponse(BaseModel):
    id: str
    ticket_id: str
    content: str
    author: str
    created_at: str


class TicketStats(BaseModel):
    total: int
    open: int
    in_progress: int
    resolved: int
    closed: int
