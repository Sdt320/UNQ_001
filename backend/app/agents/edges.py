"""Conditional routing edges for LangGraph multi-agent state machine."""

from typing import Literal
from app.agents.state import FieldMindState


def route_after_spatial_match(state: FieldMindState) -> Literal["dispatch_broadcast", "expand_radius"]:
    """Determines whether to broadcast dispatch or expand search radius."""
    candidates = state.get("matched_candidates", [])
    if candidates and len(candidates) > 0:
        return "dispatch_broadcast"
    
    # If no candidates and we haven't maxed out radius
    current_radius = state.get("search_radius_meters", 10000)
    if current_radius < 20000:
        return "expand_radius"
    
    return "dispatch_broadcast"


def route_after_dispatch(state: FieldMindState) -> Literal["process_acceptance", "expand_radius", "end"]:
    """Determines if workflow pauses for technician webhook or proceeds."""
    claim_status = state.get("claim_status", "AWAITING_CLAIM")
    if claim_status == "CLAIMED":
        return "process_acceptance"
    elif claim_status in ["EXPIRED", "NO_CLAIM"]:
        current_radius = state.get("search_radius_meters", 10000)
        if current_radius < 20000:
            return "expand_radius"
        return "end"
    
    # Standard flow awaits external callback; default path for graph compilation
    return "process_acceptance"
