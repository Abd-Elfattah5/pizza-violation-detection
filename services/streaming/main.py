# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - Main Entry Point
# ══════════════════════════════════════════════════════════════

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

import config
from database import db
from consumer import frame_consumer
from routes import api_router, ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    """
    # ═══════════════════════════════════════════════════════════
    # STARTUP
    # ═══════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("STREAMING SERVICE - Starting")
    print("=" * 60 + "\n")
    
    config.print_config()
    
    # Connect to database
    db.connect()
    
    # Start background consumer
    frame_consumer.start()
    
    print("\n" + "=" * 60)
    print("STREAMING SERVICE - Ready!")
    print(f"API Docs: http://{config.HOST}:{config.PORT}/docs")
    print("=" * 60 + "\n")
    
    yield  # Application runs here
    
    # ═══════════════════════════════════════════════════════════
    # SHUTDOWN
    # ═══════════════════════════════════════════════════════════
    print("\n[Main] Shutting down...")
    frame_consumer.stop()
    db.close()
    print("[Main] Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Pizza Violation Detection - Streaming Service",
    description="REST API and WebSocket streaming for violation detection",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Pizza Violation Detection - Streaming Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False
    )
