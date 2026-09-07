"""Authentication & RBAC endpoints (/api/v1/auth)."""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.database.session import get_db
from app.database.models import User, UserRole, FieldOfficer

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


class CustomerRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: str


class EmployeeRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: str
    skills: List[str]
    latitude: float = 37.7749
    longitude: float = -122.4194
    license_doc_url: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    full_name: str
    role: str
    is_approved: bool


@router.post("/register/customer", status_code=status.HTTP_201_CREATED)
async def register_customer(payload: CustomerRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Registers a new customer account."""
    # Check if email or phone exists
    stmt = select(User).where((User.email == payload.email) | (User.phone_number == payload.phone_number))
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone number already registered")

    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        role=UserRole.CUSTOMER,
        is_approved=True,
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(subject=user.id, role=user.role.value, is_approved=True)

    return {
        "user_id": user.id,
        "role": user.role.value,
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/register/employee", status_code=status.HTTP_201_CREATED)
async def register_employee(payload: EmployeeRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Registers a field technician; initial status set to is_approved = FALSE."""
    stmt = select(User).where((User.email == payload.email) | (User.phone_number == payload.phone_number))
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone number already registered")

    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        role=UserRole.EMPLOYEE,
        is_approved=False,
        is_active=True
    )
    db.add(user)
    await db.flush()

    officer = FieldOfficer(
        user_id=user.id,
        skills=payload.skills,
        is_available=True,
        latitude=payload.latitude,
        longitude=payload.longitude,
        license_doc_url=payload.license_doc_url,
        average_rating=5.00,
        completed_jobs_current_month=0,
        reward_eligible=False,
        stripe_account_id=f"acct_{uuid.uuid4().hex[:12]}"
    )
    db.add(officer)
    await db.commit()
    await db.refresh(user)

    return {
        "user_id": user.id,
        "role": user.role.value,
        "is_approved": False,
        "message": "Employee registration submitted. Account pending admin verification."
    }


class DirectLoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: Optional[OAuth2PasswordRequestForm] = Depends(None),
    json_body: Optional[DirectLoginRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    """Issues JWT Access and Refresh tokens with RBAC claims."""
    username = form_data.username if form_data else (json_body.username if json_body else "")
    password = form_data.password if form_data else (json_body.password if json_body else "")

    if not username or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username/Email and Password are required")

    stmt = select(User).where(User.email == username)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(subject=user.id, role=user.role.value, is_approved=user.is_approved)
    refresh_token = create_refresh_token(subject=user.id, role=user.role.value)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=user.id,
        full_name=user.full_name,
        role=user.role.value,
        is_approved=user.is_approved
    )
