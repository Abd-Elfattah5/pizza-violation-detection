# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - Routes Package
# ══════════════════════════════════════════════════════════════

from fastapi import APIRouter

# Create main router
api_router = APIRouter()

# Import and include all route modules
from . import health, videos, violations, roi, websocket

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(violations.router, prefix="/violations", tags=["Violations"])
api_router.include_router(roi.router, prefix="/roi", tags=["ROI"])

# WebSocket router is separate (not under /api prefix)
ws_router = websocket.router
