"""
Step 6 Automated Test Suite: Escrow Holds, Fee Splitting, Vision Audit & PDF Invoicing.
Acceptance: Verify Stripe pre-authorizations, completion photo evaluation, ReportLab PDF generation, and 85/15 splits.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.stripe_service import stripe_service
from app.services.openai_service import openai_service
from app.services.pdf_service import pdf_service
from app.tasks.rewards_tasks import _perform_rewards_audit


@pytest.mark.asyncio
async def test_stripe_escrow_preauth_and_85_15_split_calculation():
    """
    Tests Stripe escrow manual pre-authorization hold and exact 85/15 fee splitting.
    """
    job_id = "f29b439c-85e7-4b77-a89e-4e432a514d31"
    customer_id = "893c5d6e-1d54-4f51-b841-3b7c858cf832"
    amount_cents = 12000  # $120.00

    # 1. Place pre-auth hold
    hold_res = await stripe_service.create_escrow_hold(
        job_id=job_id,
        customer_id=customer_id,
        amount_in_cents=amount_cents
    )
    assert hold_res["capture_method"] == "manual"
    assert hold_res["status"] == "requires_capture"
    assert hold_res["payment_intent_id"].startswith("pi_")

    # 2. Release escrow payout with 85/15 split
    payout_res = await stripe_service.release_escrow_payout(
        job_id=job_id,
        total_amount_cents=amount_cents,
        destination_stripe_account="acct_1NJ2h9K9zLm"
    )
    assert payout_res["status"] == "SETTLED"
    assert payout_res["total_captured"] == 120.00
    assert payout_res["technician_payout"] == 102.00  # 85% of $120.00
    assert payout_res["platform_service_fee"] == 18.00  # 15% of $120.00
    assert payout_res["split_ratio"] == "85/15"


@pytest.mark.asyncio
async def test_vision_completion_photo_audit():
    """Validates vision model verification of repair completion photos."""
    res = await openai_service.verify_completion_photo(
        photo_url_or_bytes="https://s3.amazonaws.com/fieldmind/repairs/proof1.jpg",
        expected_category="Plumbing"
    )
    assert res.is_verified is True
    assert res.confidence >= 0.90
    assert len(res.detected_repairs) > 0


def test_reportlab_pdf_invoice_generation():
    """Validates that ReportLab compiles a valid PDF invoice with itemized line items."""
    pdf_bytes = pdf_service.generate_invoice_pdf(
        job_id="f29b439c-85e7-4b77-a89e-4e432a514d31",
        customer_name="David Miller",
        officer_name="Marcus Vance",
        category="Plumbing",
        labor_cost=85.00,
        materials_cost=17.00,
        platform_fee=18.00
    )

    assert pdf_bytes is not None
    assert len(pdf_bytes) > 200
    assert pdf_bytes.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_celery_monthly_100_job_reward_audit(test_db: AsyncSession, seed_data):
    """
    Validates the Celery month-end task auditing workers with completed_jobs >= 100
    and rating >= 4.5, flagging them as reward_eligible = True.
    """
    # In seed_data:
    # officer1 (Marcus): 104 jobs, 4.92 rating -> Qualifies
    # officer4 (Elena): 101 jobs, 4.95 rating -> Qualifies
    # officer2 (Sarah): 89 jobs -> Not qualified
    # officer3 (Dave): 45 jobs -> Not qualified

    # Run audit function
    audit_res = await _perform_rewards_audit(session=test_db)
    assert audit_res["status"] == "COMPLETED"
    assert audit_res["qualified_count"] >= 2

    # Check Marcus in qualified officers
    qual_names = [o["full_name"] for o in audit_res["qualified_officers"]]
    assert "Marcus Vance" in qual_names
    assert "Elena Far" in qual_names
