from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.domain.entities.ticket import (
    TicketCreate,
    TicketUpdate,
    CommentCreate,
)
from backend.infrastructure.di import get_db
from backend.infrastructure.db.sqlite.database import Database

router = APIRouter(prefix="/tickets", tags=["tickets"])

VALID_STATUSES = {"open", "in_progress", "resolved", "closed"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}


def _validate_priority(priority: str) -> str:
    if priority not in VALID_PRIORITIES:
        raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")
    return priority


def _validate_status(status: str) -> str:
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    return status


@router.get("")
async def list_tickets(
    status: str | None = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Database = Depends(get_db),
):
    if status:
        rows = db.fetch_all(
            "SELECT * FROM tickets WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (status, limit, offset),
        )
        total = db.fetch_one(
            "SELECT COUNT(*) as cnt FROM tickets WHERE status = ?", (status,)
        )
    else:
        rows = db.fetch_all(
            "SELECT * FROM tickets ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        total = db.fetch_one("SELECT COUNT(*) as cnt FROM tickets")

    return {
        "tickets": rows,
        "count": total["cnt"] if total else 0,
        "limit": limit,
        "offset": offset,
    }


@router.post("")
async def create_ticket(
    ticket: TicketCreate,
    db: Database = Depends(get_db),
):
    _validate_priority(ticket.priority)
    ticket_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    db.execute(
        """INSERT INTO tickets (id, title, description, status, priority, created_by, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (ticket_id, ticket.title, ticket.description, "open", ticket.priority, ticket.created_by, now, now),
    )
    db.commit()

    row = db.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    return row


@router.get("/stats")
async def get_ticket_stats(
    db: Database = Depends(get_db),
):
    row = db.fetch_one("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open,
            SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed
        FROM tickets
    """)
    return dict(row) if row else {"total": 0, "open": 0, "in_progress": 0, "resolved": 0, "closed": 0}


@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: str,
    db: Database = Depends(get_db),
):
    row = db.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")

    comments = db.fetch_all(
        "SELECT * FROM ticket_comments WHERE ticket_id = ? ORDER BY created_at ASC",
        (ticket_id,),
    )
    row["comments"] = comments
    return row


@router.put("/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    updates: TicketUpdate,
    db: Database = Depends(get_db),
):
    row = db.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")

    fields = {}
    if updates.title is not None:
        fields["title"] = updates.title
    if updates.description is not None:
        fields["description"] = updates.description
    if updates.status is not None:
        _validate_status(updates.status)
        fields["status"] = updates.status
    if updates.priority is not None:
        _validate_priority(updates.priority)
        fields["priority"] = updates.priority

    if fields:
        fields["updated_at"] = datetime.now(timezone.utc).isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [ticket_id]
        db.execute(f"UPDATE tickets SET {set_clause} WHERE id = ?", tuple(values))
        db.commit()

    row = db.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    return row


@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    db: Database = Depends(get_db),
):
    row = db.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.execute("DELETE FROM ticket_comments WHERE ticket_id = ?", (ticket_id,))
    db.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    db.commit()
    return {"status": "deleted", "ticket_id": ticket_id}


@router.post("/{ticket_id}/comments")
async def add_comment(
    ticket_id: str,
    comment: CommentCreate,
    db: Database = Depends(get_db),
):
    row = db.fetch_one("SELECT id FROM tickets WHERE id = ?", (ticket_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")

    comment_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    db.execute(
        """INSERT INTO ticket_comments (id, ticket_id, content, author, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (comment_id, ticket_id, comment.content, comment.author, now),
    )
    db.commit()

    row = db.fetch_one("SELECT * FROM ticket_comments WHERE id = ?", (comment_id,))
    return row
