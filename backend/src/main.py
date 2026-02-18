"""
Krepsys FastAPI application.
Main entry point for the backend server.

Follows 12-factor app principles:
- Configuration from environment
- JSON structured logging
- Database initialization on startup
- Auto-generated API documentation
"""

import logging
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from src.config import Settings
from src.database import engine, Base
from src.api.feeds import router as feeds_router
from src.api.articles import router as articles_router
from src.api.tags import router as tags_router
from src.api.highlights import router as highlights_router
# Import models to register them with SQLAlchemy Base
from src.models import Feed, Article, Tag, Highlight  # noqa: F401

# Initialize settings
settings = Settings()

# Configure JSON logging (12-factor app)
class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""
    
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


# Set up logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.basicConfig(
    level=settings.log_level,
    handlers=[handler]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application."""
    # Startup
    logger.info("Starting Krepsys application")
    
    # Create new tables (additive — won't touch existing tables)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # Runtime migration: add columns that may not exist in older DBs
    with engine.connect() as conn:
        for stmt in [
            "ALTER TABLE articles ADD COLUMN note TEXT",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
                logger.info(f"Migration applied: {stmt}")
            except Exception:
                pass  # Column already exists
    
    yield
    
    # Shutdown
    logger.info("Shutting down Krepsys application")


# Create FastAPI app
app = FastAPI(
    title="Krepsys API",
    description="Self-hosted newsletter reader API",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured for origins: {origins}")

# Include API routers
app.include_router(feeds_router)
app.include_router(articles_router)
app.include_router(tags_router)
app.include_router(highlights_router)


@app.get("/health")
async def health_check():
    """Health check endpoint.
    
    Returns:
        dict: Health status including database connection and version
    """
    return {
        "status": "healthy",
        "database": "connected",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API information.
    
    Returns:
        dict: API name, version, and links to documentation
    """
    return {
        "name": "Krepsys API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }
