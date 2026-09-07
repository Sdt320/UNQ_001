"""Gamification, reviews & leaderboard engine (/api/v1/rewards)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.database.models import FieldOfficer, User, CustomerReview, ServiceRequest
from app.core.logging import logger

router = APIRouter(prefix="/rewards", tags=["Gamification, Reviews & Leaderboard"])


class LeaderboardEntry(BaseModel):
    officer_id: str
    officer_name: str
    completed_jobs_current_month: int
    average_rating: float
    reward_eligible: bool
    bonus_tier: str


class CreateReviewPayload(BaseModel):
    job_id: str
    customer_id: str
    officer_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: str
    job_id: str
    customer_name: str
    officer_id: str
    rating: int
    comment: Optional[str]
    created_at: str


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_rewards_leaderboard(db: AsyncSession = Depends(get_db)):
    """
    Returns monthly rankings of top-performing field officers and 100-job bonus eligibility.
    """
    stmt = (
        select(FieldOfficer, User)
        .join(User, FieldOfficer.user_id == User.id)
        .order_by(FieldOfficer.completed_jobs_current_month.desc(), FieldOfficer.average_rating.desc())
        .limit(50)
    )
    res = await db.execute(stmt)
    rows = res.all()

    leaderboard = []
    for officer, user in rows:
        bonus_tier = "TIER_1_BONUS_QUALIFIED" if officer.reward_eligible else "IN_PROGRESS"
        leaderboard.append(LeaderboardEntry(
            officer_id=str(officer.id),
            officer_name=user.full_name,
            completed_jobs_current_month=officer.completed_jobs_current_month,
            average_rating=float(officer.average_rating),
            reward_eligible=officer.reward_eligible,
            bonus_tier=bonus_tier
        ))

    # If DB is empty, provide baseline benchmark seed for UI demo
    if not leaderboard:
        leaderboard = [
            LeaderboardEntry(
                officer_id="a5c7602b-bf27-4a0b-967b-2e9eb5c4c9e8",
                officer_name="Marcus Vance",
                completed_jobs_current_month=104,
                average_rating=4.92,
                reward_eligible=True,
                bonus_tier="TIER_1_BONUS_QUALIFIED"
            ),
            LeaderboardEntry(
                officer_id="b8d8713c-cf38-5b1c-078c-3f0fc6d5d0f9",
                officer_name="Elena Rostova",
                completed_jobs_current_month=101,
                average_rating=4.88,
                reward_eligible=True,
                bonus_tier="TIER_1_BONUS_QUALIFIED"
            ),
            LeaderboardEntry(
                officer_id="c9e9824d-da49-6c2d-189d-4a1ad7e6e1aa",
                officer_name="Sarah Connor",
                completed_jobs_current_month=89,
                average_rating=4.80,
                reward_eligible=False,
                bonus_tier="IN_PROGRESS"
            ),
            LeaderboardEntry(
                officer_id="d0f0935e-eb50-7d3e-290e-5b2be8f7f2bb",
                officer_name="Dave Miller",
                completed_jobs_current_month=76,
                average_rating=4.65,
                reward_eligible=False,
                bonus_tier="IN_PROGRESS"
            )
        ]

    return leaderboard


@router.post("/reviews", status_code=status.HTTP_201_CREATED)
async def submit_customer_review(payload: CreateReviewPayload, db: AsyncSession = Depends(get_db)):
    """Submits customer rating and comment, recomputing officer average score."""
    review = CustomerReview(
        job_id=payload.job_id,
        customer_id=payload.customer_id,
        officer_id=payload.officer_id,
        rating=payload.rating,
        comment=payload.comment
    )
    db.add(review)
    await db.commit()

    # Recalculate average rating
    stmt = select(func.avg(CustomerReview.rating)).where(CustomerReview.officer_id == payload.officer_id)
    res = await db.execute(stmt)
    avg_rating = res.scalar() or payload.rating

    officer_stmt = select(FieldOfficer).where(FieldOfficer.id == payload.officer_id)
    off_res = await db.execute(officer_stmt)
    officer = off_res.scalar_one_or_none()
    if officer:
        officer.average_rating = round(float(avg_rating), 2)
        officer.completed_jobs_current_month += 1
        await db.commit()

    return {"status": "SUCCESS", "average_rating": round(float(avg_rating), 2)}


@router.get("/reviews", response_model=List[ReviewResponse])
async def list_recent_reviews(db: AsyncSession = Depends(get_db)):
    """Lists recent customer reviews."""
    stmt = (
        select(CustomerReview, User)
        .join(User, CustomerReview.customer_id == User.id)
        .order_by(CustomerReview.created_at.desc())
        .limit(20)
    )
    res = await db.execute(stmt)
    rows = res.all()

    reviews = []
    for rev, user in rows:
        reviews.append(ReviewResponse(
            id=str(rev.id),
            job_id=str(rev.job_id),
            customer_name=user.full_name,
            officer_id=str(rev.officer_id),
            rating=rev.rating,
            comment=rev.comment,
            created_at=rev.created_at.isoformat()
        ))

    if not reviews:
        reviews = [
            ReviewResponse(
                id="rev-01",
                job_id="job-893c5d6e",
                customer_name="David Miller",
                officer_id="a5c7602b",
                rating=5,
                comment="Arrived within 12 minutes! Fixed the burst bathroom copper pipe and tested pressure.",
                created_at="2026-09-08T00:15:00Z"
            ),
            ReviewResponse(
                id="rev-02",
                job_id="job-782b4c5d",
                customer_name="Jessica Hayes",
                officer_id="b8d8713c",
                rating=5,
                comment="Replaced tripping circuit breaker cleanly. Official PDF invoice arrived immediately.",
                created_at="2026-09-07T22:30:00Z"
            )
        ]

    return reviews
