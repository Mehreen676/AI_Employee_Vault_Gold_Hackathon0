"""
AI Employee Vault — Gold Cloud
Production entry point.

Start with:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
import os
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

_REQUIRED_VARS = ["DATABASE_URL", "OPENAI_API_KEY", "INSTAGRAM_ACCESS_TOKEN"]
_missing = [v for v in _REQUIRED_VARS if not os.getenv(v)]
if _missing:
    logging.warning(
        "Missing environment variables: %s — some features may be degraded.",
        _missing,
    )

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("vault")

# ---------------------------------------------------------------------------
# DB (import after load_dotenv so DATABASE_URL is available)
# ---------------------------------------------------------------------------
from backend.db import Base, db_available, engine  # noqa: E402
from backend import models as _models  # noqa: E402, F401  — registers ORM classes


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup ----
    if db_available and engine is not None:
        logger.info("Running create_all against Neon Postgres …")
        Base.metadata.create_all(bind=engine)
        logger.info("Schema ready.")
    else:
        logger.warning("DATABASE_URL not set — running without DB persistence.")

    logger.info("AI Employee Vault is online.")
    yield

    # ---- shutdown ----
    if db_available and engine is not None:
        engine.dispose()
        logger.info("DB connection pool disposed.")
    logger.info("AI Employee Vault shut down cleanly.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Employee Vault — Gold Cloud",
    description="Autonomous AI agent vault with Neon PostgreSQL, OpenAI, and Instagram Graph API.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
_ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request timing + error middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:  # pragma: no cover
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error.", "path": request.url.path},
        )
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
    logger.info(
        "%s %s → %s  (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Caught unhandled exception for %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )


# ---------------------------------------------------------------------------
# Core routes
# ---------------------------------------------------------------------------
@app.get("/", tags=["General"], summary="Root")
async def root():
    return {
        "service": "AI Employee Vault — Gold Cloud",
        "version": app.version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["General"], summary="Health check")
async def health():
    db_status = "connected" if db_available else "unavailable"

    checks = {
        "database": db_status,
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "instagram_token_set": bool(os.getenv("INSTAGRAM_ACCESS_TOKEN")),
    }

    # Consider DB critical for "healthy"
    healthy = db_available

    return JSONResponse(
        status_code=200 if healthy else 503,
        content={
            "status": "healthy" if healthy else "degraded",
            "checks": checks,
        },
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
def _try_include_router(module_path: str) -> None:
    """
    Safely import a backend router and register it with the app.
    If the module or its `router` attribute is missing, the app continues
    running — the missing route is logged as a warning, not a crash.
    """
    try:
        mod = __import__(module_path, fromlist=["router"])
        app.include_router(mod.router)
        logger.info("Router loaded: %s  (prefix=%s)", module_path, mod.router.prefix)
    except Exception as exc:
        logger.warning("Router skipped: %s — %s", module_path, exc)


_try_include_router("backend.routers.agent")
_try_include_router("backend.routers.hitl")
_try_include_router("backend.routers.approve")
_try_include_router("backend.routers.mcp")
_try_include_router("backend.routers.inbox")
_try_include_router("backend.routers.metrics")
_try_include_router("backend.routers.social")
