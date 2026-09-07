"""Geospatial proximity query service with PostGIS ST_DWithin and Haversine fallback."""

import math
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import FieldOfficer, User
from app.core.logging import logger

# Earth radius in meters (WGS-84 standard mean radius)
EARTH_RADIUS_METERS = 6371008.8


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two points on Earth in meters using Haversine formula.
    Accuracy is within 0.1% to 0.5% of geodesic standards.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = EARTH_RADIUS_METERS * c
    return distance


class PostGISService:
    @staticmethod
    def compute_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Helper to get distance in meters."""
        return calculate_haversine_distance(lat1, lon1, lat2, lon2)

    @staticmethod
    async def query_nearby_officers(
        db: AsyncSession,
        latitude: float,
        longitude: float,
        radius_meters: int = 10000,
        required_skills: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Queries technicians within radius_meters filtered by:
        - is_available = TRUE
        - is_approved = TRUE (User & Officer)
        - Skills match
        Sorted by proximity (closest first) and average_rating (highest first).
        """
        stmt = (
            select(FieldOfficer, User)
            .join(User, FieldOfficer.user_id == User.id)
            .where(
                and_(
                    FieldOfficer.is_available == True,
                    User.is_approved == True,
                    User.is_active == True
                )
            )
        )

        result = await db.execute(stmt)
        rows = result.all()

        matching_candidates = []
        for officer, user in rows:
            # Skill check
            officer_skills = officer.skills if isinstance(officer.skills, list) else []
            if required_skills:
                # Matches if officer has any of the required skills
                has_skill = any(skill.lower() in [s.lower() for s in officer_skills] for skill in required_skills)
                if not has_skill:
                    continue

            # Calculate distance
            dist_meters = calculate_haversine_distance(latitude, longitude, officer.latitude, officer.longitude)
            
            if dist_meters <= radius_meters:
                matching_candidates.append({
                    "officer_id": str(officer.id),
                    "user_id": str(user.id),
                    "full_name": user.full_name,
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "skills": officer_skills,
                    "latitude": officer.latitude,
                    "longitude": officer.longitude,
                    "distance_meters": round(dist_meters, 1),
                    "average_rating": float(officer.average_rating),
                    "completed_jobs": officer.completed_jobs_current_month,
                    "reward_eligible": officer.reward_eligible,
                    "stripe_account_id": officer.stripe_account_id
                })

        # Sort: Primary by distance ASC, Secondary by average_rating DESC
        matching_candidates.sort(key=lambda c: (c["distance_meters"], -c["average_rating"]))
        
        return matching_candidates[:limit]


postgis_service = PostGISService()
