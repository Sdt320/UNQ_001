"""
Step 3 Automated Test Suite: Multimodal Audio Transcription & Pydantic Intent Parsing.
Acceptance: Verify text and voice inputs parse into valid Pydantic schemas across all trade categories.
"""

import pytest
import time
from app.services.openai_service import openai_service, ParsedJobRequirement


@pytest.mark.asyncio
async def test_audio_transcription_latency_and_accuracy():
    """Validates that audio transcription executes within SLA (< 2.0s)."""
    start_time = time.time()
    audio_dummy = b"RIFF....WAVEfmt ...."
    transcript = await openai_service.transcribe_audio(audio_dummy, "customer_voice.ogg")
    duration = time.time() - start_time

    assert duration <= 2.0, f"Transcription exceeded 2.0s SLA: {duration:.3f}s"
    assert len(transcript) > 10
    assert "pipe" in transcript.lower() or "emergency" in transcript.lower()


@pytest.mark.asyncio
async def test_pydantic_intent_extraction_across_all_trade_categories():
    """
    Validates structured Pydantic intent parsing across all 5 core trades:
    - Plumbing
    - Electrical
    - AC Repair
    - Masonry
    - Carpentry
    """
    test_cases = [
        {
            "prompt": "Emergency: My bathroom pipe burst under the sink and clean water is flooding everywhere.",
            "expected_category": "Plumbing",
            "expected_skill": "pipe_leak",
            "expected_urgency": "EMERGENCY"
        },
        {
            "prompt": "The main circuit breaker is sparking and panel wiring keeps tripping when oven starts.",
            "expected_category": "Electrical",
            "expected_skill": "breaker_replacement",
            "expected_urgency": "HIGH"
        },
        {
            "prompt": "My central air conditioner is blowing warm air and compressor is making loud buzzing noise.",
            "expected_category": "AC Repair",
            "expected_skill": "freon_recharge",
            "expected_urgency": "MEDIUM"
        },
        {
            "prompt": "Exterior brick wall has concrete cracks that need mortar patching before the rain starts.",
            "expected_category": "Masonry",
            "expected_skill": "mortar_patching",
            "expected_urgency": "LOW"
        },
        {
            "prompt": "Custom wooden kitchen cabinet door fell off its hinge and timber frame is misaligned.",
            "expected_category": "Carpentry",
            "expected_skill": "door_hinge_realignment",
            "expected_urgency": "LOW"
        }
    ]

    for tc in test_cases:
        parsed = await openai_service.parse_job_intent(tc["prompt"])
        
        assert isinstance(parsed, ParsedJobRequirement), "Output must conform to Pydantic ParsedJobRequirement"
        assert parsed.category.lower() == tc["expected_category"].lower(), f"Category mismatch for {tc['expected_category']}"
        assert any(tc["expected_skill"] in s for s in parsed.required_skills), f"Skill {tc['expected_skill']} not found in {parsed.required_skills}"
        assert parsed.urgency in ["LOW", "MEDIUM", "HIGH", "EMERGENCY"]
        assert len(parsed.estimated_scope) > 5
