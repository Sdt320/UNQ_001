"""
Step 5 Automated Test Suite: Concurrency Locking & WhatsApp Webhook Race Conditions.
Acceptance: Run 50 concurrent simulated acceptance requests to verify that only one claim succeeds.
"""

import asyncio
import pytest
import uuid
from app.services.redis_lock_service import RedisLockService, redis_lock_service
from app.api.webhooks.whatsapp import verify_whatsapp_webhook
from fastapi import Response


@pytest.mark.asyncio
async def test_redis_mutex_50_concurrent_claims_single_winner():
    """
    Simulates 50 field technicians simultaneously clicking 'ACCEPT' on WhatsApp
    within milliseconds of each other.
    Validates that:
    1. Exactly 1 technician acquires the atomic mutex lock.
    2. Exactly 49 technicians fail the atomic check (HTTP 409 / Rejection).
    3. No double-bookings occur under race condition load.
    """
    job_id = f"job-race-{uuid.uuid4().hex[:8]}"
    service = RedisLockService()  # Clean lock instance

    async def attempt_claim(officer_index: int):
        officer_id = f"officer-pro-{officer_index:03d}"
        # Slight jitter to simulate distributed network latency
        await asyncio.sleep(0.001 * (officer_index % 5))
        won = await service.acquire_job_claim_lock(
            job_id=job_id,
            officer_id=officer_id,
            ttl_seconds=15
        )
        return {"officer_id": officer_id, "won": won}

    # Launch 50 simultaneous tasks
    tasks = [attempt_claim(i) for i in range(50)]
    results = await asyncio.gather(*tasks)

    winners = [r for r in results if r["won"] is True]
    losers = [r for r in results if r["won"] is False]

    assert len(winners) == 1, f"Expected exactly 1 winner, but found {len(winners)}"
    assert len(losers) == 49, f"Expected exactly 49 rejected claims, but found {len(losers)}"

    # Check lock holder matches the single winner
    lock_holder = await service.get_lock_holder(job_id)
    assert lock_holder == winners[0]["officer_id"]


@pytest.mark.asyncio
async def test_whatsapp_webhook_verification_handshake():
    """
    Validates Meta Cloud API challenge handshake verification.
    """
    challenge_code = "1158201444"
    response: Response = await verify_whatsapp_webhook(
        hub_mode="subscribe",
        hub_challenge=challenge_code,
        hub_verify_token="FIELDMIND_SECURE_TOKEN_2026"
    )

    assert response.status_code == 200
    assert response.body.decode() == challenge_code
