"""LangGraph StateGraph compilation and execution helpers."""

from typing import Any, Dict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.state import FieldMindState
from app.agents.nodes import (
    parse_request_node,
    spatial_match_node,
    dispatch_broadcast_node,
    expand_radius_node,
    process_acceptance_node,
    escrow_preauth_hold_node,
    verify_and_invoice_node
)
from app.agents.edges import route_after_spatial_match
from app.core.logging import logger


def build_fieldmind_graph(checkpointer=None, interrupt_before_acceptance: bool = False):
    """
    Constructs the FieldMind AI multi-agent workflow graph.
    """
    workflow = StateGraph(FieldMindState)

    # Register Nodes
    workflow.add_node("parse_request", parse_request_node)
    workflow.add_node("spatial_match", spatial_match_node)
    workflow.add_node("dispatch_broadcast", dispatch_broadcast_node)
    workflow.add_node("expand_radius", expand_radius_node)
    workflow.add_node("process_acceptance", process_acceptance_node)
    workflow.add_node("escrow_preauth_hold", escrow_preauth_hold_node)
    workflow.add_node("verify_and_invoice", verify_and_invoice_node)

    # Define Linear & Conditional Edges
    workflow.add_edge(START, "parse_request")
    workflow.add_edge("parse_request", "spatial_match")

    # Conditional routing after spatial matchmaking
    workflow.add_conditional_edges(
        "spatial_match",
        route_after_spatial_match,
        {
            "dispatch_broadcast": "dispatch_broadcast",
            "expand_radius": "expand_radius"
        }
    )

    # Loop back from radius expansion to spatial matchmaking
    workflow.add_edge("expand_radius", "spatial_match")

    # Execution path from dispatch to acceptance and escrow
    workflow.add_edge("dispatch_broadcast", "process_acceptance")
    workflow.add_edge("process_acceptance", "escrow_preauth_hold")
    workflow.add_edge("escrow_preauth_hold", "verify_and_invoice")
    workflow.add_edge("verify_and_invoice", END)

    # Compile with persistence
    saver = checkpointer if checkpointer is not None else MemorySaver()
    interrupts = ["process_acceptance"] if interrupt_before_acceptance else []
    
    app = workflow.compile(
        checkpointer=saver,
        interrupt_before=interrupts
    )
    return app


# Shared global graph instance with in-memory checkpointer
global_checkpointer = MemorySaver()
fieldmind_agent_graph = build_fieldmind_graph(checkpointer=global_checkpointer, interrupt_before_acceptance=True)
fieldmind_direct_graph = build_fieldmind_graph(checkpointer=global_checkpointer, interrupt_before_acceptance=False)


async def execute_intake_and_dispatch(initial_state: FieldMindState, thread_id: str) -> Dict[str, Any]:
    """
    Executes initial phase of graph: intake -> spatial matchmaking -> dispatch broadcast.
    Pauses before process_acceptance awaiting technician webhook claim.
    """
    config = {"configurable": {"thread_id": thread_id}}
    logger.info(f"Starting agent graph execution for thread {thread_id}")
    
    # Run until the interrupt before process_acceptance
    result = await fieldmind_agent_graph.ainvoke(initial_state, config=config)
    return result


async def resume_graph_with_acceptance(
    thread_id: str,
    officer_id: str,
    officer_name: str = "Marcus Vance",
    officer_phone: str = "+14155559821"
) -> Dict[str, Any]:
    """
    Resumes graph after technician button click webhook.
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    # Update state with winning technician
    update_payload = {
        "assigned_officer_id": officer_id,
        "assigned_officer_name": officer_name,
        "assigned_officer_phone": officer_phone,
        "claim_status": "CLAIMED"
    }
    
    # Update state in checkpointer
    await fieldmind_agent_graph.aupdate_state(config, update_payload, as_node="dispatch_broadcast")
    
    # Resume graph execution through escrow, verification, and settlement
    final_result = await fieldmind_agent_graph.ainvoke(None, config=config)
    return final_result
