"""Escrow settlement, billing & invoicing engine (/api/v1/payments)."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.services.stripe_service import stripe_service
from app.services.pdf_service import pdf_service
from app.core.logging import logger

router = APIRouter(prefix="/payments", tags=["Escrow Payments & Settlements"])


class EscrowHoldPayload(BaseModel):
    job_id: str
    customer_id: str
    amount_in_cents: int = 12000


class EscrowHoldResponse(BaseModel):
    payment_intent_id: str
    status: str
    capture_method: str


class ReleasePayoutPayload(BaseModel):
    job_id: str
    total_amount_cents: int = 12000
    destination_stripe_account: Optional[str] = "acct_1NJ2h9K9zLm"


class ReleasePayoutResponse(BaseModel):
    status: str
    total_captured: float
    technician_payout: float
    platform_service_fee: float
    destination_stripe_account: str


@router.post("/escrow-hold", response_model=EscrowHoldResponse)
async def create_escrow_hold_endpoint(payload: EscrowHoldPayload):
    """
    Places Stripe Connect manual capture pre-authorization hold upon assignment.
    """
    res = await stripe_service.create_escrow_hold(
        job_id=payload.job_id,
        customer_id=payload.customer_id,
        amount_in_cents=payload.amount_in_cents
    )
    return EscrowHoldResponse(
        payment_intent_id=res["payment_intent_id"],
        status=res["status"],
        capture_method=res["capture_method"]
    )


@router.post("/release-payout", response_model=ReleasePayoutResponse)
async def release_escrow_payout_endpoint(payload: ReleasePayoutPayload):
    """
    Releases escrow hold and applies split (85% officer / 15% platform).
    """
    res = await stripe_service.release_escrow_payout(
        job_id=payload.job_id,
        total_amount_cents=payload.total_amount_cents,
        destination_stripe_account=payload.destination_stripe_account
    )
    return ReleasePayoutResponse(
        status=res["status"],
        total_captured=res["total_captured"],
        technician_payout=res["technician_payout"],
        platform_service_fee=res["platform_service_fee"],
        destination_stripe_account=res["destination_stripe_account"]
    )
