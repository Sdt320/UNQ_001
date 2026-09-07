"""SQLAlchemy ORM models for FieldMind AI."""

import enum
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
    JSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship

from app.database.session import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
    EMPLOYEE = "EMPLOYEE"


class UrgencyLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EMERGENCY = "EMERGENCY"


class RequestStatus(str, enum.Enum):
    PENDING_MATCH = "PENDING_MATCH"
    DISPATCHED = "DISPATCHED"
    CLAIMED = "CLAIMED"
    IN_TRANSIT = "IN_TRANSIT"
    WORK_IN_PROGRESS = "WORK_IN_PROGRESS"
    COMPLETED_PENDING_REVIEW = "COMPLETED_PENDING_REVIEW"
    SETTLED = "SETTLED"
    CANCELLED = "CANCELLED"


def generate_uuid_str() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid_str, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    phone_number = Column(String(32), unique=True, nullable=False, index=True)
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER, nullable=False, index=True)
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    field_officer = relationship("FieldOfficer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    service_requests = relationship("ServiceRequest", back_populates="customer", foreign_keys="ServiceRequest.customer_id")
    customer_reviews = relationship("CustomerReview", back_populates="customer")


class FieldOfficer(Base):
    __tablename__ = "field_officers"

    id = Column(String(36), primary_key=True, default=generate_uuid_str, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    skills = Column(JSON, default=list, nullable=False)  # Stored as list of strings
    is_available = Column(Boolean, default=True, nullable=False, index=True)
    latitude = Column(Float, nullable=False, default=37.7749)
    longitude = Column(Float, nullable=False, default=-122.4194)
    completed_jobs_current_month = Column(Integer, default=0, nullable=False)
    reward_eligible = Column(Boolean, default=False, nullable=False)
    average_rating = Column(Float, default=5.00, nullable=False)
    license_doc_url = Column(Text, nullable=True)
    stripe_account_id = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="field_officer")
    assigned_requests = relationship("ServiceRequest", back_populates="assigned_officer")
    reviews = relationship("CustomerReview", back_populates="officer")


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(String(36), primary_key=True, default=generate_uuid_str, index=True)
    customer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    assigned_officer_id = Column(String(36), ForeignKey("field_officers.id"), nullable=True, index=True)
    category = Column(String(64), nullable=False)
    required_skills = Column(JSON, default=list, nullable=False)
    urgency = Column(SQLEnum(UrgencyLevel), default=UrgencyLevel.MEDIUM, nullable=False)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING_MATCH, nullable=False, index=True)
    description = Column(Text, nullable=False)
    audio_transcript = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False, default=37.7749)
    longitude = Column(Float, nullable=False, default=-122.4194)
    search_radius_meters = Column(Integer, default=10000, nullable=False)
    stripe_payment_intent_id = Column(String(128), nullable=True)
    completion_photo_url = Column(Text, nullable=True)
    invoice_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    customer = relationship("User", back_populates="service_requests", foreign_keys=[customer_id])
    assigned_officer = relationship("FieldOfficer", back_populates="assigned_requests")
    review = relationship("CustomerReview", back_populates="service_request", uselist=False, cascade="all, delete-orphan")


class CustomerReview(Base):
    __tablename__ = "customer_reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid_str, index=True)
    job_id = Column(String(36), ForeignKey("service_requests.id", ondelete="CASCADE"), unique=True, nullable=False)
    customer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    officer_id = Column(String(36), ForeignKey("field_officers.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    service_request = relationship("ServiceRequest", back_populates="review")
    customer = relationship("User", back_populates="customer_reviews")
    officer = relationship("FieldOfficer", back_populates="reviews")


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    thread_id = Column(String(255), primary_key=True)
    checkpoint_ns = Column(String(255), primary_key=True, default="")
    checkpoint_id = Column(String(255), primary_key=True)
    parent_checkpoint_id = Column(String(255), nullable=True)
    type = Column(String(100), nullable=True)
    checkpoint = Column(JSON, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
