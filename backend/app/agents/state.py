"""State schemas and Pydantic validation models for LangGraph."""

from typing import Any, Dict, List, Optional, TypedDict
from pydantic import BaseModel, Field


class ParsedJobRequirement(BaseModel):
    category: str = Field(..., description="Trade category, e.g. Plumbing, Electrical, AC Repair, Masonry, Carpentry")
    required_skills: List[str] = Field(default_factory=list, description="Sub-trade skill tags")
    urgency: str = Field(default="MEDIUM", description="Urgency: LOW, MEDIUM, HIGH, EMERGENCY")
    estimated_scope: str = Field(default="", description="Scope summary and tool requirements")


class FieldMindState(TypedDict, total=False):
    job_id: str
    customer_id: str
    customer_name: Optional[str]
    customer_phone: Optional[str]
    user_prompt: str
    audio_url: Optional[str]
    latitude: float
    longitude: float
    
    # Intent diagnostics
    audio_transcript: Optional[str]
    category: Optional[str]
    required_skills: List[str]
    urgency: str
    estimated_scope: Optional[str]
    
    # Spatial Matchmaking
    search_radius_meters: int
    matched_candidates: List[Dict[str, Any]]
    candidates_notified: int
    fallback_iteration: int
    
    # Dispatch & Claim
    claim_status: str  # PENDING, CLAIMED, EXPIRED, CANCELLED
    assigned_officer_id: Optional[str]
    assigned_officer_name: Optional[str]
    assigned_officer_phone: Optional[str]
    
    # Escrow & Payments
    stripe_payment_intent_id: Optional[str]
    amount_in_cents: int
    
    # Closure & Invoice
    completion_photo_url: Optional[str]
    vision_verified: bool
    invoice_url: Optional[str]
    total_amount: float
    technician_payout: float
    platform_fee: float
    
    # Workflow metadata
    status: str
    step_history: List[str]
    error_message: Optional[str]
