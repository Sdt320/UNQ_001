"""Pytest fixtures and test environment setup."""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.database.models import User, FieldOfficer, ServiceRequest, UserRole, UrgencyLevel, RequestStatus
from app.core.security import get_password_hash
from app.main import app

# Test Async SQLite Database
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Sets up an isolated in-memory test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def seed_data(test_db: AsyncSession):
    """Seeds test data for customers, admin, and qualified field officers."""
    # 1. Admin User
    admin = User(
        id="admin-uuid-001",
        email="admin@fieldmind.com",
        password_hash=get_password_hash("AdminPass123!"),
        full_name="Elena Platform Admin",
        phone_number="+14155550001",
        role=UserRole.ADMIN,
        is_approved=True,
        is_active=True
    )
    # 2. Customer User
    customer = User(
        id="customer-uuid-001",
        email="david.customer@example.com",
        password_hash=get_password_hash("CustomerPass123!"),
        full_name="David Miller",
        phone_number="+14155552671",
        role=UserRole.CUSTOMER,
        is_approved=True,
        is_active=True
    )

    # 3. Field Officer 1 (Close Plumber, High Rating)
    officer_user1 = User(
        id="officer-user-001",
        email="marcus.pro@fieldmind.com",
        password_hash=get_password_hash("WorkerPass123!"),
        full_name="Marcus Vance",
        phone_number="+14155559821",
        role=UserRole.EMPLOYEE,
        is_approved=True,
        is_active=True
    )
    officer1 = FieldOfficer(
        id="officer-001",
        user_id=officer_user1.id,
        skills=["pipe_leak", "soldering", "drain_cleaning", "pipe_replacement"],
        is_available=True,
        latitude=37.7749,
        longitude=-122.4194,
        completed_jobs_current_month=104,
        reward_eligible=True,
        average_rating=4.92,
        stripe_account_id="acct_1NJ2h9K9zLm"
    )

    # 4. Field Officer 2 (Close Plumber, Moderate Rating)
    officer_user2 = User(
        id="officer-user-002",
        email="sarah.connor@fieldmind.com",
        password_hash=get_password_hash("WorkerPass123!"),
        full_name="Sarah Connor",
        phone_number="+14155554321",
        role=UserRole.EMPLOYEE,
        is_approved=True,
        is_active=True
    )
    officer2 = FieldOfficer(
        id="officer-002",
        user_id=officer_user2.id,
        skills=["pipe_leak", "pipe_replacement"],
        is_available=True,
        latitude=37.7800,
        longitude=-122.4200,
        completed_jobs_current_month=89,
        reward_eligible=False,
        average_rating=4.85,
        stripe_account_id="acct_2OK3i0L0aMn"
    )

    # 5. Field Officer 3 (Electrician, Close)
    officer_user3 = User(
        id="officer-user-003",
        email="dave.electric@fieldmind.com",
        password_hash=get_password_hash("WorkerPass123!"),
        full_name="Dave Spark",
        phone_number="+14155557788",
        role=UserRole.EMPLOYEE,
        is_approved=True,
        is_active=True
    )
    officer3 = FieldOfficer(
        id="officer-003",
        user_id=officer_user3.id,
        skills=["breaker_replacement", "panel_wiring", "short_circuit_diagnosis"],
        is_available=True,
        latitude=37.7760,
        longitude=-122.4180,
        completed_jobs_current_month=45,
        reward_eligible=False,
        average_rating=4.70,
        stripe_account_id="acct_3PL4j1M1bNo"
    )

    # 6. Field Officer 4 (Far Away Plumber - 15km)
    officer_user4 = User(
        id="officer-user-004",
        email="elena.far@fieldmind.com",
        password_hash=get_password_hash("WorkerPass123!"),
        full_name="Elena Far",
        phone_number="+14155559900",
        role=UserRole.EMPLOYEE,
        is_approved=True,
        is_active=True
    )
    officer4 = FieldOfficer(
        id="officer-004",
        user_id=officer_user4.id,
        skills=["pipe_leak", "soldering"],
        is_available=True,
        latitude=37.8900,
        longitude=-122.3000,
        completed_jobs_current_month=101,
        reward_eligible=True,
        average_rating=4.95,
        stripe_account_id="acct_4QM5k2N2cOp"
    )

    # 7. Field Officer 5 (Unapproved Technician)
    officer_user5 = User(
        id="officer-user-005",
        email="unapproved.worker@fieldmind.com",
        password_hash=get_password_hash("WorkerPass123!"),
        full_name="Bob Rookie",
        phone_number="+14155551122",
        role=UserRole.EMPLOYEE,
        is_approved=False,
        is_active=True
    )
    officer5 = FieldOfficer(
        id="officer-005",
        user_id=officer_user5.id,
        skills=["pipe_leak"],
        is_available=True,
        latitude=37.7750,
        longitude=-122.4190,
        completed_jobs_current_month=0,
        reward_eligible=False,
        average_rating=5.00,
        license_doc_url="https://s3.amazonaws.com/fieldmind/licenses/bob.pdf"
    )

    test_db.add_all([
        admin, customer,
        officer_user1, officer1,
        officer_user2, officer2,
        officer_user3, officer3,
        officer_user4, officer4,
        officer_user5, officer5
    ])
    await test_db.commit()
    return {
        "admin": admin,
        "customer": customer,
        "officers": [officer1, officer2, officer3, officer4, officer5]
    }
