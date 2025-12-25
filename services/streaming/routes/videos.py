# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - Video Routes
# ══════════════════════════════════════════════════════════════

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database import db

router = APIRouter()


class VideoResponse(BaseModel):
    """Video response model."""
    id: str
    filename: str
    status: str
    total_frames: int
    processed_frames: int
    fps: float
    duration: float
    total_violations: int


class VideoStartRequest(BaseModel):
    """Request to start video processing."""
    video_path: str


@router.get("")
async def list_videos():
    """
    Get list of all videos.
    
    Returns:
        List of video records
    """
    videos = db.get_all_videos()
    
    # Convert UUID and datetime objects to strings
    for video in videos:
        video['id'] = str(video['id'])
        if video.get('created_at'):
            video['created_at'] = video['created_at'].isoformat()
        if video.get('updated_at'):
            video['updated_at'] = video['updated_at'].isoformat()
    
    return {
        "count": len(videos),
        "videos": videos
    }


@router.get("/{video_id}")
async def get_video(video_id: str):
    """
    Get details for a specific video.
    
    Args:
        video_id: UUID of the video
    
    Returns:
        Video details
    """
    video = db.get_video(video_id)
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Convert types
    video['id'] = str(video['id'])
    if video.get('created_at'):
        video['created_at'] = video['created_at'].isoformat()
    if video.get('updated_at'):
        video['updated_at'] = video['updated_at'].isoformat()
    
    return video


@router.get("/status/{status}")
async def get_videos_by_status(status: str):
    """
    Get videos filtered by status.
    
    Args:
        status: Video status (pending, processing, completed, error)
    
    Returns:
        List of videos with that status
    """
    valid_statuses = ["pending", "processing", "completed", "error"]
    
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    videos = db.get_video_by_status(status)
    
    for video in videos:
        video['id'] = str(video['id'])
        if video.get('created_at'):
            video['created_at'] = video['created_at'].isoformat()
        if video.get('updated_at'):
            video['updated_at'] = video['updated_at'].isoformat()
    
    return {
        "status": status,
        "count": len(videos),
        "videos": videos
    }


@router.post("/start")
async def start_video_processing(request: VideoStartRequest):
    """
    Request to start processing a video.
    
    Note: This endpoint signals intent to process.
    Actual processing is handled by Frame Reader service.
    
    Args:
        video_path: Path to the video file
    
    Returns:
        Acknowledgment message
    """
    # In a full implementation, this would:
    # 1. Validate the video file exists
    # 2. Send a message to Frame Reader service
    # 3. Return a video_id to track progress
    
    return {
        "message": "Video processing request received",
        "video_path": request.video_path,
        "note": "Start the Frame Reader service with this video path"
    }
