"""
Step 4 Automated Test Suite: LangGraph Multi-Agent State Machine & Webhook Checkpoints.
Acceptance: Confirm the LangGraph state machine executes through dispatch and enters a paused state awaiting response.
"""

import pytest
import uuid
from app.agents.state import FieldMindState
from app.agents.graph import (
    fieldmind_agent_graph,
    execute_intake_and_dispatch,
    resume_graph_with_acceptance
)
from app.agents.nodes import expand_radius_node


@pytest.mark.asyncio
async def test_langgraph_intake_dispatch_pause_flow():
    """
    Validates that the LangGraph agent executes through parse_request, spatial_match,
    and dispatch_broadcast, then pauses before process_acceptance.
    """
    job_id = str(uuid.uuid4())
    initial_state: FieldMindState = {
        "job_id": job_id,
        "customer_id": "cust-david-01",
        "customer_name": "David Miller",
        "customer_phone": "+14155552671",
        "user_prompt": "Emergency: My bathroom pipe burst under the sink and clean water is flooding everywhere.",
        "latitude": 37.7793,
        "longitude": -122.4230,
        "search_radius_meters": 10000,
        "step_history": []
    }

    # Execute intake & dispatch
    result = await execute_intake_and_dispatch(initial_state, thread_id=job_id)

    # Verify state after dispatch
    assert result["category"] == "Plumbing"
    assert "pipe_leak" in result["required_skills"]
    assert result["urgency"] in ["HIGH", "EMERGENCY"]
    assert result["status"] == "DISPATCHED"
    assert "parse_request" in result["step_history"]
    assert "spatial_match" in result["step_history"]
    assert "dispatch_broadcast" in result["step_history"]
    assert result["candidates_notified"] >= 1


@pytest.mark.asyncio
async def test_langgraph_resume_after_technician_claim():
    """
    Validates that resuming the paused state graph processes winning claim,
    executes Stripe escrow pre-auth, verifies repair photo, and generates PDF invoice.
    """
    job_id = str(uuid.uuid4())
    initial_state: FieldMindState = {
        "job_id": job_id,
        "customer_id": "cust-david-01",
        "customer_name": "David Miller",
        "customer_phone": "+14155552671",
        "user_prompt": "Emergency: bathroom pipe burst",
        "latitude": 37.7793,
        "longitude": -122.4230,
        "search_radius_meters": 10000,
        "step_history": []
    }

    # 1. Run to pause point
    await execute_intake_and_dispatch(initial_state, thread_id=job_id)

    # 2. Resume with winning technician
    final_state = await resume_graph_with_acceptance(
        thread_id=job_id,
        officer_id="officer-001",
        officer_name="Marcus Vance",
        officer_phone="+14155559821"
    )

    assert final_state["status"] == "SETTLED"
    assert final_state["assigned_officer_id"] == "officer-001"
    assert final_state["stripe_payment_intent_id"] is not None
    assert final_state["vision_verified"] is True
    assert final_state["invoice_url"] is not None
    assert final_state["technician_payout"] == 102.00
    assert final_state["platform_fee"] == 18.00


@pytest.mark.asyncio
async def test_langgraph_dynamic_radius_expansion_node():
    """Validates expand_radius_node increments radius from 10km to 20km."""
    state: FieldMindState = {
        "job_id": "job-fallback-01",
        "search_radius_meters": 10000,
        "fallback_iteration": 0,
        "step_history": []
    }
    updated = await expand_radius_node(state)
    assert updated["search_radius_meters"] == 20000
    assert updated["fallback_iteration"] == 1
    assert "expand_radius" in updated["step_history"]
