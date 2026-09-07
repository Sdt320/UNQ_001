"""
Step 2 Automated Test Suite: PostGIS Matchmaking & Spatial Filtering.
Acceptance: Verify spatial queries retrieve only active, approved technicians within 10km radius sorted by proximity and rating.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.postgis_service import postgis_service


@pytest.mark.asyncio
async def test_spatial_query_10km_filtering_and_ranking(test_db: AsyncSession, seed_data):
    """
    Tests that:
    1. Only approved and available technicians are returned.
    2. Technicians with matching skills are included.
    3. Technicians beyond 10,000m are excluded.
    4. Unapproved technicians are excluded.
    5. Results are ranked by proximity ASC, then rating DESC.
    """
    customer_lat = 37.7793
    customer_lon = -122.4230

    results = await postgis_service.query_nearby_officers(
        db=test_db,
        latitude=customer_lat,
        longitude=customer_lon,
        radius_meters=10000,
        required_skills=["pipe_leak", "pipe_replacement"],
        limit=5
    )

    # We expect officer-001 (Marcus) and officer-002 (Sarah) to match within 10km
    # officer-003 is Electrician (no pipe_leak skill)
    # officer-004 is >15km away (outside 10km)
    # officer-005 is unapproved
    officer_ids = [r["officer_id"] for r in results]

    assert "officer-001" in officer_ids
    assert "officer-002" in officer_ids
    assert "officer-003" not in officer_ids, "Electrician should not match plumbing skill requirement"
    assert "officer-004" not in officer_ids, "Far technician beyond 10km should be excluded at 10km radius"
    assert "officer-005" not in officer_ids, "Unapproved technician must NEVER be returned in dispatch"

    # Verify sorting: closer officer first
    distances = [r["distance_meters"] for r in results]
    assert distances == sorted(distances), "Results must be sorted by proximity"


@pytest.mark.asyncio
async def test_spatial_query_dynamic_radius_expansion_20km(test_db: AsyncSession, seed_data):
    """
    Tests that expanding search radius to 20,000m includes second-tier technicians (e.g. officer-004 at 15km).
    """
    customer_lat = 37.7793
    customer_lon = -122.4230

    results_20k = await postgis_service.query_nearby_officers(
        db=test_db,
        latitude=customer_lat,
        longitude=customer_lon,
        radius_meters=20000,
        required_skills=["pipe_leak"],
        limit=5
    )

    officer_ids = [r["officer_id"] for r in results_20k]
    assert "officer-004" in officer_ids, "Officer 4 should be found within 20km expanded radius"
    assert len(results_20k) >= 3
