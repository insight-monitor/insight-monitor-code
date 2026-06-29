from fastapi import APIRouter, Depends, HTTPException, Query

from backend.application.use_cases.manage_tickets import (
    ManageTicketsUseCase,
    TicketValidationError,
)
from backend.domain.entities.ticket import (
    TicketCreate,
    TicketUpdate,
    CommentCreate,
)
from backend.infrastructure.di import get_manage_tickets_use_case

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("")
async def list_tickets(
    status: str | None = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    use_case: ManageTicketsUseCase = Depends(get_manage_tickets_use_case),
):
    try:
        return use_case.list_tickets(status=status, limit=limit, offset=offset)
    except TicketValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("")
async def create_ticket(
    ticket: TicketCreate,
    use_case: ManageTicketsUseCase = Depends(get_manage_tickets_use_case),
):
    try:
        return use_case.create_ticket(ticket.model_dump())
    except TicketValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
async def get_ticket_stats(
    use_case: ManageTicketsUseCase = Depends(get_manage_tickets_use_case),
):
    return use_case.get_stats()


@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: str,
    use_case: ManageTicketsUseCase = Depends(get_manage_tickets_use_case),
):
    ticket = use_case.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    updates: TicketUpdate,
    use_case: ManageTicketsUseCase = Depends(get_manage_tickets_use_case),
):
    try:
        ticket = use_case.update_ticket(ticket_id, updates.model_dump())
    except TicketValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    use_case: ManageTicketsUseCase = Depends(get_manage_tickets_use_case),
):
    deleted = use_case.delete_ticket(ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"status": "deleted", "ticket_id": ticket_id}


@router.post("/{ticket_id}/comments")
async def add_comment(
    ticket_id: str,
    comment: CommentCreate,
    use_case: ManageTicketsUseCase = Depends(get_manage_tickets_use_case),
):
    created = use_case.add_comment(ticket_id, comment.content, comment.author)
    if not created:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return created
