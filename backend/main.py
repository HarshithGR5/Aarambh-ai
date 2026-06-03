import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base
from app.routers import (
    auth, children, attendance, observations,
    milestones, pdrs, drawings, referrals,
    recommendations, dashboard,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
# Silence SQLAlchemy's engine logger (SQL queries) — set to WARNING in production.
# Duplicate logs were caused by echo=True in database.py + root logger both firing.
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Create all tables on startup (use Alembic in production)
Base.metadata.create_all(bind=engine)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Aarambh AI API",
    description="India's First Developmental Digital Twin Platform for Early Childhood Development",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    redirect_slashes=False,
    contact={
        "name": "Aarambh AI Team",
        "url": "https://aarambh.ai",
    },
    license_info={
        "name": "MIT",
    },
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    body_preview = None
    try:
        body_preview = str(exc.body)[:800] if exc.body else None
    except Exception:
        pass
    logger.error(
        f"422 Validation Error — {request.method} {request.url}\n"
        f"  Errors: {errors}\n"
        f"  Body preview: {body_preview}"
    )
    return JSONResponse(status_code=422, content={"detail": errors})


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:5000",
        "https://*.replit.app",
        "https://*.replit.dev",
        "https://aarambh-ai-gold.vercel.app",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR, check_dir=False), name="uploads")

# Include all routers
app.include_router(auth.router,            prefix="/api/v1/auth",            tags=["Auth"])
app.include_router(children.router,        prefix="/api/v1/children",        tags=["Children"])
app.include_router(attendance.router,      prefix="/api/v1/attendance",      tags=["Attendance"])
app.include_router(observations.router,    prefix="/api/v1/observations",    tags=["Observations"])
app.include_router(milestones.router,      prefix="/api/v1/milestones",      tags=["Milestones"])
app.include_router(pdrs.router,            prefix="/api/v1/pdrs",            tags=["PDRS"])
app.include_router(drawings.router,        prefix="/api/v1/drawings",        tags=["Drawings"])
app.include_router(referrals.router,       prefix="/api/v1/referrals",       tags=["Referrals"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(dashboard.router,       prefix="/api/v1/dashboard",       tags=["Dashboard"])


@app.on_event("startup")
async def on_startup():
    logger.info("=== AARAMBH AI BACKEND STARTING ===")
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"OpenAI configured: {bool(settings.OPENAI_API_KEY)}")
    try:
        from app.utils.seed_data import seed_all
        seed_all()
        logger.info("Seed data loaded")
    except Exception as e:
        logger.warning(f"Seed data warning: {e}")


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Aarambh AI API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "description": "India's First Developmental Digital Twin Platform",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "service": "aarambh-ai-backend"}
