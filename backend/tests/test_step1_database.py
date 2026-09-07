"""
Step 1 Automated Test Suite: Database Schema, Connection & Geospatial Precision.
Acceptance: Confirm database models and verify geospatial distance calculations within 0.5% margin of error.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, FieldOfficer, ServiceRequest, UserRole
from app.services.postgis_service import calculate_haversine_distance, postgis_service


@pytest.mark.asyncio
async def test_database_user_and_officer_schema(test_db: AsyncSession):
    """Verifies User and FieldOfficer relational integrity and constraints."""
    user = User(
        email="test.plumber@fieldmind.com",
        password_hash="$2b$12$e8Fj19K...",
        full_name="Marcus Vance",
        phone_number="+14155559821",
        role=UserRole.EMPLOYEE,
        is_approved=False
    )
    test_db.add(user)
    await test_db.flush()

    officer = FieldOfficer(
        user_id=user.id,
        skills=["pipe_leak", "soldering"],
        is_available=True,
        latitude=37.7749,
        longitude=-122.4194,
        average_rating=4.95,
        completed_jobs_current_month=105,
        reward_eligible=True
    )
    test_db.add(officer)
    await test_db.commit()

    # Query back
    stmt = select(FieldOfficer).where(FieldOfficer.user_id == user.id)
    res = await test_db.execute(stmt)
    saved_officer = res.scalar_one()

    assert saved_officer is not None
    assert saved_officer.user_id == user.id
    assert saved_officer.average_rating == 4.95
    assert saved_officer.completed_jobs_current_month == 105
    assert saved_officer.reward_eligible is True
    assert "pipe_leak" in saved_officer.skills


def test_geospatial_distance_margin_of_error():
    """
    Validates that Haversine distance calculations are within a strict 0.5% margin-of-error
    compared to internationally standardized geodesic reference distances (Vincenty / WGS84).
    """
    benchmark_pairs = [
        {
            "name": "SF City Hall to Oakland City Hall",
            "p1": (37.7793, -122.4192),
            "p2": (37.8044, -122.2711),
            "geodesic_ref_meters": 13320.0  # ~13.32 km
        },
        {
            "name": "Times Square to Empire State Building NYC",
            "p1": (40.7580, -73.9855),
            "p2": (40.7484, -73.9857),
            "geodesic_ref_meters": 1068.0  # ~1.068 km
        },
        {
            "name": "London Big Ben to Tower of London",
            "p1": (51.5007, -0.1246),
            "p2": (51.5081, -0.0759),
            "geodesic_ref_meters": 3470.0  # ~3.47 km
        },
        {
            "name": "Local 500m Technician Proximity Check",
            "p1": (37.7749, -122.4194),
            "p2": (37.7794, -122.4194),
            "geodesic_ref_meters": 500.4
        }
    ]

    for pair in benchmark_pairs:
        lat1, lon1 = pair["p1"]
        lat2, lon2 = pair["p2"]
        ref_meters = pair["geodesic_ref_meters"]

        calculated = calculate_haversine_distance(lat1, lon1, lat2, lon2)
        error_margin = abs(calculated - ref_meters) / ref_meters

        print(f"\n{pair['name']}: Calc = {calculated:.2f}m, Ref = {ref_meters}m, Margin = {error_margin * 100:.3f}%")
        
        # Assert accuracy within 0.5% (0.005)
        assert error_margin <= 0.005, f"Margin of error exceeded for {pair['name']}: {error_margin * 100:.3f}% > 0.5%"
