# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - Violation Routes
# ══════════════════════════════════════════════════════════════

from fastapi import APIRouter, Query
from typing import Optional
from database import db
from stream_manager import stream_manager

router = APIRouter()


@router.get("")
async def get_violations(video_id: Optional[str] = Query(None)):
    """
    Get violations, optionally filtered by video.
    
    Args:
        video_id: Optional video ID to filter by
    
    Returns:
        List of violations
    """
    violations = db.get_violations(video_id)
    
    # Convert types
    for v in violations:
        v['id'] = str(v['id'])
        v['video_id'] = str(v['video_id'])
        if v.get('created_at'):
            v['created_at'] = v['created_at'].isoformat()
    
    return {
        "video_id": video_id,
        "count": len(violations),
        "violations": violations
    }


@router.get("/count")
async def get_violation_count(video_id: Optional[str] = Query(None)):
    """
    Get total violation count.
    
    Args:
        video_id: Optional video ID to filter by
    
    Returns:
        Violation count
    """
    count = db.get_violation_count(video_id)
    
    return {
        "video_id": video_id,
        "count": count
    }


@router.get("/current")
async def get_current_violations():
    """
    Get current violation status from the live stream.
    
    Returns:
        Current violation count from streaming data
    """
    frame = stream_manager.get_frame()
    
    if frame:
        return {
            "is_streaming": True,
            "video_id": frame.video_id,
            "frame_number": frame.frame_number,
            "violation_detected": frame.violation_detected,
            "violation_count": frame.violation_count
        }
    else:
        return {
            "is_streaming": False,
            "video_id": None,
            "frame_number": 0,
            "violation_detected": False,
            "violation_count": 0
        }
