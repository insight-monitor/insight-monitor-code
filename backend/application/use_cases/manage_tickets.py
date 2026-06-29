"""
Use Case — Manage Tickets
Encapsulates business logic for ticket CRUD and comments.
Routes depend on this use case, not on repositories directly.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from backend.domain.ports.repositories import (
    ITicketRepository,
    ICommentRepository,
)


VALID_STATUSES = {"open", "in_progress", "resolved", "closed"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}


class TicketValidationError(ValueError):
    """Raised when ticket data fails validation."""


class ManageTicketsUseCase:
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        comment_repo: ICommentRepository,
    ):
        self.ticket_repo = ticket_repo
        self.comment_repo = comment_repo

    def list_tickets(
        self, status: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> dict[str, Any]:
        if status is not None:
            self._validate_status(status)
        tickets = self.ticket_repo.find_all(status=status, limit=limit, offset=offset)
        total = self.ticket_repo.count_all(status=status)
        return {
            "tickets": tickets,
            "count": total,
            "limit": limit,
            "offset": offset,
        }

    def create_ticket(self, ticket: dict[str, Any]) -> dict[str, Any]:
        self._validate_priority(ticket.get("priority", "medium"))
        now = datetime.now(timezone.utc).isoformat()
        ticket_id = str(uuid.uuid4())
        record = {
            "id": ticket_id,
            "title": ticket["title"],
            "description": ticket.get("description", ""),
            "status": "open",
            "priority": ticket.get("priority", "medium"),
            "created_by": ticket.get("created_by", "system"),
            "created_at": now,
            "updated_at": now,
        }
        self.ticket_repo.create(record)
        return self.ticket_repo.find_by_id(ticket_id) or record

    def get_stats(self) -> dict[str, int]:
        return self.ticket_repo.stat_counts()

    def get_ticket(self, ticket_id: str) -> Optional[dict[str, Any]]:
        ticket = self.ticket_repo.find_by_id(ticket_id)
        if ticket is None:
            return None
        ticket["comments"] = self.comment_repo.find_by_ticket(ticket_id)
        return ticket

    def update_ticket(self, ticket_id: str, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        existing = self.ticket_repo.find_by_id(ticket_id)
        if not existing:
            return None
        if updates.get("status") is not None:
            self._validate_status(updates["status"])
        if updates.get("priority") is not None:
            self._validate_priority(updates["priority"])
        applied = {k: v for k, v in updates.items() if v is not None}
        if applied:
            applied["updated_at"] = datetime.now(timezone.utc).isoformat()
            self.ticket_repo.update(ticket_id, applied)
        return self.ticket_repo.find_by_id(ticket_id)

    def delete_ticket(self, ticket_id: str) -> bool:
        existing = self.ticket_repo.find_by_id(ticket_id)
        if not existing:
            return False
        self.ticket_repo.delete(ticket_id)
        return True

    def add_comment(
        self, ticket_id: str, content: str, author: str = "system"
    ) -> Optional[dict[str, Any]]:
        existing = self.ticket_repo.find_by_id(ticket_id)
        if not existing:
            return None
        comment_id = str(uuid.uuid4())
        record = {
            "id": comment_id,
            "ticket_id": ticket_id,
            "content": content,
            "author": author,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.comment_repo.create(record)
        return self.comment_repo.find_by_id(comment_id)

    @staticmethod
    def _validate_priority(priority: str) -> None:
        if priority not in VALID_PRIORITIES:
            raise TicketValidationError(f"Invalid priority: {priority}")

    @staticmethod
    def _validate_status(status: str) -> None:
        if status not in VALID_STATUSES:
            raise TicketValidationError(f"Invalid status: {status}")
