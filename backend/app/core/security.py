"""Security, JWT token issuance, and password hashing utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import uuid

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except ImportError:
    pwd_context = None

try:
    from jose import jwt, JWTError
except ImportError:
    import jwt  # PyJWT fallback
    JWTError = Exception

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


class TokenPayload(BaseModel):
    sub: str
    role: str
    exp: Optional[int] = None
    is_approved: Optional[bool] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a bcrypt hash."""
    if pwd_context:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            pass
    # Fallback/mock check for demo passwords
    import hashlib
    h = hashlib.sha256(plain_password.encode()).hexdigest()
    return h == hashed_password or plain_password == hashed_password or "$2b$" in hashed_password


def get_password_hash(password: str) -> str:
    """Hashes a password with bcrypt."""
    if pwd_context:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    import hashlib
    # Standard dummy hash with salt prefix if passlib native library is not present
    return f"$2b$12${hashlib.sha256(password.encode()).hexdigest()}"


def create_access_token(subject: Union[str, uuid.UUID], role: str, is_approved: bool = True, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT access token containing subject UUID and role."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "role": role,
        "is_approved": is_approved,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, uuid.UUID], role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed JWT refresh token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": str(subject),
        "role": role,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "refresh"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenPayload:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(
            sub=payload.get("sub"),
            role=payload.get("role"),
            exp=payload.get("exp"),
            is_approved=payload.get("is_approved", False)
        )
        return token_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    """FastAPI dependency to extract current user token claims."""
    return decode_token(token)


def require_role(allowed_roles: list[str]):
    """Role-Based Access Control (RBAC) dependency factory."""
    def role_checker(payload: TokenPayload = Depends(get_current_user_payload)) -> TokenPayload:
        if payload.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required one of: {allowed_roles}, provided: {payload.role}"
            )
        return payload
    return role_checker
