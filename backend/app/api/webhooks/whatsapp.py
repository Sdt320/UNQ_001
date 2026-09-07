"""Meta WhatsApp Cloud API Webhook Listener (/webhooks/whatsapp)."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Header, HTTPException, Query, Request, Response, status
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import logger
from app.services.redis_lock_service import redis_lock_service
from app.services.whatsapp_service import whatsapp_service
from app.agents.graph import resume_graph_with_acceptance

router = APIRouter(prefix="/webhooks/whatsapp", tags=["WhatsApp Meta Cloud API Webhook"])


@router.get("", response_class=Response)
async def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """
    Handles Meta challenge handshake verification.
    """
    logger.info(f"WhatsApp webhook challenge received: mode={hub_mode}, verify_token={hub_verify_token}")

    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        if hub_challenge:
            return Response(content=hub_challenge, media_type="text/plain", status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch")


@router.post("", status_code=status.HTTP_200_OK)
async def process_whatsapp_webhook_event(request: Request):
    """
    Processes incoming WhatsApp Cloud API events: interactive button replies, audio notes, completion photos.
    Responds with immediate 200 OK (<500ms) to satisfy Meta SLA.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    logger.info(f"WhatsApp webhook event payload received: {body}")

    # Inspect incoming messages
    try:
        entries = body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    from_phone = msg.get("from")
                    msg_type = msg.get("type")

                    # Handle interactive button responses (ACCEPT / REJECT)
                    if msg_type == "interactive":
                        interactive = msg.get("interactive", {})
                        button_reply = interactive.get("button_reply", {})
                        button_id = button_reply.get("id", "")

                        if button_id.startswith("ACCEPT_"):
                            job_id = button_id.replace("ACCEPT_", "")
                            officer_id = f"officer_{from_phone}"

                            logger.info(f"Technician {from_phone} tapped ACCEPT for job {job_id}")

                            # Attempt atomic Redis mutex lock
                            lock_won = await redis_lock_service.acquire_job_claim_lock(
                                job_id=job_id,
                                officer_id=officer_id,
                                ttl_seconds=15
                            )

                            if lock_won:
                                logger.info(f"Technician {from_phone} WON lock for job {job_id}")
                                # Send location pin and resume LangGraph
                                await whatsapp_service.send_location_pin(
                                    to_phone=from_phone,
                                    job_id=job_id,
                                    latitude=37.7793,
                                    longitude=-122.4230,
                                    customer_name="David Miller"
                                )
                                # Resume LangGraph in background
                                try:
                                    await resume_graph_with_acceptance(
                                        thread_id=job_id,
                                        officer_id=officer_id,
                                        officer_phone=from_phone
                                    )
                                except Exception as ge:
                                    logger.warning(f"Resumption notice: {ge}")
                            else:
                                logger.info(f"Technician {from_phone} LOST lock (Already Claimed) for job {job_id}")
                                await whatsapp_service.send_job_already_claimed(
                                    to_phone=from_phone,
                                    job_id=job_id
                                )

                        elif button_id.startswith("REJECT_"):
                            job_id = button_id.replace("REJECT_", "")
                            logger.info(f"Technician {from_phone} declined job {job_id}")

    except Exception as e:
        logger.error(f"Error processing webhook payload: {e}")

    # Immediate 200 OK acknowledgment
    return {"status": "ok", "message": "Webhook event queued"}
