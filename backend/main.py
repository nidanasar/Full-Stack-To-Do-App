# """FastAPI application entry point."""

# from contextlib import asynccontextmanager

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from config import settings
# from database import close_db, init_db
# from exceptions import register_exception_handlers
# from routes import auth_router, tasks_router


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Application lifespan manager for startup and shutdown events."""
#     # Startup validation
#     if not settings.database_url:
#         raise RuntimeError("DATABASE_URL environment variable is not configured")
#     if not settings.better_auth_secret:
#         raise RuntimeError("BETTER_AUTH_SECRET environment variable is not configured")

#     # Initialize database tables
#     await init_db()

#     yield

#     # Cleanup on shutdown
#     await close_db()


# app = FastAPI(
#     title="Hackathon Todo API",
#     description="Phase II Todo Application - FastAPI Backend with JWT Authentication",
#     version="1.0.0",
#     lifespan=lifespan,
#     docs_url="/docs",
#     redoc_url="/redoc",
# )

# # CORS middleware configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://127.0.0.1:3000",
#         settings.better_auth_url,
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Register exception handlers
# register_exception_handlers(app)

# # Register routers
# app.include_router(auth_router, prefix="/api/v1")
# app.include_router(tasks_router, prefix="/api/v1")


# @app.get("/health", tags=["health"])
# async def health_check() -> dict:
#     """Health check endpoint."""
#     return {"status": "healthy", "version": "1.0.0"}

"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import close_db, init_db
from exceptions import register_exception_handlers
from routes import auth_router, tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup validation
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL environment variable is not configured")
    if not settings.better_auth_secret:
        raise RuntimeError("BETTER_AUTH_SECRET environment variable is not configured")

    # Initialize database tables
    await init_db()

    yield

    # Cleanup on shutdown
    await close_db()


app = FastAPI(
    title="Hackathon Todo API",
    description="Phase II Todo Application - FastAPI Backend with JWT Authentication",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        settings.better_auth_url,
        "https://fullstack-todo-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Register routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Hackathon Todo API", "docs": "/docs", "health": "/health"}

