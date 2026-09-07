"""Celery task for monthly 100-job performance audit and reward qualification."""

import asyncio
from typing import Any, Dict, List
from app.tasks.celery_app import celery
from app.core.logging import logger


def run_async(coro):
    """Utility to run async DB operations inside synchronous Celery worker."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


async def _perform_rewards_audit(session=None) -> Dict[str, Any]:
    """
    Audits technicians with completed_jobs_current_month >= 100 and average_rating >= 4.5.
    Sets reward_eligible = True and records rewards.
    """
    from sqlalchemy import select, update
    from app.database.session import AsyncSessionLocal
    from app.database.models import FieldOfficer, User

    qualified_count = 0
    officer_records = []

    async def audit_logic(s):
        nonlocal qualified_count, officer_records
        stmt = (
            select(FieldOfficer, User)
            .join(User, FieldOfficer.user_id == User.id)
            .where(
                FieldOfficer.completed_jobs_current_month >= 100,
                FieldOfficer.average_rating >= 4.5
            )
        )
        result = await s.execute(stmt)
        rows = result.all()

        for officer, user in rows:
            officer.reward_eligible = True
            qualified_count += 1
            officer_records.append({
                "officer_id": str(officer.id),
                "full_name": user.full_name,
                "completed_jobs": officer.completed_jobs_current_month,
                "average_rating": float(officer.average_rating),
                "reward_eligible": True,
                "bonus_tier": "TIER_1_BONUS_QUALIFIED"
            })
            logger.info(f"Officer {user.full_name} ({officer.id}) qualified for 100-job monthly bonus with {officer.completed_jobs_current_month} jobs and {officer.average_rating} rating!")

        await s.commit()

    if session:
        await audit_logic(session)
    else:
        async with AsyncSessionLocal() as s:
            await audit_logic(s)

    logger.info(f"Monthly Rewards Audit Completed: {qualified_count} officers qualified.")
    return {
        "status": "COMPLETED",
        "qualified_count": qualified_count,
        "qualified_officers": officer_records
    }


@celery.task(name="app.tasks.rewards_tasks.audit_monthly_technician_rewards")
def audit_monthly_technician_rewards() -> Dict[str, Any]:
    """Celery entrypoint for monthly rewards audit."""
    logger.info("Executing Celery task: audit_monthly_technician_rewards")
    return run_async(_perform_rewards_audit())
