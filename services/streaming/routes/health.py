# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - Health Check Routes
# ══════════════════════════════════════════════════════════════

from fastapi import APIRouter
from database import db
from consumer import frame_consumer
from stream_manager import stream_manager

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns status of all service dependencies.
    """
    return {
        "status": "healthy",
        "service": "streaming",
        "dependencies": {
            "database": "connected" if db.is_connected() else "disconnected",
            "rabbitmq_consumer": "running" if frame_consumer.is_running else "stopped"
        },
        "stream": stream_manager.get_status()
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check - is the service ready to handle requests?
    """
    is_ready = db.is_connected()
    
    return {
        "ready": is_ready,
        "database": db.is_connected(),
        "consumer": frame_consumer.is_running
    }
