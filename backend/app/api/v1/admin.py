"""Technician approval and governance engine (/api/v1/admin)."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role, TokenPayload
from app.database.session import get_db
from app.database.models import User, FieldOfficer, UserRole
from app.core.logging import logger

router = APIRouter(prefix="/admin", tags=["Admin Operations Console"])


class PendingWorkerResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    phone_number: str
    skills: List[str]
    license_doc_url: str | None = None
    created_at: str
    latitude: float
    longitude: float


class ApproveWorkerResponse(BaseModel):
    status: str
    user_id: str
    is_approved: bool
    message: str


@router.get("/pending-workers", response_model=List[PendingWorkerResponse])
async def get_pending_workers(
    token_payload: TokenPayload = Depends(require_role(["ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """Returns all field technicians awaiting admin license verification and approval."""
    stmt = (
        select(User, FieldOfficer)
        .join(FieldOfficer, User.id == FieldOfficer.user_id)
        .where(User.role == UserRole.EMPLOYEE, User.is_approved == False)
        .order_by(User.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    pending_list = []
    for user, officer in rows:
        pending_list.append(PendingWorkerResponse(
            user_id=str(user.id),
            full_name=user.full_name,
            email=user.email,
            phone_number=user.phone_number,
            skills=officer.skills if isinstance(officer.skills, list) else [],
            license_doc_url=officer.license_doc_url,
            created_at=user.created_at.isoformat(),
            latitude=officer.latitude,
            longitude=officer.longitude
        ))

    return pending_list


@router.patch("/approve-worker/{user_id}", response_model=ApproveWorkerResponse)
async def approve_worker(
    user_id: str,
    token_payload: TokenPayload = Depends(require_role(["ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """Grants administrative approval for a field technician, enabling them for spatial dispatch."""
    stmt = select(User).where(User.id == user_id, User.role == UserRole.EMPLOYEE)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Technician not found")

    user.is_approved = True
    await db.commit()
    logger.info(f"Admin approved technician: {user.full_name} ({user_id})")

    return ApproveWorkerResponse(
        status="APPROVED",
        user_id=str(user.id),
        is_approved=True,
        message="Field technician approved for service dispatch."
    )
