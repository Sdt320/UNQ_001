"""FieldMind AI - Main FastAPI Application Entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.database.session import init_db
from app.api.v1 import auth, admin, requests, payments, rewards
from app.api.webhooks import whatsapp


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan events."""
    logger.info("FieldMind AI backend starting up...")
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"Database initialization encountered warning: {e}")
    yield
    logger.info("FieldMind AI backend shutting down...")


app = FastAPI(
    title="FieldMind AI - Autonomous Field Operations API",
    description="Multi-Agent on-demand home repair and field workforce marketplace platform with LangGraph, PostGIS, WhatsApp Business Cloud API, Redis Mutex, and Stripe Escrow.",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(requests.router, prefix=settings.API_V1_STR)
app.include_router(payments.router, prefix=settings.API_V1_STR)
app.include_router(rewards.router, prefix=settings.API_V1_STR)

# Webhook Listener Routers
app.include_router(whatsapp.router)


@app.get("/health", tags=["Health & Status"])
async def health_check():
    """Health check probe endpoint."""
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["Health & Status"])
async def root():
    """Welcome root endpoint."""
    return {
        "message": "Welcome to FieldMind AI Autonomous Operations Gateway",
        "documentation": "/docs",
        "version": settings.VERSION
    }
